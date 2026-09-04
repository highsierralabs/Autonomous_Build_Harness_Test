"""(h) edges_for direction/relation checks; (i) supersession_chain over data
located dynamically through the catalog (no new SQL)."""
from __future__ import annotations

from explorer.models import CatalogFilters


def test_edges_for_hand_has_incoming_campaign_child_from_cmp(live_adapter, hand_card_ref, cmp_doc_id):
    hand = live_adapter.card(hand_card_ref)
    assert hand is not None

    edge_set = live_adapter.edges_for(hand)
    incoming_campaign_child = [
        e for e in edge_set.incoming if e.relation == "campaign_child" and e.from_id == cmp_doc_id
    ]
    assert incoming_campaign_child, (
        f"expected an incoming campaign_child edge from {cmp_doc_id!r}; "
        f"incoming relations were {[(e.relation, e.from_id) for e in edge_set.incoming]}"
    )


def test_edges_for_amendment_has_outgoing_amends_from_its_own_stem(live_adapter, a1_card_ref):
    amendment = live_adapter.card(a1_card_ref)
    assert amendment is not None

    edge_set = live_adapter.edges_for(amendment)
    outgoing_amends = [e for e in edge_set.outgoing if e.relation == "amends"]
    assert outgoing_amends, f"expected an outgoing amends edge; outgoing was {edge_set.outgoing}"
    assert outgoing_amends[0].from_id == amendment.filename_stem


def test_supersession_chain_from_a_catalog_located_superseded_card(live_adapter):
    page = live_adapter.catalog(CatalogFilters(status="Superseded"), "date", 1, 20)
    assert page.rows, "expected at least one Superseded card in the live corpus"

    start_id = None
    for row in page.rows:
        edge_set = live_adapter.edges_for(row)
        if any(e.relation == "supersedes" and e.from_id == row.doc_id for e in edge_set.outgoing):
            start_id = row.doc_id
            break
    assert start_id is not None, "expected at least one Superseded card with a resolved supersedes edge"

    chain = live_adapter.supersession_chain(start_id)
    chain_ids = [c.doc_id for c in chain]
    assert start_id in chain_ids
    assert len(set(chain_ids)) >= 2, "a supersession chain must include at least the start and one neighbour"
