"""Search view assembly (builder-owned: search). ARCHITECTURE.md 4.3; task B5.

`run_search(adapter, settings, query)` reads the adapter's already-defined
read-only search surface (ARCHITECTURE.md 4.1: resolve_identifier,
cards_for_doc_id, search_lexical, search_hybrid, search_graph,
vector_availability) and assembles a single SearchView for both the HTML page
and its JSON twin (dataclasses.asdict). Nothing here opens a database
connection or imports RHACO_corpus_index / RHACO_tool_catalog_librarian --
the adapter is the only importer (ARCHITECTURE.md section 2, CONSTRAINTS.md
S2). No ranking is reimplemented: `rank`, `mode_effective`, and
`degradation_notice` are taken from the adapter's ModeResult verbatim; the
only computation this module performs on retrieval output is (a) building an
"open" link per card row and (b) an optional post-hoc narrowing of hybrid /
graph results by card metadata (CONSTRAINTS.md O5 -- never presented as
retrieval-side filtering, and never re-ranked: narrowing only drops items
from the list, it never reorders the survivors' `rank`).

Module-API gotcha recorded here because it is easy to get backwards: RHACO_corpus_index.search_fts's
`doc_type_filter` is iterated character-by-character when it is a bare string
(`{t.upper() for t in doc_type_filter}` -- verified by reading
C:\\RHACO\\rhaco\\RHACO_corpus_index.py lines 1189-1213, and empirically: a
fixture-index probe run with `doc_type_filter="EVT"` returned 0 matches for a
query known to hit the EVT fixture document, while `doc_type_filter=["EVT"]`
returned the expected 4 lines -- see docs/rounds/R02_search.report.md
Evidence). This module therefore always wraps the single query-string value
in a one-item list before calling `adapter.search_lexical`.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from explorer.models import CardRow, Evidence, ResultItem, VectorAvailability

# CONSTRAINTS.md O20: RHACO_corpus_index.search_fts's own default and hard cap
# (MAX_SEARCH_RESULTS). Not imported directly -- this module never imports
# RHACO_corpus_index (S2) -- so the two figures are pinned here as constants.
LEXICAL_MAX_RESULTS_DEFAULT = 100
LEXICAL_MAX_RESULTS_CAP = 200

# Task B5 deliverable 1: "top_k from the query (default 10, max 50)".
TOP_K_DEFAULT = 10
TOP_K_CAP = 50

VALID_MODES = ("identifier", "lexical", "hybrid", "graph")
DEFAULT_MODE = "hybrid"  # CONSTRAINTS.md S3: flat hybrid is the accepted default.

GRAPH_RELATION_NOTE = "expansion of a seed; relation not exposed by the current RHACO API"
HYBRID_LEXICAL_LOOKUP_LABEL = "lexical excerpt, not the hybrid evidence"
NO_LITERAL_MATCH_TEXT = "no literal match for this query in the document"
NO_CARD_ROW_TEXT = "no card row in the index"

# docs/REFERENCE.md section 1: standing retrieval dispositions of record, restated
# here in one line each (task B5 deliverable 1). Figures are RHACO campaign results
# on Gold v1.1 (40 rows); this module re-evaluates none of them.
MODE_LABELS = {
    "identifier": "Identifier",
    "lexical": "Lexical / FTS5",
    "hybrid": "Hybrid (default)",
    "graph": "graph / lineage (auxiliary)",
}

# R08 dispatch item 1 (critic round 1, ranked issue 2; CONSTRAINTS.md S8: no hidden
# epistemic uplift). Every Recall@10 figure this page shows is a RHACO campaign
# result, not a live measurement -- it must be attributed to its source ANL and the
# date it was evaluated, so a reader can tell it is a July measurement and not a
# claim about today. All four Gold v1.1 figures below share one source and date.
GOLD_V1_1_SOURCE = "RHACO-ANL-20260712-001"
GOLD_V1_1_EVAL_DATE = "2026-07-12"

# The hybrid figure is worse than merely stale: it is CONTRADICTED by this build's
# own measurement on the corpus this page searches. tools/l4_gold_oracle.py scored
# the adapter's hybrid path at 0.675 (27/40), twice, against the July 0.700.
# SCOPE.md's "Gold v1.1 compatibility" row carries this as an evidenced regression
# whose cause is corpus evolution (one gold row's target family gained a new
# supersession head after the July evaluation), not the adapter. Restated here,
# dated, rather than left as a second bare figure beside the first.
HYBRID_CURRENT_MEASURE = (
    "This build ran its own oracle (tools/l4_gold_oracle.py), which evaluated "
    "Recall@10 at 0.675 (27/40) on 2026-09-04, on the corpus as it then stood -- "
    "see the Gold v1.1 compatibility row in SCOPE.md for the evidence and its "
    "cause (corpus evolution, not the adapter)."
)

HYBRID_RERANK_NOTE = (
    f"Hybrid-rerank is not offered on this interactive surface: {GOLD_V1_1_SOURCE} "
    f"(evaluated {GOLD_V1_1_EVAL_DATE}) recorded a documented-FAIL batch mode "
    "(Recall@10 0.575 vs threshold 0.700, ~26 min/query; docs/REFERENCE.md section "
    "1). It is never called from any UI path."
)

# R08 dispatch item 2 (critic round 1, ranked issue 5): identifier-mode evidence
# disclosure text. Verified against explorer/corpus_adapter/adapter.py before
# writing this: `resolve_identifier` (adapter.py, "def resolve_identifier") calls
# only `self._rhaco_index.resolve_identifier`, and `cards_for_doc_id` walks
# `_cards_for_doc_id` / `_row_to_card`, which read `cards`/`card_programs`/
# `card_tags`/`edges` tables only -- neither path calls `vector_availability()` or
# anything in the vector channel, so "identifier mode cannot degrade" is a checked
# claim, not an assumption.
IDENTIFIER_COMPONENT_RANK_TEXT = (
    "not applicable -- no fusion in this mode (identifier mode never calls "
    "search_hybrid or search_graph, so there is no per-channel rank to expose "
    "or withhold)"
)
IDENTIFIER_DEGRADATION_TEXT = (
    "not applicable -- identifier mode is an exact alias lookup and does not use "
    "the vector channel at all, so it cannot degrade"
)


@dataclass
class ModeExplanation:
    mode: str
    label: str
    standing: str


MODE_EXPLANATIONS: tuple[ModeExplanation, ...] = (
    ModeExplanation(
        mode="identifier",
        label=MODE_LABELS["identifier"],
        standing="Exact alias lookup only, no ranking; returns every doc_id whose alias matches.",
    ),
    ModeExplanation(
        mode="lexical",
        label=MODE_LABELS["lexical"],
        standing=(
            "Available; the only channel that accepts filters. Exact substring hit-set, "
            f"bm25 order only ({GOLD_V1_1_SOURCE}, evaluated {GOLD_V1_1_EVAL_DATE}: "
            "Recall@10 0.200 aggregate on Gold v1.1)."
        ),
    ),
    ModeExplanation(
        mode="hybrid",
        label=MODE_LABELS["hybrid"],
        standing=(
            f"ACCEPTED -- the operational default. {GOLD_V1_1_SOURCE} (evaluated "
            f"{GOLD_V1_1_EVAL_DATE}) measured Recall@10 0.700 aggregate on Gold v1.1. "
            f"{HYBRID_CURRENT_MEASURE}"
        ),
    ),
    ModeExplanation(
        mode="graph",
        label=MODE_LABELS["graph"],
        standing=(
            "AUXILIARY lineage mode, retained for its typed-edge expansions, not a ranking "
            f"improvement. {GOLD_V1_1_SOURCE} (evaluated {GOLD_V1_1_EVAL_DATE}) measured "
            "Recall@10 0.575 on Gold v1.1."
        ),
    ),
)


@dataclass
class CardLine:
    """One rendered card row within a result (O7: every card row for the id,
    never picked silently), carrying its own reader open-link."""

    card: CardRow
    open_link: str


@dataclass
class IdentifierRow:
    doc_id: str
    cards: list[CardLine] = field(default_factory=list)
    no_card_row: bool = False
    # R08 dispatch item 2: the evidence disclosure for this doc_id's resolution
    # (not per card row -- an id with several card rows, O7, gets ONE disclosure
    # covering all of them, so it never implies the page picked one).
    evidence: Evidence | None = None


@dataclass
class ResultView:
    rank: int
    doc_id: str
    evidence: Evidence
    cards: list[CardLine] = field(default_factory=list)
    path: str | None = None  # lexical hits: the body path from the FTS match
    no_card_row: bool = False


@dataclass
class SearchView:
    q: str
    mode_requested: str
    mode_effective: str | None  # None only when no query ran (empty q)
    ran: bool
    vector: VectorAvailability | None = None
    degradation_notice: str | None = None
    identifier_rows: list[IdentifierRow] = field(default_factory=list)
    results: list[ResultView] = field(default_factory=list)
    truncated: bool = False
    total_matched: int | None = None
    returned: int = 0
    doc_type_filter: str | None = None
    path_glob: str | None = None
    max_results: int = LEXICAL_MAX_RESULTS_DEFAULT
    top_k: int = TOP_K_DEFAULT
    narrow_doc_type: str | None = None
    narrow_status: str | None = None
    narrow_lifecycle_state: str | None = None
    narrow_program: str | None = None
    narrowed_from: int | None = None
    narrowed_to: int | None = None
    mode_explanations: tuple[ModeExplanation, ...] = MODE_EXPLANATIONS
    hybrid_rerank_note: str = HYBRID_RERANK_NOTE
    mode_labels: dict = field(default_factory=lambda: dict(MODE_LABELS))


# -- query-parameter helpers ---------------------------------------------------


def _clean(value) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _bounded_int(raw, default: int, lo: int, hi: int) -> int:
    if raw is None or str(raw).strip() == "":
        return default
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return default
    return max(lo, min(hi, value))


def _normalize_mode(raw) -> str:
    value = _clean(raw)
    return value if value in VALID_MODES else DEFAULT_MODE


# -- card-line / open-link assembly ---------------------------------------------


def _open_link(card_ref: str, mode_effective: str, line_no: int | None) -> str:
    """Task B5 deliverable 1: lexical hits link to /doc/<card_ref>?line=<line_no>;
    every other mode links to /doc/<card_ref> with no line anchor."""
    if mode_effective == "lexical" and line_no is not None:
        return f"/doc/{card_ref}?line={line_no}"
    return f"/doc/{card_ref}"


def _card_line(card: CardRow, mode_effective: str, line_no: int | None) -> CardLine:
    return CardLine(card=card, open_link=_open_link(card.card_ref, mode_effective, line_no))


def _to_result_view(item: ResultItem, mode_effective: str) -> ResultView:
    # The line anchor is only meaningful for the module's own lexical hits
    # (item.evidence.line_no on a hybrid/graph item is a labelled lexical-lookup
    # excerpt, not the reason the document was retrieved -- CONSTRAINTS.md A7).
    line_no = item.evidence.line_no if mode_effective == "lexical" else None
    cards = [_card_line(c, mode_effective, line_no) for c in item.cards]
    return ResultView(
        rank=item.rank,
        doc_id=item.doc_id,
        evidence=item.evidence,
        cards=cards,
        path=item.path,
        no_card_row=not item.cards,
    )


# -- post-hoc narrowing (CONSTRAINTS.md O5) -------------------------------------


def _item_matches_narrow(
    item: ResultItem,
    doc_type: str | None,
    status: str | None,
    lifecycle_state: str | None,
    program: str | None,
) -> bool:
    """True iff at least one of the item's card rows satisfies every supplied
    filter (an id with several card rows, e.g. a hand and its amendment, is
    kept if any one of its rows matches -- consistent with O7's "never pick
    one row silently"; this only decides list membership, never re-ranks)."""
    for card in item.cards:
        if doc_type and (card.doc_type or "") != doc_type:
            continue
        if status and (card.status or "") != status:
            continue
        if lifecycle_state and (card.lifecycle_state or "") != lifecycle_state:
            continue
        if program and program not in (card.programs or []):
            continue
        return True
    return False


# -- per-mode runners ------------------------------------------------------------


def _run_identifier(adapter, q: str, mode_requested: str, vector: VectorAvailability) -> SearchView:
    resolved_ids = adapter.resolve_identifier(q)
    # `matched` is the honest "exact identifier match" fact for every row this call
    # produces: True iff resolve_identifier itself returned this alias's doc_ids.
    # The fallback path below (a query with no matching alias at all) is NOT a
    # match -- it lists the literal query text as an unresolved id, and the
    # evidence disclosure must say so rather than claim an exact match it did not
    # make (R08 dispatch item 2).
    matched = bool(resolved_ids)
    # O7: an id with no card rows is listed as the literal id with the
    # "no card row in the index" text -- including a query that resolves
    # to no alias at all, using the literal query text as the id.
    ids = resolved_ids if matched else [q]
    rows = []
    for doc_id in ids:
        cards = adapter.cards_for_doc_id(doc_id)
        card_lines = [_card_line(c, "identifier", None) for c in cards]
        evidence = Evidence(
            retrieval_mode="identifier",
            returned_rank=0,  # no ranking in this mode; the template never renders this number
            exact_identifier_match=matched,
            excerpt_source="none",
            degradation_status=IDENTIFIER_DEGRADATION_TEXT,
            component_rank=IDENTIFIER_COMPONENT_RANK_TEXT,
        )
        rows.append(
            IdentifierRow(doc_id=doc_id, cards=card_lines, no_card_row=not cards, evidence=evidence)
        )
    return SearchView(
        q=q,
        mode_requested=mode_requested,
        mode_effective="identifier",
        ran=True,
        vector=vector,
        identifier_rows=rows,
        returned=len(rows),
    )


def _run_lexical(adapter, q: str, mode_requested: str, vector: VectorAvailability, query: dict) -> SearchView:
    doc_type_raw = _clean(query.get("doc_type_filter"))
    path_glob = _clean(query.get("path_glob"))
    max_results = _bounded_int(query.get("max_results"), LEXICAL_MAX_RESULTS_DEFAULT, 1, LEXICAL_MAX_RESULTS_CAP)
    # See module docstring: search_fts iterates a bare string character-by-character,
    # so the single filter value is always wrapped in a one-item list here.
    doc_type_filter = [doc_type_raw] if doc_type_raw else None

    mode_result = adapter.search_lexical(
        q, doc_type_filter=doc_type_filter, path_glob=path_glob, max_results=max_results
    )
    results = [_to_result_view(item, mode_result.mode_effective) for item in mode_result.items]
    return SearchView(
        q=q,
        mode_requested=mode_requested,
        mode_effective=mode_result.mode_effective,
        ran=True,
        vector=vector,
        degradation_notice=mode_result.degradation_notice,
        results=results,
        truncated=mode_result.truncated,
        total_matched=mode_result.total_matched,
        returned=mode_result.returned,
        doc_type_filter=doc_type_raw,
        path_glob=path_glob,
        max_results=max_results,
    )


def _run_hybrid_or_graph(
    adapter, q: str, mode_requested: str, vector: VectorAvailability, query: dict, *, kind: str
) -> SearchView:
    top_k = _bounded_int(query.get("top_k"), TOP_K_DEFAULT, 1, TOP_K_CAP)
    mode_result = adapter.search_hybrid(q, top_k=top_k) if kind == "hybrid" else adapter.search_graph(q, top_k=top_k)
    effective_vector = mode_result.vector if mode_result.vector is not None else vector

    narrow_doc_type = _clean(query.get("narrow_doc_type"))
    narrow_status = _clean(query.get("narrow_status"))
    narrow_lifecycle_state = _clean(query.get("narrow_lifecycle_state"))
    narrow_program = _clean(query.get("narrow_program"))

    items = mode_result.items
    narrowed_from = len(items)
    if any((narrow_doc_type, narrow_status, narrow_lifecycle_state, narrow_program)):
        items = [
            it
            for it in items
            if _item_matches_narrow(it, narrow_doc_type, narrow_status, narrow_lifecycle_state, narrow_program)
        ]
    narrowed_to = len(items)

    results = [_to_result_view(item, mode_result.mode_effective) for item in items]
    return SearchView(
        q=q,
        mode_requested=mode_requested,
        mode_effective=mode_result.mode_effective,
        ran=True,
        vector=effective_vector,
        degradation_notice=mode_result.degradation_notice,
        results=results,
        returned=len(results),
        top_k=top_k,
        narrow_doc_type=narrow_doc_type,
        narrow_status=narrow_status,
        narrow_lifecycle_state=narrow_lifecycle_state,
        narrow_program=narrow_program,
        narrowed_from=narrowed_from,
        narrowed_to=narrowed_to,
    )


def run_search(adapter, settings, query: dict) -> SearchView:
    """Assemble the search view. `query` is a plain mapping of request query
    parameters (routes.py passes `dict(request.query_params)`). `settings` is
    accepted for contract symmetry with the other modules' service entry
    points; nothing here currently reads it (no search knob is configurable
    beyond the query string, CONSTRAINTS.md S7)."""
    del settings  # unused -- see docstring
    q = _clean(query.get("q")) or ""
    mode_requested = _normalize_mode(query.get("mode"))
    vector = adapter.vector_availability()

    if not q:
        # Empty q: render the form and the mode explanation, run nothing
        # (task B5 deliverable 1). mode_effective stays None; the template
        # renders data-mode="search" for this state (ARCHITECTURE.md A19).
        return SearchView(q=q, mode_requested=mode_requested, mode_effective=None, ran=False, vector=vector)

    if mode_requested == "identifier":
        return _run_identifier(adapter, q, mode_requested, vector)
    if mode_requested == "lexical":
        return _run_lexical(adapter, q, mode_requested, vector, query)
    if mode_requested == "graph":
        return _run_hybrid_or_graph(adapter, q, mode_requested, vector, query, kind="graph")
    return _run_hybrid_or_graph(adapter, q, mode_requested, vector, query, kind="hybrid")
