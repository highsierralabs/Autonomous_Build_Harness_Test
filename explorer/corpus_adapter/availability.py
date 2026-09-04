"""Vector-channel availability probe (CONSTRAINTS.md O4; ARCHITECTURE.md A4).

The module degrades `search_hybrid` / `search_graph` silently on a
`VecUnavailable` substrate (no raise -- I1 section 6), so nothing about a
degraded result's *shape* tells the caller it was degraded. This probe
decides availability itself, before a hybrid/graph call, so the adapter can
label the result honestly.

This module never imports RHACO_corpus_index directly -- adapter.py imports it
(the sole importer, ARCHITECTURE.md section 2) and passes the live module
object in as `rhaco_index`, matching every other file in this package.

Probe budget note (dispatch B1 item 4): `embed_query_cpu` has no timeout
parameter of its own -- `OLLAMA_TIMEOUT_S = 300` is fixed inside the module,
and the public API exposes no way to lower it. Rather than accept a
worst-case 300 s hang inside a 5-second-cached availability check, the probe
below bounds its OWN wall-clock exposure with a one-shot daemon-thread call
(`ThreadPoolExecutor(max_workers=1).result(timeout=PROBE_BUDGET_S)`): if the
embed call has not returned within the budget, the probe reports
`embedder_unreachable` and moves on. The call itself is a plain read-only
network request (no state it can corrupt), so leaving it to finish or fail on
its own in the background thread is safe; this is a calling-side bound, not a
change to the module's own timeout. See docs/rounds/R01_corpus_adapter.report.md,
"Material alternatives".
"""
from __future__ import annotations

import os
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError

from explorer.models import VectorAvailability

PROBE_BUDGET_S = 8.0
CACHE_TTL_S = 5.0


def probe(rhaco_index, db_path: str) -> VectorAvailability:
    """One-shot vector-availability probe (CONSTRAINTS O4 procedure a-d). Never
    raises; every failure path is reported through VectorAvailability.reason."""
    t0 = time.perf_counter()
    tag = rhaco_index.CPU_FLOOR_TAG

    if os.environ.get(rhaco_index.VEC_DISABLE_ENV):
        return _result(False, "disabled_by_env", tag, t0, f"{rhaco_index.VEC_DISABLE_ENV} is set")

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
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(rhaco_index.embed_query_cpu, tag, ["probe"])
            future.result(timeout=PROBE_BUDGET_S)
    except FutureTimeoutError:
        return _result(
            False, "embedder_unreachable", tag, t0,
            f"embed_query_cpu did not return within the {PROBE_BUDGET_S:.0f}s probe "
            "budget (the module's own OLLAMA_TIMEOUT_S=300 is not the probe's bound)",
        )
    except Exception as exc:  # noqa: BLE001 -- VecUnavailable or any other embed-path failure
        return _result(False, "embedder_unreachable", tag, t0, f"{type(exc).__name__}: {exc}")

    return _result(True, "ok", tag, t0, "")


def _result(available: bool, reason: str, model_tag: str, t0: float, detail: str) -> VectorAvailability:
    probe_ms = (time.perf_counter() - t0) * 1000.0
    return VectorAvailability(available=available, reason=reason, model_tag=model_tag, probe_ms=probe_ms, detail=detail)
