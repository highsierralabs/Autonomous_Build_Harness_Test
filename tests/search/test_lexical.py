"""Lexical mode (task B5 deliverable 5): TestClient against the fixture index.

The "quartz lattice lantern" phrase and its line 15 are pinned facts of the
fixture corpus (docs/rounds/R01_probe.report.md fixture inventory table,
verified again for this round -- see docs/rounds/R02_search.report.md
Evidence). `doc_type_filter=EVT` narrows a broader "fixture" hit-set to the
one EVT document -- verified against the built fixture index before writing
this test (R02_search.report.md Evidence): RHACO_corpus_index.search_fts
iterates a bare `doc_type_filter` string character-by-character
(`{t.upper() for t in doc_type_filter}`), so a single value must reach it as
a one-item list; explorer.search.service does this wrapping.
"""
from __future__ import annotations

ANL_CARD_REF = "reports/RHACO-ANL-20260115-002_Fixture_Analysis.card.yaml"
EVT_CARD_REF = "reports/RHACO-EVT-20260115-004_Fixture_Event_E000777.card.yaml"


def test_lexical_quartz_phrase_returns_anl_at_line_15_with_line_anchor(fixture_client):
    resp = fixture_client.get("/search", params={"q": "quartz lattice lantern", "mode": "lexical"})
    assert resp.status_code == 200
    body = resp.text
    assert 'data-mode="lexical"' in body
    assert 'data-mode-effective="lexical"' in body
    assert 'data-doc-id="RHACO-ANL-20260115-002"' in body
    assert "quartz lattice lantern" in body
    assert f"/doc/{ANL_CARD_REF}?line=15" in body


def test_lexical_doc_type_filter_narrows_to_evt(fixture_client):
    unfiltered = fixture_client.get("/search", params={"q": "fixture", "mode": "lexical"})
    assert unfiltered.status_code == 200
    unfiltered_data = fixture_client.get("/api/search", params={"q": "fixture", "mode": "lexical"}).json()
    assert unfiltered_data["returned"] > 1, "expected 'fixture' to hit more than one document unfiltered"

    filtered = fixture_client.get(
        "/search", params={"q": "fixture", "mode": "lexical", "doc_type_filter": "EVT"}
    )
    assert filtered.status_code == 200
    filtered_data = fixture_client.get(
        "/api/search", params={"q": "fixture", "mode": "lexical", "doc_type_filter": "EVT"}
    ).json()
    assert filtered_data["returned"] >= 1
    assert all(r["doc_id"] == "RHACO-EVT-20260115-004" for r in filtered_data["results"])
    assert f'data-card-ref="{EVT_CARD_REF}"' in filtered.text


def test_lexical_evidence_carries_line_and_context(fixture_client):
    resp = fixture_client.get("/api/search", params={"q": "quartz lattice lantern", "mode": "lexical"})
    data = resp.json()
    assert data["results"], "expected at least one lexical result"
    evidence = data["results"][0]["evidence"]
    assert evidence["excerpt_source"] == "lexical-hit"
    assert evidence["line_no"] == 15
    assert "quartz lattice lantern" in evidence["line"]
    assert isinstance(evidence["context_before"], list)
    assert isinstance(evidence["context_after"], list)
