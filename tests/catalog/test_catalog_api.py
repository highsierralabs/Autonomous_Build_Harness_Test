"""TestClient tests for GET /api/catalog -- the JSON twin (task B4 items 2, 4).

Cross-checks: for the same query, /api/catalog reports the same total, row
set, and facets as the HTML page (dataclasses.asdict(view) over the same
CatalogView the page renders from).
"""
from __future__ import annotations

import re

CARD_REF_RE = re.compile(r'data-card-ref="([^"]+)"')


def test_api_catalog_no_filter_shape_and_total(client):
    resp = client.get("/api/catalog")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 7
    assert len(data["rows"]) == 7
    assert data["index_total_cards"] == 7
    assert data["page"] == 1
    assert data["page_size"] == 50
    assert data["page_count"] == 1
    assert data["has_prev"] is False
    assert data["has_next"] is False
    assert data["no_matches"] is False
    assert data["sort_column"] == "date"
    assert data["sort_direction"] == "desc"

    # every CardRow field plus card_ref / doc_ref / frozen
    row = data["rows"][0]
    for key in ("yaml_path", "doc_id", "doc_type", "date", "status", "card_ref", "doc_ref", "frozen", "programs", "tags"):
        assert key in row, f"missing {key!r} in API row: {sorted(row)}"


def test_api_catalog_facets_are_present_and_not_fabricated(client):
    resp = client.get("/api/catalog")
    data = resp.json()
    doc_type_values = {v for v, _c in data["global_facets"]["doc_types"]}
    assert doc_type_values == {"ANL", "CMP", "EVT", "HND", "REF"}
    assert data["global_facets"]["lifecycle_states"] == [["OPEN", 1]]


def test_api_catalog_matches_page_for_doc_type_cmp(client):
    page_resp = client.get("/", params={"doc_type": "CMP"})
    api_resp = client.get("/api/catalog", params={"doc_type": "CMP"})
    assert api_resp.status_code == 200

    page_refs = set(CARD_REF_RE.findall(page_resp.text))
    data = api_resp.json()
    api_refs = {row["card_ref"] for row in data["rows"]}

    assert page_refs == api_refs
    assert data["total"] == len(page_refs) == 1
    assert data["show_lifecycle_control"] is True
    assert data["rows"][0]["lifecycle_state"] == "OPEN"


def test_api_catalog_matches_page_for_doc_type_hnd(client):
    page_resp = client.get("/", params={"doc_type": "HND"})
    api_resp = client.get("/api/catalog", params={"doc_type": "HND"})

    page_refs = set(CARD_REF_RE.findall(page_resp.text))
    data = api_resp.json()
    api_refs = {row["card_ref"] for row in data["rows"]}

    assert page_refs == api_refs
    assert len(api_refs) == 2
    assert data["show_lifecycle_control"] is False
    assert all(row["lifecycle_state"] is None for row in data["rows"])


def test_api_catalog_no_match_reports_zero_total_and_empty_rows(client):
    resp = client.get("/api/catalog", params={"doc_type": "SOP"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["rows"] == []
    assert data["no_matches"] is True
    assert "no cards match" in data["no_match_text"]


def test_api_catalog_filters_in_force_echoed(client):
    resp = client.get("/api/catalog", params={"program": "DetPhys", "sort": "title:asc"})
    data = resp.json()
    assert data["filters"]["program"] == "DetPhys"
    assert data["sort"] == "title:asc"
    assert data["sort_column"] == "title"
    assert data["sort_direction"] == "asc"
    assert data["total"] == 2
