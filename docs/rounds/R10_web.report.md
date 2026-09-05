# R10 web report -- strand S8-B16 (web module round 2 of 4)

## Header

| Field | Value |
|---|---|
| Strand | S8-B16, module builder (web), round 2 of 4 -- twentieth of a Director-set ceiling of 20 for the convergence phase |
| Role | shell de-duplication and cross-page legibility (task B16) |
| Model | Claude Sonnet 5 (model id `claude-sonnet-5`) -- sentence from my own system prompt: "You are powered by the model named Sonnet 5. The exact model ID is claude-sonnet-5." |
| Dispatch record | RHACO-HND-20260903-001 section 2 I as amended by A1.3 |
| Prompt of record | `docs/rounds/R10_web.prompt.md`, sha256 `feb168985c774e70219f86f10def13adbc7fba8ea2fdd4a64658de7fa9a83329`, 14327 bytes -- **verified, matches** (`Get-FileHash -Algorithm SHA256` observed `FEB168985C774E70219F86F10DEF13ADBC7FBA8EA2FDD4A64658DE7FA9A83329`) |
| Worktree | `C:\highsierralabs\RHACO_Corpus_Explorer\.worktrees\web`, branch `build/web` |
| Base commit (`git rev-parse HEAD` at start) | `c89cfbc4ee2e7e904cdb9d714ca7ae14ce510b09` |
| Ancestor check | `git merge-base --is-ancestor 3f62226 HEAD` -- exit 0, HEAD contains `3f62226` |
| Window start (UTC) | 2026-09-05T16:47:22.9556747Z |
| Window end (UTC) | 2026-09-05T17:05:12.3132863Z |
| Concurrent strand | none -- "No other strand is running; you are alone this round" (per the dispatch) |

## Change

Nine files touched across seven commits, exactly as licensed by working rule 1 (`explorer/web/**`, `tests/web/**`, this report, plus the one named exception).

1. **`explorer/web/templates/base.html`** (commit `dc202de`): the `#keyhelp` block (six `<dt>`/`<dd>` pairs, byte-identical to the five removed copies) now renders once, inside `<main>` before `{% block content %}` -- so it appears on every merged page regardless of which page's own content block used to carry it. A new `<form id="global-search-form" method="get" action="/search">` with `<input type="search" id="global-search-q" name="q">` was added to the nav, guarded by `{% if not _nav_active.search %}` so it does not render on the search page itself (which already has its own inline field, `id="q"`).
2. **Five page templates** (commit `bb1c014`): `explorer/catalog/templates/catalog/catalog.html`, `explorer/search/templates/search/search.html`, `explorer/reader/templates/reader/reader.html`, `explorer/lineage/templates/lineage/lineage.html`, `explorer/diagnostics/templates/diagnostics/diagnostics.html` -- the licensed exception, exercised exactly as scoped: each file's own byte-identical `#keyhelp` block deleted, nothing else touched (see Evidence -- diffs pasted in full).
3. **`explorer/web/static/app.css`** (commit `13e934d`): `.global-search` layout rules (item 2); `.doc-body table { table-layout: fixed; }` plus `.doc-body table th, .doc-body table td { overflow-wrap: anywhere; word-break: break-word; }` (item 3, new selector); the shared `pre { ... }` rule extended with `overflow-wrap: anywhere; word-break: break-word;` (item 3, existing selector extended); the file's header comment and the `#keyhelp` section comment updated to describe the moved, single-copy contract.
4. **`explorer/web/static/app.js`** (commit `04381c1`): docstring-only -- the `/` and `?` key comments now describe the shell-level affordances. No binding logic changed (still exactly the same `"/"`, `"?"`, `"j"`, `"k"`, `"Enter"`, `"Escape"`, `"ArrowDown"`, `"ArrowUp"` literals `tests/web/test_app_js_content.py` already asserts).
5. **Three new test files** (commits `cce6216`, `8d81844`, `06342b7`): `tests/web/test_keyhelp_shell.py` (17 tests, item 1), `tests/web/test_global_search_affordance.py` (15 tests, item 2), `tests/web/test_wide_content_legibility.py` (5 tests, item 3, all labelled static).

No other file was read as a write target. `explorer/app.py`, `config.py`, `models.py`, `faults.py`, `corpus_adapter/**`, `tools/**` (other than running, never editing, `l1_index_write_check.py`), `fixtures/**`, and every other module's non-template files were neither read as write targets nor touched.

## Evidence

### Item 1 -- verifying byte-identity BEFORE deleting anything (item 2's "verify before assuming")

Read all five `#keyhelp` blocks (catalog.html:9-18, search.html:93-102, reader.html:7-16, lineage.html:7-16, diagnostics.html:8-17) and then verified programmatically, not by eye, with the same extraction regex `tests/integration/test_keyhelp_contract.py` uses:

```
C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe - <<'PYEOF'
[regex-extract each file's #keyhelp block via the KEYHELP_RE pattern, sha256 it]
PYEOF

explorer/catalog/templates/catalog/catalog.html 4d6609c3baac4a570db0282d605a86a486257b524ca4ca3af44ac29addfb79fa 426
explorer/search/templates/search/search.html 4d6609c3baac4a570db0282d605a86a486257b524ca4ca3af44ac29addfb79fa 426
explorer/reader/templates/reader/reader.html 4d6609c3baac4a570db0282d605a86a486257b524ca4ca3af44ac29addfb79fa 426
explorer/diagnostics/templates/diagnostics/diagnostics.html 4d6609c3baac4a570db0282d605a86a486257b524ca4ca3af44ac29addfb79fa 426
explorer/lineage/templates/lineage/lineage.html 4d6609c3baac4a570db0282d605a86a486257b524ca4ca3af44ac29addfb79fa 426
UNIQUE HASHES: 1 -> IDENTICAL
```

**No drift.** All five copies were still byte-identical (426 bytes, sha256 `4d6609c3...`) at the moment this round read them -- unlike the round-3 history the prompt names (the lineage page copying a stale block inside the very wave that created it), this time nothing had drifted before the fix landed.

### Item 1 -- the five deletions, in full (nothing else touched)

```diff
diff --git a/explorer/catalog/templates/catalog/catalog.html b/explorer/catalog/templates/catalog/catalog.html
@@ -6,17 +6,6 @@
 <h1>Catalog</h1>
 <p class="lede">What is in the RHACO corpus? Browse, filter, and sort every carded document.</p>

-<div id="keyhelp" hidden>
-  <h2>Keyboard shortcuts</h2>
-  <dl>
-    <dt><kbd>/</kbd></dt><dd>focus search</dd>
-    <dt><kbd>j</kbd> / <kbd>k</kbd></dt><dd>move the result selection down / up (<kbd>Down</kbd> / <kbd>Up</kbd> also work)</dd>
-    <dt><kbd>Enter</kbd></dt><dd>open the selected result</dd>
-    <dt><kbd>Escape</kbd></dt><dd>clear the selection</dd>
-    <dt><kbd>?</kbd></dt><dd>toggle this help</dd>
-  </dl>
-</div>
-
 {% if adapter_absent %}
 <div class="degradation" role="status" data-catalog-state="adapter-absent">
```
(Identical -6,17→-... shape for search.html, reader.html, lineage.html, diagnostics.html -- `git diff` for the full five-file set was inspected in full before committing; every file's diff is exactly this one block removed, confirmed with `git diff -- <the five paths>` showing only `-` lines for the block plus its one surrounding blank line, and zero `+` lines, zero other hunks.)

### Item 1 -- render-time proof the block still appears once per page, unchanged content, same id and toggle target

```
C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m pytest tests/web/test_keyhelp_shell.py -v
```
17 passed (5 pages x 3 parametrized behavioural tests + 2 module-level tests), including `test_every_merged_page_renders_exactly_one_keyhelp_block` (catalog `/`, search `/search?q=fixture`, reader `/doc/reports/RHACO-ANL-20260115-002_Fixture_Analysis.card.yaml`, diagnostics `/diagnostics`, lineage `/lineage/reports/RHACO-CMP-20260115-001_Fixture_Campaign.card.yaml`) and `test_no_former_keyhelp_template_carries_its_own_copy_any_more` (the O-2 regression guard, written to FAIL on re-introduction).

### Item 2 -- the `/` key now has something real to focus everywhere

`app.js`'s `searchBox()` is unchanged (`document.querySelector('input[name="q"]')`); what changed is that such an input now exists on every page. Chosen shape (a): a real `<form method="get" action="/search">` in the shell nav, guarded off on the search page itself (which keeps its own pre-existing `id="q"` field and behaviour exactly as before -- verified by `test_shell_global_search_form_absent_on_search_itself`, which asserts `id="global-search-form"` is ABSENT there and `id="q"` (the page's own) still present).

```
C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m pytest tests/web/test_global_search_affordance.py -v
```
15 passed: `input[name="q"]` present on all five pages; `#global-search-form` present with `method="get"` / `action="/search"` on the four pages that previously had nothing (catalog, reader, diagnostics, lineage); absent on search; no `onsubmit` handler on the form (real navigation, not a second retrieval surface); the field has an associated `<label for="global-search-q">`.

### Item 3 -- the wide-content legibility rules, static

```
C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m pytest tests/web/test_wide_content_legibility.py -v
```
5 passed, all labelled static in their own docstrings: `.doc-body table { table-layout: fixed; }` present; its `th`/`td` wrap long tokens; the shared `pre` rule (which reaches `#card-panel`'s unclassed `<pre>` blocks at reader.html:243,251 without touching reader.css) wraps too; neither rule hides overflow (checked against the whole file with the one pre-existing, unrelated `.sr-only { overflow: hidden; ... }` excluded); the pre-existing bare `table { border-collapse: collapse; width: 100%; }` rule is untouched -- the fix is scoped, not global.

No browser was launched to measure rendered pixels (forbidden to this strand, D-12/D-3). Whether the reader page now actually fits 1280px is UNVERIFIED as rendered geometry -- see "Unresolved uncertainty."

### Gate (a) -- ruff

```
C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m ruff check explorer tools tests --output-format concise
All checks passed!
```

### Gate (b) -- tests

```
C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m pytest tests/web -q
.............................................................            [100%]
61 passed, 2 warnings in 3.17s
```

```
C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m pytest tests -q
...
=========================== short test summary info ===========================
FAILED tests/integration/test_keyhelp_contract.py::test_keyhelp_documents_every_bound_key[explorer\catalog\templates\catalog\catalog.html]
FAILED tests/integration/test_keyhelp_contract.py::test_keyhelp_documents_every_bound_key[explorer\search\templates\search\search.html]
FAILED tests/integration/test_keyhelp_contract.py::test_keyhelp_documents_every_bound_key[explorer\reader\templates\reader\reader.html]
FAILED tests/integration/test_keyhelp_contract.py::test_keyhelp_documents_every_bound_key[explorer\diagnostics\templates\diagnostics\diagnostics.html]
FAILED tests/integration/test_keyhelp_contract.py::test_keyhelp_documents_every_bound_key[explorer\lineage\templates\lineage\lineage.html]
FAILED tests/integration/test_keyhelp_contract.py::test_keyhelp_advertises_nothing_it_does_not_bind[explorer\catalog\templates\catalog\catalog.html]
FAILED tests/integration/test_keyhelp_contract.py::test_keyhelp_advertises_nothing_it_does_not_bind[explorer\search\templates\search\search.html]
FAILED tests/integration/test_keyhelp_contract.py::test_keyhelp_advertises_nothing_it_does_not_bind[explorer\reader\templates\reader\reader.html]
FAILED tests/integration/test_keyhelp_contract.py::test_keyhelp_advertises_nothing_it_does_not_bind[explorer\diagnostics\templates\diagnostics\diagnostics.html]
FAILED tests/integration/test_keyhelp_contract.py::test_keyhelp_advertises_nothing_it_does_not_bind[explorer\lineage\templates\lineage\lineage.html]
FAILED tests/integration/test_keyhelp_contract.py::test_every_keyhelp_page_is_registered
11 failed, 329 passed, 2 warnings in 29.70s
```

**This is not a gate PASS, and I am not calling it one.** These 11 failures are the exact, anticipated consequence of item 1: `tests/integration/test_keyhelp_contract.py` is integrator-owned (`tests/integration/` is out of my licensed paths), and its own `KEYHELP_TEMPLATES` constant and `test_every_keyhelp_page_is_registered`'s disk walk both hard-code the assumption that `#keyhelp` lives in the five page templates -- an assumption item 1's own task text told me to break ("Move the block into base.html once... and delete the five copies"). The task anticipated this exactly: *"If the test needs to change shape because the source of truth moved, that is a change request to the integrator ... NOT an edit: say exactly what it should assert now."* I did not edit this file. See "Change requests" below for the precise replacement assertions. Arithmetic check: 303 tests at the round-7 boundary + 37 new (17+15+5 in the three new files) = 340 = 329 passed + 11 failed. No test outside `tests/integration/test_keyhelp_contract.py` regressed.

### Gate (c) -- L1 index-write + import-boundary check

```
C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe tools/l1_index_write_check.py
l1-index-write-check: hits=6 allowlisted=6 defects=0 verdict=PASS
l1-import-boundary: hits=10 licensed=10 defects=0 unused_licences=0 verdict=PASS
```
Both checks PASS -- unaffected by this round's changes (no import, no index-writing call was touched).

## Material alternatives

**Item 2.** The task named two honest shapes and asked me to choose and defend. I chose (a) -- a real global search affordance -- over (b) -- advertise `/` only where it works -- because (a) is strictly more useful (closes the actual usability gap the critic found, rather than narrowing the promise to match the defect) and the task explicitly prefers it when affordable ("(a) is more useful and more work; (b) is honest and cheap"). Within (a), I considered rendering the shell's field unconditionally on all five pages (simpler markup, no `{% if %}` guard) versus hiding it on the search page (what I built). I chose to hide it on search because that page already has a full-featured inline search form (mode/filter controls, not just a `q` box); rendering a second, smaller `input[name="q"]` next to it would be redundant UI solving a problem search does not have, and -- because `document.querySelector` returns the first DOM match and the header renders before `<main>` -- an unconditional field would have silently changed `/`'s existing, already-correct target on the search page from its own prominent inline field to the new, smaller header stub, a behavioural change to a page nothing in this task asked me to touch. The guard is one line (`{% if not _nav_active.search %}`) reusing a boolean base.html already computes, so the cost of avoiding that regression is negligible.

I also considered making the field an unlabelled `<input>` with only a `placeholder` for the visible cue, and rejected it: a placeholder is not an accessible name once the field has content or for a screen-reader user tabbing to a filled/empty field ambiguously, so I added a `.sr-only` `<label for="global-search-q">` (test-verified) at essentially no visual cost, matching `app.css`'s own existing "text-first" accessibility posture (round 1's high-contrast focus-ring rule, its own comment on the `.sr-only` utility).

**Item 3.** The task's own suggestion -- scope to `.doc-body table` or to `pre` inside the document body -- was the material alternative I evaluated against a global rewrite of the bare `table` selector (`table-layout: fixed` for every table on every page). I rejected the global version even though it would likely have been harmless for lineage's and diagnostics's plain tables (neither ships a `<colgroup>` today, so `table-layout: fixed` without explicit widths just splits columns evenly and wraps content, which those pages have not been measured against): it is untested by anyone for those two modules, changes behaviour on two pages this task does not ask me to touch, and the task's own phrasing ("a well-chosen selector... reaches the reader's markup without your touching `explorer/reader/**`") reads as a preference for the narrowest selector that closes the gap, not the broadest one that happens to be convenient. Catalog's own table is already unaffected either way (`.catalog-table` is more specific and already carries its own `table-layout: fixed`), so the only real trade was reader (fixed) versus reader+lineage+diagnostics (fixed, unasked-for, unverified for the latter two). I chose the narrower fix and recorded the broader one as a possible future change, not acted on (see "Change requests").

For the `<pre>` half of item 3, there was no real alternative to extending the existing shared `pre` rule: `#card-panel`'s offending blocks (reader.html:243,251) are unclassed, generic `<pre>` tags with no reader.css rule of their own, so the shared rule was already the only thing styling them, and extending it in place is the minimal change that reaches them without a reader-owned edit.

## Decisions

- **Item 1 invariant, stated once:** `#keyhelp` is now a shell contract like the nav or the authority notice -- declared once in `base.html`, never per page. The five-file exception is scoped exactly to a delete (working rule 1's own words: "and nothing else in those files"); I did not touch indentation, surrounding blank lines beyond the one needed to avoid a double-blank-line, or any other content in those five files, verified above by pasting the full diff.
- **Item 1 placement:** the block now sits immediately inside `<main>`, before `{% block content %}`, on every page -- a single, consistent position (previously catalog and search rendered it after their own `<h1>`/lede, reader/lineage/diagnostics rendered it before their `<h1>`; now it is uniformly first). The task's own caution ("make sure moving it does not change which pages have it, its id, or its toggle behaviour") is about identity and toggle, not exact pixel position, and I judged a consistent position across all five pages an improvement over the pre-existing inconsistency, not a regression.
- **Item 2:** the field's `id="global-search-q"` is distinct from search's own `id="q"`, so no duplicate-id violation exists even in principle (they never render on the same request, since the guard means at most one of them exists per page); `name="q"` is shared deliberately, since that is what makes `/search?q=...` GET navigation work identically from either field.
- **Item 3:** followed the catalog module's own established recipe (`table-layout: fixed` + `overflow-wrap: anywhere` + `word-break: break-word`, `R09_catalog.report.md` Decisions) rather than inventing a new pattern, for consistency across the codebase's two independent fixes to the same class of defect.

## Result

**Web module round 2 of 4.** This strand consumes one of the 28 builder-rounds budget and is the **twentieth round of the Director-set ceiling of 20 for the convergence phase** -- there is no round after this one before critic round 2, per the dispatch record.

| Item | Disposition | Reason |
|---|---|---|
| 1 -- `#keyhelp` duplication (open item O-2) | **landed** | Moved into `base.html` once; five copies deleted (verified byte-identical before deletion, no drift); render-time proof it still appears exactly once per page, `hidden`, same id, same six keys documented (`tests/web/test_keyhelp_shell.py`, 17 tests). `tests/integration/test_keyhelp_contract.py` now fails its own hard-coded five-template assumption -- expected, not editable by this strand, change request filed below. |
| 2 -- `/` advertised on five, worked on one (critic ranked issue 9) | **landed** | Chose shape (a): real `<form method="get" action="/search">` in the shell nav on every page but search (which keeps its own). 15 new tests. |
| 3 -- horizontal overflow, fixed once in the shell (critic ranked issue 4 + catalog's change request) | **landed** (mechanism fix; STATIC verification only) | `.doc-body table` given a fixed column budget; shared `pre` rule extended to wrap unbroken tokens; neither by hiding overflow; the pre-existing bare `table` rule untouched. 5 new tests, all labelled static. No browser was launched to measure rendered pixels -- UNVERIFIED as rendered geometry. |
| 4 -- the limit that cannot be closed | **stated, not closed** (by design) | See "Unresolved uncertainty" below -- the required sentence. |
| 5 -- tests in `tests/web/` | **landed** | 37 new tests across three files (17 + 15 + 5); full `tests/web` (61) green; full `tests` shows the 11 anticipated, non-regressive failures above and nothing else. |

## Unresolved uncertainty

**Item 4's required sentence, stated plainly:** after this round, the keyboard behaviour of this build has still never been executed by any layer. Items 1 and 2 improve the accuracy of the claim `#keyhelp` makes -- the block now genuinely exists once and is genuinely present everywhere it says a key does something, and `/` now genuinely has a real `input[name="q"]` to focus on every page -- but neither item adds behavioural evidence that a keypress in a real browser actually does what the source text says. `tests/web/test_keyhelp_shell.py` and `tests/web/test_global_search_affordance.py` are TestClient-rendered-markup assertions; nothing in this round, or in any layer before it, has driven `app.js` with an actual keydown event. Executing a key press needs a browser; the probe is the only sanctioned launcher and it is exhausted at 4 of 4 with its budget explicitly not waived (build_state.json `modules.probe`). This strand did not attempt to write a test that appears to close this gap.

**Is any OTHER shell contract duplicated per page the way `#keyhelp` was?** I checked rather than guessed, with this command (inline Python, not committed anywhere, run against the five page templates):

```
C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe - <<'PYEOF'
[for each of the 5 templates, extract every 3-consecutive-line run >=20 chars;
 collect which templates share each run; print any shared by >=2 files]
PYEOF
```
Result: 24 distinct 3-line runs are shared across at least two of the five templates. Of those, **the `#keyhelp` block's own lines are the only run shared across all five** (nine overlapping 3-line windows, all covering the same one block). Every other shared run is either a trivial piece of Jinja control flow common to any template extending `base.html` with an `{% if adapter_absent %}...{% elif not_found %}` shape (`{% endif %}\n{% endif %}\n{% endblock %}`, `</div>\n{% elif not_found %}`, etc. -- structural necessity, not a "contract" carrying real content), or a two-file overlap. **So: no other population-scale duplication exists in these five templates. `#keyhelp` was the one shell contract copied everywhere.**

One two-file overlap is worth reporting on its own terms even though it does not meet the "population" bar: `diagnostics.html`'s and `reader.html`'s `adapter_absent` banners share the exact 3-line run `{% if adapter_absent %}\n<div class="degradation" role="status" data-diagnostics-state="adapter-absent">\n  <p><strong>corpus_adapter not built.</strong>`. That is `reader.html` carrying diagnostics's `data-diagnostics-state` attribute name verbatim on `reader.html`'s OWN adapter-absent banner (reader.html:21) -- lineage's equivalent banner correctly reads `data-lineage-state` (lineage.html:21), and diagnostics's own reads `data-diagnostics-state` correctly (diagnostics.html:20) for itself. This reads as a copy-paste artifact from diagnostics into reader, not an intentional shared contract, and it is very likely a genuine mislabeling bug (reader's banner should probably say `data-reader-state`) -- but `reader.html` is not licensed to me beyond the `#keyhelp` deletion (working rule 1), so I have not touched it and have not written a test asserting the "correct" name, since I do not have standing to decide what reader.py's service layer or its own tests expect there. Filed as a change request below.

**Item 3's rendered-pixel gap, restated for this section specifically:** the static tests prove the CSS rules exist and are shaped as claimed; they cannot prove the reader page actually renders within 1280px, matching item 4's limit -- both are "no browser was launched" gaps, but they are two different unclosed claims (item 4 is about keyboard execution; this one is about layout geometry) and I am naming both rather than letting one substitute for the other.

## Change requests

1. **`tests/integration/test_keyhelp_contract.py` needs its shape updated now that the source of truth moved (integrator-owned, not edited here).** Concretely, I believe it should now assert:
   - `test_keyhelp_documents_every_bound_key` / `test_keyhelp_advertises_nothing_it_does_not_bind`: read `explorer/web/templates/base.html` (not the five page templates) and run the same documents-every-bound-key / advertises-nothing-extra checks against its one `#keyhelp` block.
   - `test_every_keyhelp_page_is_registered`: its disk walk is still valuable (it is exactly the regression guard against a copy being re-introduced into a page template), but its assertion should become "the only file under `explorer/` containing `id=\"keyhelp\"` is `explorer/web/templates/base.html`" rather than comparing against the five old paths.
   - `test_app_js_binds_every_documented_key` (the `BINDINGS`-parametrized check against `app.js` itself) needs no change -- it never depended on the page templates and still passes unmodified.
   - I have built the render-time behavioural half of this already, in `tests/web/test_keyhelp_shell.py` (every merged page still renders exactly one `#keyhelp`, hidden, with all six keys) -- the integrator's file would then own the static, cross-file, single-source-of-truth half, matching the existing division of labour (`tests/web/` behavioural via TestClient; `tests/integration/` static, cross-module contract).

2. **`.doc-body table` / shared `pre` legibility rule could be generalized.** This round scoped the fix narrowly (see "Material alternatives") to `.doc-body table` and the existing `pre` rule, deliberately not touching the bare `table` selector that lineage's and diagnostics's own plain tables also match. If either of those modules independently develops the same wide-content problem the reader had, the fix is already written once in `app.css` (`table-layout: fixed` + `overflow-wrap: anywhere` + `word-break: break-word`) and only needs its selector broadened or a shared `.data-table`-style class added to those templates -- a web-owned change, but one that reads their markup as stable first (which I did not do this round, per working rule 1).

3. **`reader.html`'s `adapter_absent` banner carries `data-diagnostics-state` instead of (presumably) `data-reader-state`** (reader.html:21) -- likely a copy-paste artifact from `diagnostics.html`, found via the n-gram check above. Not fixed here: `reader.html` is licensed to this strand only for the `#keyhelp` deletion (working rule 1), and I have no standing to know what value the reader module's own service layer or tests expect there without reading `explorer/reader/**` as a stable surface, which I am not licensed to do either.

## Assumptions

- **`{% if not _nav_active.search %}` is the correct place to hide the shell's search field, not a narrower/broader condition.** `_nav_active.search` is `_path.startswith("/search")`, already computed by `base.html` for nav highlighting -- I assumed reusing it (rather than introducing a second predicate) is correct because the two questions ("is this nav item active" and "does this page already have its own search box") happen to coincide exactly for the search page today. If a future page under `/search/...` existed that did NOT have its own `input[name="q"]`, this assumption would silently hide the shell's affordance there too; no such page exists in this build.
- **`fixture_client` renders `/lineage/{ref}` and `/doc/{ref}` successfully for the two fixture card refs I duplicated from `tests/lineage/conftest.py`'s literal values** (`reports/RHACO-CMP-20260115-001_Fixture_Campaign.card.yaml`) and `tests/web/test_shell.py`'s existing reader ref (`reports/RHACO-ANL-20260115-002_Fixture_Analysis.card.yaml`) -- confirmed by the tests actually passing (200 status asserted in every parametrized case), not merely assumed.
- **No change was needed to `app.js`'s binding logic, `explorer/app.py`, or any route.** All three items were achievable entirely in templates and CSS/comments; `searchBox()`'s selector (`input[name="q"]`) already generalizes correctly to "whichever matching input exists on this page" without modification.
- **The five-file diff, pasted in full in Evidence, is the complete and only change to those files.** Verified with `git diff` before every commit that touched them, not merely asserted from memory.

---
*Report written by strand S8-B16. Worktree left clean: `git status --porcelain` after the seventh commit shows nothing untracked or modified.*
