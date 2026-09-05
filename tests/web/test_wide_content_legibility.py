"""Task B16 item 3 (critic ranked issue 4, plus the catalog builder's
change request in `docs/rounds/R09_catalog.report.md` "Change requests"):
the reader page overflowed its viewport horizontally on every capture
(1387px / 1577-1585px measured against a 1280px viewport). Named causes:
`.doc-body table` had no width budget, and `#card-panel`'s `<pre>` blocks
hold unbreakable paths and hashes with no wrap rule.

Fixed once, in `explorer/web/static/app.css` (shared, loaded on every
page) rather than per module -- `.doc-body table` and the shared `pre`
rule reach the reader's markup without this strand touching
`explorer/reader/**`, which working rule 1 does not license.

STATIC ONLY. These are file-content assertions on app.css; TestClient
never applies CSS and no browser is launched from this strand (D-12/D-3),
so nothing here proves the reader page actually stays within 1280px as
rendered -- that gap is explicit in the round report's "Unresolved
uncertainty" and is the L2 probe's / L3 critic's job to close. What this
file proves is narrower and real: the rules exist, are scoped the way the
report claims, and the fix was not achieved by hiding the overflow
(task B16 item 3's own explicit prohibition).
"""
from __future__ import annotations

import re
from pathlib import Path

APP_CSS = Path(__file__).resolve().parents[2] / "explorer" / "web" / "static" / "app.css"


def _source() -> str:
    return APP_CSS.read_text(encoding="utf-8")


def test_doc_body_table_rule_gives_a_fixed_column_budget():
    src = _source()
    assert re.search(r"\.doc-body\s+table\s*\{[^}]*table-layout:\s*fixed", src), (
        "app.css has no `.doc-body table { table-layout: fixed; ... }` rule"
    )


def test_doc_body_table_cells_wrap_long_unbroken_tokens():
    src = _source()
    match = re.search(
        r"\.doc-body\s+table\s+t[hd],\s*\n\.doc-body\s+table\s+t[hd]\s*\{([^}]*)\}",
        src,
    )
    assert match, "no `.doc-body table th, .doc-body table td { ... }` rule found"
    body = match.group(1)
    assert "overflow-wrap: anywhere" in body
    assert "word-break: break-word" in body


def test_shared_pre_rule_wraps_long_unbroken_tokens():
    """This is the rule that reaches #card-panel's unclassed <pre> blocks
    (reader.html:243,251) without a reader-owned edit -- see the round
    report's Evidence and Decisions sections. Literal substring, not a
    regex, so it cannot be fooled by the earlier `code, pre { font-family:
    ... }` rule that also contains the word `pre`."""
    assert (
        "pre { white-space: pre-wrap; overflow-x: auto; "
        "overflow-wrap: anywhere; word-break: break-word; }"
    ) in _source()


def test_overflow_was_not_fixed_by_hiding_content():
    """Task B16 item 3's explicit prohibition: `overflow: hidden` on a
    document body trades a visible problem for an invisible one. Checked
    against the whole file with the one known, pre-existing, unrelated use
    removed first -- `.sr-only` (round 1: a standard visually-hidden-but-
    screen-reader-visible technique) is not the anti-pattern this item
    forbids."""
    without_sr_only = re.sub(r"\.sr-only\s*\{[^}]*\}", "", _source(), count=1)
    assert "overflow: hidden" not in without_sr_only
    assert "overflow:hidden" not in without_sr_only


def test_doc_body_table_selector_does_not_touch_the_shared_table_rule():
    """The fix is scoped to `.doc-body table`, not the bare `table`
    selector every module's plain tables also match (catalog's own
    `.catalog-table` already budgets its own columns; lineage's and
    diagnostics's tables use the browser's default auto layout and are
    untouched by this round, per working rule 1 -- only web-owned paths).
    The shared `table { ... }` rule (pre-existing, round 1) is unchanged:
    still no `table-layout` of its own."""
    assert "table { border-collapse: collapse; width: 100%; }" in _source(), (
        "the shared `table` rule changed shape -- item 3 must not touch it, "
        "only `.doc-body table` (scoped, added this round)"
    )
