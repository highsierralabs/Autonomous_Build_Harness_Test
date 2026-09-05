"""TestClient tests for GET / (task B4 item 4). No server process is launched
(ARCHITECTURE.md A18); every assertion runs against the deterministic fixture
index built by tests/catalog/conftest.py.

Fixture facts asserted below (re-derived independently from a fresh fixture
build before writing any assertion; docs/rounds/R01_probe.report.md carries
the same inventory):
  7 cards outside docs_archive/: CMP (RHACO-CMP-20260115-001, lifecycle_state
  OPEN), ANL (RHACO-ANL-20260115-002, programs DetPhys+Radon), HND parent +
  HND amendment (both RHACO-HND-20260115-003, distinct card_ref, neither
  carries a lifecycle_state), EVT (RHACO-EVT-20260115-004, program DetPhys),
  REF v1_0 (RHACO_Fixture_Reference_v1_0, status Superseded -> frozen), REF
  v1_1 (RHACO_Fixture_Reference_v1_1, status Active).
"""
from __future__ import annotations

import re

CARD_REF_RE = re.compile(r'data-card-ref="([^"]+)"')
DOC_ID_RE = re.compile(r'data-doc-id="([^"]+)"')

HND_CARD_REF = "handoffs/RHACO-HND-20260115-003_Fixture_Handoff.card.yaml"
HND_AMENDMENT_CARD_REF = "handoffs/RHACO-HND-20260115-003_Fixture_Handoff_Amendment_A1.card.yaml"
REF_V1_0_CARD_REF = "reference/RHACO_Fixture_Reference_v1_0.card.yaml"
REF_V1_1_CARD_REF = "reference/RHACO_Fixture_Reference_v1_1.card.yaml"
CMP_CARD_REF = "reports/RHACO-CMP-20260115-001_Fixture_Campaign.card.yaml"
ANL_CARD_REF = "reports/RHACO-ANL-20260115-002_Fixture_Analysis.card.yaml"
EVT_CARD_REF = "reports/RHACO-EVT-20260115-004_Fixture_Event_E000777.card.yaml"

ALL_CARD_REFS = {
    HND_CARD_REF, HND_AMENDMENT_CARD_REF, REF_V1_0_CARD_REF, REF_V1_1_CARD_REF,
    CMP_CARD_REF, ANL_CARD_REF, EVT_CARD_REF,
}


def test_home_lists_every_fixture_card_with_doc_id_and_total(client):
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.text
    assert 'data-mode="catalog"' in body
    assert 'id="keyhelp"' in body

    card_refs = CARD_REF_RE.findall(body)
    assert set(card_refs) == ALL_CARD_REFS
    assert len(card_refs) == 7

    assert 'data-total-indexed="7"' in body
    assert 'data-total-matching="7"' in body


def test_doc_type_cmp_returns_exactly_the_cmp_row_with_lifecycle(client):
    resp = client.get("/", params={"doc_type": "CMP"})
    assert resp.status_code == 200
    body = resp.text
    card_refs = CARD_REF_RE.findall(body)
    assert card_refs == [CMP_CARD_REF]
    assert 'data-lifecycle-state="OPEN"' in body
    # the SEPARATE lifecycle control is rendered
    assert 'CMP lifecycle state (campaigns only)' in body
    assert 'data-total-matching="1"' in body


def test_doc_type_hnd_returns_both_rows_with_empty_lifecycle_and_no_control(client):
    resp = client.get("/", params={"doc_type": "HND"})
    assert resp.status_code == 200
    body = resp.text
    card_refs = CARD_REF_RE.findall(body)
    assert set(card_refs) == {HND_CARD_REF, HND_AMENDMENT_CARD_REF}
    assert len(card_refs) == 2
    # both HND rows share one doc_id but are distinct rows (distinct card_ref)
    doc_ids = DOC_ID_RE.findall(body)
    assert doc_ids.count("RHACO-HND-20260115-003") == 2
    # empty lifecycle cell on both rows
    assert body.count('data-lifecycle-state=""') >= 2
    # the lifecycle control itself is absent -- the under-filter facets carry
    # no lifecycle_state value for doc_type=HND
    assert "CMP lifecycle state (campaigns only)" not in body


def test_status_superseded_returns_v1_0_marked_frozen(client):
    resp = client.get("/", params={"status": "Superseded"})
    assert resp.status_code == 200
    body = resp.text
    card_refs = CARD_REF_RE.findall(body)
    assert card_refs == [REF_V1_0_CARD_REF]
    assert 'data-status="Superseded"' in body
    assert "frozen" in body


def test_program_filter_narrows_correctly(client):
    resp = client.get("/", params={"program": "DetPhys"})
    assert resp.status_code == 200
    card_refs = CARD_REF_RE.findall(resp.text)
    assert set(card_refs) == {ANL_CARD_REF, EVT_CARD_REF}
    assert len(card_refs) == 2


def test_tag_filter_narrows_correctly(client):
    resp = client.get("/", params={"tag": "amendment"})
    assert resp.status_code == 200
    card_refs = CARD_REF_RE.findall(resp.text)
    assert card_refs == [HND_AMENDMENT_CARD_REF]


def test_sort_title_asc_orders_by_title(client):
    resp = client.get("/", params={"sort": "title:asc"})
    assert resp.status_code == 200
    card_refs = CARD_REF_RE.findall(resp.text)
    assert card_refs == [
        ANL_CARD_REF, CMP_CARD_REF, EVT_CARD_REF,
        HND_CARD_REF, HND_AMENDMENT_CARD_REF,
        REF_V1_0_CARD_REF, REF_V1_1_CARD_REF,
    ]
    assert 'data-sort-column="title"' in resp.text
    assert 'data-sort-direction="asc"' in resp.text


def test_date_from_bounds_the_set(client):
    resp = client.get("/", params={"date_from": "2026-01-15"})
    assert resp.status_code == 200
    card_refs = CARD_REF_RE.findall(resp.text)
    assert set(card_refs) == {ANL_CARD_REF, CMP_CARD_REF, EVT_CARD_REF, HND_CARD_REF, HND_AMENDMENT_CARD_REF}
    assert len(card_refs) == 5


def test_date_to_bounds_the_set(client):
    resp = client.get("/", params={"date_to": "2026-01-10"})
    assert resp.status_code == 200
    card_refs = CARD_REF_RE.findall(resp.text)
    assert set(card_refs) == {REF_V1_0_CARD_REF, REF_V1_1_CARD_REF}


def test_no_matching_filter_value_yields_zero_rows_and_no_fabrication(client):
    resp = client.get("/", params={"doc_type": "SOP"})
    assert resp.status_code == 200
    body = resp.text
    assert CARD_REF_RE.findall(body) == []
    assert "no cards match" in body
    assert 'data-total-matching="0"' in body


def test_pagination_page_size_3_partitions_the_seven_rows(client):
    seen: list[str] = []
    for page in (1, 2, 3):
        resp = client.get("/", params={"page_size": 3, "page": page, "sort": "doc_id:asc"})
        assert resp.status_code == 200
        refs = CARD_REF_RE.findall(resp.text)
        assert 1 <= len(refs) <= 3
        seen.extend(refs)
        assert f"Page {page} of 3" in resp.text
    assert sorted(seen) == sorted(ALL_CARD_REFS)
    assert len(seen) == 7


def test_pagination_links_present_and_preserve_filters(client):
    resp = client.get("/", params={"page_size": 3, "program": "Infra", "sort": "doc_id:asc"})
    assert resp.status_code == 200
    body = resp.text
    assert "program=Infra" in body
    assert "page_size=3" in body
    assert "Next page" in body


def test_status_and_lifecycle_state_never_merged(client):
    resp = client.get("/", params={"doc_type": "CMP"})
    body = resp.text
    assert 'data-status="Active"' in body
    assert 'data-lifecycle-state="OPEN"' in body
    # the CMP row's status cell must not itself carry the lifecycle value
    status_cell_match = re.search(r'<td>\s*Active(?:\s*<span class="frozen">frozen</span>)?\s*</td>', body)
    assert status_cell_match is not None
    assert "OPEN" not in status_cell_match.group(0)


def test_clear_filters_link_present(client):
    resp = client.get("/", params={"doc_type": "CMP"})
    assert '<a href="/">Clear filters</a>' in resp.text
