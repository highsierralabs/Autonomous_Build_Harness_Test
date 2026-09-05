"""Known-bad qualification cases (task B6 item 5; ARCHITECTURE.md section 6):
`stale_card` must surface as a non-empty data-card-index-mismatch, `broken_jump`
must surface as at least one data-line-verified="false" heading plus a non-empty
anchor-mismatch notice. Faults are honoured only against the fixture db (outside
both RHACO trees, explorer/faults.py) -- these clients are built with
`fault=...` against that same fixture db path.
"""
from __future__ import annotations

ANL_CARD_REF = "reports/RHACO-ANL-20260115-002_Fixture_Analysis.card.yaml"


def test_stale_card_fault_shows_title_and_status_mismatch(stale_card_client):
    resp = stale_card_client.get(f"/doc/{ANL_CARD_REF}")
    assert resp.status_code == 200
    body = resp.text
    assert 'data-card-index-mismatch="title,status"' in body
    assert "index row differs from card file: title, status" in body
    assert "[STALE]" in body  # the mutated index-row title, shown "as indexed"


def test_broken_jump_fault_marks_a_heading_unverified(broken_jump_client):
    resp = broken_jump_client.get(f"/doc/{ANL_CARD_REF}")
    assert resp.status_code == 200
    body = resp.text
    assert 'data-line-verified="false"' in body
    assert "anchor mismatch" in body


def test_broken_jump_fault_api_matches_page(broken_jump_client):
    resp = broken_jump_client.get(f"/api/doc/{ANL_CARD_REF}")
    assert resp.status_code == 200
    data = resp.json()
    mismatches = data["document"]["anchor_mismatches"]
    assert mismatches, "expected at least one anchor mismatch in the JSON twin"
    assert all(h["line_verified"] is False for h in mismatches)
