"""Read-only smoke test against the LIVE index (Settings() defaults) --
asserts shape only (task B8 deliverable 5), guarded by conftest.py's
session-scoped corpus_cards_sha + mtime check. The target is this build's own
dispatch campaign card (RHACO-CMP-20260903-001), verified via the adapter
(read-only, this round's report Evidence) to carry campaign children on the
live index today, including RHACO-HND-20260903-001."""
from __future__ import annotations

from tests.lineage.conftest import LIVE_CMP_CARD_REF, LIVE_CMP_CHILD_DOC_ID, LIVE_CMP_DOC_ID


def test_live_cmp_campaign_lineage_smoke(live_client):
    resp = live_client.get(f"/lineage/{LIVE_CMP_CARD_REF}")
    assert resp.status_code == 200
    body = resp.text
    assert len(body) > 0
    assert f'data-selected-doc-id="{LIVE_CMP_DOC_ID}"' in body
    assert f'data-card-ref="{LIVE_CMP_CARD_REF}"' in body
    assert LIVE_CMP_CHILD_DOC_ID in body  # a real campaign child is present in the subtree/graph


def test_live_cmp_campaign_lineage_api_smoke(live_client):
    resp = live_client.get(f"/api/lineage/{LIVE_CMP_CARD_REF}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["doc_id"] == LIVE_CMP_DOC_ID
    assert data["subtree"] is not None
    child_ids = {n["card"]["doc_id"] for n in data["subtree"]["nodes"]}
    assert LIVE_CMP_CHILD_DOC_ID in child_ids
