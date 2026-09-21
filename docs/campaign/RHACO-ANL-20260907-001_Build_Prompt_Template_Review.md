# RHACO-ANL-20260907-001 | Domain-Agnostic Build-Prompt Template — Review Against the CMP-20260903-001 Record

*Reno High-Altitude Cosmic Ray Observatory (RHACO) · 5,050 ft ASL · 39°N*
*RadiaCode RC-110-003225 · CsI(Tl) · 30 mm Pb walls / 40 mm Pb lid · sealed castle*

| Field | Value |
|---|---|
| Document type | ANL (Discrete analysis report — instrument-structure evaluation) |
| Status | Baseline |
| Target campaign | None — the last section 9 queue item of RHACO-CMP-20260903-001 (CLOSED; charter and card untouched) |
| Object under evaluation | `working\PROMPT_TEMPLATE_CHARTER.md` (the Charter-aligned rewrite of the domain-agnostic build-prompt template); `working\HOW_TO_USE.md` as companion; `working\PROMPT_TEMPLATE.md` as the base the rewrite derives from |
| Evidence base | RHACO-CMP-20260903-001, one run of one instantiation (n = 1); RHACO-ANL-20260905-001 + Amendment A1; the HND-20260903-001 handback ledger P-1…P-24; RHACO-CHG-20260906-003; RHACO-CCX-20260907-001 section 5 |
| Data | Files pinned in section 0 of this document; no observatory data stream consumed |
| Author | Kris E. Granholm, Director, RHACO (drafted by Claude chat under Director ratification; CCX-20260907-001 receiving session) |
| Date | 2026-09-07 UTC |
| Naming convention | v1.17 · Style RSG v1.9 · Schema Card YAML v1.9 · ANL Specification v1.0 |

## 0  Pre-flight pins (this session)

Chat full-file `read_corpus` unless marked ranged. Server 0.22.1, librarian 1.19, NC 1.17; head `c76a810`; census 1464 at session open.

| Artifact | sha256 (prefix) | Bytes | Note |
|---|---|---|---|
| `working\PROMPT_TEMPLATE_CHARTER.md` (the rewrite — object) | `7d6b39e1` | 10,153 | mtime 2026-09-07T01:49:24Z |
| `working\HOW_TO_USE.md` (companion) | `4ac3ebda` | 12,736 | self-described companion to the base; not revised with the rewrite (Director, 2026-09-07) |
| `working\PROMPT_TEMPLATE.md` (base) | `d1f2dee6` | 7,908 | placed by the Director 2026-09-07T02:02:21Z; absent at CCX-20260907-001 filing |
| `working\m3_evidence\PROMPT.md` (instantiation, frozen) | `dd75dd2e` | 28,665 | equals the CMP-20260903-001 section 2 item 5 chat-side pin — byte-identical to the as-uploaded prompt |
| RHACO-ANL-20260905-001 | `c6b6421c` | 31,386 | matches the CCX pin |
| RHACO-ANL-20260905-001 Amendment A1 | `1dcd86fb` | 4,218 | — |
| RHACO-CMP-20260903-001 | `39505d6c` | 23,632 | post Q-1/Q-2/Q-3 lines |
| RHACO-CHG-20260906-003 | `44ec1347` | 25,553 | section 5 read with CCX-20260907-001 section 5 item 1 as errata |
| `working\HND-20260903-001_report.md` section P (ledger) | ranged, bytes 140,000–186,000 | 196,366 | file pin of record `79079690` per ANL-20260905-001 section 0; ranged slice hashes are not pins |
| RHACO-CCX-20260907-001 | `02202191` | 22,376 | receiving scope |

## 1  Object, question, method

**Object.** The domain-agnostic template as a structure — the Charter rewrite's text — not its performance. HOW_TO_USE is read as the base's companion carrying a known version skew (section 6). The base is read to separate what the rewrite added from what it inherited.

**Question.** Does the rewrite, as written, carry the mechanisms the CMP-20260903-001 record shows a self-verifying build prompt needs — and where it does not, is the gap the template's, the instantiation's, or the hand's?

**Method.** Adoption criteria were stated and ratified before the evidence map was built (section 2; Charter: measurement defines category). Every finding is classified by layer first, using the ledger's own column — `prompt-design | hand-design | harness | client | build | governance | measurement design` — and only prompt-design findings indict the template. A finding whose cause is the RHACO instantiation (`PROMPT.md` diverging from the template) or the hand (HND-20260903-001 riders) is recorded as such and not charged. Three texts are held distinct throughout: **template** (the rewrite), **base** (`PROMPT_TEMPLATE.md`), **instantiation** (`PROMPT.md` as frozen). The template's own principle labels (P1–P7, GL) are part of what is under test, not the test.

**Non-claims.** n = 1: one run of one instantiation. Nothing here measures the template's performance or generalizes to the harness; the ANL evaluates whether the template's structure could have produced the campaign's positive results and whether it forbids the campaign's negative ones. Nothing about model cognition. The companion review (`…Pattern_3_Prompt_Recommendations.md`) is not an independent reader (ANL-20260905-001 section 6.1) and is not used as evidence here.

## 2  Adoption criteria (ratified 2026-09-07, before the evidence map)

Sources: RHACO-CMP-20260903-001 section 2 (H1 sub-hypotheses), section 3 (criteria 1–6), section 6 (review triggers), section 9 (closure findings); Measurement Philosophy v1.4.1. A revised template is adoptable only if it:

- **T1** defines terminal states PASS / BOUNDED_FAIL / BLOCKED / INVALID as first-class; PASS declarable only from probe data; budget exhaustion never PASS.
- **T2** places probe qualification (known-good plus enumerated known-bad classes) before product claims, sequenced so it is satisfiable before the surfaces it depends on exist.
- **T3** carries an authority-boundary slot — what the build may not touch — verified by a closeout hand, never asserted by the build.
- **T4** requires verification layers to register shared dependencies instead of claiming independence.
- **T5** writes dispatch and round records at dispatch, with required fields including execution mode.
- **T6** gives every prose behaviour claim a named check or an `UNVERIFIED` tag that survives integration; the template either defines the claim-audit layer or declares which claim classes remain reader-owned.
- **T7** treats executing-client identity as a measurement variable: a conjunction of surfaces read at round boundaries, switch behaviour set to halt.
- **T8** makes every P1–P7 / GL label resolve to a testable mechanism in its own section.
- **T9** stays domain-agnostic.

Caveat the Charter requires: these test structure against one run; they calibrate nothing.

## 3  Findings — evidence map (descriptive)

Claim strength: *descriptive* throughout — each row is a reading of the rewrite's text against a cited record; no statistical claim is made or possible at n = 1. Status is against the rewrite's own text: `covered | partial | absent`.

### 3.1  Ledger rows of class prompt-design (the rows that can indict the template)

| Item | Rewrite section governing | Status | Charge |
|---|---|---|---|
| P-1 — probe qualification unsatisfiable before later-wave surfaces (AC-3 ruling) | section 2 (probe before artifact); section 4 (waves) | **absent** — the template defines no qualification protocol; known-good / known-bad cases were instantiation section 2; no sequencing rule | template (T2). The specific wave conflict was instantiation section 14 against section 4 |
| P-2 — probe failure predicate is capture failure only (`ok = error is None`; run 20260904T033047Z `ok: true` on 404 + console error) | section 2 PROBE_LOG_FIELDS | **absent** — the probe writes output plus a log; no observed-fault predicate is defined | template (T2). Ledger class prompt-design; not carried into ANL-20260905-001 section 5 or section 10 (section 7 below) |
| P-8 — the instrument budgeted like a product module (probe 3 of 4 rounds spent before the lineage surface existed) | section 5 MAX_ROUNDS (per module); section 2 | **absent** — the probe is not a module in the template and carries no round budget at all; the instantiation's equal budget repaired a template silence | template (T2) |
| P-13 — shared ownership decided by round cost, three instances (keyhelp markup; `mode_effective` callers; retyped date) | section 4 integrator "fixes the seams" / CORE_PATH | **partial** — ownership is structural only for CORE_PATH; shared markup or vocabulary outside it has no owner by rule | template. Instantiation phrasing ("when ownership cannot be isolated") widened the same gap |
| P-21 / P-17 / ANL section 6.2 — no layer reads a claim against its referent; class (b) regenerated three times inside the compensating controls | section 3 layer table; section 7 "must cite the module or probe result" | **absent** — L1–L4 lint, probe, score, compare; section 7's citation rule has no layer enforcing it | template (T6). The campaign's primary prompt-design row |

Five prompt-design rows; the template is indicted on all five (three absent, two partial).

### 3.2  Ledger rows of other classes (not chargeable; mapped for completeness)

| Item | Ledger class | Rewrite section | Status | Owner |
|---|---|---|---|---|
| P-14 — hand-authored fixture reproduces the authors' conventions, not corpus variance (866 of 1,443 census cards bare-date; four green rounds) | measurement design | section 2 "probe must exercise the production path" | **partial** — the production-path rule is covered and is what caught W6 (positive evidence); fixture representativeness and a round-0 type census are absent because the template has no fixture concept | template partial; fixture design was instantiation |
| P-16 — qualification asserted on a substrate attribute, not the rendered observable (KB3 green while the sentence was wrong) | measurement design | section 2 PROBE_OUTPUT | **partial** — PROBE_OUTPUT is the rendered artefact by design, but with no qualification step the rule has nothing to attach to | instantiation (KB3 design); template partial via T2 |
| P-22 — builder's UNVERIFIED recorded as `landed: YES` at integration (1387 px unchanged) | governance / record | section 8 STATE_FILE fields; section 4 integrator record | **absent** — no UNVERIFIED value in the state schema (HOW_TO_USE section 4: `status`, `issues` only) | template (T6b): the record schema is the template's |
| P-9 / P-10 / P-19 — identity as a conjunction (safeguard swap; prompt stale two changes later; suffix stripped 255/255, 173/173) | client | none | **absent** | not a ledger indictment; T7 requires the template to carry it |
| P-11 — carried text diffed against its archive at dispatch | governance | none | absent | hand / HOW_TO_USE |
| P-12 — a control shown executable on the surface that runs it | client | none | absent | hand / HOW_TO_USE |
| P-15 / P-20 (second half) — no round-specific or self-referential literals in generated prompts | governance / harness | none | absent | hand |
| P-20 (first half) — re-derive a prose-claim defect's full extent before scoping the remedy (2 named, 7 found) | governance / measurement design | none | absent | folds into T6 |
| P-23 — a reconciliation rule names its mechanism | measurement design | none | absent | RHACO hand / SOP-20260708-001 v5 fold (queued) |
| P-24 — the findings record inside the census walk | governance / record | section 8 | not applicable | RHACO (CLAUDE.md section 17 rule 7 corollary) |
| P-18 — handoffs state observed dispatch state, never intent | governance | none | not applicable | CCX Specification / draft-doc |
| ANL-20260905-001 section 6.5 (three) and RHACO-CCX-20260907-001 section 5 item 1 (five) — chat-side instances of the P-21 class | governance, harness-external | none | not applicable | not template defects. They establish that the class is general, which raises T6's weight; with ANL-20260905-001 Amendment A1 section A1.3 they show the citation auditor is already a narrow claim-audit layer with a stated grammar — a design input for R3 |

### 3.3  Criteria-derived gaps not in the ledger

| Criterion | Rewrite section | Status | Reading |
|---|---|---|---|
| T1 terminal states | sections 7–8 ("loop until every critic passes or SCOPE.md records why it cannot") | **absent** | PASS / BOUNDED_FAIL / BLOCKED / INVALID were instantiation section 12 — the section ANL-20260905-001 section 5 credits for forcing the honest terminal state. The template received credit for an instantiation addition |
| T3 authority boundary | Rules; HUMAN_GATE_POLICY | **partial** | folder ownership only; no substrate or authority boundary; no closeout-hand verification (instantiation section 11 supplied both) |
| T4 shared-dependency register | section 3 "Four **independent** verification layers"; column `Independent of` | **absent, and contrary** | the template asserts per-layer independence; H1(f) held only because instantiation section 3 inverted the claim ("do not claim L2–L4 independent") and recorded shared dependencies |
| T5 dispatch records at dispatch | section 8 (round reports after the round) | **absent** | the GD-1 class |
| T8 label to mechanism | section 4 "(P3 structural; unchanged)"; section 6 "(P4; unchanged in mechanism)"; section 5 "(GL)" | **partial** | fan-out carries no filtering mechanism; section 6's mechanism is the base's, which predates the Charter; GL is a parked candidate licensing a section |
| T9 domain-agnostic | whole | covered | — |
| GL self-application | header provenance | partial | the template demands version, date and access-date provenance of every reference; its own `rawprogress/fable-cities` credit carries none. External provenance of the structure is recorded here as the CCX asked |

## 4  What the campaign's positive results owe to the instantiation

Structural sections present in `PROMPT.md` and absent from the rewrite: terminal states (section 12), authority boundary (section 11), invariants (section 13), acceptance workflow set (section 8), probe qualification with known-good / known-bad cases (section 2), hard budgets, and the shared-dependency register (section 3, inverting the template's independence claim). Seven additions. The rewrite's own contributions that the record credits: the production-path rule (section 2 — the W6 catch, P-14), SCOPE.md (section 7 — the honest register, ANL-20260905-001 section 3.3), reasoning artifacts (section 8 — docs/rounds and docs/critique as evidence), and the existence of LAYERS.md (section 3). The reading that follows is descriptive: the run's terminal honesty, its criterion-3 satisfiability and its H1(f) result rest on instantiation text, and a second instantiation of the rewrite as written would not inherit them.

## 5  Revision proposal (adopted by the Director 2026-09-07 as listed)

| # | Item | Revision | Ledger evidence | Alternative considered |
|---|---|---|---|---|
| R1 | T1 | New section 9 Terminal states: PASS / BOUNDED_FAIL / BLOCKED / INVALID, exactly one; PASS only from probe data with gates and zero-tolerance; budget exhaustion → BOUNDED_FAIL; INVALID when the verification path cannot support claims; required report fields per state (instantiation section 12, de-domained) | ANL-20260905-001 section 5 positive row; section 3.4; H1(g) | keep the loop rule — rejected: the property that produced the headline result would live outside the template |
| R2 | T2 (P-1, P-2, P-8, P-16) | Section 2 rewrite: qualification protocol — one known-good case plus `{{KNOWN_BAD_CLASSES}}`, each asserted on the rendered observable, on a fixture or fault-injected substrate, evidence under `docs/probe-qualification/`; fault predicate — FAIL when any PROBE_LOG_FIELD violates its declared bound or any required capture is missing, capture success never `ok`; progressive sequencing — each known-bad class qualified when its surface first exists, no product claim citing a probe result before the qualification it depends on; `{{PROBE_ROUNDS}}` budgeted separately, one extension round per wave that adds a surface | P-1, P-2, P-8, P-16; ANL-20260905-001 sections 3.2, 4(c) | qualification in HOW_TO_USE only — rejected: criterion 3 was satisfiable (SA-6) because the instantiation instructed it |
| R3 | T6 (P-21, P-22, P-20a, section 7 rule) | Section 3 gains L5 Claim audit: a separate agent reads every prose behaviour claim (docstring, notice, ARCHITECTURE / CONSTRAINTS sentence, round report, state-file entry, critic report) against the artifact it describes → MATCH / MISMATCH / UNVERIFIABLE per claim, after each integrator merge; mismatches to the owning builder as ranked issues; unchecked claims carry `UNVERIFIED`. LAYERS.md records which claim classes have a mechanical grammar and which remain a reader's. State schema: `UNVERIFIED` first-class; the integrator overrules only with a cited check. An audit-named claim defect is re-derived to full extent before the remedy is scoped | P-21; ANL-20260905-001 sections 6.1, 6.2; P-22; P-20; section 6.5 and CCX-20260907-001 section 5 item 1; Amendment A1 section A1.3 | keep section 7's citation rule and defer — rejected: no layer enforces it, and the class regenerated three times under it |
| R4 | T4 | Section 3 heading loses "independent"; column `Independent of` → `Shared dependencies`; LAYERS.md lists shared dependencies (build, data, capture path, reference set, model family) and "independence claims not made"; disagreement protocol — record, name shared dependencies, smallest discriminating check, leave unresolved if undecidable | ANL-20260905-001 section 3.2 row 4; H1(f); instantiation section 3 | none — the text contradicts a ratified criterion |
| R5 | T3 | New block after Rules, Authority boundary: may-autonomously list; stop-BLOCKED-before list; `{{SUBSTRATE_PATHS}}` never written; substrate-untouched verified by a closeout hand outside the build (hash before / after), never asserted by the build | ANL-20260905-001 sections 3.1 row 4, 7, 8 criterion 6; instantiation section 11 | rely on HUMAN_GATE_POLICY — rejected: it governs when to ask, not what is untouchable or who verifies |
| R6 | T5 | Section 8: a dispatch record (role, model, effort, pattern, agent type, execution mode, dispatched_utc) written to STATE_FILE before the strand returns; evidence paths append-only by rule | GD-1 (HND-20260903-001 Amendment A2 section A2.9); ANL-20260905-001 section 6.3; P-15 | leave to the hand or Guide — rejected: STATE_FILE is the template's artifact |
| R7 | T7 | New Rule plus section 8 field: client identity of record is the conjunction of `{{IDENTITY_SURFACES}}` (config sha plus model key; system-prompt sentence; per-request model as a family check), read and recorded at every round boundary; any change → BLOCKED; client auto-switch configured to halt | P-9, P-10, P-19; ANL-20260905-001 section 6.4 | HOW_TO_USE only — defensible as a client-layer finding; rejected by ratified T7 |
| R8 | P-13 | Section 4: shared markup, vocabulary or contract is owned by the shell or integrator by rule, decided at ARCHITECTURE time, never by round cost; each shared block guarded by a contract test; omissions wait for a round, affirmatively false statements are repaired with a control | P-13 (three instances; the ruled amendment) | treat as instantiation wording — rejected: "fixes the seams" leaves the same gap |
| R9 | P-14 | Section 2, one sentence: a fixture is derived from the production corpus's loader-resolved types, with a fixture-versus-production type census at round 0; detail to HOW_TO_USE | P-14 | keep the production-path rule alone — viable; the one-sentence form adopted |
| R10 | T8; GL; provenance | Section 4 drops "(P3 structural)" or states a filtering mechanism; section 6 states its mechanism or drops the label; GL either promoted in the Charter or removed as a section warrant; header pins `rawprogress/fable-cities` by commit or date and access date as section 5 demands of every reference | Charter: measurement defines category | none |

Not template — routed elsewhere, template unchanged: P-11, P-12, P-15, P-20 (second half) → HOW_TO_USE orchestration notes; P-23 → SOP-20260708-001 v5 fold (queued); P-18 → CCX Specification / draft-doc; P-24 → CLAUDE.md section 17 rule 7 corollary.

## 6  Companion skew (HOW_TO_USE, unrevised with the rewrite)

Recorded, not charged to the template: no CONSTRAINTS.md, SCOPE.md, LAYERS.md or REFERENCE.md; section 4 state schema carries a single `score`, not `ref_gap` / `round_delta` / `iso_vs_integrated`, and no `UNVERIFIED`; section 10 pre-launch checklist has no calibration-artifact, provenance, identity-surface or claim-audit items; section 3's verification-block test ("directly comparable to REFERENCE_CORPUS, inspectable by a second agent") and section 6's human-gate policies remain valid for the rewrite. Revision alongside the template: section 3 gains the known-bad-classes and identity-surfaces slots; section 4 the three numbers and `UNVERIFIED`; section 10 the four missing checks. Cost, one clause: R1–R7 roughly double the template; the section 5 token warning stands and belongs in the revised text.

## 7  Data-quality notes

1. P-2 is class prompt-design in the ledger and was not carried into ANL-20260905-001 section 5's prompt-design row or section 10; this ANL restores it. No other ledger row changed class between the handback and the ANL.
2. The base file was absent at CCX-20260907-001 filing (80 files under `working\`, no match) and placed by the Director at 02:02:21Z this session; the review object was resolved as the rewrite alone, per the CCX's own contingency, with the base read for inheritance only.
3. The ledger was read by ranged `read_corpus` (bytes 140,000–186,000 of 196,366); ranged slice hashes are not pins. The file's pin of record is ANL-20260905-001 section 0 (`79079690`), Code-verified with two instruments.
4. The rewrite's section numbering is internal to a non-canonical file; every "section N" in sections 3–5 above that is not prefixed by a RHACO document id refers to the rewrite (or, where stated, to the instantiation).

## 8  What this ANL does not decide

The REF cut and its filename; the HOW_TO_USE revision text; whether GL is promoted in the Charter (R10 offers two forms); any second run of the harness under the revised template; the claim-audit layer's grammar boundary (which claim classes are mechanical) — R3 requires it to be stated per instantiation, not fixed here. Adoption of R1–R10 was the Director's ruling of 2026-09-07 and is recorded in section 5 as such; this ANL maps evidence to template sections and proposes; it does not adopt (CCX Specification v1.1 section 7.1).

## 9  Scope limits

n = 1. The evidence is one run of one instantiation on one host under one client; the ANL evaluates the template's structure against that run and makes no claim about the template's performance, about any other domain, or about the harness in general. No quantity here is a measurement; counts of ledger rows are tallies of a hand-classified record. Nothing is claimed about model cognition. The observatory's physical scope limits (Charter Principle 7) are unaffected: no cosmic-ray, heliospheric, detector-physics or radon measurement is asserted or implied.

## 10  Cross-references

RHACO-CMP-20260903-001 (CLOSED; section 9 queue — this item) · RHACO-ANL-20260905-001 + Amendment A1 · RHACO-HND-20260903-001 + A1–A3 (the hand; ledger section P in its handback) · RHACO-CHG-20260906-003 (section 5; chat-side P-21 instances) · RHACO-CCX-20260907-001 (receiving scope; section 5 pointers; section 6 vocabulary lock) · RHACO-CCX-20260906-003 (predecessor) · RHACO_Subagent_Pattern_Application_Guide_v1_4 · RHACO_CCX_Specification_v1_1 · RHACO_ANL_Specification_v1_0 · RHACO_Measurement_Philosophy_v1_4_1.

---

*Reno High-Altitude Cosmic Ray Observatory (RHACO) | Kris E. Granholm, Director*
