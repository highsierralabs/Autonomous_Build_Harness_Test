"""SA-2 (dispatch R07 item 2): `availability.probe()`'s wall-clock exposure
must be bounded near `PROBE_BUDGET_S` even when `embed_query_cpu` hangs well
past it -- a defect invisible to any assertion about the *returned* reason,
which the previous ThreadPoolExecutor-based implementation already got right
(`embedder_unreachable`) while still blocking the caller for the embed call's
full duration, because `with ThreadPoolExecutor(...) as pool:` joins its
worker thread on `__exit__` regardless of what `future.result(timeout=...)`
did. Round 1's own flagged UNVERIFIED gap ("verified by code reading, not an
observed slow run", docs/rounds/R01_corpus_adapter.report.md) was the
precursor to this finding, not the finding itself -- this test is the first
thing in this build to actually run a slow embedder against the probe.

Against the OLD code, this test would have measured `elapsed` close to
`_HungEmbedder.SLEEP_S` (2.0s here; up to OLLAMA_TIMEOUT_S=300s against a
real hung Ollama), not close to the shortened budget -- because
`ThreadPoolExecutor.__exit__` would have joined the worker before `probe()`
could return. That comparison is not re-run here (the old code no longer
exists in this file to run side by side); it is stated as what the test
would have shown, per the old implementation's documented behaviour.
"""
from __future__ import annotations

import time

from explorer.corpus_adapter import availability


class _FakeCursor:
    def __init__(self, row):
        self._row = row

    def fetchone(self):
        return self._row


class _FakeConn:
    """Just enough of a sqlite3.Connection for probe()'s pre-embed checks:
    `SELECT vec_version()` must succeed (sqlite-vec "loaded"), and
    `get_meta(conn, "vec_rows__<tag>")` must return non-None (vec table
    "present") -- so the probe reaches the embed-call step being tested."""

    def execute(self, sql_text, params=()):
        if "vec_version" in sql_text:
            return _FakeCursor(("v0.1.0",))
        raise AssertionError(f"unexpected SQL against the fake conn: {sql_text!r}")

    def close(self):
        pass


class _HungEmbedder:
    """Fake `rhaco_index` whose `embed_query_cpu` sleeps well past a
    (monkeypatched, shortened) PROBE_BUDGET_S -- standing in for a genuinely
    slow/hung Ollama, which round 1 flagged as never having been exercised."""

    VEC_DISABLE_ENV = "RHACO_CORPUS_DISABLE_VEC"
    CPU_FLOOR_TAG = "nomic-embed-text"
    SLEEP_S = 2.0  # comfortably past the shortened test budget; short enough to keep the suite fast

    @staticmethod
    def connect(db_path):
        return _FakeConn()

    @staticmethod
    def get_meta(conn, key):
        return "1" if key.startswith("vec_rows__") else None

    @classmethod
    def embed_query_cpu(cls, model_tag, texts):
        time.sleep(cls.SLEEP_S)
        return [[0.0]]


def test_probe_bounds_callers_own_elapsed_time_when_embedder_hangs(tmp_path, monkeypatch):
    """The load-bearing assertion is on `elapsed` (the CALLER's own wall-clock
    time around the `probe()` call), not merely on `result.reason` -- the
    return-value-only assertion is exactly what the old, defective code could
    already pass while still blocking for the embedder's full duration."""
    monkeypatch.delenv(_HungEmbedder.VEC_DISABLE_ENV, raising=False)
    shortened_budget = 0.2
    monkeypatch.setattr(availability, "PROBE_BUDGET_S", shortened_budget)

    db_file = tmp_path / "live.db"
    db_file.write_bytes(b"")  # probe() only needs os.path.isfile to see a file

    t0 = time.perf_counter()
    result = availability.probe(_HungEmbedder, str(db_file))
    elapsed = time.perf_counter() - t0

    assert result.available is False
    assert result.reason == "embedder_unreachable"

    assert elapsed < shortened_budget + 1.0, (
        f"probe() took {elapsed:.2f}s against a {shortened_budget:.2f}s budget while "
        f"embed_query_cpu was sleeping for {_HungEmbedder.SLEEP_S:.1f}s -- the caller "
        "was blocked past the budget, which is exactly the defect SA-2 describes "
        "(the old ThreadPoolExecutor-context-manager code joined the worker on exit)"
    )
    # And the discriminating comparison: elapsed must be well under the full
    # embed_query_cpu sleep -- if this failed while `reason` above still
    # passed, that would reproduce the exact invisibility SA-2 named.
    assert elapsed < _HungEmbedder.SLEEP_S / 2, (
        f"probe() took {elapsed:.2f}s, not meaningfully less than the embedder's "
        f"{_HungEmbedder.SLEEP_S:.1f}s sleep -- the caller was effectively joined to it"
    )
