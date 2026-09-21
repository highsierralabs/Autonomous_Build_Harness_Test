# RHACO Build Prompt Template Guide — Running the Self-Verifying Build Prompt

*Reference Document | Version 2.0 | September 7, 2026*
*Companion to: RHACO_Build_Prompt_Template_v2_0*

Structure credited to `rawprogress/fable-cities` (accessed 2026-09-03; see the template's provenance block). Wording, generalisation and the v2.0 additions are RHACO's; the additions are drawn from one run (RHACO-CMP-20260903-001, n = 1) and are structural, not performance claims.

## 1. What this prompt is

A single instruction that turns an agentic coding tool into a small organisation: builders who own folders, one integrator who owns core and every shared thing, critics who score against an external reference and write no code, a claim auditor who reads prose against artifacts, and a persisted state file the whole thing loops on until it declares one of four terminal states.

Three components carry most of the value. If you adopt nothing else, adopt these:

1. **A qualified probe the builder must run before saying "done"**, whose output the critic can look at, and which has been shown to fail on known-bad cases.
2. **A separate critic** that never touches code and scores against something outside the project.
3. **A separate claim audit** that reads every prose behaviour claim against the artifact it describes. Without it the harness produces true code and false prose about it, and cannot see that it is doing so (RHACO-ANL-20260905-001 section 6.2).

Everything else (waves, integrator, blind gate, state file) reduces cost and thrash.

## 2. When to use it — and when not

Use it when all of the following hold: the deliverable splits into 8–15 subsystems with real interfaces; a script can produce an inspectable artefact from the current build (screenshot, rendered page, benchmark table, golden diff, test report); a concrete external reference exists to score against; you can afford the budget — the source project consumed ~20M output tokens across six runs and did not clear its own bar; the RHACO run consumed 20 of 28 builder rounds and ended BOUNDED_FAIL.

Do not use it for single-module tasks, for outputs judged only subjectively with no comparable artefact, or where "keep going without asking" is unacceptable — unless the gated or reviewed human-gate policy (section 6) is selected.

## 3. Filling the slots

Work top to bottom. Slots marked ★ determine whether the harness functions at all.

### Goal block

| Slot | What goes in it | Weak | Strong |
|---|---|---|---|
| `TARGET_CLASS` | A named external product/standard the output is measured against | "a good city builder" | "a Cities: Skylines II–class city builder" |
| `STACK` | Language, framework, build tooling, module system | "JavaScript" | "Three.js (latest) + Vite, plain ES modules" |
| `QUALITY_BAR` | 3–6 observable properties | "high quality" | "PBR materials, plausible sun/sky/shadows, believable traffic" |
| `ANTI_PATTERN` | The one thing that fails the project on sight | "bugs" | "programmer art" / "hand-written SQL in handlers" |

### Architecture block

| Slot | Notes |
|---|---|
| `KNOWN_CONSTRAINTS` | Every limit of stack, runtime, data, budget and authority; each becomes a CONSTRAINTS.md row with basis, design consequence and user-visible limitation. |
| `MODULE_LIST` | 8–15 nouns. Each becomes a folder, a builder, a showcase mode, a critic target. Group by data ownership. |
| `CORE_DATA_MODEL` | The one shared schema. Only the integrator edits it. |
| Shared things | Name every shared block (markup, vocabulary, contract) in ARCHITECTURE.md with its owner. The RHACO run's integrator crossed ownership lines three times, every time because a shared thing had no owner by rule. |
| `UNITS_AND_CONVENTIONS`, `DETERMINISM_POLICY`, `PERF_BUDGET`, `ASSET_DATA_POLICY` | As before. PERF_BUDGET numbers appear in PROBE_LOG_FIELDS so the critic sees them without trusting the builder. |

### ★ Verification block

Your `PROBE_OUTPUT` must pass one test: **is it directly comparable to `REFERENCE_CORPUS`, and can a second agent inspect it without running the build?**

| Domain | `PROBE_ACTION` | `PRESET_KIND` | `PROBE_OUTPUT` | `PROBE_LOG_FIELDS` | `KNOWN_BAD_CLASSES` |
|---|---|---|---|---|---|
| Web/3D app | load in headless browser | camera + time of day / route + viewport | PNG | console errors, fps, draw calls | missing asset; wrong shader; stalled frame |
| Data pipeline | run on fixture set F | fixture + config profile | golden-output diff, summary stats | exit code, stderr, wall time, peak RSS, schema validation | wrong join; dropped rows; stale schema |
| HTTP service | boot, run golden request set | request set + load profile | response diff, latency histogram | 5xx count, p50/p95/p99 | wrong record for key; stale cache; auth bypass |
| Document generator | render to PDF/HTML | page + viewport | rendered page image | lint errors, broken links | missing section; wrong cross-ref; overflow |
| Corpus explorer (RHACO run) | drive the local app | preset + retrieval mode | screenshot + JSON observations | console errors, failed requests, result ids | wrong doc for id; stale card; reversed edge; broken jump; runtime error |

`PROBE_ROUNDS`: the per-module MAX_ROUNDS plus one per wave that adds a surface. In the RHACO run the probe spent three of four rounds before the surface it had to qualify existed.

Fault predicate: the probe FAILs on any bound violation, missing capture, or non-empty error channel. The RHACO run's first probe returned `ok: true` on a 404 with a console error because `ok` meant "captured".

Fixtures: derive from the production corpus's loader-resolved types; census fixture-vs-production types at round 0. The RHACO run's hand-authored fixture quoted every date; 60% of the live corpus did not, and four green rounds could not see the crash.

### Orchestration block

| Slot | Notes |
|---|---|
| `ORCHESTRATION_MECHANISM` | Name what exists in your environment. Sequential waves preserve the critic/builder separation, which is the part that matters. |
| `WAVE_1/2/3_MODULES` | Wave 1: no upstream dependencies (include the probe and the diagnostics surface). Wave 2: consumes wave-1 APIs. Wave 3: integration. |
| `CORE_PATH` | Integrator-only. |
| Dispatch discipline | Every dispatch is recorded in STATE_FILE before the strand returns (three RHACO strands ran with no record and were reconstructed after the fact). Text carried verbatim into a dispatch is diffed against its archive at dispatch time (a retyped apostrophe drifted one dispatch). A proposed control is shown executable on the surface that will run it before it is recorded (a Workflow script had no filesystem access). Generated prompt boilerplate carries no round-specific or self-referential literal (a hard-coded `R02_` told later rounds to overwrite an earlier report). |

### ★ Critic and audit block

| Slot | Notes |
|---|---|
| `CRITIC_PERSONA` | A named professional role with a reputation to protect and no stake in the code. "Writes no code" removes the incentive to defend anything. |
| `REFERENCE_CORPUS` | Real, external, concrete, with provenance in REFERENCE.md. |
| `CALIBRATION_ARTIFACTS` | Three things of known quality. Without them the scale is ordinal: say so in SCOPE.md and never read PASS from it. |
| `ANCHOR_10 / 8.5 / 7 / 5` | Each recognisable from the probe output alone. |
| `PASS_THRESHOLD` | Aspirational (drives quality, expect to fail) or achievable (drives closure). State which. |
| `ZERO_TOLERANCE_CONDITION` | Zero console errors / failing tests / schema violations. |
| `MAX_ROUNDS` | 3–5. Past that the fix is a contract change, not another round. |
| Claim audit (5a) | A separate agent after each merge. State in LAYERS.md which claim classes have a mechanical grammar (a citation auditor, a docstring-vs-signature check) and which remain a reader's. Every prose behaviour claim ends up with a named check or an `UNVERIFIED` tag. |

### Authority and identity block

| Slot | Notes |
|---|---|
| `SUBSTRATE_PATHS` | The corpus, database, service or repository the artifact reads and must never write. Verified by a closeout hand with hashes, never asserted by the build. |
| `PROTECTED_CONTRACTS` | CORE_DATA_MODEL, public APIs, the accepted default configuration of any upstream system. |
| `IDENTITY_SURFACES` | Config-file sha + model key; system-prompt model sentence; per-request model field as a family check. In the RHACO run a client safeguard swapped the orchestrator's model mid-session on the build's own fault-injection vocabulary, the system prompt still named the old model two changes later, and the per-request field stripped the context-window suffix — no single surface would have caught it. Set the client's switch behaviour to halt. |

### Rules block

| Slot | Notes |
|---|---|
| `LIVE_CONDITION` | Dev server up; fixtures runnable from clean checkout; main green. |
| `HUMAN_GATE_POLICY` | Section 6. |

## 4. State file schema

```json
{
  "run": 7,
  "updated": "2026-09-07T02:00:00Z",
  "client": { "identity_of_record": {"config_sha": "...", "model": "...", "effort": "..."},
              "history": [ {"round": 6, "config_sha": "...", "model": "...", "prompt_model": "...", "request_model": "..."} ] },
  "dispatch_records": [ {"strand": "S3-B1", "role": "builder", "model": "...", "effort": "...", "pattern": "...",
                          "agent_type": "...", "execution_mode": "concurrent", "dispatched_utc": "...", "returned_utc": null} ],
  "modules": {
    "terrain": { "ref_gap": 8.1, "round_delta": 0.4, "iso_vs_integrated": 0.0, "rounds": 3, "status": "open",
                 "issues": ["LOD pop at 400 m"], "unverified": ["fits 1280 px as rendered — no browser in strand"] },
    "sky":     { "ref_gap": 8.6, "round_delta": 0.1, "iso_vs_integrated": 0.0, "rounds": 2, "status": "pass", "issues": [], "unverified": [] }
  },
  "integrator_queue": ["roads -> core: add lane-count to RoadSegment"],
  "assumptions": ["Using metres, +Y up per ARCHITECTURE.md 2"],
  "layer_gaps": [ {"found_by": "L3", "missed_by": "L2", "item": "..."} ],
  "claim_audit": { "last_run": "...", "match": 169, "mismatch": 0, "unverifiable": 8 },
  "final_gate": { "whole_ref_gap": null, "blind_ab": [] },
  "terminal_state": null
}
```

`unverified` entries are never deleted by the integrator; they are retired only by a cited check. "Resume from the weakest module" is `min(ref_gap)` over `status == open`. The "never inflate" rule applies to this file first.

## 5. Running it

1. Fill every slot. Grep for `{{` — zero hits before launch.
2. Delete the guidance comments; they cost tokens on every turn. v2.0 is roughly twice the length of v1; budget for it.
3. Start from an empty folder.
4. Expect the first run to end at a usage limit partway through wave 1; the state file makes run 2 cheap.
5. Read `ARCHITECTURE.md` after the first run and before the second — the cheapest point to correct.
6. Read the critic and claim-audit outputs raw. Rounds where scores go down are the signal that the critic is working; a claim audit that finds nothing on a fresh tree is the signal that it is not.
7. When a module hits `MAX_ROUNDS` without passing, do not add rounds. Look for a contract problem and route it through the integrator.
8. At every round boundary, read the identity surfaces before reading anything else.

## 6. Human-gate policy

- **Autonomous.** Assumptions land in the state file for post-hoc review. Suitable when the cost of a wrong routine decision is a redo, not a loss.
- **Gated.** Autonomous except for Authority-boundary items. Recommended default for anything you will maintain.
- **Reviewed.** Nothing starts a new wave until a human ratifies the previous state file. Appropriate when outputs feed a governed record or a two-instance workflow with a human ratifying authority between instances.

Pick one and delete the others.

## 7. Cost and threshold calibration

Source project: six runs, ~20M output tokens, best module 2.5 points below the 8.5 bar, blind judging lost every round. RHACO run: one run, 20 of 28 rounds, nine objective gates PASS, 11 of 12 presets, BOUNDED_FAIL on an uncalibrated scale and an unconverged claim class. Both harnesses produced honestly-scored results; neither met its own goal. Budget by wave; if closure matters more than ceiling, set `PASS_THRESHOLD` where a strong module lands on round 2 and let the anchors carry the quality signal; check the reference corpus before lowering the bar.

## 8. Failure modes to watch

| Symptom | Likely cause | Fix |
|---|---|---|
| Every module passes round 1 | Critic is scoring the builder's description, not the probe output | Enforce "critic runs its own probe"; check `PROBE_OUTPUT` is inspectable |
| Probe green, product broken on real data | Fixture reproduces the authors' conventions | Derive the fixture from loader-resolved production types; type census at round 0 |
| Docstrings, notices and design docs disagree with the code | No layer reads claims against referents | Run the claim audit after every merge; tag or check every prose claim |
| A builder's "unverified" vanishes at integration | State schema has no first-class UNVERIFIED | Add it; integrator may retire only with a cited check |
| Scores oscillate without converging | Contract problem disguised as a quality problem | Route through integrator; freeze the API |
| Integrator editing builder folders | Shared things with no owner by rule | Assign in ARCHITECTURE.md; contract test per shared block |
| Critic scores drift between rounds | Anchors not specific, or scale uncalibrated | Calibrate on known artifacts; freeze anchor text |
| Model or effort changed and nobody noticed | Identity read from one surface, or client set to retry | Read the conjunction each round; set the client to halt |
| Blind judge always picks the reference | Expected for a novel build | Track margin over runs |
| Agent asks questions despite autonomous policy | Slot left vague | Fill it |

## 9. Minimal worked instance (non-visual)

- `TARGET_CLASS`: "a dbt-class transformation layer"
- `PROBE_TOOL`: `tools/probe.py`, runs the DAG on `fixtures/small/` (derived from production types) and `fixtures/skew/`
- `PROBE_OUTPUT`: golden-output diff + summary-stats table per model
- `PROBE_LOG_FIELDS`: exit code, stderr, wall time, peak RSS, schema-validation result
- `KNOWN_BAD_CLASSES`: wrong join key; dropped rows; stale schema; silent null coercion
- `REFERENCE_CORPUS`: a published dbt project of comparable scope and its documented outputs (provenance in REFERENCE.md)
- `CRITIC_PERSONA`: principal data engineer doing a production-readiness review, writes no code
- `ANCHOR_8_5`: "all models idempotent, documented, tested; diff vs. golden empty; one reviewer nit per model"
- `SUBSTRATE_PATHS`: the warehouse schemas the layer reads
- `IDENTITY_SURFACES`: client config sha + model key; system-prompt sentence; per-request model
- `ZERO_TOLERANCE_CONDITION`: zero failing tests, zero schema violations
- `LIVE_CONDITION`: `make probe` runs green from a clean checkout

## 10. Pre-launch checklist

- [ ] No `{{` remains
- [ ] `PROBE_OUTPUT` and `REFERENCE_CORPUS` are the same medium
- [ ] Critic can run the probe without the builder's help
- [ ] `KNOWN_BAD_CLASSES` enumerated; each asserts on a rendered observable
- [ ] `PROBE_ROUNDS` budgeted separately from module rounds
- [ ] `CALIBRATION_ARTIFACTS` named, or the scale declared ordinal in SCOPE.md
- [ ] `REFERENCE.md` provenance fields planned (source, version/date, access date, properties compared)
- [ ] Claim-audit grammar boundary stated in LAYERS.md
- [ ] `SUBSTRATE_PATHS` named; closeout hand assigned
- [ ] `IDENTITY_SURFACES` named; client switch behaviour set to halt
- [ ] Every shared thing has an owner in ARCHITECTURE.md
- [ ] One human-gate policy selected, others deleted
- [ ] `ORCHESTRATION_MECHANISM` names something that exists in this environment
- [ ] `STATE_FILE` path exists and is git-tracked; dispatch records written before strands return
- [ ] Token budget for wave 1 estimated and acceptable

---

## Version History

| Version | Date | Notes |
|---|---|---|
| 2.0 | 2026-09-07 | First filed version, companion to Template v2.0. Adds the claim audit as the third core component, the known-bad-classes / probe-rounds / substrate / identity slots, the state-file schema with three numbers, UNVERIFIED, dispatch records and identity history, dispatch discipline, and five failure-mode rows drawn from the RHACO-CMP-20260903-001 run. Cut by RHACO-CHG-20260907-002. |

---

*Reno High-Altitude Cosmic Ray Observatory (RHACO) | Kris E. Granholm, Director*
