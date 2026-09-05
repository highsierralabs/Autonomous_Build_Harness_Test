"""/api/search returns the same ranks, ids and evidence as the page renders
(task B5 deliverable 5)."""
from __future__ import annotations


def test_api_and_page_agree_on_ranks_ids_and_evidence_lexical(fixture_client):
    page = fixture_client.get("/search", params={"q": "quartz lattice lantern", "mode": "lexical"}).text
    data = fixture_client.get("/api/search", params={"q": "quartz lattice lantern", "mode": "lexical"}).json()

    assert data["results"], "expected at least one result"
    for r in data["results"]:
        assert f'data-doc-id="{r["doc_id"]}"' in page
        assert f'data-rank="{r["rank"]}"' in page
        assert r["evidence"]["line"] in page


def test_api_and_page_agree_on_evidence_hybrid_degraded(fixture_client):
    page = fixture_client.get("/search", params={"q": "quartz lattice lantern", "mode": "hybrid"}).text
    data = fixture_client.get("/api/search", params={"q": "quartz lattice lantern", "mode": "hybrid"}).json()

    assert data["mode_effective"] == "hybrid-degraded-lexical"
    assert data["degradation_notice"] in page
    for r in data["results"]:
        assert f'data-doc-id="{r["doc_id"]}"' in page
        assert r["evidence"]["component_rank"] in page
