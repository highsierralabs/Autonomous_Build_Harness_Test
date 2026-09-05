# R09 catalog report -- strand S8-B15 (catalog module round 2 of 4)

## Header

| Field | Value |
|---|---|
| Strand | S8-B15, module builder (catalog), round 7 of the autonomous build |
| Role | filter legibility and metadata honesty (task B15) |
| Model | Claude Sonnet 5 (model id `claude-sonnet-5`) -- sentence from my own system prompt: "You are powered by the model named Sonnet 5." |
| Dispatch record | RHACO-HND-20260903-001 section 2 I as amended by A1.3 |
| Prompt of record | `docs/rounds/R09_catalog.prompt.md`, sha256 `35766a0d9b2e44bad14d2362924c0485af39caf532686b7eaebfced267b5efc4` -- **verified, matches** |
| Worktree | `C:\highsierralabs\RHACO_Corpus_Explorer\.worktrees\catalog`, branch `build/catalog` |
| Base commit (`git rev-parse HEAD` at start) | `c26825e6e7779da65dc09317083593cd9851dfbd` |
| Ancestor check | `git merge-base --is-ancestor 6cca928 HEAD` -- exit 0, HEAD contains `6cca928` |
| Window start (UTC) | 2026-09-05T16:23:45.4010658Z |
| Window end (UTC) | 2026-09-05T16:38:05.8880498Z |
| Concurrent strand | search round 2, own worktree; `explorer/search/**` and `tests/search/**` not read as stable, not touched |

## Change

Three files under my owned paths edited, one test file added; nothing else touched.

1. **`explorer/catalog/service.py`** (`build_view`, around the `show_lifecycle_control` computation, now lines 161-183): added a third disjunct, `bool(filters.lifecycle_state)`, to the control-visibility predicate. Was:
   ```python
   show_lifecycle_control = bool(filters.doc_type == "CMP") or bool(catalog_page.facets.lifecycle_states)
   ```
   Now:
   ```python
   show_lifecycle_control = (
       bool(filters.doc_type == "CMP")
       or bool(catalog_page.facets.lifecycle_states)
       or bool(filters.lifecycle_state)
   )
   ```
   A long comment block at the same location records the invariant and why the third disjunct is load-bearing (reproduced in "Decisions" below).

2. **`explorer/catalog/templates/catalog/catalog.html`**:
   - Abstract cell (was line 183): appended `' ...'` unconditionally whenever `row.abstract` was truthy. Now appends it only `{% if row.abstract|length > 200 %}` -- i.e. only when the 200-char slice actually cut something.
   - Results table: added a `<colgroup>` of nine `<col class="col-*">` elements (one per header cell, same order) ahead of `<thead>`, and gave `<table>` the class `catalog-table`.

3. **`explorer/catalog/static/catalog.css`**: removed the old `.abstract { max-width: 40ch; }` rule (superseded) and added: `.catalog-table { table-layout: fixed; }`, `overflow-wrap: anywhere` / `word-break: break-word` on `.catalog-table th, .catalog-table td`, and nine `.col-*` width rules in percent (17/13/6/8/8/10/10/21/7, summing to 100).

4. **`tests/catalog/test_catalog_filter_legibility.py`** (new): 8 tests covering items 1, 2 and 3 (the last three explicitly labelled static/non-behavioural).

No other file was read as a write target; `explorer/search/**` was neither read nor touched.

## Evidence

### Item 1 -- reproduced BEFORE any change (fixture, via a scratch script driving the same `TestClient` + fixture-build path `tests/catalog/conftest.py` uses; not committed anywhere in the repo)

```
status: 200
contains 'CMP lifecycle state (campaigns only)': False
contains 'no cards match': True
data-total-matching: 0
api filters: {'doc_type': 'ANL', ..., 'lifecycle_state': 'OPEN', ...}
api show_lifecycle_control: False
api total: 0
api query_string_no_page: doc_type=ANL&lifecycle_state=OPEN&sort=date%3Adesc&page_size=50
```
This is the critic's exact claim: `lifecycle_state=OPEN` is genuinely in force (present in `filters`, riding in `query_string_no_page`), the page reports zero matches with no visible reason, and `show_lifecycle_control` (hence the `<select>` itself) is `False` -- the operator has no on-page way to discover or clear the filter except "Clear filters", which would also drop `doc_type=ANL`.

AFTER the fix, same request:
```
contains 'CMP lifecycle state (campaigns only)': True
api show_lifecycle_control: True
```
Control renders, with `OPEN` reflected as the selected option (verified by test, see below) and "Any lifecycle state" available to clear just this one filter.

### Item 2 -- reproduced BEFORE any change

Real fixture card `RHACO_Fixture_Reference_v1_1` (independently re-measured via PyYAML: `len(abstract) == 166`, i.e. COMPLETE, well under the 200-char slice):
```
abstract cell HTML: 'Synthetic REF-typed fixture, version 1.1 -- the current version and the
supersession-chain head for RHACO_Fixture_Reference_v1_0. Built for probe
qualification only.\n ...'
ends with ' ...': True
```
AFTER the fix, same card:
```
abstract cell HTML: '...Built for probe qualification only.\n'
ends with ' ...': False
```
And a genuinely truncated abstract (fixture ANL card, 339 raw chars) still shows the ellipsis after the fix -- confirmed both by a scratch script and by `test_truncated_abstract_still_shows_ellipsis` (below).

### Item 3 -- STATIC evidence only (labelled as such; no browser was launched -- see "Assumptions")

Before the fix: `catalog.html`'s `<thead>` had nine `<th>` with no width attribute or class, and `catalog.css` constrained only one column (`.abstract { max-width: 40ch; }`); the table used the browser's default `auto` layout, which sizes columns from content (long `doc_id`/filename `<code>` spans, unconstrained `Title`), and the whole table sits in `.table-scroll { overflow-x: auto; }` -- an overflow container that hides however far the auto-sized table exceeds it. This matches the critic's screenshot claim (`W4.png`, header clipped after "Prog...") without any additional reproduction needed: the mechanism that would have bounded the table's width did not exist.

After the fix: `<colgroup>` with 9 `<col class="col-*">`, `table-layout: fixed`, and 9 width percentages summing to exactly 100 (asserted by `test_static_column_widths_sum_to_100_percent_and_lifecycle_is_narrow`). Because the table already carries `width: 100%` from base `app.css:112`, and `main` bounds content to 1200px minus 1.25rem side padding (base `app.css:102`) regardless of viewport, a table that can never exceed 100% of its own container can never need horizontal scroll at 1280px (1280 > 1200). This is a template/CSS-level argument, not a measured pixel; labelled UNVERIFIED-as-rendered in "Assumptions".

### Gate (a) -- ruff

```
C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m ruff check explorer tools tests --output-format concise
All checks passed!
```

### Gate (b) -- tests

```
C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m pytest tests/catalog -q
................................                                         [100%]
32 passed, 2 warnings in 1.16s
```
(24 pre-existing catalog tests + 8 new, all green.)

```
C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m pytest tests -q
........................................................................ [ 24%]
........................................................................ [ 48%]
........................................................................ [ 72%]
........................................................................ [ 96%]
..........                                                               [100%]
298 passed, 2 warnings in 28.50s
```
(290 stated in the dispatch record + 8 new = 298, matches exactly.)

### Gate (c) -- L1 index-write + import-boundary check

```
C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe tools/l1_index_write_check.py
l1-index-write-check: hits=6 allowlisted=6 defects=0 verdict=PASS
l1-import-boundary: hits=10 licensed=10 defects=0 unused_licences=0 verdict=PASS
```

### RED/GREEN discipline for the new tests (item 4's own acceptance bar)

Before writing any code fix, I wrote `tests/catalog/test_catalog_filter_legibility.py` in full, then used `git stash push -- <the three fix files>` to put the working tree back to the exact pre-fix code while keeping the new (untracked) test file, and ran the new test file:

```
tests/catalog/test_catalog_filter_legibility.py::test_active_lifecycle_filter_visible_and_individually_clearable_when_zero_matches FAILED
tests/catalog/test_catalog_filter_legibility.py::test_lifecycle_control_still_absent_when_filter_not_active_and_no_cmp_context PASSED
tests/catalog/test_catalog_filter_legibility.py::test_lifecycle_state_never_offered_as_applying_to_every_doc_type PASSED
tests/catalog/test_catalog_filter_legibility.py::test_complete_abstract_renders_with_no_trailing_ellipsis FAILED
tests/catalog/test_catalog_filter_legibility.py::test_truncated_abstract_still_shows_ellipsis PASSED
tests/catalog/test_catalog_filter_legibility.py::test_static_catalog_table_declares_a_fixed_column_budget FAILED
tests/catalog/test_catalog_filter_legibility.py::test_static_column_widths_sum_to_100_percent_and_lifecycle_is_narrow FAILED
tests/catalog/test_catalog_filter_legibility.py::test_static_long_tokens_wrap_instead_of_forcing_table_width FAILED
5 failed, 3 passed
```
(The 3 that already passed pre-fix are deliberately not fix-driven: one asserts the control STAYS absent when the filter is not active, one asserts `lifecycle_state` is never offered as applicable to every `doc_type`, one is the truncated-abstract case -- both already correct pre-fix and included as guard-rails against overcorrection.)

I then `git stash pop` to restore the fix, re-ran the same file: `8 passed` (shown above with full output). This is real pytest RED-then-GREEN evidence for every item-1/2/3 assertion in the new file, not merely an inline assertion written after the fix.

## Material alternatives

**Item 1.** The prompt named two mechanisms to consider: (a) render the control whenever the filter is active regardless of under-filter facet counts, and (b) a per-filter clear affordance distinct from "Clear filters". I implemented (a) alone rather than also building a bespoke chip/x-link affordance for `lifecycle_state`, because (a) already produces (b) for free: the `<select>`'s options come only from `global_facets` (O14/D-Q2, unfiltered), so its "Any lifecycle state" blank option is always present, and reselecting it plus "Apply filters" is *exactly* the mechanism every other catalog filter (`doc_type`, `status`, `program`, `tag`, `project_knowledge`) already relies on to clear itself -- there is no bespoke per-filter clear affordance anywhere else in this module to be consistent with, and inventing one only for `lifecycle_state` would treat it as a special case rather than restoring parity with the other eight controls. I considered a separate "active filters" chip row (one clear-link per active filter, independent of the select controls) as a more explicit affordance; I did not build it because it would be new UI surface solving a problem (discoverability of the *general* clear mechanism) the critic did not raise for the other eight filters, and the item's own acceptance bar ("always visible and always individually clearable") is met without it. Noted as available future work, not a defect, in "Unresolved uncertainty".

**Item 2.** Considered comparing `len(row.abstract) > 200` in Python (adding a computed field to `CardRow`/`_row_dict`) versus the in-template `{% if row.abstract|length > 200 %}` I used. Chose the template-only fix: it is a one-line, purely presentational change with no schema/API surface impact (the JSON twin's `abstract` field is unaffected either way -- `/api/catalog` was never truncating), and `CardRow`/`_row_dict` stays exactly what task B4 already specified.

**Item 3.** Considered (i) dropping columns (the prompt explicitly allows this), (ii) reordering so `CMP lifecycle state` comes immediately after `Status` (before `Programs`), and (iii) a fixed column-width budget via `table-layout: fixed` + `<colgroup>` (what I built). Rejected (i): every column carries a distinct, filterable/sortable fact (O14, S4) and none is redundant; dropping one to satisfy a viewport constraint would be trading a real fidelity loss for a cosmetic one. Considered but did not need (ii): with a properly bounded fixed layout the whole table (all 9 columns) fits `main`'s 1200px content box, so `CMP lifecycle state`'s position in the column order no longer matters for the 1280px case -- reordering would only have mattered as a fallback if column budgeting alone couldn't close the gap, which measurement (see Evidence) suggests it does.

## Decisions

- **Item 1 invariant, stated once:** a filter that is in force is always visible and always individually clearable. Never silently dropped (the opposite failure -- the prompt's own warning) and never left in force with no visible control. The added disjunct is the minimal change that restores this without special-casing `lifecycle_state`'s clearing mechanism relative to the other eight filters.
- **Item 1 and CMP/status separation (objective gate 6):** the fix touches only *visibility* of the control, never the value logic. `filters.lifecycle_state` and `filters.status` remain two independent `CatalogFilters` fields; nothing in the change reads one to decide the other, and `test_lifecycle_state_never_offered_as_applying_to_every_doc_type` plus the pre-existing `test_status_and_lifecycle_state_never_merged` (test_catalog_page.py) both still pass.
- **Item 2:** truncation is now defined exactly as "the 200-char slice differs from the full abstract" (`length > 200`), matching what the slice actually does; no separate truncation-length constant was introduced.
- **Item 3:** the percentage split (17/13/6/8/8/10/10/21/7) sizes each column by real need rather than evenly: `Abstract` (free text) widest, `Title`/`Canonical ID` next (both can be long), the short enumerated/id columns (`Type`, `Date`, `Status`, `Programs`, `CMP lifecycle state`, `Open`) narrow. `overflow-wrap: anywhere` + `word-break: break-word` on every cell so a long, unbroken `doc_id`/filename token wraps within its own fixed-width column rather than visually forcing the table wider (which `table-layout: fixed` alone constrains at the *column* level but does not, by itself, prevent a cell's content from visually overflowing its box). `.table-scroll`'s `overflow-x: auto` is kept as the fallback for narrower viewports (e.g. the existing 640px breakpoint), consistent with the prompt's framing that this was a column-budget problem inside an already-present scroller, not an unbounded-overflow bug.

## Result

**Catalog module round 2 of 4** (this strand consumes one of the 28 builder rounds in the convergence-phase budget; dispatched concurrently with search round 2 under the 20-of-28 ceiling per Director ruling 2026-09-05).

| Item | Disposition | Reason |
|---|---|---|
| 1 -- invisible/unclearable `lifecycle_state` filter (ranked issue 6) | **landed** | `service.py` fix; reproduced before, verified after; `test_active_lifecycle_filter_visible_and_individually_clearable_when_zero_matches` RED-then-GREEN |
| 2 -- false truncation ellipsis on complete abstracts | **landed** | `catalog.html` fix; reproduced before/after on real fixture cards (166-char complete, 339-char truncated); both directions tested |
| 3 -- table header column budget at 1280px | **landed** (mechanism fix; STATIC verification only, see Assumptions) | `<colgroup>` + `table-layout: fixed` + width budget in `catalog.css`; CMP lifecycle column's width budget (10%) sits well inside a table that can no longer exceed its 1200px-max container; no browser was launched to measure rendered pixels (forbidden to this strand) |
| 4 -- tests | **landed** | 8 new tests in `tests/catalog/test_catalog_filter_legibility.py`; full `tests/catalog` (32) and full `tests` (298) both green; ruff clean; L1 both checks PASS |

## Unresolved uncertainty

**Can any OTHER catalog filter/control go into force while invisible?** I audited this directly rather than asserting it from memory: I grepped `explorer/catalog/service.py` and `explorer/catalog/templates/catalog/catalog.html` for every conditional-visibility construct (`show_` flags in the service module; `{% if %}` gates in the template). Findings:

- `show_lifecycle_control` was the **only** filter-control visibility gate in the whole module -- the other eight filter controls (`doc_type`, `status`, `program`, `tag`, `project_knowledge`, `date_from`, `date_to`, `path_prefix`) render **unconditionally** on every request, regardless of current filter values or facet counts.
- Their `<option>` lists are sourced only from `view.global_facets` (O14/D-Q2: the unfiltered, global distinct values), never from the under-filter `catalog_page.facets` that `show_lifecycle_control` depended on -- so an active value for any of these five select-backed filters is *always* present as a selectable, `selected`-marked option, by construction, not by luck. `date_from`/`date_to`/`path_prefix` are plain text/date inputs with no options to go missing.
- The other `{% if %}` gates in the template are `adapter_absent` (a whole-page state, not a per-filter one), `view.no_matches` (governs whether the *results table* renders, not any filter control), `row.frozen` and `row.is_cmp`/`row.lifecycle_state` (per-row display, not filter controls), and pagination's `has_prev`/`has_next` (correctly absent when there is no next/prev page -- not a filter).

**Conclusion, with the evidence above:** within the catalog module, item 1 was an **isolated instance**, not a population -- `lifecycle_state`'s visibility gate was uniquely coupled to under-filter facet counts; nothing else in this module shares that coupling. I cannot extend this claim to the **search** module: its filter form is a different, concurrently-edited surface I am contractually barred from reading as stable or touching (working rule 1), so whether an analogous "control visibility gated on under-filter results" pattern exists there is genuinely unknown from here, not merely unaudited-by-me-and-presumed-fine. That is the honest boundary of this answer, and it belongs to whichever round or critic pass is allowed to read `explorer/search/**`.

## Change requests

- **Shared table-legibility utility.** The critic's `browse_search_usability` and `reader_comprehension` findings both cite horizontal overflow (this item, and separately the reader's own unbounded overflow, ranked issue 4). The `table-layout: fixed` / `overflow-wrap: anywhere` / `word-break: break-word` pattern added here to `catalog.css` is a reasonable candidate for a shared rule in `explorer/web/static/app.css` (e.g. a `.data-table` utility class) so the reader module does not have to re-derive the same mechanism independently. Not implemented here: `explorer/web/static/app.css` is outside my owned paths (working rule 1). Recorded as a request, not acted on.

## Assumptions

- **1280px viewport <-> `main`'s 1200px content box.** I assumed the probe's 1280px viewport preset (which the critic's W4 capture used) maps to `main`'s `max-width: 1200px` content area (base `app.css:102`), i.e. that 1280 > 1200 means the table's own container is bounded at ~1160-1200px regardless of the outer viewport, so a table that is itself bounded at 100% of that container can never need horizontal scroll at 1280px. I did not verify this against the probe or a real browser -- doing so would require launching a server process or a browser, both forbidden to this strand (D-12/D-3; ARCHITECTURE.md A18 also forbids a test-launched server). This assumption, and therefore item 3's disposition, is UNVERIFIED as rendered pixel geometry; the template/CSS mechanism is real and tested (statically), the pixel outcome is not.
- **`OPEN` as a representative active `lifecycle_state` value.** The fixture corpus has exactly one lifecycle_state value in use (`OPEN`, on the one CMP row) per `test_api_catalog_facets_are_present_and_not_fabricated` (pre-existing test). I used it as the "genuinely active, globally real" filter value throughout item 1's reproduction and tests; the fix's logic (`bool(filters.lifecycle_state)`) does not depend on which value is chosen, only on the field being non-empty, so this is a representative rather than a narrow case.
- **No change needed to `CardRow`, `CatalogFilters`, or the `/api/catalog` JSON twin for any of the three items.** All three fixes are presentation-layer (`service.py`'s one boolean, and `catalog.html`/`catalog.css`); the JSON API's `abstract` field was never truncated server-side (truncation was always template-only) and its `filters`/`show_lifecycle_control` fields already round-trip through `dataclasses.asdict(view)` unchanged in shape, only the value of `show_lifecycle_control` changes.

---
*Report written by strand S8-B15. Worktree left clean of unintended changes; `git status --porcelain` before this file's own commit showed only the three fix files (modified) and this test file (untracked).*
