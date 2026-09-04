"""(c) cards_for_doc_id / card round-trip; (f) resolve_identifier."""
from __future__ import annotations


def test_cards_for_doc_id_returns_hand_and_amendment(live_adapter, hand_doc_id, hand_card_ref, a1_card_ref):
    cards = live_adapter.cards_for_doc_id(hand_doc_id)
    assert len(cards) == 2, f"expected the hand + its Amendment A1, got {[c.card_ref for c in cards]}"

    card_refs = {c.card_ref for c in cards}
    assert card_refs == {hand_card_ref, a1_card_ref}
    for c in cards:
        assert c.doc_id == hand_doc_id

    by_ref = {c.card_ref: c for c in cards}
    assert by_ref[hand_card_ref].is_amendment is False
    assert by_ref[a1_card_ref].is_amendment is True


def test_card_round_trips_for_hand_and_amendment(live_adapter, hand_doc_id, hand_card_ref, a1_card_ref):
    via_lookup = {c.card_ref: c for c in live_adapter.cards_for_doc_id(hand_doc_id)}

    for card_ref in (hand_card_ref, a1_card_ref):
        original = via_lookup[card_ref]

        fetched = live_adapter.card(card_ref)
        assert fetched is not None, f"card({card_ref!r}) returned None"
        assert fetched.yaml_path == original.yaml_path
        assert fetched.doc_id == original.doc_id
        assert fetched.card_ref == card_ref
        assert fetched.title == original.title


def test_resolve_identifier_exact_campaign_id(live_adapter, cmp_doc_id):
    assert live_adapter.resolve_identifier(cmp_doc_id) == [cmp_doc_id]
