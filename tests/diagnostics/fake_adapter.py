"""Fake CorpusAdapter for diagnostics tests (task B3 item 4).

Returns fixed IndexMeta / VectorAvailability / FreshnessView / exclusion_sets values
built from explorer/models.py, matching the read-only surface documented in
ARCHITECTURE.md 4.1. Injected as app.state.adapter -- never touches a real database,
the real corpus, or RHACO_corpus_index.
"""
from __future__ import annotations

from explorer.models import FreshnessView, IndexMeta, VectorAvailability

FIXTURE_DB_PATH = r"C:\fake\corpus_index.db"
FIXTURE_DOCS_ROOT = r"C:\fake\docs"

EXCLUSION_SETS = {
    "body_deny_dirs": [".git", "__pycache__", "_staging", "deprecated", "docs_archive", "drafts", "logs", "templates"],
    "body_suffixes": [".md", ".txt"],
    "librarian_deny_dirs": ["_staging", "docs_archive", "drafts", "logs", "templates"],
}


def make_index_meta(db_path: str = FIXTURE_DB_PATH) -> IndexMeta:
    return IndexMeta(
        db_path=db_path,
        db_bytes=123456,
        db_mtime_utc="2026-09-01T12:00:00Z",
        meta={
            "index_schema_version": "1",
            "librarian_version": "1.19",
            "current_nc_version": "1.17",
            "last_full_reindex_utc": "2026-09-01T11:00:00Z",
            "corpus_card_count": "1150",
            "corpus_cards_sha": "deadbeefcafe",
            "fts_docs_count": "1100",
            "edges_count": "500",
            "id_aliases_count": "1300",
            "vec_rows__nomic-embed-text": "1100",
        },
        live_counts={
            "cards": 1150,
            "fts_docs": 1100,
            "edges": 500,
            "id_aliases": 1300,
            "edges_unresolved": 12,
        },
    )


def make_vector_available() -> VectorAvailability:
    return VectorAvailability(
        available=True, reason="ok", model_tag="nomic-embed-text", probe_ms=42.5, detail=""
    )


def make_vector_unavailable(reason: str = "disabled_by_env") -> VectorAvailability:
    return VectorAvailability(
        available=False,
        reason=reason,
        model_tag="nomic-embed-text",
        probe_ms=None,
        detail="RHACO_CORPUS_DISABLE_VEC=1",
    )


def make_freshness_fresh() -> FreshnessView:
    return FreshnessView(
        fresh=True,
        status="FRESH",
        corpus_card_count_live=1150,
        corpus_card_count_index=1150,
        corpus_cards_sha_live="deadbeefcafe",
        corpus_cards_sha_index="deadbeefcafe",
        added=[],
        removed=[],
        sha_changed=[],
        computed_at_utc="2026-09-03T00:00:00Z",
        scan_seconds=0.42,
    )


def make_freshness_drift() -> FreshnessView:
    return FreshnessView(
        fresh=False,
        status="DRIFT",
        corpus_card_count_live=1151,
        corpus_card_count_index=1150,
        corpus_cards_sha_live="beadfeedcafe",
        corpus_cards_sha_index="deadbeefcafe",
        added=["docs/reports/RHACO-ANL-20260903-002_New.card.yaml"],
        removed=["docs/reports/RHACO-ANL-20260801-003_Old.card.yaml"],
        sha_changed=["docs/reports/RHACO-ANL-20260802-001_Changed.card.yaml"],
        computed_at_utc="2026-09-03T00:05:00Z",
        scan_seconds=0.55,
    )


class FakeAdapter:
    """Minimal stand-in for corpus_adapter.adapter.CorpusAdapter, exposing only the
    read-only surface diagnostics.service.build_view calls."""

    def __init__(
        self,
        *,
        db_path: str = FIXTURE_DB_PATH,
        docs_root: str = FIXTURE_DOCS_ROOT,
        vector: VectorAvailability | None = None,
        index_meta: IndexMeta | None = None,
        freshness: FreshnessView | None = None,
        exclusion_sets: dict | None = None,
        active_fault: str | None = None,
    ) -> None:
        self.db_path = db_path
        self.docs_root = docs_root
        self.active_fault = active_fault
        self._vector = vector if vector is not None else make_vector_available()
        self._index_meta = index_meta if index_meta is not None else make_index_meta(db_path)
        self._freshness = freshness if freshness is not None else make_freshness_fresh()
        self._exclusion_sets = exclusion_sets if exclusion_sets is not None else dict(EXCLUSION_SETS)

    def index_meta(self) -> IndexMeta:
        return self._index_meta

    def vector_availability(self) -> VectorAvailability:
        return self._vector

    def exclusion_sets(self) -> dict:
        return self._exclusion_sets

    def freshness(self) -> FreshnessView:
        return self._freshness
