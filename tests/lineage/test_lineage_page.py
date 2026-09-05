"""Functional tests against the fixture corpus (task B8 deliverable 5): the
CMP, amendment, HND, and reference-v1_0 pages; the relation filter and hops
controls; and the "no recorded relationships" state."""
from __future__ import annotations

from tests.lineage.conftest import (
    AMENDMENT_CARD_REF,
    AMENDMENT_STEM,
    ANL_DOC_ID,
    CMP_CARD_REF,
    CMP_DOC_ID,
    EVT_CARD_REF,
    HND_CARD_REF,
    HND_DOC_ID,
    REF_V1_0_CARD_REF,
    UNRESOLVED_TARGET,
)


def test_cmp_page_shape(client):
    resp = client.get(f"/lineage/{CMP_CARD_REF}")
    assert resp.status_code == 200
    body = resp.text
    assert 'data-mode="lineage"' in body
    assert f'data-selected-doc-id="{CMP_DOC_ID}"' in body
    assert f'data-card-ref="{CMP_CARD_REF}"' in body


def test_cmp_page_has_two_outgoing_campaign_child_edges(client):
    resp = client.get(f"/lineage/{CMP_CARD_REF}")
    body = resp.text
    assert "has campaign child" in body
    assert f'data-relation="campaign_child" data-edge-from="{CMP_DOC_ID}" data-edge-to="{HND_DOC_ID}" data-edge-direction="outgoing"' in body
    assert f'data-relation="campaign_child" data-edge-from="{CMP_DOC_ID}" data-edge-to="{ANL_DOC_ID}" data-edge-direction="outgoing"' in body


def test_cmp_page_subtree_lists_both_children_with_counts(client):
    resp = client.get(f"/lineage/{CMP_CARD_REF}")
    body = resp.text
    assert "Campaign subtree" in body
    assert "Documents by type in this campaign subtree" in body
    # counts_by_doc_type rendered as a table: CMP root (1), both children's
    # doc types present with non-zero counts (HND appears twice: the parent
    # and its amendment share the HND doc_id, O7).
    assert "<td>CMP</td><td>1</td>" in body
    assert "<td>ANL</td><td>1</td>" in body
    assert "<td>HND</td><td>2</td>" in body
    assert f'data-doc-id="{ANL_DOC_ID}"' in body
    assert f'data-doc-id="{HND_DOC_ID}"' in body
    # both children present as subtree nodes at depth 1
    assert 'data-depth="1"' in body


def test_amendment_page_outgoing_amends_edge(client):
    resp = client.get(f"/lineage/{AMENDMENT_CARD_REF}")
    assert resp.status_code == 200
    body = resp.text
    assert f'data-relation="amends" data-edge-from="{AMENDMENT_STEM}" data-edge-to="{HND_DOC_ID}" data-edge-direction="outgoing"' in body


def test_hnd_page_unresolved_cites_edge(client):
    resp = client.get(f"/lineage/{HND_CARD_REF}")
    assert resp.status_code == 200
    body = resp.text
    assert f'data-relation="cites" data-edge-from="{HND_DOC_ID}" data-edge-to="{UNRESOLVED_TARGET}" data-edge-direction="unresolved"' in body
    assert "unresolved" in body
    assert f"<code>{UNRESOLVED_TARGET}</code>" in body


def test_hnd_page_incoming_campaign_child_and_amends(client):
    resp = client.get(f"/lineage/{HND_CARD_REF}")
    body = resp.text
    assert f'data-relation="campaign_child" data-edge-from="{CMP_DOC_ID}" data-edge-to="{HND_DOC_ID}" data-edge-direction="incoming"' in body
    assert f'data-relation="amends" data-edge-from="{AMENDMENT_STEM}" data-edge-to="{HND_DOC_ID}" data-edge-direction="incoming"' in body


def test_reference_v1_0_page_supersedes_edge_and_chain(client):
    resp = client.get(f"/lineage/{REF_V1_0_CARD_REF}")
    assert resp.status_code == 200
    body = resp.text
    assert 'data-relation="supersedes"' in body
    assert 'data-edge-direction="outgoing"' in body
    assert "Fixture Reference" in body  # v1_1's title, linked as the outgoing target
    # chain: v1_0 then v1_1, v1_1 marked current head
    idx_chain_heading = body.find('id="chain-heading"')
    assert idx_chain_heading != -1
    chain_block = body[idx_chain_heading:]
    assert 'data-chain-head="true"' in chain_block
    assert "current head" in chain_block


def test_reference_v1_0_page_superseded_banner(client):
    resp = client.get(f"/lineage/{REF_V1_0_CARD_REF}")
    body = resp.text
    assert 'data-superseded-banner="true"' in body
    assert "This version is superseded -- current head:" in body


def test_no_recorded_relationships_state(client):
    resp = client.get(f"/lineage/{EVT_CARD_REF}")
    assert resp.status_code == 200
    body = resp.text
    assert "no recorded relationships" in body


def test_relation_filter_narrows_typed_edges(client):
    resp = client.get(f"/lineage/{CMP_CARD_REF}?relation=campaign_child")
    assert resp.status_code == 200
    body = resp.text
    assert 'name="relation" value="campaign_child" checked' in body
    # the (only) two outgoing edges around the CMP center are both
    # campaign_child, so filtering to that relation keeps the outgoing list
    # non-empty and unchanged in count.
    assert body.count('data-edge-direction="outgoing"') >= 2


def test_invalid_relation_and_hops_fall_back_to_defaults(client):
    resp = client.get(f"/lineage/{CMP_CARD_REF}?relation=bogus&hops=99")
    assert resp.status_code == 200
    body = resp.text
    assert 'name="relation" value="" checked' in body  # bogus relation ignored -> "All relations"
    assert 'name="hops" value="1" checked' in body      # bogus hops ignored -> one hop
