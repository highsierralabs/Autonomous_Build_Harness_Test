"""(e) search_lexical carries line_no + lexical-hit excerpts; (g) search_hybrid
returns top_k items whose mode_effective is consistent with vector_availability()."""
from __future__ import annotations


def test_search_lexical_has_line_no_and_lexical_hit_excerpts(live_adapter):
    result = live_adapter.search_lexical("firmware transfer function")

    assert result.mode_effective == "lexical"
    assert result.items, "expected at least one lexical hit for this literal phrase"

    for item in result.items:
        assert item.evidence.excerpt_source == "lexical-hit"
        assert item.evidence.line_no is not None
        assert item.evidence.line is not None


def test_search_hybrid_top_k_and_mode_consistency(live_adapter):
    result = live_adapter.search_hybrid("firmware transfer function", top_k=5)

    assert len(result.items) == 5
    vec = live_adapter.vector_availability()
    expected_mode = "hybrid" if vec.available else "hybrid-degraded-lexical"
    assert result.mode_effective == expected_mode
    for item in result.items:
        assert item.evidence.retrieval_mode == expected_mode
        assert item.evidence.component_rank == "not exposed by current RHACO retrieval API"
    if not vec.available:
        assert result.degradation_notice == (
            "Hybrid unavailable: using lexical retrieval. Result ordering is lexical-only."
        )
    else:
        assert result.degradation_notice is None
