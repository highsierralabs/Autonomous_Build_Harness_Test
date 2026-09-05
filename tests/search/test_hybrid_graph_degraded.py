"""Hybrid / graph modes, degraded path (task B5 deliverable 5): the fixture
index carries no vector set, so both modes degrade by construction
(docs/rounds/R01_probe.report.md). Verifies the exact degradation notice
text, the degraded mode_effective label, and that the bare "Hybrid" label is
never shown as the active mode (CONSTRAINTS.md S3/O4).
"""
from __future__ import annotations

HYBRID_NOTICE = "Hybrid unavailable: using lexical retrieval. Result ordering is lexical-only."
GRAPH_NOTICE = (
    "Graph seed channel degraded: hybrid seeding fell back to identifier "
    "resolution plus lexical (FTS) search. The graph expansion itself -- one "
    "hop over the typed edges table -- is unaffected and still shapes result "
    "ordering."
)


def test_hybrid_degrades_on_fixture(fixture_client):
    resp = fixture_client.get("/search", params={"q": "quartz lattice lantern", "mode": "hybrid"})
    assert resp.status_code == 200
    body = resp.text
    assert 'data-mode="hybrid-degraded-lexical"' in body
    assert 'data-vector="unavailable"' in body
    assert 'data-mode-effective="hybrid-degraded-lexical"' in body
    assert HYBRID_NOTICE in body
    assert "Active mode: hybrid-degraded-lexical" in body


def test_hybrid_default_mode_is_hybrid(fixture_client):
    # No `mode` query param at all -> default is hybrid (CONSTRAINTS.md S3).
    resp = fixture_client.get("/search", params={"q": "quartz lattice lantern"})
    assert resp.status_code == 200
    assert 'data-mode="hybrid-degraded-lexical"' in resp.text


def test_hybrid_component_rank_line_present_for_every_result(fixture_client):
    data = fixture_client.get("/api/search", params={"q": "quartz lattice lantern", "mode": "hybrid"}).json()
    assert data["results"], "expected at least one hybrid result on the fixture"
    for r in data["results"]:
        assert r["evidence"]["component_rank"] == "not exposed by current RHACO retrieval API"
        assert r["evidence"]["degradation_status"] != "none"


def test_graph_degrades_on_fixture(fixture_client):
    resp = fixture_client.get("/search", params={"q": "quartz lattice lantern", "mode": "graph"})
    assert resp.status_code == 200
    body = resp.text
    assert 'data-mode="graph-degraded-semantic-seed"' in body
    assert 'data-mode-effective="graph-degraded-semantic-seed"' in body
    assert GRAPH_NOTICE in body
    assert "expansion of a seed; relation not exposed by the current RHACO API" in body


def test_graph_never_shows_bare_hybrid_or_graph_label(fixture_client):
    body = fixture_client.get("/search", params={"q": "quartz lattice lantern", "mode": "graph"}).text
    assert 'data-mode-effective="graph"' not in body
