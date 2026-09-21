# How the build prompt changed, and why

**Audience:** readers who want to know what happened to the autonomous build prompt after the Corpus Explorer pilot, and what evidence each change rests on.

This is an account of RHACO's recorded review and change documents. It introduces no new findings. Every statement below is drawn from a record included in this repository, listed in [section 8](#8-sources). The build itself is described in [`BUILD_CASE_STUDY.md`](BUILD_CASE_STUDY.md).

One caution governs the whole document: **the evidence is one run of one prompt (n = 1), and no later template version has been validated by any run.** The changes below are responses to recorded failures and gaps. They are not demonstrated improvements.

## 1. Five texts, not two

The short version of this story is "a prompt was used, then improved." The record is more specific, and the difference matters. Five distinct texts are involved:

| Text | What it is | Status |
|---|---|---|
| **Upstream** | `rawprogress/fable-cities/PROMPT.md`, the structural starting point, read on September 3, 2026. | External, MIT-licensed. Pinned after the fact; see [`BUILD_CASE_STUDY.md`](BUILD_CASE_STUDY.md) section 2. |
| **v0, the base** | The upstream structure generalised into a domain-agnostic template with `{{SLOT}}` placeholders. | RHACO working file; never filed as a governed document. Included as found: [`campaign/unfiled/PROMPT_TEMPLATE.md`](campaign/unfiled/PROMPT_TEMPLATE.md). |
| **v1, the rewrite** | The base rewritten against RHACO's [Measurement Philosophy](MEASUREMENT_PHILOSOPHY.md), with each section labelled by the principle it claims to implement. | RHACO working file; never filed. This is the text the post-pilot review evaluated. Included as found: [`campaign/unfiled/PROMPT_TEMPLATE_CHARTER.md`](campaign/unfiled/PROMPT_TEMPLATE_CHARTER.md). |
| **The instantiation** | [`PROMPT.md`](../PROMPT.md) in this repository: the template filled in for the Corpus Explorer, then frozen and hash-pinned as the instrument under test (28,665 bytes, SHA-256 `dd75dd2e…`). | **This is the prompt the build ran.** |
| **v2.x, the filed template** | [v2.0](campaign/RHACO_Build_Prompt_Template_v2_0.md), [v2.1](campaign/RHACO_Build_Prompt_Template_v2_1.md), [v2.2](campaign/RHACO_Build_Prompt_Template_v2_2.md), each with a companion guide. | Produced after the pilot. None was used to run it. |

The instantiation is not simply v1 with the blanks filled. When it was written, it gained structure the template did not have. That turned out to be the most important thing the post-pilot review found.

## 2. The central finding: the template was credited for the instantiation's work

Two days after the pilot closed, RHACO reviewed the template's text against the pilot's record ([RHACO-ANL-20260907-001](campaign/RHACO-ANL-20260907-001_Build_Prompt_Template_Review.md)). The review set nine adoption criteria and had them ratified **before** mapping the evidence, so the evidence could not shape the test. It then classified every recorded finding by the layer that caused it (prompt design, the dispatching handoff, the harness, the client, the build, governance, measurement design) and charged the template only with prompt-design findings.

It found that seven structural sections the pilot's positive results rested on were present in the frozen instantiation and **absent from the template**:

1. first-class terminal states (`PASS`, `BOUNDED_FAIL`, `BLOCKED`, `INVALID`);
2. the authority boundary, with verification by a closeout hand outside the build;
3. invariants;
4. the acceptance workflow set;
5. probe qualification with known-good and known-bad cases;
6. hard budgets;
7. a register of shared dependencies between verification layers, which inverted the template's own claim that its layers were independent.

The review's conclusion, in its own framing: the run's honest terminal state, the satisfiability of its probe-qualification criterion, and its shared-dependency result all rest on instantiation text, and **a second instantiation of the template as written would not have inherited them.** The section that the pilot's harness evaluation credits with forcing an honest `BOUNDED_FAIL` was one the template never contained; in the review's words, the template had received credit for an instantiation addition.

What the record does credit to the template itself: the rule that the probe must exercise the production path (which caught a real defect), the `SCOPE.md` honest-limits register, reasoning artifacts kept as evidence, and the existence of a verification-layers document.

The template was also charged on **all five** prompt-design findings in the builder's handback ledger, and carried one statement contrary to a ratified criterion (the independence claim).

## 3. From the rewrite to v2.0: finding to change

The review proposed ten revisions, R1 to R10. The Director adopted all ten on September 7, 2026, and [RHACO-CHG-20260907-002](campaign/RHACO-CHG-20260907-002_Build_Prompt_Template_v2_0_REF_Cut.md) cut them as v2.0, the first filed version.

A note on labels, because the record uses two similar-looking sets. **P-1 to P-24** (with a hyphen) are rows in the builder's handback ledger: things that went wrong or were learned during the run. **P1 to P7** (no hyphen) are principles of RHACO's Measurement Philosophy. They are unrelated.

| # | What the pilot showed | What v2.0 changed |
|---|---|---|
| **R1** | The honest terminal state came from a section only the instantiation had. | Terminal states become part of the template: exactly one of four; `PASS` only from probe data with every gate green; running out of budget is `BOUNDED_FAIL`, never `PASS`; `INVALID` when the verification path cannot support claims. |
| **R2** | The probe could not be qualified before the surfaces it tested existed (P-1). Its only failure condition was a failed capture, so a run reported `ok: true` on a 404 with a console error (P-2). It was budgeted like a product module and spent three of its four rounds before one surface existed (P-8). One known-bad case went green while the rendered sentence was wrong, because it asserted on a data attribute instead of the rendered output (P-16). | A qualification protocol: one known-good case plus enumerated known-bad classes, each asserted on the **rendered observable**. A fault predicate: the probe fails when any logged field breaks its declared bound or a required capture is missing; a successful capture is never by itself `ok`. Progressive sequencing: each known-bad class is qualified when its surface first exists, and no product claim may cite a probe result ahead of the qualification it depends on. A separate round budget for the probe. |
| **R3** | No verification layer read a prose claim against the thing it described. That class of defect regenerated three times inside the controls meant to compensate for it (P-21, P-17). A builder's `UNVERIFIED` was recorded as landed at integration (P-22). A claim defect named as two instances proved on re-derivation to be seven (P-20). | A fifth layer, the **claim audit**: a separate agent reads every prose behaviour claim against its artifact and returns `MATCH`, `MISMATCH` or `UNVERIFIABLE`. `UNVERIFIED` becomes a first-class value in the state record that an integrator may overrule only with a cited check. A claim defect is re-derived to its full extent before its remedy is scoped. The layers document must say which claim classes are checked mechanically and which remain a reader's judgement. |
| **R4** | The template asserted four *independent* verification layers. The pilot's result held only because the instantiation said the opposite. | "Independent" is removed. Layers record their **shared dependencies** (build, data, capture path, reference set, model family) and list the independence claims they do not make. A disagreement protocol: record it, name the shared dependencies, run the smallest discriminating check, and leave it unresolved if it cannot be decided. |
| **R5** | The template bounded folder ownership only. What the build must never touch, and who verifies that, came from the instantiation. | An authority-boundary block: what the build may do alone, what stops it as `BLOCKED`, which substrate paths are never written, and verification by a closeout hand outside the build. The build asserts nothing about its own compliance; it is measured. |
| **R6** | The template wrote its records only after each round. The pilot showed the need for a record made at the moment of dispatch, including the execution mode. | A dispatch record (role, model, effort, pattern, agent type, execution mode, time) is written to the state file **before** the strand returns. Evidence paths are append-only. |
| **R7** | The executing model changed during the run, and no single surface reported it reliably: configuration is precise but static, the system prompt was stale after a switch, the per-request field was live but truncated (P-9, P-10, P-19). | Client identity is treated as a measurement variable: a conjunction of surfaces read and recorded at every round boundary; any change is `BLOCKED` until ratified; the client's automatic model switch is set to halt. |
| **R8** | Ownership of shared markup and vocabulary was decided by which round was cheaper, three times (P-13). | Shared markup, vocabulary and contracts are owned by the shell or the integrator **by rule**, decided at architecture time, each guarded by a contract test. |
| **R9** | A hand-authored fixture reproduced its authors' conventions, not the corpus's variance: the review records 866 of 1,443 cards using a date form the fixture never contained, across four green rounds (P-14). | A fixture is derived from the production input's resolved types, with a fixture-versus-production census recorded at round 0. |
| **R10** | The template demanded provenance of every reference and gave none for its own upstream. Some principle labels named no mechanism. | Each label must resolve to a mechanism in its own section or be dropped. One candidate principle was removed as a section's warrant. The upstream was pinned by access date. |

**What the review deliberately kept out of the template.** Findings caused by the dispatching handoff, the client or RHACO's own governance were routed to those layers and the template was left unchanged: checking carried text against its archive at dispatch, showing a control is executable on the surface that runs it, keeping round-specific literals out of generated prompts, and several record-keeping rules. A template that absorbs every lesson stops being domain-agnostic, which was itself one of the nine criteria.

**The cost, stated by the review:** revisions R1 to R7 roughly double the template's length.

## 4. v2.0 to v2.1: an outside reader finds the template contradicting itself

On the same day v2.0 was cut, an external model review of it (ChatGPT) reported eight prioritized issues and three refinements. RHACO checked each claim against the on-disk text; every factual claim about the text held. The dispositions are recorded in [RHACO-CHG-20260907-004](campaign/RHACO-CHG-20260907-004_Build_Prompt_Template_v2_1_REF_Cut.md).

One issue was a real control-flow defect. The template defined its quality score with 10 as best and passed a module when the score met a threshold, but told the loop to resume each iteration from the module with the **largest** score. The guide said the smallest. Executed literally, the loop would keep re-working its strongest module. The change record notes the irony plainly: this is exactly the divergence between prose and mechanism that v2.0's new claim-audit layer exists to catch, found by an outside reader in the harness's own text. The score was renamed so that higher is unambiguously better, and the loop resumes from the lowest.

The remaining adopted changes tightened meaning without changing flow:

- a claim audit is **clean** only with zero mismatches and zero `UNVERIFIED` on any claim a `PASS` criterion rests on;
- any mechanical part of the claim audit is itself an instrument, and must be shown to return `MATCH` on a known-good claim and `MISMATCH` on a known-bad one before its verdicts count;
- the critic scores each calibration artifact twice, blind, and the spread is its repeatability; a round-to-round score change inside that spread is "unchanged" whatever its decimal;
- escalation reads matched probe outputs and the ranked issue set, not a number;
- a critic's score never compensates for a failed objective gate;
- the rule against unprobed claims is narrowed to production-behaviour claims, since other kinds of claim are supported by other layers;
- closeout verification is stated per substrate. Hash equality is one such control, not the rule: a changed hash does not show who wrote, and an unchanged one does not rule out transient writes.

One generalisation was adopted: the fixture rule was rewritten without corpus-specific vocabulary.

Not everything was accepted. A proposed rename of a generic slot was skipped as having no leverage, and a proposed new slot was declined to avoid slot creep. The record also states that one premise of the external review, concerning writes to live state during the pilot, **was not verified** against the evaluation, and that the disposition does not depend on it. The review's proposed validation targets were set aside as seed material for a future validation run.

Because the defect changed control flow, this was cut as v2.1, not as a patch.

## 5. v2.1 to v2.2: correcting the template's account of its own sources

While this repository was being prepared for publication, a read-only sweep ([RHACO-ANL-20260920-001](campaign/RHACO-ANL-20260920-001_Corpus_Explorer_Public_Release_Readiness_Sweep.md)) found that both v2.0 and v2.1 said the upstream file "as retrieved" had been retained in RHACO working material. The named file is v0, RHACO's own generalisation. No byte-identical copy of the upstream had been kept.

[RHACO-CHG-20260920-001](campaign/RHACO-CHG-20260920-001_Build_Prompt_Template_v2_2_REF_Cut_Provenance_Correction.md) cut v2.2 to say so. It moves the existing hash pin onto v0, pins the upstream's single public commit and file as measured on September 20 with the bound that a later upstream history rewrite would be undetectable, and records the upstream's licence. **v2.2 changes no mechanism.** v2.0 and v2.1 are included here unedited, error and all, because RHACO corrects a reference document by cutting a new version, never by editing a filed one.

This is the same class of defect as R3's and section 4's: a prose claim that nobody had read against its referent. R10 had asked the template to pin its own provenance; the pin it received was wrong for two versions.

## 6. What this does and does not establish

- **n = 1.** One run, one instantiation, one host, one client. The nine criteria test the template's *structure* against that run. In the review's words, they calibrate nothing.
- **No v2.x mechanism has been validated by any run.** Every version's own provenance paragraph says so. A validation run is a future RHACO campaign, not part of this record.
- The review evaluates whether the template's structure *could* have produced the pilot's positive results and whether it forbids the negative ones. It does not measure performance, and it claims nothing about how models reason.
- The boundary of the claim-audit layer (which claims can be checked mechanically) is left to each instantiation to state. It is not settled here.
- Counts of ledger rows are tallies of a hand-classified record, not measurements.

## 7. Reading the three versions

Each template's **Version History** table, at the end of the file, is the shortest accurate summary of what that cut changed. The change records in section 8 carry the exact edit lists: for v2.1 and v2.2, every edit is an anchored replacement against a byte copy of the previous version, so the difference between versions is fully reconstructible from the record.

## 8. Sources

All under [`campaign/`](campaign/) as hash-pinned, unedited snapshot copies; see [`campaign/MANIFEST.md`](campaign/MANIFEST.md). Identifiers cited inside those documents that have no file here refer to RHACO-internal records.

| Record | Role in this account |
|---|---|
| [`../PROMPT.md`](../PROMPT.md), [`../RATIONALE.md`](../RATIONALE.md) | The frozen instantiation the build ran, and its design rationale. |
| [RHACO-ANL-20260905-001](campaign/RHACO-ANL-20260905-001_Corpus_Explorer_Harness_Evaluation.md) | The pilot's harness evaluation. |
| [RHACO-ANL-20260907-001](campaign/RHACO-ANL-20260907-001_Build_Prompt_Template_Review.md) | The template review: criteria, evidence map, revisions R1 to R10. Sections 2 and 3 of this document. |
| [RHACO-CHG-20260907-002](campaign/RHACO-CHG-20260907-002_Build_Prompt_Template_v2_0_REF_Cut.md) | The v2.0 cut, carrying the full v2.0 text as its payload. |
| [RHACO-CHG-20260907-004](campaign/RHACO-CHG-20260907-004_Build_Prompt_Template_v2_1_REF_Cut.md) | The v2.1 cut and the external review's dispositions. Section 4. |
| [RHACO-CHG-20260920-001](campaign/RHACO-CHG-20260920-001_Build_Prompt_Template_v2_2_REF_Cut_Provenance_Correction.md) | The v2.2 cut. Section 5. |
| Templates [v2.0](campaign/RHACO_Build_Prompt_Template_v2_0.md), [v2.1](campaign/RHACO_Build_Prompt_Template_v2_1.md), [v2.2](campaign/RHACO_Build_Prompt_Template_v2_2.md) and guides [v2.0](campaign/RHACO_Build_Prompt_Template_Guide_v2_0.md), [v2.1](campaign/RHACO_Build_Prompt_Template_Guide_v2_1.md), [v2.2](campaign/RHACO_Build_Prompt_Template_Guide_v2_2.md) | The filed template lineage. |
| The builder's handback, under [`campaign/`](campaign/) | The ledger rows P-1 to P-24 cited in section 3. |
| [`campaign/unfiled/`](campaign/unfiled/) | v0 and v1, the two unfiled originals, so the v1 to v2.0 difference can be read directly. |
| [`MEASUREMENT_PHILOSOPHY.md`](MEASUREMENT_PHILOSOPHY.md) | The principles behind the P1 to P7 section labels. |
