"""(d) catalog(doc_type=CMP) returns only CMP rows with lifecycle_state
populated; facets() is non-empty."""
from __future__ import annotations

from explorer.models import CatalogFilters


def test_catalog_cmp_filter_and_lifecycle_state(live_adapter):
    page = live_adapter.catalog(CatalogFilters(doc_type="CMP"), "date", 1, 50)

    assert page.total > 0
    assert len(page.rows) > 0
    assert len(page.rows) <= 50

    for row in page.rows:
        assert row.doc_type == "CMP"
        assert row.lifecycle_state, f"CMP row {row.card_ref} is missing lifecycle_state"

    assert page.facets.doc_types, "catalog page facets should be non-empty under the current filter"


def test_facets_global_is_non_empty(live_adapter):
    facets = live_adapter.facets()

    assert facets.doc_types
    assert facets.statuses
    assert facets.programs
    assert facets.tags
