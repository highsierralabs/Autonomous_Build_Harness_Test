"""Read-only smoke test against the LIVE index (Settings() defaults) --
asserts shape only (task B6 item 5, dispatch conventions block), guarded by
conftest.py's session-scoped corpus_cards_sha + mtime check.
"""
from __future__ import annotations

# Mirrors conftest.py's LIVE_HAND_* constants (this build's own dispatch hand
# and its amendment, verified on disk -- see tests/corpus_adapter/conftest.py).
LIVE_HAND_DOC_ID = "RHACO-HND-20260903-001"
LIVE_HAND_CARD_REF = "handoffs/RHACO-HND-20260903-001_Corpus_Explorer_Autonomous_Build_Dispatch.card.yaml"

# task B11: the exact production card the probe's W6 workflow (docs/rounds/
# R04_probe.report.md, docs/probe-qualification/runs/20260905T043147Z/W6.json)
# recorded as `unexpected_http_status[reader_v1_8]: 500` /
# `TypeError: Object of type date is not JSON serializable` on -- an unquoted
# `date:`/`last_human_review:` scalar in this card's own identity block
# (verified on disk, see this round's report). This is the live-corpus
# document task B11 item 3's "live-index smoke on the exact document that
# failed" names.
NATIVE_DATE_DOC_ID = "RHACO_Card_YAML_Schema_Specification_v1_8"
NATIVE_DATE_CARD_REF = "reference/RHACO_Card_YAML_Schema_Specification_v1_8.card.yaml"


def test_live_hand_document_smoke(live_client):
    resp = live_client.get(f"/doc/{LIVE_HAND_CARD_REF}")
    assert resp.status_code == 200
    body = resp.text
    assert f'data-selected-doc-id="{LIVE_HAND_DOC_ID}"' in body
    assert "amended by" in body


def test_live_native_date_card_page_no_longer_500s(live_client):
    resp = live_client.get(f"/doc/{NATIVE_DATE_CARD_REF}")
    assert resp.status_code == 200
    body = resp.text
    assert f'data-selected-doc-id="{NATIVE_DATE_DOC_ID}"' in body
    # A non-empty card panel: the Identity section actually rendered, not a
    # blank/degraded page that merely happens to return 200.
    assert "<dt>Date</dt><dd>2026-06-24</dd>" in body
    assert "datetime.date" not in body
    assert "not JSON serializable" not in body


def test_live_native_date_card_api_no_longer_500s(live_client):
    resp = live_client.get(f"/api/doc/{NATIVE_DATE_CARD_REF}")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["doc_id"] == NATIVE_DATE_DOC_ID
    assert payload["card_panel"]["date"] == "2026-06-24"
    assert payload["card_parsed"]["identity"]["date"] == "2026-06-24"
