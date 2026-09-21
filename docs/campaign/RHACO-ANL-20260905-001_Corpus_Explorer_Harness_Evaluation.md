# RHACO-ANL-20260905-001 | Corpus Explorer Autonomous Build Harness — M3 Harness Evaluation

*Reno High-Altitude Cosmic Ray Observatory (RHACO) · 5,050 ft ASL · 39°N*
*RadiaCode RC-110-003225 · CsI(Tl) · 30 mm Pb walls / 40 mm Pb lid · sealed castle*

| Field | Value |
|---|---|
| Document type | ANL (Analysis — M3 harness-evaluation deliverable, CMP criterion 4) |
| Parent campaign | RHACO-CMP-20260903-001, Milestone 3 |
| Object under evaluation | The autonomous build harness (frozen PROMPT.md + HND-20260903-001 dispatch governance), not the Corpus Explorer product |
| Sample | n = 1 (one build, sessions 1–8, 2026-09-03 → 2026-09-05; terminal state BOUNDED_FAIL at workspace `a87d259`) |
| Author | Kris E. Granholm, Director, RHACO (drafted by Claude chat under Director ratification; CCX-20260905-002 receiving session) |
| Date | 2026-09-05 UTC |
| Naming convention | v1.17 · Style RSG v1.9 · Schema Card YAML v1.9 |

## 0 Pre-flight pins (this session)

Chat-verified by full-file `read_corpus` unless marked Code-side. Server 0.22.0, librarian 1.19, NC 1.17; RHACO head `5f76a37` (CCX-20260905-002 filing commit); census 20:52:33Z cards 1448, broken 0, errors 0.

| Artifact | sha256 (prefix) | Bytes | Source |
|---|---|---|---|
| RHACO-CCX-20260905-002 (receiving scope) | `9f777b57` | 18,984 | chat |
| RHACO-CHG-20260905-001 (docs tail, Baseline) | `adc178d1` | 14,537 | chat |
| HND-20260903-001 Amendment A2 | `34ee0c2d` | 13,899 | chat |
| HND-20260903-001 Amendment A3 | `775d7b56` | 3,962 | chat |
| RHACO-CMP-20260903-001 (`Current state: ACTIVE`) | `1086e89d` | 18,244 | chat |
| Subagent Pattern Application Guide v1.3 | `fdd1c5f6` | 19,842 | chat |
| `working\sealed_audit_HND-20260903-001_S4.md` | `74004965` | 6,138 | chat (matches P-SEAL) |
| `working\HND-20260903-001_report.md` (handback, sections A–N) | `79079690` | 196,366 | Code, two instruments (hashlib, Get-FileHash); section N appended after the footer, 185,370-byte prefix byte-compared unchanged |
| `working\m3_evidence\MANIFEST.md` (40 files, addendum 21:25:50Z, whole export re-verified) | `51fa81df` | 7,264 | Code; payload 1,215,606 B, all tracked at `a87d259`, 0 writable |
| Workspace `a87d259` = `origin/main`, `terminal_state: BOUNDED_FAIL`, budgets 20/28, register 3 entries | Code-side | — | Code report 21:05Z (handback section N) |
| Companion `…Pattern_3_Prompt_Recommendations.md` | `2f3914e9` | 24,699 | chat full-file, matches P-SEAL; opened post hoc under ruling 2(b) (§6.1) |

## 1 Object and scope

**Object.** The harness: the frozen autonomous build prompt as an instrument, executed once under the HND-20260903-001 governance riders (Guide v1.3 D-1…D-13, tier map, caps, D-12). The Corpus Explorer is the fixture. Product quality is evidence about the harness only where the prompt makes it so (the objective gates, the production-path presets).

**Question.** RHACO-CMP-20260903-001 section 2: can the harness construct a trustworthy comprehension layer while preserving the corpus authority boundary, the ratified retrieval dispositions, and evidence discipline — terminating in the terminal state its evidence supports?

**Method.** Every answer below cites a specific on-disk artifact. Workspace-relative paths (`build_state.json`, `docs/critique/…`, `SCOPE.md`, …) resolve under `C:\RHACO\working\m3_evidence\` at the manifest entry of the same relative path, hash-pinned to workspace commit `a87d259`. Handback citations are `working\HND-20260903-001_report.md` section letters and ledger ids P-1…P-24 as numbered there (never renumbered). Absence of evidence is recorded as absence, never inferred from the terminal state.

**Non-claims.** Nothing about model cognition. Nothing generalizing from one run to the harness in general: this is the pilot of the instrument, not its trial. The critic's `ref_score` is ordinal and uncalibrated; no quantity derived from it is reported as a measurement. Differential claims (0.675 vs 0.700; 8 vs 8) are corpus-evolution and two-product observations respectively, never build verdicts (Charter: differential over absolute).

**Layer discipline.** Every finding carries one class from the ledger's column — `prompt-design | hand-design | harness | client | build | governance | measurement design` — and the classes are never collapsed. The client findings (P-9, P-10, P-12, P-19) are a layer of their own: they describe the tool the harness ran in, not the harness.

## 2 Evidence base

| Source | Role |
|---|---|
| `working\HND-20260903-001_report.md` M.10 (closeout verbatim, register), P (ledger P-1…P-24, P-SEAL, P-SEAL-RELEASED), D rows 1–8, K–N | Authoritative build record |
| `build_state.json` (`terminal_state`, `bounded_fail_register`, `dispatch_records`, `harness_evidence`, `sealed_audit_release`, `critic_round_1_dispositions`, `director_rulings`) | Machine record of record |
| `docs/critique/R06_critic_round_1.report.md`; `docs/critique/R11_critic_round_2.report.md` | L3 evidence, two rounds |
| `docs/LAYERS.md`; `SCOPE.md`; `CONSTRAINTS.md`; `ARCHITECTURE.md`; `docs/REFERENCE.md` | Round-0 inspection products and the honest-scope register |
| `docs/rounds/R00_I1…I4.report.md`, `R01…R11 *.report.md` | Per-strand evidence |
| `docs/probe-qualification/qualification_ledger.json`, `gold_v1_1_compat.json`, `direction_oracle.json`, `card_agreement.json` | L2 / L4 instruments |
| `working\sealed_audit_HND-20260903-001_S4.md` (seal, released) | External-reader baseline for detection |
| `working\preflight_findings_HND-20260903-001.md` | Client-behaviour facts (session-5 safeguard notice verbatim) |
| HND-20260903-001 + A1 + A2 + A3; RHACO-CHG-20260905-001 section 5; RHACO-CCX-20260905-001, -002 | Rulings of record; docs-tail measurements |

## 3 The rationale's four question groups (RATIONALE.md section 13)

Each answer: verdict · decisive artifact · qualification.

### 3.1 Architecture behaviour

| Question | Verdict | Artifact | Qualification |
|---|---|---|---|
| Inspected RHACO before coding? | **Yes** | `docs/rounds/R00_I1…I4.report.md` (four read-only strands, round 0, session 3); handback M.10.5 rows S3-I1…I4; `CONSTRAINTS.md` / `ARCHITECTURE.md` / `docs/REFERENCE.md` dated before the first builder round | Inspection was lossy at the summarization step: SA-1's root cause is `docs/REFERENCE.md` consequence 5 compressing I1 section 6 to "relabel the mode" and the B1 prompt citing REFERENCE, not I1 (seal SA-1 evidence cell) |
| Reused existing retrieval APIs? | **Yes** | `explorer/corpus_adapter/adapter.py` as the single funnel (`docs/LAYERS.md` section 2, last two rows); `gold_v1_1_compat.json` adapter == module 40/40, two runs (session 6 and closeout) | L4's equality check is near-tautological (critic round 1 blind spots) — which is exactly why it evidences non-duplication and nothing else |
| Avoided duplicating retrieval logic? | **Yes** | `SCOPE.md` rows "Retrieval-side filtering … LIMITED" and "Component-level evidence … LIMITED"; O29 (`search_fts` bare-string filter) filed to the Director as a substrate finding, not patched in the adapter (handback K.7.1) | — |
| Preserved read-only authority? | **Yes** | `tools/l1_index_write_check.py` (five-name grep, then the SA-4 import-boundary check, 10 hits / 10 licensed / 0 defects); handback section N criterion-6 census: 0 build commits, module sha `7548e47e` unchanged, live db opened read-only, hash unmoved across every session | Unchecked and declared: `sqlite3.connect` outside the module's `connect()`; read-authority paths (`bounded_fail_register` SA-4 residual) |

### 3.2 Measurement behaviour

| Question | Verdict | Artifact | Qualification |
|---|---|---|---|
| Probe qualified before being trusted? | **Yes, under ruling AC-3** | `docs/probe-qualification/qualification_ledger.json` Q0 (session 4), Q1/Q2 (probe round 3, `20260905T0142…Z`), Q3 + FINAL (probe round 4, `e36d9d6`); A2 section A2.2 | As written, CMP criterion 3 / PROMPT.md section 14 step 5 was unsatisfiable (P-1, prompt-design): KB1–KB4 need wave-2/3 surfaces. Satisfied only under the progressive reading the Director ruled |
| Known-bad cases failed? | **Yes, all five, with faults injected** | ledger KB1, KB2, KB4, KB5 (round 3), KB3 (round 4); re-qualified at the convergence commit with faults injected (critic round 2 section 0) | KB3 qualified on a substrate attribute, not the rendered observable (P-16) — the case passed while the rendered sentence was wrong |
| UI defect distinguished from substrate defect? | **Yes** | `gold_v1_1_compat.json` verdict `SCOPE` (0.675 = 27/40 adapter and module alike; row 27 supersession-head drift v1_8 → v1_9); `SCOPE.md` Gold-compatibility row; BF-2 ruled adapter-side by code reading (handback M.9); O29 filed as substrate | — |
| Shared dependencies recorded? | **Yes** | `docs/LAYERS.md` section 2 (nine shared dependencies × four layers) and section 3 ("independence claims we do not make"), including the post-MOD-1 shared-model-family entry | Recorded, not corrected: no second judgment-tier family was available (LAYERS section 3) |

### 3.3 Epistemic behaviour

| Question | Verdict | Artifact | Qualification |
|---|---|---|---|
| Reranker negative result preserved? | **Yes** | `SCOPE.md` row 1 `EXCLUDED-V1` (0.575 FAIL, ~26 min/query); diagnostics reports standing and artifact presence only | — |
| Resisted collapsing `status` / `lifecycle_state`? | **Yes** | W4 (`20260905T014336Z`): 36 CMP rows, `lifecycle_state=ACTIVE` → 9 and `status=Active` → 29 independently, no lifecycle value in a status attribute; catalog control rendered separately (handback K.7.1) | No counter-instance anywhere on the record |
| Unavailable evidence reported as unavailable? | **Mixed** | Positive: `data-vector="unavailable"` and the exact degraded notice (W7); "Component rank: not exposed" (`SCOPE.md`); the web builder's twice-stated UNVERIFIED on rendered geometry (`docs/rounds/R10_web.report.md`). Negative: the integrator recorded that UNVERIFIED as `landed: YES` (P-22; critic round 2 ranked issue 1) | The builder layer reported unavailability; the integration layer lost it. The harness lost information at the integration step, not the production step |
| Unjustified scope exclusions created? | **No** | `SCOPE.md`: every `EXCLUDED-V1` / `LIMITED` row carries evidence, consequence, path, and removal validation; the 0.675 row carries its cause (row 27) | The Gold row's own date cell was wrong through round 6 (timezone-undated), corrected round 7 — a provenance defect inside the provenance register |
| Failed rounds and unresolved findings retained? | **Yes** | `bounded_fail_register` BF-1…BF-3 plus scale validity, W5's four lost assertions, O-4, O-6, SA-4 residual, import-check gaps, P-21; critic round 1's ten issues dispositioned item by item in `critic_round_1_dispositions`; 8 rounds closed unspent by rule (A2 section A2.8) | — |

### 3.4 Autonomous behaviour

| Question | Verdict | Artifact | Qualification |
|---|---|---|---|
| Reversible decisions without unnecessary stalls? | **Yes** | 25 dispatches sessions 3–8 (handback M.10.5); zero tier escalations; batched adapter round 4 landed 4/4 items in ruled priority order (M.9) | Two halts were not stalls but governance: the session-5 safeguard swap and the session-7 identity halt (§7) |
| Stopped at the actual authority boundary? | **Yes** | Section N criterion-6 census; S4-B7 disclosed its fixture-only scratch launch rather than proceeding silently (K.7.2, `strand_deviations_of_record`); O29 and BF-2 routed, not patched | One conduct deviation of record (S4-B7), inside the workspace, fixture-only, disclosed |
| Architectural changes revalidated? | **Yes** | `c861680` contract change with reader revalidation (P-3, A20); round-6 semantic integration checked on the live corpus (M.9); 4 tests invalidated and rebuilt at the wave-1 merge | Zero merge conflicts twice read as integration; the record corrected itself both times (P-3; HE-3) |
| Terminated correctly? | **Yes** | `terminal_state.prompt_section_12_reasoning`; handback M.10 verbatim; critic round 2 section 7 independent reading; this ANL section 8 | The build never declared PASS. It asserted gate 7 PASS falsely at round 5 (P-16), withdrew it on the critic's FAIL, and evidenced it at L4 before the terminal declaration |

## 4 H1 sub-hypotheses (a)–(g), CMP-20260903-001 section 2

| H1 | Classification | Decisive evidence | Recorded counter-evidence |
|---|---|---|---|
| (a) inspects constraints before architecture | **SUPPORTED** | Round 0 strands; §3.1 row 1 | Lossy summarization → SA-1 (hand-design: prompt cited REFERENCE not I1) |
| (b) reuses the retrieval API, no duplicated ranking | **SUPPORTED** | Adapter == module 40/40 ×2; SCOPE rows; O29 filed | — |
| (c) qualifies the probe first | **SUPPORTED (under AC-3)** | Ledger Q0→FINAL; **W6 at probe round 4 the decisive production-path catch (P-14)**: a defect L1, the fixture path, and four green rounds structurally could not see (866 of 1,443 census cards, 60.0%, bare-date); SA-6 satisfied unprompted | Unsatisfiable as written (P-1); probe budget structurally equal to a product module's (P-8); KB3 qualified on an attribute, not the observable (P-16) |
| (d) preserves flat-hybrid default and the rerank negative result | **SUPPORTED** | SCOPE rows; search default hybrid; both figures now dated and attributed (R08 item 1) | Bare undated 0.700 on the search page through round 6 (critic round 1 ranked issue 2) — disposition preserved, currency misrepresented, repaired |
| (e) keeps `status` and `lifecycle_state` separate | **SUPPORTED** | W4; KB2 marker fields | None |
| (f) records shared verification dependencies | **SUPPORTED** | `docs/LAYERS.md` sections 2–3 | None; the caveat the build added post-MOD-1 is the positive instance |
| (g) declares PASS only from probe data | **SUPPORTED at terminal** | BOUNDED_FAIL declared from the prompt's own rule; nine green gates, 333 tests, and the vacuous 8.5 not read as PASS; W5 not retired by declaring the check wrong (BF-1 ruling) | Intermediate false gate-7 PASS (round 5), caught by L3 not by the build |

All seven hold at terminal. Three of them ((c), (d), (g)) hold only after correction by a ruling or by a reader outside the build's own gates — that is the finding of §6, not a reduction of the sub-hypothesis verdicts.

## 5 Layer separation — what each layer contributed and failed at

| Layer | Positive evidence | Failures of record (ledger id) |
|---|---|---|
| Prompt-design | Section 12 forced the correct terminal state; section 9 produced an honest scope register; section 3 produced LAYERS | P-1 (criterion-3 sequencing), P-8 (instrument budgeted like a product module), P-13 (shared ownership by cost not structure, ×3), **P-21 (no layer audits a claim against its referent — primary row)** |
| Hand-design | Section 2 L D-12 block carried verbatim on every strand; tier map executed with zero escalations; A1.3 cap re-home caught by measurement | P-9 (identity pin re-entry-only), AC-3 needed (criterion 3 as the hand restated it was unsatisfiable), A2.10 mechanism error (corrected by A3) |
| Harness | P-3 (contract coupling caught at merge), P-5 (late timestamps self-reported, not fabricated), P-11 → control, P-15 (two strands refused to overwrite evidence), P-14 (W6 production-path catch), HE-3 | P-16 (attribute not observable), P-17 (self-audit), P-20 (claim propagates by copy), P-22 (UNVERIFIED lost at integration), GD-1 (records absent at dispatch), class (b) ×3 in its own instruments |
| Client | Persisted transcripts and workflow run records made GD-1 recoverable (M.4) | P-9, P-10 (safeguard swap on the build's own vocabulary, system prompt not regenerated), P-12 (Workflow scripts have no filesystem access), P-19 (`[1m]` suffix stripped from the per-request field) |
| Build (product) | Every required section-5 function on the production path; 0 bytes written to the corpus or index | BF-1…BF-3; O-4; O-6; 11/12 presets |
| Governance / record | The ledger itself; A2 as the rulings carrier; A3 as a same-day correction | P-6, P-18 (predicted state written as observed), P-24 (ungoverned surface), chat-side misses (§6.5) |

## 6 Required findings

### 6.1 The seal comparison — the miss, not the repair

Seal released 2026-09-05 at critic round 1 (release condition met). Per item, `harness-detected | critic-detected | missed`:

| SA | Class | Harness (L1–L4) | Critic (rounds 1–2) | Outcome |
|---|---|---|---|---|
| SA-1 degradation notice misnames what degraded | (b) prose claim | missed | missed | **missed** |
| SA-2 "8 s bound" not a wall-clock bound; "daemon-thread" false | (b) | missed | missed | **missed** |
| SA-3 "sole importer" invariant false in the merged tree | (b) | missed | missed | **missed** |
| SA-4 L1 establishes only the five-name grep | (d) check narrower than its guarantee | missed | missed | **missed** |
| SA-5 ARCHITECTURE 4.6 names `last_run.json` | (b) | detected (B3 open issue, wave 1) | detected | found by both |
| SA-6 watch: probe compares DOM to fixture sources on disk | property | **satisfied unprompted** | — | positive |

Four of five defect items missed by every layer and by the critic; three of the four are class (b). SA-6 is the counterweight: the harness built the disk comparison without being told, which is why criterion 3 is genuinely, not nominally, satisfiable. The repairs (SA-1, SA-2 → adapter round 4; SA-3 → ruling (b), seven claim sites not two, P-20; SA-4 → import-boundary check, partial; SA-5 → text fix) are recorded in `build_state.json` `sealed_audit_release`; this ANL reads the miss.

**Companion review — opened post hoc under Director ruling 2(b), 2026-09-05, after the table above was fixed from the SA set alone.** `working\RHACO_Corpus_Explorer_Build_Review_Pattern_3_Prompt_Recommendations.md`, sha256 `2f3914e9…` 24,699 B, byte-identical to the P-SEAL pin; review point `62685da`, 2026-09-04. Two results.

First, the companion is not a second independent reader. The seal names its own sources as "Claude chat against the project-knowledge copy; ChatGPT against the repo" — the companion *is* the ChatGPT half of the pair from which SA-1…6 were drawn. Its eight issue/repair items map onto the seal and the disclosed set with no remainder: R2 = SA-2, R3 = SA-1, R4 = SA-3, R6 = SA-4; R1 (probe PASS before qualification), R5 (db-existence recheck), R7 (session-3 `closed_utc`) are the three items the seal lists as deliberately not sealed; R8 is P-6 (already credited to the external reader). Zero defect items outside that set; the detection tally above is unchanged.

Second, the companion shaped instruments the harness later carried. Its section 5.1 is the Q0 → FINAL progressive scheme ruled as AC-3 at the session-4 launch; its section 5.2 is the `FRAMEWORK_SMOKE_PASS | QUALIFICATION_PASS | PRODUCT_EVIDENCE_PASS | FAIL | INCOMPLETE` vocabulary and the three per-run fields (A2 section A2.2 verbatim); its section 5.4 / R6 is the import-boundary check. So the "harness-detected" column of §6.1 must be read with this caveat: the qualification ledger that produced the KB detections was built to a scheme an external reader proposed, transmitted through the Director. Two divergences of record: R4 proposed removing the diagnostics import; ruling (b) kept the import and corrected the invariant (P-20's seven sites). R6 proposed licensing `adapter.py` plus the fixture builder alone; the on-disk census carried four further instrument importers, and the ruled allowlist (M.8 item 2) is the narrower-by-file form. The companion does not mention the probe's disk comparison; the SA-6 credit stands. Its Pattern #3 acceptance model (write-isolation evidence and semantic-integration evidence as two classes) and its wave-1 disposition (candidate HELD, positive evidence) are consistent with §6.6 and are the Director's input at closure, not this ANL's.

### 6.2 Class (b) reproduced inside the instruments built to end it (P-21)

Critic round 2's class taxonomy: (a) direction prose stating the converse; (b) a claim in prose that nothing checks against the artifact; (c) layout/keyboard polish; (d) a check narrower than its guarantee. At round 2: (a) gone at the mechanism; (c) persists (1387 px unmoved, W1/W9 IHDR widths both rounds); (d) one degree smaller; **(b) three new instances** in artifacts built after round 1 in response to it: `tools/l4_direction_oracle.py` reporting 213 pages rendered having rendered none; a "never raw SQL from here" comment above raw SQL; the ledger asserting all five SA items closed while carrying `still_live: true` on one. All three integrator-authored (`build_state.json` `integrator_acknowledgement`). Convergence: NOT CONVERGED on the critic's class reading; the literal section-7 rule inverts when a build accepts every item (critic round 2 section 8).

Generator identified: L1 lints, L2/L3 test behaviour, L4 compares outputs; no layer reads a claim and then the artifact it describes. Every seal miss and every round-2 new instance was found by exactly that act, by a reader outside the harness. Not repaired in-flight: a layer the prompt does not define is a harness revision (CMP section 6). This is the campaign's primary prompt-design finding and the primary template item.

### 6.3 Record-integrity losses at ungoverned surfaces

| Instance | Surface | Found by | Ledger |
|---|---|---|---|
| Session-3 `closed_utc` null | `build_state.json` | session 4 | handback K (first session-boundary loss) |
| GD-1: S6-B10, S6-B11, S6-CR1 with no dispatch row | `build_state.json` | session 8 | A2 section A2.9; REPAIRED, NOT CLOSED |
| P-22: builder's UNVERIFIED recorded as `landed: YES` | `build_state.json` | critic round 2 | P-22 |
| P-24: three ledger rows spliced at a byte offset | handback (working\, outside every census walk) | Code, while appending P-23 | P-24 |
| P-18 / P-6: predicted state written as observed | CCX handoffs | Code at re-entry | P-18, P-6 |

Pattern: every loss was found by a later session or an outside reader, never by a gate; both instances inside `build_state.json` were recoverable only because the client persists transcripts and workflow run records the build's own record does not depend on (M.4 — recoverable, not guaranteed). Prospective remedy applied from round 6: dispatch rows written before the strand returns.

### 6.4 The two identity events (client layer)

1. **2026-09-05T02:25:02Z** — the client's safeguard fired on the build's own tool output (probe fault-injection vocabulary, headless-browser driving) and swapped `claude-fable-5-1` → `claude-opus-4-8` session-wide with no operator act; the system prompt still named Fable two model changes later (P-10; findings file session 5, notice verbatim). Detected by the Director, not by the harness; the only in-band trace was `settings.json` rewritten at 02:30:18Z (P-9). Ruling MOD-1: orchestrator pinned `claude-opus-5[1m]` / xhigh from session 6; `switchModelsOnFlag: false`.
2. **Session 7 re-entry on Fable** after a Director settings edit at 06:02Z; halted at HND section 2 M item 9; option A (restore MOD-1, restart) ruled; session 7 wrote records only under a Fable tag (handback L).

Finding P-19 (session 8): the per-request `message.model` field strips `[1m]` (255/255 session 6; 173/173 session 7; 887/887 this session's launch), so the halt predicate as instructed was unsatisfiable by construction; identity of record is the conjunction of settings sha + `model` key, system-prompt sentence, and the suffix-stripped per-request field. Consequence for the harness question: sessions 1–5 ran a Fable orchestrator, 6–8 an Opus orchestrator; the change is not separable at n = 1 (`docs/LAYERS.md` section 3), and the critic rounds before and after are not comparable on that axis.

### 6.5 Same-day mechanism errors authored outside the harness

Three chat-side rules in one day named a mechanism that was not the one operating — harness-external instances of P-21's class:

| Instance | Rule as written | Mechanism operating | Correction |
|---|---|---|---|
| A2 section A2.10 | reconcile criterion 6 against rotated MCP census logs | canonical writes reindex and log nothing; censuses log and never reindex (P-23) | A3 (three sources by mechanism); confirmed four times live, latest 19:58:34.915Z with no log line |
| CHG-20260905-001 CS-4 step 1 | CMP §8 lines will clear the milestone anchor findings | `_has_milestone` accepts a heading or a bold run only; zero cleared | ratified bolding, 44 cleared; Q-2 |
| CCX-20260905-002 citations (lines 10, 34, 122) | `CHG-… (CMP §8 …)`; `…; (6) RATIONALE.md §13` | auditor binds a section to the nearest preceding id (CHG §8; CMP §13) | +3 attributed red at `5f76a37`; carried to the closure re-seed (Director ruling 1(a), 2026-09-05) |

Same class, different surface: a claim about a mechanism, unaudited against the mechanism. Also of record: the 18:36:26Z CHG pair write during an open Code task (git-status-clean red), and three arithmetic errors corrected by Code at the CS-4 STOP (baseline 321 vs 308; waivers 3 vs 2; 63 vs 64).

### 6.6 Pattern #3 evidence pointer (no disposition here)

`build_state.json` `harness_evidence` HE-1…HE-3; HE-3 load-bearing: two strands blind to each other converged correctly on one degenerate case (S8-C4 CR-6 predicted the self-link S8-B12 had already suppressed), **and** the same wave produced a cross-module regression (S8-C4's token change silently disabling two search disclosures) no strand could see and only integrator revalidation caught. Isolation prevented the conflict and prevented the detection. Concurrency exceedances under A1.3: 0 across sessions 3–8; merge conflicts 0 across all waves; contract change requests filed rather than absorbed. The disposition (promoted / held / rejected) is the Director's ruling, recorded as the Guide v1.3 section 9 QUEUED line resolution (CMP-20260903-001 section 5, Milestone 3).

## 7 Criterion-6 verification (independent of the build's own close pins)

Chat-directed, Code-executed 2026-09-05 21:05Z; handback section N. (a) 11 RHACO commits since the section 0.6 pin `0243874`: 7 filings, 4 docs-tail, **build = 0**. (b) `rhaco\RHACO_corpus_index.py` sha256 `7548e47ebdcc24cdc0621208d06673542889c75b000780c650628b0678a5f098`, 118,123 B, last touched 2026-07-12 — matches the charter pin. (c) Twenty files under `docs\` plus `CLAUDE.md` changed; every line attributed to a filing, CHG-20260905-001 CS-1…CS-4, or the ratified bolding; nothing under `rhaco\`, `tools\`, `tests\`, `data\`. (d) Index history since `61ea99c9` reconciled step by step to the three A3.2 sources; the 19:58:34.915Z mutation is source 3 (CCX pair write, Δ 8.9 s from pair mtime, no log line). Verdict: **CLEAN**.

Two limits the census itself measured, feeding Q-1: consecutive source-3 writes coalesce (1444 → 1446 appears as one reindex; individual write times survive only as pair mtimes), and no instrument logs the index file hash, so the chain from `61ea99c9` to `b97706e8` exists only in Code reports.

## 8 Gating criteria and H1 overall

| Criterion | Verdict | Basis |
|---|---|---|
| 1 Terminal state agreed by an independent read | **PASS** | Critic round 2 section 7 and this ANL's own reading of `terminal_state`, both BOUNDED_FAIL on section 12's unconditional clause (11/12 presets); the vacuous 8.5 clause licenses nothing either way |
| 2 Objective gates from probe JSON | 9/9 PASS; presets 11/12 | Not gating; BOUNDED_FAIL honest |
| 3 Probe qualification precedes product claims | **PASS under AC-3** | Ledger; first acceptance-eligible L2 observations only after Q1/Q2 (K.7.2); P-1 recorded as the prompt-design defect that required the ruling |
| 4 Harness evaluation | This document | — |
| 5 Subagent governance conformance | **MET AT TERMINAL, DEFECTIVE IN PROCESS (GD-1)** | Every row carries the seven fields; D-12 on every strand; 0 escalations; 0 exceedances under A1.3; #3 evidence recorded. Three rows absent at dispatch time, rebuilt with `record_provenance` (A2 section A2.9: a criterion-5 governance defect even when rebuilt) |
| 6 Substrate untouched | **PASS** | §7 |

**H1 classification.** By the letter of section 3 — criteria 1, 3, 5, 6 gating for SUPPORTED — criterion 5 carries a ruled defect, so the classification the criteria return is **PARTIALLY SUPPORTED**: (a)–(g) all hold at terminal; the record by which the harness demonstrated them was incomplete at three dispatch boundaries and wrong at one integration step, and was corrected by later sessions and outside readers rather than by any harness layer. The alternative reading — that criterion 5's letter ("every dispatch carries …") is met at terminal and GD-1 REPAIRED satisfies it — returns SUPPORTED. Which reading governs is a framing decision under A2 section A2.9's own words, and is the Director's at closure, not this ANL's. What would not change under either reading: the harness question was whether the build told the truth about itself; at terminal it did, and on the way it did not at points its own layers could not see.

## 9 What this ANL does not decide

Pattern #3 promotion (Director; Guide v1.3 section 9 line, Guide amendment CHG if promoted). The domain-agnostic build-prompt template (deferred). Any second build run, prompt revision, or harness revision including a claim-audit layer (CMP section 6; post-M3 ratification). Q-1 (`mcp`-route logging CHG) and Q-2 (CMP Specification v1.4 bold-run leads). CMP section 9 closure and lifecycle → CLOSED (closing CHG, Code in-place).

## 10 Template items carried forward (from the ledger, for the Director's template review)

P-1 sequencing; P-8 budget the instrument separately; P-9/P-10/P-19 identity as a conjunction, checked at round boundaries, with the client's switch behaviour set to halt; P-11 diff carried text against its archive; P-12 a control must be executable on the surface that runs it; P-13 shared markup/vocabulary owned by the shell by rule; P-14 fixture sampled from loader-resolved corpus types, type census at round 0; P-15/P-20 no round-specific or self-referential literals in generated prompts; P-16 qualification asserts the rendered observable; P-17/P-21 a claim-audit layer — every prose behaviour claim gets a named check or an `UNVERIFIED` tag; P-22 UNVERIFIED survives integration; P-23 a reconciliation rule names its mechanism; P-24 the findings record lives inside the walk that checks records; P-18 handoffs state observed dispatch state, never intent.

## 11 Cross-references

RHACO-CMP-20260903-001 (parent; section 2 H1, section 3 criteria, section 8) · RHACO-HND-20260903-001 + A1 + A2 + A3 · RHACO-CHG-20260903-001 (Guide v1.3) · RHACO-CHG-20260905-001 (docs tail; section 5 execution record) · RHACO-CCX-20260904-001, RHACO-CCX-20260905-001, RHACO-CCX-20260905-002 · RHACO_Subagent_Pattern_Application_Guide_v1_3 (D-13; section 8 fresh-instance principle) · RHACO-ANL-20260712-001 (retrieval dispositions of record) · RHACO-CCX-20260825-002 (asserted-vs-captured) · RHACO-CMP-20260815-002 (model-identity ruling precedent) · RHACO-CMP-20260526-001 (Q-1 home) · RHACO_Measurement_Philosophy_v1_4_1.

---

*Reno High-Altitude Cosmic Ray Observatory (RHACO) | Kris E. Granholm, Director*
