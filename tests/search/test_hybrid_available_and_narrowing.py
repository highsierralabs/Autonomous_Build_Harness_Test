"""Hybrid mode, vector-AVAILABLE path (task B5 deliverable 5): the fixture
index cannot produce this state (no vector set), so a hand-written fake
adapter (tests/search/fake_adapter.py) stands in, matching every other
module's pattern for a state the fixture cannot reach.
"""
from __future__ import annotations

from tests.search.fake_adapter import FakeAvailableAdapter


def test_hybrid_available_shows_hybrid_badge_no_notice_and_component_rank(client_with_adapter):
    client = client_with_adapter(FakeAvailableAdapter())
    resp = client.get("/search", params={"q": "anything", "mode": "hybrid"})
    assert resp.status_code == 200
    body = resp.text
    assert 'data-mode="hybrid"' in body
    assert 'data-vector="available"' in body
    assert 'data-mode-effective="hybrid"' in body
    assert "Hybrid unavailable" not in body

    data = client.get("/api/search", params={"q": "anything", "mode": "hybrid"}).json()
    assert data["mode_effective"] == "hybrid"
    assert data["degradation_notice"] is None
    assert data["results"], "expected fake results"
    for r in data["results"]:
        assert r["evidence"]["component_rank"] == "not exposed by current RHACO retrieval API"


def test_narrowing_reduces_hybrid_results_by_doc_type_without_changing_ranks(client_with_adapter):
    client = client_with_adapter(FakeAvailableAdapter())
    unfiltered = client.get("/api/search", params={"q": "anything", "mode": "hybrid"}).json()
    assert unfiltered["returned"] == 4
    original_ranks = {r["doc_id"]: r["rank"] for r in unfiltered["results"]}

    narrowed = client.get(
        "/api/search", params={"q": "anything", "mode": "hybrid", "narrow_doc_type": "ANL"}
    ).json()
    assert narrowed["narrowed_from"] == 4
    assert narrowed["narrowed_to"] == 1
    assert narrowed["returned"] == 1
    assert narrowed["results"][0]["doc_id"] == "RHACO-ANL-20260901-101"
    # Ranks are the surviving items' original retrieval ranks -- narrowing drops
    # items, it never re-ranks the survivors (CONSTRAINTS.md O5).
    for r in narrowed["results"]:
        assert r["rank"] == original_ranks[r["doc_id"]]

    body = client.get(
        "/search", params={"q": "anything", "mode": "hybrid", "narrow_doc_type": "ANL"}
    ).text
    assert "narrowed from 4 to 1" in body
    assert "narrow results after retrieval (ranking unchanged)" in body
