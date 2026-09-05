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


# -- R08 dispatch item 2 (critic round 1, ranked issue 5): identifier-mode
# evidence disclosure. Identifier results previously carried no Evidence at
# all; these tests would have caught that -- each asserts content the old
# `_run_identifier` (which built a SearchView with no evidence on IdentifierRow)
# could not have produced. ---------------------------------------------------


def test_identifier_evidence_discloses_exact_match_no_ranking_no_fusion_no_degradation(fixture_client):
    resp = fixture_client.get("/search", params={"q": "E000777", "mode": "identifier"})
    assert resp.status_code == 200
    body = resp.text
    assert "Why this result" in body
    assert "not applicable -- exact alias lookup (resolve_identifier), no ranking" in body
    assert "not applicable -- no fusion in this mode" in body
    assert "not applicable -- identifier mode is an exact alias lookup" in body

    data = fixture_client.get("/api/search", params={"q": "E000777", "mode": "identifier"}).json()
    evidence = data["identifier_rows"][0]["evidence"]
    assert evidence["exact_identifier_match"] is True
    assert evidence["retrieval_mode"] == "identifier"


def test_identifier_shared_id_evidence_appears_once_and_never_picks_a_row(fixture_client):
    """O7: an id with several card rows (a hand and its amendment) gets ONE
    evidence disclosure for the id's resolution, never one per card row --
    a disclosure repeated per card, or omitted, would both misstate what
    happened (the query resolved once; the several rows are a corpus fact,
    not several retrieval answers)."""
    resp = fixture_client.get("/search", params={"q": "RHACO-HND-20260115-003", "mode": "identifier"})
    assert resp.status_code == 200
    body = resp.text
    assert f'data-card-ref="{HAND_CARD_REF}"' in body
    assert f'data-card-ref="{AMENDMENT_CARD_REF}"' in body
    assert body.count("Why this result") == 1
    assert "none is preferred over another" in body


def test_identifier_unknown_id_evidence_discloses_no_exact_match(fixture_client):
    resp = fixture_client.get("/search", params={"q": "RHACO-XXX-99999999-999", "mode": "identifier"})
    assert resp.status_code == 200
    body = resp.text
    assert "no card row in the index" in body
    assert "Why this result" in body

    data = fixture_client.get("/api/search", params={"q": "RHACO-XXX-99999999-999", "mode": "identifier"}).json()
    evidence = data["identifier_rows"][0]["evidence"]
    assert evidence["exact_identifier_match"] is False
    assert evidence["retrieval_mode"] == "identifier"
