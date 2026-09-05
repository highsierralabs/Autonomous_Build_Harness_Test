"""Vector-channel availability probe (CONSTRAINTS.md O4; ARCHITECTURE.md A4).

The module degrades `search_hybrid` / `search_graph` silently on a
`VecUnavailable` substrate (no raise -- I1 section 6), so nothing about a
degraded result's *shape* tells the caller it was degraded. This probe
decides availability itself, before a hybrid/graph call, so the adapter can
label the result honestly.

O10 guard (round 3 / C3): the live index can be removed or replaced out from
under the explorer while it runs, and `RHACO_corpus_index.connect()` creates
the parent directory and the database file (applying DDL) if the path is
absent -- the same hazard `CorpusAdapter.connect()` guards (round 2 / C2).
`probe()` reaches `rhaco_index.connect()` directly, not through
`CorpusAdapter.connect()`, so it is a second, independent call site for that
hazard and needed its own guard: `os.path.isfile(db_path)` is required
before `rhaco_index.connect(db_path)` is ever called. On failure `probe()`
returns `VectorAvailability(available=False, reason="db_unavailable", ...)`
without calling `connect()` at all -- the adapter never creates a database
(O10). This module still never opens or creates anything itself; the check
is `os.path.isfile` only.

This module never imports RHACO_corpus_index directly -- adapter.py imports it
and passes the live module object in as `rhaco_index`, matching every other
file in this package. adapter.py is one of three licensed product-tree
importers of RHACO_corpus_index (ARCHITECTURE.md 4.1's importer table; the
other two are explorer/diagnostics/service.py under O17 and
fixtures/build_fixture_index.py under O3) -- corrected from the earlier,
false "the sole importer" claim (ARCHITECTURE.md 4.1, SA-3; dispatch R07
item 4).

Probe budget note (dispatch B1 item 4; corrected dispatch R07 item 2, SA-2):
`embed_query_cpu` has no timeout parameter of its own -- `OLLAMA_TIMEOUT_S =
300` is fixed inside the module, and the public API exposes no way to lower
it. Rather than accept a worst-case 300 s hang inside a 5-second-cached
availability check, the probe below bounds its OWN wall-clock exposure with a
plain `threading.Thread(daemon=True)` that it starts and then waits on with
`threading.Event.wait(timeout=PROBE_BUDGET_S)` -- NOT joined, and NOT run
through `ThreadPoolExecutor`: an executor's context manager (or its own
`shutdown(wait=True)`) joins its worker on the way out regardless of what
`future.result(timeout=...)` did, so the *previous* implementation's "one-shot
daemon-thread call" description was false in exactly the way SA-2 found -- its
worker threads are plain (non-daemon) `Thread` objects that ARE joined, so the
caller was still blocked by `Executor.__exit__` until `embed_query_cpu`
itself returned or raised, i.e. up to `OLLAMA_TIMEOUT_S=300`, not
`PROBE_BUDGET_S=8`. The call itself is a plain read-only network request (no
state it can corrupt), so leaving a genuinely hung one to finish or fail on
its own, unjoined, in a daemon thread is safe: a daemon thread never blocks
interpreter exit, and `CACHE_TTL_S` bounds how often a new one can be spun up
while the embedder stays unreachable (at most roughly `OLLAMA_TIMEOUT_S /
CACHE_TTL_S` ~ 60 such threads outstanding at once in the worst continuous-
outage case, each self-terminating within OLLAMA_TIMEOUT_S regardless). See
docs/rounds/R01_corpus_adapter.report.md, "Material alternatives", and this
round's report, "Decisions", for the alternatives considered (a long-lived
shared single-worker executor was rejected: a hung call would occupy its one
worker indefinitely, queuing every later probe's task behind it for the life
of the outage rather than running independently).
"""
from __future__ import annotations

import os
import threading
import time

from explorer.models import VectorAvailability

PROBE_BUDGET_S = 8.0
CACHE_TTL_S = 5.0


def probe(rhaco_index, db_path: str) -> VectorAvailability:
    """One-shot vector-availability probe (CONSTRAINTS O4 procedure a-d). Never
    raises; every failure path is reported through VectorAvailability.reason.

    O10 guard: `os.path.isfile(db_path)` is checked -- and must succeed --
    before `rhaco_index.connect(db_path)` is ever called. A missing database
    returns `reason="db_unavailable"` immediately, short-circuiting before
    `connect()` is reached, so this probe can never be the one that lets
    `RHACO_corpus_index.connect()` create a missing database (O10)."""
    t0 = time.perf_counter()
    tag = rhaco_index.CPU_FLOOR_TAG

    if os.environ.get(rhaco_index.VEC_DISABLE_ENV):
        return _result(False, "disabled_by_env", tag, t0, f"{rhaco_index.VEC_DISABLE_ENV} is set")

    if not os.path.isfile(db_path):
        return _result(
            False, "db_unavailable", tag, t0,
            f"database file does not exist: {db_path!r} (the adapter never creates a database, O10)",
        )

    try:
        conn = rhaco_index.connect(db_path)
    except Exception as exc:  # noqa: BLE001 -- any connect failure means "unavailable", not a crash
        return _result(False, "db_unavailable", tag, t0, f"{type(exc).__name__}: {exc}")

    try:
        try:
            conn.execute("SELECT vec_version()").fetchone()
        except Exception as exc:  # noqa: BLE001 -- sqlite-vec extension not loaded
            return _result(False, "sqlite_vec_not_loaded", tag, t0, f"{type(exc).__name__}: {exc}")

        if rhaco_index.get_meta(conn, f"vec_rows__{tag}") is None:
            return _result(False, "vec_table_missing", tag, t0, f"no vec_rows__{tag} meta key")
    finally:
        conn.close()

    try:
        done = threading.Event()
        outcome: dict = {}

        def _embed_probe() -> None:
            try:
                outcome["value"] = rhaco_index.embed_query_cpu(tag, ["probe"])
            except Exception as exc:  # noqa: BLE001 -- VecUnavailable or any other embed-path failure
                outcome["error"] = exc
            finally:
                done.set()

        # SA-2 fix: a plain daemon thread, never joined -- NOT ThreadPoolExecutor,
        # whose `with` block (or an explicit shutdown(wait=True)) joins its
        # worker on exit regardless of the timeout below, which is exactly how
        # the previous implementation's bound was not a real wall-clock bound
        # (see the module docstring's "Probe budget note"). `daemon=True` means
        # this thread never blocks interpreter exit either.
        worker = threading.Thread(target=_embed_probe, daemon=True)
        worker.start()
        if not done.wait(timeout=PROBE_BUDGET_S):
            return _result(
                False, "embedder_unreachable", tag, t0,
                f"embed_query_cpu did not return within the {PROBE_BUDGET_S:.0f}s probe "
                "budget (the module's own OLLAMA_TIMEOUT_S=300 is not the probe's bound); "
                "the worker is a daemon thread, left unjoined to finish or fail on its "
                "own rather than waited on again",
            )
        if "error" in outcome:
            exc = outcome["error"]
            return _result(False, "embedder_unreachable", tag, t0, f"{type(exc).__name__}: {exc}")
    except Exception as exc:  # noqa: BLE001 -- belt-and-suspenders around the thread machinery itself
        return _result(False, "embedder_unreachable", tag, t0, f"{type(exc).__name__}: {exc}")

    return _result(True, "ok", tag, t0, "")


def _result(available: bool, reason: str, model_tag: str, t0: float, detail: str) -> VectorAvailability:
    probe_ms = (time.perf_counter() - t0) * 1000.0
    return VectorAvailability(available=available, reason=reason, model_tag=model_tag, probe_ms=probe_ms, detail=detail)
