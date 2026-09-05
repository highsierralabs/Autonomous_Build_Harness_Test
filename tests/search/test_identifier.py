"""Identifier mode (task B5 deliverable 5, first bullet): TestClient against
the fixture index. O7 -- an id with several card rows (a hand and its
amendment) lists every row, never one silently; an id with no card row is
listed as the literal id with the "no card row in the index" text.
"""
from __future__ import annotations

EVT_CARD_REF = "reports/RHACO-EVT-20260115-004_Fixture_Event_E000777.card.yaml"
HAND_CARD_REF = "handoffs/RHACO-HND-20260115-003_Fixture_Handoff.card.yaml"
AMENDMENT_CARD_REF = "handoffs/RHACO-HND-20260115-003_Fixture_Handoff_Amendment_A1.card.yaml"


def test_identifier_event_id_lists_evt_card(fixture_client):
    resp = fixture_client.get("/search", params={"q": "E000777", "mode": "identifier"})
    assert resp.status_code == 200
    body = resp.text
    assert 'data-mode="identifier"' in body
    assert 'data-mode-effective="identifier"' in body
    assert 'data-doc-id="RHACO-EVT-20260115-004"' in body
    assert f'data-card-ref="{EVT_CARD_REF}"' in body
    assert f"/doc/{EVT_CARD_REF}" in body


def test_identifier_shared_id_lists_hand_and_amendment_distinct_card_refs(fixture_client):
    resp = fixture_client.get("/search", params={"q": "RHACO-HND-20260115-003", "mode": "identifier"})
    assert resp.status_code == 200
    body = resp.text
    assert body.count('data-doc-id="RHACO-HND-20260115-003"') >= 1
    assert f'data-card-ref="{HAND_CARD_REF}"' in body
    assert f'data-card-ref="{AMENDMENT_CARD_REF}"' in body
    assert f"/doc/{HAND_CARD_REF}" in body
    assert f"/doc/{AMENDMENT_CARD_REF}" in body


def test_identifier_unknown_id_yields_no_card_row_line(fixture_client):
    resp = fixture_client.get("/search", params={"q": "RHACO-XXX-99999999-999", "mode": "identifier"})
    assert resp.status_code == 200
    body = resp.text
    assert "no card row in the index" in body
    assert "RHACO-XXX-99999999-999" in body


def test_identifier_mode_via_api_matches_page(fixture_client):
    resp = fixture_client.get("/api/search", params={"q": "RHACO-HND-20260115-003", "mode": "identifier"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["mode_effective"] == "identifier"
    assert len(data["identifier_rows"]) == 1
    row = data["identifier_rows"][0]
    assert row["doc_id"] == "RHACO-HND-20260115-003"
    card_refs = {c["card"]["card_ref"] for c in row["cards"]}
    assert card_refs == {HAND_CARD_REF, AMENDMENT_CARD_REF}
