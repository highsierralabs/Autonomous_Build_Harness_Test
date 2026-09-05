# docs/probe-qualification/ -- evidence output (builder probe; ARCHITECTURE.md section 2)

This directory holds evidence artifacts written by `tools/probe_corpus_explorer.py`.
It is the probe's owned evidence area (dispatch record working rule 1); nothing
here is hand-edited, with the one exception of `qualification_ledger.json`, which
the probe itself appends to (idempotently) on a QUALIFICATION_PASS run.

## Layout

```
docs/probe-qualification/
  README.md                     -- this file
  qualification_ledger.json     -- the qualification ledger (task C1 item 2): which
                                    KB failure classes have a recorded QUALIFICATION_PASS,
                                    and from which run. The only file the probe writes
                                    outside its own --out directory. Committed evidence;
                                    a product run reads it and never writes it.
  runs/
    <utc stamp>/          -- one directory per probe invocation, named
                             YYYYMMDDTHHMMSSZ by default (--out overrides it)
      run_summary.json    -- always written; one row per preset (ok/kind/
                              http_status/route_absent/status/verdict/reasons/
                              fault_detected/fault_class) plus run_kind, the
                              AC-3 qualification_state and its supporting
                              fields (product_evidence_eligible,
                              qualified_failure_classes, incomplete_presets,
                              product_evidence_blocked_by, reasons), the
                              overall verdict (PASS/FAIL/INCOMPLETE), the
                              healthz body recorded at readiness, the ledger
                              path used, and any run_error
      server.log          -- the child uvicorn process's stdout+stderr
      <preset>.json        -- one observation file per preset that ran. A
                              "page"-kind preset (url, viewport, http_status,
                              title, active retrieval mode, vector state,
                              selected document id, observed result ids,
                              console errors, page errors, failed requests,
                              timings, screenshot path, verdict, reasons,
                              fault_detected, fault_class, ok). A
                              "workflow"-kind preset (task B7 -- KG, KB1,
                              KB2, KB4, KB5, W1-W4, W7-W10): `steps` (one
                              entry per named navigation, each with its own
                              url/http_status/error/title/timings),
                              `requests_total`, `console_errors`,
                              `failed_requests`, `page_errors` (accumulated
                              across every step, each tagged with the step
                              active when captured), `observations` (the
                              preset's own named findings -- e.g. KG's
                              `identifier_first_doc_id`, W3's `returned_ids`
                              vs `oracle_order`), `screenshot` (the final
                              step's page), `verdict`, `reasons`,
                              `fault_detected`, `fault_class`, `ok`, and
                              (W3 only, when applicable) `incomplete: true`.
      <preset>.png         -- full-page screenshot (final step, for a
                              "workflow" preset), for "page"/"workflow"-kind
                              presets only (a "json_endpoint" preset like
                              healthz has no page to screenshot; a
                              "not_implemented" stub writes no files under
                              runs/ at all beyond its own <preset>.json)
      W8_server.log         -- W8 only: its OWN dedicated uvicorn child's
                              stdout+stderr (W8 builds a temp fixture copy,
                              adds one more card+document without
                              rebuilding, and drives a SECOND server against
                              it -- the run's main --db/--docs-root, and
                              this directory's plain server.log, are unused
                              by this one preset)
```

## What each preset kind means

`tools/probe_corpus_explorer.py`'s `PRESET_REGISTRY` classifies every preset
by `kind`:

- **`json_endpoint`** -- a plain HTTP GET + JSON assertion, no browser. This
  round: `healthz` (status must equal `"ok"`).
- **`page`** -- a Playwright navigation with the full observation set (DOM
  `data-mode` / `data-vector` / `data-selected-doc-id` / `data-doc-id`
  extraction, console errors, page errors, failed requests, screenshot,
  timings), scored by the observed-fault predicate `evaluate_page()` (task
  C1 item 1). This round: `diagnostics` -- now that the diagnostics module
  is merged, its route must return HTTP 200 with `data-mode` in
  `{hybrid, hybrid-degraded-lexical}`, `data-vector` in
  `{available, unavailable}`, and a non-empty title; a 404 ("route absent")
  is **no longer an accepted state** (round 1's tolerance for it is gone).
- **`workflow`** (task B7, round 2) -- a `Session` (one Playwright browser
  context + page, reused across a short, named sequence of navigation
  "steps" -- `tools/probe_corpus_explorer.py`'s `Session` class) drives the
  merged catalog / search / reader / diagnostics surfaces, cross-checks the
  `/api` twin, and (where the dispatch specifies) reads the fixture or
  production docs root directly from disk for an independent comparison
  (sha256, verbatim line content, YAML parsing) -- never through the index,
  only through the server this file launches. `WORKFLOW_RUNNERS` maps each
  such preset name to its runner function. This round: `KG`, `KB1`, `KB2`,
  `KB4`, `KB5` (fixture only) and `W1`, `W2`, `W3`, `W4`, `W7`, `W8`, `W9`,
  `W10` (production, except `W8` which builds and drives its own dedicated
  temp-fixture server -- see "Which presets are real" below).
- **`not_implemented`** -- a clean stub that reports
  `{"status": "not_implemented_yet", "ok": true}` without touching the
  server. After round 2 (task B7), only `W5`, `W6`, and `KB3` remain --
  lineage (`reverse_edges` / typed-edge direction) is wave 3 (Q3). A run
  that selects any of these three is `INCOMPLETE` (never a PASS of any
  kind, task C1 item 2).

## The observed-fault predicate (task C1 item 1)

Round 1's page-preset pass criterion was `ok = error is None` -- it could not
distinguish a known-good page from a known-bad one (see
`runs/20260904T033047Z/diagnostics.json`: `http_status 404`, one console
error, one failed request, `ok: true`). `evaluate_page(observation, spec) ->
Verdict` (`tools/probe_corpus_explorer.py`) replaces it. A page preset FAILs
if any of: (a) a navigation/extraction error; (b) `http_status >= 400` unless
`spec.expected_status` matches it; (c) any console error (a `pageerror` --
see below -- is mirrored into `console_errors` so this one rule covers both);
(d) any failed request (`requestfailed`, or a response `>= 400`); (e) a
declared assertion on the spec's `data_mode_in` / `data_vector_in` /
`require_title` fails, named in `reasons`. `ok` in the preset JSON stays a
boolean mirror of `verdict` so existing readers (e.g.
`explorer/diagnostics/service.py`'s `_find_last_probe_run`, which reads
`run_summary.json` as an opaque JSON object) keep working unchanged.

**Empirical finding (task C1 item 1):** the diagnostics fault template's
`<script>throw new Error("RHACO_EXPLORER_FAULT console_error")</script>`
(`explorer/diagnostics/templates/diagnostics/diagnostics.html`) does **not**
arrive on Playwright's `console` event (that event only fires for explicit
`console.*` calls -- CDP `Runtime.consoleAPICalled`). It arrives only on
`pageerror` (CDP `Runtime.exceptionThrown`). Verified by running
`--preset diagnostics --fault console_error` against the fixture and
inspecting the resulting `diagnostics.json`: `console_errors` is empty until
the probe's own `pageerror` listener fires and `run_page_preset` mirrors its
message into `console_errors` with `"type": "pageerror"`; `page_errors`
carries the one captured message directly. The probe therefore registers
both a `console` listener and a `pageerror` listener.

A FAIL is additionally attributed to a known-bad class when its text matches
`FAULT_TEXT_MARKERS` (next to `PRESET_REGISTRY` in the module): `KB5`'s rule
(its text is `CONSOLE_ERROR_FAULT_TEXT`, the exact string above) is the only
one that works this way -- a substring match against a console/page-error
message. `FAULT_CLASS_TABLE` maps `KB1..KB5` onto `explorer.faults.FAULTS`
(`wrong_doc_for_id, stale_card, reverse_edges, broken_jump, console_error`).

**KB1, KB2, KB4's attribution rules (task B7) are not text markers** -- each
fault's observable signature has no console/page error at all, so each gets
its own pure, dependency-free predicate (`tools/probe_corpus_explorer.py`,
unit-tested in `tests/probe/test_workflow_verdicts.py`) fed by its
`kind="workflow"` runner's own DOM/`/api` observations:

- `_kb1_verdict(observed_first_card_ref, expected_correct_ref,
  expected_fault_ref)` -- `wrong_doc_for_id`: an identifier search for a
  multi-card-row id must list that id's OWN card first; the fault rotates
  the row order by one. The SAME predicate doubles as the clean-match sanity
  check when no fault is active (a match to `expected_correct_ref` is a
  quiet PASS), so KB1's runner is safe to include in an ordinary smoke run.
- `_kb2_verdict(mismatch_attr, file_title, file_status, indexed_title,
  indexed_status)` -- `stale_card`: FAIL/KB2 when EITHER the reader's own
  `data-card-index-mismatch` marker is set OR the probe's independent
  title/status comparison (the card file, parsed by the probe itself from
  disk, vs. the index row the `/api/doc` twin reports) disagrees.
- `_kb4_verdict(page_any_unverified, independent_mismatch_count)` --
  `broken_jump`: FAIL/KB4 when EITHER the reader's TOC shows a
  `data-line-verified="false"` heading OR the probe's own independent
  re-check (`_verify_heading_independently`: `lines[line_no-1]` must begin
  an ATX heading marker matching the heading's text -- re-implemented here,
  never imported from `explorer.reader.service`) finds a mismatch.

`KB5`'s real runner (a `kind="workflow"` preset, not `kind="page"`) visits
diagnostics AND catalog/search/reader in one composite run, demonstrating
the fault on a wave-2 surface: only the diagnostics step's own
`_attribute_fault_class` match sets `fault_detected`/`fault_class`, while
the other three steps are expected to stay clean (no console error of their
own) -- proving the round-1 rule ("every page-kind preset run" touches
`console_error`) still holds precisely where it is true (diagnostics) and
does not accidentally also require catalog/search/reader to fail.
`_touched_presets` (next to `derive_qualification`) unions two rules so
neither invocation shape regresses the other: the legacy "every kind=page
preset, for `console_error`" rule (kept for `--preset diagnostics --fault
console_error`, still exercised by the C1 tests) and the round-2 rule
(any selected preset whose own `PresetSpec.fault` equals the requested
fault -- how `KB1`/`KB2`/`KB4`/`KB5` are matched regardless of `kind`).

## The qualification-state vocabulary (Director ruling AC-3; task C1 item 2)

Every run records, in `run_summary.json`: `run_kind` (`"qualification"` when
`--fault` was given; else `"product"` when the resolved `--db` path lies
under a RHACO tree, i.e. `explorer.faults.is_under_rhaco_tree`; else
`"smoke"`), `qualification_state` (one of the five states below),
`product_evidence_eligible` (bool), `qualified_failure_classes` (KB names),
`incomplete_presets`, and `product_evidence_blocked_by`.

- **`INCOMPLETE`** -- any selected preset still reports `not_implemented_yet`
  (a run with stubs is never a PASS of any kind, regardless of run_kind) --
  **or** (task B7) a `workflow`-kind preset self-reports `"incomplete":
  true` in its own JSON (currently only `W3`, when the vector channel is
  unavailable on this host at run time: the dispatch's own "recorded as
  INCOMPLETE for W3, not FAIL" rule, folded into this same run-level state
  rather than a sixth vocabulary value).
- **`QUALIFICATION_PASS`** (qualification runs only) -- every preset
  `_touched_presets(results, fault)` names (see above) reported `FAIL` with
  `fault_detected=true` and `fault_class` equal to the injected fault's
  class, and every other selected preset passed. `qualified_failure_classes`
  becomes `[that class]`; the class (and the run) is appended to
  `qualification_ledger.json`. Otherwise the run is `FAIL` -- the probe did
  not detect a known-bad.
- **`FRAMEWORK_SMOKE_PASS`** -- a fixture-db run with no fault, every preset
  passed (mechanism evidence only: server lifecycle, extraction, the
  predicate itself -- not a qualification, not product evidence). Also the
  outcome of an otherwise-clean **product** run whose presets are not yet
  covered by the ledger (see below).
- **`PRODUCT_EVIDENCE_PASS`** (product runs only) -- every preset passed
  **and** every selected preset's `required_classes` (the per-preset table
  below) are all present in the qualification ledger. If every preset
  passed but coverage is missing, the run is `FRAMEWORK_SMOKE_PASS` instead,
  with `product_evidence_eligible=false` and the uncovered presets listed
  under `product_evidence_blocked_by`.
- **`FAIL`** -- any selected preset failed (any run_kind), or (qualification
  runs) the fault was not detected as required above.

Exit code: 0 for `FRAMEWORK_SMOKE_PASS` / `QUALIFICATION_PASS` /
`PRODUCT_EVIDENCE_PASS`; 1 for `FAIL`; 3 for `INCOMPLETE`. `verdict` in
`run_summary.json` mirrors this as `"PASS"` / `"FAIL"` / `"INCOMPLETE"` (the
healthz-only smoke test's `verdict == "PASS"` expectation is unaffected).

### Per-preset required failure classes (`required_classes`)

The classes a preset's `PRODUCT_EVIDENCE_PASS` requires the ledger to already
cover (`PRESET_REGISTRY[name].required_classes` in
`tools/probe_corpus_explorer.py`):

| Preset | required_classes |
|---|---|
| healthz | (none) |
| diagnostics | KB5 |
| W1 | KB1, KB5 |
| W2 | KB1, KB2, KB5 |
| W3 | KB1, KB5 |
| W4 | KB2, KB5 |
| W5 | KB3, KB5 |
| W6 | KB3, KB5 |
| W7 | KB5 |
| W8 | KB2, KB5 |
| W9 | KB4, KB5 |
| W10 | KB1, KB2, KB4, KB5 |
| KG, KB1-KB5 | (none -- they are qualification cases themselves) |

### Qualification waves (AC-3 reading)

- **Q0** -- probe mechanism (server lifecycle, screenshot, DOM capture,
  console/network/page-error capture, the observed-fault predicate). Round 1
  / C1.
- **Q1** -- search surfaces (KB1, KB2, known-good exact-id and lexical
  phrase). **Done this round (task B7)**: `KG`'s identifier/lexical checks
  and `KB1`/`KB2`'s runners are real and QUALIFICATION_PASS against the
  fixture (see `docs/rounds/R02_probe.report.md` Evidence).
- **Q2** -- reader (KB4, known-good body-and-card-match). **Done this round
  (task B7)**: `KG`'s reader check and `KB4`'s runner are real and
  QUALIFICATION_PASS against the fixture.
- **Q3** -- lineage (KB3, known-good typed edge direction). Wave 3 -- `W5`,
  `W6`, and `KB3` remain `not_implemented_yet`.
- **FINAL** -- the complete known-good + known-bad suite before the critic's
  first round.

### Which presets are real (task B7)

| Preset | Status | Substrate |
|---|---|---|
| healthz | real (round 1) | either |
| diagnostics | real (round 1/C1) | either |
| KG | real (task B7) | fixture only |
| KB1 | real (task B7) | fixture only (`--fault wrong_doc_for_id`) |
| KB2 | real (task B7) | fixture only (`--fault stale_card`) |
| KB3 | `not_implemented_yet` | -- lineage, wave 3 (Q3) |
| KB4 | real (task B7) | fixture only (`--fault broken_jump`) |
| KB5 | real (task B7) | fixture only (`--fault console_error`) |
| W1 | real (task B7) | production |
| W2 | real (task B7) | production |
| W3 | real (task B7) | production (INCOMPLETE, not FAIL, if the vector channel is unavailable) |
| W4 | real (task B7) | production |
| W5 | `not_implemented_yet` | -- lineage, wave 3 (Q3) |
| W6 | `not_implemented_yet` | -- lineage, wave 3 (Q3) |
| W7 | real (task B7) | production (`--disable-vec`) |
| W8 | real (task B7) | fixture only -- builds and drives its OWN dedicated temp-fixture server (see below); the run's main `--db`/`--docs-root` is unused by this preset |
| W9 | real (task B7) | production |
| W10 | real (task B7) | production |

### Historical runs predate this vocabulary

`runs/20260904T033047Z/` and `runs/20260904T034711Z/` were written by the
round-1 probe, before `evaluate_page`, the qualification-state vocabulary,
and the ledger existed (their `run_summary.json` has no `qualification_state`
key at all, and round 1's `diagnostics` preset treated a 404 as an accepted
`route_absent` state rather than a failure). The integrator classifies both
as **`FRAMEWORK_SMOKE_PASS`** retroactively -- mechanism evidence only, never
qualification, never product evidence -- and they are left unedited as
historical record (dispatch record working rule 1; not reclassified in
place, only in `build_state.json`).

### The qualification ledger

`qualification_ledger.json`: `{"classes": {"<KBn>": {"run": "<run dir path
relative to the workspace root>", "recorded_utc": "..."}}, "runs":
[{"run": "...", "qualification_state": "...", "classes": [...]}]}`. Writes
are idempotent (re-running the same `--out` never duplicates a `runs` entry)
and ASCII. `--ledger PATH` overrides the default (`<workspace root>/docs/
probe-qualification/qualification_ledger.json`, resolved from the probe
file's own location so a worktree run writes the worktree's ledger); tests
always pass a tmp path so the committed ledger is never touched by a test
run.

## Template attribute conventions the probe reads

`evaluate_page` (page-kind presets: healthz's sibling `diagnostics`) reads:

| Observation | DOM read |
|---|---|
| active retrieval mode | `document.documentElement.getAttribute('data-mode')` |
| vector availability | `document.documentElement.getAttribute('data-vector')` |
| selected document id | the first `[data-selected-doc-id]` element's attribute |
| observed result ids | every `[data-doc-id]` element's attribute, in DOM order |

`explorer/diagnostics/templates/diagnostics/diagnostics.html` originates
`data-mode`/`data-vector` on both `<html>` (`{% block html_attrs %}`) and a
wrapper `<div>`, per ARCHITECTURE.md A19; catalog/search/reader (wave 2)
follow the same convention on their own templates' root/result elements.

The wave-2 `workflow`-kind runners (task B7, `Session.attr`/`.attr_all`/
`.count`/`.text`/`.html_attr` in `tools/probe_corpus_explorer.py`) additionally
read, by the same convention -- one attribute contract per surface, never
scraped page text where a `data-*` attribute or the `/api` twin already
carries the value:

| Observation | DOM read | Surface |
|---|---|---|
| catalog row id / card ref / status / lifecycle | `data-doc-id` / `data-card-ref` / `data-status` / `data-lifecycle-state` on each result `<tr>` | catalog |
| lifecycle filter control shown | `[data-lifecycle-control="shown"]` present | catalog |
| identifier result row id | `.identifier-results > li`'s `data-doc-id` | search |
| identifier/lexical result card ref | `.result-card`'s `data-card-ref` (nested inside a result row) | search |
| lexical/hybrid/graph result id + rank | `.search-results > li`'s `data-doc-id` / `data-rank` | search |
| active mode badge | `.mode-badge`'s `data-mode-effective` | search |
| narrowing counts | `[data-narrowed-from]` / `data-narrowed-to` | search |
| document identity / body hash / jump line | `#document`'s `data-selected-doc-id` / `data-card-ref` / `data-body-sha256` / `data-jump-line` | reader |
| card/index mismatch | `#card-panel`'s `data-card-index-mismatch` (comma-joined field names, `""` when clean) | reader |
| heading line-anchor verification | `.toc li`'s `data-line` / `data-line-verified` | reader |
| source line hit marker | `#L<n>.hit .line-text` | reader |
| freshness result | `[data-freshness-status]` | diagnostics |

See `docs/rounds/R01_probe.report.md` ("Change requests" / "Assumptions")
for the original convention proposal filed to the integrator.

## Fixture substrate

Every run here is expected to point `--db`/`--docs-root` at a fixture index
built by `fixtures/build_fixture_index.py` from `fixtures/corpus/` -- never
at the live `C:\RHACO\index\corpus_index.db`. `fixtures/fixture_index.db` is
gitignored (`fixtures/*.db`) and rebuilt on demand; it is not evidence and is
never committed. See `docs/rounds/R01_probe.report.md` for the fixture
inventory table (file, id, purpose, known facts).
