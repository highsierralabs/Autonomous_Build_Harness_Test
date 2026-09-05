# Critic round 1 -- RHACO Corpus Explorer (strand S6-CR1)

*Filed by the integrator on the critic's behalf: the critic is read-only and writes nothing (ARCHITECTURE.md section 2). The text below section 1 is the critic's own, verbatim.*

| Field | Value |
|---|---|
| Strand | S6-CR1, critic round 1 |
| Model | `claude-opus-5[1m]`, agent type Explore, read-only, effort xhigh (explicit) |
| Reviewed at | commit `183955e` |
| Prompt of record | `docs/rounds/R06_critic.prompt.md`, sha256 `502d83a02b085aef8c611ace59856dc8f56ee739f22ff88ee613985bacfa0ed4` (verified by the strand before acting) |
| Window | 2026-09-05T05:07:53.9163962Z - 2026-09-05T05:22:38.5350352Z |
| `ref_score` | **8** against a pass threshold of 8.5 |
| Score precision | **ORDINAL, not metrological** (PROMPT.md section 7 requires this be stated where no calibrated exemplars exist) |
| Objective gates | **8 PASS, 1 FAIL** |
| Disputes the build's record | **typed relation direction preserved** |

## Integrator note on independence

Under Director ruling MOD-1 the orchestrator and the critic share a model family, which `docs/LAYERS.md` section 3 records as a limit on this review's independence from integration judgment. The critic was told so, and answered it by weighting its disagreements above its agreements. Its one gate FAIL contradicts `build_state.json` directly, and several of the overstated claims it lists are the integrator's own bookkeeping. That is the behaviour the arrangement was supposed to make difficult, so it is recorded here rather than smoothed over.

---
# Critic report — RHACO Corpus Explorer, round 1 (strand S6-CR1)

**Instruction of record:** `docs/rounds/R06_critic.prompt.md`, sha256 observed `502D83A02B085AEF8C611ACE59856DC8F56EE739F22FF88EE613985BACFA0ED4` — **matches** the pin in the dispatch.
**Window:** 2026-09-05T05:07:53.9163962Z → 2026-09-05T05:22:38.5350352Z.
**Reviewed at:** `fc08dc3` (working tree clean; the product is unchanged since `183955e`).
**Mode:** read-only. I created, edited and deleted nothing; I ran no test, no lint, no server and no probe. Every behavioural claim below is attributed to an artifact someone else captured, or derived by reading source.

---

## 0. The short version

This is a good build, and I want to say why before I say what is wrong with it, because the failure mode of a critic who shares a model family with the orchestrator is to be *agreeably* thorough.

What is genuinely good, and rare:

- **The instrument observes itself and it found something.** The probe's W6 preset reached a card with an unquoted YAML date and produced a real HTTP 500 on a path that L1, four rounds of green tests, and the entire fixture substrate could not reach. The build recorded the FAIL in the run directory, filed it, repaired it in a scoped round, and re-ran the whole acceptance set. That is the harness working.
- **The evidence disclosure refuses to invent.** `Component rank: not exposed by current RHACO retrieval API`; `expansion of a seed; relation not exposed by the current RHACO API`; hybrid excerpts explicitly stamped *"lexical excerpt, not the hybrid evidence"*. The easy, wrong move here — reconstructing component ranks to make the panel look explanatory — was available and was not taken.
- **Degradation is probed, not inferred.** `adapter.search_hybrid` calls `vector_availability()` *before* the module call, so the mode label is decided from an observed channel state. Result shape cannot distinguish a degraded hybrid from a real one; the build knew that (ARCHITECTURE A4) and built around it.
- **The reader distinguishes three things where the prompt only asked for two** — the card file, the index row *as indexed*, and the document — and prints a per-field verdict between the first two.
- **The diagnostics page is the best surface in the build.** Non-authoritative notice on the database path, every `index_meta` key, live counts including `edges_unresolved: 413`, vector reason and probe time, exclusion sets, rerank standing with its negative-result evidence, last probe run, and the authority notice verbatim.
- **The SQL is clean.** Fixed whitelists for identifiers, bound parameters for every value, `LIKE ? ESCAPE '\'` with escaping applied. I re-derived the index-write prohibition myself rather than trusting the L1 record: the five writing names appear nowhere under `explorer/`, and `search_hybrid_rerank` appears in no code path at all.

Now the part that matters.

---

## 1. Objective gates, independently assessed

| # | Gate | My verdict | Differs from `build_state`? |
|---|---|---|---|
| 1 | Exact identifier fixture targets correct | **PASS** | no |
| 2 | Gold-query compatibility not regressed beyond baseline unless scoped/evidenced | **PASS** | no |
| 3 | No write path to corpus from UI | **PASS** | no |
| 4 | No arbitrary text-to-SQL | **PASS** | no |
| 5 | Zero unresolved template/runtime exceptions in acceptance probes | **PASS** | no |
| 6 | Card `status` and CMP `lifecycle_state` never collapsed | **PASS** | no |
| 7 | Typed relation direction preserved | **FAIL** | **yes** |
| 8 | Flat hybrid remains default | **PASS** | no |
| 9 | Semantic-unavailable degradation explicit and functional | **PASS** | no |

### Gate 7 — the disagreement

`build_state.json` records *"PASS — KB3 qualified this round (reverse_edges detected); W5 and W6 on the production path."* I record **FAIL**, and here is the whole of my reasoning.

The **machine-readable** direction is preserved perfectly. `data-edge-from` / `data-edge-to` / `data-edge-direction` are correct, the outgoing/incoming buckets come straight from the adapter and are never recomputed (a deliberate, correct decision — it is what keeps KB3 observable), the SVG arrowheads always run from→to, and KB3 genuinely detects a from/to swap.

The **human-readable** direction is not.

- `explorer/models.py:24-29` defines exactly one label per relation.
- `Edge.direction_label` (`models.py:155-157`) returns it with no reference to direction.
- `explorer/lineage/service.py:271-286` copies that same label onto the outgoing view **and** the incoming view.
- `lineage.html:112` renders it verbatim under the heading `Incoming`.

Consequences, in descending order of how directly I observed them:

1. **Observed in a screenshot.** `runs/20260905T050401Z/W5.png`, Incoming section: `has campaign child: RHACO-CMP-20260628-001`. On that page, `RHACO-CMP-20260628-001` is the *parent*. The sentence states the converse.
2. **Observed in probe JSON.** `runs/20260905T050330Z/W6.json` → `parent_api_incoming_amends` = `{direction: "incoming", direction_label: "amends", from_id: <the amendment>, to_id: <the parent>}`. The parent hand's page says it *amends* its own amendment.
3. **Derived from code, not screenshotted.** `RELATION_LABELS["supersedes"] == "is superseded by"`. W6 captured the chain v1_6 → v1_7 → v1_8 → v1_9 with v1_9 marked `current head`. On v1_9's own lineage page the incoming edge from v1_8 therefore renders **"is superseded by: RHACO_Card_YAML_Schema_Specification_v1_8"** — the current head reported as superseded by its own predecessor.

PROMPT.md 5.5 requires that *"directional relationships must be displayed directionally."* A section heading plus a sentence that states the converse is not that; it is a display that requires the operator to know to invert it.

Two things make this worse than a wording slip:

- **The reader gets it right on the same data.** `reader/service.py:416-430` builds `"is superseded by"` for outgoing and `"supersedes"` for incoming. So the direction-aware form was understood in this codebase — and then the reader's *generic* "Lineage (all typed edges)" list (`reader.html:218-231`) uses the direction-blind label anyway, so a single reader page can display the correct sentence in one section and the reversed sentence in the next for the same edge.
- **The probe encodes the defect.** `_run_w5` asserts `label != RELATION_LABELS.get(rel, rel)` → FAIL. It compares the product's rendering against the very constant the product renders from. It can only detect a divergence between two copies of the same answer.

I considered arguing PASS on the structural reading and I decline to. The sentence is the thing the operator reads.

### Notes attached to the gates I passed

- **Gate 2** holds *as written*: the regression is scoped in `SCOPE.md` row 16 with its cause, and `gold_v1_1_compat.json` shows `lists_equal 40`, adapter and module both 0.675. I add a qualification the build does not: the scoping reached the repository and not the product (see ranked issue 2).
- **Gate 5** is *"no exception on the exercised set"*, not *"no exception on the corpus."* Twelve presets touch on the order of a dozen documents out of 1,443; the class of defect that produced the W6 500 was invisible until one particular card was reached. The broader support is `card_agreement.json` — 120 live cards, every `reader_status` 200, `reader_errors: []` — and that run is not in `build_state`.
- **Gate 1** rests on KG/KB1 evidence captured at 04:31Z and 01:42Z, before the reader repair at 04:55:53Z. It still passes on W1's production evidence at 05:03Z.

---

## 2. The ten criteria

Full assessments are in the structured `criteria` block; the compressed form:

| Criterion | Reading |
|---|---|
| Retrieval fidelity | Mechanism strong (no ranking reimplemented; narrowing labelled and non-reordering); one stale figure on the surface |
| Metadata fidelity | Best part of the build; card/index/document kept distinct with a per-field verdict. Blemish: every abstract labelled `...` |
| Relationship fidelity | Data faithful, nothing inferred, `amends` limit disclosed; **prose not direction-aware** |
| Authority-boundary legibility | Excellent and consistent; notice verbatim in every footer, guarded by a word-for-word test |
| Browse/search usability | Complete and honest; form-first search page, catalog table wider than its viewport |
| Reader comprehension | Strong content model (independent anchor re-verification, labelled degradation); horizontal overflow |
| Lineage comprehension | Richest surface; needs interpretation because of the labels, identical link text, crowded graph |
| Degradation honesty | Exemplary — the clearest evidence the build understood its brief |
| Accessibility | Well above norm; `/` inert on 4 of 5 pages; `role="img"` over interactive SVG links; reflow |
| Performance (local interactive) | Comfortable everywhere measured (38 ms–1.83 s); the one expensive operation is unmeasured |

Throughout I tried to hold the prompt's distinction — what the product **does** versus what it **claims**. The three places where those diverge are ranked 1, 2 and 8.

---

## 3. Ranked issue set

Ranked by consequence to a scientist relying on this tool, not by cost to fix. Full evidence in the structured `ranked_issues` block.

1. **Incoming typed edges carry the outgoing sentence** — lineage states the converse of the record. *fidelity*
2. **Search page shows July's `Recall@10 0.700` as present standing**, and `SCOPE.md` says the page shows no such number. *fidelity*
3. **No known-bad probe run exists at or after the reviewed commit** — every ledger entry predates the reader repair; re-running costs no round. *fidelity*
4. **Reader page overflows its viewport horizontally** on every capture, both substrates. *polish*
5. **Identifier-mode results have no Evidence disclosure** — the one mode where the answer is unambiguous says nothing. *fidelity*
6. **An active catalog `lifecycle_state` filter can become invisible and unclearable.** *polish*
7. **Shared `doc_id`s render as runs of identical links, including a self-pointing `amends` edge.** *polish*
8. **`build_state.json` is two builder rounds stale** — understates rounds consumed, overstates rounds remaining. *fidelity*
9. **`/` advertised on five pages, works on one.** *polish*
10. **Live freshness scan duration never measured.** *polish*

---

## 4. `ref_score`

**8 / 10. Below the 8.5 pass threshold. ORDINAL, not metrological.**

Above the 7 anchor because the tool does not, in general, require interpretation and does not impede comprehension. Below 8.5 because that anchor requires *"minor polish issues only"* and two findings are not polish: the lineage direction labels, and a retrieval figure the build has itself measured differently on the corpus being searched.

No calibrated exemplar exists for this UI class — no second critic, no prior round, no other scored tool of this kind. The score is a placement between published anchors, not a measurement. To become repeatable it would need two or more independently scored exemplars on the same scale **and** two or more critics (or matched rounds on an unchanged product), with at least one critic from a different model family than the orchestrator per `docs/LAYERS.md` §3. None exist. PROMPT.md §7 anticipates this and directs qualitative convergence on unchanged ranked issue sets — my list above is written to be compared item by item, and that comparison, not the digit, is the instrument.

---

## 5. What the build's own measurement cannot see

Eight items are in the structured `blind_spots` block. The four that matter most:

- **W3 cannot fail for the reason its label implies.** It compares the page's ids to a constant snapshotted from `gold_v1_1_compat.json` — produced by the same adapter, module and database. A regression pin, not a baseline-preservation check.
- **"Adapter matches module 40/40" is near-tautological.** `adapter.search_hybrid` calls the module and wraps the ids in order, in three lines. `LAYERS.md` states the limit correctly; `build_state`'s reading leans on the number harder than the number can bear.
- **W5's `direction_label` assertion is a check that cannot fail on the defect it appears to guard** — it compares the product against the constant the product renders from. That is exactly how ranked issue 1 survived a qualified production probe.
- **Keyboard navigation is string-matched in three places and executed in none.** The `#keyhelp` contract test is honest about this in its own docstring; L2 does not fill the gap. I am the first layer to have looked, and `/` is inert on four of five pages.

And the item I owe the reader about myself: **I share a model family with the orchestrator.** Where I agree with the build's judgment — the gold regression is a substrate fact, the `amends` click-through is correctly scoped, the duplication is the real defect behind O-2 — discount it. The load-bearing part of this review is the four places I disagree: gate 7, the Mode standing figure, the ledger's currency, and `build_state`'s own arithmetic.

---

## 6. Round-2 questions

Eleven concrete asks are in the structured `round_2_questions` block. The three that would move the score:

1. **Direction-aware `RELATION_LABELS`**, plus one preset centred on a supersession *head* asserting the rendered sentence (not just the `data-*` triple). Retires ranked issue 1 and my FAIL on gate 7.
2. **Date or remove the Mode standing figures**, and correct `SCOPE.md` row 16. Retires ranked issue 2.
3. **Re-run the five known-bad fixture presets at the current commit and pin the commit in the ledger.** Costs no builder round. Until that exists, KB2 and KB4 are not qualified for the code now shipping.

Two cheap measurements would settle findings rather than argue them: `scrollWidth <= innerWidth` in any production preset, and one timing of the live freshness scan.

And one procedural ask: state, item by item, which of my ten ranked issues the build accepts, disputes (with evidence), or declines within budget. PROMPT.md §7 defines convergence on unchanged ranked issue sets across two rounds; an explicit disposition is what makes round 2's comparison a measurement rather than a re-derivation.

---

## Appendix — what I actually read

`PROMPT.md` (full), `ARCHITECTURE.md`, `CONSTRAINTS.md` (S3/S6/S7/S8, O17/O18/O24/O29), `SCOPE.md`, `docs/LAYERS.md`, `docs/REFERENCE.md`, `build_state.json` (all top-level sections; `rounds`, `budgets`, `modules`, `open_items`, `director_rulings`, `l4_oracle_runs`, `l4_card_agreement_runs`, `acceptance_set_runs`, `objective_gates_status`); `explorer/app.py`, `config.py`, `models.py`, `faults.py`; `corpus_adapter/adapter.py` and `sql.py`; `catalog/service.py` + template; `search/service.py`, `routes.py` + template; `reader/service.py`, `routes.py` + template + CSS; `lineage/service.py` + template; `diagnostics` template; `web/static/app.css` + `app.js`; `tools/probe_corpus_explorer.py` (W1–W6 runners, preset registry region); `tools/l1_index_write_check.py`; `tests/integration/test_keyhelp_contract.py` and the `tests/web` inventory; `docs/probe-qualification/README.md`, `qualification_ledger.json`, `gold_v1_1_compat.json`, `card_agreement.json`; the twelve production observation JSONs and `run_summary.json`s of `20260905T0503*`/`0504*`; the FINAL fixture suite `20260905T043117Z` (KG, KB1–KB5, `run_summary.json`); KB3's qualification run `20260905T043102Z`; and the screenshots `W3.png`, `W4.png`, `W5.png`, `W9.png`, `diagnostics.png` plus the PNG geometry of every capture in the two most recent sets.
