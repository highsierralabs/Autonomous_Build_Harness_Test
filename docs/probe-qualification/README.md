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
      <preset>.json        -- one observation file per preset that ran
                              (url, viewport, http_status, title, active
                              retrieval mode, vector state, selected document
                              id, observed result ids, console errors, page
                              errors, failed requests, timings, screenshot
                              path, verdict, reasons, fault_detected,
                              fault_class, ok)
      <preset>.png         -- full-page screenshot, for "page"-kind presets
                              only (a "json_endpoint" preset like healthz has
                              no page to screenshot; a "not_implemented" stub
                              writes no files under runs/ at all beyond its
                              own <preset>.json)
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
- **`not_implemented`** -- a clean stub that reports
  `{"status": "not_implemented_yet", "ok": true}` without touching the
  server. This round: the ten acceptance workflows `W1`-`W10` (PROMPT.md
  section 8) and the qualification cases `KG` / `KB1`-`KB5` (one per
  `RHACO_EXPLORER_FAULT` value in `explorer/faults.FAULTS`, same order:
  KB1=wrong_doc_for_id, KB2=stale_card, KB3=reverse_edges, KB4=broken_jump,
  KB5=console_error). A run that selects any of these is `INCOMPLETE`
  (never a PASS of any kind, task C1 item 2). Wave 2, once catalog/search/
  reader/lineage exist to drive, replaces these stubs with real runners.

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
`FAULT_TEXT_MARKERS` (next to `PRESET_REGISTRY` in the module): this round,
only KB5 has a rule (its text is `CONSOLE_ERROR_FAULT_TEXT`, the exact string
above). `FAULT_CLASS_TABLE` maps `KB1..KB5` onto `explorer.faults.FAULTS`
(`wrong_doc_for_id, stale_card, reverse_edges, broken_jump, console_error`);
wave 2 adds KB1-KB4's attribution rules to `FAULT_TEXT_MARKERS` without
restructuring `evaluate_page` or the registry.

## The qualification-state vocabulary (Director ruling AC-3; task C1 item 2)

Every run records, in `run_summary.json`: `run_kind` (`"qualification"` when
`--fault` was given; else `"product"` when the resolved `--db` path lies
under a RHACO tree, i.e. `explorer.faults.is_under_rhaco_tree`; else
`"smoke"`), `qualification_state` (one of the five states below),
`product_evidence_eligible` (bool), `qualified_failure_classes` (KB names),
`incomplete_presets`, and `product_evidence_blocked_by`.

- **`INCOMPLETE`** -- any selected preset still reports `not_implemented_yet`
  (a run with stubs is never a PASS of any kind, regardless of run_kind).
- **`QUALIFICATION_PASS`** (qualification runs only) -- every page-kind
  preset the injected fault touches (for `console_error`: every page-kind
  preset run, per the dispatch) reported `FAIL` with `fault_detected=true`
  and `fault_class` equal to the injected fault's class, and every other
  selected preset passed. `qualified_failure_classes` becomes `[that
  class]`; the class (and the run) is appended to
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
  console/network/page-error capture, the observed-fault predicate). **This
  round.**
- **Q1** -- search surfaces (KB1, KB2, known-good exact-id and lexical
  phrase). Wave 2.
- **Q2** -- reader (KB4, known-good body-and-card-match). Wave 2.
- **Q3** -- lineage (KB3, known-good typed edge direction). Wave 3.
- **FINAL** -- the complete known-good + known-bad suite before the critic's
  first round.

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

Page-kind presets extract these from the DOM, by convention:

| Observation | DOM read |
|---|---|
| active retrieval mode | `document.documentElement.getAttribute('data-mode')` |
| vector availability | `document.documentElement.getAttribute('data-vector')` |
| selected document id | the first `[data-selected-doc-id]` element's attribute |
| observed result ids | every `[data-doc-id]` element's attribute, in DOM order |

`explorer/diagnostics/templates/diagnostics/diagnostics.html` originates
`data-mode`/`data-vector` on both `<html>` (`{% block html_attrs %}`) and a
wrapper `<div>`, per ARCHITECTURE.md A19; later builders (catalog/search/
reader/lineage) should emit the same three attributes on their templates'
root/result elements so the probe can observe them without reading page
source; see `docs/rounds/R01_probe.report.md` ("Change requests" /
"Assumptions") for the same note filed as a convention proposal to the
integrator.

## Fixture substrate

Every run here is expected to point `--db`/`--docs-root` at a fixture index
built by `fixtures/build_fixture_index.py` from `fixtures/corpus/` -- never
at the live `C:\RHACO\index\corpus_index.db`. `fixtures/fixture_index.db` is
gitignored (`fixtures/*.db`) and rebuilt on demand; it is not evidence and is
never committed. See `docs/rounds/R01_probe.report.md` for the fixture
inventory table (file, id, purpose, known facts).
