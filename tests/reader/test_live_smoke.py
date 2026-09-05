"""Read-only smoke test against the LIVE index (Settings() defaults) --
asserts shape only (task B6 item 5, dispatch conventions block), guarded by
conftest.py's session-scoped corpus_cards_sha + mtime check.
"""
from __future__ import annotations

# Mirrors conftest.py's LIVE_HAND_* constants (this build's own dispatch hand
# and its amendment, verified on disk -- see tests/corpus_adapter/conftest.py).
LIVE_HAND_DOC_ID = "RHACO-HND-20260903-001"
LIVE_HAND_CARD_REF = "handoffs/RHACO-HND-20260903-001_Corpus_Explorer_Autonomous_Build_Dispatch.card.yaml"


def test_live_hand_document_smoke(live_client):
    resp = live_client.get(f"/doc/{LIVE_HAND_CARD_REF}")
    assert resp.status_code == 200
    body = resp.text
    assert f'data-selected-doc-id="{LIVE_HAND_DOC_ID}"' in body
    assert "amended by" in body
