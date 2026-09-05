# R02_reader -- round report (task B6)

## Header

- Hand: RHACO-HND-20260903-001 section 2 I as amended by A1.3.
- Strand: S4-B6, role module builder (reader), tier mid, model Claude Sonnet 5
  (`claude-sonnet-5`), agent_type general-purpose write-scoped to the worktree,
  pattern #3 candidate (worktree-isolated builder), wave 2 (concurrent with
  `catalog` and `search`, the cap).
- Worktree: `C:\highsierralabs\RHACO_Corpus_Explorer\.worktrees\reader`, branch
  `build/reader`, base commit `c96664dd82e19da730cbd741f0e2ace43501121d` (the
  correction-boundary commit: `corpus_adapter`, `diagnostics`, and the probe
  framework merged and green).
- Interpreter: `C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe`
  (Python 3.13).
- t_start_utc: 2026-09-05T00:32:23Z (first tool call, `(Get-Date).ToUniversalTime().ToString("o")`).
- t_end_utc: 2026-09-05T00:54:49Z (same command, run again at close).
- Round: 1 of budget 4 (module), task B6 (build `explorer/reader`, wave 2 round 1).
- Prompt of record: `docs/rounds/R02_reader.prompt.md`, sha256
  `213db495d7eaf38ff12ef286bde0df4d53983d17a710187b178e972ddab06cec` -- confirmed
  via `Get-FileHash -Algorithm SHA256` before any other action (matches the hash
  in the dispatch message).

## Change

Added `explorer/reader/` (the canonical document and card reader, PROMPT.md 5.4)
and `tests/reader/`, entirely inside the owned paths (`explorer/reader/**`,
`tests/reader/**`, this report). No file outside those paths was touched or
staged; `git status --short` before commit showed only `?? explorer/reader/` and
`?? tests/reader/`.

New files:

- `explorer/reader/__init__.py` -- module docstring only.
- `explorer/reader/service.py` -- `build_view(adapter, settings, card_ref, line)
  -> ReaderView | None` and its view dataclasses (`HeadingView`, `LineView`,
  `RefLink`, `EdgeLink`, `SupersededBanner`, `DocumentView`, `CardPanelView`,
  `ReaderView`). Keeps the card file, the index row, and the document distinct
  (S1) and never blends `status`/`lifecycle_state` (S4).
- `explorer/reader/routes.py` -- `register(app)`: `GET /doc/{card_ref:path}`
  (HTML) and `GET /api/doc/{card_ref:path}` (JSON twin via
  `dataclasses.asdict`); adapter-absent -> 503 on both (the diagnostics
  precedent); unknown/out-of-root card_ref -> 404 on both.
- `explorer/reader/templates/reader/reader.html` -- extends `base.html`; two
  landmarks (`<section id="document">`, `<aside id="card-panel">`); the hidden
  `#keyhelp` element; `<html data-mode="reader">`.
- `explorer/reader/static/reader.css` -- the two-region grid layout, the
  horizontally-scrolling source view, the `.hit` line highlight; linked from
  the template via `<link rel="stylesheet" href="/static/reader/reader.css">`
  inside `{% block content %}` (`base.html` has no head/style block hook, and
  is out of bounds to edit -- see "Material alternatives").
- `tests/reader/conftest.py` -- session-scoped fixture-index build via
  `fixtures.build_fixture_index.build` into `tmp_path_factory`; fault-flavoured
  `TestClient` fixtures (`stale_card_client`, `broken_jump_client`,
  `adapter_absent_client`); a live-index client plus the session-scoped
  `corpus_cards_sha` + mtime no-mutation guard, written independently in the
  same shape as `tests/corpus_adapter/conftest.py` (not imported from it, per
  the dispatch's conventions block).
- `tests/reader/test_reader_page.py`, `test_api.py`, `test_faults.py`,
  `test_adapter_absent.py`, `test_live_smoke.py`, `test_service_unit.py` -- 34
  tests total, all green.

## Evidence

Checks actually run, in order, with results:

| # | Check | Command | Result |
|---|---|---|---|
| 1 | Prompt hash confirmation | `Get-FileHash -Algorithm SHA256 docs\rounds\R02_reader.prompt.md` | `213DB495D7EAF38FF12EF286BDE0DF4D53983D17A710187B178E972DDAB06CEC` -- matches the dispatch (case-insensitive) |
| 2 | Manual render inspection (ANL) | ad hoc script: `TestClient` against a freshly-built fixture db, `GET /doc/reports/RHACO-ANL-20260115-002_Fixture_Analysis.card.yaml` | 200; `data-selected-doc-id="RHACO-ANL-20260115-002"`; heading `id="1-purpose" data-line="3"`; no `data-line-verified="false"`; `data-card-index-mismatch=""`; `/static/reader/reader.css` linked and served 200 |
| 3 | Manual render inspection (HND) | same, `GET /doc/handoffs/RHACO-HND-20260115-003_Fixture_Handoff.card.yaml` | full page dumped and read (see this round's working notes): TOC lines 1/3/9/19 all `data-line-verified="true"`; depends_on shows the CMP link and the literal `RHACO-ANL-20260101-099` marked "unresolved in index"; "amended by" links to the Amendment A1 card_ref; "campaign child of" links to the CMP card_ref; the generic "Lineage (all typed edges)" list additionally shows the raw `amends` `from_id` (the amendment's filename stem) unlinked -- expected, see "Unresolved uncertainty" |
| 4 | Manual render inspection (CMP) | same, `GET /doc/reports/RHACO-CMP-20260115-001_Fixture_Campaign.card.yaml` | "CMP lifecycle state" / "OPEN" shown; two outgoing "has campaign child" edges, one of them listing both the HND parent and its amendment (they share `doc_id`) comma-linked |
| 5 | Gate (a) ruff | `C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m ruff check explorer tools tests --output-format concise` | `All checks passed!` exit 0 |
| 6 | Gate (b) pytest (module) | `C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m pytest tests/reader -q` | `34 passed` exit 0 |
| 7 | Full-tree regression | `C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m pytest tests -q` | `116 passed` exit 0 (corpus_adapter + diagnostics + probe + reader together; this also surfaced and fixed the `test_reader.py` / `test_reader.py` basename collision with `tests/corpus_adapter/test_reader.py` -- renamed to `test_reader_page.py`, see Decisions) |
| 8 | Gate (c) L1 index-write check | `C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe tools/l1_index_write_check.py` | `hits=6 allowlisted=6 defects=0 verdict=PASS` exit 0 (all 6 hits inside `fixtures/build_fixture_index.py`, unrelated to this round's changes) |
| 9 | Git cleanliness | `git status --short` before and after commit | only `explorer/reader/**` and `tests/reader/**` staged; clean after commit |

Every "tested" claim above names the test or command that produced it.

### What each of the 34 tests covers, by file

- `test_reader_page.py` (13 tests): two-landmark page shape and `data-body-sha256`
  matching the fixture file's real sha256; heading slug ids and `data-line`
  with no false verification failures on the clean fixture; empty
  `data-card-index-mismatch` on the clean fixture; `?line=15` hits the "quartz
  lattice lantern" line and sets `data-jump-line="15"`; `?line=9999` renders
  "line 9999 not found (document has 21 lines)" with an empty `data-jump-line`;
  the amendment page shows "amendment of" linking to the parent, and the
  parent shows "amended by"; the HND page shows "campaign child of" linking to
  the CMP and the literal unresolved cites target marked "unresolved"; the
  v1_0 reference page shows the superseded banner linking to v1_1's card_ref
  and the text "frozen"; v1_1 has no such banner; the CMP page shows "CMP
  lifecycle state" / OPEN and the ANL page shows neither lifecycle label; the
  `docs_archive` card_ref and a percent-encoded `..` traversal card_ref both
  404; a direct `build_view` call also rejects a literal `..`-segment
  `card_ref` and an unknown one.
- `test_api.py` (4 tests): the JSON twin's `document.sha256` matches the page's
  `data-body-sha256` and an independently-computed sha256 of the fixture file
  on disk; `document.lines[14].text` equals the quartz line verbatim and
  `line_count == len(lines) == 21`; every heading in the clean fixture has
  `line_verified: true`; `index_mismatch_fields == []`; the `?line=15` API
  response marks exactly one line `is_hit: true`; an unknown card_ref returns
  404 with `{"error": "card not found"}` on the API.
- `test_faults.py` (3 tests): `stale_card` -> `data-card-index-mismatch="title,status"`,
  the "index row differs from card file: title, status" notice, and the
  mutated `"[STALE]"` title visible in the "as indexed" section (never in the
  card-file-sourced Identity section, which still shows the real title --
  proving the two sections stay distinct, S1); `broken_jump` -> at least one
  `data-line-verified="false"` heading and a non-empty anchor-mismatch notice,
  on both the page and the API twin.
- `test_adapter_absent.py` (2 tests): `explorer.app.ADAPTER_ABSENT` sentinel ->
  503 with "corpus_adapter not built" on both the page and the API
  (`{"error": "corpus_adapter not built"}`).
- `test_live_smoke.py` (1 test): `GET /doc/` for this build's own dispatch hand
  against the live index (`Settings()` defaults) returns 200 with
  `data-selected-doc-id="RHACO-HND-20260903-001"` and an "amended by" link,
  inside the session-scoped `corpus_cards_sha` + mtime guard (conftest.py).
- `test_service_unit.py` (11 tests): direct, adapter-free unit tests of the
  pure helpers -- `_verify_heading_line` (match / out-of-range / text
  mismatch), `_index_mismatch` (partial and full agreement), `_render_markdown`
  (id/data-line injection, `data-line-verified="false"` injection, and that
  `table` + `strikethrough` render correctly -- neither construct exists in
  the fixture corpus), `_lifecycle_label` (CMP / non-CMP / absent), and
  `_parse_card_yaml` (invalid YAML and a non-mapping document). These exercise
  states the fixture corpus cannot produce (no fixture document uses a table,
  strikethrough, or malformed YAML) without fabricating adapter behaviour --
  the dispatch's conventions block restricts a *hand-written fake adapter* to
  "vector channel unavailable; adapter absent" only, and the reader never
  calls `vector_availability()`, so no fake adapter was written at all; every
  adapter-backed state in this round runs against the real `CorpusAdapter`
  over the fixture or live index.

## Material alternatives

- **Heading anchor verification: re-derive vs. trust the adapter.** Considered
  trusting `DocumentText.headings` outright (the adapter already computes
  `line_no` and `slug`). Rejected: the task is explicit that a heading's
  `data-line` must be independently checked against the source line it claims
  (O23), and this is exactly what makes the `broken_jump` fault (line numbers
  off by +50) visible as `data-line-verified="false"` instead of the page
  silently trusting a wrong anchor. `_verify_heading_line` re-parses the same
  ATX shape the adapter's own `_headings()` uses, but as an independent check
  run in the reader's own code, against `doc.lines` (the same lines the
  fault-injected `read_document` returned) -- so it fails exactly when the
  claimed line no longer begins the claimed heading text, regardless of *why*
  it drifted.
- **Matching rendered heading tokens to `doc.headings`: by position vs. by an
  independent slug re-derivation.** The task specifies "matched ... by order
  and text". Implemented as a positional `zip(heading_token_indices,
  doc.headings)`: both the adapter's regex-based heading scan and
  markdown-it's own ATX heading rule skip fenced code and require the same
  `#{1,6}\s+...` shape, so in practice the two lists are the same length and
  order for every fixture document (verified: `test_render_markdown_injects_*`
  and every page-render check above). A from-scratch text-similarity matcher
  was considered and rejected as unneeded complexity for a case the two
  parsers already agree on structurally; documented as an assumption below
  rather than hidden.
- **Card panel field sourcing: the card FILE vs. the CardRow (index).**
  CONSTRAINTS.md S1's design consequence is explicit that "the card panel
  reads the .card.yaml from disk ... and shows index-derived fields as 'from
  index'". Read literally, this means the curated panel fields (title,
  doc_type, date, seq, status, lifecycle_state, programs, tags,
  project_knowledge, schema/naming versions, review fields, abstract,
  depends_on, see_also) are sourced from the parsed card FILE, with `doc_id`
  as the one field that only the index carries (O7) -- labelled "(from
  index)" in the template. A separate "Index row (as indexed)" section shows
  the CardRow's own values for the five compared fields side by side with the
  mismatch notice, so a stale index row is visible without ever contaminating
  the record-of-truth display. This is why `test_stale_card_fault_*` asserts
  the mutated `"[STALE]"` title appears only in the "as indexed" section, not
  in Identity's Title.
- **"Unknown keys are shown raw, never dropped" (item 1(a)): a curated
  unknown-field tracker vs. a full JSON dump.** Considered building an
  `unknown_fields` dict that diffs the parsed card against a hardcoded list of
  schema keys. Rejected in favour of a `<pre>{{ view.card_parsed |
  tojson(indent=2) }}</pre>` dump of the *entire* parsed structure inside a
  `<details>` ("Parsed card fields (complete)"): this trivially satisfies
  "never dropped" for every key at every nesting level (including a future
  schema field this round never anticipated) with no maintenance burden, and
  sits alongside the curated, human-labelled panel rather than instead of it.
- **`amends` edge resolution for "amendment of" / "amended by": `edges_for`'s
  `source_cards`/`target_cards` vs. the shared-`doc_id` sibling lookup.**
  `edges_for`'s `to_id`/`from_id` -> `cards_for_doc_id` resolution works for
  every relation except `amends`, whose `from_id` is the amendment's own
  *filename stem*, not a `doc_id` (O7/O8) -- `cards_for_doc_id(stem)` reliably
  returns nothing (confirmed empirically, evidence #3's generic-lineage-list
  observation). Because an amendment shares its parent's canonical `doc_id`
  by construction, `adapter.cards_for_doc_id(card.doc_id)` already returns
  both rows; filtering that list by `CardRow.is_amendment` gives a reliable
  "the other card(s) sharing this id" resolution for both directions without
  depending on the stem-vs-doc_id mismatch. The generic "Lineage (all typed
  edges)" list still shows the raw, unresolved `amends` edge exactly as
  `edges_for` returns it (see evidence #3) -- the two views are complementary,
  not contradictory: one is a reliable narrative, the other is the literal
  edge record.
- **Reader-owned stylesheet: a `<link>` inside `{% block content %}` vs.
  waiting for a `base.html` head hook.** `base.html` (web builder's module,
  wave 3, out of bounds to edit this round) has no style/head block, only
  `html_attrs`, `main_attrs`, `title`, `content`, `scripts`. ARCHITECTURE.md
  section 2 explicitly anticipates a reader-owned `static/reader.css` "served
  under /static/reader/ by the app factory" (already wired generically in
  `explorer/app.py`'s `MODULES` loop), so a per-module stylesheet is an
  intended pattern without a dedicated hook yet. Placed the `<link>` at the
  top of `{% block content %}` rather than skip the stylesheet or duplicate
  its rules as an inline `<style>`; verified served (200) and linked from the
  rendered page (evidence #2).
- **Test file naming: avoiding the `tests/corpus_adapter/test_reader.py`
  collision.** The natural name `tests/reader/test_reader.py` collided at
  full-tree collection time with `tests/corpus_adapter/test_reader.py` (no
  `__init__.py` package boundary separates same-basename test modules under
  pytest's default import mode -- "import file mismatch", caught by evidence
  #7, the full-tree regression run this round added beyond the two required
  gate commands). Renamed to `test_reader_page.py` rather than add
  `__init__.py` files across the tree (a package-boundary change with
  effects outside this round's owned paths) or touch the other module's test
  file (out of bounds, working rule 1).

## Decisions

- The view keeps three things visually and structurally distinct per S1: the
  card FILE (Identity/Abstract/Dependencies sections, sourced from
  `yaml.safe_load` of `read_card_text`), the INDEX ROW ("as indexed" section,
  sourced from the `CardRow` the adapter returned, with the five-field
  comparison and `data-card-index-mismatch`), and the DOCUMENT (the `Document`
  landmark, rendered from `read_document`'s bytes on disk, never the
  `fts_docs.body` copy the adapter never even exposes to this module).
- `status` and `lifecycle_state` are never joined into one control or cell
  (S4): the template renders them as two separate `<dt>/<dd>` pairs, and
  `_lifecycle_label` computes the label ("CMP lifecycle state" /
  "informational (non-CMP)" / absent) purely from `doc_type`, never from
  `status`.
- A frozen status is marked with the literal text "frozen" (`<span
  class="frozen">frozen</span>`, reusing `explorer/web/static/app.css`'s
  existing `.frozen` small-caps rule) next to the status value, never by
  colour alone.
- Every related-card link (`depends_on`/`see_also`, supersession/amendment,
  the generic lineage list) carries `data-doc-id`/`data-card-ref` on the
  anchor, matching ARCHITECTURE.md A19's project-wide DOM convention even
  though this round's specified test list does not name it -- the probe reads
  exactly these attribute names project-wide (section 4.8) and later waves
  should see them consistently from every module.
- `?line=N` for `N` outside `1..line_count` renders the exact text
  "line N not found (document has M lines)" and sets `data-jump-line=""` --
  never a silent top-of-page landing (O23's "explicit, never a silent
  landing" is applied to the jump path as well as the heading-anchor path).
- The `/lineage/<card_ref>` link is emitted unconditionally (the lineage
  module lands in wave 3); a request against it today 404s from the app
  factory's per-module route skip, which is the accepted state per the task
  ("the link may 404 until then -- do not build lineage here").
- `_parse_line` treats an unparsable or empty `line` query value as "no line
  requested" (returns `None`) rather than a 400 -- the task specifies the
  behaviour for `N` outside the valid range, not for a non-numeric value;
  falling back to "no jump" is the same posture diagnostics and search take
  toward malformed optional query parameters elsewhere in this build, and
  keeps every malformed input case a clean page render instead of a new error
  surface this task did not ask for.

## Result

**COMPLETE.** All three required gates pass with the exact specified commands
(evidence #5, #6, #8), plus a full-tree regression run (evidence #7, 116
passed) confirming no interference with `corpus_adapter`, `diagnostics`, or
`probe`'s own suites. All five deliverables are present: `service.py`'s
`build_view` and view dataclasses; the card panel content (item 2, verified
against the ANL/HND/CMP/amendment/v1_0 fixture pages, evidence #2-4); `routes.py`
with `register(app)` for both `GET /doc/{card_ref:path}` and `GET
/api/doc/{card_ref:path}`, including the 503/404 paths; the template with its
two landmarks, `#keyhelp`, and `<html data-mode="reader">`; and `tests/reader/`
covering every case item 5 enumerates by name (quartz-line jump and
out-of-range jump, the amendment/parent pair, the CMP campaign-child +
unresolved-cites HND page, the v1_0 superseded banner, the CMP/ANL lifecycle
contrast, the docs_archive and traversal 404s, the clean-fixture empty
mismatch, `stale_card` and `broken_jump` on both the page and the API, and the
live-index smoke guarded by the corpus_cards_sha + mtime check). Worktree left
clean after commit `8d963610b5cb5ae876d12bbd85ab9bdc2de4edac` (`git status
--short` empty).

## Unresolved uncertainty

- **The generic "Lineage (all typed edges)" list shows an unlinked, literal
  `amends` `from_id`** (the amendment's filename stem) on the parent card,
  because `cards_for_doc_id(stem)` cannot resolve a filename stem to a card
  row (O7) -- this is `edges_for`'s own return shape, rendered faithfully, not
  a bug in this round's code, but it means that one list entry is visibly
  less useful than the dedicated "amended by" narrative line two sections
  above it. Not fixed here because doing so would mean the reader inventing
  its own edge-identity resolution beyond what `adapter.edges_for` documents
  (ARCHITECTURE.md 4.1) -- a module-boundary question, not a reader-local one.
- **`.txt`-kind and binary-kind (`.docx`/`.pdf`/`.ipynb`) document rendering
  is exercised only at the `_build_document_view`/`DocumentView` code-path
  level via direct construction in `test_service_unit.py`-adjacent reasoning,
  not against a real carded fixture** -- the committed fixture corpus
  (owned by builder `probe`, out of this round's write scope) has no carded
  `.txt` document (`RHACO_Fixture_Loose_Notes.txt` is deliberately uncarded,
  per `docs/rounds/R01_probe.report.md`) and no binary-typed card at all. The
  code path (`doc.kind == "text"` -> preformatted; `doc.kind == "binary"` ->
  card + path + notice, `unsupported_binary` flag) follows the adapter's
  already-tested `read_document` kind detection (`tests/corpus_adapter/test_reader.py`
  covers markdown headings; kind detection itself is exercised by
  `tests/corpus_adapter` for the live corpus's own binary-suffix handling)
  and was read through by hand against the template, but UNVERIFIED by an
  end-to-end reader-module test against a real `.txt`-carded or binary-carded
  fixture document in this round.
- **The exact interaction between `wrong_doc_for_id`/`reverse_edges` faults
  and this module's card-panel rendering is UNVERIFIED** -- both faults are
  implemented module-agnostically inside the adapter (`_cards_for_doc_id`,
  `edges_for`) and this round's code renders whatever the adapter returns
  without special-casing either fault, but neither fault is in task B6 item
  5's enumerated test list and no test here exercises them (they are
  documented as lineage-module and identifier-mode qualification cases,
  ARCHITECTURE.md section 6).
- **Whether the probe's wave-2 W-series/KB-series runners will read this
  page's DOM the way this round assumes is UNVERIFIED from this worktree** --
  `tools/probe_corpus_explorer.py`'s reader-facing presets are stubs as of
  the round-1 probe report; this round followed ARCHITECTURE.md A19's
  attribute names (`data-mode`, `data-selected-doc-id`, `data-doc-id`,
  `data-card-ref`) and PROMPT.md 5.4's literal contract text, but the probe
  itself was not run against this build in this round (out of scope; D-12/D-3
  and the task's own gate list name only ruff/pytest/L1).

## Change requests

None. Every deliverable was buildable against the current, already-merged
contracts (`explorer/models.py`, `explorer/config.py`, `explorer/app.py`,
`explorer/faults.py`, `explorer/corpus_adapter/adapter.py`) with no change to
any file outside `explorer/reader/**` / `tests/reader/**`.

## Assumptions

- `zip(heading_token_indices, doc.headings, strict=False)` (positional
  matching between markdown-it's rendered heading tokens and the adapter's
  `doc.headings`) is safe because both derive headings via the same ATX shape
  and both skip fenced code -- true for every fixture and live document this
  round rendered, but not proven true in general for a document markdown-it's
  parser and the adapter's regex would disagree on (e.g. a heading-like line
  inside an HTML block, which the adapter's line-oriented regex does not
  special-case but CommonMark's HTML-block rule would suppress from being a
  heading). No such document was found in the fixture or the one live
  document rendered this round.
- KB1-KB5 <-> `explorer.faults.FAULTS` mapping is per `docs/rounds/R01_probe.report.md`'s
  Assumptions (`wrong_doc_for_id, stale_card, reverse_edges, broken_jump,
  console_error`); this round exercises `stale_card` (KB2) and `broken_jump`
  (KB4) directly, per task B6 item 5's enumerated list.
- "the fixture inventory is in docs/rounds/R01_probe.report.md" (dispatch
  read-first list) was read and its card_ref/line-number claims (line 15's
  "quartz lattice lantern", the amendment/parent doc_id sharing, the
  supersession pair, the unresolved cites target) were independently
  re-verified against the actual fixture files on disk in this round, not
  merely trusted from the report text.
- `Settings(db_path=..., docs_root=..., fault=...)` against the same fixture
  db path built once per test session (rather than a fresh fixture build per
  fault variant) is safe because `explorer.faults.active_fault` is evaluated
  once at `CorpusAdapter.__init__` from the `Settings.fault` value and the db
  path -- a fault never mutates the on-disk fixture db, only the adapter's
  in-memory `active_fault` value and its per-call behaviour, so three
  `CorpusAdapter` instances (clean, stale_card, broken_jump) can safely share
  one built fixture index within a test session.
