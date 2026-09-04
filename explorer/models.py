"""Shared typed models (integrator-owned). ARCHITECTURE.md section 3.

Plain dataclasses, no ORM. Builders import these shapes and never redefine
them; a change here is an integrator change request (PROMPT.md section 4).
"""
from __future__ import annotations

from dataclasses import dataclass, field

# The 21 `cards` columns exactly as the index stores them
# (RHACO_corpus_index.py _CARDS_COLUMNS, lines 305-311; I1 report section 2).
CARDS_COLUMNS = (
    "yaml_path", "doc_id", "doc_type", "date", "seq", "title", "status",
    "project_knowledge", "current_version", "schema_version",
    "naming_convention_version", "lifecycle_state", "last_human_review",
    "reviewer", "doc_filename", "doc_path", "local_path", "abstract",
    "card_sha256", "card_mtime_utc", "indexed_at_utc",
)

# CONSTRAINTS.md O24: status values that mean frozen / non-current.
FROZEN_STATUSES = frozenset({"Superseded", "Archived"})

# CONSTRAINTS.md O8: direction labels per relation (from -> to).
RELATION_LABELS = {
    "cites": "cites",
    "supersedes": "is superseded by",
    "amends": "amends",
    "campaign_child": "has campaign child",
}

COMPONENT_RANK_NOT_EXPOSED = "not exposed by current RHACO retrieval API"

AUTHORITY_NOTICE = (
    "Retrieval is not adjudication. This application helps locate and traverse "
    "RHACO documents. The canonical documents and their governed metadata remain "
    "the record; search rank does not establish scientific correctness or authority."
)


@dataclass
class CardRow:
    yaml_path: str
    doc_id: str
    doc_type: str | None = None
    date: str | None = None
    seq: str | None = None
    title: str | None = None
    status: str | None = None
    project_knowledge: str | None = None
    current_version: str | None = None
    schema_version: int | None = None
    naming_convention_version: str | None = None
    lifecycle_state: str | None = None
    last_human_review: str | None = None
    reviewer: str | None = None
    doc_filename: str | None = None
    doc_path: str | None = None
    local_path: str | None = None
    abstract: str | None = None
    card_sha256: str | None = None
    card_mtime_utc: str | None = None
    indexed_at_utc: str | None = None
    programs: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    card_ref: str = ""                 # relative POSIX path of the .card.yaml under the docs root (URL key, A5)
    doc_ref: str | None = None      # relative POSIX path of the document under the docs root
    is_amendment: bool = False         # an `amends` edge exists from this card's filename stem (O7/O8)

    @property
    def frozen(self) -> bool:
        return (self.status or "") in FROZEN_STATUSES

    @property
    def filename_stem(self) -> str:
        name = self.doc_filename or ""
        return name.rsplit(".", 1)[0] if "." in name else name

    @property
    def is_cmp(self) -> bool:
        return (self.doc_type or "").upper() == "CMP"


@dataclass
class IndexMeta:
    db_path: str
    db_bytes: int
    db_mtime_utc: str
    meta: dict                          # every index_meta key -> value (strings)
    live_counts: dict                   # cards, fts_docs, edges, id_aliases, edges_unresolved
    non_authoritative_notice: str = (
        "corpus_index.db is a derived, rebuildable, non-authoritative index; "
        "the cards and documents under the docs root are the record."
    )


@dataclass
class VectorAvailability:
    available: bool
    reason: str                         # ok | disabled_by_env | sqlite_vec_not_loaded | vec_table_missing | embedder_unreachable | db_unavailable
    model_tag: str = "nomic-embed-text"
    probe_ms: float | None = None
    detail: str = ""


@dataclass
class Evidence:
    retrieval_mode: str                 # mode_effective at the time of the search
    returned_rank: int
    exact_identifier_match: bool = False
    line_no: int | None = None
    line: str | None = None
    context_before: list[str] = field(default_factory=list)
    context_after: list[str] = field(default_factory=list)
    excerpt_source: str = "none"        # lexical-hit | lexical-lookup | none
    graph_relation: str | None = None
    graph_seed: str | None = None
    degradation_status: str = "none"
    component_rank: str = COMPONENT_RANK_NOT_EXPOSED


@dataclass
class ResultItem:
    rank: int
    doc_id: str
    cards: list[CardRow]                # every card row for the id (O7); may be empty for an unresolved id
    evidence: Evidence
    path: str | None = None          # lexical hits carry the body path


@dataclass
class ModeResult:
    query: str
    mode_requested: str                 # identifier | lexical | hybrid | graph
    mode_effective: str                 # identifier | lexical | hybrid | hybrid-degraded-lexical | graph | graph-degraded
    items: list[ResultItem] = field(default_factory=list)
    degradation_notice: str | None = None
    truncated: bool = False
    total_matched: int | None = None
    returned: int = 0
    vector: VectorAvailability | None = None


@dataclass
class Edge:
    from_id: str
    to_id: str
    relation: str
    source_field: str | None
    from_yaml_path: str | None
    note: str | None
    resolved: bool
    target_cards: list[CardRow] = field(default_factory=list)
    source_cards: list[CardRow] = field(default_factory=list)

    @property
    def direction_label(self) -> str:
        return RELATION_LABELS.get(self.relation, self.relation)


@dataclass
class EdgeSet:
    center: CardRow
    outgoing: list[Edge] = field(default_factory=list)
    incoming: list[Edge] = field(default_factory=list)
    unresolved: list[Edge] = field(default_factory=list)
    chain_head: CardRow | None = None


@dataclass
class Heading:
    level: int
    text: str
    slug: str
    line_no: int


@dataclass
class DocumentText:
    path: str
    size_bytes: int
    sha256: str
    text: str
    lines: list[str]
    headings: list[Heading]
    renderable: bool                    # True for .md / .txt
    kind: str                           # markdown | text | binary


@dataclass
class FreshnessView:
    fresh: bool
    status: str                         # FRESH | DRIFT
    corpus_card_count_live: int
    corpus_card_count_index: int
    corpus_cards_sha_live: str
    corpus_cards_sha_index: str
    added: list[str]
    removed: list[str]
    sha_changed: list[str]
    computed_at_utc: str
    scan_seconds: float
    scope_note: str = "card metadata only (cards vs index); document bodies are not compared"


@dataclass
class CatalogFilters:
    doc_type: str | None = None
    status: str | None = None
    lifecycle_state: str | None = None
    program: str | None = None
    tag: str | None = None
    project_knowledge: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    path_prefix: str | None = None


@dataclass
class FacetValues:
    doc_types: list[tuple]              # (value, count)
    statuses: list[tuple]
    lifecycle_states: list[tuple]
    programs: list[tuple]
    tags: list[tuple]
    project_knowledge: list[tuple]


@dataclass
class CatalogPage:
    filters: CatalogFilters
    sort: str
    page: int
    page_size: int
    total: int
    rows: list[CardRow]
    facets: FacetValues
