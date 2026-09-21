# RHACO Build Prompt Template — Self-Verifying Build Prompt

*Reference Document | Version 2.2 | September 20, 2026*
*Companion to: RHACO_Build_Prompt_Template_Guide_v2_2, RHACO_Measurement_Philosophy_v1_4_1*

---

## Provenance and lineage

Structure derived from `rawprogress/fable-cities` — `https://github.com/rawprogress/fable-cities/blob/main/PROMPT.md`, accessed 2026-09-03 ~15:30 UTC (the commit was not recorded at access, and the retrieved bytes were not retained. Measured on 2026-09-20 by RHACO-ANL-20260920-001: the public upstream history is a single commit, `aea8b1035030952555395de0c1de14ba693a1427`, committed 2026-09-02T22:47:42Z, some seventeen hours before the access; its `PROMPT.md` is blob `c2bc981d4af76130f8ad88f2ddd857491c517c72`, 5,742 B, sha256 `29815365b64ec65e9c9bbbdb429eb8b8352e21ccaa6887db6a302082f9565972`, the only version that history carries. A rewrite of the upstream history after the access would leave no trace and cannot be excluded. The upstream tree carries an MIT licence file, Copyright (c) 2026 raw). v0 was that structure generalised (`working\PROMPT_TEMPLATE.md`, sha256 `d1f2dee6…`, 7,908 B); v1 was its rewrite against Measurement Philosophy v1.4.1 (`working\PROMPT_TEMPLATE_CHARTER.md`, sha256 `7d6b39e1…`); neither was filed. v2.0 applies the revisions R1–R10 of RHACO-ANL-20260907-001, from one run of one instantiation (RHACO-CMP-20260903-001; n = 1). v2.1 applies the ratified dispositions of an external model review of v2.0 (RHACO-CHG-20260907-004): one control-flow defect, six semantic tightenings, three generalisations; no run has yet validated any v2.x mechanism. v2.2 corrects this paragraph's own account of what was retained and pins the upstream (RHACO-CHG-20260920-001); it changes no mechanism. Each section names the Charter principle it operationalizes (P1–P7); a label is a claim the section's mechanism must support. Fill every `{{SLOT}}`; delete `<!-- -->` comments before use.

---

# Goal

Build a {{TARGET_CLASS}} in {{STACK}}, from this empty folder.
The bar is {{QUALITY_BAR}}. Never {{ANTI_PATTERN}}.

Wherever a choice exists between the easier path and the more rigorous path, take the rigorous path. Where rigor is impossible, name the limitation in `SCOPE.md` (step 7) rather than working around it silently.

# How to work

## 1. Constraints first, then architecture. *(P1 Architectural Acceptance; P6)*

Before any feature code, write `CONSTRAINTS.md`: every known limitation of {{STACK}}, the runtime, the data sources, the budget, and the authority boundary (below) — {{KNOWN_CONSTRAINTS}}. Each constraint is an **input to the design**, not an obstacle. Where a constraint suppresses the obvious approach, the design lives downstream of the constraint in what remains uncorrupted. Never fight a constraint with a workaround that pretends it is absent; if a constraint is later removed, that is an explicit, versioned event with its own validation.

Then write `ARCHITECTURE.md`:
- one folder per subsystem: {{MODULE_LIST}}
- a shared {{CORE_DATA_MODEL}} every module reads from and writes to
- the public API each module exposes and the events it emits
- **ownership of every shared thing** — markup, vocabulary, contract, asset — assigned to the shell or the integrator by rule, decided here and never later by round cost; each shared block guarded by a contract test that fails when a copy diverges
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

**The probe's verdict is a fault predicate, not a capture predicate.** A run is FAIL when any PROBE_LOG_FIELD violates its declared bound, when any required capture is missing, or when the artifact's own error channel is non-empty. Successful capture is never `ok` by itself.

**Qualify the probe before trusting it.** Before any product claim cites a probe result, demonstrate on a frozen fixture or under controlled fault injection — never on the production data — that the probe passes one known-good case and fails each of {{KNOWN_BAD_CLASSES}}. Every qualification case asserts on the **rendered, user-facing observable**, never on a substrate attribute alone: a case that reads an attribute while the operator reads a sentence qualifies nothing the operator sees. Evidence lives under `docs/probe-qualification/`. Qualification is **progressive**: a known-bad class is qualified when the surface it needs first exists, and no product claim may cite a probe result for a surface whose class is unqualified. A probe that cannot separate known-good from known-bad is repaired before anything downstream is evaluated.

**A fixture is derived, not authored.** Where the probe uses a fixture, derive it from the production input source's runtime-resolved schemas, types, ranges and value shapes — records, payloads, rows, frames, files, traces, whatever the deliverable actually consumes — and record a fixture-versus-production census of the properties that bear on the verification target as a round-0 inspection output; a hand-authored fixture reproduces its authors' conventions, not the production input's variance.

**Budget the instrument separately.** The probe is not a product module: it carries {{PROBE_ROUNDS}} of its own plus one extension round for every wave that adds a surface it must qualify.

Every module ships a **showcase mode** that stages a representative minimal instance of just that module through the production code, so it can be probed in isolation.

**No agent may make a production-behaviour claim from a probe it has not run and inspected.** Claims of other kinds — structural, provenance, authority, record — cite the layer or check that supports them (Rules).

<!-- KNOWN_BAD_CLASSES: the fault classes the deliverable must be shown to expose, e.g. "wrong record for a known key; stale displayed metadata; reversed relation direction; broken deep link; console/runtime error". PROBE_ROUNDS: usually the per-module MAX_ROUNDS plus the wave extensions. -->

## 3. Verification layers and the shared-dependency register. *(P3 Layered Self-Filtering)*

The build is checked by five layers. Each carries its own version, its own validation criteria and its own **shared dependencies** in `docs/LAYERS.md`; none is claimed independent of the others.

| Layer | Mechanism | Catches | Shared dependencies (declared, not denied) |
|---|---|---|---|
| L1 Static | {{STATIC_CHECKS}} — types, lint, contract/schema validation, run on every commit | Contract violations before anything executes | the build tree; the schema |
| L2 Probe | `{{PROBE_TOOL}}` per step 2, run by the builder | Runtime failures, budget violations, visibly wrong output, unqualified surfaces | the build; the data; the capture path |
| L3 Critic | Separate agent per step 5, runs its own probes | What the builder saw and rationalized | the probe; the reference corpus; the model family |
| L4 Blind gate | External judge per step 6, sees only A/B artifacts | What the critic has grown used to | the probe output medium; the reference corpus |
| L5 Claim audit | Separate agent per step 5a, reads claims against referents | True code with false prose about it | the artifact tree; the record |

`docs/LAYERS.md` records: the shared dependencies above, filled in for this build; the sentence "independence claims we do not make"; and, for L5, which claim classes have a mechanical grammar and which remain a reader's. When layers disagree: record the disagreement; name the shared dependencies; distinguish an artifact defect from an instrument defect where evidence permits; run the smallest discriminating check; leave it unresolved if evidence cannot decide. A finding surfaced by a lower layer that a higher layer missed is logged as a gap in `{{STATE_FILE}}`, not silently absorbed. Upgrades stay local to one layer.

<!-- STATIC_CHECKS: e.g. "tsc --strict, eslint, JSON-schema validation of the core data model, folder-ownership check". -->

## 4. Fan out under explicit ownership. *(P6 Reasoning as Artifact)*

Use {{ORCHESTRATION_MECHANISM}}. One builder agent per module, owning only its folder. Waves ordered by dependency:
- Wave 1: {{WAVE_1_MODULES}}
- Wave 2: {{WAVE_2_MODULES}}
- Wave 3: {{WAVE_3_MODULES}}

Between waves, exactly one **integrator agent** — the only agent allowed to touch `{{CORE_PATH}}` and the shared things assigned in `ARCHITECTURE.md` — applies builders' core-change requests and revalidates every dependent after a contract change. Every accepted core change is recorded with the request, the alternatives, and the reason the integrator chose as it did. Ownership is never re-decided under budget pressure: a repair that crosses an ownership line waits for the owner's round if the defect is an omission, and is repaired at once **with a control** (a test that fails when the repair regresses) only if the defect is an affirmatively false statement about the artifact beside it.

Before every dispatch, record in `{{STATE_FILE}}` — before the strand returns — its role, model, effort, pattern, agent type, execution mode and `dispatched_utc`; any text carried verbatim into a dispatch is diffed against its archive at dispatch time; generated prompt text carries no round-specific and no self-referential literal.

<!-- ORCHESTRATION_MECHANISM: name what your environment provides — a subagent/task tool, one worktree per module driven by a script, a CI matrix, or "sequential waves in one session". -->

## 5. Differential critic. *(P4 Differential Measurement; P5 Measurement Defines Category)*

After each builder round, a separate **critic agent** — {{CRITIC_PERSONA}}, who writes no code — runs its own probes across several {{PRESET_KIND}} values, checks the API contract and {{PROBE_LOG_FIELDS}}, and scores each module.

**Scoring is differential, not absolute.** Three numbers per module per round:
- `ref_score`: quality against {{REFERENCE_CORPUS}} on the anchored 0–10 scale, higher is better — 10 = {{ANCHOR_10}}, 8.5 = {{ANCHOR_8_5}}, 7 = {{ANCHOR_7}}, 5 = {{ANCHOR_5}}
- `round_delta`: change since the previous round on the same presets — converging, oscillating, or thrashing, which the absolute score buries; read as a number only inside the critic's measured repeatability (below), otherwise as improving / unchanged / worsening plus the ranked issue-set delta
- `iso_vs_integrated`: showcase-mode score minus integrated-mode score — non-zero is a seam problem for the integrator, not a module problem for the builder

**The reference corpus carries provenance.** *(P6)* Before scoring, the critic records in `docs/REFERENCE.md` what {{REFERENCE_CORPUS}} is, where each item was obtained, its version or date, the access date, and which properties are compared. A reference without provenance is not a reference.

**Anchors are calibrated empirically.** *(P5)* Before wave 1 completes, the critic scores {{CALIBRATION_ARTIFACTS}} and records the results in `docs/REFERENCE.md`. Each calibration artifact is scored twice, the second time blind to the first; the spread is the critic's repeatability, recorded beside the anchors, and a `round_delta` inside it is `unchanged` whatever its decimal. If the anchors do not reproduce on known artifacts, rewrite the anchors, not the scores; thereafter the anchor text is frozen. If no calibration artifacts exist for the domain, record in `SCOPE.md` that the scale is ordinal and uncalibrated, and never read PASS from it.

Pass = `ref_score` ≥ {{PASS_THRESHOLD}} with {{ZERO_TOLERANCE_CONDITION}} and every objective gate green; a critic score never compensates for a failed objective gate. Below that, the builder receives the ranked issue list and goes again, up to {{MAX_ROUNDS}} rounds. A module at {{MAX_ROUNDS}} whose matched probe outputs and ranked issue set show no material change across its last two rounds is escalated to the integrator as a suspected contract problem, not given more rounds.

<!-- CALIBRATION_ARTIFACTS: three things of known quality — the reference itself (should score 10), a deliberately degraded copy (~5), an existing equivalent of known quality. -->

## 5a. Claim audit. *(P2; P6)*

After each integrator merge, a separate **claim-audit agent** — who writes no code and did not author the claims — reads every prose behaviour claim in the tree and the record (docstrings, notices, `ARCHITECTURE.md` and `CONSTRAINTS.md` sentences, round reports, `{{STATE_FILE}}` entries, critic reports) against the artifact it describes and returns, per claim, MATCH / MISMATCH / UNVERIFIABLE with the referent cited. A MISMATCH is a ranked issue to the owning builder; an UNVERIFIABLE claim is tagged `UNVERIFIED` in place. When an audit names a claim defect, the full extent of the claim across the tree is re-derived before the remedy is scoped — the named site is a sample. Every prose behaviour claim in the shipped tree carries either a named check or an `UNVERIFIED` tag; there is no third state. The audit is **clean** when it carries zero MISMATCH and zero `UNVERIFIED` on any claim a PASS criterion rests on — a required capability, an objective gate, the authority boundary, a terminal-state decision, or an externally presented behaviour claim; every other `UNVERIFIED` may stand at PASS only if it is listed in `SCOPE.md` or the terminal record and cited by no PASS criterion. Where any part of the audit is mechanical — a citation resolver, a docstring-versus-signature check — that tool is an instrument: before its MATCH verdicts support PASS, show it returns MATCH on one known-good claim and MISMATCH on one known-bad, evidence under `docs/probe-qualification/`; a reader's judgement is not qualified this way and `docs/LAYERS.md` says so. *(P2)*

## 6. Blind final gate. *(P4 — the paired comparison with the project's frame removed)*

A whole-{{ARTIFACT_NOUN}} critic scores {{END_TO_END_TARGET}} with the same three numbers. Then **blind judges** receive pairs of probe outputs labelled only A and B (ours vs. {{REFERENCE_CORPUS}}, order shuffled) and state which is better and why. Report the margin per round; a loss with narrowing margin is a result, not a failure to report. If no external artefact of the same medium exists, drop this gate and say so in `SCOPE.md`; never fake a reference.

## 7. Honest scope. *(P7 Honest Scope)*

Maintain `SCOPE.md` from the first commit: a normative table of every capability the {{ARTIFACT_NOUN}} does **not** provide, its status, the evidence for the limit, its consequence, the path to addressing it if one exists, and the validation required to remove it. Seed it from `CONSTRAINTS.md`. Any claim outside this table cites the module, probe result or audit verdict that supports it; any claim inside it states the limit explicitly. A capability leaving the table is a versioned event with its own validation criteria. Unmet bars — including a {{PASS_THRESHOLD}} never reached — are recorded here at the end of every run, plainly.

## 8. Reasoning as artifact, then loop. *(P6 Reasoning as Artifact)*

Persist to `{{STATE_FILE}}`: per module, `ref_score`, `round_delta`, `iso_vs_integrated`, round count, open issues, assumptions, invalidated evidence, and every `UNVERIFIED` a builder reported — **`UNVERIFIED` is a first-class value that survives integration**; the integrator may overrule it only with a cited check, never by omission. Also: the dispatch records of step 4; the identity record of the executing client at every round boundary (Rules); layer gaps; the terminal state. Every critic report, claim-audit report and blind-judge response is stored unedited under `docs/critique/`; every builder round produces `docs/rounds/{{module}}-{{n}}.md` stating what was tried, what was rejected and why, and which probe outputs the claims rest on. Evidence paths are append-only: no round overwrites another's report.

Loop until every critic passes and the claim audit is clean, or `SCOPE.md` records why it cannot; then declare a terminal state (step 9). Each iteration resumes from the open module with the lowest `ref_score`.

## 9. Terminal states. *(P7)*

End in exactly one state, declared once, from the record.

- **PASS** — only if every required capability exists, every objective gate passes from probe data, production-path probes pass, the claim audit is clean, `ref_score` reaches {{PASS_THRESHOLD}} on a calibrated scale, no `SCOPE.md` row contradicts a required capability, and the authority boundary is intact.
- **BOUNDED_FAIL** — the artifact is usable but a required bar is unmet after convergence or budget exhaustion. Report: achieved capabilities; failed presets; best observed quality; whether the limit lies in the artifact, the substrate, the architecture, the instrument, or an external dependency; unresolved alternative explanations; the next discriminating action. Budget exhaustion is always this state, never PASS.
- **BLOCKED** — progress requires human authority or an unavailable mandatory dependency.
- **INVALID** — the verification path cannot support trustworthy claims about the artifact. INVALID is preferable to a PASS resting on an unqualified probe.

# Authority boundary *(P7; P1)*

Agents may autonomously: create, edit and delete files inside the workspace; refactor; change internal architecture and contracts through the integrator; add local dependencies consistent with the stack policy; run tests, probes and audits; read {{SUBSTRATE_PATHS}}; commit inside the workspace.

Stop in BLOCKED before: writing anywhere under {{SUBSTRATE_PATHS}}; changing {{PROTECTED_CONTRACTS}}; lowering {{PASS_THRESHOLD}} or changing anchor text after calibration; changing the meaning of an objective gate; removing a `SCOPE.md` row without its validation; any external deployment or credential exposure; redefining a required capability out of scope without qualifying evidence.

At closeout, a hand outside the build verifies the authority boundary and records it. `CONSTRAINTS.md` names, in advance, the invariant that hand checks for each {{SUBSTRATE_PATHS}} entry, and the control must be one capable of detecting a violation: for a frozen artifact, hash before equals hash after; for a repository, no build-attributable commit and no dirty protected path; for a live store or service, no build-origin write in the store's own audit and every observed change reconciled to an authorized external writer. Hash equality is one such control, not the rule — a changed hash proves nothing about who wrote, an unchanged one proves nothing about transient writes. The build asserts nothing here; it is measured.

<!-- SUBSTRATE_PATHS: the corpus, database, service or repository the artifact reads and must never write, each with the closeout invariant that proves it. PROTECTED_CONTRACTS: CORE_DATA_MODEL, public APIs, the accepted default configuration of any upstream system. -->

# Rules

- Never inflate scores. Report real numbers, failed rounds, negative deltas, and what is still missing. *(P7)*
- Never edit another module's folder. Core and shared changes go through the integrator and are recorded with reasoning. *(P6)*
- Never probe through a mock. If the production path cannot be probed, that is a `SCOPE.md` entry, not a reason to probe something else. *(P2)*
- Never claim a comparison against a reference whose provenance is not in `docs/REFERENCE.md`. *(P6)*
- Never state a behaviour in prose without a named check or an `UNVERIFIED` tag; never record a builder's `UNVERIFIED` as verified. *(P2)*
- **Identity of the executing client is a measurement variable.** At every round boundary read and record the conjunction of {{IDENTITY_SURFACES}}; any change from the value of record is BLOCKED until ratified; configure the client's automatic model-switch behaviour to halt, never to retry-and-continue. *(P5)*
- Keep {{LIVE_CONDITION}} at all times; other agents are probing it.
- {{HUMAN_GATE_POLICY}}

<!-- IDENTITY_SURFACES: e.g. "the client config file's sha and its model key; the system-prompt model sentence; the per-request model field read as a family/generation check". No single surface is sufficient: config is precise but static, the prompt is stale after a switch, the per-request field is live but may be truncated.
     HUMAN_GATE_POLICY — recommended default under P6: "Make routine decisions yourself and log assumptions and rejected alternatives to STATE_FILE and docs/rounds/. Stop and request ratification before any Authority-boundary item. Otherwise keep going." State which of autonomous / gated / reviewed is in force. -->

Start now.

---

## Version History

| Version | Date | Notes |
|---|---|---|
| 2.0 | 2026-09-07 | First filed version. Applies RHACO-ANL-20260907-001 R1–R10 to the v1 Charter rewrite: terminal states (9); probe qualification, fault predicate, progressive sequencing, separate instrument budget, derived fixtures (2); L5 claim audit and the shared-dependency register replacing the independence claim (3, 5a); structural shared ownership and dispatch records at dispatch (4); authority boundary with closeout verification; UNVERIFIED as a first-class state value (8); client identity as a measurement variable (Rules); labels resolved to mechanisms, GL dropped as a warrant, provenance pinned. Cut by RHACO-CHG-20260907-002. |
| 2.1 | 2026-09-07 | Applies the ratified dispositions of an external review of v2.0. Control flow: `ref_gap` renamed `ref_score` (higher is better), resume from the lowest open score (5, 8, 9). Semantics: clean claim audit defined against PASS criteria; mechanical sub-auditors qualified like the probe (5a); critic repeatability measured on the calibration artifacts and bounding any numeric `round_delta`; escalation reads probe outputs and the issue set, not a decimal; gate over score (5); probe-claim rule narrowed to production-behaviour claims (2); closeout by per-substrate invariant, hash equality one instance (Authority boundary). Generalisation: fixture derivation freed of corpus vocabulary (2). No v2.x mechanism validated by any run. Cut by RHACO-CHG-20260907-004. |
| 2.2 | 2026-09-20 | Provenance correction only; no normative change. The v2.0 and v2.1 provenance paragraphs stated that the upstream file as retrieved was held at `working\PROMPT_TEMPLATE.md`; that file is the v0 generalisation, and no byte-identical copy of the upstream was kept (RHACO-ANL-20260920-001, finding S-6(c)). The paragraph now says so, places the `d1f2dee6…` pin on v0 where it belongs, pins the upstream's single public commit and its `PROMPT.md` blob as measured on 2026-09-20 with the stated bound, and records the upstream licence. Cut by RHACO-CHG-20260920-001. |

---

*Reno High-Altitude Cosmic Ray Observatory (RHACO) | Kris E. Granholm, Director*
