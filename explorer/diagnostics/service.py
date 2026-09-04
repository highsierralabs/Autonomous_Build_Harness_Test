"""Diagnostics view assembly (builder-owned: diagnostics). ARCHITECTURE.md 4.6;
CONSTRAINTS.md S3/S8/O4/O9/O17/O24; PROMPT.md 5.6.

build_view(adapter, settings) reads the adapter's already-defined, read-only
surface (ARCHITECTURE.md 4.1: index_meta, vector_availability, exclusion_sets,
freshness, and the db_path / docs_root / active_fault attributes) and assembles
a single DiagnosticsView for both the HTML page and its JSON twin. Nothing here
opens a database connection, imports RHACO_corpus_index for anything but the one
documented constant (RERANK_MODEL_DIR, path-existence check only, model never
loaded -- CONSTRAINTS.md O17), or performs any write.
"""
from __future__ import annotations

import glob
import json
import os
import sys
from dataclasses import dataclass
from typing import Any

from explorer.config import RHACO_PATH_ENTRIES, Settings
from explorer.models import AUTHORITY_NOTICE, FreshnessView, IndexMeta, VectorAvailability

# PROMPT.md 5.2; docs/REFERENCE.md section 1: flat hybrid is the accepted default.
DEFAULT_MODE = "hybrid"
DEGRADED_MODE = "hybrid-degraded-lexical"

# ARCHITECTURE.md 4.3 / CONSTRAINTS.md O4 -- exact wording, reused verbatim (task B3 item 1).
DEGRADATION_TEXT = "Hybrid unavailable: using lexical retrieval. Result ordering is lexical-only."
NO_DEGRADATION_TEXT = "none"

# CONSTRAINTS.md S3/A11; docs/REFERENCE.md section 1 (RHACO-ANL-20260712-001 lines 16, 48) --
# fixed text, quoted verbatim per the dispatch (task B3 item 1).
RERANK_STANDING_TEXT = (
    "hybrid-rerank: documented-FAIL batch mode (RHACO-ANL-20260712-001: "
    "Recall@10 0.575; ~26 min/query); not offered interactively"
)

NO_PROBE_RUN = "none recorded"

# explorer/diagnostics/service.py -> explorer/diagnostics -> explorer -> workspace root.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_WORKSPACE_ROOT = os.path.dirname(os.path.dirname(_THIS_DIR))
_PROBE_RUNS_GLOB = os.path.join(_WORKSPACE_ROOT, "docs", "probe-qualification", "runs", "*", "run_summary.json")


@dataclass
class RerankStanding:
    """CONSTRAINTS.md A11/O17: rerank is never invoked; only its documented standing
    and whether the pinned artifact directory exists on disk are reported."""

    text: str
    artifact_present: bool


@dataclass
class DiagnosticsView:
    """The complete instrument-state page (task B3 item 1). Every field is either an
    adapter-reported value, a fixed disposition string, or a filesystem observation --
    nothing here is computed retrieval output."""

    app_version: str
    db_path: str
    non_authoritative_notice: str
    index_meta: IndexMeta
    vector: VectorAvailability
    default_mode: str
    effective_mode: str
    degradation_text: str
    exclusion_sets: dict
    rerank: RerankStanding
    last_probe_run: Any  # dict {"path": ..., "summary": {...}} when found, else NO_PROBE_RUN
    authority_notice: str
    active_fault: str | None
    freshness: FreshnessView | None = None


def _rerank_artifact_present() -> bool:
    """os.path.isdir on RHACO_corpus_index.RERANK_MODEL_DIR -- import only, call
    nothing, never load the model (task B3 item 1; CONSTRAINTS.md O17)."""
    for entry in RHACO_PATH_ENTRIES:
        if entry not in sys.path:
            sys.path.insert(0, entry)
    try:
        import RHACO_corpus_index as rhaco_corpus_index  # import only; no calls
    except ImportError:
        return False
    rerank_dir = getattr(rhaco_corpus_index, "RERANK_MODEL_DIR", None)
    return bool(rerank_dir) and os.path.isdir(rerank_dir)


def _find_last_probe_run() -> Any:
    """docs/probe-qualification/runs/*/run_summary.json, newest-first by mtime,
    or NO_PROBE_RUN when none exist or the newest is unreadable (task B3 item 1)."""
    matches = glob.glob(_PROBE_RUNS_GLOB)
    if not matches:
        return NO_PROBE_RUN
    matches.sort(key=os.path.getmtime, reverse=True)
    newest = matches[0]
    try:
        with open(newest, encoding="utf-8") as fh:
            summary = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return NO_PROBE_RUN
    rel_path = os.path.relpath(newest, _WORKSPACE_ROOT).replace(os.sep, "/")
    return {"path": rel_path, "summary": summary}


def build_view(adapter: Any, settings: Settings, *, freshness: FreshnessView | None = None) -> DiagnosticsView:
    """Assemble the diagnostics view from the adapter's read-only surface.

    `freshness` is None by default (task B3 item 1); the POST /diagnostics/freshness
    route is the only caller that supplies one, from its own adapter.freshness() call.
    """
    index_meta = adapter.index_meta()
    vector = adapter.vector_availability()
    effective_mode = DEFAULT_MODE if vector.available else DEGRADED_MODE
    degradation_text = NO_DEGRADATION_TEXT if vector.available else DEGRADATION_TEXT
    return DiagnosticsView(
        app_version=settings.app_version,
        db_path=index_meta.db_path,
        non_authoritative_notice=index_meta.non_authoritative_notice,
        index_meta=index_meta,
        vector=vector,
        default_mode=DEFAULT_MODE,
        effective_mode=effective_mode,
        degradation_text=degradation_text,
        exclusion_sets=adapter.exclusion_sets(),
        rerank=RerankStanding(text=RERANK_STANDING_TEXT, artifact_present=_rerank_artifact_present()),
        last_probe_run=_find_last_probe_run(),
        authority_notice=AUTHORITY_NOTICE,
        active_fault=getattr(adapter, "active_fault", None),
        freshness=freshness,
    )
