"""API/page parity (task B8 deliverable 5): /api/lineage/... carries the same
edges, directions, chain, and subtree as the HTML page (ARCHITECTURE.md A14)."""
from __future__ import annotations

from tests.lineage.conftest import (
    ANL_DOC_ID,
    CMP_CARD_REF,
    CMP_DOC_ID,
    HND_DOC_ID,
    REF_V1_0_CARD_REF,
    REF_V1_0_DOC_ID,
    REF_V1_1_DOC_ID,
)


def test_api_edges_match_page_for_cmp(client):
    page = client.get(f"/lineage/{CMP_CARD_REF}").text
    api = client.get(f"/api/lineage/{CMP_CARD_REF}").json()

    assert api["doc_id"] == CMP_DOC_ID
    assert api["card_ref"] == CMP_CARD_REF
    assert api["center"]["doc_id"] == CMP_DOC_ID

    outgoing_pairs = {(e["from_id"], e["to_id"], e["relation"], e["direction"]) for e in api["outgoing"]}
    assert (CMP_DOC_ID, HND_DOC_ID, "campaign_child", "outgoing") in outgoing_pairs
    assert (CMP_DOC_ID, ANL_DOC_ID, "campaign_child", "outgoing") in outgoing_pairs

    for from_id, to_id, relation, direction in outgoing_pairs:
        marker = f'data-relation="{relation}" data-edge-from="{from_id}" data-edge-to="{to_id}" data-edge-direction="{direction}"'
        assert marker in page, f"API edge {marker!r} not found on the rendered page"

    # every API edge carries the contract's required fields (task B8 deliverable 2)
    for e in (*api["outgoing"], *api["incoming"], *api["unresolved"]):
        for key in ("from_id", "to_id", "relation", "direction_label", "direction", "resolved", "target_card_refs"):
            assert key in e


def test_api_subtree_matches_page(client):
    api = client.get(f"/api/lineage/{CMP_CARD_REF}").json()
    subtree = api["subtree"]
    assert subtree is not None
    assert subtree["root_id"] == CMP_DOC_ID
    assert subtree["counts_by_doc_type"]["ANL"] == 1
    assert subtree["counts_by_doc_type"]["HND"] == 2  # parent + amendment share the doc_id (O7)

    page = client.get(f"/lineage/{CMP_CARD_REF}").text
    assert "Campaign subtree" in page
    assert f'data-doc-id="{ANL_DOC_ID}"' in page


def test_api_chain_matches_page_for_reference_v1_0(client):
    api = client.get(f"/api/lineage/{REF_V1_0_CARD_REF}").json()
    chain = api["chain"]
    assert [c["card"]["doc_id"] for c in chain] == [REF_V1_0_DOC_ID, REF_V1_1_DOC_ID]
    assert chain[0]["is_head"] is False
    assert chain[-1]["is_head"] is True

    page = client.get(f"/lineage/{REF_V1_0_CARD_REF}").text
    assert 'data-chain-head="true"' in page
    assert "current head" in page
