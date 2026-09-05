"""Task B12 -- direction-aware sentence rendering (critic round 1, gate 7 FAIL
/ ranked issue 1) and the O7/O8 self-pointing `amends` edge (ranked issue 7,
lineage half). Every assertion here is against the RENDERED SENTENCE (or the
rendered link count/text), never against `models.RELATION_LABELS` or
`RELATION_LABELS_INCOMING` directly -- a test that compared the page to the
same constant the page renders from is exactly the pathology that let this
defect survive four builder waves, 262 tests, and a dedicated critic (see
this round's report, "Evidence" and models.py's own RELATION_LABELS comment).

All fixture-backed (the `client` fixture, deterministic); none touch the live
index."""
from __future__ import annotations

from tests.lineage.conftest import (
    AMENDMENT_CARD_REF,
    AMENDMENT_STEM,
    CMP_CARD_REF,
    CMP_DOC_ID,
    HND_CARD_REF,
    HND_DOC_ID,
    REF_V1_0_DOC_ID,
    REF_V1_1_CARD_REF,
    REF_V1_1_DOC_ID,
)


def _li_containing(body: str, marker: str) -> str:
    """The full <li ...>...</li> block whose opening tag contains `marker`."""
    idx = body.index(marker)
    start = body.rfind("<li", 0, idx)
    end = body.index("</li>", idx)
    return body[start:end]


def test_supersession_head_incoming_sentence_is_direction_aware(client):
    """The current HEAD of the v1_0 -> v1_1 supersession family is v1_1
    itself (test_api_parity.py confirms the chain). From v1_1's OWN page the
    edge recorded as v1_0 --supersedes--> v1_1 is read from the `to` end --
    INCOMING -- so it must render "supersedes", never "is superseded by".
    This is the exact case the critic derived from code (ranked issue 1,
    point 3): "the current head of a supersession family would read 'is
    superseded by <its own predecessor>'." This test would FAIL if
    `relation_sentence` were reverted to a direction-blind
    `RELATION_LABELS.get(relation)` lookup (it would then render "is
    superseded by" here, the exact regression this round repairs)."""
    resp = client.get(f"/lineage/{REF_V1_1_CARD_REF}")
    assert resp.status_code == 200
    body = resp.text

    marker = (
        f'data-relation="supersedes" data-edge-from="{REF_V1_0_DOC_ID}" '
        f'data-edge-to="{REF_V1_1_DOC_ID}" data-edge-direction="incoming"'
    )
    assert marker in body
    li = _li_containing(body, marker)
    assert "supersedes:" in li
    assert "is superseded by" not in body


def test_campaign_edge_direction_aware_sentence_parent_vs_child(client):
    """The SAME campaign_child edge (CMP -> HND), rendered from both ends:
    the CMP page holds it outgoing ("has campaign child"), the HND page holds
    it incoming ("is campaign child of") -- the two sentences must differ,
    and each must be correct for its own end (Task B12 deliverable 4, bullet
    2)."""
    parent_body = client.get(f"/lineage/{CMP_CARD_REF}").text
    child_body = client.get(f"/lineage/{HND_CARD_REF}").text

    parent_marker = (
        f'data-relation="campaign_child" data-edge-from="{CMP_DOC_ID}" '
        f'data-edge-to="{HND_DOC_ID}" data-edge-direction="outgoing"'
    )
    child_marker = (
        f'data-relation="campaign_child" data-edge-from="{CMP_DOC_ID}" '
        f'data-edge-to="{HND_DOC_ID}" data-edge-direction="incoming"'
    )
    assert parent_marker in parent_body
    assert child_marker in child_body

    parent_li = _li_containing(parent_body, parent_marker)
    child_li = _li_containing(child_body, child_marker)

    assert "has campaign child:" in parent_li
    assert "is campaign child of:" in child_li
    # the wrong (direction-blind) sentence never appears on either page: HND
    # has no OUTGOING campaign_child edge of its own, and CMP has no INCOMING
    # one (its incoming edges are all `cites`, docs/rounds/... KB3 report) --
    # so this also catches a reversion to a direction-blind lookup, which
    # would print "has campaign child" on BOTH pages.
    assert "is campaign child of" not in parent_body
    assert "has campaign child" not in child_body


def test_amends_edge_direction_aware_sentence_amendment_vs_parent(client):
    """The SAME amends edge, rendered from the amendment's own page
    (outgoing: "amends") and from the parent's page (incoming: "amended
    by") -- Task B12 deliverable 4, bullet 3. Also asserts the amendment's
    own page does NOT additionally render the degenerate self-pointing
    INCOMING copy of this same edge (Task B12 item 3 -- Decisions; see
    test_amendment_own_page_amends_edge_does_not_link_to_itself below for the
    companion self-link defect)."""
    amendment_body = client.get(f"/lineage/{AMENDMENT_CARD_REF}").text
    parent_body = client.get(f"/lineage/{HND_CARD_REF}").text

    outgoing_marker = (
        f'data-relation="amends" data-edge-from="{AMENDMENT_STEM}" '
        f'data-edge-to="{HND_DOC_ID}" data-edge-direction="outgoing"'
    )
    incoming_marker = (
        f'data-relation="amends" data-edge-from="{AMENDMENT_STEM}" '
        f'data-edge-to="{HND_DOC_ID}" data-edge-direction="incoming"'
    )
    assert outgoing_marker in amendment_body
    assert incoming_marker in parent_body

    assert "amends:" in _li_containing(amendment_body, outgoing_marker)
    assert "amended by:" in _li_containing(parent_body, incoming_marker)

    # the degenerate double-bucketed copy must not ALSO appear on the
    # amendment's own page under "Incoming"
    assert incoming_marker not in amendment_body


def test_amendment_own_page_amends_edge_does_not_link_to_itself(client):
    """O7 (shared doc_id) + O8 (amends addressed by filename stem) mean the
    outgoing amends edge's target id resolves to BOTH the real parent card
    AND the amendment card being displayed. Before this round's fix, both
    were rendered as links with IDENTICAL text (the shared doc_id) -- one of
    them pointing the page back at itself. Task B12 item 3 (Decisions): the
    anchor's own card is excluded from an edge's resolved target list, so
    exactly one link remains, to the real parent."""
    resp = client.get(f"/lineage/{AMENDMENT_CARD_REF}")
    assert resp.status_code == 200
    body = resp.text

    outgoing_marker = (
        f'data-relation="amends" data-edge-from="{AMENDMENT_STEM}" '
        f'data-edge-to="{HND_DOC_ID}" data-edge-direction="outgoing"'
    )
    li = _li_containing(body, outgoing_marker)
    assert li.count("<a ") == 1
    assert f'data-card-ref="{HND_CARD_REF}"' in li
    assert f'data-card-ref="{AMENDMENT_CARD_REF}"' not in li


def test_cmp_outgoing_campaign_child_to_hnd_shows_distinguishable_links(client):
    """Critic ranked issue 7 (lineage half): CMP's outgoing campaign_child
    edge to HND_DOC_ID resolves to two cards sharing that doc_id -- the
    parent HND card and its amendment (O7). Before this round's fix both
    rendered as links with IDENTICAL text ("RHACO-HND-20260115-003" twice,
    indistinguishable). Each must now read the card's own identity (title,
    CONSTRAINTS.md O8 says filename stem is the fallback)."""
    resp = client.get(f"/lineage/{CMP_CARD_REF}")
    assert resp.status_code == 200
    body = resp.text

    marker = (
        f'data-relation="campaign_child" data-edge-from="{CMP_DOC_ID}" '
        f'data-edge-to="{HND_DOC_ID}" data-edge-direction="outgoing"'
    )
    li = _li_containing(body, marker)
    assert li.count("<a ") == 2
    assert f'data-card-ref="{HND_CARD_REF}"' in li
    assert f'data-card-ref="{AMENDMENT_CARD_REF}"' in li
    # exact anchor text: ">Fixture Handoff</a>" would also match as a prefix
    # of the amendment's own title, so the closing tag is checked immediately
    # after each to tell the two rows apart.
    assert ">Fixture Handoff</a>" in li
    assert ">Fixture Handoff -- Amendment A1</a>" in li


def test_relation_filter_chip_label_is_direction_neutral(client):
    """The relation filter selects edges in EITHER direction (O8), so its
    chip must not read as a directional sentence (Task B12 item 1,
    Decisions: RelationOption.label). HND's own campaign_child edge is
    INCOMING; the chip must be neither the outgoing sentence ("has campaign
    child") nor the incoming one ("is campaign child of") -- it names the
    relation."""
    resp = client.get(f"/lineage/{HND_CARD_REF}")
    body = resp.text
    assert 'value="campaign_child"' in body
    assert "campaign relationship (" in body
    assert "is campaign child of (" not in body
    assert "has campaign child (" not in body


def test_relation_filter_amends_count_not_inflated_by_self_pointing_duplicate(client):
    """The amends edge is double-bucketed by the adapter on the amendment's
    own page (outgoing AND incoming, O7/O8). The filter's per-relation count
    must reflect the ONE recorded edge, not two (Task B12 item 3 --
    Decisions)."""
    resp = client.get(f"/lineage/{AMENDMENT_CARD_REF}")
    body = resp.text
    assert "amendment (1)" in body
