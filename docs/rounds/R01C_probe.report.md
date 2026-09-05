# R01C_probe -- round report (task C1, correction round)

## Header

- Hand: RHACO-HND-20260903-001 section 2 I as amended by A1.3
- Strand: S4-C1 (module builder, probe, correction round), tier mid, agent_type
  general-purpose write-scoped to the worktree
- Model: You are powered by the model named Sonnet 5. The exact model ID is
  claude-sonnet-5.
- Worktree: `C:\highsierralabs\RHACO_Corpus_Explorer\.worktrees\probe`
- Branch: `build/probe`
- t_start_utc: 2026-09-05T00:09:30Z
- t_end_utc: 2026-09-05T00:22:55Z
- Round: probe round 2 of budget 4, task C1 (repair the probe's verdict
  predicate and add the qualification-state vocabulary)

## Change

Landed, inside the worktree, on owned paths only:

1. **`tools/probe_corpus_explorer.py`** (commit `0f19e6d`):
   - `PresetSpec` gains `expected_status`, `data_mode_in`, `data_vector_in`,
     `require_title`, `required_classes`.
   - `Verdict` dataclass (`ok`, `reasons`, `fault_detected`, `fault_class`)
     and `evaluate_page(observation, spec) -> Verdict`, the observed-fault
     predicate for page presets (rules a-e per the dispatch), replacing
     round 1's `ok = error is None`.
   - `FAULT_CLASS_TABLE` (KB1..KB5 -> `explorer.faults.FAULTS` names) and
     `FAULT_TO_CLASS` (its reverse), kept next to `PRESET_REGISTRY`;
     `CONSOLE_ERROR_FAULT_TEXT` and `FAULT_TEXT_MARKERS` (currently one
     entry, KB5) with `_attribute_fault_class()`.
   - `_page_error_listener()` registers a Playwright `pageerror` listener;
     `run_page_preset` now collects `page_errors` and mirrors each into
     `console_errors` with `"type": "pageerror"` before calling
     `evaluate_page`; `_extract_dom_observations` now also reads
     `data-vector`.
   - `run_page_preset`'s return dict gains `verdict` ("PASS"/"FAIL"),
     `reasons`, `fault_detected`, `fault_class`, `page_errors`, `vector`;
     `ok` stays the boolean mirror of `verdict`.
   - `diagnostics` preset upgraded: `data_mode_in={"hybrid",
     "hybrid-degraded-lexical"}`, `data_vector_in={"available",
     "unavailable"}`, `require_title=True`, `required_classes=("KB5",)`; the
     round-1 404-tolerant "route absent" language is gone from its label
     (the field `route_absent` is kept as a descriptive, non-gating
     observation).
   - `_w()`/`W1`-`W10` gain the `required_classes` table from the dispatch
     (item 2); `healthz`/`KG`/`KB1`-`KB5` get `required_classes=()`.
   - `determine_run_kind()`, `derive_qualification()` (the AC-3 state
     machine: INCOMPLETE / QUALIFICATION_PASS / FRAMEWORK_SMOKE_PASS /
     PRODUCT_EVIDENCE_PASS / FAIL), `_load_ledger()` / `_update_ledger()`
     (idempotent, ASCII).
   - New `--ledger PATH` CLI flag (default resolved from the probe file's
     own location).
   - `main()` rewritten: computes `run_kind`, loads the ledger, derives
     `qual`, writes it to `run_summary.json` (`run_kind`,
     `qualification_state`, `product_evidence_eligible`,
     `qualified_failure_classes`, `incomplete_presets`,
     `product_evidence_blocked_by`, `reasons`, `ledger_path`), appends to
     the ledger only on `QUALIFICATION_PASS`, prints `qualification_state`,
     and returns the new exit-code table (0/0/0/1/3).
   - Module docstring: added `v1.1 2026-09-04` history entry.
2. **`tests/probe/test_evaluate_page.py`** (new, 16 tests, commit `878a4c1`):
   unit tests for every rule (a)-(e), the `expected_status` exception, and
   fault attribution (marker match -> KB5; unrelated error -> FAIL without
   attribution; marker as a substring still attributes).
3. **`tests/probe/test_qualification_state.py`** (new, 11 tests, commit
   `878a4c1`): synthetic-result unit tests for `derive_qualification` --
   qualification with/without detection, wrong-class attribution, a missing
   page preset, other-preset-must-pass, smoke clean/fail,
   product covered/uncovered by a synthetic ledger, and INCOMPLETE
   overriding any run_kind.
4. **`tests/probe/test_probe_qualification_subprocess.py`** (new, 1 test,
   commit `878a4c1`): subprocess run of `--preset diagnostics --fault
   console_error --ledger <tmp path>` against a tmp fixture db, asserting
   the item 4(ii) run_summary/observation fields, exit code 0, the tmp
   ledger recording KB5, and that the **committed** ledger's bytes are
   unchanged before/after.
5. **`docs/probe-qualification/README.md`** (commit `31f82b3`): the
   observed-fault predicate rules, the empirical pageerror-vs-console
   finding, the full AC-3 vocabulary and derivation, the per-preset
   `required_classes` table, the Q0-Q3/FINAL wave reading, the ledger
   format, and the historical-runs classification note.
6. **Q0 qualification evidence** (commit `edaada4`), against
   `fixtures/fixture_index.db` freshly built with `fixtures/
   build_fixture_index.py --docs-root fixtures/corpus --db fixtures/
   fixture_index.db --force`:
   - `docs/probe-qualification/runs/20260905T002014Z/` -- (i) clean fixture,
     `--preset diagnostics`.
   - `docs/probe-qualification/runs/20260905T002024Z/` -- (ii) `--fault
     console_error --preset diagnostics`.
   - `docs/probe-qualification/runs/20260905T002034Z/` -- (iii) `--preset
     all` on the clean fixture (INCOMPLETE demonstration).
   - `docs/probe-qualification/qualification_ledger.json` -- gained KB5
     from run (ii).
7. This report.

No file outside the owned paths (`tools/probe_corpus_explorer.py`,
`fixtures/**`, `tests/probe/**`, `docs/probe-qualification/**`, this report)
was touched. The two pre-existing run directories
(`runs/20260904T033047Z/`, `runs/20260904T034711Z/`) were read but not
modified, renamed, or deleted. `explorer/**` (including `explorer/faults.py`
and `explorer/diagnostics/`) was read only, never edited.

## Evidence

Checks actually run, in order, with results:

| # | Check | Command | Result |
|---|---|---|---|
| 1 | Ruff (gate a) | `...\.venv\Scripts\python.exe -m ruff check explorer tools tests --output-format concise` | `All checks passed!` exit 0 -- run twice, before and after the final commit, both clean |
| 2 | Pytest (gate b) | `...\.venv\Scripts\python.exe -m pytest tests/probe -q` | `40 passed in 4.13s` exit 0 (12 round-1 + 28 new: 16 `test_evaluate_page.py` + 11 `test_qualification_state.py` + 1 `test_probe_qualification_subprocess.py`) |
| 3 | L1 index-write check (gate c) | `...\.venv\Scripts\python.exe tools/l1_index_write_check.py` | `hits=6 allowlisted=6 defects=0 verdict=PASS` (unchanged from round 1: all 6 hits inside `fixtures/build_fixture_index.py`) |
| 4 | Fixture rebuild | `fixtures/build_fixture_index.py --docs-root fixtures/corpus --db fixtures/fixture_index.db --force` | `cards=7 fts_docs=8 edges=7 edges_unresolved=1 id_aliases=11 orphan_cards=0 missing_cards=0 broken_yamls=0` (matches round 1) |
| 5 | Empirical finding: which event carries the fault's throw | scratch run: `--preset diagnostics --fault console_error --port 8902 --out _scratch_fault --ledger _scratch_ledger.json`, then read `_scratch_fault/diagnostics.json` before mirroring logic ran in production form | `console_errors` from the raw `console` listener was empty; the throw arrived only as `page_errors: [{"message": "RHACO_EXPLORER_FAULT console_error"}]`, i.e. on Playwright's `pageerror` event, not `console`. This is why `run_page_preset` registers both listeners and mirrors `page_errors` into `console_errors` (type `"pageerror"`) so `evaluate_page` rule (c) covers it. Scratch dirs (`_scratch_clean/`, `_scratch_fault/`, `_scratch_all/`, `_scratch_ledger.json`) were deleted before committing -- not evidence, not present in the tree |
| 6 | Item 4(i): clean fixture, `--preset diagnostics` | `python tools/probe_corpus_explorer.py --db fixtures/fixture_index.db --docs-root fixtures/corpus --preset diagnostics --port 8911` (committed `--out`, default `--ledger`) | exit 0; `run_kind=smoke`; `diagnostics` verdict `PASS`, `mode=hybrid-degraded-lexical`, `vector=unavailable` (fixture has no vector set), `reasons=[]`; `qualification_state=FRAMEWORK_SMOKE_PASS`; committed at `runs/20260905T002014Z/` |
| 7 | Item 4(ii): fixture + fault, `--preset diagnostics --fault console_error` | same, `--fault console_error --port 8912` | exit 0; `run_kind=qualification`; `diagnostics` verdict `FAIL`, `fault_detected=true`, `fault_class=KB5`, `reasons=["console_error[pageerror] (fault KB5): RHACO_EXPLORER_FAULT console_error"]`; `qualification_state=QUALIFICATION_PASS`, `qualified_failure_classes=["KB5"]`; committed at `runs/20260905T002024Z/`; `qualification_ledger.json` gained `"KB5": {"run": "docs/probe-qualification/runs/20260905T002024Z", "recorded_utc": "2026-09-05T00:20:26.215108+00:00"}` and a matching `runs[]` entry |
| 8 | Item 4(iii): clean fixture, `--preset all` | same, `--preset all --port 8913` | exit **3**; `qualification_state=INCOMPLETE`; `incomplete_presets` lists all 16 not-yet-implemented presets (`W1-W10, KG, KB1-KB5`); `healthz` and `diagnostics` both `ok:true` underneath; committed at `runs/20260905T002034Z/` |
| 9 | Existing healthz smoke test still green | `test_probe_smoke.py::test_probe_healthz_preset_subprocess` (part of check #2's 40) | passed; `summary["verdict"] == "PASS"` for a healthz-only smoke run, confirmed still holds under the new `qualification_state`-derived verdict (`FRAMEWORK_SMOKE_PASS -> "PASS"`) |
| 10 | New subprocess test | `test_probe_qualification_subprocess.py::test_probe_diagnostics_console_error_fault_subprocess` (part of check #2's 40) | passed; asserts `run_kind`, `qualification_state`, `qualified_failure_classes`, per-preset `verdict`/`fault_detected`/`fault_class`, the tmp ledger gaining KB5, and the committed ledger's bytes unchanged before/after |
| 11 | Worktree cleanliness | `git status --porcelain=v1` | clean after each commit; final `git rev-parse HEAD` = `edaada4e535f8ce4977fd444a52a8dee312bbc23` |

Every "tested" claim above names the test, command, or file read that
produced it. Anything not covered by a row above is UNVERIFIED (see
"Unresolved uncertainty").

## Material alternatives

- **Where to attach the observed-fault predicate.** Considered making
  `evaluate_page` a method on a class holding registry/state. Rejected: the
  dispatch specifies "a pure function `evaluate_page(observation, spec) ->
  Verdict`" explicitly so it is independently unit-testable without a
  server, browser, or registry in scope -- exactly what
  `test_evaluate_page.py` exercises.
- **Fault attribution table shape.** Considered inlining the KB5 marker
  check directly in `evaluate_page`'s rule (c). Chose a `FAULT_TEXT_MARKERS`
  dict (marker substring -> class) plus the separate `FAULT_CLASS_TABLE`
  (KBn -> fault name) the dispatch explicitly asked for "next to
  `PRESET_REGISTRY`", so wave 2 adds KB1-KB4 by inserting one dict entry
  each rather than editing `evaluate_page`'s control flow.
- **`route_absent` field.** Considered deleting it now that a 404 is never
  an accepted outcome. Kept it as a descriptive (non-gating) observation --
  removing a previously-consumed key is a needless compatibility break for
  no one specified as depending on its absence, whereas keeping it costs
  nothing and preserves round-1's shape for any reader that still checks it
  informationally.
- **Which pages a fault "touches" for `QUALIFICATION_PASS`.** The dispatch
  states the rule only for `console_error` ("every page-kind preset run").
  Implemented `_FAULTS_TOUCHING_ALL_PAGES = frozenset({"console_error"})`
  rather than guessing a rule for KB1-KB4 (whose runners do not exist this
  round); a fault not in that set yields `touched=[]`, which
  `derive_qualification` treats as "no page-kind preset selected to
  exercise the fault" -> FAIL with that reason, rather than silently
  passing. Wave 2 extends the set as each KB's page-touch rule is
  specified.
- **Ledger overwrite vs. append-only classes.** Considered making
  `ledger["classes"][cls]` append-only (refuse to overwrite an existing
  class's run pointer). Chose overwrite-with-latest: the ledger is evidence
  of "this class has been detected at least once, most recently here";
  `runs[]` already preserves the full history of qualifying runs, so no
  information is lost by letting `classes` track the newest.
- **Item 4(iii) as a genuinely separate evidence run vs. reusing item
  4(ii)'s directory.** The dispatch marks (iii) optional; ran it as its own
  committed run (`runs/20260905T002034Z/`) rather than skip it, since it is
  the only evidence in this round that exercises `INCOMPLETE` end-to-end
  (exit code 3, `incomplete_presets` populated) and every other row's
  qualification path is otherwise untested against a live subprocess.

## Decisions

- `evaluate_page` treats `spec.expected_status` as an exact-match
  exception to rule (b), not a general "acceptable status" allowlist --
  matches the dispatch's wording ("unless the spec declares
  `expected_status` equal to that status") and the fact that no preset
  declares one this round.
- `page_errors` is recorded as its own list on the page-preset observation
  (raw Playwright `pageerror` payloads) in addition to being mirrored into
  `console_errors`; `evaluate_page` reads only `console_errors` (per the
  dispatch: "mirror them into console_errors ... so rule (c) covers them"),
  so `page_errors` is diagnostic redundancy, not a second predicate input.
- `determine_run_kind` reuses `explorer.faults.is_under_rhaco_tree` exactly
  as named in the dispatch and ARCHITECTURE.md A13, rather than
  reimplementing the two-tree-spelling check.
- `_qual()` always emits all six AC-3-related keys
  (`qualification_state`, `product_evidence_eligible`,
  `qualified_failure_classes`, `incomplete_presets`,
  `product_evidence_blocked_by`, `reasons`) regardless of state, so
  `run_summary.json`'s shape is uniform across FAIL/INCOMPLETE/PASS states
  rather than varying by which keys happen to apply.
- The per-preset trimmed summary under `run_summary.json["results"]` was
  extended with `verdict`/`reasons`/`fault_detected`/`fault_class` (present
  as `null` for `json_endpoint`/`not_implemented` kinds) so a reader of
  `run_summary.json` alone -- e.g. `explorer/diagnostics/service.py`'s
  `_find_last_probe_run`, which treats it as an opaque JSON object -- sees
  the qualification-relevant fields without opening each `<preset>.json`.
- A `run_error` (server never became ready, or an unhandled exception)
  short-circuits straight to `qualification_state="FAIL"` with the error
  text under `reasons`, bypassing `derive_qualification` entirely --
  `results` may be empty or partial in that case and should not be
  interpreted as "every preset passed."

## Result

**COMPLETE.** Probe round 2 of budget 4 (task C1). All three required gates
pass with the exact specified commands (Evidence #1-3). 40/40 tests green,
including the 12 round-1 tests kept green unmodified and 28 new tests for
this round's deliverables. All three item-4 evidence runs were produced,
committed, and match their specified expectations exactly (Evidence #6-8);
the qualification ledger gained KB5 from the fault run. The empirical
question the dispatch asked to be settled (`console` vs. `pageerror` for the
diagnostics fault's throw) was settled by direct observation (Evidence #5)
and is documented in both the module (`_page_error_listener`'s docstring)
and the README. Worktree left clean after every commit; final
`git rev-parse HEAD` = `edaada4e535f8ce4977fd444a52a8dee312bbc23`.

## Unresolved uncertainty

- **W1-W10 / KG / KB1-KB5 remain stubs**, by design this round; their real
  runners are UNVERIFIED beyond "reports `not_implemented_yet` cleanly and
  makes the run `INCOMPLETE`" (Evidence #8).
- **KB1-KB4's attribution rules are not implemented.** `FAULT_TEXT_MARKERS`
  and `_FAULTS_TOUCHING_ALL_PAGES` currently cover only KB5/console_error;
  wave 2 must determine each fault's actual observable signature (e.g.
  `wrong_doc_for_id`'s neighbouring-card substitution has no console/page
  error at all -- it will need a DOM/API-comparison rule, not a text-marker
  rule) and extend both structures accordingly.
- **KB3 (`reverse_edges`) and W5/W6 (lineage)** are deferred to wave 3 per
  the dispatch; nothing in this round exercises the lineage surface at all.
- **`required_classes` for W1-W10 are asserted, never yet checked against a
  real product run** -- no product-path (`--db` under a RHACO tree) run was
  performed this round (the dispatch explicitly reserves that for the
  integrator, post-merge); `PRODUCT_EVIDENCE_PASS` / the
  `product_evidence_blocked_by` path is verified only against synthetic
  data (`test_qualification_state.py`) and is UNVERIFIED against a real
  server response.
- **`_FAULTS_TOUCHING_ALL_PAGES`'s generalization is a guess for future
  faults.** The dispatch specifies the "every page-kind preset run" rule
  only for `console_error`; when wave 2 adds KB1/KB2/KB4 (search/reader
  pages), whether each touches *every* page-kind preset or only specific
  ones is an open question the dispatch does not answer for those faults.
- **Ledger idempotency was verified only for the "same `--out` path
  reused" case implicitly** (via the two runs in this round each getting a
  distinct auto-generated stamp, so no direct-collision test exists);
  no test constructs two runs sharing one `run_rel` and asserts the second
  does not duplicate a `runs[]` entry. UNVERIFIED beyond code inspection of
  `_update_ledger`'s `any(r.get("run") == run_rel ...)` guard.
- **`disable_vec` / W7's degraded-channel path** was not exercised this
  round (no preset that reads it is implemented yet); the fixture's
  no-vector-by-construction state (`vector: unavailable` in Evidence #6-7)
  is a different code path (no vec table at all) than `RHACO_CORPUS_DISABLE_VEC=1`
  against an index that *does* have one.

## Change requests

None this round. The round-1 DOM-attribute change request (`data-mode`,
`data-selected-doc-id`, `data-doc-id` on templates) is superseded by
observed fact: `explorer/diagnostics/templates/diagnostics/diagnostics.html`
already implements `data-mode` and (new) `data-vector` on both `<html>` and
a wrapper element per ARCHITECTURE.md A19, confirmed by Evidence #6-7's
`mode`/`vector` readings. No new cross-module change is requested this
round; KB1-KB4's attribution rules and the real W1-W10/KG/KB1-KB5 runners
are wave-2 work already scoped by the dispatch, not a change to another
module's contract.

## Assumptions

- KB1-KB5 continue to map 1:1, in order, onto `explorer.faults.FAULTS`
  (`wrong_doc_for_id, stale_card, reverse_edges, broken_jump,
  console_error`), per round 1's assumption, now made explicit and
  machine-checkable as `FAULT_CLASS_TABLE`.
- "Every page-kind preset the injected fault touches" for `console_error`
  means every page-kind preset actually *selected in this run*, not every
  page-kind preset that exists in `PRESET_REGISTRY` -- a run with
  `--preset diagnostics --fault console_error` need not also run W9 (also
  page-kind, once implemented) to qualify, since W9 was not selected.
- The `required_classes` table in item 2 of the dispatch is copied
  verbatim into `PRESET_REGISTRY`; no interpretation was needed since the
  dispatch enumerates it exhaustively per preset.
- `route_absent` in the observation/summary is now purely descriptive
  (`http_status == 404`) with no bearing on `ok`/`verdict` -- the dispatch's
  "'route absent' is no longer an accepted state" is read as "no longer a
  *passing* state," not as "remove the field."
- A `run_error` (e.g. the server failed to become ready) is treated as an
  unconditional `FAIL`, not `INCOMPLETE` -- the dispatch's INCOMPLETE
  condition is specifically "a selected preset still reporting
  `not_implemented_yet`," which a `run_error` (no presets even ran) does
  not satisfy.
