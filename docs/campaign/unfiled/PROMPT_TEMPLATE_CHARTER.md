# PROMPT_TEMPLATE_CHARTER.md — Self-Verifying Build Prompt, Charter-Aligned

Rewrite of `PROMPT_TEMPLATE.md` against RHACO_Measurement_Philosophy_v1_4_1. Each section names the principle it operationalizes (P1–P7; "GL" = parked candidate *Grounding Against the Literature*). The harness structure from `rawprogress/fable-cities` is retained where it already satisfied a principle and altered where it did not. Fill every `{{SLOT}}`; delete `<!-- -->` comments before use.

---

# Goal

Build a {{TARGET_CLASS}} in {{STACK}}, from this empty folder.
The bar is {{QUALITY_BAR}}. Never {{ANTI_PATTERN}}.

Wherever a choice exists between the easier path and the more rigorous path, take the rigorous path. Where rigor is impossible, name the limitation in `SCOPE.md` (see step 7) rather than working around it silently.

# How to work

## 1. Constraints first, then architecture. *(P1 Architectural Acceptance)*

Before any feature code, write `CONSTRAINTS.md`: every known limitation of {{STACK}}, the runtime, the data sources, and the budget — {{KNOWN_CONSTRAINTS}}. Each constraint is an **input to the design**, not an obstacle. Where a constraint suppresses the obvious approach, the design lives downstream of the constraint in what remains uncorrupted. Do not fight a constraint with a workaround that pretends it is absent; if a constraint is later removed, that is an explicit, versioned event with its own validation.

Then write `ARCHITECTURE.md`:
- one folder per subsystem: {{MODULE_LIST}}
- a shared {{CORE_DATA_MODEL}} every module reads from and writes to
- the public API each module exposes and the events it emits
- conventions: {{UNITS_AND_CONVENTIONS}}
- determinism: {{DETERMINISM_POLICY}}
- performance budget: {{PERF_BUDGET}}
- asset/data policy: {{ASSET_DATA_POLICY}}
- for every non-obvious design decision: the alternatives considered and why each was rejected, with specific reasoning *(P6)*

Isolate module failures so one broken module never takes the whole {{ARTIFACT_NOUN}} down.

<!-- KNOWN_CONSTRAINTS: e.g. "no WebGPU on target browser; 4 GB RAM ceiling; API rate limit 60/min; reference dataset has 30-min cadence only". These become the first entries in SCOPE.md. -->

## 2. The artifact observes itself. *(P2 The Instrument Observes Itself)*

Build the verification loop before the {{ARTIFACT_NOUN}}. Write `{{PROBE_TOOL}}`: a headless tool that {{PROBE_ACTION}}, waits until ready, applies a named {{PRESET_KIND}}, and writes {{PROBE_OUTPUT}} plus a JSON log containing {{PROBE_LOG_FIELDS}}.

**The probe must exercise the production path.** No mocks, stubs, fixtures-only branches, or instrumentation-only code paths: the probe observes the same build, the same data flow, and the same rendering or execution path the deliverable uses. Health telemetry ({{PROBE_LOG_FIELDS}}) is derived from that same stream, not from a separate monitoring layer with its own failure modes. If the probe is wrong about the artifact, it must be wrong for the same reasons the artifact is wrong — that coupling is the point.

Every module ships a **showcase mode** that stages a representative minimal instance of just that module through the production code, so it can be probed in isolation.

**No agent may claim anything it has not run the probe on and inspected.**

## 3. Four independent verification layers. *(P3 Layered Self-Filtering)*

The build is checked by four layers that can each fail without compromising the others. Each carries its own version and its own validation criteria in `docs/LAYERS.md`.

| Layer | Mechanism | Catches | Independent of |
|---|---|---|---|
| L1 Static | {{STATIC_CHECKS}} — types, lint, contract/schema validation, run on every commit | Contract violations before anything executes | Whether the probe or critic runs at all |
| L2 Probe | `{{PROBE_TOOL}}` per step 2, run by the builder | Runtime failures, budget violations, visibly wrong output | Builder's description of the work |
| L3 Critic | Separate agent per step 5, runs its own probes | What the builder saw and rationalized | Builder's incentives |
| L4 Blind gate | External judge per step 6, sees only A/B artifacts | What the critic has grown used to | The whole project's frame of reference |

A finding surfaced by a lower layer that a higher layer missed is logged as a layer-3/4 gap in `{{STATE_FILE}}`, not silently absorbed. Upgrades stay local to one layer.

<!-- STATIC_CHECKS: e.g. "tsc --strict, eslint, JSON-schema validation of the core data model, folder-ownership check". -->

## 4. Fan out. *(P3 structural; unchanged)*

Use {{ORCHESTRATION_MECHANISM}}. One builder agent per module, owning only its folder. Waves ordered by dependency:
- Wave 1: {{WAVE_1_MODULES}}
- Wave 2: {{WAVE_2_MODULES}}
- Wave 3: {{WAVE_3_MODULES}}

Between waves, exactly one **integrator agent** — the only agent allowed to touch `{{CORE_PATH}}` — applies builders' core-change requests and fixes the seams. Every accepted core change is recorded with the request, the alternatives, and the reason the integrator chose as it did *(P6)*.

## 5. Differential critic. *(P4 Differential Measurement; GL; P5)*

After each builder round, a separate **critic agent** — {{CRITIC_PERSONA}}, who writes no code — runs its own probes across several {{PRESET_KIND}} values, checks the API contract and {{PROBE_LOG_FIELDS}}, and scores each module.

**Scoring is differential, not absolute.** The critic produces three numbers per module per round:
- `ref_gap`: distance from {{REFERENCE_CORPUS}} on the anchored 0–10 scale — 10 = {{ANCHOR_10}}, 8.5 = {{ANCHOR_8_5}}, 7 = {{ANCHOR_7}}, 5 = {{ANCHOR_5}}
- `round_delta`: change since the previous round on the same presets — the quantity that shows whether the builder is converging, oscillating, or thrashing, which the absolute score buries
- `iso_vs_integrated`: showcase-mode score minus integrated-mode score — a non-zero value is a seam problem for the integrator, not a module problem for the builder

**The reference corpus carries provenance.** Before scoring, the critic records in `docs/REFERENCE.md` what {{REFERENCE_CORPUS}} is, where each item was obtained, its version or date, the access date, and which specific properties are being compared. A reference without provenance is not a reference. *(GL)*

**Anchors are calibrated empirically.** Before wave 1 completes, the critic scores three known artifacts — {{CALIBRATION_ARTIFACTS}} — and records the results in `docs/REFERENCE.md`. If the anchors do not reproduce on known artifacts, rewrite the anchors, not the scores. Thereafter the anchor text is frozen for the run. *(P5)*

Pass = `ref_gap` ≥ {{PASS_THRESHOLD}} with {{ZERO_TOLERANCE_CONDITION}}. Below that, the builder receives the ranked issue list and goes again, up to {{MAX_ROUNDS}} rounds. A module that reaches {{MAX_ROUNDS}} with `round_delta` ≈ 0 is escalated to the integrator as a suspected contract problem, not given more rounds.

<!-- CALIBRATION_ARTIFACTS: three things whose quality is already known — e.g. "the reference itself (should score 10), a deliberately degraded copy (should score ~5), an existing open-source equivalent of known quality". If no such artifacts exist for your domain, say so in SCOPE.md and drop the calibration step rather than fake it. -->

## 6. Blind final gate. *(P4; unchanged in mechanism)*

A whole-{{ARTIFACT_NOUN}} critic scores {{END_TO_END_TARGET}} with the same three numbers. Then **blind judges** receive pairs of probe outputs labelled only A and B (ours vs. {{REFERENCE_CORPUS}}, order shuffled) and state which is better and why. Report the margin per round; a loss with narrowing margin is a result, not a failure to report.

## 7. Honest scope. *(P7 Honest Scope)*

Maintain `SCOPE.md` from the first commit. It lists, as a normative table: every capability the {{ARTIFACT_NOUN}} does **not** provide, its status, and the path to addressing it if one exists. Seed it from `CONSTRAINTS.md`. Any claim in a report, README, or status that lies outside this table must cite the module or probe result that supports it; any claim inside it must state the limit explicitly. A capability leaving the table is a versioned event with its own validation criteria. Unmet bars — including a `PASS_THRESHOLD` never reached — are recorded here at the end of every run, plainly.

## 8. Reasoning as artifact, then loop. *(P6 Reasoning as Artifact)*

Persist to `{{STATE_FILE}}`: per-module `ref_gap`, `round_delta`, `iso_vs_integrated`, round count, open issues, and assumptions made. Every critic report and every blind-judge response is stored unedited under `docs/critique/`, including rounds where scores went down. Every builder round produces a short `docs/rounds/{{module}}-{{n}}.md` stating what was tried, what was rejected and why, and which probe outputs the claims rest on.

Loop until every critic passes or `SCOPE.md` records why it cannot. Each iteration resumes from the module with the largest `ref_gap`, not from scratch.

# Rules

- Never inflate scores. Report real numbers, failed rounds, negative deltas, and what is still missing. *(P7)*
- Never edit another module's folder. Core changes go through the integrator and are recorded with reasoning. *(P6)*
- Never probe through a mock. If the production path cannot be probed, that is a `SCOPE.md` entry, not a reason to probe something else. *(P2)*
- Never claim a comparison against a reference whose provenance is not in `docs/REFERENCE.md`. *(GL)*
- Keep {{LIVE_CONDITION}} at all times; other agents are probing it.
- {{HUMAN_GATE_POLICY}}

<!-- HUMAN_GATE_POLICY — recommended default under P6, since ratification is itself part of the reasoning record:
     "Make routine decisions yourself and log assumptions and rejected alternatives to STATE_FILE and docs/rounds/. Stop and request ratification before: changing CORE_DATA_MODEL, changing any public API contract, changing anchor text after calibration, changing PASS_THRESHOLD, or removing a SCOPE.md entry. Otherwise keep going."
     Fully autonomous and fully reviewed variants remain valid choices; state which one is in force. -->

Start now.
