"""R09 catalog round-2 tests -- task B15, three critic round-1 findings on
the surface whose whole job is keeping metadata legible
(docs/critique/R06_critic_round_1.report.md ranked issue 6 and the
`metadata_fidelity` / `browse_search_usability` section-2 rows).

Item 1 -- an active `lifecycle_state` filter must never become invisible
and unclearable (ranked issue 6): reproduced against `service.py:163`
(pre-fix) as `doc_type=ANL` + `lifecycle_state=OPEN` -- both real, selectable
values -- yielding zero rows, empty under-filter lifecycle facets, and
therefore (pre-fix) a control that vanished while its filter still narrowed
the result set and still rode along in `query_string_no_page`.

Item 2 -- every abstract was labelled truncated, including complete ones
(`catalog.html:183` pre-fix): shown here against a real fixture card whose
abstract is under the 200-char slice (REF v1_1, 166 chars) versus one over
it (ANL, 339 chars).

Item 3 -- the table's column budget at a 1280px viewport (browse_search_
usability): asserted STATICALLY here (colgroup width percentages, present
CSS rules) per the task's own instruction that a template/CSS assertion is
legitimate but is not behavioural evidence -- L2 (a real browser) is the
layer that renders; no browser or server process is launched in this
package (ARCHITECTURE.md A18, D-12/D-3 foreground-only + no-device rules).
"""
from __future__ import annotations

import html
import re
from pathlib import Path

STATIC_ROOT = Path(__file__).resolve().parents[2] / "explorer" / "catalog"
CSS_TEXT = (STATIC_ROOT / "static" / "catalog.css").read_text(encoding="utf-8")
HTML_TEXT = (STATIC_ROOT / "templates" / "catalog" / "catalog.html").read_text(encoding="utf-8")


# -- Item 1 ------------------------------------------------------------------

def test_active_lifecycle_filter_visible_and_individually_clearable_when_zero_matches(client):
    """doc_type=ANL + lifecycle_state=OPEN: lifecycle_state is a real, global
    facet value (the CMP row carries it) so the filter is genuinely in force,
    but no ANL row carries a lifecycle_state (S4: it is a CMP-only concept),
    so the combination matches zero rows. Before the fix this hid the control
    entirely (service.py:163 computed show_lifecycle_control from the
    under-filter, now-empty facets) -- the filter narrowed the result set
    with no visible reason and no way to clear just it."""
    resp = client.get("/", params={"doc_type": "ANL", "lifecycle_state": "OPEN"})
    assert resp.status_code == 200
    body = resp.text
    assert 'data-total-matching="0"' in body
    assert "no cards match" in body

    # THE CONTROL ITSELF must render because the filter is active, regardless
    # of the (now empty) under-filter facet counts.
    assert "CMP lifecycle state (campaigns only)" in body
    assert 'id="f-lifecycle_state"' in body

    # Its current value is reflected as selected (options still come only
    # from the unfiltered global_facets, O14/D-Q2, so "OPEN" is present).
    assert re.search(r'<option value="OPEN"[^>]*\bselected\b[^>]*>OPEN', body) is not None

    # ... and it offers the blank option every other catalog filter already
    # uses to clear itself (reselect + Apply filters) -- individually
    # clearable, not just visible.
    assert '<option value="">Any lifecycle state</option>' in body

    # Exercise that affordance for real: dropping lifecycle_state alone (as
    # choosing "Any lifecycle state" then submitting would) restores the ANL
    # row, proving the mechanism actually clears just this one filter rather
    # than merely rendering a decorative control.
    cleared = client.get("/", params={"doc_type": "ANL"})
    assert 'data-total-matching="1"' in cleared.text
    assert 'data-doc-id="RHACO-ANL-20260115-002"' in cleared.text


def test_lifecycle_control_still_absent_when_filter_not_active_and_no_cmp_context(client):
    """Guard against overcorrection: doc_type=HND with NO lifecycle_state
    selected must still hide the control (unchanged from pre-fix behaviour;
    also asserted in test_catalog_page.py). The fix adds one disjunct for an
    ACTIVE filter -- it must not make the control unconditionally visible."""
    resp = client.get("/", params={"doc_type": "HND"})
    assert "CMP lifecycle state (campaigns only)" not in resp.text


def test_lifecycle_state_never_offered_as_applying_to_every_doc_type(client):
    """CONSTRAINTS.md S4 / objective gate 6: lifecycle_state is a CMP-only
    concept; the fix must not collapse it with card `status` or offer it as
    though every doc_type had one. With no filter active and doc_type unset,
    the control stays gated on the pre-existing predicates (CMP present in
    results, or a CMP row's lifecycle_state surviving the current filter)."""
    resp = client.get("/", params={"doc_type": "EVT"})
    assert "CMP lifecycle state (campaigns only)" not in resp.text
    # the EVT row's own lifecycle cell stays empty, never substituted
    assert 'data-lifecycle-state=""' in resp.text


# -- Item 2 -------------------------------------------------------------------

def _abstract_cell(body: str, doc_id: str) -> str:
    row = re.search(rf'data-doc-id="{re.escape(doc_id)}"[^>]*>.*?</tr>', body, re.S)
    assert row is not None, f"no row for {doc_id!r}"
    cell = re.search(r'<td class="abstract">(.*?)</td>', row.group(0), re.S)
    assert cell is not None
    return cell.group(1)


def test_complete_abstract_renders_with_no_trailing_ellipsis(client):
    """RHACO_Fixture_Reference_v1_1's abstract is 166 chars -- independently
    re-measured from the fixture card.yaml via PyYAML before writing this
    assertion -- well under the 200-char slice, i.e. COMPLETE. Before the fix
    (catalog.html:183 appended ' ...' unconditionally) this rendered as
    though truncated; a small false statement about the record on a
    provenance tool (the exact defect class round 6's SA-1/SA-2/SA-3 spent
    itself on)."""
    resp = client.get("/", params={"doc_type": "REF"})
    cell = _abstract_cell(resp.text, "RHACO_Fixture_Reference_v1_1")
    assert "..." not in cell
    assert cell.rstrip().endswith("only.")


def test_truncated_abstract_still_shows_ellipsis(client):
    """The ANL fixture card's abstract is 339 chars -- genuinely truncated at
    the 200-char slice -- and must still show the ellipsis; the fix must not
    have swung the other way into silently dropping a true truncation
    signal (the same class of lie, pointing the other direction, per the
    task's own framing)."""
    resp = client.get("/", params={"doc_type": "ANL"})
    cell = _abstract_cell(resp.text, "RHACO-ANL-20260115-002")
    assert cell.rstrip().endswith("...")
    # unescape before measuring: Jinja HTML-escapes the 200-char raw slice
    # (this abstract's first 200 chars contain a literal '"'), which inflates
    # the character count of the rendered cell relative to the raw slice.
    unescaped = html.unescape(cell.rstrip())
    assert len(unescaped) - len(" ...") == 200


# -- Item 3 (STATIC only -- template/CSS assertion; UNVERIFIED as rendered
# pixel geometry. No browser is launched in this package: ARCHITECTURE.md
# A18 and this strand's own D-12/D-3 rules forbid a server or browser
# process here. L2 (the probe, a real browser at a real viewport) is the
# only layer that can produce genuine behavioural evidence for this item.) --

def test_static_catalog_table_declares_a_fixed_column_budget(client):
    """Static template/CSS check (NOT behavioural): a <colgroup> with nine
    <col> elements exists ahead of <thead>, one per header cell, and
    catalog.css switches the table to table-layout: fixed so those <col>
    widths -- not the widest free-form content in a column (long doc_id /
    filename <code> spans, long abstracts) -- decide the table's layout.
    This is the mechanism that keeps the table from exceeding its
    .table-scroll container width; it does not by itself prove any pixel
    was or was not clipped in a rendered browser."""
    resp = client.get("/")
    body = resp.text
    m = re.search(r'<colgroup>(.*?)</colgroup>', body, re.S)
    assert m is not None, "no <colgroup> found in the rendered catalog table"
    cols = re.findall(r'<col class="(col-[a-z]+)">', m.group(1))
    assert cols == [
        "col-title", "col-id", "col-type", "col-date", "col-status",
        "col-programs", "col-lifecycle", "col-abstract", "col-open",
    ]
    assert "table-layout: fixed" in CSS_TEXT


def test_static_column_widths_sum_to_100_percent_and_lifecycle_is_narrow(client):
    """Static CSS check (NOT behavioural): the nine .col-* width percentages
    sum to exactly 100, so the table (already width:100% per base app.css)
    can never exceed its container regardless of viewport -- the mechanism
    by which the CMP lifecycle state column becomes reachable without
    horizontal scrolling at 1280px, rather than a claim that 1280px was
    actually measured here."""
    widths = {}
    for name in ("title", "id", "type", "date", "status", "programs", "lifecycle", "abstract", "open"):
        m = re.search(rf'\.col-{name}\s*\{{\s*width:\s*(\d+)%', CSS_TEXT)
        assert m is not None, f".col-{name} width rule not found in catalog.css"
        widths[name] = int(m.group(1))
    assert sum(widths.values()) == 100
    # the lifecycle column is a short enumerated value (OPEN/CLOSED/...): it
    # does not need anywhere near the room the free-text Abstract column
    # needs, and getting it into budget (rather than dropped or squeezed to
    # the point of illegibility) is the item's actual acceptance bar.
    assert widths["lifecycle"] < widths["abstract"]


def test_static_long_tokens_wrap_instead_of_forcing_table_width(client):
    """Static CSS check (NOT behavioural): overflow-wrap/word-break rules on
    catalog-table cells let a long, unbroken token (a long doc_id or
    filename inside <code>) wrap onto further lines within its own column's
    fixed width instead of visually forcing that column -- and therefore the
    whole table -- wider than its container."""
    assert re.search(r'\.catalog-table\s+t[dh]\s*,\s*\n?\.catalog-table\s+t[dh]\s*\{[^}]*overflow-wrap:\s*anywhere', CSS_TEXT) is not None \
        or "overflow-wrap: anywhere" in CSS_TEXT
    assert "word-break: break-word" in CSS_TEXT
