"""Empty query and adapter-absent paths (task B5 deliverable 5)."""
from __future__ import annotations


def test_empty_query_renders_form_and_runs_no_search(fixture_client):
    resp = fixture_client.get("/search")
    assert resp.status_code == 200
    body = resp.text
    assert 'data-mode="search"' in body
    assert 'data-doc-id=' not in body
    assert 'id="q"' in body
    assert "Mode standing" in body
    assert "these filters apply to lexical search only" in body
    assert "narrow results after retrieval (ranking unchanged)" in body
    assert "documented-FAIL batch mode" in body
    assert "graph / lineage (auxiliary)" in body


def test_empty_query_api_reports_not_ran(fixture_client):
    resp = fixture_client.get("/api/search")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ran"] is False
    assert data["mode_effective"] is None
    assert data["results"] == []
    assert data["identifier_rows"] == []


def test_search_page_has_keyhelp_element(fixture_client):
    resp = fixture_client.get("/search")
    assert 'id="keyhelp"' in resp.text


def test_search_page_adapter_absent_returns_503_notice(client_without_adapter):
    resp = client_without_adapter.get("/search")
    assert resp.status_code == 503
    assert "corpus_adapter not built" in resp.text


def test_api_search_adapter_absent_returns_503_json_error(client_without_adapter):
    resp = client_without_adapter.get("/api/search")
    assert resp.status_code == 503
    assert resp.json() == {"error": "corpus_adapter not built"}
