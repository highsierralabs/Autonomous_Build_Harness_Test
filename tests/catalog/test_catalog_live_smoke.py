"""Read-only smoke test against the LIVE index (Settings() defaults; task B4
item 4). Asserts shape only (HTTP 200, a positive total) -- no fixture-shaped
assertion, since the live corpus's exact contents are not this test's
concern. Guarded by tests/catalog/conftest.py's session-scoped
`_live_db_unchanged` fixture (corpus_cards_sha + mtime, copied from
tests/corpus_adapter/conftest.py's approach, not imported).
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from explorer.app import create_app
from explorer.config import Settings


def test_live_catalog_home_returns_positive_total():
    app = create_app(Settings())
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    assert 'data-mode="catalog"' in resp.text
    # at least one card is listed on the real corpus
    assert 'data-doc-id="' in resp.text


def test_live_catalog_api_returns_positive_total():
    app = create_app(Settings())
    client = TestClient(app)
    resp = client.get("/api/catalog")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] > 0
    assert data["index_total_cards"] > 0
    assert len(data["rows"]) > 0
