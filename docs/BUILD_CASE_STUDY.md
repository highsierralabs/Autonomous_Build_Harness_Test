# How the Corpus Explorer was built

**A case study in adapting a game-building prompt into a measurement-governed autonomous software build.**

This document explains the experiment and its provenance for readers outside RHACO. It distinguishes what the prompt required, what the build recorded, and what was changed later. The original [`../PROMPT.md`](../PROMPT.md) and [`../RATIONALE.md`](../RATIONALE.md) remain the primary design records; this is a retrospective guide, not a replacement or a rewritten instruction to rerun the build.

## 1. Two objectives in one project

The immediate software need was straightforward: RHACO had a structured document corpus and machine-facing search, but not a direct human interface for browsing the resulting research record. The intended application would be a local, read-only, no-frontier-LLM explorer for documents, metadata, search, and recorded lineage.

The research objective was separate: test whether a bounded autonomous-build prompt, rewritten under RHACO's Measurement Philosophy, could produce that application while preserving authority boundaries and describing its own evidence accurately. The campaign explicitly treated the **build harness as the object under evaluation** and the Explorer as its real-world software artifact. Its scope was one frozen prompt executed once, not a statistical evaluation of autonomous agents generally.

The September 3–5, 2026 campaign is [RHACO-CMP-20260903-001](campaign/RHACO-CMP-20260903-001_Corpus_Explorer_Autonomous_Build_Harness.md). The historical analysis is [RHACO-ANL-20260905-001](campaign/RHACO-ANL-20260905-001_Corpus_Explorer_Harness_Evaluation.md). Both are RHACO records; the copies linked here are hash-pinned, unedited snapshots under [`campaign/`](campaign/), described in its [`MANIFEST.md`](campaign/MANIFEST.md).

## 2. The prompt lineage, in chronological order

```text
rawprogress/fable-cities PROMPT.md
        |  structural inspiration (accessed Sept 3, 2026)
        v
Generalized autonomous build-prompt structure (working draft)
        |
        v
Measurement-Philosophy rewrite (working draft)
        |
        +------> Frozen Corpus Explorer PROMPT.md + RATIONALE.md
        |          (Sept 3–5 pilot; one instantiation)
        |                         |
        |                         v
        |                  Evidence and findings
        |                         |
        +-------------------------+
                                  v
                  RHACO build-prompt template v2.0
                         (Sept 7, 2026)
                                  |
                                  v
              v2.1 (Sept 7, 2026; external review of v2.0)
                                  |
                                  v
        v2.2 (Sept 20, 2026; provenance correction, no mechanism change)
```

**External structural inspiration.** The starting source was [`rawprogress/fable-cities/PROMPT.md`](https://github.com/rawprogress/fable-cities/blob/main/PROMPT.md), accessed September 3, 2026, around 15:30 UTC. RHACO did not record the upstream commit at the time, and it did not keep the retrieved bytes. RHACO's template v2.0 and v2.1 said otherwise: they stated that the file as retrieved had been retained in working material. A pre-publication check found that the named file is RHACO's own first generalisation of the structure, not the upstream file, and template v2.2 corrects the statement ([change record](campaign/RHACO-CHG-20260920-001_Build_Prompt_Template_v2_2_REF_Cut_Provenance_Correction.md)).

What can be said now: measured on September 20, 2026, the upstream's public history is a single commit, `aea8b1035030952555395de0c1de14ba693a1427`, committed 2026-09-02T22:47:42Z, about seventeen hours before the access. Its `PROMPT.md` is git blob `c2bc981d4af76130f8ad88f2ddd857491c517c72`, 5,742 bytes, and is the only version that history carries. That makes it a strong inference, not a captured fact, that this is the text RHACO read: a rewrite of the upstream history after the access would leave no trace. The upstream is MIT-licensed, and a copy retrieved on September 20 is kept with its licence under [`campaign/upstream/`](campaign/upstream/).

**RHACO adaptation.** An initial generalized structure ([v0](campaign/unfiled/PROMPT_TEMPLATE.md)) was rewritten against RHACO Measurement Philosophy v1.4.1 ([v1](campaign/unfiled/PROMPT_TEMPLATE_CHARTER.md)); neither was ever filed as a governed document, and both are included as found. The resulting Corpus Explorer-specific [`PROMPT.md`](../PROMPT.md) and [`RATIONALE.md`](../RATIONALE.md) were frozen as experimental inputs before the build. Their task was not to recreate a city-building game: it was to transfer an autonomous-build structure to a constrained, evidence-sensitive document browser.

**Post-pilot template.** The generalized [RHACO Build Prompt Template v2.0](campaign/RHACO_Build_Prompt_Template_v2_0.md) is dated **September 7, 2026**, two days after the Explorer pilot closed. It incorporates revisions derived from this build's evaluation. It therefore must not be listed as the executable template used by the September 3–5 run. [v2.1](campaign/RHACO_Build_Prompt_Template_v2_1.md) followed the same day, from an external review of v2.0 that found a control-flow contradiction in the template's own text. [v2.2](campaign/RHACO_Build_Prompt_Template_v2_2.md), dated September 20, corrects the provenance statement described above and changes no mechanism. This chronology is important evidence about which safeguards were available during the experiment and which arose from its failures. The changes are traced one by one in [How the prompt changed](PROMPT_EVOLUTION.md).

## 3. What was transferred—and what was changed

The useful transferable structure was an agent-directed build brief that describes the target artifact, divides it into subsystems, coordinates builders, repeatedly measures their work, records decisions, and terminates against explicit criteria rather than stopping when the output looks plausible.

RHACO changed the purpose and rigor of the structure in several concrete ways:

| Area | Corpus Explorer adaptation | Why it matters |
|---|---|---|
| Goal | Replace a game-like target with a local research-document comprehension tool. | The artifact must preserve and expose sources, not optimize visual resemblance or produce generative answers. |
| Constraints | Inspect RHACO's existing index, schema, retrieval dispositions, environment, and authority boundaries **before** choosing the architecture. | Prevents an autonomous builder from treating an existing system as a blank slate. |
| Module work | Assign bounded ownership to adapter, catalog, search, reader, lineage, diagnostics, web, and probe; integration owns shared contracts. | Makes concurrent work governable and contract changes visible. |
| Verification | Require an instrument that drives the real browser/server path and captures screenshots plus structured observations. | Evaluation is about observable behavior, not the builder's narrative. |
| Probe qualification | Use known-good and deliberately faulty fixture cases to test whether the observer can recognize failures. | A passing probe is uninformative if it cannot detect a known error. |
| Evidence | Compare outcomes with existing corpus evaluations and document shared dependencies among checks. | Multiple checks relying on the same source are not independent proof. |
| Authority | Make documents/cards canonical; keep the UI read-only; prohibit invented edges, SQL generation, and unearned authority claims. | The software cannot silently upgrade retrieval output into research truth. |
| Ending | Use bounded rounds and explicit PASS / BOUNDED_FAIL / BLOCKED / INVALID states. | An incomplete build must be allowed to say so without lowering the bar. |

This adaptation is tied to RHACO's [Measurement Philosophy](MEASUREMENT_PHILOSOPHY.md), which is to this prompt what *Cities: Skylines II* is to the original: accept real constraints as architectural inputs; make the instrument's state observable; use layered but dependency-aware checks; use measured differences rather than unsupported improvement claims; retain negative results; preserve reasoning as inspectable artifacts; and bound conclusions to the evidence.

These are design intentions and documented requirements. They are not, by themselves, proof that each was implemented successfully.

### A more direct comparison with the Cities prompt

The following comparison is based on inspection of the [currently accessible `fable-cities/PROMPT.md`](https://github.com/rawprogress/fable-cities/blob/main/PROMPT.md) and the frozen Explorer prompt. The upstream's public history holds one commit, which predates RHACO's access, so the currently accessible file is the only version that history shows. RHACO did not capture the bytes it read, and an upstream history rewrite cannot be excluded, so this comparison still does **not** establish a byte-for-byte historical diff.

| Element in the Cities prompt | Explorer adaptation | Meaningful change |
|---|---|---|
| A target city builder with explicit visual and performance goals. | A browser whose acceptance goals are correct retrieval, canonical reading, lineage, and authority boundaries. | Correctness and traceability replace visual fidelity as the core evidence. |
| `ARCHITECTURE.md` first, with subsystems and a shared world model. | Inspect existing RHACO constraints *before* architecture; specify a read-only corpus adapter and separate UI modules. | The target is an existing institution's system, not an empty-folder greenfield build. |
| Screenshot tool and JSON performance observations before game features. | A production-path Playwright browser probe with screenshots, JSON, named workflows, and known-good/known-bad qualification. | The observer must demonstrate that it can detect wrong documents, cards, directions, navigation, and runtime faults. |
| One module builder per folder, waves, and a shared-core integrator. | Owned modules, isolated worktrees, change requests, and explicit contract revalidation. | Parallel work must obey the corpus and integration authority boundary. |
| An art-director critic and anchored visual 0–10 comparison with Cities: Skylines II; blind screenshots as a final gate. | Static checks, behavioral browser checks, a critic, and target-based corpus oracles; an uncalibrated critic score cannot by itself license PASS. | There is no established comparable visual product benchmark for the Explorer; objective domain-specific checks take priority. |
| `/loop` until critics pass, with persistent `docs/STATUS.json`. | Frozen round budgets, `build_state.json`, preserved issues, and explicit non-PASS terminal states. | The system is permitted—and required—to stop with a bounded failure if evidence is insufficient. |

The transfer was therefore **structural rather than literal**. The original prompt itself encourages swapping domains, but RHACO also had to change what was being measured and who had authority to change the underlying system. The Explorer pilot revealed still more necessary changes, discussed in section 7 below.

## 4. How execution was organized

The separate Explorer repository was used as a work area so the autonomous build could commit within its own scope without receiving authority to change RHACO's canonical repository or live research corpus. A dispatch handoff carried the frozen prompt, environment and agent-governance rules, and requirements for the closeout record.

The build began with read-only inspection, then wrote [`../CONSTRAINTS.md`](../CONSTRAINTS.md) and [`../ARCHITECTURE.md`](../ARCHITECTURE.md) before feature implementation. An integrator assigned the owned modules in dependency-aware waves. Builders worked in isolated Git worktrees, reported change requests across ownership boundaries, and provided round records. The integrator resolved shared interfaces and revalidated integrations. Dispatches and outcomes were tracked in [`../build_state.json`](../build_state.json), with detailed reports under [`rounds/`](rounds/).

The historical prompt set a maximum of four builder rounds per module, 28 total rounds, and a two-round convergence window. Exhausting a budget did not authorize lowering acceptance criteria. The build had no paid external service or external-deployment requirement.

Agent roles and model-tier assignments were governed separately from the application prompt. The campaign's run record documents changes in the orchestrator's model identity and explicitly warns that these changes are not separable from a single-run outcome. The mere presence of several agents does not turn the run into a controlled comparison of models.

## 5. How the build checked itself

The planned measurement system had several layers:

1. **L1 — static checks and tests:** lint, module tests, contract checks, and a guard against unauthorized index-write functions.
2. **L2 — runtime browser probe:** Playwright launches the application, drives named workflows on the actual server path, and retains browser captures and JSON observations.
3. **L3 — critic:** a separate read-only review strand examines captured behavior, code, and acceptance evidence and reports issues.
4. **L4 — corpus oracles:** known identifiers, documents, edges, retrieval gold queries, and card/index comparisons test specific expected behavior.

The executed layer register is [`LAYERS.md`](LAYERS.md). It also records shared failure modes: L2 and L4 can share the same retrieval module and database; L3 consumes L2 captures; the fixture cannot expose variation absent from its source examples. Agreement among these layers is not independent corroboration where they share the same defect.

Crucially, the project tried to **qualify its probe** by injecting known faults, including wrong-document resolution, mismatched cards, reversed relationship direction, broken reader navigation, and runtime errors. The campaign later found a mismatch between a case checking an internal attribute and the user-visible sentence it was supposed to test. This distinction affected the next template revision: qualification should assert the actual observable, not a proxy that can be correct while the interface is wrong.

## 6. Outcome: a useful artifact, a bounded build result

The build closed on September 5, 2026 with a recorded terminal state of **`BOUNDED_FAIL`**, not PASS. The closeout analysis reports nine objective gates passing, **11 of 12 acceptance presets** satisfied, and an unresolved set of product and verification findings. Its count of 333 tests is a historical test-suite observation, not evidence that all acceptance conditions were satisfied.

The harness evaluation concluded **PARTIALLY SUPPORTED under its gating criteria**. It describes seven target behaviors as holding at terminal, while documenting governance-record defects, incorrect intermediate claims, and corrections supplied by later sessions or outside readers. That is a different finding from the application's terminal state. The evaluation itself identifies the criterion-5 interpretation as a consequential scope issue; do not flatten its discussion into "the harness was proven" or "the software passed."

The record includes several instructive observations:

- **A real production-path defect escaped the fixture:** differences in date-value representations in the live corpus were invisible to a fixture whose cards all used quoted dates. A live workflow exposed it.
- **A check can assert the wrong observable:** one injected reversed-edge test could pass by reading a substrate attribute while the displayed sentence remained wrong.
- **Source agreement can establish compatibility, not correctness:** the adapter matched the original retrieval module on all 40 gold queries while the measured current-corpus Recall@10 remained below the previous baseline due to a changed target.
- **Parallel isolation has tradeoffs:** worktree ownership avoided conflicts, but some cross-module semantic regressions appeared only after integration.
- **Claims can outrun checks:** comments, architectural descriptions, and verification records sometimes asserted behavior that the associated code or instrument did not establish. The existing checks did not systematically audit these prose claims against their referents.

These are findings from a single build. They are not measured failure rates for autonomous software engineering in general.

## 7. What the later template learned

The September 7 RHACO template v2.0 documents changes informed by this pilot, including progressive qualification as surfaces become available, checking rendered observables, drawing fixtures from actual corpus value shapes, budgeting the probe separately, more explicit ownership and dispatch records, and a separate **claim-audit** step. Its claim-audit proposal evaluates written behavior claims against the artifacts they describe and marks unsupported claims `UNVERIFIED` rather than accepting correct-sounding prose as evidence.

These improvements are **post-experiment recommendations and subsequent template content**, not capabilities retroactively exercised by the frozen Explorer prompt. The later template's additional gates and instructions have their own validation burden; this single pilot does not demonstrate that the revised template works as intended.

For the post-pilot artifacts, read [How the prompt changed](PROMPT_EVOLUTION.md), which maps each pilot finding to the template change it produced. The templates and their guides are included as snapshot copies: [v2.0](campaign/RHACO_Build_Prompt_Template_v2_0.md) ([guide](campaign/RHACO_Build_Prompt_Template_Guide_v2_0.md)), [v2.1](campaign/RHACO_Build_Prompt_Template_v2_1.md) ([guide](campaign/RHACO_Build_Prompt_Template_Guide_v2_1.md)) and the current [v2.2](campaign/RHACO_Build_Prompt_Template_v2_2.md) ([guide](campaign/RHACO_Build_Prompt_Template_Guide_v2_2.md)). The review that produced v2.0 is [RHACO-ANL-20260907-001](campaign/RHACO-ANL-20260907-001_Build_Prompt_Template_Review.md).

## 8. How to examine the repository as evidence

| Question | Primary record |
|---|---|
| What was the agent instructed to do? | [`../PROMPT.md`](../PROMPT.md), frozen for this pilot. |
| Why those instructions and constraints? | [`../RATIONALE.md`](../RATIONALE.md), [`../CONSTRAINTS.md`](../CONSTRAINTS.md). |
| What was the planned system architecture? | [`../ARCHITECTURE.md`](../ARCHITECTURE.md). |
| What did individual builders report? | [`rounds/`](rounds/), plus [`../build_state.json`](../build_state.json). |
| What did the critic detect? | [`critique/`](critique/). |
| What did tests and probes capture? | [`probe-qualification/`](probe-qualification/), [`LAYERS.md`](LAYERS.md). |
| What remained limited or unresolved? | [`../SCOPE.md`](../SCOPE.md), `build_state.json` closeout fields. |
| What was the formally evaluated outcome? | [Campaign](campaign/RHACO-CMP-20260903-001_Corpus_Explorer_Autonomous_Build_Harness.md) and [harness analysis](campaign/RHACO-ANL-20260905-001_Corpus_Explorer_Harness_Evaluation.md). |
| How was the build dispatched, shepherded and handed back? | The dispatch handoff with its amendments, the builder's handback, and the shepherding handoffs, all under [`campaign/`](campaign/); start from [`campaign/MANIFEST.md`](campaign/MANIFEST.md). |
| How did the prompt change afterwards, and why? | [`PROMPT_EVOLUTION.md`](PROMPT_EVOLUTION.md). |
| What was altered to publish this repository? | [`release/`](release/), and the pre-publication measurement [RHACO-ANL-20260920-001](campaign/RHACO-ANL-20260920-001_Corpus_Explorer_Public_Release_Readiness_Sweep.md). |

The records use distinct terms for **source authority**, **retrieval relevance**, **build acceptance**, and **harness-evaluation support**. Keeping them distinct is part of the case study, not editorial fussiness: they answer different questions and require different evidence.

## 9. Limits on reproduction and generalization

The Explorer is tied to RHACO's Windows-based source paths, card schema, Python modules, derived index, and local retrieval environment; its historical records refer to that configured host. No turnkey setup or portable packaging has been demonstrated by this document. This public copy also omits the browser captures of the live-corpus probe runs, so those runs can be examined through their structured observations but not re-viewed as images (see [`release/`](release/)). An outsider can examine the source and experiment without treating the repository as a ready-made application for arbitrary collections.

The original external prompt reference was not pinned at the time it was read, and the pin given in section 2 is a later measurement with a stated bound; the later RHACO template was produced after the pilot; and the pilot was **n = 1**, with recorded model/session changes and shared verification dependencies. These limits prevent an exact upstream reconstruction or a general claim that this method reliably produces correct software. A new build, port, or repeat experiment needs its own frozen inputs and evaluation.

---

*Related guide: [How the Explorer works](HOW_IT_WORKS.md). Primary records remain unchanged in the repository root and build-evidence directories.*
