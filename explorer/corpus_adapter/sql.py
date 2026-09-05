"""Documented read-only SQL: D-Q1..D-Q11, and nothing else (ARCHITECTURE.md 4.1).

Every statement here is one of the eleven queries ARCHITECTURE.md section 4.1
documents by id; adding a twelfth is a change request, not a local decision.
Values are always bound (`?`); the only text ever assembled from caller input
is a fixed whitelist of column/table fragments (never the values themselves),
and every fragment is chosen from a small local `dict`/`set`, never taken
verbatim from caller input. This module never imports RHACO_corpus_index or
RHACO_tool_catalog_librarian -- one of three licensed product-tree importers
does that (ARCHITECTURE.md 4.1's importer table); `adapter.py` is the one
that also imports `sql.py` (corrected from the earlier, false "adapter.py is
the sole importer" claim, ARCHITECTURE.md 4.1 SA-3; this round's item 4).

D-Q12 below is a twelfth statement, added this round (dispatch R07 item 3;
SCOPE.md's deferred amends click-through row) -- a change request against
ARCHITECTURE.md 4.1's documented table is filed in this round's report
rather than edited here, since that file is outside this module's owned
paths.
"""
from __future__ import annotations

from explorer.models import CARDS_COLUMNS, CatalogFilters

CARDS_SELECT_COLUMNS = ", ".join(CARDS_COLUMNS)

TAG_FACET_LIMIT = 200

# --- D-Q1: live counts and vector extension check --------------------------
Q1_COUNT_CARDS = "SELECT count(*) FROM cards"
Q1_COUNT_FTS_DOCS = "SELECT count(*) FROM fts_docs"
Q1_COUNT_EDGES = "SELECT count(*) FROM edges"
Q1_COUNT_ID_ALIASES = "SELECT count(*) FROM id_aliases"
Q1_COUNT_EDGES_UNRESOLVED = "SELECT count(*) FROM edges WHERE resolved=0"
Q1_VEC_VERSION = "SELECT vec_version()"

# --- D-Q2: facet values (global, unfiltered) --------------------------------
Q2_DOC_TYPE_COUNTS = "SELECT doc_type, count(*) FROM cards GROUP BY doc_type ORDER BY doc_type"
Q2_STATUS_COUNTS = "SELECT status, count(*) FROM cards GROUP BY status ORDER BY status"
Q2_LIFECYCLE_STATE_COUNTS = (
    "SELECT lifecycle_state, count(*) FROM cards WHERE lifecycle_state IS NOT NULL "
    "GROUP BY lifecycle_state ORDER BY lifecycle_state"
)
Q2_PROJECT_KNOWLEDGE_COUNTS = "SELECT project_knowledge, count(*) FROM cards GROUP BY project_knowledge ORDER BY project_knowledge"
Q2_PROGRAM_COUNTS = "SELECT program, count(*) FROM card_programs GROUP BY program ORDER BY program"
Q2_TAG_COUNTS = "SELECT tag, count(*) FROM card_tags GROUP BY tag ORDER BY count(*) DESC, tag LIMIT ?"

# --- D-Q3: cards for an id --------------------------------------------------
Q3_CARDS_FOR_DOC_ID = f"SELECT {CARDS_SELECT_COLUMNS} FROM cards WHERE doc_id = ? ORDER BY yaml_path"
Q3_PROGRAMS_FOR_YAML_PATH = "SELECT program FROM card_programs WHERE yaml_path = ?"
Q3_TAGS_FOR_YAML_PATH = "SELECT tag FROM card_tags WHERE yaml_path = ?"

# --- D-Q4: card by reference (both spellings) -------------------------------
Q4_CARD_BY_YAML_PATH = f"SELECT {CARDS_SELECT_COLUMNS} FROM cards WHERE yaml_path IN (?, ?)"

# --- D-Q5 / D-Q6: catalog page + facet counts under the current filter -----
# Fixed whitelists -- the only fragments build_catalog_where / parse_sort /
# the facet builders below may ever emit.
_FILTER_ORDER = (
    "doc_type", "status", "lifecycle_state", "project_knowledge",
    "date_from", "date_to", "program", "tag", "path_prefix",
)
SORT_COLUMNS = {"date": "c.date", "doc_id": "c.doc_id", "title": "c.title", "status": "c.status"}
_DEFAULT_SORT_DIRECTION = {"date": "DESC", "doc_id": "ASC", "title": "ASC", "status": "ASC"}
_FACET_COLUMNS = ("doc_type", "status", "lifecycle_state", "project_knowledge")


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def build_catalog_where(filters: CatalogFilters) -> tuple[str, list]:
    """WHERE clause for D-Q5/D-Q6, built only from the fixed CatalogFilters
    whitelist; every value is appended to `params` and bound, never
    interpolated into the SQL text."""
    clauses: list[str] = []
    params: list = []
    for name in _FILTER_ORDER:
        value = getattr(filters, name)
        if not value:
            continue
        if name == "date_from":
            clauses.append("c.date >= ?")
            params.append(value)
        elif name == "date_to":
            clauses.append("c.date <= ?")
            params.append(value)
        elif name == "program":
            clauses.append("EXISTS (SELECT 1 FROM card_programs p WHERE p.yaml_path = c.yaml_path AND p.program = ?)")
            params.append(value)
        elif name == "tag":
            clauses.append("EXISTS (SELECT 1 FROM card_tags t WHERE t.yaml_path = c.yaml_path AND t.tag = ?)")
            params.append(value)
        elif name == "path_prefix":
            clauses.append("c.yaml_path LIKE ? ESCAPE '\\'")
            params.append(_escape_like(value) + "%")
        else:
            clauses.append(f"c.{name} = ?")
            params.append(value)
    where_sql = " WHERE 1=1" + "".join(f" AND {c}" for c in clauses)
    return where_sql, params


def parse_sort(sort: str) -> tuple[str, str]:
    """Parse a `column` or `column:asc`/`column:desc` sort spec against the
    whitelist (date, doc_id, title, status); anything unrecognised falls back
    to the catalog default, date desc."""
    raw = (sort or "").strip()
    col, _, direction = raw.partition(":")
    col = col.strip().lower()
    if col not in SORT_COLUMNS:
        col = "date"
    direction = direction.strip().lower()
    if direction in ("asc", "desc"):
        direction = direction.upper()
    else:
        direction = _DEFAULT_SORT_DIRECTION[col]
    return SORT_COLUMNS[col], direction


def build_catalog_count_query(filters: CatalogFilters) -> tuple[str, list]:
    where_sql, params = build_catalog_where(filters)
    return f"SELECT count(*) FROM cards c{where_sql}", params


def build_catalog_query(filters: CatalogFilters, sort: str, page: int, page_size: int) -> tuple[str, list]:
    where_sql, params = build_catalog_where(filters)
    order_col, order_dir = parse_sort(sort)
    offset = max(0, (max(1, page) - 1) * max(1, page_size))
    sql_text = (
        f"SELECT {CARDS_SELECT_COLUMNS} FROM cards c{where_sql} "
        f"ORDER BY {order_col} {order_dir}, c.yaml_path LIMIT ? OFFSET ?"
    )
    return sql_text, [*params, max(1, page_size), offset]


def build_catalog_facet_column_query(filters: CatalogFilters, column: str) -> tuple[str, list]:
    """D-Q6: one WHERE-reused facet-count query over a direct `cards` column."""
    if column not in _FACET_COLUMNS:
        raise ValueError(f"unsupported facet column: {column!r}")
    where_sql, params = build_catalog_where(filters)
    extra = " AND c.lifecycle_state IS NOT NULL" if column == "lifecycle_state" else ""
    sql_text = f"SELECT c.{column}, count(*) FROM cards c{where_sql}{extra} GROUP BY c.{column} ORDER BY c.{column}"
    return sql_text, params


def build_catalog_facet_program_query(filters: CatalogFilters) -> tuple[str, list]:
    """D-Q6's program facet: the same WHERE, joined through card_programs."""
    where_sql, params = build_catalog_where(filters)
    sql_text = (
        "SELECT p.program, count(DISTINCT c.yaml_path) FROM cards c "
        f"JOIN card_programs p ON p.yaml_path = c.yaml_path{where_sql} "
        "GROUP BY p.program ORDER BY p.program"
    )
    return sql_text, params


# --- D-Q7: edges around a card (by doc_id and by filename stem, O8) --------
Q7_EDGES_FOR = (
    "SELECT from_id, to_id, relation, source_field, from_yaml_path, note, resolved "
    "FROM edges WHERE from_id = ? OR to_id = ? OR from_id = ? OR to_id = ?"
)

# --- D-Q8: body row for a document (reader fallback when the file is missing)
Q8_BODY_ROW = "SELECT doc_id, path FROM fts_docs WHERE doc_id = ?"

# --- D-Q9: supersession chain (both directions, depth-capped) --------------
Q9_CHAIN_FORWARD = (
    "WITH RECURSIVE chain(id, depth) AS ("
    "SELECT ?, 0 "
    "UNION ALL "
    "SELECT e.to_id, depth+1 FROM edges e JOIN chain ON e.from_id = chain.id "
    "WHERE e.relation='supersedes' AND depth < 50"
    ") SELECT id, depth FROM chain"
)
Q9_CHAIN_BACKWARD = (
    "WITH RECURSIVE chain(id, depth) AS ("
    "SELECT ?, 0 "
    "UNION ALL "
    "SELECT e.from_id, depth+1 FROM edges e JOIN chain ON e.to_id = chain.id "
    "WHERE e.relation='supersedes' AND depth < 50"
    ") SELECT id, depth FROM chain"
)

# --- D-Q10: campaign subtree (depth-optional, capped) -----------------------
Q10_CAMPAIGN_SUBTREE = (
    "WITH RECURSIVE sub(id, depth) AS ("
    "SELECT ?, 0 "
    "UNION ALL "
    "SELECT e.to_id, depth+1 FROM edges e JOIN sub ON e.from_id = sub.id "
    "WHERE e.relation='campaign_child' AND (? IS NULL OR depth < ?)"
    ") SELECT id, depth FROM sub LIMIT ?"
)


# --- D-Q11: dangling references ---------------------------------------------
def build_dangling_query(relation: str | None, from_doc_type: str | None, max_results: int) -> tuple[str, list]:
    clauses = ["resolved = 0"]
    params: list = []
    if relation:
        clauses.append("relation = ?")
        params.append(relation)
    if from_doc_type:
        clauses.append("from_id IN (SELECT doc_id FROM cards WHERE doc_type = ?)")
        params.append(from_doc_type)
    where = " AND ".join(clauses)
    sql_text = (
        "SELECT from_id, to_id, relation, source_field, from_yaml_path, note "
        f"FROM edges WHERE {where} LIMIT ?"
    )
    params.append(max_results)
    return sql_text, params


# --- D-Q12: card by document filename stem (amends' from_id is a stem, O8) --
# An `amends` edge's `from_id` is the amendment's filename stem, never a
# `doc_id` (CONSTRAINTS.md O8) -- D-Q3 (doc_id-keyed) can never match it. This
# resolves it through `cards.doc_filename` instead: an exact stem match is a
# LIKE prefix ending in a literal '.' (escaped the same way D-Q5's
# `path_prefix` is), so "stem" matches "stem.md" or "stem.txt" but never
# "stemX.md" (the next literal character after the escaped prefix must be
# the '.' the pattern names).
Q12_CARDS_BY_FILENAME_STEM = (
    f"SELECT {CARDS_SELECT_COLUMNS} FROM cards WHERE doc_filename LIKE ? ESCAPE '\\' ORDER BY yaml_path"
)


def filename_stem_like_pattern(stem: str) -> str:
    """The bound parameter for Q12_CARDS_BY_FILENAME_STEM: `stem` escaped for
    LIKE, followed by a literal '.', then any suffix."""
    return _escape_like(stem) + ".%"
