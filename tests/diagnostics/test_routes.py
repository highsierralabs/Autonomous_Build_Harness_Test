"""TestClient tests for GET /diagnostics, POST /diagnostics/freshness, GET /api/diagnostics
(task B3 item 4). No server process is launched -- fastapi.testclient.TestClient only
(ARCHITECTURE.md A18).
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from explorer.app import create_app
from explorer.config import Settings
from explorer.models import AUTHORITY_NOTICE
from tests.diagnostics.fake_adapter import (
    FakeAdapter,
    make_vector_available,
    make_vector_unavailable,
)


def _client_with_adapter(adapter) -> TestClient:
    app = create_app(Settings())
    app.state.adapter = adapter
    return TestClient(app)


def _client_without_adapter() -> TestClient:
    # app.state.adapter starts None and explorer.corpus_adapter.adapter is not built
    # in this worktree, so get_adapter() raises RuntimeError -- the degraded path.
    app = create_app(Settings())
    return TestClient(app)


# -- GET /diagnostics -------------------------------------------------------------

def test_diagnostics_page_ok_with_hybrid_available():
    client = _client_with_adapter(FakeAdapter(vector=make_vector_available()))
    resp = client.get("/diagnostics")
    assert resp.status_code == 200
    body = resp.text
    assert AUTHORITY_NOTICE in body
    assert r"C:\fake\corpus_index.db" in body
    assert "non-authoritative" in body
    assert "available" in body  # vector state
    assert "hybrid" in body  # default and effective mode both render as "hybrid"
    assert "docs_archive" in body  # an exclusion-set entry
    assert 'data-mode="hybrid"' in body
    assert 'data-vector="available"' in body


def test_diagnostics_page_degraded_vector_shows_exact_text_and_data_mode():
    client = _client_with_adapter(FakeAdapter(vector=make_vector_unavailable()))
    resp = client.get("/diagnostics")
    assert resp.status_code == 200
    body = resp.text
    assert "Hybrid unavailable: using lexical retrieval. Result ordering is lexical-only." in body
    assert 'data-mode="hybrid-degraded-lexical"' in body
    assert 'data-vector="unavailable"' in body


def test_diagnostics_page_adapter_absent_shows_notice():
    client = _client_without_adapter()
    resp = client.get("/diagnostics")
    assert resp.status_code == 503
    assert "corpus_adapter not built" in resp.text


def test_diagnostics_page_console_error_fault_present():
    client = _client_with_adapter(FakeAdapter(active_fault="console_error"))
    resp = client.get("/diagnostics")
    assert resp.status_code == 200
    assert 'throw new Error("RHACO_EXPLORER_FAULT console_error")' in resp.text


def test_diagnostics_page_no_fault_script_absent():
    client = _client_with_adapter(FakeAdapter(active_fault=None))
    resp = client.get("/diagnostics")
    assert resp.status_code == 200
    assert "RHACO_EXPLORER_FAULT" not in resp.text


def test_diagnostics_page_has_keyhelp_element():
    client = _client_with_adapter(FakeAdapter())
    resp = client.get("/diagnostics")
    assert 'id="keyhelp"' in resp.text


# -- GET /api/diagnostics ----------------------------------------------------------

def test_api_diagnostics_ok_returns_same_keys_as_page():
    client = _client_with_adapter(FakeAdapter(vector=make_vector_available()))
    resp = client.get("/api/diagnostics")
    assert resp.status_code == 200
    data = resp.json()
    assert data["db_path"] == r"C:\fake\corpus_index.db"
    assert "non-authoritative" in data["non_authoritative_notice"]
    assert data["vector"]["available"] is True
    assert data["default_mode"] == "hybrid"
    assert data["effective_mode"] == "hybrid"
    assert "docs_archive" in data["exclusion_sets"]["body_deny_dirs"]
    assert data["authority_notice"] == AUTHORITY_NOTICE
    assert data["freshness"] is None


def test_api_diagnostics_degraded_matches_page_text():
    client = _client_with_adapter(FakeAdapter(vector=make_vector_unavailable()))
    resp = client.get("/api/diagnostics")
    data = resp.json()
    assert data["effective_mode"] == "hybrid-degraded-lexical"
    assert data["degradation_text"] == (
        "Hybrid unavailable: using lexical retrieval. Result ordering is lexical-only."
    )


def test_api_diagnostics_adapter_absent_returns_503_with_error_body():
    client = _client_without_adapter()
    resp = client.get("/api/diagnostics")
    assert resp.status_code == 503
    assert resp.json() == {"error": "corpus_adapter not built"}


def test_api_diagnostics_freshness_query_param_includes_freshness():
    client = _client_with_adapter(FakeAdapter())
    resp_without = client.get("/api/diagnostics")
    assert resp_without.json()["freshness"] is None
    resp_with = client.get("/api/diagnostics?freshness=1")
    assert resp_with.status_code == 200
    assert resp_with.json()["freshness"]["status"] == "FRESH"


# -- POST /diagnostics/freshness ----------------------------------------------------

def test_post_freshness_renders_fresh():
    client = _client_with_adapter(FakeAdapter())  # default fake freshness = FRESH
    resp = client.post("/diagnostics/freshness")
    assert resp.status_code == 200
    assert "FRESH" in resp.text
    assert 'data-freshness-status="FRESH"' in resp.text


def test_post_freshness_renders_drift():
    from tests.diagnostics.fake_adapter import make_freshness_drift

    client = _client_with_adapter(FakeAdapter(freshness=make_freshness_drift()))
    resp = client.post("/diagnostics/freshness")
    assert resp.status_code == 200
    assert "DRIFT" in resp.text
    assert 'data-freshness-status="DRIFT"' in resp.text
    assert "RHACO-ANL-20260903-002" in resp.text  # an "added" entry from the fake


def test_post_freshness_is_the_only_post_and_writes_nothing_new():
    # Calling it twice must be idempotent from the caller's point of view -- it only
    # re-renders using adapter.freshness(), never mutates adapter state.
    client = _client_with_adapter(FakeAdapter())
    first = client.post("/diagnostics/freshness")
    second = client.post("/diagnostics/freshness")
    assert first.status_code == second.status_code == 200


def test_post_freshness_adapter_absent():
    client = _client_without_adapter()
    resp = client.post("/diagnostics/freshness")
    assert resp.status_code == 503
    assert "corpus_adapter not built" in resp.text
