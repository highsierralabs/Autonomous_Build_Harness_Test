# docs/probe-qualification/ -- evidence output (builder probe; ARCHITECTURE.md section 2)

This directory holds evidence artifacts written by `tools/probe_corpus_explorer.py`.
It is the probe's owned evidence area (dispatch record working rule 1); nothing
here is hand-edited.

## Layout

```
docs/probe-qualification/
  README.md              -- this file
  runs/
    <utc stamp>/          -- one directory per probe invocation, named
                             YYYYMMDDTHHMMSSZ by default (--out overrides it)
      run_summary.json    -- always written; one row per preset (ok/kind/
                              http_status/route_absent/status) plus the
                              overall verdict (PASS/FAIL), the healthz body
                              recorded at readiness, and any run_error
      server.log          -- the child uvicorn process's stdout+stderr
      <preset>.json        -- one observation file per preset that ran
                              (url, viewport, http_status, title, active
                              retrieval mode, selected document id, observed
                              result ids, console errors, failed requests,
                              timings, screenshot path, ok)
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
  `data-mode` / `data-selected-doc-id` / `data-doc-id` extraction, console
  errors, failed requests, screenshot, timings). This round: `diagnostics`
  (its route is expected to 404 until the diagnostics module merges into
  `main` -- recorded as `route_absent: true`, `ok: true`; a 404 is an
  accepted, documented state here, never a probe failure).
- **`not_implemented`** -- a clean stub that reports
  `{"status": "not_implemented_yet", "ok": true}` without touching the
  server. This round: the ten acceptance workflows `W1`-`W10` (PROMPT.md
  section 8) and the qualification cases `KG` / `KB1`-`KB5` (one per
  `RHACO_EXPLORER_FAULT` value in `explorer/faults.FAULTS`, same order:
  KB1=wrong_doc_for_id, KB2=stale_card, KB3=reverse_edges, KB4=broken_jump,
  KB5=console_error). Wave 2, once catalog/search/reader/lineage exist to
  drive, replaces these stubs with real runners.

## Template attribute conventions the probe reads

Page-kind presets extract three things from the DOM, by convention, since no
template exists yet to originate them:

| Observation | DOM read |
|---|---|
| active retrieval mode | `document.documentElement.getAttribute('data-mode')` |
| selected document id | the first `[data-selected-doc-id]` element's attribute |
| observed result ids | every `[data-doc-id]` element's attribute, in DOM order |

Later builders (catalog/search/reader/lineage) should emit these attributes
on their templates' root/result elements so the probe can observe them
without reading page source; see `docs/rounds/R01_probe.report.md`
("Change requests" / "Assumptions") for the same note filed as a convention
proposal to the integrator.

## Fixture substrate

Every run here is expected to point `--db`/`--docs-root` at a fixture index
built by `fixtures/build_fixture_index.py` from `fixtures/corpus/` -- never
at the live `C:\RHACO\index\corpus_index.db`. `fixtures/fixture_index.db` is
gitignored (`fixtures/*.db`) and rebuilt on demand; it is not evidence and is
never committed. See `docs/rounds/R01_probe.report.md` for the fixture
inventory table (file, id, purpose, known facts).
