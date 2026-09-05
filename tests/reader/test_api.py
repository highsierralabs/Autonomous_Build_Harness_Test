"""GET /api/doc/{card_ref} JSON twin (task B6 item 3/5): carries the same
sha256, lines, headings and mismatch fields as the page.
"""
from __future__ import annotations

import hashlib
import os

ANL_CARD_REF = "reports/RHACO-ANL-20260115-002_Fixture_Analysis.card.yaml"
QUARTZ_LINE = 15

_MD_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "fixtures", "corpus",
    "reports", "RHACO-ANL-20260115-002_Fixture_Analysis.md",
)


def test_api_doc_matches_page_sha_lines_headings_mismatch(client):
    page = client.get(f"/doc/{ANL_CARD_REF}")
    api = client.get(f"/api/doc/{ANL_CARD_REF}")
    assert api.status_code == 200
    data = api.json()

    expected_sha = hashlib.sha256(open(_MD_PATH, "rb").read()).hexdigest()
    assert data["document"]["sha256"] == expected_sha
    assert f'data-body-sha256="{expected_sha}"' in page.text

    assert data["document"]["lines"][QUARTZ_LINE - 1]["text"] == (
        "the quartz lattice lantern glows only in this fixture document"
    )
    assert len(data["document"]["lines"]) == data["document"]["line_count"] == 21

    heading_texts = [h["text"] for h in data["document"]["headings"]]
    assert "1. Purpose" in heading_texts
    assert all(h["line_verified"] for h in data["document"]["headings"])

    assert data["index_mismatch_fields"] == []
    assert data["doc_id"] == "RHACO-ANL-20260115-002"
    assert data["card_row"]["doc_id"] == "RHACO-ANL-20260115-002"


def test_api_doc_line_jump_field(client):
    resp = client.get(f"/api/doc/{ANL_CARD_REF}?line={QUARTZ_LINE}")
    data = resp.json()
    assert data["jump_found"] is True
    assert data["jump_line_attr"] == str(QUARTZ_LINE)
    hit_lines = [ln for ln in data["document"]["lines"] if ln["is_hit"]]
    assert len(hit_lines) == 1
    assert hit_lines[0]["number"] == QUARTZ_LINE


def test_api_doc_not_found_returns_404_json(client):
    resp = client.get("/api/doc/reports/does_not_exist.card.yaml")
    assert resp.status_code == 404
    assert resp.json() == {"error": "card not found"}
