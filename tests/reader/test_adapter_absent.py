"""corpus_adapter-absent path (ARCHITECTURE.md 4.4/4.6 precedent): the HTML
page renders a visible 503 notice, the API returns 503 with an error body --
never a crash. Uses explorer.app.ADAPTER_ABSENT (A20), never a fake adapter
(this state needs no fixture data at all).
"""
from __future__ import annotations

ANL_CARD_REF = "reports/RHACO-ANL-20260115-002_Fixture_Analysis.card.yaml"


def test_doc_page_adapter_absent_returns_503_notice(adapter_absent_client):
    resp = adapter_absent_client.get(f"/doc/{ANL_CARD_REF}")
    assert resp.status_code == 503
    assert "corpus_adapter not built" in resp.text


def test_api_doc_adapter_absent_returns_503_json(adapter_absent_client):
    resp = adapter_absent_client.get(f"/api/doc/{ANL_CARD_REF}")
    assert resp.status_code == 503
    assert resp.json() == {"error": "corpus_adapter not built"}
