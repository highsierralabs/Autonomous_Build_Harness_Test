# RHACO-CHG-20260907-004 — Build Prompt Template v2.1 and Guide v2.1: REF Cut from the External Review of v2.0

*Reno High-Altitude Cosmic Ray Observatory (RHACO) · 5,050 ft ASL · 39°N*
*RadiaCode RC-110-003225 · CsI(Tl) · 30 mm Pb walls / 40 mm Pb lid · sealed castle*

| Field | Value |
|---|---|
| Document type | CHG (Rule / schema codification — REF cut) |
| Status | Baseline |
| Execution route | `docs` |
| Target campaign | None — the v2.x lineage is a REF family; its validation run is a future charter, not this hand |
| Predecessor CHG | RHACO-CHG-20260907-002 (v2.0 cut) |
| Priority | HIGH — a control-flow defect in the v2.0 template must not survive into a validation build |
| Author | Kris E. Granholm, Director, RHACO |
| Date | 2026-09-07 UTC |
| Naming convention | v1.17 · Style RSG v1.9 · Schema Card YAML v1.9 · CHG Specification v1.0 |

## §1  Rationale

An external model review of the v2.0 cut (ChatGPT, 2026-09-07, saved at `working\RHACO_Build_Prompt_v2_0_Issues_And_Proposed_Fixes.md`, chat full-file pin `4fcc005d…` 22,416 B) reported eight prioritized issues and three refinements. Chat verified each against the on-disk v2.0 template (`3e248533…` 19,562 B) and guide (`c5146bf7…` 16,639 B); every factual claim about the text checked. The Director ratified the disposition below on 2026-09-07.

The one defect is normative. Template section 5 defines `ref_gap` with 10 = best and passes on `ref_gap ≥ PASS_THRESHOLD`; section 8 resumes each iteration from the module with the *largest* `ref_gap`; guide section 4 resumes from `min(ref_gap)`. The template contradicts itself and the guide contradicts the template. Executed literally, the loop re-iterates the strongest open module. This is exactly the prose-versus-mechanism divergence the v2.0 L5 layer exists to catch, found by an outside reader in the harness's own text.

Dispositions (review numbering): **P0 `ref_gap`** — adopt; rename to `ref_score`, higher is better, resume from `min(ref_score)`. **P1 fixture language** — adopt the generalized sentence; no new `PRODUCTION_INPUT_SOURCE` slot (slot creep; the guide's domain table already specializes). **P1 numeric convergence** — adopt, modified: repeatability is measured by scoring each calibration artifact twice, a step the template already has; a `round_delta` inside that spread is `unchanged`; escalation reads matched probe outputs and the ranked issue set, not a decimal. **P1 probe-claim rule** — adopt the narrowing to production-behaviour claims only; the proposed general rule already exists as the fifth Rules item and is not duplicated. **P1 PASS with `UNVERIFIED`** — adopt; clean = zero MISMATCH and zero `UNVERIFIED` on any claim a PASS criterion rests on. **P2 substrate invariants** — adopt as a per-entry invariant on the existing `SUBSTRATE_PATHS` slot, not a new slot. **P2 8–15 heuristic** — adopt. **P2 state-file framing** — adopt. **11.3 mechanical L5 qualification** — adopt; the citation auditor's silent-failure class (repo root versus docs root; path-spelling sensitivity; queued from RHACO-CCX-20260907-002, unfiled) is the on-disk instance a known-good/known-bad pair would have caught. **11.2 gate-over-score sentence** — adopt as one sentence. **11.1 `REFERENCE_CORPUS` rename** — skip; defensible as a generic term, ten occurrences, no leverage. **Review section 13 (V1–V8 validation targets)** — not a template edit; parked as seed material for the validation charter.

The review's premise under P2 substrate invariants — that the RHACO run saw authorized external writes to live state during the campaign — was not verified by chat against the evaluation ANL; the disposition does not depend on it. Hash equality is one implementation of a control, not the control.

Version: **v2.1**, not 2.0.1 — P0 changes control flow. Per CHG Specification v1.0 section 8 the bump is a new cut, never an in-place edit: v2.1 is produced by applying the CS-1 and CS-2 edit lists to byte copies of the v2.0 files; the v2.0 pair stays on disk, cards flipped to Superseded. No run has validated any v2.x mechanism; v2.1 inherits v2.0's n = 1 provenance and says so.

Pins (chat full-file): template v2.0 `3e2485…` 19,562 B; guide v2.0 `c5146b…` 16,639 B; review memo `4fcc00…` 22,416 B; RHACO-CHG-20260907-002 card `e9781e…` 3,539 B. Server 0.22.1, librarian 1.19, NC 1.17, head `4d0d86d`, corpus-index card count 1472 (index readback, not a census).

## §2  Change Specification

Edit form throughout: anchor text is quoted as it stands in v2.0; the executor asserts anchor count == 1 in the copy before replacing; a count ≠ 1 is a HALT. Wording inside replacement blocks lands verbatim. Where a replacement contains a slot, the `{{SLOT}}` form is preserved.

### CS-1  `docs\reference\RHACO_Build_Prompt_Template_v2_1.md` — new REF, from a byte copy of v2.0 with edits T-1 … T-14

**T-1  Header.** `*Reference Document | Version 2.0 | September 7, 2026*` → `*Reference Document | Version 2.1 | September 7, 2026*`. `*Companion to: RHACO_Build_Prompt_Template_Guide_v2_0, RHACO_Measurement_Philosophy_v1_4_1*` → `*Companion to: RHACO_Build_Prompt_Template_Guide_v2_1, RHACO_Measurement_Philosophy_v1_4_1*`.

**T-2  Provenance paragraph.** Append, after the sentence ending `(RHACO-CMP-20260903-001; n = 1).`, one sentence: `v2.1 applies the ratified dispositions of an external model review of v2.0 (RHACO-CHG-20260907-004): one control-flow defect, six semantic tightenings, three generalisations; no run has yet validated any v2.x mechanism.`

**T-3  Section 2, fixture paragraph.** Replace the whole paragraph beginning `**A fixture is derived, not authored.**` with:

```
**A fixture is derived, not authored.** Where the probe uses a fixture, derive it from the production input source's runtime-resolved schemas, types, ranges and value shapes — records, payloads, rows, frames, files, traces, whatever the deliverable actually consumes — and record a fixture-versus-production census of the properties that bear on the verification target as a round-0 inspection output; a hand-authored fixture reproduces its authors' conventions, not the production input's variance.
```

**T-4  Section 2, bold rule.** `**No agent may claim anything it has not run the probe on and inspected.**` → `**No agent may make a production-behaviour claim from a probe it has not run and inspected.** Claims of other kinds — structural, provenance, authority, record — cite the layer or check that supports them (Rules).`

**T-5  Section 5, `ref_gap` bullet.** `- \`ref_gap\`: distance from {{REFERENCE_CORPUS}} on the anchored 0–10 scale — 10 =` → `- \`ref_score\`: quality against {{REFERENCE_CORPUS}} on the anchored 0–10 scale, higher is better — 10 =` (rest of the line unchanged).

**T-6  Section 5, `round_delta` bullet.** `- \`round_delta\`: change since the previous round on the same presets — converging, oscillating, or thrashing, which the absolute score buries` → `- \`round_delta\`: change since the previous round on the same presets — converging, oscillating, or thrashing, which the absolute score buries; read as a number only inside the critic's measured repeatability (below), otherwise as improving / unchanged / worsening plus the ranked issue-set delta`

**T-7  Section 5, calibration paragraph.** After the sentence `Before wave 1 completes, the critic scores {{CALIBRATION_ARTIFACTS}} and records the results in \`docs/REFERENCE.md\`.` insert: `Each calibration artifact is scored twice, the second time blind to the first; the spread is the critic's repeatability, recorded beside the anchors, and a \`round_delta\` inside it is \`unchanged\` whatever its decimal.`

**T-8  Section 5, pass paragraph.** Replace the whole paragraph beginning `Pass = \`ref_gap\` ≥ {{PASS_THRESHOLD}}` with:

```
Pass = `ref_score` ≥ {{PASS_THRESHOLD}} with {{ZERO_TOLERANCE_CONDITION}} and every objective gate green; a critic score never compensates for a failed objective gate. Below that, the builder receives the ranked issue list and goes again, up to {{MAX_ROUNDS}} rounds. A module at {{MAX_ROUNDS}} whose matched probe outputs and ranked issue set show no material change across its last two rounds is escalated to the integrator as a suspected contract problem, not given more rounds.
```

**T-9  Section 5a, append.** After the sentence ending `there is no third state.` append, same paragraph:

```
 The audit is **clean** when it carries zero MISMATCH and zero `UNVERIFIED` on any claim a PASS criterion rests on — a required capability, an objective gate, the authority boundary, a terminal-state decision, or an externally presented behaviour claim; every other `UNVERIFIED` may stand at PASS only if it is listed in `SCOPE.md` or the terminal record and cited by no PASS criterion. Where any part of the audit is mechanical — a citation resolver, a docstring-versus-signature check — that tool is an instrument: before its MATCH verdicts support PASS, show it returns MATCH on one known-good claim and MISMATCH on one known-bad, evidence under `docs/probe-qualification/`; a reader's judgement is not qualified this way and `docs/LAYERS.md` says so. *(P2)*
```

**T-10  Section 8.** `Persist to \`{{STATE_FILE}}\`: per module, \`ref_gap\`, \`round_delta\`,` → `Persist to \`{{STATE_FILE}}\`: per module, \`ref_score\`, \`round_delta\`,`. And `Each iteration resumes from the module with the largest \`ref_gap\`.` → `Each iteration resumes from the open module with the lowest \`ref_score\`.`

**T-11  Section 9, PASS bullet.** `\`ref_gap\` reaches {{PASS_THRESHOLD}} on a calibrated scale` → `\`ref_score\` reaches {{PASS_THRESHOLD}} on a calibrated scale`.

**T-12  Authority boundary, closeout paragraph.** Replace the paragraph beginning `At closeout, a hand outside the build verifies the substrate untouched` with:

```
At closeout, a hand outside the build verifies the authority boundary and records it. `CONSTRAINTS.md` names, in advance, the invariant that hand checks for each {{SUBSTRATE_PATHS}} entry, and the control must be one capable of detecting a violation: for a frozen artifact, hash before equals hash after; for a repository, no build-attributable commit and no dirty protected path; for a live store or service, no build-origin write in the store's own audit and every observed change reconciled to an authorized external writer. Hash equality is one such control, not the rule — a changed hash proves nothing about who wrote, an unchanged one proves nothing about transient writes. The build asserts nothing here; it is measured.
```

**T-13  Authority boundary, guidance comment.** `<!-- SUBSTRATE_PATHS: the corpus, database, service or repository the artifact reads and must never write.` → `<!-- SUBSTRATE_PATHS: the corpus, database, service or repository the artifact reads and must never write, each with the closeout invariant that proves it.` (rest of the comment unchanged).

**T-14  Version History.** Append row: `| 2.1 | 2026-09-07 | Applies the ratified dispositions of an external review of v2.0. Control flow: \`ref_gap\` renamed \`ref_score\` (higher is better), resume from the lowest open score (5, 8, 9). Semantics: clean claim audit defined against PASS criteria; mechanical sub-auditors qualified like the probe (5a); critic repeatability measured on the calibration artifacts and bounding any numeric \`round_delta\`; escalation reads probe outputs and the issue set, not a decimal; gate over score (5); probe-claim rule narrowed to production-behaviour claims (2); closeout by per-substrate invariant, hash equality one instance (Authority boundary). Generalisation: fixture derivation freed of corpus vocabulary (2). No v2.x mechanism validated by any run. Cut by RHACO-CHG-20260907-004. |`

Residual global check: after T-1 … T-14 the string `ref_gap` occurs zero times in the v2.1 template [VERIFY by grep]; `production corpus` occurs zero times [VERIFY]; `{{` count equals the v2.0 count [VERIFY — no slot added or removed].

### CS-2  `docs\reference\RHACO_Build_Prompt_Template_Guide_v2_1.md` — new REF, from a byte copy of v2.0 with edits G-1 … G-12

**G-1  Header.** `*Reference Document | Version 2.0 | September 7, 2026*` → `*Reference Document | Version 2.1 | September 7, 2026*`. `*Companion to: RHACO_Build_Prompt_Template_v2_0*` → `*Companion to: RHACO_Build_Prompt_Template_v2_1*`.

**G-2  Section 1, last paragraph.** Replace `Everything else (waves, integrator, blind gate, state file) reduces cost and thrash.` with:

```
The state file is not one of the cost reducers. It is the persistent epistemic record — critic state, invalidated evidence, `UNVERIFIED`, assumptions, dispatch records, identity history, layer gaps, terminal state — that keeps the findings above intact across rounds and lets a later run resume without inventing state; the RHACO run reconstructed three dispatches after the fact for want of it. Waves, integrator ownership and the blind gate mainly reduce coordination failure, correlated judgement and thrash.
```

**G-3  Section 2, first sentence.** `Use it when all of the following hold: the deliverable splits into 8–15 subsystems with real interfaces;` → `Use it when all of the following hold: the deliverable contains several independently ownable subsystems with real interfaces and benefits from separate builder, integrator and critic roles (roughly 8–15 modules is a useful starting range from one run, not a rule);`

**G-4  Section 3, `MODULE_LIST` row.** `| \`MODULE_LIST\` | 8–15 nouns. Each becomes` → `| \`MODULE_LIST\` | One noun per independently ownable subsystem — roughly 8–15 in practice. Each becomes` (rest of the row unchanged).

**G-5  Section 3, fixtures line.** `Fixtures: derive from the production corpus's loader-resolved types; census fixture-vs-production types at round 0.` → `Fixtures: derive from the production input source's runtime-resolved types, ranges and value shapes; census fixture-vs-production at round 0.` (rest of the paragraph unchanged).

**G-6  Section 3, `CALIBRATION_ARTIFACTS` row.** `| \`CALIBRATION_ARTIFACTS\` | Three things of known quality. Without them the scale is ordinal: say so in SCOPE.md and never read PASS from it. |` → `| \`CALIBRATION_ARTIFACTS\` | Three things of known quality, each scored twice; the spread is the critic's repeatability and the floor under any numeric \`round_delta\`. Without them the scale is ordinal: say so in SCOPE.md and never read PASS from it. |`

**G-7  Section 3, claim-audit row.** After `Every prose behaviour claim ends up with a named check or an \`UNVERIFIED\` tag.` append, same cell: ` A mechanical sub-auditor is qualified like the probe — one known-good, one known-bad — before its MATCH counts toward PASS. Clean = zero MISMATCH and zero \`UNVERIFIED\` on any claim a PASS criterion rests on.`

**G-8  Section 3, `SUBSTRATE_PATHS` row.** `Verified by a closeout hand with hashes, never asserted by the build.` → `Each entry names its closeout invariant in CONSTRAINTS.md (hash equality for a frozen artifact; commit and dirty-path census for a repository; the store's own write audit for a live store or service); verified by a closeout hand, never asserted by the build.`

**G-9  Section 4, state-file schema and text.** In the JSON block: `"ref_gap": 8.1` → `"ref_score": 8.1`; `"ref_gap": 8.6` → `"ref_score": 8.6`; `"whole_ref_gap": null` → `"whole_ref_score": null`; `"claim_audit": { "last_run": "...", "match": 169, "mismatch": 0, "unverifiable": 8 }` → `"claim_audit": { "last_run": "...", "match": 169, "mismatch": 0, "unverifiable": 8, "unverifiable_material": 0 }`. In the prose below the block: `"Resume from the weakest module" is \`min(ref_gap)\` over \`status == open\`.` → `"Resume from the weakest module" is \`min(ref_score)\` over \`status == open\`; \`unverifiable_material\` counts the \`UNVERIFIED\` entries a PASS criterion rests on and must read 0 at PASS.`

**G-10  Section 8, failure-modes row.** `| Derive the fixture from loader-resolved production types; type census at round 0 |` → `| Derive the fixture from the production input source's runtime-resolved types; census at round 0 |`

**G-11  Section 10, checklist.** `- [ ] \`SUBSTRATE_PATHS\` named; closeout hand assigned` → `- [ ] \`SUBSTRATE_PATHS\` named, each with its closeout invariant; closeout hand assigned`. After `- [ ] Claim-audit grammar boundary stated in LAYERS.md` insert `- [ ] Mechanical claim-audit tools qualified on one known-good and one known-bad`.

**G-12  Version History.** Append row: `| 2.1 | 2026-09-07 | Companion to Template v2.1. \`ref_gap\` renamed \`ref_score\` in the schema and the resume rule; \`unverifiable_material\` added to the claim-audit record; state file reframed as the persistent epistemic record (1); 8–15 modules recast as a heuristic (2, 3); fixture derivation generalised (3, 8); calibration repeatability, mechanical sub-auditor qualification and clean-audit definition added to the critic block (3); per-substrate closeout invariants (3, 10). Cut by RHACO-CHG-20260907-004. |`

Residual global check: `ref_gap` zero occurrences in the v2.1 guide [VERIFY]; `production corpus` zero occurrences [VERIFY]; the section 9 worked instance and section 7 cost figures are untouched.

### CS-3  Cards for CS-1 and CS-2 (new, Code)

Two sibling `.card.yaml` modelled byte-shape on the live v2.0 REF cards [executor: `get_card` both; mirror field shapes]. `current_version` quoted `"2.1"`; status `Active`; programs `[Infra]`; `depends_on` → RHACO-CHG-20260907-004, RHACO_Build_Prompt_Template_v2_0 (or Guide v2_0 respectively; note "predecessor cut, superseded by this version"), RHACO_Measurement_Philosophy_v1_4_1; `see_also` → RHACO-CHG-20260907-002, RHACO-ANL-20260907-001, RHACO-CMP-20260903-001; abstract authored from the landed v2.1 body, not from this CHG.

### CS-4  v2.0 cards → Superseded (in-place, Code)

`RHACO_Build_Prompt_Template_v2_0.card.yaml` and `RHACO_Build_Prompt_Template_Guide_v2_0.card.yaml`: `identity.status: Active` → `Superseded`; `superseded_by: null` → mapping `{id: RHACO_Build_Prompt_Template_v2_1, note: "v2.1 cut by RHACO-CHG-20260907-004; v2.0 retained as the pre-review record"}` (Guide: `id: RHACO_Build_Prompt_Template_Guide_v2_1`); `last_human_review` → `"2026-09-07"`; one notes entry naming this CHG. The two fields move together (Channel 1 rule). Bodies untouched.

Not directed: the review memo under `working\` (retained, not carded, not edited — its dispositions are recorded in section 1 above so the record does not depend on it); the Corpus Explorer run record and its `build_state.json` (field name `ref_gap` stays as the run wrote it; the template is the reference, not the run); the Measurement Philosophy; any code; the two rule-level auditor findings queued from RHACO-CCX-20260907-002 (still unfiled; named here as motivation only).

## §3  Changes Directed

None to production code. Executor: Claude Code under `/ho`, route `docs`, on `main`, Rule-2 commits, one doc-id at position 0 (this CHG's); gate-then-amend-before-push per RHACO-SOP-20260708-001 v4 Amendment A1, each body citing the tree sha its gate measured. Client identity read at entry as the P-19 conjunction including effort and the settings-file sha, against the most recent pin of record on disk [VERIFY: the RHACO-CHG-20260907-001 execution record or the RHACO-CHG-20260907-003 section 5 pin, whichever is later]; a sha change is a HALT for a ruling.

| # | Commit subject (ASCII, ≤72) | Content |
|---|---|---|
| 0 | `RHACO-CHG-20260907-004: file build prompt template v2.1 carrier CHG` (67) | this pair (chat-written via MCP) |
| 1 | `RHACO-CHG-20260907-004: land build prompt template and guide v2.1` (65) | CS-1, CS-2, CS-3 |
| 2 | `RHACO-CHG-20260907-004: supersede v2.0 REF cards and discharge` (62) | CS-4; this CHG body Status → Baseline, card → Baseline, section 5 Execution Record |

Pre-flight: hash the two v2.0 files and the review memo against the section 1 pins; copy each v2.0 file byte-for-byte to its v2.1 name; apply the edit lists in order, asserting anchor count == 1 before each replacement and running the residual global checks after; re-hash both v2.1 files and record in section 5. Expected gate: librarian MATCH at the census-of-record plus 2; auditor at its baseline of record [VERIFY the live number — do not carry 314 from memory] or +N attributable to this pair and the two REFs — attribute, do not baseline, do not waive. Halt-and-report on any pin mismatch, any anchor count ≠ 1, any residual-check hit, an unexpected auditor member, or a librarian MISMATCH.

## §4  Cross-references

RHACO-CHG-20260907-002 (predecessor; v2.0 cut; section 5 artifact pins) · RHACO-ANL-20260907-001 (the review that produced v2.0; R1–R10) · RHACO-ANL-20260905-001 (evaluation of record) · RHACO-CMP-20260903-001 (the n = 1 run; CLOSED, untouched) · RHACO-CCX-20260907-002 (queued auditor findings named in section 1) · RHACO_Measurement_Philosophy_v1_4_1 (P2, P4, P5, P7 as cited in the edits) · RHACO_CHG_Specification_v1_0 section 8 (REF cuts) · RHACO_Card_YAML_Schema_Specification_v1_9 (Superseded / superseded_by pairing) · RHACO-SOP-20260708-001 v4 Amendment A1 (commit form) · `working\RHACO_Build_Prompt_v2_0_Issues_And_Proposed_Fixes.md` (the external review; uncarded, ops grey-zone).

## §5  Execution Record

Executed 2026-09-07 by Claude Code under `/ho`, route `docs`, on `main`, from clean base `4d0d86d`. Three commits under this identifier, preceded by one swept commit under its own.

**Pre-flight, all four pins matched.** Template v2.0 `3e248533091b`, 19,562 B; Guide v2.0 `c5146bf76762`, 16,639 B; review memo `4fcc005da2ee`, 22,416 B; the predecessor's card `e9781edf2679`, 3,539 B. Census of record at entry: 1,473 cards, no missing, three orphans, 128 carded-with-parent, none carded-with-code, no broken, no errors, baseline MATCH.

**Client identity, and a correction to this document's own section 3.** The pointer in section 3 sends the executor to the RHACO-CHG-20260907-001 execution record or to this hand's predecessor carrier for the pin of record. Neither carries a client-identity pin. The most recent pin of record on disk is RHACO-CCX-20260907-002, its pre-flight item 4, and the observed conjunction matches it exactly: settings file sha256 `c4964b786a6aa3c341799a3089e4ccefd650c9a240e3a8eb96f31341202cb0b3`, 9,096 B; model key `claude-opus-5[1m]`; `switchModelsOnFlag` false; client 2.1.260. The pointer was a chat-side authoring error, not a missing record, and no sha changed. One reading differs from that pin's narration: the effort in force is `xhigh`, not `high`. The settings file scopes effort per model — `claude-opus-5` to `high`, `claude-opus-5[1m]` to `xhigh` — and the session model is the long-context entry. The bytes are identical to the pinned bytes, so this is a derivation reading of the same file, not a between-session edit.

**Landed artifacts.**

| Artifact | sha256 | Bytes |
|---|---|---|
| `RHACO_Build_Prompt_Template_v2_1.md` | `6ee71cf7a16a4b63927fb11f30bb8ab07f2ef7ea30c664711dc4f6fa131b5b2d` | 22,742 |
| `RHACO_Build_Prompt_Template_Guide_v2_1.md` | `50c397f3bdf8418274d1a0a90e02961030367661270b1cdb3019a2c2e410c3c4` | 18,614 |

**Edit execution.** All fifteen template anchors and all sixteen guide anchors asserted at count 1 before any byte was written, in one transactional pass that writes nothing unless every assertion holds; both version-history rows were extracted from this document rather than retyped, so they landed verbatim. No anchor was ambiguous and no count deviated. The residual global checks pass on every term but one, below.

**Residual check — one hit, and it is this document's own internal contradiction.** Section 2 requires that `ref_gap` occur zero times in each v2.1 file, and also requires that the appended version-history rows land verbatim. Those two directives cannot both hold: each row describes the rename and therefore names the retired field. One occurrence survives in each file, in the version-history row and nowhere else; both normative bodies carry none. This is a defect in the change specification, not in its execution, and it is recorded rather than resolved by editing the mandated rows. Each new card carries the same note.

**Instrument note — the line-ending probe failed exactly as its own rule predicts.** Both v2.0 files are LF with zero CR bytes. An initial pattern-matching probe reported them CRLF at 171 and 211 lines, a false positive of the class the census/librarian rules record as a founding incident: a probe that can only answer yes is indistinguishable from a working one. The transactional precondition refused to write on the contradiction, the probe was replaced with a CR-byte count, and the cut proceeded. Nothing was written under the wrong reading. Both landed files are LF with zero CR bytes.

**Acceptance, at recorded delta.** The base state carries two gate members red, both inherited and both owned: regression by RHACO-INC-20260829-001 and RHACO-INC-20260830-001, and the auditor by a single standing add. Per Director ruling of 2026-09-07 this hand is accepted on the form its two predecessors used — delta 0 against base, not absolute green.

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| 1 | Section 1 pins match on disk | PASS | All four, exact on digest and byte count |
| 2 | Every anchor count 1; a deviation is a halt | PASS | 31 of 31 asserted before the first write; none deviated |
| 3 | Residual global checks | PASS with one recorded hit | Slot count unchanged at 64; the retired corpus phrase at zero in both files; the retired field at zero in both normative bodies, surviving once per file in the mandated version-history row |
| 4 | Librarian at the census of record plus two | PASS | 1,475 cards, no missing, three orphans, 128 carded-with-parent, none carded-with-code, no broken, no errors, baseline MATCH; warning breakdown identical to base |
| 5 | Regression at recorded delta, membership exactly the two owned members | PASS | 837 passed, 2 failed, 1 skipped at base; the gate's member observes 2 failures after the hand, the same two, delta 0 |
| 6 | Auditor delta 0 against base; an attributable add is a halt | PASS | Unwaived gating 315, one add, no removes, at base and after the cut. The add is sourced from RHACO-CCX-20260907-001 and is attributable to neither this pair nor the two new documents. Citations, unresolved, anchor-missing and waived all unmoved; only the file count moves, by the two documents added |
| 7 | Structure guard green as at base | PASS | Self-test green |

**Closeout gate.** Run against `C:\RHACO` on the clean tree of this commit, tree sha `24f02fbb3fb6696a640d25a4e56e8888919025dc`. Librarian PASS, structure guard PASS, git-status-clean PASS; regression and auditor red at their inherited, owned states with delta 0 on both. Overall exit 1, accepted at recorded delta under the Director ruling of 2026-09-07, on the form the two preceding hands used. The gate ran three times with identical results.

**Instrument note — the gate's per-member status line reports the child's last line, not its verdict.** The `[FAIL] regression` line relays a single finding, so a member observing two failures displays one. Read literally it looks like a one-member delta against a two-member base; the child output under `--verbose` reads `observed 2 FAIL(s)` and names both. This was misread once here before the verbose output settled it. Nothing was accepted on the wrong reading, and the display is cosmetic — the exit code, which is the verdict, is unaffected — but a delta-aware acceptance rule is read off exactly this line, and there it can turn an unchanged member into an apparent improvement. Recorded for the routing-instrument backlog; not this hand's to fix.

**Deviation on execution — none in direction.** Every change specification landed as written. The two departures from this document's own text are both in its premises: the section 3 identity pointer, corrected above, and the section 2 residual check, recorded above. Both are chat-side authoring misses; neither altered what was built.

**Commit ledger.**

| Step | Commit | Note |
|---|---|---|
| Sweep, under its own identifier | `78ef732` | RHACO-CCX-20260907-003 pair, swept ahead of this hand per Director ruling |
| 0 | `6177ce4` | This document and its card |
| 1 | `af8cc4a` | CS-1, CS-2, CS-3 — the v2.1 pair and their cards |
| 2 | (this commit) | CS-4, both channels of this document to Baseline, and this record |

---

*Reno High-Altitude Cosmic Ray Observatory (RHACO) | Kris E. Granholm, Director*
*RadiaCode RC-110-003225 | CsI(Tl) | 30 mm Pb walls / 40 mm Pb lid | 5,050 ft ASL, Reno NV*
