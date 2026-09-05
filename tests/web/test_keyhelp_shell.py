"""Task B16 item 1 (open item O-2): the #keyhelp block now lives once in
`explorer/web/templates/base.html`; the five page templates that used to
carry a byte-identical copy each (catalog, search, reader, diagnostics,
lineage) no longer do.

This file is the web-owned counterpart to `tests/integration/
test_keyhelp_contract.py`, which is integrator-owned and NOT editable by
this strand (working rule 1). That file's own `test_every_keyhelp_page_is
_registered` walks `explorer/` for `id="keyhelp"` and compares the result
against a hardcoded list of the five old page-template paths -- a
comparison this round's move necessarily fails, since the block's one
remaining copy is in base.html, not in any of the five. See the round
report's "Change requests" for the exact assertion that file needs now
that the source of truth moved; per the dispatch, that is filed as a
request, not an edit.

What this file proves instead, behaviourally (TestClient rendering the
real merged pages against the fixture index, ARCHITECTURE.md A18 -- no
server process, no browser):
  1. base.html's own source declares the block exactly once;
  2. none of the five former page templates carries its own copy any more
     -- written so a re-introduced per-page copy FAILS, since
     re-introduction is exactly the duplication's own history (round-3
     change request S6-B9, the lineage page copying a stale block inside
     the very wave that created it);
  3. every merged page still renders exactly one #keyhelp, `hidden` by
     default, same id -- so app.js's `document.getElementById("keyhelp")`
     toggle target is unchanged by the move.
"""
from __future__ import annotations

import os
import re

import pytest

WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE_HTML = os.path.join(WORKSPACE, "explorer", "web", "templates", "base.html")

# Duplicated literal values rather than imported from another package's
# conftest/tests, matching this package's own convention (tests/web/
# conftest.py's docstring: "mirrors tests/search/conftest.py's convention").
READER_CARD_REF = "reports/RHACO-ANL-20260115-002_Fixture_Analysis.card.yaml"
LINEAGE_CARD_REF = "reports/RHACO-CMP-20260115-001_Fixture_Campaign.card.yaml"

PAGES = [
    "/",
    "/search?q=fixture",
    f"/doc/{READER_CARD_REF}",
    "/diagnostics",
    f"/lineage/{LINEAGE_CARD_REF}",
]

# The five page templates that used to carry their own #keyhelp copy --
# identical path list to tests/integration/test_keyhelp_contract.py's
# KEYHELP_TEMPLATES, duplicated here (not imported) for the same reason.
FORMER_KEYHELP_TEMPLATES = (
    os.path.join("explorer", "catalog", "templates", "catalog", "catalog.html"),
    os.path.join("explorer", "search", "templates", "search", "search.html"),
    os.path.join("explorer", "reader", "templates", "reader", "reader.html"),
    os.path.join("explorer", "diagnostics", "templates", "diagnostics", "diagnostics.html"),
    os.path.join("explorer", "lineage", "templates", "lineage", "lineage.html"),
)


def _read(rel: str) -> str:
    with open(os.path.join(WORKSPACE, rel), encoding="utf-8") as fh:
        return fh.read()


def test_base_html_declares_keyhelp_exactly_once():
    """File-content assertion (UNVERIFIED as render behaviour by itself --
    the render-time proof is test_every_merged_page_renders_exactly_one_
    keyhelp_block below): base.html's own source carries exactly one
    #keyhelp block, not zero and not more than one."""
    with open(BASE_HTML, encoding="utf-8") as fh:
        src = fh.read()
    count = src.count('id="keyhelp"')
    assert count == 1, f"base.html should declare #keyhelp exactly once, found {count}"


def test_no_former_keyhelp_template_carries_its_own_copy_any_more():
    """The regression guard for O-2 itself: if a copy is ever
    re-introduced into one of the five page templates -- exactly the
    duplication's own history -- this FAILS."""
    offenders = [rel for rel in FORMER_KEYHELP_TEMPLATES if 'id="keyhelp"' in _read(rel)]
    assert not offenders, (
        f"these page templates carry their own #keyhelp copy again: {offenders} "
        "-- the single source of truth is explorer/web/templates/base.html"
    )


@pytest.mark.parametrize("path", PAGES)
def test_every_merged_page_renders_exactly_one_keyhelp_block(fixture_client, path):
    resp = fixture_client.get(path)
    assert resp.status_code == 200, f"{path} -> {resp.status_code}: {resp.text[:300]}"
    count = resp.text.count('id="keyhelp"')
    assert count == 1, f"{path}: expected exactly one #keyhelp, found {count}"


@pytest.mark.parametrize("path", PAGES)
def test_keyhelp_still_hidden_by_default_with_the_same_id(fixture_client, path):
    """The move must not change which pages have the block, its id, or its
    toggle behaviour (task B16 item 2's caution): app.js's toggle target
    (`getElementById("keyhelp")`) and initial `hidden` state are asserted
    directly against the rendered page."""
    resp = fixture_client.get(path)
    match = re.search(r'<div id="keyhelp"([^>]*)>', resp.text)
    assert match, f"{path}: no <div id=\"keyhelp\"...> found"
    assert "hidden" in match.group(1), f"{path}: #keyhelp is not `hidden` by default"


@pytest.mark.parametrize("path", PAGES)
def test_keyhelp_still_documents_all_six_bound_keys(fixture_client, path):
    """The content the block carries is unchanged by the move (still the
    same byte-identical text that was verified across all five source
    templates before this round's edit -- see the round report's
    Evidence section for the sha256 comparison)."""
    body = fixture_client.get(path).text
    block_match = re.search(r'<div id="keyhelp".*?</div>', body, re.DOTALL)
    assert block_match, f"{path}: no #keyhelp block found"
    block = block_match.group(0)
    for label in ("/", "j", "k", "Enter", "Escape", "?"):
        assert f"<kbd>{label}</kbd>" in block, f"{path}: #keyhelp no longer documents {label!r}"
