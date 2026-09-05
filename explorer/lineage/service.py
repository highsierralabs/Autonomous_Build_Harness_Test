"""Lineage view assembly (builder-owned: lineage). ARCHITECTURE.md 4.5; PROMPT.md 5.5;
CONSTRAINTS.md S1/S4/S8/O1/O7/O8/O13/O22/O25.

`build_view(adapter, settings, card_ref, relation, hops)` is the lineage module's
one entry point. It never opens a database connection itself and never imports
RHACO_corpus_index or RHACO_tool_catalog_librarian -- every fact comes from the
adapter's already-defined surface (ARCHITECTURE.md 4.1: card, edges_for,
supersession_chain, campaign_subtree).

Everything comes from the adapter; nothing is inferred (PROMPT.md invariant:
"Never infer a relationship not recorded in RHACO data"). In particular, this
module never re-derives an edge's direction from `edge.from_id == center.doc_id`
-- it renders whichever bucket (`EdgeSet.outgoing` / `.incoming` / `.unresolved`)
the adapter placed the edge into, faithfully, even under the `reverse_edges`
fault (ARCHITECTURE.md section 6; `explorer/corpus_adapter/adapter.py` line 506).
That is what makes the KB3 fault OBSERVABLE instead of silently corrected.

Two scopes are kept distinct throughout this module:
  - the CENTER'S OWN typed edges (`outgoing` / `incoming` / `unresolved`) --
    always exactly `adapter.edges_for(center)`, one hop, regardless of the
    `hops` query parameter (ARCHITECTURE.md 4.5: "typed, directional edges
    from D-Q7"); the relation filter narrows this list but hops never does;
  - the GRAPH / REASONING-TRAIL scope -- the center's edges plus, when
    `hops=2`, one further step out from each resolved neighbour's own
    `edges_for` (task B8 deliverable 1, bullet 4). The relation filter is
    applied before hop-2 expansion chooses which neighbours to expand from,
    so a filtered view only ever grows along the filtered relation -- a
    deliberate design choice recorded in this round's report ("Decisions"),
    since neither PROMPT.md nor ARCHITECTURE.md fully specifies two-hop
    relation-filter interaction and no acceptance test exercises hops=2.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from explorer.config import Settings
from explorer.models import CardRow, EdgeSet, Subtree, relation_sentence

# CONSTRAINTS.md O8: the four relations, in the order the filter control lists them.
KNOWN_RELATIONS = ("cites", "supersedes", "amends", "campaign_child")

# Task B12 item 1 (RelationOption label, Decisions): the relation filter selects
# edges in EITHER direction (O8) -- a CMP center's page and one of its children's
# page both offer a `campaign_child` chip, one from the outgoing bucket, one from
# the incoming. `models.RELATION_LABELS` is the OUTGOING sentence only, so using it
# here prints a direction-aware sentence on a control that is not direction-aware
# -- exactly the critic round 1 gate-7 defect, recurring on a different surface.
# These labels name the RELATION, deliberately neutral of direction, distinct from
# the sentences `relation_sentence` builds for the typed-edges lists below.
RELATION_FILTER_LABELS = {
    "cites": "citation",
    "supersedes": "supersession",
    "amends": "amendment",
    "campaign_child": "campaign relationship",
}

# task B8 deliverable 1, bullet 4: "Cap the rendered node count at 200".
MAX_GRAPH_NODES = 200


# --------------------------------------------------------------------------
# View dataclasses (lineage-owned; not shared -- explorer/models.py is the
# integrator's shared shapes, ARCHITECTURE.md section 3).
# --------------------------------------------------------------------------


@dataclass
class RelationOption:
    relation: str
    label: str
    count: int


@dataclass
class LineageEdgeView:
    """One typed edge, rendered exactly as the adapter returned it (never
    re-derived) -- ARCHITECTURE.md 4.5, the KB3 contract. `direction` is the
    bucket (`EdgeSet.outgoing` / `.incoming` / `.unresolved`) the edge was
    found in relative to the anchor card whose `edges_for` produced it (the
    center at hop 1; a resolved neighbour at hop 2 -- see module docstring).
    `target_card_refs` is the API contract's field (task B8 deliverable 2):
    the "other side" card refs from the anchor's point of view, which can be
    more than one card when the target id is shared (O7, an amendment)."""

    from_id: str
    to_id: str
    relation: str
    direction_label: str
    direction: str  # "outgoing" | "incoming" | "unresolved"
    resolved: bool
    note: str | None
    hop: int  # 1 = direct edges_for(center); 2 = one further step (hops=2 only)
    anchor_card_ref: str  # the card_ref whose edges_for produced this edge
    from_card_refs: list[str] = field(default_factory=list)
    to_card_refs: list[str] = field(default_factory=list)
    target_card_refs: list[str] = field(default_factory=list)
    # Per-`target_card_refs` link text, same order/length (Task B12 item 3). When
    # more than one card resolves to the shared id (O7 -- a document and its
    # amendment), repeating the id as every link's text renders indistinguishable
    # runs; each entry here is instead that card's own title (or filename stem,
    # CONSTRAINTS.md O8) so the rows are told apart. The single-card case (the
    # overwhelming majority of edges) is unchanged: the id itself, as before.
    target_labels: list[str] = field(default_factory=list)


@dataclass
class GraphNodeView:
    card: CardRow
    is_center: bool


@dataclass
class ChainEntryView:
    card: CardRow
    is_head: bool


@dataclass
class SubtreeNodeView:
    card: CardRow
    depth: int


@dataclass
class SubtreeView:
    root_id: str
    depth_limit: int | None
    max_results: int
    truncated: bool
    nodes: list[SubtreeNodeView] = field(default_factory=list)
    counts_by_doc_type: dict = field(default_factory=dict)


@dataclass
class TrailEntryView:
    card: CardRow
    relation: str
    direction_label: str
    direction: str  # "outgoing" | "incoming"


@dataclass
class SupersededBannerView:
    head: CardRow


@dataclass
class LineageView:
    card_ref: str
    doc_id: str
    center: CardRow
    relation: str | None            # active filter (None = all relations)
    relation_options: list[RelationOption]
    hops: int                       # 1 or 2, as effectively applied
    outgoing: list[LineageEdgeView]     # center's own edges, hop 1, relation-filtered
    incoming: list[LineageEdgeView]     # center's own edges, hop 1, relation-filtered
    unresolved: list[LineageEdgeView]   # center's own edges, hop 1, relation-filtered
    has_relationships: bool             # true iff the center has ANY edge at all (unfiltered)
    superseded_banner: SupersededBannerView | None
    chain: list[ChainEntryView]         # only populated when len > 1 (O22)
    subtree: SubtreeView | None         # CMP centers only
    graph_nodes: list[GraphNodeView]    # center + every resolved card in scope (hops-aware, filtered)
    graph_edges: list[LineageEdgeView]  # every edge in scope (hop 1 [+ hop 2], filtered)
    graph_truncated: bool               # node cap (200) bit
    reasoning_trail: list[TrailEntryView]  # graph_nodes minus center, chronological


# --------------------------------------------------------------------------
# build_view
# --------------------------------------------------------------------------


def build_view(
    adapter: Any,
    settings: Settings,
    card_ref: str,
    relation: str | None = None,
    hops: int = 1,
) -> LineageView | None:
    """Assemble the lineage view, or None when `adapter.card(card_ref)` finds
    nothing (unknown card_ref, a `docs_archive` card_ref -- never indexed, so
    `adapter.card` already returns None for it -- or a `..` traversal;
    routes.py turns None into a 404)."""
    center = adapter.card(card_ref)
    if center is None:
        return None

    relation = relation if relation in KNOWN_RELATIONS else None
    hops = 2 if hops == 2 else 1

    center_edge_set = adapter.edges_for(center)
    relation_options = _relation_options(center_edge_set)
    has_relationships = bool(
        center_edge_set.outgoing or center_edge_set.incoming or center_edge_set.unresolved
    )

    hop1_edges = _edge_views_from_set(center_edge_set, hop=1, anchor=center, relation=relation)
    outgoing = [e for e in hop1_edges if e.direction == "outgoing"]
    incoming = [e for e in hop1_edges if e.direction == "incoming"]
    unresolved = [e for e in hop1_edges if e.direction == "unresolved"]

    graph_edges, graph_nodes, truncated = _build_graph(
        adapter, center, center_edge_set, hop1_edges, hops=hops, relation=relation
    )

    reasoning_trail = _reasoning_trail(graph_nodes, graph_edges, center)

    chain_cards = adapter.supersession_chain(center.doc_id)
    chain: list[ChainEntryView] = []
    superseded_banner: SupersededBannerView | None = None
    if len(chain_cards) > 1:
        chain = [
            ChainEntryView(card=c, is_head=(i == len(chain_cards) - 1))
            for i, c in enumerate(chain_cards)
        ]
        if (center.status or "") == "Superseded" and chain_cards[-1].card_ref != center.card_ref:
            superseded_banner = SupersededBannerView(head=chain_cards[-1])

    subtree: SubtreeView | None = None
    if center.is_cmp:
        raw_subtree: Subtree = adapter.campaign_subtree(center.doc_id, depth=1)
        counts = dict(raw_subtree.counts_by_doc_type)
        subtree = SubtreeView(
            root_id=raw_subtree.root_id,
            depth_limit=raw_subtree.depth_limit,
            max_results=raw_subtree.max_results,
            truncated=raw_subtree.truncated,
            nodes=[SubtreeNodeView(card=c, depth=d) for c, d in raw_subtree.nodes],
            counts_by_doc_type=counts,
        )

    return LineageView(
        card_ref=center.card_ref,
        doc_id=center.doc_id,
        center=center,
        relation=relation,
        relation_options=relation_options,
        hops=hops,
        outgoing=outgoing,
        incoming=incoming,
        unresolved=unresolved,
        has_relationships=has_relationships,
        superseded_banner=superseded_banner,
        chain=chain,
        subtree=subtree,
        graph_nodes=graph_nodes,
        graph_edges=graph_edges,
        graph_truncated=truncated,
        reasoning_trail=reasoning_trail,
    )


# --------------------------------------------------------------------------
# O7/O8 double-classification (Task B12 item 3, "the self-pointing amends
# edge"): an `amends` edge's `from_id` is the amendment's filename stem and
# its `to_id` is the shared parent doc_id (O8). On the amendment's OWN
# lineage page `anchor.doc_id` IS that same shared id (O7), so
# `adapter.edges_for` (adapter.py:513-516 -- two independent `if`s, not
# `elif`) appends the identical Edge object to BOTH `outgoing` and
# `incoming`: one recorded fact rendered as two edges. Verified against the
# fixture (this round's report, Evidence): exactly one such overlap on the
# amendment's own page, zero on the parent's. This is an adapter behaviour;
# `explorer/corpus_adapter/**` is not this module's to fix (dispatch working
# rule 1), so the view suppresses the degenerate INCOMING copy instead --
# detected by object identity (not by relation name, so it also covers any
# future relation that develops the same O7-style collision) -- and keeps
# only the OUTGOING rendering, since the anchor genuinely IS the edge's
# `from` (the amendment authored it); the INCOMING appearance is an artifact
# of the shared doc_id, never a second edge.
# --------------------------------------------------------------------------


def _self_pointing_incoming_ids(edge_set: EdgeSet) -> set[int]:
    outgoing_ids = {id(e) for e in edge_set.outgoing}
    return {id(e) for e in edge_set.incoming if id(e) in outgoing_ids}


# --------------------------------------------------------------------------
# relation options (O8: counted over the center's own hop-1 edges, unfiltered,
# so the control always lists every relation the filter could select)
# --------------------------------------------------------------------------


def _relation_options(edge_set: EdgeSet) -> list[RelationOption]:
    skip = _self_pointing_incoming_ids(edge_set)
    counts: dict[str, int] = {}
    for e in (*edge_set.outgoing, *edge_set.unresolved):
        counts[e.relation] = counts.get(e.relation, 0) + 1
    for e in edge_set.incoming:
        if id(e) in skip:
            continue
        counts[e.relation] = counts.get(e.relation, 0) + 1
    return [
        RelationOption(relation=r, label=RELATION_FILTER_LABELS.get(r, r), count=counts[r])
        for r in KNOWN_RELATIONS
        if r in counts
    ]


# --------------------------------------------------------------------------
# edge-view construction (one hop, from one EdgeSet -- shared by hop 1 and
# each hop-2 neighbour expansion)
# --------------------------------------------------------------------------


def _refs(cards: list[CardRow]) -> list[str]:
    return [c.card_ref for c in cards]


def _other_side_cards(cards: list[CardRow], anchor_ref: str) -> list[CardRow]:
    """Cards resolved for one endpoint of an edge, with the ANCHOR's own card
    excluded (Task B12 item 3). O7 (a shared doc_id) plus the `amends`
    relation's shared-parent addressing (O8) mean the id/stem lookup that
    resolves an edge's endpoint can legitimately include the anchor's own
    card row when the anchor itself shares that id -- concretely, on an
    amendment's own lineage page the outgoing `amends` edge's target (the
    shared parent doc_id) resolves to BOTH the real parent card and the
    amendment card being displayed, which would otherwise render a link from
    the page to itself, indistinguishable by text from the real target
    (verified against the fixture, this round's report Evidence). The anchor
    is never legitimately "the other side" of its own edge, so it is
    excluded here, at the one place every edge-view / graph-layout call site
    draws its card lists from."""
    return [c for c in cards if c.card_ref != anchor_ref]


def _target_labels(fallback_id: str, cards: list[CardRow]) -> list[str]:
    """Per-ref link text for the typed-edges section (Task B12 item 3, the
    critic's ranked issue 7): when a relation's target/source resolves to
    more than one card sharing the same doc_id (O7 -- e.g. a document and its
    amendment), repeating the shared id as every link's text renders
    indistinguishable runs. Disambiguate with each card's own identity
    (title, falling back to its filename stem, CONSTRAINTS.md O8 -- never the
    doc_id, which is exactly the field that collides) in that case; the
    single-card case (the overwhelming majority of edges) renders exactly as
    it did before this round: the plain id."""
    if len(cards) <= 1:
        return [fallback_id for _ in cards]
    return [c.title or c.filename_stem for c in cards]


def _edge_views_from_set(
    edge_set: EdgeSet, hop: int, anchor: CardRow, relation: str | None
) -> list[LineageEdgeView]:
    """Build LineageEdgeViews for one `edges_for(...)` result, tagging each
    with the bucket it actually came from -- never recomputed from from_id/
    to_id, so a fault-swapped edge stays swapped (module docstring). Every
    sentence is built from `(relation, direction)` via `models.relation_sentence`
    (Task B12 item 1) rather than the direction-blind `Edge.direction_label`;
    the degenerate O7/O8 self-pointing case is suppressed / de-duplicated per
    `_self_pointing_incoming_ids` and `_other_side_cards` above (Task B12
    item 3)."""
    skip_incoming = _self_pointing_incoming_ids(edge_set)
    views: list[LineageEdgeView] = []
    for e in edge_set.outgoing:
        if relation and e.relation != relation:
            continue
        source_cards = _other_side_cards(e.source_cards, anchor.card_ref)
        target_cards = _other_side_cards(e.target_cards, anchor.card_ref)
        from_refs, to_refs = _refs(source_cards), _refs(target_cards)
        views.append(LineageEdgeView(
            from_id=e.from_id, to_id=e.to_id, relation=e.relation,
            direction_label=relation_sentence(e.relation, "outgoing"), direction="outgoing",
            resolved=e.resolved, note=e.note, hop=hop, anchor_card_ref=anchor.card_ref,
            from_card_refs=from_refs, to_card_refs=to_refs, target_card_refs=to_refs,
            target_labels=_target_labels(e.to_id, target_cards),
        ))
    for e in edge_set.incoming:
        if id(e) in skip_incoming:
            continue
        if relation and e.relation != relation:
            continue
        source_cards = _other_side_cards(e.source_cards, anchor.card_ref)
        target_cards = _other_side_cards(e.target_cards, anchor.card_ref)
        from_refs, to_refs = _refs(source_cards), _refs(target_cards)
        views.append(LineageEdgeView(
            from_id=e.from_id, to_id=e.to_id, relation=e.relation,
            direction_label=relation_sentence(e.relation, "incoming"), direction="incoming",
            resolved=e.resolved, note=e.note, hop=hop, anchor_card_ref=anchor.card_ref,
            from_card_refs=from_refs, to_card_refs=to_refs, target_card_refs=from_refs,
            target_labels=_target_labels(e.from_id, source_cards),
        ))
    for e in edge_set.unresolved:
        if relation and e.relation != relation:
            continue
        views.append(LineageEdgeView(
            from_id=e.from_id, to_id=e.to_id, relation=e.relation,
            direction_label=relation_sentence(e.relation, "unresolved"), direction="unresolved",
            resolved=e.resolved, note=e.note, hop=hop, anchor_card_ref=anchor.card_ref,
            from_card_refs=[], to_card_refs=[], target_card_refs=[], target_labels=[],
        ))
    return views


# --------------------------------------------------------------------------
# graph assembly: hop 1 (always) + hop 2 (controlled expansion, task B8
# deliverable 1 bullet 4), node-capped at MAX_GRAPH_NODES
# --------------------------------------------------------------------------


def _edge_identity(e: LineageEdgeView) -> tuple:
    return (e.from_id, e.to_id, e.relation, e.resolved)


def _build_graph(
    adapter: Any,
    center: CardRow,
    center_edge_set: EdgeSet,
    hop1_edges: list[LineageEdgeView],
    hops: int,
    relation: str | None,
) -> tuple[list[LineageEdgeView], list[GraphNodeView], bool]:
    """`hop1_edges` is already relation-filtered (built by the caller with the
    active `relation`). Hop-2 expansion (when requested) walks only the
    neighbours those filtered edges actually touch, and applies the same
    filter to what it finds one step further out -- a filtered view grows
    along the filtered relation only, at both hops (module docstring)."""
    cards_by_ref: dict[str, CardRow] = {center.card_ref: center}
    node_order: list[str] = [center.card_ref]
    all_edges: list[LineageEdgeView] = list(hop1_edges)
    seen_edge_ids = {_edge_identity(e) for e in hop1_edges}
    truncated = False

    def _add_card(card: CardRow) -> bool:
        """Register `card` as an in-scope node; False if the cap already bit."""
        nonlocal truncated
        if card.card_ref in cards_by_ref:
            return True
        if len(node_order) - 1 >= MAX_GRAPH_NODES:  # -1: center does not count against the cap
            truncated = True
            return False
        cards_by_ref[card.card_ref] = card
        node_order.append(card.card_ref)
        return True

    # A full (unfiltered) card_ref -> CardRow lookup over every card touched
    # by the center's own edges, so the (already relation-filtered)
    # `hop1_edges` refs can be resolved back to real CardRow objects without
    # a second adapter call.
    all_center_cards: dict[str, CardRow] = {}
    for e in (*center_edge_set.outgoing, *center_edge_set.incoming):
        for c in (*e.source_cards, *e.target_cards):
            all_center_cards[c.card_ref] = c

    hop1_neighbour_cards: list[CardRow] = []
    for e in hop1_edges:
        for ref in (*e.from_card_refs, *e.to_card_refs):
            if ref != center.card_ref and ref in all_center_cards:
                hop1_neighbour_cards.append(all_center_cards[ref])

    for c in hop1_neighbour_cards:
        _add_card(c)

    if hops == 2 and not truncated:
        # Dedupe neighbours by card_ref (a shared doc_id, e.g. an amendment
        # pair, must not be expanded twice) but preserve first-seen order.
        expanded: set[str] = set()
        for c in hop1_neighbour_cards:
            if truncated:
                break
            if c.card_ref in expanded:
                continue
            expanded.add(c.card_ref)
            neighbour_edge_set = adapter.edges_for(c)
            neighbour_cards: dict[str, CardRow] = {}
            for e in (*neighbour_edge_set.outgoing, *neighbour_edge_set.incoming):
                for card in (*e.source_cards, *e.target_cards):
                    neighbour_cards[card.card_ref] = card
            neighbour_views = _edge_views_from_set(neighbour_edge_set, hop=2, anchor=c, relation=relation)
            for ev in neighbour_views:
                ident = _edge_identity(ev)
                if ident in seen_edge_ids:
                    continue
                seen_edge_ids.add(ident)
                all_edges.append(ev)
                for ref in (*ev.from_card_refs, *ev.to_card_refs):
                    if ref != center.card_ref and ref in neighbour_cards:
                        _add_card(neighbour_cards[ref])

    graph_nodes = [
        GraphNodeView(card=cards_by_ref[ref], is_center=(ref == center.card_ref))
        for ref in node_order
    ]
    return all_edges, graph_nodes, truncated


# --------------------------------------------------------------------------
# reasoning trail: the in-scope connected cards, chronological (PROMPT.md
# 5.5's chronological fallback -- must work with JavaScript disabled)
# --------------------------------------------------------------------------


def _reasoning_trail(
    graph_nodes: list[GraphNodeView], graph_edges: list[LineageEdgeView], center: CardRow
) -> list[TrailEntryView]:
    # First edge (in discovery order) that introduces each connected card ref
    # supplies the relation/direction shown against it in the trail.
    connecting: dict[str, LineageEdgeView] = {}
    for e in graph_edges:
        for ref in (*e.from_card_refs, *e.to_card_refs):
            if ref != center.card_ref and ref not in connecting:
                connecting[ref] = e

    entries: list[TrailEntryView] = []
    for node in graph_nodes:
        if node.is_center:
            continue
        edge = connecting.get(node.card.card_ref)
        if edge is None:
            continue  # defensive: every non-center node is reached by some edge
        # `edge.direction` is relative to the anchor whose edges_for produced
        # it (the center at hop 1; a hop-1 neighbour at hop 2 -- module
        # docstring). Unresolved edges never reach here (they connect no real
        # card, so they are never a node's `connecting` edge).
        direction = edge.direction if edge.direction in ("outgoing", "incoming") else "outgoing"
        # Task B12 item 1, line 421: built directly from (relation, direction)
        # via `models.relation_sentence` -- not read off `edge.direction_label`
        # -- so this call site is correct on its own terms rather than by
        # inheriting an upstream fix.
        entries.append(TrailEntryView(
            card=node.card, relation=edge.relation,
            direction_label=relation_sentence(edge.relation, direction),
            direction=direction,
        ))

    entries.sort(key=lambda t: (t.card.date is None, t.card.date or "", t.card.card_ref))
    return entries


# --------------------------------------------------------------------------
# graph layout (presentation only -- deliberately NOT part of LineageView, so
# it never appears in the JSON twin, which reports data, not pixel geometry).
# Radial layout (ARCHITECTURE.md 4.5): the center at the middle, every other
# in-scope card and every unresolved-edge "ghost" target placed on one ring
# around it. Computed once per HTML render, in routes.py, and handed to the
# template as `layout` alongside `view`.
# --------------------------------------------------------------------------


@dataclass
class LaidOutNode:
    card: CardRow
    is_center: bool
    x: float
    y: float


@dataclass
class LaidOutEdge:
    edge: LineageEdgeView
    x1: float
    y1: float
    y2: float
    x2: float
    is_ghost: bool  # True: the "to" end is a literal unresolved id, not a real node


@dataclass
class GraphLayout:
    width: int
    height: int
    view_box: str
    nodes: list[LaidOutNode]
    edges: list[LaidOutEdge]


def compute_layout(
    view: LineageView, width: int = 640, height: int = 640, radius: float = 240.0
) -> GraphLayout:
    cx, cy = width / 2.0, height / 2.0
    other_nodes = [n for n in view.graph_nodes if not n.is_center]
    unresolved_edges = [e for e in view.graph_edges if e.direction == "unresolved"]
    total_slots = max(len(other_nodes) + len(unresolved_edges), 1)

    positions: dict[str, tuple[float, float]] = {view.center.card_ref: (cx, cy)}
    laid_nodes = [LaidOutNode(card=view.center, is_center=True, x=cx, y=cy)]

    slot = 0
    for n in other_nodes:
        angle = (2 * math.pi * slot / total_slots) - (math.pi / 2)
        x, y = cx + radius * math.cos(angle), cy + radius * math.sin(angle)
        positions[n.card.card_ref] = (x, y)
        laid_nodes.append(LaidOutNode(card=n.card, is_center=False, x=x, y=y))
        slot += 1

    ghost_positions: dict[int, tuple[float, float]] = {}
    for e in unresolved_edges:
        angle = (2 * math.pi * slot / total_slots) - (math.pi / 2)
        ghost_positions[id(e)] = (cx + radius * math.cos(angle), cy + radius * math.sin(angle))
        slot += 1

    laid_edges: list[LaidOutEdge] = []
    for e in view.graph_edges:
        anchor_pos = positions.get(e.anchor_card_ref, (cx, cy))
        if e.direction == "unresolved":
            gx, gy = ghost_positions[id(e)]
            laid_edges.append(LaidOutEdge(edge=e, x1=anchor_pos[0], y1=anchor_pos[1], x2=gx, y2=gy, is_ghost=True))
            continue
        # The anchor sits on whichever side its own direction says (outgoing:
        # anchor is the "from"; incoming: anchor is the "to"); the other side
        # is drawn from `to_card_refs` / `from_card_refs` respectively, one
        # line per resolved card there (O7: a shared id can be more than one
        # card, e.g. an amendment) -- x1/y1/x2/y2 always literally "from" then
        # "to", so the arrowhead (marker-end) always points from->to (the
        # task's graph contract), regardless of which side is the anchor.
        other_refs = e.to_card_refs if e.direction == "outgoing" else e.from_card_refs
        for ref in other_refs:
            if ref not in positions:
                continue
            other_pos = positions[ref]
            if e.direction == "outgoing":
                x1, y1, x2, y2 = anchor_pos[0], anchor_pos[1], other_pos[0], other_pos[1]
            else:
                x1, y1, x2, y2 = other_pos[0], other_pos[1], anchor_pos[0], anchor_pos[1]
            laid_edges.append(LaidOutEdge(edge=e, x1=x1, y1=y1, x2=x2, y2=y2, is_ghost=False))

    return GraphLayout(
        width=width, height=height, view_box=f"0 0 {width} {height}",
        nodes=laid_nodes, edges=laid_edges,
    )
