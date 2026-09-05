"""Catalog view assembly (builder-owned: catalog). ARCHITECTURE.md 4.2;
CONSTRAINTS.md O14; task B4 item 1.

`build_view(adapter, settings, query)` parses a request's query parameters
into `CatalogFilters` plus sort/page/page_size, calls the adapter's
already-defined read-only catalog surface (ARCHITECTURE.md 4.1: `catalog`,
`facets`, `index_meta`), and assembles one `CatalogView` for both the HTML
page and its JSON twin (`dataclasses.asdict(view)` in routes.py).

Nothing here opens a database connection or imports RHACO_corpus_index --
every read goes through `adapter.catalog()` / `adapter.facets()` /
`adapter.index_meta()` (ARCHITECTURE.md 4.1). Filtering never fabricates a
value not present in the index: every control's *options* come from
`adapter.facets()` (the global, unfiltered distinct values, D-Q2), never
from a hardcoded vocabulary list (CONSTRAINTS.md O14); a filter combination
that matches nothing simply yields `total == 0` -- no fallback substitution.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlencode

from explorer.models import CardRow, CatalogFilters, FacetValues

# ARCHITECTURE.md 4.2 / CONSTRAINTS.md O14: the four sortable columns. This is
# a *display-only* mirror of the whitelist the adapter (explorer/corpus_adapter/
# sql.py SORT_COLUMNS) actually enforces against SQL -- duplicated here (not
# imported) because this module reaches the adapter only through the documented
# instance methods (ARCHITECTURE.md 4.1), never through corpus_adapter internals.
# An invalid or unrecognised `sort` value passed to `adapter.catalog()` is
# harmless either way: the adapter's own `parse_sort` is the authority and
# silently falls back to "date desc" (ARCHITECTURE.md sql.py `parse_sort`).
SORT_COLUMNS: tuple[str, ...] = ("date", "doc_id", "title", "status")
_DEFAULT_SORT_DIRECTION: dict[str, str] = {"date": "desc", "doc_id": "asc", "title": "asc", "status": "asc"}
DEFAULT_SORT = "date:desc"

MAX_PAGE_SIZE = 200

# CatalogFilters field order (explorer/models.py) -- the exact, closed set of
# query parameters this endpoint accepts; task B4 item 1: "nothing else is
# accepted" (any other query parameter is simply never read).
_FILTER_FIELDS: tuple[str, ...] = (
    "doc_type", "status", "lifecycle_state", "program", "tag",
    "project_knowledge", "date_from", "date_to", "path_prefix",
)

NO_MATCH_TEXT = "no cards match the current filters"


def _clean(value: Any) -> str | None:
    """Empty strings (and missing values) become None (task B4 item 1)."""
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def parse_filters(query: dict) -> CatalogFilters:
    return CatalogFilters(**{name: _clean(query.get(name)) for name in _FILTER_FIELDS})


def parse_sort(query: dict) -> str:
    return _clean(query.get("sort")) or DEFAULT_SORT


def parse_page(query: dict) -> int:
    try:
        page = int(str(query.get("page")).strip())
    except (TypeError, ValueError):
        page = 1
    return max(1, page)


def parse_page_size(query: dict, default_size: int) -> int:
    raw = query.get("page_size")
    if raw is None or str(raw).strip() == "":
        size = default_size
    else:
        try:
            size = int(str(raw).strip())
        except ValueError:
            size = default_size
    return max(1, min(size, MAX_PAGE_SIZE))


def effective_sort(raw_sort: str) -> tuple[str, str]:
    """The (column, direction) the adapter will actually apply for `raw_sort`,
    computed with the same whitelist-and-default rule as `sql.parse_sort` --
    for display only (the "active sort shown", task B4 item 2)."""
    col, _, direction = (raw_sort or "").strip().partition(":")
    col = col.strip().lower()
    if col not in SORT_COLUMNS:
        col = "date"
    direction = direction.strip().lower()
    if direction not in ("asc", "desc"):
        direction = _DEFAULT_SORT_DIRECTION[col]
    return col, direction


def _row_dict(card: CardRow) -> dict:
    """Every CardRow dataclass field, plus `frozen` -- a computed @property,
    so it does not otherwise survive `dataclasses.asdict()` (task B4 item 2:
    the JSON twin carries "every CardRow field plus card_ref / doc_ref /
    frozen"; card_ref and doc_ref are already plain fields)."""
    d = dataclasses.asdict(card)
    d["frozen"] = card.frozen
    d["is_cmp"] = card.is_cmp
    return d


@dataclass
class CatalogView:
    """The complete catalog page (task B4 item 1): every field is either an
    adapter-reported value or a value computed from it -- nothing here is a
    retrieval-ranked result and no control's options are hardcoded."""

    filters: CatalogFilters
    sort: str
    sort_column: str
    sort_direction: str
    page: int
    page_size: int
    total: int
    rows: list[dict] = field(default_factory=list)
    facets: FacetValues | None = None          # under-filter facet counts (D-Q6)
    global_facets: FacetValues | None = None   # global control vocabularies (D-Q2)
    page_count: int = 1
    has_prev: bool = False
    has_next: bool = False
    prev_page: int | None = None
    next_page: int | None = None
    index_total_cards: int = 0
    db_path: str = ""
    show_lifecycle_control: bool = False
    no_matches: bool = False
    no_match_text: str = NO_MATCH_TEXT
    query_string_no_page: str = ""   # current filters+sort+page_size, urlencoded, for pagination links


def build_view(adapter: Any, settings: Any, query: dict) -> CatalogView:
    filters = parse_filters(query)
    sort = parse_sort(query)
    page = parse_page(query)
    page_size = parse_page_size(query, settings.page_size)

    catalog_page = adapter.catalog(filters, sort, page, page_size)
    global_facets = adapter.facets()
    index_meta = adapter.index_meta()

    sort_column, sort_direction = effective_sort(sort)

    total = catalog_page.total
    page_count = max(1, -(-total // page_size)) if total else 1
    has_prev = page > 1
    has_next = page < page_count
    prev_page = page - 1 if has_prev else None
    next_page = page + 1 if has_next else None

    # ARCHITECTURE.md 4.2 / task B4 item 2: the lifecycle_state control is a
    # SEPARATE control shown only when CMP is among the results or selected.
    show_lifecycle_control = bool(filters.doc_type == "CMP") or bool(catalog_page.facets.lifecycle_states)

    # Pagination links preserve the filters (task B4 item 2) -- and sort /
    # page_size, so a page-2 link never silently resets either.
    qs_params: dict[str, str] = {name: getattr(filters, name) for name in _FILTER_FIELDS if getattr(filters, name)}
    qs_params["sort"] = sort
    qs_params["page_size"] = str(page_size)
    query_string_no_page = urlencode(qs_params)

    return CatalogView(
        filters=filters,
        sort=sort,
        sort_column=sort_column,
        sort_direction=sort_direction,
        page=page,
        page_size=page_size,
        total=total,
        rows=[_row_dict(c) for c in catalog_page.rows],
        facets=catalog_page.facets,
        global_facets=global_facets,
        page_count=page_count,
        has_prev=has_prev,
        has_next=has_next,
        prev_page=prev_page,
        next_page=next_page,
        index_total_cards=index_meta.live_counts.get("cards", 0),
        db_path=index_meta.db_path,
        show_lifecycle_control=show_lifecycle_control,
        no_matches=(total == 0),
        query_string_no_page=query_string_no_page,
    )
