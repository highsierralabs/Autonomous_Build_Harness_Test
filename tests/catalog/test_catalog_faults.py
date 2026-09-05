"""Adapter-absent path for GET / and GET /api/catalog (task B4 item 4;
ARCHITECTURE.md 4.2 access rule / diagnostics precedent)."""
from __future__ import annotations


def test_home_adapter_absent_shows_notice_and_503(client_adapter_absent):
    resp = client_adapter_absent.get("/")
    assert resp.status_code == 503
    assert "corpus_adapter not built" in resp.text


def test_api_catalog_adapter_absent_returns_503_json_error(client_adapter_absent):
    resp = client_adapter_absent.get("/api/catalog")
    assert resp.status_code == 503
    assert resp.json() == {"error": "corpus_adapter not built"}
