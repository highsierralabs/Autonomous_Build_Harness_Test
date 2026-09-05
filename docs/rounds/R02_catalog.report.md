# R02_catalog -- round report (task B4)

## Header

- Hand: RHACO-HND-20260903-001 section 2 I as amended by A1.3
- Strand: S4-B4 (module builder, catalog), tier mid, agent_type general-purpose write-scoped to the worktree
- Model: You are powered by the model named Sonnet 5. The exact model ID is claude-sonnet-5.
- Worktree: `C:\highsierralabs\RHACO_Corpus_Explorer\.worktrees\catalog`
- Branch: `build/catalog`, checked out at `c96664dd82e19da730cbd741f0e2ace43501121d`
- t_start_utc: 2026-09-05T00:32:19.9998578Z
- t_end_utc: 2026-09-05T00:45:07.0434862Z
- Round: 2 (wave 2), catalog module round 1 of budget 4, task B4

Archived prompt of record: `docs/rounds/R02_catalog.prompt.md`, sha256
`847048563d9a059a98e6382b95eedf8e38fa3f52d7a8d45fd4e8fd1c810c4755`, 14,725
bytes, UTF-8, LF -- confirmed byte-identical via `Get-FileHash -Algorithm
SHA256` before any other action (step 2 of the dispatch procedure).

## Change

Landed, inside the worktree, on owned paths only (`explorer/catalog/**`,
`tests/catalog/**`, this report):

1. **`explorer/catalog/__init__.py`** -- module docstring only.
2. **`explorer/catalog/service.py`** -- `build_view(adapter, settings, query: dict) -> CatalogView`:
   - Parses the request's query parameters into `CatalogFilters` (`doc_type`,
     `status`, `lifecycle_state`, `program`, `tag`, `project_knowledge`,
     `date_from`, `date_to`, `path_prefix` -- empty strings become `None`;
     nothing else is read), `sort` (`<column>[:asc|desc]`, passed through
     unvalidated to the adapter, whose own whitelist in
     `explorer/corpus_adapter/sql.py` is the actual authority), `page`
     (`>= 1`), `page_size` (default `settings.page_size`, capped at 200).
   - Calls `adapter.catalog(filters, sort, page, page_size)` for the rows
     and the under-filter facet counts, `adapter.facets()` for the global
     control vocabularies, `adapter.index_meta()` for the total indexed
     card count and db path.
   - Computes `page_count`, `has_prev`/`has_next`, `prev_page`/`next_page`,
     and a `query_string_no_page` (urlencoded current filters + sort +
     page_size) for pagination links that preserve filters.
   - `show_lifecycle_control = filters.doc_type == "CMP" or bool(catalog_page.facets.lifecycle_states)`
     (ARCHITECTURE.md 4.2's exact rule).
   - Row rendering: `dataclasses.asdict(card)` plus `frozen` (a
     `CardRow.@property`, so it does not otherwise survive `asdict`) and
     `is_cmp`, so the JSON twin carries every `CardRow` field, `card_ref`,
     `doc_ref`, and `frozen` per the dispatch.
   - No fabricated values anywhere: every control's option list comes from
     `adapter.facets()` (D-Q2, the index's own distinct values); a filter
     combination that matches nothing produces `total == 0` and
     `no_matches = True` with a fixed, honest message
     (`NO_MATCH_TEXT = "no cards match the current filters"`) -- never a
     fallback substitution.
3. **`explorer/catalog/routes.py`** -- `register(app)`:
   - `GET /` -- HTML, `catalog/catalog.html` extending `base.html`.
   - `GET /api/catalog` -- JSON twin, `dataclasses.asdict(view)`.
   - The adapter is reached only through `explorer.app.get_adapter(request)`;
     `RuntimeError` -> HTML notice at 503 / JSON `{"error": "corpus_adapter not built"}` at 503 (the diagnostics precedent, byte-identical message).
4. **`explorer/catalog/templates/catalog/catalog.html`** -- `<html data-mode="catalog">`
   (a fixed literal -- the catalog page never runs a retrieval call, so there
   is no `mode_effective` to reflect and no `data-vector` attribute); hidden
   `#keyhelp` element; total-indexed / total-matching counts (each also
   exposed as a `data-total-indexed` / `data-total-matching` attribute for
   probe/automated cross-checking); one `<form method="get" action="/">`
   carrying every filter control (`doc_type`, `status`, the **separate**
   conditionally-rendered `lifecycle_state` control labelled "CMP lifecycle
   state (campaigns only)", `program`, `tag`, `project_knowledge`,
   `date_from`, `date_to`, `path_prefix`, and a combined `sort` select) plus
   a "Clear filters" link to `/`; a table with `<caption>`, `scope="col"`
   headers (Title, Canonical ID / filename, Type, Date, Status, Programs,
   CMP lifecycle state, Abstract, Open); every row `<tr>` carries
   `data-doc-id`, `data-card-ref`, `data-status`, `data-lifecycle-state`;
   frozen status renders the visible text "frozen" (never colour-only);
   a non-CMP row carrying a `lifecycle_state` value renders the visible text
   "informational (non-CMP)"; compact abstract = first 200 characters + a
   visible " ..." marker; open action links to `/doc/<card_ref>`;
   pagination links built from `query_string_no_page` preserve every filter,
   the sort, and the page size.
5. **`explorer/catalog/static/catalog.css`** -- filter-form grid layout,
   `.sr-only`, table-scroll wrapper; linked via `/static/catalog/catalog.css`
   (the app factory's per-module static mount, verified in `explorer/app.py`
   lines 90-93) through `base.html`'s `{% block scripts %}` hook (the only
   template-extension point `base.html` exposes; there is no head-injection
   block to add a `<link>` to, and `explorer/web/**` is out of my owned
   paths).
6. **`tests/catalog/`** (24 tests, all green):
   - `conftest.py` -- session-scoped fixture index build via
     `fixtures.build_fixture_index.build` into `tmp_path_factory`; a shared
     `create_app(Settings(db_path=<tmp db>, docs_root=<fixture corpus>))`;
     a `client` fixture (`TestClient`); a `client_adapter_absent` fixture
     (a separate app instance with `app.state.adapter = ADAPTER_ABSENT`);
     and an autouse, session-scoped live-index no-mutation guard
     (`corpus_cards_sha` + db mtime, before/after) whose approach is copied
     from `tests/corpus_adapter/conftest.py` (not imported, per the
     dispatch's testing conventions paragraph).
   - `test_catalog_page.py` (14 tests) -- home lists all 7 fixture rows with
     `data-doc-id`/total counts; `doc_type=CMP` / `doc_type=HND` lifecycle
     behaviour; `status=Superseded` frozen marker; `program=DetPhys` and
     `tag=amendment` narrowing; `sort=title:asc` ordering (asserted against
     the exact expected `card_ref` sequence); `date_from` / `date_to`
     bounding; a no-match filter (`doc_type=SOP`) yielding zero rows and the
     "no cards match" text; pagination with `page_size=3` partitioning the
     seven rows across three pages with no loss or duplication; pagination
     links preserving filters; status/lifecycle_state never merged (both
     attributes present, and the status `<td>` never contains the
     lifecycle value); the "Clear filters" link.
   - `test_catalog_api.py` (6 tests) -- JSON shape and totals; facets not
     fabricated; API/page cross-checks for `doc_type=CMP` and `doc_type=HND`
     (same `card_ref` sets, same `show_lifecycle_control`); no-match shape;
     filters-in-force echoed.
   - `test_catalog_faults.py` (2 tests) -- adapter-absent 503 for both the
     page and the API.
   - `test_catalog_live_smoke.py` (2 tests) -- `Settings()` defaults against
     the real corpus_index.db, asserting only shape (HTTP 200, a positive
     total), guarded by the conftest's live-index fingerprint check.

No file outside `explorer/catalog/**`, `tests/catalog/**`, and this report
was modified. `explorer/app.py`, `explorer/config.py`, `explorer/models.py`,
`explorer/corpus_adapter/**`, `explorer/diagnostics/**`, `explorer/web/**`,
`fixtures/**`, `tools/**` were read only.

## Evidence

Checks actually run, in order, with results:

| # | Check | Command | Result |
|---|---|---|---|
| 1 | Prompt hash confirmation | `Get-FileHash -Algorithm SHA256 docs\rounds\R02_catalog.prompt.md` | `847048563D9A059A98E6382B95EEDF8E38FA3F52D7A8D45FD4E8FD1C810C4755` -- matches the dispatch, case-insensitive; `wc -c` confirmed 14,725 bytes |
| 2 | Worktree baseline check | `git status`; `git log --oneline -5`; `git rev-parse HEAD` | clean, on `build/catalog`, HEAD `c96664dd82e19da730cbd741f0e2ace43501121d` (the correction-boundary commit named in the dispatch) |
| 3 | Fixture-value verification (before writing any test) | ad hoc script (`fixtures.build_fixture_index.build` into a real `tempfile.mkdtemp()`, then `CorpusAdapter.catalog()`/`.facets()`/`.index_meta()` against it), deleted after use -- never committed | Confirmed independently, not merely read from `docs/rounds/R01_probe.report.md`: 7 cards; `doc_type=HND` -> 2 rows sharing `doc_id=RHACO-HND-20260115-003`, neither carrying `lifecycle_state`; `doc_type=CMP` -> 1 row, `lifecycle_state=OPEN`; `program=DetPhys` -> `{RHACO-ANL-20260115-002, RHACO-EVT-20260115-004}`; `tag=amendment` -> the amendment row only; `status=Superseded` -> `RHACO_Fixture_Reference_v1_0`, `frozen=True`; `date_from=2026-01-15` -> 5 rows; `date_to=2026-01-10` -> 2 rows (both REF cards); `doc_type=SOP` -> 0 rows; `page_size=3` over 7 rows -> pages of 3/3/1; `sort=title:asc` order verified title-by-title |
| 4 | Gate (a) ruff | `C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m ruff check explorer tools tests --output-format concise` | `All checks passed!` exit 0 |
| 5 | Gate (b) pytest, catalog only | `C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m pytest tests/catalog -q` | `24 passed` exit 0 |
| 6 | Full-suite regression | `C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m pytest tests -q` | `106 passed` exit 0 (82 pre-existing + 24 new; nothing broken by this round) |
| 7 | Gate (c) L1 index-write check | `C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe tools/l1_index_write_check.py` | `hits=6 allowlisted=6 defects=0 verdict=PASS` exit 0 (all 6 hits are inside `fixtures/build_fixture_index.py`, the sole allowlisted file; catalog added zero hits) |
| 8 | Worktree cleanliness | `git status --porcelain` (before commit) | only `explorer/catalog/` and `tests/catalog/` untracked, no stray files (the verification script from check #3 was deleted, not committed) |

Every "tested" claim above names the test file or command that produced it.

## Material alternatives

- **Row shape for the JSON twin.** Considered keeping `CatalogView.rows` as
  `list[CardRow]` and letting `dataclasses.asdict(view)` handle the
  conversion. Rejected: `CardRow.frozen` is a `@property`, not a dataclass
  field, so plain `asdict` silently drops it, and the dispatch explicitly
  requires "every CardRow field plus card_ref / doc_ref / frozen" in the
  JSON twin. Considered subclassing `CardRow` to add a `frozen: bool` field;
  rejected because `CardRow.frozen` is a read-only property with no setter,
  and a dataclass subclass's generated `__init__` would call `self.frozen =
  value`, which raises `AttributeError` through the inherited property
  descriptor before ever reaching instance `__dict__`. Chose: build each row
  as a plain `dict` (`dataclasses.asdict(card)` plus `frozen`/`is_cmp`
  injected), stored as `CatalogView.rows: list[dict]`. `dataclasses.asdict`
  passes an already-plain dict straight through, and Jinja's dot notation
  falls back to `__getitem__`, so both the JSON route and the template read
  `row.<field>` identically with no special-casing.
- **Where to compute the "effective" (whitelisted, defaulted) sort column
  and direction for display.** Considered importing
  `explorer.corpus_adapter.sql.parse_sort` / `SORT_COLUMNS` directly, since
  they are the actual authority. Rejected in favour of a small, explicitly
  commented local mirror in `explorer/catalog/service.py`: working rule 1
  scopes my writes to `explorer/catalog/**`, and while *reading* another
  module's public names is not a rule violation, coupling the catalog
  module's display logic to `corpus_adapter`'s internal whitelist constant
  would make a future adapter-side rename or refactor silently break
  catalog's sort-label rendering with no compile-time signal. The local
  mirror is documented as display-only and non-authoritative; correctness
  of the actual SQL sort is entirely the adapter's, unaffected by this
  choice either way.
- **Pagination link construction.** Considered a Jinja macro building query
  strings inline from `view.filters` fields. Chose to precompute
  `query_string_no_page` (`urlencode`) once in `service.py` instead: simpler
  templates, and one place (Python, easily unit-testable in principle) owns
  the URL-encoding rules rather than duplicating them in Jinja.
- **Stylesheet placement.** `base.html` (owned by the `web` builder, wave 3)
  exposes only `{% block title %}`, `{% block html_attrs %}`,
  `{% block main_attrs %}`, `{% block content %}`, and `{% block scripts %}`
  -- no head-injection hook. Considered omitting `catalog.css` entirely
  (relying only on `app.css`'s existing table/focus styling) to avoid
  loading a stylesheet from the body-level `scripts` block. Chose to add it
  anyway, loaded via `{% block scripts %}` as a `<link>` (functionally
  correct -- the browser still fetches and applies it; the only cost is a
  theoretical flash-of-unstyled-filter-form on a slow connection, not a
  functional defect) because the nine-control filter form is materially
  harder to scan without a grid layout. Recorded as a **Change request**
  below for `web`/the integrator to add a head-injection block in a later
  wave.
- **Whether to reset `page` to 1 when a filter form is resubmitted.** The
  GET filter `<form>` has no `page` field, so resubmitting filters always
  lands on page 1 implicitly (the browser omits fields absent from the
  form); `page_size` is preserved via a hidden input so a mid-browsing page
  size choice survives a filter change. Considered adding a `page` hidden
  input pinned to `1` for clarity; decided the omission is self-explanatory
  and one fewer moving part.

## Decisions

- Filter parsing lives entirely in `service.py.parse_filters` /
  `parse_sort` / `parse_page` / `parse_page_size`, each independently
  callable and independently correct against malformed input (non-integer
  `page`/`page_size` fall back to `1` / `settings.page_size`; an
  out-of-whitelist `sort` column is not rejected here -- it is passed
  through and the adapter's own `parse_sort` silently normalizes it, per
  ARCHITECTURE.md 4.1's documented behaviour).
- `show_lifecycle_control` reads `catalog_page.facets.lifecycle_states`
  (the **under-filter** facets from `adapter.catalog()`), not
  `adapter.facets()` (the global vocabulary) -- confirmed by check #3 above
  that this produces the exact behaviour the dispatch specifies for both
  `doc_type=CMP` (control shown) and `doc_type=HND` (control absent,
  because no HND row carries a `lifecycle_state`).
- Every dropdown's *options* come from `adapter.facets()` (the global,
  unfiltered vocabulary) so that narrowing by one facet never hides another
  facet's valid choices from the control -- CONSTRAINTS.md O14's
  "filtering never fabricates values" is read as also forbidding the
  inverse failure (a control silently losing options a filtered view
  happens not to intersect).
- The compact abstract is always `abstract[:200]` followed by a literal
  " ..." marker (when an abstract is present at all), regardless of whether
  the true abstract is longer than 200 characters -- read literally from
  the dispatch's wording ("first 200 characters ... then a visible ' ...'
  marker") as a fixed compact-preview convention, not a conditional
  truncation-only marker. Not directly tested by the required test list
  (which does not exercise the abstract text), so this is a judgment call,
  recorded under "Assumptions" below.

## Result

**COMPLETE.** All four deliverables built on the owned paths only. Gate (a)
ruff clean, gate (b) `tests/catalog` 24/24 green (and the full workspace
suite 106/106, confirming no regression), gate (c) L1 index-write check
PASS with catalog contributing zero hits. Every required test-list item in
the dispatch (task B4 deliverable 4) has a corresponding, passing assertion
(see Evidence #5 and the file-by-file breakdown in "Change"). Worktree left
clean; commits list follows in the structured result's `git rev-parse HEAD`.

## Unresolved uncertainty

- **The compact-abstract-marker convention** (always append " ..." vs. only
  when truncated) is a judgment call, not required by any test in the
  dispatch's test list -- UNVERIFIED against any other builder's or the
  probe's expectation, since no fixture card's abstract length was checked
  against the 200-character boundary in this round (every fixture abstract
  happens to be well under 200 characters, so this convention was never
  exercised at the boundary by the tests above).
- **`path_prefix` and `project_knowledge` controls are UNVERIFIED by a
  dedicated test** -- both are parsed (task B4 item 1 requires it) and
  rendered as form controls (ARCHITECTURE.md 4.2 lists `path_prefix`
  explicitly), but the required test list (task B4 item 4) does not name
  either, and no fixture-shaped assertion exercises them here. `service.py`
  treats them identically to every other `CatalogFilters` field (passed to
  `adapter.catalog()`, which is already tested end-to-end against the live
  corpus in `tests/corpus_adapter/`), so the risk is narrow, but it is not
  this round's own test evidence.
- **Whether the catalog's `<html data-mode="catalog">` literal is the
  correct probe-facing value** is UNVERIFIED against `tools/probe_corpus_explorer.py`'s
  actual `W1`-style preset runners, since those are still stubs
  (`not_implemented_yet`, per `docs/rounds/R01_probe.report.md`) in this
  worktree; the value was chosen to satisfy the dispatch's literal
  instruction (`<html data-mode="catalog">`) and ARCHITECTURE.md A19's
  general convention, not against a live probe assertion.

## Change requests

- **Requestor:** catalog (B4). **Affected contract/path:**
  `explorer/web/templates/base.html` (owned by the `web` builder, wave 3).
  **Change:** add a head-injection block (e.g. `{% block head_extra %}{% endblock %}`
  placed inside `<head>`, after the existing `<link rel="stylesheet"
  href="/static/web/app.css">`) so a module's own stylesheet can be linked
  from `<head>` instead of the body-level `{% block scripts %}` hook.
  **Evidence:** `explorer/web/templates/base.html` currently exposes only
  `title`, `html_attrs`, `main_attrs`, `content`, and `scripts` (the last
  rendered at the end of `<body>`); this round's `catalog.html` links
  `/static/catalog/catalog.css` through `{% block scripts %}` for lack of
  any earlier hook (see "Material alternatives" above) -- functionally
  correct today, but not the conventional place for a stylesheet.
  **Compatibility impact:** none -- an additive empty block is a no-op
  until a module uses it; `catalog.html`'s current placement keeps working
  unchanged either way. **Migration:** once the block exists, `catalog.html`'s
  stylesheet `<link>` can move from `{% block scripts %}` into the new
  block in a later round; not required for this round's tests to pass.
  **Invalidated tests/probes:** none.

## Assumptions

- `program=DetPhys` and `tag=amendment` were chosen as the dispatch's
  "`<a fixture program>`" / "`<a fixture tag>`" test values because they
  narrow to a small, unambiguous, independently-verified subset (2 rows and
  1 row respectively) -- any other fixture program/tag would have served
  the same test-list requirement equally well.
- "Nothing else is accepted" (task B4 item 1, query parameters) is read as
  "no other query parameter is read into `CatalogFilters`" -- an unknown
  query parameter is silently ignored (not a 400 error), matching how
  `sort`/`page`/`page_size` already degrade gracefully on malformed input
  rather than raising.
- The catalog page's stylesheet is loaded via `{% block scripts %}` (see
  "Material alternatives") because `base.html` is out of my owned paths and
  offers no other extension point; this is treated as a compatible,
  non-invasive choice pending the change request above, not a violation of
  working rule 1 (no file under `explorer/web/**` was modified).
- `CatalogFilters.path_prefix` and `.project_knowledge` are exposed as form
  controls (a text input and a select respectively) on the strength of
  ARCHITECTURE.md 4.2's filter-form list, even though the required test
  list does not name either -- read as "build the complete contract, test
  what the dispatch enumerates."
