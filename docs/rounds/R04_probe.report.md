# R04_probe -- round report (task B10, Q3 + FINAL suite)

## Header

- Dispatch: RHACO-HND-20260903-001 section 2 I as amended by A1.3, item 4 of the
  Director's 2026-09-05 ruling.
- Strand: S6-B10, probe builder (Q3 lineage cases and the FINAL suite), tier mid,
  agent_type general-purpose write-scoped to the worktree.
- Model: You are powered by the model named Sonnet 5. The exact model ID is
  claude-sonnet-5.
- Worktree: `C:\highsierralabs\RHACO_Corpus_Explorer\.worktrees\probe`
- Branch: `build/probe`. Started at round-3 commit `a0dacd7`; fast-forwarded (the
  dispatch's required first git act) to the round-3 boundary
  `d9e71adb3c2f791cf0f6d94321e8d524843baa62` (`git merge --ff-only`, confirmed
  fast-forward, `git log --oneline -1` matched the boundary sha before any other
  work began).
- Round: **probe module round 4 of 4 -- the LAST round this module gets.** No
  round 5 exists (Director ruling, not waived).
- Prompt verification: archived prompt
  `docs/rounds/R04_probe.prompt.md`, sha256
  `c88e5402665dbaa421778eba9955fe3dd42bfef00acc40a33d91b8f29b860410`, matched the
  dispatch header exactly (`Get-FileHash -Algorithm SHA256`, run before reading
  the file or acting on it).

## Change

Landed, inside the worktree, on owned paths only (`tools/probe_corpus_explorer.py`,
`tests/probe/**`, `docs/probe-qualification/**`, this report):

1. **`tools/probe_corpus_explorer.py`** (v1.2 -> v1.3):
   - `_kb3_verdict(observed, expected_correct, expected_fault)` -- a pure,
     dependency-free predicate for `reverse_edges`, symmetric like `_kb1_verdict`
     (a match to `expected_correct` is a quiet PASS, `expected_fault` is the
     known-bad detection, anything else -- including a missing edge observed as
     a tuple of `None`s -- is an unattributed FAIL).
   - `_run_kb3` -- a `kind="workflow"` runner: navigates the CMP fixture's
     lineage page, locates the campaign_child edge to the ANL fixture card in
     BOTH the `.edge-list` `<li>` and the graph `<line>` via the new
     `Session.attr_dicts` helper, cross-checks the two against each other and
     against `/api/lineage`, then hands the one observed `(from_id, to_id,
     direction)` triple to `_kb3_verdict` against the frozen fixture fact.
   - `Session.attr_dicts(selector, names)` -- reads several attributes (or,
     via the literal name `"$text"`, `textContent`) off every element matching
     `selector` at once, in DOM order -- needed because the Q3 checks compare
     several fields of the SAME row/line against each other, which `attr_all`
     (one attribute across every match) cannot express without an ordering
     assumption across separate calls.
   - `_run_kg` extended with the Q3 "known-good typed-edge-direction" case
     (deliverable 2): (d) the CMP fixture's two campaign_child edges, both
     outgoing, page/API agree; (e) the amendment's outgoing `amends` edge,
     `from`=the amendment's own filename stem, `to`=the parent id; (f) the
     reference v1_0 fixture's outgoing `supersedes` edge to v1_1, the chain
     marking v1_1 head with "current head" text, and the superseded banner
     present, page/API agree; (g) the HND fixture's unresolved `cites` edge to
     the deliberately-absent id, with the unresolved marker, page/API agree.
   - `_run_w5` -- production, centered on `RHACO-CMP-20260903-001`: typed
     directional edges (campaign_child to its members, outgoing), every
     `direction_label` checked against `explorer.models.RELATION_LABELS`
     (imported, matching the existing `COMPONENT_RANK_NOT_EXPOSED` precedent --
     both are integrator-owned shared constants in `explorer/models.py`, unlike
     `HYBRID_DEGRADED_NOTICE_TEXT`, which is deliberately re-derived
     independently because it names a DIFFERENT builder's own text), a
     chronological reasoning trail, page/API edge-set parity, and the
     "independent check" (deliverable 3): for two resolved edges (to
     `RHACO-HND-20260903-001` and `RHACO-CHG-20260903-001`), the child's own
     `.card.yaml` is read directly off `C:\RHACO\docs` and its `depends_on`
     list is confirmed to name the campaign -- never through the index.
   - `_run_w6` -- production, two centres: (a) `RHACO_Card_YAML_Schema_
     Specification_v1_8` (Superseded): the banner, the chain (`v1_9` head,
     "current head" text), the outgoing `supersedes` edge, and (per PROMPT.md
     W6) the historical document still opened through the reader; (b) this
     build's own A1 amendment of `RHACO-HND-20260903-001`: its outgoing
     `amends` edge, resolved and linked, PLUS a visit to the PARENT's own
     lineage page recording the SCOPE.md row 17 known limitation (a new
     `W6_KNOWN_LIMITATION` constant) -- asserting only what that row says still
     holds (present, typed, directional, resolved), never failing on the
     disclosed missing click-through.
   - `--preset` now also accepts a comma-separated list (e.g.
     `KG,KB1,KB2,KB3,KB4,KB5`), used for the FINAL fixture run below; a single
     name or `all` behave exactly as before.
   - `PRESET_REGISTRY["KB3"/"W5"/"W6"]` changed `kind` from `"not_implemented"`
     to `"workflow"`; `WORKFLOW_RUNNERS` gained the three new entries. No
     preset in the registry is `not_implemented_yet` after this round.
   - Module docstring VERSION HISTORY gained the v1.3 entry.
2. **`tests/probe/test_workflow_verdicts.py`** -- four new unit tests for
   `_kb3_verdict` (correct direction is a clean pass, swapped direction is
   detected as KB3, a missing edge fails without attribution, an unexpected
   triple fails without attribution), mirroring the existing `_kb1_verdict`
   coverage exactly.
3. **`tests/probe/test_probe_workflow_subprocess.py`** -- one new subprocess
   test, `test_probe_kb3_reverse_edges_fault_subprocess_qualifies`, mirroring
   the existing KB2 test: runs the probe as a subprocess against a tmp-built
   fixture db with `--fault reverse_edges --preset KB3` and a tmp `--ledger`,
   asserts `QUALIFICATION_PASS`, `fault_class == "KB3"`, the swapped
   observation values, that the TMP ledger gains KB3, and that the COMMITTED
   ledger is untouched by the test.
4. **`docs/probe-qualification/README.md`** -- the preset-reality table (KB3,
   W5, W6 now "real"), the `not_implemented` bullet (none left), a new bullet
   describing `_kb3_verdict` next to KB1/KB2/KB4's, and the Q3 / FINAL rows in
   "Qualification waves" (both marked done this round, with the FINAL row
   disclosing the W6 production FAIL up front rather than burying it).
5. **`docs/probe-qualification/qualification_ledger.json`** -- gained `KB3`
   (idempotent append via a real `--fault reverse_edges --preset KB3` run
   against this worktree's own ledger; `KB1`, `KB2`, `KB4`, `KB5` were already
   present from earlier rounds and are unchanged).
6. **`docs/probe-qualification/runs/**`** -- fourteen new run directories (the
   KB3 qualification run, the FINAL fixture run, and the twelve refreshed
   production runs -- Evidence below).
7. This report.

No file outside the owned paths was modified. `explorer/**` (every module),
`tools/l1_index_write_check.py`, `tools/l4_gold_oracle.py`, every other test
directory, `requirements.txt`, `ruff.toml`, `PROMPT.md`, `RATIONALE.md`,
`DISPATCH_PARAMETERS.md`, `CONSTRAINTS.md`, `ARCHITECTURE.md`, `SCOPE.md`,
`build_state.json`, `docs/LAYERS.md`, `docs/REFERENCE.md`, and every other
module's directory were read only.

## Evidence

Checks actually run, in order, with results:

| # | Check | Command | Result |
|---|---|---|---|
| 1 | Prompt hash verification | `Get-FileHash -Algorithm SHA256 docs/rounds/R04_probe.prompt.md` | `C88E5402665DBAA421778EBA9955FE3DD42BFEF00ACC40A33D91B8F29B860410` -- matched the dispatch header exactly |
| 2 | Fast-forward to round-3 boundary | `git merge --ff-only d9e71adb3c2f791cf0f6d94321e8d524843baa62` | `Updating a0dacd7..d9e71ad`, `Fast-forward` |
| 3 | Baseline suite count at the boundary | `.venv\Scripts\python.exe -m pytest tests -q` (before any change) | `247 passed in 21.42s` |
| 4 | Gate (a) ruff | `.venv\Scripts\python.exe -m ruff check explorer tools tests --output-format concise` | `All checks passed!` exit 0 |
| 5 | Gate (b) pytest (whole suite) | `.venv\Scripts\python.exe -m pytest tests -q` | `252 passed, 2 warnings in 23.27s` (247 base + 5 new: 4 `_kb3_verdict` unit tests, 1 KB3 subprocess test) |
| 6 | Gate (c) L1 index-write check | `.venv\Scripts\python.exe tools/l1_index_write_check.py` | `hits=6 allowlisted=6 defects=0 verdict=PASS` (all 6 hits inside `fixtures/build_fixture_index.py`, unmodified this round) |
| 7 | Fixture index rebuilt | `.venv\Scripts\python.exe fixtures/build_fixture_index.py --docs-root fixtures/corpus --db fixtures/fixture_index.db --force` | `cards=7 fts_docs=8 edges=7 edges_unresolved=1 id_aliases=11` |
| 8 | KB3 qualification (fixture, real ledger) | `.venv\Scripts\python.exe tools/probe_corpus_explorer.py --db fixtures/fixture_index.db --docs-root fixtures/corpus --preset KB3 --fault reverse_edges` | `docs/probe-qualification/runs/20260905T043102Z`: `run_kind=qualification`, `qualification_state=QUALIFICATION_PASS`; `KB3.json`: `verdict=FAIL`, `fault_detected=true`, `fault_class="KB3"`, `observed_triple=["RHACO-ANL-20260115-002","RHACO-CMP-20260115-001","incoming"]` (the swap), edge-list row / graph `<line>` / `/api/lineage` all agree on the swapped triple; ledger now holds `KB1, KB2, KB3, KB4, KB5` |
| 9 | FINAL fixture suite (one run, all known-good + known-bad) | `.venv\Scripts\python.exe tools/probe_corpus_explorer.py --db fixtures/fixture_index.db --docs-root fixtures/corpus --preset "KG,KB1,KB2,KB3,KB4,KB5"` (no fault) | `docs/probe-qualification/runs/20260905T043117Z`: `run_kind=smoke`, `qualification_state=FRAMEWORK_SMOKE_PASS`; every one of the 6 presets `ok=true, verdict=PASS`; `KG.json`'s new Q3 observations verified directly (below) |
| 10 | KG's Q3 observations | inspected `docs/probe-qualification/runs/20260905T043117Z/KG.json` | `cmp_campaign_child_rows`: two rows, both `data-edge-direction=outgoing`, `data-edge-from=RHACO-CMP-20260115-001`, targets `{RHACO-HND-20260115-003, RHACO-ANL-20260115-002}`; `amendment_outgoing_amends_row`: `from=RHACO-HND-20260115-003_Fixture_Handoff_Amendment_A1 to=RHACO-HND-20260115-003 direction=outgoing`; `ref_v1_0_supersedes_row`: `to=RHACO_Fixture_Reference_v1_1 direction=outgoing`; `ref_v1_0_chain`: `v1_0 head=false`, `v1_1 head=true`; `ref_v1_0_banner_present=true`; `hnd_unresolved_cites_row`: `to=RHACO-ANL-20260101-099 direction=unresolved`; `hnd_unresolved_marker_present=true` |
| 11 | Production refresh: W1-W4, W8-W10, healthz, diagnostics (8 individual runs, no fault) | `.venv\Scripts\python.exe tools/probe_corpus_explorer.py --db "C:\RHACO\index\corpus_index.db" --docs-root "C:\RHACO\docs" --preset <NAME>` per name | All 8: `run_kind=product`, `qualification_state=PRODUCT_EVIDENCE_PASS`, `results[<NAME>].ok=true`. Run dirs: W1 `...T043130Z`, W2 `...T043133Z`, W3 `...T043136Z`, W4 `...T043142Z`, W8 `...T043150Z`, W9 `...T043154Z`, W10 `...T043157Z`, healthz `...T043201Z`, diagnostics `...T043203Z` |
| 12 | Production refresh: W7 (`--disable-vec`) | `.venv\Scripts\python.exe tools/probe_corpus_explorer.py --db "C:\RHACO\index\corpus_index.db" --docs-root "C:\RHACO\docs" --preset W7 --disable-vec` | `docs/probe-qualification/runs/20260905T043213Z`: `run_kind=product`, `qualification_state=PRODUCT_EVIDENCE_PASS`, `results.W7.ok=true` |
| 13 | Production refresh: **W5** | `.venv\Scripts\python.exe tools/probe_corpus_explorer.py --db "C:\RHACO\index\corpus_index.db" --docs-root "C:\RHACO\docs" --preset W5` | `docs/probe-qualification/runs/20260905T043145Z`: `qualification_state=PRODUCT_EVIDENCE_PASS`; `W5.json`: `verdict=PASS`, `page_edge_count=19`, `page_campaign_child_outgoing_targets=[RHACO-CCX-20260903-001, RHACO-CCX-20260904-001, RHACO-CHG-20260903-001, RHACO-HND-20260903-001]`, `mismatched_direction_labels=[]`, `reasoning_trail_dates` non-decreasing, `independent_checks`: both `status="VERIFIED"` (read directly from `C:\RHACO\docs\handoffs\RHACO-HND-20260903-001_...card.yaml` and `C:\RHACO\docs\reports\RHACO-CHG-20260903-001_...card.yaml`, `depends_on` names `RHACO-CMP-20260903-001` in both, verbatim on disk) |
| 14 | Production refresh: **W6** -- genuine FAIL, reproduced and root-caused | `.venv\Scripts\python.exe tools/probe_corpus_explorer.py --db "C:\RHACO\index\corpus_index.db" --docs-root "C:\RHACO\docs" --preset W6` | `docs/probe-qualification/runs/20260905T043147Z`: `qualification_state=FAIL`, `verdict=FAIL`; `W6.json`: `reasons=["W6(a): reader for v1_8 data-selected-doc-id=None, expected 'RHACO_Card_YAML_Schema_Specification_v1_8'", "unexpected_http_status[reader_v1_8]: 500", "console_error[error@reader_v1_8]: ...500 (Internal Server Error)", "failed_request[response@reader_v1_8]: http://127.0.0.1:8765/doc/reference/RHACO_Card_YAML_Schema_Specification_v1_8.card.yaml (500)"]`. `server.log` line 109-127 carries the full traceback: `explorer/reader/routes.py:65` -> Jinja renders `explorer/reader/templates/reader/reader.html:251` (`{{ view.card_parsed \| tojson(indent=2) }}`) -> `TypeError: Object of type date is not JSON serializable`. **Everything else in W6 passed cleanly** (see obs below and "Decisions") -- the failure is isolated to this one reader navigation |
| 15 | W6's other observations (all correct, despite the overall FAIL) | inspected `docs/probe-qualification/runs/20260905T043147Z/W6.json` | `v1_8_banner_present=true`; `v1_8_chain`: v1_6/v1_7/v1_8 `head=false`, v1_9 `head=true` with `"current head"` text; `v1_8_supersedes_edge`: `to=RHACO_Card_YAML_Schema_Specification_v1_9 direction=outgoing`; `amendment_outgoing_amends_row`: `to=RHACO-HND-20260903-001 direction=outgoing`; `amendment_outgoing_amends_link=/doc/handoffs/RHACO-HND-20260903-001_..._Dispatch.card.yaml` (a real link); `amendment_api_outgoing_amends.resolved=true`; `parent_incoming_amends_row`: `from=RHACO-HND-20260903-001_..._Amendment_A1... direction=incoming`; `parent_incoming_amends_link=None`; `parent_api_incoming_amends.resolved=true` (NOT unresolved); `known_limitation_reproduced=true` -- SCOPE.md row 17 reproduces exactly: present, typed, directional, resolved, no link |
| 16 | Root-cause severity check (read-only grep, no process spawned, no db opened) | `grep -rlE '^\s*date:\s*[0-9]{4}-[0-9]{2}-[0-9]{2}\s*$' C:\RHACO\docs --include=*.card.yaml \| wc -l` (and the same for `last_human_review:`) against `find C:\RHACO\docs -iname *.card.yaml \| wc -l` | 870 of 1449 cards have an unquoted `date:`; 872 have an unquoted `date:` and/or `last_human_review:` -- roughly 60% of the governed corpus. Cross-check: `RHACO-MTN-20260520-001` (W9's reader target, which PASSES) declares `date: "2026-05-20"` (quoted) -- consistent with the hypothesis that an UNQUOTED date scalar is what triggers the crash, not something specific to REF-typed cards or to v1_8 itself |
| 17 | `db_meta_before == db_meta_after` on every production run | inspected all 12 refreshed `run_summary.json` files (read through `/api/diagnostics`, never by opening the db) | All 12: `db_meta_before == db_meta_after`, `db_bytes=115089408`, `db_mtime_utc="2026-09-04T23:58:11Z"` (unchanged across every run) -- the live index was never touched |
| 18 | `_kb3_verdict` unit tests | `.venv\Scripts\python.exe -m pytest tests/probe/test_workflow_verdicts.py -q` (subset of gate 5) | 4/4 new tests pass (`test_kb3_correct_direction_is_a_clean_pass`, `test_kb3_swapped_direction_is_detected_as_kb3`, `test_kb3_missing_edge_fails_without_attribution`, `test_kb3_unexpected_triple_fails_without_attribution`) |
| 19 | KB3 subprocess test | `.venv\Scripts\python.exe -m pytest tests/probe/test_probe_workflow_subprocess.py -q` (subset of gate 5) | `test_probe_kb3_reverse_edges_fault_subprocess_qualifies` passes; committed ledger byte-identical before/after |

Two additional exploratory runs (against tmp output directories under the OS
temp dir, `C:\Users\kgran\AppData\Local\Temp\kb3_smoke_test` and
`\final_fixture_smoke`, plus `\w5_smoke` and `\w6_smoke`) were made during
development to shake the new runners out before committing to the worktree's
own evidence tree; they are NOT part of the committed evidence (outside the
worktree, never added to git) and are disclosed here only for the reader's
benefit -- every claim in this report is backed by the COMMITTED runs listed
above, re-derived from their JSON, not from the exploratory ones.

## Material alternatives

- **Batching all non-`W7` production presets into one combined run vs. one
  run per preset.** The dispatch's task 5 lists the production presets
  individually ("W1, W2, W3, W4, W5, W6, W7 (`--disable-vec`), W8, W9, W10,
  healthz, diagnostics"), and round 3's own evidence used one run directory
  per preset. Considered combining everything except `W7` into a single
  `--preset W1,W2,...,W10,healthz,diagnostics` invocation (the new
  comma-list feature makes this possible) to save wall-clock time. Rejected
  in favour of one run per preset: once `W6` turned out to genuinely fail,
  a combined run's single `qualification_state`/`verdict` would have gone
  `FAIL` for the WHOLE batch (10 clean presets bundled with the one broken
  one), which is technically still fully inspectable per-preset inside
  `results`, but reads as far weaker evidence than eleven individually clean
  `PRODUCT_EVIDENCE_PASS` runs plus one isolated, unambiguous `W6` `FAIL` --
  exactly the shape that makes the defect easy to cite and impossible to miss.
  The comma-list CLI feature itself was kept (used for the fixture FINAL
  run, deliverable 5's "one fixture run") since there the combined verdict
  IS the desired single piece of evidence ("every preset in PRESET_REGISTRY
  is real and exercised").
- **KB3's detection observable: the CMP<->ANL edge vs. the CMP<->HND edge.**
  The dispatch names the ANL edge specifically ("the campaign_child edge to
  RHACO-ANL-20260115-002 must be..."), so `_run_kb3` locates that one edge by
  searching every `.edge-list`/graph-`<line>` row for one whose
  `data-relation="campaign_child"` and whose `from`/`to` mentions the ANL doc
  id (present on either side, since the fault swaps which side it's on) --
  rather than assuming a fixed row index or hardcoding which bucket
  (outgoing/incoming) to look in, since that bucket is exactly what the fault
  changes. This also lets the SAME lookup logic serve both the clean and
  faulted case unmodified (`_find_campaign_child_to_anl`), which is what makes
  the predicate symmetric and unit-testable per deliverable 7's "missing edge"
  case (`(None, None, None)` when the lookup finds nothing at all).
- **W5's "independent check" scope: `depends_on` -> `campaign_child`, not
  `cites`.** The dispatch's own example phrasing ("a `depends_on` entry
  behind a `cites` edge, or a `parent` behind a `campaign_child`") reads as
  two illustrative alternatives, not a rule that `campaign_child` specifically
  must come from a `parent` field. Verified directly against both the fixture
  (`RHACO-ANL-20260115-002_Fixture_Analysis.card.yaml`'s own comment: "Parent
  fixture campaign -- membership produces a campaign_child edge") and
  production (`RHACO-HND-20260903-001`'s and `RHACO-CHG-20260903-001`'s
  `depends_on` entries, each with an explicit "Parent campaign" note) that a
  `depends_on` entry naming a CMP is exactly what backs a `campaign_child`
  edge in this corpus. Chose two `depends_on`-backed `campaign_child` checks
  over inventing a `cites`-backed example, since the latter would have
  required guessing at the derivation rule for a relation W5 does not
  primarily test, where the former is directly evidenced by both fixture and
  production card text.
- **W6's parent-side check: assert exactly what SCOPE.md row 17 claims, no
  more.** Considered treating the parent's incoming `amends` edge having no
  `<a>` link as a FAIL (a stricter reading of "amendment resolved and
  linked" applied uniformly to both directions). Rejected per the dispatch's
  explicit instruction ("assert only what the SCOPE row says still holds"):
  the row's own claim is bounded to "present, typed, directional, resolved
  -- the click-through is what's missing," so the runner asserts exactly
  that (`known_limitation_reproduced` is recorded as an observation, not
  wired into `custom_reasons` at all) and would only fail if the edge were
  altogether absent or newly marked `unresolved` -- a genuine regression
  from the row's own claim, not the disclosed gap itself.
- **The W6 reader-crash defect: report vs. work around.** Considered
  loosening the reader-navigation assertion (e.g. treating a 500 on
  `reader_v1_8` as an accepted, informational state, the way round 1
  originally tolerated a 404) so W6 would report `PRODUCT_EVIDENCE_PASS`.
  Rejected outright per this round's own governing instruction ("Never
  weaken an assertion, a fault, or a preset to make a run pass... A recorded
  FAIL naming the missing observable is worth more than a green run that
  proves nothing"). The dispatch names `RHACO_Card_YAML_Schema_
  Specification_v1_8` specifically as W6(a)'s target -- not a free choice of
  card -- so there is no substitute target that would sidestep the defect
  while still satisfying the deliverable as written. `explorer/reader/**` is
  outside every path this strand owns, so the fix itself is filed as a
  Change Request (below), not applied here.

## Decisions

- `_run_kb3` and the `_run_kg` Q3 extension both use the new
  `Session.attr_dicts` helper rather than several separate `attr_all` calls
  per field -- reading `data-relation`/`data-edge-from`/`data-edge-to`/
  `data-edge-direction` off the SAME element in one JS round trip guarantees
  the four values actually belong to the same row, which a set of four
  independent `attr_all` calls (each returning a bare list, positionally
  matched by hope rather than by construction) would not guarantee if the
  DOM ever reordered between calls.
- W5's `direction_label` check reads `explorer.models.RELATION_LABELS`
  directly (an import, not a re-derivation) because it is the single
  integrator-owned shared dict every builder module already imports from
  verbatim (`explorer/lineage/service.py` itself does the same) -- unlike
  `HYBRID_DEGRADED_NOTICE_TEXT` above it in this same file, which
  deliberately duplicates a DIFFERENT builder's (corpus_adapter's) own
  literal text so the probe checks an observable contract independently of
  that builder's implementation. Checking a shared, single-source-of-truth
  constant for internal self-consistency (does the lineage module's own
  output agree with the shared label table it is supposed to use) is a
  different kind of check than re-deriving a builder-private string, and the
  file's own precedent (`COMPONENT_RANK_NOT_EXPOSED`) already draws this
  same line.
- W5's page/API edge-set parity check compares `(relation, from_id, to_id,
  direction)` 4-tuples, deliberately excluding `direction_label` from the
  equality set (checked separately, per-edge, against `RELATION_LABELS`)
  and excluding `resolved`/`note`/hop metadata (not rendered as page
  attributes at all) -- so a legitimate difference in fields the page does
  not expose can never register as a false "disagreement."
- W6(b)'s parent-side observations are recorded even though the overall
  preset FAILs on an unrelated step (the v1_8 reader crash) -- `Session`
  accumulates steps across the whole run and `session.goto`'s failure mode
  (an HTTP 500 response, not a Python exception) never aborts the remaining
  steps, so every later `session.goto` call still executes normally. This
  is why Evidence #15 above shows full, correct W6(b) observations sitting
  alongside the W6(a) failure in the very same run.
- The blast-radius check (Evidence #16) uses a plain, read-only `grep`
  over `C:\RHACO\docs\**` -- never an additional uvicorn launch, never
  `RHACO_corpus_index.connect()`, never a raw open of the live db -- to
  characterize how many production cards likely share the defect, without
  violating O12 (probe as the only sanctioned server launcher) or the
  device-safety prohibition's "never open the device on any transport"
  (irrelevant here, no device is touched) / "must not read or write
  `C:\RHACO\data\`" (irrelevant, `docs\` is explicitly a permitted read path
  per working rule 2).

## Result

**Probe module round 4 of 4 -- the last round.** All deliverables 1-8
implemented and exercised:

1. KB3 (`--fault reverse_edges`) is real, unit-tested (`_kb3_verdict`,
   4 tests), subprocess-tested, and `QUALIFICATION_PASS` against the fixture
   (Evidence #8, #18, #19).
2. KG's Q3 typed-edge-direction extension is real and passes cleanly as part
   of the FINAL fixture run (Evidence #9, #10).
3. W5 (production, `RHACO-CMP-20260903-001`) is real and
   `PRODUCT_EVIDENCE_PASS` (Evidence #13), including its independent
   disk-based check of two resolved edges (both `VERIFIED`, no
   `UNVERIFIED`s needed).
4. W6 (production, two centres) is real and fully exercised, but its
   `qualification_state` for this run is `FAIL` -- one specific, well-isolated,
   root-caused defect in `explorer/reader` (Evidence #14, #15, #16; Change
   Request below), not an incompleteness in the probe itself. Every OTHER
   assertion task 4 names (the banner, the chain, the replacement edge, the
   amendment's outgoing edge, and the SCOPE.md row 17 parent-side check) is
   verified and correct.
5. The FINAL suite is complete: one fixture run
   (`docs/probe-qualification/runs/20260905T043117Z`) exercises the complete
   known-good set (`KG`) plus all five known-bad classes (`KB1`-`KB5`) and is
   `FRAMEWORK_SMOKE_PASS`; the production acceptance set (`W1`-`W10`,
   `healthz`, `diagnostics`) was refreshed at this commit across twelve
   individual runs (Evidence #11-#14). **No preset in `PRESET_REGISTRY` is
   `not_implemented_yet`** -- every one of the 17 presets now has a real
   runner. The qualification ledger holds **KB1, KB2, KB3, KB4, KB5** (all
   five).
6. W10 already covered the new surfaces going into this round (round 2's
   `_run_w10` visits catalog, search, reader, and diagnostics and runs
   `_w10_localhost_check` over every recorded request) -- this round added no
   lineage navigation step to W10 because task 6 was already discharged by
   the wave-2 implementation and nothing in this round's own deliverables
   asked for a second W10 change; re-verified green in Evidence #11 at this
   commit with no code change needed.
7. `tests/probe/`: 4 new `_kb3_verdict` unit tests (correct direction,
   swapped direction, missing edge, unexpected triple) plus the KB3
   subprocess run, asserting `QUALIFICATION_PASS` and the tmp ledger gaining
   KB3 (Evidence #18, #19). Every existing probe test stays green (252/252
   total, Evidence #5). Module docstring VERSION HISTORY gained v1.3;
   `docs/probe-qualification/README.md` updated per deliverable 8.

Gates: (a) ruff clean, (b) 252/252 pytest, (c) L1 index-write check PASS
(Evidence #4-#6). Worktree left clean after commit; `git rev-parse HEAD`
recorded in the structured result.

## Unresolved uncertainty

- **W6's production `qualification_state` is `FAIL`, not `PRODUCT_EVIDENCE_
  PASS`, because of a genuine `explorer/reader` defect this round discovered
  (not a probe defect).** Root cause (Evidence #14): `explorer/reader/
  service.py`'s `_parse_card_yaml` calls `yaml.safe_load(raw_text)` directly
  and stores the result verbatim as `card_parsed`; when a `.card.yaml`'s
  `date` (or `last_human_review`) field is an UNQUOTED ISO date scalar (e.g.
  `date: 2026-06-24`, as `RHACO_Card_YAML_Schema_Specification_v1_8.card.yaml`
  has), PyYAML resolves it to a native `datetime.date` object rather than a
  string; `explorer/reader/templates/reader/reader.html`'s `{{ view.card_parsed
  | tojson(indent=2) }}` then calls Python's stdlib `json.dumps` with no
  custom `default=` handler, which raises `TypeError: Object of type date is
  not JSON serializable`, producing an unhandled HTTP 500 with no page body
  the probe's `data-selected-doc-id` check can find. This is fully reproduced
  and traceback-confirmed (server.log, Evidence #14), not merely suspected.
  Severity (Evidence #16): a read-only grep across `C:\RHACO\docs\**` finds
  870 of 1449 `.card.yaml` files (roughly 60% of the governed corpus) declare
  an unquoted `date:`, and 872 declare an unquoted `date:` and/or
  `last_human_review:` -- so this almost certainly crashes the reader for the
  majority of the corpus, not just this one card. This is disclosed here and
  as a Change Request below rather than fixed, since `explorer/reader/**` is
  outside every path this strand owns (working rule 1) and this is the
  probe's LAST round -- there is no probe round left to re-verify a fix even
  if one landed. This does **not** require a fifth PROBE round: the probe
  itself is complete, real, and correctly reports the defect; what remains is
  a reader-module fix and a reader-owning strand's re-verification, which is
  the build's concern, not the probe's.
- **W3's oracle-order comparison (`PRODUCT_W3_ORACLE_ORDER`) is a frozen
  constant from `gold_v1_1_compat.json` row 21, carried over unchanged from
  round 2/3.** It passed cleanly again this round (Evidence #11), but as
  before it is a point-in-time snapshot of the hybrid retrieval's ordering on
  a live, evolving corpus; a future corpus change could shift this order
  again the way SCOPE.md row 16 already documents happened once. Not
  re-investigated this round (out of this round's task scope), disclosed as
  a standing condition, not a new one.
- **The Q3 lineage contract's `data-lineage-state` attribute** (named in this
  round's dispatch as part of "the lineage contract you will drive") is,
  per direct inspection of `explorer/lineage/templates/lineage/lineage.html`,
  present ONLY on the `adapter_absent` branch (`data-lineage-state=
  "adapter-absent"`) -- there is no `data-lineage-state` value for the normal
  rendered-view state or the `not_found` state. None of this round's
  deliverables actually required reading this attribute in the normal-view
  case (every KG/KB3/W5/W6 check uses `.edge-list`, the graph `<line>`
  elements, `.supersession-chain`, `.reasoning-trail`, or `/api/lineage`
  instead), so this did not block anything, but it means the dispatch's
  contract summary is broader than what the shipped template actually
  carries. Filed as a minor Change Request below (documentation-only, no
  runner depends on the missing states).
- **KB3's fault-detection is exercised only via the CMP -> ANL edge** (the one
  the dispatch names explicitly). The SAME fault also swaps the reciprocal
  `cites` edges (CMP's incoming `cites` from HND/ANL flip to outgoing, per
  `tests/lineage/test_faults.py`'s own second test) and the CMP -> HND
  `campaign_child` edge, but `_run_kb3` does not independently re-derive or
  assert those additional swaps (only the one edge task 1 specifies).
  `_kb3_verdict` itself is generic (any triple), so extending `_run_kb3` to
  check the other swapped edges would be a small addition, but it is not
  something this round's deliverable asked for and is left as a possible
  future strengthening rather than invented scope.

**Nothing above requires a fifth probe round.** The probe module's own job --
implement every remaining preset for real, run the FINAL suite, and refresh
the production acceptance set -- is complete. The one substantive finding
(W6's reader defect) is a discovery ABOUT the product, made possible BECAUSE
the probe is now complete; addressing it is a reader-module concern for the
integrator to schedule, not unfinished probe work.

## Change requests

1. **Requestor:** probe (B10). **Affected contract/path:**
   `explorer/reader/service.py` (`_parse_card_yaml`, `yaml.safe_load`) and/or
   `explorer/reader/templates/reader/reader.html` (the `{{ view.card_parsed |
   tojson(indent=2) }}` dump). **Change:** either (a) pass a JSON encoder with
   a `default=` handler that stringifies `datetime.date`/`datetime.datetime`
   objects before the Jinja `tojson` filter runs (e.g. pre-serialize
   `card_parsed` through a small recursive stringify pass in `_parse_card_yaml`
   or `build_view`, converting any `date`/`datetime` leaf to its ISO string),
   or (b) load the YAML with a loader that never auto-resolves date-like
   scalars to native types (e.g. a `SafeLoader` subclass with the date/timestamp
   implicit resolvers removed) so every field's parsed type matches what a
   human reading the card would expect (a string). **Evidence:** this round's
   report, Evidence #14/#16 and "Unresolved uncertainty" above -- reproduced
   directly (full traceback in `docs/probe-qualification/runs/
   20260905T043147Z/server.log`, lines 109-127) via the probe's own sanctioned
   server launch against the live index, for the exact card task 4(a) names.
   **Compatibility impact:** additive/corrective only -- every currently-passing
   card (one with quoted or no date fields) is unaffected; only currently-
   crashing cards (roughly 60% of the corpus per the grep) would start
   rendering. **Migration:** none required in the corpus itself (the fix is
   code-side); a corpus-side alternative (quoting every unquoted `date`/
   `last_human_review` field) would also work but is a much larger,
   unnecessary edit across ~870 files for a defect the code side can absorb
   in one place. **Invalidated tests/probes:** none identified -- no existing
   reader test opens a card with an unquoted date (this is exactly why the
   defect went undetected through three prior rounds); W6 gains real
   evidence once fixed, at no additional probe budget (re-running `--preset
   W6` costs nothing once landed).
2. **Requestor:** probe (B10), carried forward from R03_lineage's own change
   request (SCOPE.md row 17) -- not a new finding, cited here only because
   this round is the first to exercise it against PRODUCTION data end to end.
   `docs/probe-qualification/runs/20260905T043147Z/W6.json`'s
   `parent_incoming_amends_link=None` / `known_limitation_reproduced=true`
   confirms the production behavior matches the fixture-derived row exactly;
   no new action requested beyond what SCOPE.md row 17 already tracks.
3. **Requestor:** probe (B10), documentation-only. **Affected contract/path:**
   this round's own dispatch prompt's lineage-contract summary (not a code
   path) and, optionally, `explorer/lineage/templates/lineage/lineage.html`.
   **Change:** either narrow the "the page carries `data-lineage-state`"
   contract line in a future dispatch to say explicitly that it is present
   only on the `adapter_absent` branch (matching what ships today), or add
   `data-lineage-state="ok"` / `"not-found"` values to the two other render
   branches so the attribute is actually present on every state as the
   summary implies. **Evidence:** direct inspection of
   `explorer/lineage/templates/lineage/lineage.html` (grep for
   `data-lineage-state` finds exactly one occurrence, line 21, inside the
   `adapter_absent` block). **Compatibility impact:** none either way -- no
   probe runner this round or previously reads this attribute in the normal-
   view or not-found states. **Migration:** none. **Invalidated tests/probes:**
   none.

## Assumptions

- "One fixture run exercising the complete known-good set plus all five
  known-bad classes" (task 5) is read as one `--preset KG,KB1,KB2,KB3,KB4,
  KB5` invocation (the new comma-list CLI feature), separate from "the
  production acceptance set W1-W10 with healthz and diagnostics," which the
  same sentence's second half and the following sentence ("Refresh the
  production runs... W1, W2, ..., diagnostics") describe as the individually
  enumerated production refresh -- i.e. two distinct deliverables bundled
  under one "FINAL suite" heading, not one single run spanning both fixture
  and production substrates (which is structurally impossible: KG/KB1-KB5
  navigate fixture-only card refs that do not exist in the live corpus).
- W5's "independent check" (task 3) is satisfied by two `depends_on`-backed
  `campaign_child` edges rather than a `cites`-backed example, per "Material
  alternatives" above -- both are genuinely declared-on-disk relations, and
  the task's own phrasing offers either as an acceptable example, not a
  requirement to use one specifically.
- W6(b)'s "outgoing amends edge to the parent id, resolved and linked" (task
  4b) is read as applying to the AMENDMENT's own page (where the edge is
  genuinely outgoing and does resolve to a link, per Evidence #15) -- the
  PARENT's own page's INCOMING amends edge is governed instead by the
  separate "known, dispositioned limitation" sentence immediately following
  it in the same task item, which explicitly scopes what must and must not
  be asserted there.
- The two `/tmp`-prefixed exploratory run directories used during development
  (Evidence's closing paragraph) are read as falling outside "do not edit,
  rename or delete any existing run directory under `docs/probe-qualification/
  runs/`" (working rule 1) since they were never written under that path in
  the first place -- they live under the OS temp directory, not the
  worktree, and were never `git add`ed.
