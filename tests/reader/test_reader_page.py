"""GET /doc/{card_ref} against the fixture index (task B6 item 5). TestClient
only, no server process (ARCHITECTURE.md A18); every functional assertion
runs against the deterministic fixture built by conftest.fixture_db_path.
"""
from __future__ import annotations

ANL_CARD_REF = "reports/RHACO-ANL-20260115-002_Fixture_Analysis.card.yaml"
HND_CARD_REF = "handoffs/RHACO-HND-20260115-003_Fixture_Handoff.card.yaml"
AMENDMENT_CARD_REF = "handoffs/RHACO-HND-20260115-003_Fixture_Handoff_Amendment_A1.card.yaml"
REF_V1_0_CARD_REF = "reference/RHACO_Fixture_Reference_v1_0.card.yaml"
REF_V1_1_CARD_REF = "reference/RHACO_Fixture_Reference_v1_1.card.yaml"
CMP_CARD_REF = "reports/RHACO-CMP-20260115-001_Fixture_Campaign.card.yaml"
ARCHIVED_CARD_REF = "docs_archive/RHACO-OBS-20260101-001_Fixture_Archived.card.yaml"

QUARTZ_DOC_ID = "RHACO-ANL-20260115-002"
QUARTZ_LINE = 15


# -- basic page shape / dual-region structure --------------------------------

def test_doc_page_ok_two_landmarks_and_body_sha(client):
    resp = client.get(f"/doc/{ANL_CARD_REF}")
    assert resp.status_code == 200
    body = resp.text
    assert f'data-selected-doc-id="{QUARTZ_DOC_ID}"' in body
    assert 'id="document-heading"' in body and ">Document<" in body
    assert 'id="card-heading"' in body and "Card (catalog metadata)" in body
    assert 'data-mode="reader"' in body

    import hashlib
    import os

    md_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "fixtures", "corpus",
        "reports", "RHACO-ANL-20260115-002_Fixture_Analysis.md",
    )
    expected_sha = hashlib.sha256(open(md_path, "rb").read()).hexdigest()
    assert f'data-body-sha256="{expected_sha}"' in body


def test_doc_page_headings_have_slug_ids_and_verified_lines(client):
    resp = client.get(f"/doc/{ANL_CARD_REF}")
    body = resp.text
    assert 'id="1-purpose"' in body
    assert 'data-line="3"' in body  # "## 1. Purpose" is source line 3
    assert 'data-line-verified="false"' not in body


def test_doc_page_card_index_mismatch_empty_on_clean_fixture(client):
    resp = client.get(f"/doc/{ANL_CARD_REF}")
    assert 'data-card-index-mismatch=""' in resp.text


# -- line jump ----------------------------------------------------------------

def test_line_jump_marks_hit_and_sets_jump_line(client):
    resp = client.get(f"/doc/{ANL_CARD_REF}?line={QUARTZ_LINE}")
    body = resp.text
    assert f'data-jump-line="{QUARTZ_LINE}"' in body
    assert f'id="L{QUARTZ_LINE}" data-line="{QUARTZ_LINE}" class="source-line hit"' in body
    assert "quartz lattice lantern" in body
    assert f"jumped to line {QUARTZ_LINE}" in body


def test_line_jump_out_of_range_reports_not_found(client):
    resp = client.get(f"/doc/{ANL_CARD_REF}?line=9999")
    body = resp.text
    assert 'data-jump-line=""' in body
    assert "line 9999 not found (document has 21 lines)" in body


# -- amendment / parent -------------------------------------------------------

def test_amendment_page_shows_amendment_of_parent(client):
    resp = client.get(f"/doc/{AMENDMENT_CARD_REF}")
    body = resp.text
    assert resp.status_code == 200
    assert "amendment of" in body
    assert f'href="/doc/{HND_CARD_REF}"' in body


def test_parent_page_shows_amended_by(client):
    resp = client.get(f"/doc/{HND_CARD_REF}")
    body = resp.text
    assert resp.status_code == 200
    assert "amended by" in body
    assert f'href="/doc/{AMENDMENT_CARD_REF}"' in body


# -- campaign_child / unresolved cites ----------------------------------------

def test_hnd_page_lists_incoming_campaign_child_and_unresolved_cites(client):
    resp = client.get(f"/doc/{HND_CARD_REF}")
    body = resp.text
    assert "campaign child of" in body
    assert f'href="/doc/{CMP_CARD_REF}"' in body
    assert "RHACO-ANL-20260101-099" in body
    assert "unresolved" in body


# -- supersession banner -------------------------------------------------------

def test_v1_0_page_shows_superseded_banner_and_frozen_text(client):
    resp = client.get(f"/doc/{REF_V1_0_CARD_REF}")
    body = resp.text
    assert resp.status_code == 200
    assert "This version is superseded" in body
    assert f'href="/doc/{REF_V1_1_CARD_REF}"' in body
    assert ">frozen<" in body


def test_v1_1_page_has_no_superseded_banner(client):
    resp = client.get(f"/doc/{REF_V1_1_CARD_REF}")
    assert 'data-superseded-banner="true"' not in resp.text


# -- lifecycle_state (S4: CMP-only, informational elsewhere) ------------------

def test_cmp_page_shows_cmp_lifecycle_state_label(client):
    resp = client.get(f"/doc/{CMP_CARD_REF}")
    body = resp.text
    assert "CMP lifecycle state" in body
    assert ">OPEN<" in body


def test_anl_page_has_no_lifecycle_label(client):
    resp = client.get(f"/doc/{ANL_CARD_REF}")
    body = resp.text
    assert "CMP lifecycle state" not in body
    assert "informational (non-CMP)" not in body


# -- 404s -----------------------------------------------------------------

def test_docs_archive_card_ref_is_404(client):
    resp = client.get(f"/doc/{ARCHIVED_CARD_REF}")
    assert resp.status_code == 404
    assert "no card at" in resp.text


def test_dotdot_traversal_card_ref_is_404(client):
    resp = client.get("/doc/reports/%2e%2e/%2e%2e/ARCHITECTURE.md")
    assert resp.status_code == 404


def test_build_view_rejects_dotdot_traversal_directly(fixture_settings):
    from explorer.corpus_adapter.adapter import CorpusAdapter
    from explorer.reader.service import build_view

    adapter = CorpusAdapter(fixture_settings)
    assert build_view(adapter, fixture_settings, "../../ARCHITECTURE.md", None) is None
    assert build_view(adapter, fixture_settings, "no/such/card.card.yaml", None) is None
