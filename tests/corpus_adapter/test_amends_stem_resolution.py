"""Dispatch R07 item 3: the deferred amends click-through change request
(SCOPE.md's "Click-through from an amends edge to the amendment" row).
`edges_for` now resolves an `amends` edge's `from_id` (the amendment's
filename stem, CONSTRAINTS.md O8) through D-Q12 (`cards.doc_filename`)
instead of D-Q3 (`doc_id`), which a stem never matches.

Both tests below run against the live corpus's known shared-doc_id
parent/amendment pair (conftest.py's HAND_DOC_ID / A1_CARD_REF: this build's
own dispatch hand and its Amendment A1 -- re-verified live before writing
this file, see this round's report "Evidence").
"""
from __future__ import annotations


def test_parent_page_incoming_amends_edge_now_links_to_the_amendment(live_adapter, hand_card_ref, a1_card_ref):
    """The row's own repro: on the parent's lineage page, the incoming
    `amends` edge previously carried `source_cards=[]` (typed, directional
    text with no link) because `from_id` is a filename stem and D-Q3 only
    matches `doc_id`. It must now resolve to the amendment's own card."""
    hand = live_adapter.card(hand_card_ref)
    assert hand is not None
    amendment = live_adapter.card(a1_card_ref)
    assert amendment is not None

    edge_set = live_adapter.edges_for(hand)
    incoming_amends = [e for e in edge_set.incoming if e.relation == "amends"]
    assert incoming_amends, f"expected an incoming amends edge on {hand_card_ref!r}"

    edge = incoming_amends[0]
    assert edge.from_id == amendment.filename_stem
    assert edge.source_cards, (
        "source_cards must resolve the amendment's filename stem to its own card "
        "(D-Q12) -- previously always empty for an amends edge's from_id"
    )
    assert any(c.card_ref == amendment.card_ref for c in edge.source_cards), (
        f"expected the amendment's own card_ref {amendment.card_ref!r} among "
        f"source_cards {[c.card_ref for c in edge.source_cards]!r}"
    )


def test_amendments_own_page_degenerate_self_classification_is_unchanged_by_the_fix(
    live_adapter, hand_card_ref, a1_card_ref
):
    """Caution 1 (dispatch R07 item 3): the amendment shares its `doc_id`
    with its parent (verified: hand.doc_id == amendment.doc_id), so on the
    amendment's OWN lineage page its own `amends` edge is double-classified
    -- it appears in BOTH `outgoing` (from_id == this card's own stem matches)
    AND `incoming` (to_id == the shared doc_id also matches this card's own
    doc_id) -- a pre-existing defect (lineage round-1 open issue; critic
    ranked issue 7), independent of this round's classification logic, which
    is untouched here.

    What this round's stem-aware fix DOES change: `source_cards` on that
    self-classified incoming copy, which was empty before (no link) and now
    resolves to the amendment's own card (D-Q12) -- i.e. the fix turns the
    incoming half of this self-edge from unlinked text into a link that
    points to itself. This test pins that exact before/after so the
    lineage builder can see the ground moved under this degenerate case
    without having to re-derive it.
    """
    hand = live_adapter.card(hand_card_ref)
    amendment = live_adapter.card(a1_card_ref)
    assert hand is not None and amendment is not None
    assert hand.doc_id == amendment.doc_id, (
        "this test's premise (a shared doc_id between parent and amendment) "
        "no longer holds on the live corpus -- re-derive the caution from "
        "current data before trusting this test's assertions"
    )

    edge_set = live_adapter.edges_for(amendment)
    outgoing_amends = [e for e in edge_set.outgoing if e.relation == "amends"]
    incoming_amends = [e for e in edge_set.incoming if e.relation == "amends"]
    assert outgoing_amends, "expected the amendment's own outgoing amends edge"
    assert incoming_amends, (
        "expected the SAME amends edge also classified incoming -- the "
        "double-classification this test documents; if this now fails, the "
        "degenerate case may have been fixed or the corpus changed, either "
        "of which is worth flagging to the lineage builder, not silencing"
    )

    # Both classifications are the one edge (same from_id/to_id pair).
    assert outgoing_amends[0].from_id == incoming_amends[0].from_id == amendment.filename_stem
    assert outgoing_amends[0].to_id == incoming_amends[0].to_id == hand.doc_id

    # The fix's effect: source_cards on the incoming copy now self-resolves.
    assert any(c.card_ref == amendment.card_ref for c in incoming_amends[0].source_cards), (
        "expected the incoming copy's source_cards to now include the amendment's "
        "own card (a self-link) -- the documented consequence of the stem-aware "
        "fix on this pre-existing degenerate case"
    )
