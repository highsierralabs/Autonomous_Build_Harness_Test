"""KB3 qualification case (task B8 deliverable 5, "the KB3 observable";
ARCHITECTURE.md section 6): `reverse_edges` swaps from/to on the adapter's
returned edges. The lineage page renders whatever the adapter returns,
faithfully -- this test captures the CLEAN values first and asserts the
faulted render states the SWAP explicitly, not merely "a fault is present"
(dispatch instruction: "Capture the clean values first and compare against
them, so the test states the swap rather than merely asserting a fault is
present")."""
from __future__ import annotations

from tests.lineage.conftest import ANL_DOC_ID, CMP_CARD_REF, CMP_DOC_ID, HND_DOC_ID


def test_reverse_edges_fault_swaps_from_and_to(client, reverse_edges_client):
    clean = client.get(f"/lineage/{CMP_CARD_REF}")
    assert clean.status_code == 200
    clean_body = clean.text

    # Clean baseline: the CMP center's campaign_child edge to the HND child
    # is outgoing, from=CMP, to=HND (fixture facts, docs/rounds/R01_probe.report.md).
    clean_marker = (
        f'data-relation="campaign_child" data-edge-from="{CMP_DOC_ID}" '
        f'data-edge-to="{HND_DOC_ID}" data-edge-direction="outgoing"'
    )
    assert clean_marker in clean_body, "clean render did not have the expected outgoing edge to compare against"

    faulted = reverse_edges_client.get(f"/lineage/{CMP_CARD_REF}")
    assert faulted.status_code == 200
    faulted_body = faulted.text

    # The clean marker must be GONE under the fault (this is the swap, not a
    # coincidental duplicate) ...
    assert clean_marker not in faulted_body

    # ... and the SAME named edge (relation="campaign_child", the CMP<->HND
    # pair) must now appear with from_id and to_id SWAPPED, and its direction
    # flipped from outgoing to incoming (module docstring: the lineage page
    # never re-derives direction -- it renders whichever EdgeSet bucket the
    # adapter placed the swapped edge into).
    swapped_marker = (
        f'data-relation="campaign_child" data-edge-from="{HND_DOC_ID}" '
        f'data-edge-to="{CMP_DOC_ID}" data-edge-direction="incoming"'
    )
    assert swapped_marker in faulted_body

    # The second campaign_child edge (to ANL) shows the same swap-and-flip.
    clean_marker_anl = (
        f'data-relation="campaign_child" data-edge-from="{CMP_DOC_ID}" '
        f'data-edge-to="{ANL_DOC_ID}" data-edge-direction="outgoing"'
    )
    swapped_marker_anl = (
        f'data-relation="campaign_child" data-edge-from="{ANL_DOC_ID}" '
        f'data-edge-to="{CMP_DOC_ID}" data-edge-direction="incoming"'
    )
    assert clean_marker_anl in clean_body
    assert clean_marker_anl not in faulted_body
    assert swapped_marker_anl in faulted_body


def test_reverse_edges_fault_api_matches_page(client, reverse_edges_client):
    """CMP's clean edge set is two OUTGOING campaign_child edges (to HND, to
    ANL) and two INCOMING cites edges (from HND, from ANL -- both children
    `depends_on` the campaign, fixture inventory). The fault swaps from/to on
    every edge, so campaign_child moves outgoing->incoming AND cites moves
    incoming->outgoing, both with from_id/to_id swapped -- verified against
    the adapter directly in this round's report, Evidence."""
    faulted_page = reverse_edges_client.get(f"/lineage/{CMP_CARD_REF}").text
    faulted_api = reverse_edges_client.get(f"/api/lineage/{CMP_CARD_REF}").json()

    incoming_pairs = {(e["from_id"], e["to_id"], e["relation"]) for e in faulted_api["incoming"]}
    outgoing_pairs = {(e["from_id"], e["to_id"], e["relation"]) for e in faulted_api["outgoing"]}
    assert (HND_DOC_ID, CMP_DOC_ID, "campaign_child") in incoming_pairs
    assert (ANL_DOC_ID, CMP_DOC_ID, "campaign_child") in incoming_pairs
    assert (CMP_DOC_ID, HND_DOC_ID, "cites") in outgoing_pairs
    assert (CMP_DOC_ID, ANL_DOC_ID, "cites") in outgoing_pairs
    # the pre-fault shapes must not survive: campaign_child was outgoing, cites was incoming
    assert (CMP_DOC_ID, HND_DOC_ID, "campaign_child") not in outgoing_pairs
    assert (HND_DOC_ID, CMP_DOC_ID, "cites") not in incoming_pairs

    assert f'data-edge-from="{HND_DOC_ID}" data-edge-to="{CMP_DOC_ID}"' in faulted_page
