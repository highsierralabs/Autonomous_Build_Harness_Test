"""Unit tests for explorer.diagnostics.service.build_view (task B3 item 4)."""
from __future__ import annotations

from explorer.config import Settings
from explorer.diagnostics.service import (
    DEFAULT_MODE,
    DEGRADATION_TEXT,
    DEGRADED_MODE,
    NO_DEGRADATION_TEXT,
    NO_PROBE_RUN,
    build_view,
)
from tests.diagnostics.fake_adapter import (
    FakeAdapter,
    make_freshness_drift,
    make_freshness_fresh,
    make_vector_available,
    make_vector_unavailable,
)


def _settings() -> Settings:
    return Settings()


def test_default_mode_is_hybrid_and_matches_effective_when_vector_available():
    view = build_view(FakeAdapter(vector=make_vector_available()), _settings())
    assert view.default_mode == DEFAULT_MODE == "hybrid"
    assert view.effective_mode == "hybrid"
    assert view.degradation_text == NO_DEGRADATION_TEXT == "none"


def test_effective_mode_degrades_when_vector_unavailable():
    view = build_view(FakeAdapter(vector=make_vector_unavailable()), _settings())
    assert view.default_mode == "hybrid"
    assert view.effective_mode == DEGRADED_MODE == "hybrid-degraded-lexical"
    assert view.degradation_text == DEGRADATION_TEXT
    assert view.degradation_text == (
        "Hybrid unavailable: using lexical retrieval. Result ordering is lexical-only."
    )


def test_index_meta_and_db_path_carried_through():
    adapter = FakeAdapter(db_path=r"C:\fake\corpus_index.db")
    view = build_view(adapter, _settings())
    assert view.db_path == r"C:\fake\corpus_index.db"
    assert view.index_meta.db_path == r"C:\fake\corpus_index.db"
    assert "non-authoritative" in view.non_authoritative_notice
    assert view.index_meta.meta["librarian_version"] == "1.19"
    assert view.index_meta.live_counts["cards"] == 1150


def test_exclusion_sets_passed_through_from_adapter():
    adapter = FakeAdapter()
    view = build_view(adapter, _settings())
    assert view.exclusion_sets == adapter.exclusion_sets()
    assert "docs_archive" in view.exclusion_sets["body_deny_dirs"]


def test_rerank_standing_text_is_fixed():
    view = build_view(FakeAdapter(), _settings())
    assert view.rerank.text == (
        "hybrid-rerank: documented-FAIL batch mode (RHACO-ANL-20260712-001: "
        "Recall@10 0.575; ~26 min/query); not offered interactively"
    )
    assert isinstance(view.rerank.artifact_present, bool)


def test_last_probe_run_none_recorded_when_no_runs_directory():
    # The worktree carries no docs/probe-qualification/runs/ tree (built by wave 3),
    # so this must resolve to the documented "none recorded" sentinel.
    view = build_view(FakeAdapter(), _settings())
    assert view.last_probe_run == NO_PROBE_RUN == "none recorded"


def test_freshness_is_none_by_default():
    view = build_view(FakeAdapter(), _settings())
    assert view.freshness is None


def test_freshness_passed_through_when_supplied_fresh():
    adapter = FakeAdapter(freshness=make_freshness_fresh())
    view = build_view(adapter, _settings(), freshness=adapter.freshness())
    assert view.freshness is not None
    assert view.freshness.status == "FRESH"
    assert view.freshness.added == []


def test_freshness_passed_through_when_supplied_drift():
    adapter = FakeAdapter(freshness=make_freshness_drift())
    view = build_view(adapter, _settings(), freshness=adapter.freshness())
    assert view.freshness is not None
    assert view.freshness.status == "DRIFT"
    assert view.freshness.added
    assert view.freshness.removed
    assert view.freshness.sha_changed


def test_active_fault_carried_from_adapter():
    view = build_view(FakeAdapter(active_fault="console_error"), _settings())
    assert view.active_fault == "console_error"
    view_none = build_view(FakeAdapter(active_fault=None), _settings())
    assert view_none.active_fault is None


def test_authority_notice_matches_models_constant():
    from explorer.models import AUTHORITY_NOTICE

    view = build_view(FakeAdapter(), _settings())
    assert view.authority_notice == AUTHORITY_NOTICE
