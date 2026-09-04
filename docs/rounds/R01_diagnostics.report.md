# R01 -- diagnostics (task B3)

## Header

- Strand: B3, role module builder (diagnostics), tier mid, model Claude Sonnet 5
  (`claude-sonnet-5`), pattern #3 worktree-isolated builder, wave 1 (concurrent with
  `corpus_adapter` and `probe`).
- Worktree: `C:\highsierralabs\RHACO_Corpus_Explorer\.worktrees\diagnostics`, branch
  `build/diagnostics`, base commit `4987cca1b6e4b771a00697e7cd65f948c3d6ec56`.
- Interpreter: `C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe`
  (Python 3.13.9).
- t_start (closeout phase; see Deviations) 2026-09-04T03:19:47Z UTC.
  t_end: see StructuredOutput `t_end_utc`.
- Head commit at close: `caf09a02...` (`git rev-parse HEAD`, pasted in Evidence).

## Change

Added `explorer/diagnostics/` (the instrument-state page, PROMPT.md 5.6) and its
tests, entirely inside the owned paths (`explorer/diagnostics/**`,
`tests/diagnostics/**`, this report). No file outside those paths was touched.

New files:

- `explorer/diagnostics/__init__.py` -- module docstring only.
- `explorer/diagnostics/service.py` -- `DiagnosticsView`, `RerankStanding`
  dataclasses and `build_view(adapter, settings, *, freshness=None)`.
- `explorer/diagnostics/routes.py` -- `register(app)`: `GET /diagnostics`,
  `POST /diagnostics/freshness`, `GET /api/diagnostics`.
- `explorer/diagnostics/templates/diagnostics/diagnostics.html` -- extends
  `base.html`.
- `tests/diagnostics/__init__.py`, `fake_adapter.py`, `test_service.py`,
  `test_routes.py` -- 25 tests, all via `TestClient` / direct `build_view` calls,
  no server process, no real adapter, no real database.

## Evidence

Checks actually run, exact commands and output tails (also reproduced by the
StructuredOutput `gates` block):

```
$ C:/highsierralabs/RHACO_Corpus_Explorer/.venv/Scripts/python.exe -m ruff check explorer tools tests --output-format concise
All checks passed!

$ C:/highsierralabs/RHACO_Corpus_Explorer/.venv/Scripts/python.exe -m pytest tests/diagnostics -q
.........................                                                [100%]
25 passed, 2 warnings in 0.74s
(warnings are pre-existing StarletteDeprecationWarning/DeprecationWarning from the
fastapi/starlette install itself, unrelated to this module's code)

$ C:/highsierralabs/RHACO_Corpus_Explorer/.venv/Scripts/python.exe tools/l1_index_write_check.py
l1-index-write-check: hits=0 allowlisted=0 defects=0 verdict=PASS
```

Test-by-test claims (all in `tests/diagnostics/test_service.py` and
`test_routes.py`, run above):

- Default mode is `"hybrid"` and matches effective mode when the vector channel is
  available -- `test_default_mode_is_hybrid_and_matches_effective_when_vector_available`.
- Effective mode degrades to `"hybrid-degraded-lexical"` and the degradation text is
  exactly `"Hybrid unavailable: using lexical retrieval. Result ordering is
  lexical-only."` when the vector channel is unavailable --
  `test_effective_mode_degrades_when_vector_unavailable`,
  `test_diagnostics_page_degraded_vector_shows_exact_text_and_data_mode`,
  `test_api_diagnostics_degraded_matches_page_text`.
- `index_meta` (every key/value, live counts), `db_path`, and the
  `non_authoritative_notice` are carried through from the adapter unchanged --
  `test_index_meta_and_db_path_carried_through`.
- `exclusion_sets()` is passed through verbatim --
  `test_exclusion_sets_passed_through_from_adapter`.
- Rerank standing text is the fixed string from the dispatch, word for word --
  `test_rerank_standing_text_is_fixed`.
- Last probe run resolves to the literal `"none recorded"` when
  `docs/probe-qualification/runs/` does not exist (true in this worktree; wave 3
  builds the probe) -- `test_last_probe_run_none_recorded_when_no_runs_directory`;
  confirmed independently by direct invocation (see below).
- `freshness` is `None` unless explicitly supplied to `build_view` --
  `test_freshness_is_none_by_default`,
  `test_api_diagnostics_ok_returns_same_keys_as_page` (`data["freshness"] is None`).
- POST `/diagnostics/freshness` renders `FRESH` (`test_post_freshness_renders_fresh`)
  and `DRIFT` with populated `added`/`removed`/`sha_changed`
  (`test_post_freshness_renders_drift`) from two distinct fakes.
- Adapter-absent: `GET /diagnostics` returns 503 with a visible notice
  (`test_diagnostics_page_adapter_absent_shows_notice`); `GET /api/diagnostics`
  returns 503 with body `{"error": "corpus_adapter not built"}`
  (`test_api_diagnostics_adapter_absent_returns_503_with_error_body`); POST
  `/diagnostics/freshness` likewise (`test_post_freshness_adapter_absent`).
- `active_fault == "console_error"` -> the exact throw script is present
  (`test_diagnostics_page_console_error_fault_present`); absent otherwise
  (`test_diagnostics_page_no_fault_script_absent`).
- The hidden `#keyhelp` element is present (`test_diagnostics_page_has_keyhelp_element`).
- `GET /diagnostics` 200 body contains the authority notice text, the db path, the
  word "non-authoritative", the vector state, default/effective mode strings, and an
  exclusion-set entry (`test_diagnostics_page_ok_with_hybrid_available`).
- `GET /api/diagnostics` returns the same information as JSON, plus `?freshness=1`
  toggling freshness inclusion (`test_api_diagnostics_ok_returns_same_keys_as_page`,
  `test_api_diagnostics_freshness_query_param_includes_freshness`).

Manual, non-test verification (ad hoc interpreter runs, not part of the pytest
suite, recorded here per the evidence-discipline rule):

- `_rerank_artifact_present()` invoked directly: returned `True` -- the pinned
  reranker artifact directory (`RHACO_corpus_index.RERANK_MODEL_DIR`, read as a
  constant only) exists on this host, and the call completed in well under a
  second, confirming importing `RHACO_corpus_index` does not itself trigger any
  `torch`/`FlagEmbedding` load (consistent with
  `docs/rounds/R00_I1_corpus_index_contracts.report.md` section 6, l.1424-1425:
  "NO torch/FlagEmbedding import at module import time").
- `_find_last_probe_run()` invoked directly: returned the literal string
  `"none recorded"`, confirming the glob-and-fallback path.
- `dataclasses.asdict(view)` on a populated `DiagnosticsView` inspected directly:
  produces the expected nested JSON shape (`index_meta`, `vector`, `rerank`,
  `exclusion_sets`, `freshness` all present with correct keys) -- pasted in this
  session's transcript, not reproduced here for length.

Everything else in this report not covered by a named test or the two manual runs
above is UNVERIFIED (in particular: behavior against a real `CorpusAdapter`, which
does not exist in this worktree -- `corpus_adapter` is a concurrent wave-1 strand).

## Material alternatives

- **`data-mode`/`data-vector` placement.** The dispatch requires "root `<html>` or
  `<main>` carries `data-mode=...` and `data-vector=...` for the probe", but
  `base.html` (owned by the `web` module, out of scope per working rule 1) has no
  attribute-injection hook on either tag. Considered: (a) skip the requirement and
  note it as a gap; (b) set the attributes only via a `<script>` that mutates the
  real `<main id="main">` at runtime; (c) render them server-side on a wrapper
  `<div id="diagnostics-root">` inside the content block, *and* additionally mirror
  them onto `<main>` via script for any DOM reader that expects them literally
  there. Chose (c): it is the only option that is both TestClient-visible (raw
  HTML, no JS execution needed) and, once JS runs, satisfies a DOM reader that
  queries `<main>` directly. (a) fails a stated deliverable outright; (b) alone
  would be invisible to `TestClient`-based tests and to any static HTML inspection.
  Flagged as a change request below rather than silently worked around.
- **Fault-script placement.** Considered emitting the `console_error` throw script
  unconditionally with a runtime `if` guard in JS (reading `active_fault` from a
  data attribute) versus a server-side Jinja `{% if %}` that omits the tag entirely
  when the fault is inactive. Chose the server-side `{% if %}`: task item 4 requires
  the script to be *absent* (not merely inert) when the fault is not set, which the
  Jinja-side omission satisfies directly and testably via a substring-absence
  assertion; a JS-side guard would still emit inert script text that "is present"
  in the served HTML.
- **`last_probe_run` glob root.** Considered resolving
  `docs/probe-qualification/runs/*/run_summary.json` relative to the process
  current working directory (matching the literal dispatch wording) versus relative
  to the workspace root computed from `__file__`. Chose `__file__`-relative: the
  dispatch's own gate commands are run with the worktree as cwd, but a future
  caller (e.g. a differently-cwd'd test runner) would otherwise silently see
  `"none recorded"` even when a run exists; anchoring to the module's own location
  is robust to caller cwd and still resolves to the same path (`<worktree>/docs/
  probe-qualification/runs/...`) under the documented invocation.

## Decisions

- `DiagnosticsView` and `RerankStanding` are new dataclasses defined in
  `explorer/diagnostics/service.py` (not requested to live in `explorer/models.py`,
  and adding fields there would be a change request I did not need to make --
  every value the view needs is already expressible from existing model types plus
  two small module-local wrapper types).
- `build_view(adapter, settings, *, freshness: FreshnessView | None = None)`: the
  freshness value is a parameter, not something `build_view` computes itself. The
  `GET /diagnostics` route calls it with no freshness (task item 1: "None unless
  requested"); the `POST /diagnostics/freshness` route calls `adapter.freshness()`
  itself first and passes the result in. This keeps `build_view` a pure read of
  already-fetched adapter state with no decision-making about when to trigger the
  one write-adjacent, expensive call (CONSTRAINTS.md O9).
- Adapter is reached only through `explorer.app.get_adapter(request)`, imported
  lazily inside each route handler (not at module top level) to avoid any import-
  order assumption about when `explorer.app` finishes defining `get_adapter`
  relative to `explorer.diagnostics.routes` being imported by
  `create_app()`'s `importlib.import_module` loop; verified safe either way, but
  the lazy form is the more defensive of the two and costs nothing.
- `RHACO_corpus_index` is imported inside `_rerank_artifact_present()` (not at
  module top level) so that a module-load failure of `RHACO_corpus_index` (e.g. the
  file moves, or the read-only path is unavailable in some future run context)
  degrades to `artifact_present=False` rather than making the entire
  `explorer.diagnostics.service` module unimportable.
- Test doubles use a hand-written `FakeAdapter` (not a `Mock`/`unittest.mock`
  object) exposing exactly the four methods and three attributes the diagnostics
  module calls (`index_meta`, `vector_availability`, `exclusion_sets`, `freshness`,
  `db_path`, `docs_root`, `active_fault`) -- matches the dispatch's explicit
  instruction ("tests/diagnostics/fake_adapter.py ... injected as app.state.adapter,
  returning fixed IndexMeta / VectorAvailability / FreshnessView / exclusion_sets
  values from explorer/models.py").

## Result

All three required gates pass (Evidence section, exact commands/output above).
25 new tests, 0 failures. `ruff` clean over `explorer tools tests`. The worktree is
clean (see StructuredOutput). Deliverables 1-4 of task B3 are complete:

1. `build_view` assembles every field named in the dispatch (app_version, db_path +
   non-authoritative notice, full `index_meta` incl. live counts/db size/mtime,
   `VectorAvailability`, default/effective mode, exact degradation text,
   `exclusion_sets()`, fixed rerank standing text + artifact presence, last probe
   run with the specified fallback, `AUTHORITY_NOTICE`, freshness defaulting to
   `None`).
2. `routes.py` registers exactly the three routes named, with the exact adapter-
   absent behavior (HTML notice + 503 on the page/freshness POST, JSON
   `{"error": "corpus_adapter not built"}` + 503 on the API).
3. The template extends `base.html`, labels every value with `<dt>/<dd>` or table
   headers, carries the hidden `#keyhelp` element, and emits the fault-only throw
   script gated on `adapter.active_fault == "console_error"`.
4. `tests/diagnostics/` covers every enumerated case with `TestClient` and the
   fake adapter; no server process is spawned anywhere in the suite.

## Unresolved uncertainty

- No real `CorpusAdapter` exists yet in this worktree (it is being built
  concurrently by another strand on a different branch), so nothing here has been
  exercised against the real contract's actual runtime shapes -- only against the
  dispatch's documented method signatures and `explorer/models.py`'s dataclass
  fields, both read directly. If the landed `CorpusAdapter` differs from
  `ARCHITECTURE.md` section 4.1 in a way that changes `index_meta()`,
  `vector_availability()`, `exclusion_sets()`, or `freshness()`'s return shapes,
  `build_view` would need a follow-up round.
- `docs/probe-qualification/runs/*/run_summary.json` does not exist yet (built by
  the `probe` strand / wave 3), so the "found" branch of `_find_last_probe_run` is
  verified only by direct code reading and the dataclass/JSON shape it would
  produce, not by an actual run-summary fixture. UNVERIFIED against a real file.
- The exact key/field name `run_summary.json` files will use once the probe strand
  lands is not something this strand can see; `_find_last_probe_run` treats the
  entire parsed JSON as an opaque `summary` value and does not depend on any
  specific key inside it, which should make it robust to that strand's eventual
  choices, but this is a design expectation, not a verified fact.

## Change requests

- **Requestor:** diagnostics (B3).
  **Affected contract/path:** `explorer/web/templates/base.html` (owned by the
  `web` module / integrator).
  **Evidence:** the dispatch (task B3 item 2) requires "root `<html>` or `<main>`
  carries `data-mode=\"<effective mode>\"` and `data-vector=\"available|
  unavailable\"` for the probe", but `base.html`'s `<main id="main" tabindex="-1">`
  and `<html lang="en">` tags are hard-coded with no block or slot a child template
  can use to add attributes.
  **Compatibility impact:** none to existing pages; purely additive.
  **Migration:** add an empty block on the `<main>` open tag, e.g.
  `<main id="main" tabindex="-1"{% block main_attrs %}{% endblock %}>`, so
  `diagnostics.html` (and any future module needing the same hook) can write
  `{% block main_attrs %} data-mode="..." data-vector="..."{% endblock %}` and have
  it land on the real `<main>` element server-side.
  **Invalidated tests/probes:** none of this round's tests depend on the fix --
  they assert against `#diagnostics-root` (server-rendered, TestClient-visible) and
  the JS mirror onto `<main>` (Playwright-visible). If `base.html` gains the hook,
  `diagnostics.html`'s wrapper `<div id="diagnostics-root">` and the mirroring
  `<script>` block become removable in a follow-up round, and the existing tests
  would need their `data-mode="..."`/`data-vector="..."` substring assertions
  re-pointed from the wrapper div's markup to the `<main>` tag's -- a one-line
  change per test, not a behavior change.

## Assumptions

- The workspace-root-relative glob for `run_summary.json` is anchored via
  `__file__` (see Material alternatives) rather than `os.getcwd()`; this assumes
  no future caller relocates `explorer/diagnostics/service.py` without also
  updating the two `os.path.dirname` calls that compute `_WORKSPACE_ROOT`.
- `RHACO_corpus_index.RERANK_MODEL_DIR` remains a plain string constant (not a
  property or descriptor) as documented in
  `docs/rounds/R00_I1_corpus_index_contracts.report.md` section 2 (l.395); the code
  uses `getattr(..., "RERANK_MODEL_DIR", None)` defensively but does not otherwise
  guard against the constant's type changing.
- `adapter.active_fault` is assumed to be `None` on every real (non-fixture)
  `CorpusAdapter`, per `explorer/faults.py`'s `active_fault()` function (already
  landed, integrator-owned) refusing any fault whose resolved db path lies under a
  RHACO tree -- so the `console_error` script path is inert-by-construction against
  the live index, exactly as ARCHITECTURE.md A13 intends.
- No `docs/probe-qualification/last_run.json` (singular, as ARCHITECTURE.md 4.6
  phrases it) vs. `docs/probe-qualification/runs/*/run_summary.json` (plural, as
  this dispatch phrases it) reconciliation was attempted -- the dispatch text for
  this specific task is more specific and more recent than the architecture
  summary sentence, so it was followed as the operative contract; flagged here in
  case the two were meant to describe the same thing differently, since if a wave-3
  probe writes to the singular path instead, `_find_last_probe_run` would need to
  glob or check both.
