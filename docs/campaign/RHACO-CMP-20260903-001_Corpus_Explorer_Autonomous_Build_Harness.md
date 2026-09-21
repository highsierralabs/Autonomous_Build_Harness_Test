# RHACO-CMP-20260903-001 | Corpus Explorer — Autonomous Build Harness Test

Campaign opened: 2026-09-03 UTC
Campaign closed: 2026-09-05 UTC
Current state: CLOSED
State history:
  - OPEN 2026-09-03 — initial charter (investigation-class)
  - ACTIVE 2026-09-04 — Part B dispatched (HND-20260903-001 §3, session 3); recorded 2026-09-05 by RHACO-CHG-20260905-001
  - CLOSED 2026-09-05 — M3 executed (RHACO-ANL-20260905-001 filed; criterion-6 verification CLEAN; Pattern #3 PROMOTED per RHACO-CHG-20260905-002); closure recorded by RHACO-CHG-20260905-003

## 1  Campaign Overview

This investigation-class campaign runs the first RHACO-native test of the
Measurement-Philosophy-derived autonomous self-qualifying build prompt, using a
real operational need as the fixture: a local, read-only, no-LLM human
comprehension layer (the Corpus Explorer) over the existing corpus substrate
delivered by RHACO-CMP-20260624-001 and RHACO-CMP-20260628-001. Scope: one
frozen build prompt, executed once under explicit subagent governance, with its
terminal state and its on-disk build record evaluated as evidence about the
harness — the browser is the fixture, the harness is the object under test.
Stakes: a supported result establishes the harness as a reusable RHACO
instrument for autonomous construction under authority boundaries, and
incidentally gives the Director direct access to the corpus without a frontier
model mediating; an unsupported result is recorded as such, and the browser, if
usable, is still a browser.

## 2  Scientific Question

Can the Measurement-Philosophy-derived autonomous build harness construct a
trustworthy human comprehension layer over RHACO's corpus substrate while
preserving the corpus authority boundary, the empirically ratified retrieval
dispositions, and evidence discipline — terminating in the correct terminal
state for the evidence it actually produced?

H1 (harness): under the frozen prompt and the subagent governance in §4, the
build (a) inspects standing constraints before architecture, (b) reuses the
existing retrieval API without duplicating ranking logic, (c) qualifies its
probe against known-good and known-bad cases before trusting it, (d) preserves
the flat-hybrid default and the rerank negative result, (e) keeps card `status`
and CMP `lifecycle_state` separate end to end, (f) records shared verification
dependencies rather than claiming independence, and (g) declares PASS only when
the objective gates pass from probe data. H0: one or more of (a)–(g) fails, or
the terminal state is not supported by the on-disk evidence. Non-claims:
nothing about model cognition; nothing generalizing from one run to the harness
in general (n = 1; this is the pilot of the instrument, not its trial).

Known at charter (verified live 2026-09-03; server v0.22.0, librarian 1.19,
NC 1.17, head `32195e1`, 1436 cards):

1. Substrate: `rhaco\RHACO_corpus_index.py` v1.5 (2026-07-13, 118,123 B)
   exposes `resolve_identifier`, `search_fts`, `search_hybrid`,
   `search_hybrid_rerank`, `search_graph`, `freshness_check(scan)`; typed
   degradation via `RHACO_CORPUS_DISABLE_VEC` (VecUnavailable) and
   `RHACO_CORPUS_DISABLE_RERANK` (RerankUnavailable). `freshness_check` takes
   a librarian scan object — the explorer imports the librarian as well as the
   index module. The module hard-codes `C:\RHACO` paths; the NTFS junction to
   `C:\highsierralabs\RHACO` (CHG-20260809-001) keeps them valid.
2. Retrieval dispositions of record (RHACO-ANL-20260712-001, sha256
   `78891a81f2ba581f761f8cddcc82f561391671e6680d19c0515d07431ef6af87`): flat
   `hybrid` Recall@10 = 0.700 aggregate on Gold v1.1 (40 rows, strata
   8/6/12/6/8), accepted as the default-flip candidate and flipped at M4
   (CHG-20260712-002); `hybrid-rerank` 0.575 FAIL on Criterion 1, retained as
   a documented-FAIL batch mode at ~26 min/query; `graph` 0.575, auxiliary
   lineage mode. RHACO-CMP-20260628-001 lifecycle CLOSED.
3. Gold sets on disk: `working\eval\gold_queries.yaml` (v1.1) and
   `working\eval\gold_queries_v1_2.yaml` — grey-zone location, not the
   docstring's `eval\`.
4. Subagent governance of record is `RHACO_Subagent_Pattern_Application_Guide_v1_2`
   (sha256 `8958a8489f42f2f88e3d0bc7ce2e1443af5532ada4761b7d4d011a0a7583fc5e`).
   It carries no model-tier rule; Pattern #3 (parallel write-scoped builders)
   is HELD pending a worktree-isolated module-author application; D-3
   (inline-blocking only) forbids a backgrounded server; D-12 (device-safety
   prohibition) is mandatory wherever the live primary is shell-reachable —
   which includes the observatory host this build runs on.
5. The prompt as received: `RHACO_Corpus_Explorer_Autonomous_Build_Prompt.md`
   (28,665 B, chat-side sha256
   `dd75dd2ebf6a641bd223acf47289e0f3dd5b5b70c2b506b70d0c986cded98d0d`) and
   `RHACO_Corpus_Explorer_Prompt_Rationale.md` (26,151 B, chat-side sha256
   `3070c961b08aa90bdfc6da0d87b806f3e97b98f95fba032d3f6617506d372a6b`).
   These are as-uploaded pins; the pins of record are taken on disk at M0
   after landing (line-ending normalization may change the bytes).

Unknown at charter: whether the harness terminates in the state its evidence
supports; whether Playwright provisions on the host under the current WAN
condition (INC-20260827-001); whether worktree-isolated parallel builders
satisfy Pattern #3's held condition in practice; the exact per-subagent
model-pin surface in the current Claude Code release; whether the 28-round
budget is reachable within session limits and whether `build_state.json`
resumption preserves evidence validity across sessions; any model-tier effect
on harness behavior (not separable at n = 1; observational only).

## 3  Success Criteria

1. Terminal state: the build ends in exactly one of PASS / BOUNDED_FAIL /
   BLOCKED / INVALID with an evidence-backed closeout, and an independent
   read of the on-disk record (`build_state.json`, `docs/rounds/`,
   `docs/critique/`, `docs/probe-qualification/`, `docs/LAYERS.md`,
   `SCOPE.md`) agrees the declared state is the one the evidence supports.
   BOUNDED_FAIL, BLOCKED, and INVALID are legitimate outcomes, never
   rewritten as PASS.
2. Objective gates evaluated from probe JSON observations, not narrative:
   exact identifier fixture targets correct; `status` and `lifecycle_state`
   never collapsed on any surface; flat hybrid the default with any
   degradation labelled; no write path from UI to corpus, cards, or index;
   no arbitrary text-to-SQL; typed relation direction preserved; gold-query
   compatibility through the adapter path not below the standing baseline
   (Recall@10 0.700 aggregate on Gold v1.1) unless explicitly scoped and
   evidenced in `SCOPE.md`.
3. Probe qualification precedes any product claim: the known-good case and
   all five known-bad classes (wrong document for identifier; stale or
   cross-wired card metadata; reversed relation direction; broken reader jump;
   console/runtime error) are demonstrated detectable on fixture substrate,
   evidence under `docs/probe-qualification/`, before the first round report
   cites a probe result.
4. Harness evaluation: a closeout ANL answers the four question groups of the
   rationale §13 (architecture, measurement, epistemic, autonomous behavior)
   with every answer cited to a specific on-disk build artifact. Absence of
   evidence for a behavior is recorded as absence, never inferred from the
   terminal state.
5. Subagent governance conformance: every dispatch carries `role`, `model`,
   `effort`, `pattern_primary`, `agent_type`, `execution_mode` in
   `build_state.json`; caps as ratified (§4); D-12 prohibition present on
   every strand prompt; zero unlogged tier escalations; the Pattern #3
   promotion disposition (promoted / held / rejected) is recorded from the
   build's own evidence.
6. Substrate untouched: the build makes no commit to the RHACO repository,
   `rhaco\RHACO_corpus_index.py` sha256 is unchanged open-to-close, no file
   under `docs\` is created or modified by the build, and the live
   `C:\RHACO\index\corpus_index.db` is never opened for write by any build
   process. Verified by the closeout hand, not asserted by the build.

Closure classifies H1 as SUPPORTED / PARTIALLY SUPPORTED / NOT SUPPORTED /
INDETERMINATE against (a)–(g) of §2. Criteria 1, 3, 5, and 6 are gating for a
SUPPORTED call; criterion 2 short of PASS with an honest BOUNDED_FAIL is
consistent with SUPPORTED — the harness question is whether the build told the
truth about itself, not whether the browser is finished.

## 4  Dependencies and Blockers

- BLOCKER: Subagent Pattern Application Guide v1.3 (CHG, filed alongside this
  charter) — adds the model-tier rule and extends the §6 handback schema with
  `model` and `effort`. The dispatch HND cites v1.3; it does not restate.
- BLOCKER: workspace repository created by the Director — separate private
  repo `C:\highsierralabs\RHACO_Corpus_Explorer\` (pattern: the
  `Epistemic_Operating_Style` repo), MCP-invisible, importing
  `rhaco.RHACO_corpus_index` and the librarian via a configured RHACO
  repo-root path. Ratified 2026-09-03 over an in-repo branch: it keeps the
  prompt's autonomous-commit clause inside a fixture repo, so the
  ratification-before-consequential-write rule holds unchanged for RHACO.
- BLOCKER: live verification of the per-subagent model-pin surface and the
  delegation-cap variables (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`,
  `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`) against the current Claude Code
  release, recorded in the HND §0 — the 20260815-001 criterion-4 discipline.
- DEPENDS ON: WAN sufficient for `playwright install chromium` and pip
  provisioning (INC-20260827-001 gate state confirmed at dispatch, not
  assumed).
- DEPENDS ON: RHACO-CMP-20260628-001 CLOSED with flat-hybrid default in force
  (satisfied; re-read at M0 — if the disposition has moved, the prompt's own
  §6 rule applies: current ratified evidence supersedes prompt text, recorded
  not silently followed).
- BLOCKS: nothing downstream. Reuse of the harness for any other RHACO build
  is a separate ratification informed by this campaign's §9.

Subagent governance ratified 2026-09-03 (carried into the HND as dispatch
parameters; the rule itself lives in Guide v1.3):

| Role | Model | Basis |
|---|---|---|
| Orchestrator / integrator | session model (Fable) | holds the harness, owns contracts and all synthesis (D-1) |
| Module builders | Sonnet 5 | bounded, spec'd work per module; write-scoped, worktree-isolated |
| Critic (non-coding) | Opus 5 | judgment-heavy; different model from builders, not claimed independent |
| Probe qualification, lint, fixture mechanics | Haiku 4.5 | mechanical, oracle-checked |
| Read-only inspection strands (prompt §1) | Sonnet 5 | Explore / Pattern #7 |

Escalation one tier up only on a recorded round report showing two failed
rounds on the same gate; logged, never silent. Caps:
`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` (workers spawn nothing — structural
D-4 and the 20260815-002 §2.2b compounding guard),
`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS=3` (one wave). The `--disallowed-tools`
suppression from the CMP-20260815-002 pilot is NOT inherited. The probe owns
the application server's lifecycle (child of the same foreground invocation,
readiness wait, teardown) — D-3 satisfied without background processes. Every
strand prompt carries the D-12 prohibition verbatim.

## 5  Plan and Milestones

**Milestone 0 —** Instrument freeze and governance riders. Guide v1.3 CHG filed;
  prompt and rationale landed verbatim in the workspace repo root
  (`PROMPT.md`, `RATIONALE.md`) and hash-pinned on disk; workspace repo
  created; Claude Code surface verification recorded. Gate: no builder round
  before the pins exist. Deliverable: CHG + pins recorded in §8.
**Milestone 1 —** Dispatch and Wave 1. HND authored (thin carrier: dispatch
  parameters, §0 pre-flight, governance riders, closeout obligations; the
  prompt is the payload, cited by pin, never paraphrased). Code discharges §0,
  runs prompt §1 (constraints, architecture), Wave 1 (`corpus_adapter`,
  `probe`, `diagnostics`), and probe qualification. Gate: criterion 3.
  Deliverable: HND + `working` handback with probe-qualification evidence.
**Milestone 2 —** Waves 2–3, acceptance, terminal state. Catalog / search /
  reader, then lineage / web integration; frozen workflow set W1–W10; critic
  rounds to convergence or budget; terminal state declared. Resumption across
  sessions via `build_state.json` per the HND protocol; each resumption logged.
  Deliverable: build closeout report in the workspace + handback.
**Milestone 3 —** Harness evaluation and closure. Closeout ANL per criterion 4;
  criterion 6 verification hand; Pattern #3 disposition; §9 closure. Any
  Guide, prompt, or harness revision arising is a downstream CHG or campaign,
  never an in-flight edit. Deliverable: ANL + closure statement.

## 6  Review Cadence

After each milestone (fixed). Event-triggered REVIEW on: any BLOCKED terminal
state; any need to edit prompt text (the instrument is frozen — an edit is a
version bump that reopens M0); any change to the retrieval dispositions of
record; any D-12 or cap violation observed in a handback; a
`build_state.json` resumption that cannot re-establish evidence validity.

## 7  Expected Deliverables

Guide v1.3 CHG; dispatch HND with on-disk pins; workspace repository
containing the explorer, `CONSTRAINTS.md`, `ARCHITECTURE.md`, `SCOPE.md`,
`docs/LAYERS.md`, `docs/REFERENCE.md`, probe-qualification evidence, round and
critic reports, `build_state.json`, and the build closeout; harness-evaluation
ANL; closure statement; Pattern #3 promotion disposition (as a Guide
amendment if promoted). A usable explorer is a welcome side effect, not a
criterion.

## 8  Campaign Log

2026-09-03 | OPEN | Campaign chartered. Pre-flight verified live: substrate
v1.5 surface, W7 mechanism present, gold sets located at `working\eval\`,
ANL-20260712-001 baseline pinned, Guide v1.2 read (no model-tier rule; #3
HELD; D-3/D-12 interactions identified). Director rulings this date: prompt
frozen as instrument, wrapped not converted; separate workspace repo; Pattern
#3 promotion case with worktree isolation; five-role model-tier map; Guide
v1.3 CHG filed alongside. Working inputs: the two uploaded files pinned in §2
item 5 (chat-side; on-disk pins at M0).

2026-09-03 | — | M0: Guide v1.3 cut (D-13, handback schema) via
CHG-20260903-001. Remaining M0 items: workspace repo, prompt landing and
on-disk pins, Claude Code surface verification.

2026-09-04 | M0 | COMPLETE 02:24:07Z (HND-20260903-001 Part A, session 3).
Workspace repo created; PROMPT.md / RATIONALE.md landed byte-identical to the
chat-side pins and committed unchanged (e9c9539); DISPATCH_PARAMETERS.md
assembled from HND section 2 as amended by A1 (8da0712). Claude Code 2.1.260
surface verified live: per-subagent model pin (Agent tool model enum; Workflow
opts.model / opts.effort), spawn depth 1 structural, concurrency cap NOT
client-enforced -- re-homed to the orchestrator by HND Amendment A1 (section 6
REVIEW not fired: a mechanism finding, not a cap violation). Pins of record:
handback section J.

2026-09-04 | M1 | Dispatch and Wave 1 CLOSED at the round-1 boundary 62685da
(session 3): CONSTRAINTS / ARCHITECTURE / SCOPE / REFERENCE / LAYERS from four
read-only inspection strands; corpus_adapter, probe, diagnostics built in
worktrees, merged, integrated (52 tests; L1 PASS). Gate criterion 3 read
progressively under Director ruling AC-3 (A2 section A2.2): Q0 qualified at
the correction round (session 4), Q1/Q2 at probe round 3, Q3 and FINAL at probe
round 4 (session 6, e36d9d6) -- criterion 3 satisfiable for the first time at
that point. L4 gold oracle: adapter == module 40/40; Recall@10 0.675 vs 0.700,
verdict SCOPE (corpus evolution, row 27; not an adapter regression).

2026-09-05 | M2 | TERMINAL STATE: BOUNDED_FAIL (PROMPT.md section 12), declared
once, at 20 of 28 builder rounds; workspace a87d259 pushed. Nine acceptance
gates PASS; production-path presets 11 of 12 (W5 red as declared, BF-1). The
section 12 scale-validity clause is vacuous (no calibrated exemplar, no second
scorer; two products scored) -- PASS unavailable on that route regardless of
score. Critic round 2 issue set not converged; no third round (same model, no
independence). Register: BF-1 (W5 tautology, probe budget exhausted), BF-2
(edges_for double-append, adapter-side), BF-3 (reader 1387 px, measured cause:
bare <code> sha256 at reader.html:132), scale validity, W5's four lost
assertions, O-4, O-6, SA-4 residual, import-check gaps, claim-audit deficiency
(P-21). Criterion 5: GD-1 (three session-6 dispatch records rebuilt after the
fact) reported as a defect with its repair. Criterion 6 asserted clean by the
build (no RHACO commit; module sha unchanged; docs unchanged; live db
byte-identical open-to-close) -- verification by the M3 closeout hand pending.
Section 6 REVIEW fired twice (session-5 safeguard model swap; session-7 Fable
re-entry), dispositioned MOD-1 and A (A2 section A2.5). Pattern #3 disposition
evidence: HE-3 both ways (isolation prevented the conflict and the detection).
Amendments A1 (3b860bf), A2 filed. M3 (harness-evaluation ANL; criterion-6
verification hand; #3 ruling; closure) OPEN.

2026-09-05 | -- | Docs tail per RHACO-CHG-20260905-001: this entry set;
CLAUDE.md section 5 pins; citation-auditor baseline re-seed.

2026-09-05 | M3 | CLOSED. Harness-evaluation ANL RHACO-ANL-20260905-001 filed at
f38e61a (31,386 B, sha256 c6b6421c...): the rationale's four question groups
answered with every answer cited to an on-disk artifact under working\m3_evidence\
(40 files, MANIFEST.md 51fa81df...) or the handback sections A-N; H1 (a)-(g) each
SUPPORTED at terminal, (c), (d), (g) only after correction by a ruling or an outside
reader. Gating criteria: 1 PASS; 3 PASS under AC-3; 5 met at terminal, defective in
process (GD-1); 6 PASS by the independent Code-side census of handback section N
(build commits 0; module sha 7548e47e... unchanged; index history reconciled to the
three A3.2 sources). H1 overall PARTIALLY SUPPORTED by the criteria's letter
(Director ruling 2026-09-05). Seal comparison: 4 of 5 defect items missed by harness
and critic, 3 of them prose-claim class (b); SA-6 satisfied unprompted; the ChatGPT
companion review opened post hoc under ruling 2(b) is the seal's own source, not a
second reader. Pattern #3 disposition: PROMOTED on first application, integration-
validity gate as the earned property (RHACO-CHG-20260905-002, Guide v1.4). Closure
per RHACO-CHG-20260905-003.

## 9  Closure Statement

Closed 2026-09-05 UTC. The campaign asked whether the Measurement-Philosophy-derived
autonomous build harness could construct a trustworthy comprehension layer over the
corpus substrate while preserving the authority boundary, the ratified retrieval
dispositions and evidence discipline, terminating in the state its evidence supports.
One build was run under the frozen prompt and the HND-20260903-001 governance
(sessions 1-8, 2026-09-03 to 2026-09-05); it terminated BOUNDED_FAIL at 20 of 28
builder rounds, declared from the prompt's own section 12 rule, with nine objective
gates PASS, 333 tests, 11 of 12 production-path presets, and a register of three
declared BOUNDED_FAIL items.

H1 is classified PARTIALLY SUPPORTED. Every sub-hypothesis (a)-(g) holds at terminal
(RHACO-ANL-20260905-001 section 4); the authority boundary was preserved to the byte
(criterion 6, verified by the closeout hand, not asserted by the build); the retrieval
dispositions were preserved and the status / lifecycle_state distinction was never
collapsed; the terminal state is the one the evidence supports (criterion 1). The
classification stops short of SUPPORTED because criterion 5 carries a ruled defect
(GD-1: three dispatch records absent at dispatch time, rebuilt from primary evidence
under Amendment A2 section A2.9), and because the record by which the harness
demonstrated (c), (d) and (g) was corrected by a Director ruling, by later sessions,
and by readers outside the harness rather than by any harness layer. The campaign's
central finding, and its primary template item, is that the harness tests behaviour
well and audits its own claims poorly: no layer reads a claim and then the artifact
it describes, four of five sealed defect items were missed by every layer and by the
critic, and the class regenerated three times inside the instruments built to end it
(ledger P-21). Its second finding is that record integrity fails at ungoverned
surfaces and is recovered, when it is recovered, by later readers and never by a gate
(GD-1, P-22, P-24). Its third is that client identity is a measurement variable that
must be read as a conjunction of surfaces (P-9, P-10, P-19).

Pattern #3 is PROMOTED on this first application (RHACO-CHG-20260905-002, Guide
v1.4), with the integration-validity gate as the earned property: disjoint write sets
establish mutation isolation, not semantic independence, and isolation prevents the
detection as surely as the conflict. n = 1; nothing here generalizes to the harness
in general, and nothing is claimed about model cognition. Any second run, prompt
revision, or claim-audit layer is a downstream ratification (section 6), not an
in-flight edit. The explorer is usable and remains a fixture. Deliverables of record:
RHACO-CHG-20260903-001 (Guide v1.3), RHACO-HND-20260903-001 + A1-A3, the workspace at
a87d259, RHACO-ANL-20260905-001, RHACO-CHG-20260905-002, this closure. Queue carried
to the Director: Q-1 (observatory-server write-path logging, mcp route), Q-2 (CMP
Specification v1.4 bold-run milestone leads), Q-3 (gate-then-amend-before-push
convention, SOP-20260708-001 candidate), the domain-agnostic build-prompt template
review.

Queue disposition appended post-closure (the charter stays CLOSED and its
card is untouched): **Q-1 DISCHARGED 2026-09-06** by RHACO-CHG-20260906-002 --
observatory MCP server 0.22.1, one instrument record per canonical-write
reindex through the existing census logger, carrying the origin tool, the
artifact basenames, the reindex result, and the index file's post-reindex size
and sha256; commits 88c69da, b5fee3a, a41bb15, live readback confirmed.

**Q-2 DISCHARGED 2026-09-06** by RHACO-CHG-20260906-001 -- CMP Specification
v1.4 cut, section 8 citation-anchor gate: every section 5 milestone lead a
bold run; commits 66c56aa, da47c2e, f2ac010.

**Q-3 DISCHARGED 2026-09-06** by RHACO-SOP-20260708-001 v4 Amendment A1 --
gate-then-amend-before-push, the measured gate tuple in the commit body before
the push, the body citing the tree sha; landed at f3a14fc.

**Template review DISCHARGED 2026-09-07** by RHACO-ANL-20260907-001 (evidence
map, criteria T1-T9, revision R1-R10 adopted) and RHACO-CHG-20260907-002
(RHACO_Build_Prompt_Template_v2_0 and Guide v2_0 cut to docs\reference).
Section 9 queue empty.

## 10  Cross-references

- Substrate campaigns: RHACO-CMP-20260624-001 (corpus knowledge database),
  RHACO-CMP-20260628-001 (retrieval layer, CLOSED)
- Dispositions of record: RHACO-ANL-20260712-001 (M3 gate; flat-hybrid
  standing; rerank negative result), RHACO-CHG-20260712-002 (M4 default flip)
- Governance: RHACO_Subagent_Pattern_Application_Guide_v1_2 (superseded by
  v1.3 at M0), RHACO_CMP_Specification_v1_3, RHACO_Card_YAML_Schema_Specification_v1_9
- Charter: RHACO_Measurement_Philosophy_v1_4_1 (Principles 1–7 map per the
  rationale §5)
- Methodological precedent: RHACO-CMP-20260815-002 (frozen-instrument-plus-
  dispatch pattern; delegation caps; model-identity ruling)
- Related incident: RHACO-INC-20260827-001 (WAN; Playwright provisioning gate)

---

*Reno High-Altitude Cosmic Ray Observatory (RHACO) | Kris E. Granholm, Director*
