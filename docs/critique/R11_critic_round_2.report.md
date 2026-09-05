# Critic round 2 -- RHACO Corpus Explorer (strand S8-CR2)

*Filed by the integrator on the critic's behalf: the critic is read-only and writes nothing (ARCHITECTURE.md section 2). The text below the horizontal rule is the critic's own, verbatim.*

| Field | Value |
|---|---|
| Strand | S8-CR2, critic round 2 -- the second of the two-round convergence window |
| Model | `claude-opus-5[1m]`, agent type Explore, read-only, effort xhigh (explicit) |
| Reviewed at | `6d74f2e3b784cb5e564d68965247d16451a9da61 (working tree clean; product tree byte-unchanged since fe4e053 -- `git diff --stat fe4e053..HEAD` touches only build_state.json, docs/probe-qualification/**, and docs/rounds/R11_critic.prompt.md, so the convergence evidence set is genuinely contemporaneous with the code I reviewed)` |
| Prompt of record | `docs/rounds/R11_critic.prompt.md`, sha256 `D8CEF25F42CEC8CA93AAE09620486C49E9FDF6FB748ADC965E9B4B418BCC8C03` (verified by the strand before acting) |
| Window | 2026-09-05T17:21:15.9293132Z - 2026-09-05T17:41:46.1518802Z |
| `ref_score` | **8** against a pass threshold of 8.5 -- unchanged from round 1 |
| Score precision | **ORDINAL, not metrological** |
| Critic scale validly usable | **NO** -- see part 6; PROMPT.md section 12's 8.5 clause is therefore vacuous |
| Objective gates | **9 PASS / 0 FAIL** (gate 7 moved FAIL -> PASS) |
| Round-1 issues | 6 repaired, 1 partially, 2 repaired-but-created-a-new-problem, 1 not repaired |
| Build dispositions disputed | **3 of 10** (ranks 2, 4, 8) |
| Convergence | **NOT CONVERGED** |
| BF-1 claim | verified honest, with two additions the register should carry |
| O-4 convergence-blocking | **NO** |

## Integrator note

Five of this report's top seven ranked findings are against integrator-owned work -- the ledger, the
direction oracle, the import-boundary check -- and not against any builder. The critic's central
argument is that the defect class the sealed audit named as this harness's structural weakness, a
claim in prose that nothing checks against the artifact, was reproduced three times inside the
artifacts built after round 1 to end it. Two of those three are mine. Filed unedited, including the
parts that say so.

---
# Critic report — RHACO Corpus Explorer, round 2 (strand S8-CR2)

**Instruction of record:** `docs/rounds/R11_critic.prompt.md`, sha256 observed `D8CEF25F42CEC8CA93AAE09620486C49E9FDF6FB748ADC965E9B4B418BCC8C03`, 14,572 bytes — **matches** the pin in the dispatch. Read in full before acting.
**Window:** 2026-09-05T17:21:15.9293132Z → 2026-09-05T17:41:46.1518802Z.
**Reviewed at:** `6d74f2e`, working tree clean. `git diff --stat fe4e053..HEAD` touches only `build_state.json`, `docs/probe-qualification/**` and `docs/rounds/R11_critic.prompt.md` — no file under `explorer/`, `tools/`, `tests/` or `fixtures/` — so the convergence evidence set is genuinely contemporaneous with the code I read.
**Mode:** read-only. I created, edited and deleted nothing; ran no test, no lint, no server, no probe; committed nothing. Every behavioural claim below is attributed to an artifact someone else captured, **except** the capture geometry in ranked issue 1, which I derived myself from PNG headers on disk.

| Field | Value |
|---|---|
| `ref_score` | **8**, unchanged, against a threshold of 8.5 |
| Score precision | **ORDINAL, not metrological** |
| Critic scale validly usable | **NO** — and PROMPT.md §12 makes that load-bearing |
| Objective gates | **9 PASS, 0 FAIL** (round 1: 8 PASS, 1 FAIL) |
| Gate 7 | **FAIL → PASS.** A real reversal on a real repair |
| Convergence | **NOT CONVERGED** |
| O-4 convergence-blocking | **No** |

---

## 0. The short version

Round 1's worst defect is genuinely gone. Lineage no longer states the converse of the record; a supersession head can no longer report itself superseded by its own predecessor; the reader page can no longer print the correct sentence in one section and its converse in the next. That was ranked 1, it was my only gate FAIL, and it is fixed at the mechanism rather than at the symptom — `relation_sentence(relation, direction)` with two tables behind it, called from every prose call site I could find. Six of my ten items are cleanly repaired, two are partial or repaired-with-a-new-problem, one is honestly declined under an explicit scope ruling, and one is asserted repaired and is not.

The build also did the harder procedural things: it withdrew its own gate PASS in favour of my FAIL, dispositioned all ten items in writing so this round could be a comparison rather than a re-derivation, re-ran every instrument at one commit, and re-qualified the five known-bad classes **with their faults injected** rather than as a no-fault smoke run. It declared two BOUNDED_FAILs and a governance defect it could have buried. I have no complaint about the honesty of the process.

Now the part that matters, and it is one sentence: **the mechanism that produced this build's characteristic defect kept running, and produced three new instances inside the artifacts built to stop it.**

The sealed audit named that mechanism precisely — "FALSE OR UNSUPPORTED CLAIMS IN PROSE about code behaviour … The harness tests behaviour well and audits its own claims poorly." Since my round-1 report the build has produced: an oracle whose report says **213 pages rendered** when it rendered none; a comment reading **"never raw SQL from here"** directly above two raw `SELECT` statements; a ledger asserting **"ALL FIVE sealed defect items are now closed"** while carrying `"still_live": true` on one of them; and a disposition reading **"landed: YES … fixed once in app.css"** for a repair its own builder twice recorded as UNVERIFIED and which the evidence on disk says did not take.

That last one is this report's headline, so I will show the work.

---

## 1. The reader overflow: what the record says, and what the files say

Round-1 ranked issue 4 was that the reader page overflows its viewport horizontally on every capture. `build_state.json` records it repaired.

The probe pins `VIEWPORT = {"width": 1280, "height": 900}` (`probe_corpus_explorer.py:153`) and screenshots with `full_page=True` (`:708`, `:1175`), so a capture's width is the document's scroll width. The diagnostics observation at `20260905T171520Z` independently records `viewport: {height: 900, width: 1280}`. I read the IHDR width of every capture in the convergence set and in round 1's set:

| Preset (final page) | Round 1 | Convergence commit |
|---|---|---|
| **W1 — `/doc/…`** | **1387** (`050346Z`) | **1387** (`171444Z`) |
| **W9 — `/doc/…?line=1`** | **1387** (`050408Z`) | **1387** (`171510Z`) |
| W2, W3, W4, W5, W6, W7, W8, W10, diagnostics, KG | 1280 | 1280 |

Every capture whose last page is the reader is 1387. Every capture whose last page is not the reader is exactly 1280. The overflow is reader-specific, it is 107 px, and **it did not move by one pixel across the repair.**

The CSS did land — `app.css:153` extends the shared `pre` rule with `overflow-wrap: anywhere; word-break: break-word`, and `:170-172` gives `.doc-body table` a fixed column budget. Those are real rules addressing a real mechanism. They do not reach whatever is 107 px too wide, which means the cause was never `pre` or `.doc-body table`, and nobody knows what it is.

The web strand said so, unprompted, twice: *"Whether the reader page now actually fits 1280px is UNVERIFIED as rendered geometry"* and *"the static tests … cannot prove the reader page actually renders within 1280px."* It even separated the gap from the keyboard gap so one could not stand in for the other. That is exemplary conduct by the builder.

`build_state.json` `critic_round_1_dispositions` rank 4 records: *"landed: YES — round 8, S8-B16, merged 014ef53; fixed once in app.css rather than per module."* No qualifier.

**The ledger dropped the caveat its own builder insisted on keeping.** I nearly accepted it — I read the disposition, read the CSS, found it plausible, and was writing "repaired" when I decided to re-derive round 1's *evidence* rather than round 1's *finding*. That took two minutes and reversed the verdict on the top item in this report.

---

## 2. Objective gates, independently re-assessed

| # | Gate | Verdict | Differs from `build_state`? |
|---|---|---|---|
| 1 | Exact identifier fixture targets correct | PASS | no |
| 2 | Gold-query compatibility not regressed beyond baseline unless scoped | PASS as scoped | no |
| 3 | No write path to corpus from UI | PASS | no |
| 4 | No arbitrary text-to-SQL | PASS | no |
| 5 | Zero unresolved template/runtime exceptions in acceptance probes | PASS | no |
| 6 | Card `status` and CMP `lifecycle_state` never collapsed | PASS | no |
| 7 | **Typed relation direction preserved** | **PASS** *(round 1: FAIL)* | no |
| 8 | Flat hybrid remains default | PASS | no |
| 9 | Semantic-unavailable degradation explicit and functional | PASS | no |

Gate 5: all twelve convergence observations carry `page_errors: []` and `console_errors: []`. W5's FAIL is an assertion failure, not an exception. My round-1 caveat stands unchanged and I re-state rather than retire it: this is *no exception on the exercised set*, not *on the corpus*.

Gates 3 and 4 I re-derived rather than trusted: the five index-writing names appear nowhere under `explorer/`; the only POST is compute-and-display; every SQL identifier position is guarded by a fixed whitelist (`build_catalog_facet_column_query` raises `ValueError` unless `column in _FACET_COLUMNS`) and every value is bound.

### Gate 7 — I failed it, and I now pass it

The repair is real and I say so plainly. `models.py` now carries `RELATION_LABELS` **and** `RELATION_LABELS_INCOMING` behind `relation_sentence(relation, direction)`; `Edge.direction_label` survives with a docstring naming the converse defect. Every prose call site routes through the function: lineage's three edge lists (`service.py:365/380/390`), lineage's reasoning trail (`:524`), the reader's generic typed-edge list (`reader/service.py:458/463/473`). I checked the render path myself rather than trusting the oracle — `lineage.html:84/101/118/172` print the same view field `routes.py:90` serialises, and `tests/lineage/test_api_parity.py` asserts parity — so the L4 evidence does transfer to the HTML.

**Judging the instrument, not its output.** In round 1 I named "a check that could not have failed" three times. I asked it of this one.

*Can it fail?* **Yes.** `EXPECTED_SENTENCES` is hand-written, not imported; eight committed tests construct violations and assert they are caught, including my exact CONVERSE case and a head rendered as superseded. `test_a_head_with_the_correct_sentence_is_clean_but_still_counted` — asserting the head check *runs* on a correct head so coverage is distinguishable from absence — is the best piece of instrument design in this round.

*Does the independence hold?* **Partly.** It is duplication, not derivation: the four pairs are string-identical to the product's two tables. That buys independence against future drift and none against a shared misreading of `CONSTRAINTS O8` — both tables were written inside this build. I checked O8 myself and all eight sentences are right, so the risk did not materialise. But the oracle establishes *"the product still matches a copy a human once approved,"* not *"the sentences are true."*

*Is 213 cards / 93 heads adequate?* **Yes, for the claim made.** 5,052 edges is not a spot check, and the two-stratum sample is a genuinely good design decision — the recency stratum alone returned **zero** chain heads, so check 3 would have gone unexercised.

*Are the two self-defects soundly fixed?* **Yes, and better than the bugs required.** The `card_ref` normalisation addresses the actual cause of the zero-page run, and the empty-run guard is stronger than needed: it fails on no page, no edge, **and** no chain head. `PAGE_ERROR` counts as a defect rather than a skip.

*Where it remains weaker than the claim it carries.* Three things, none enough to withhold the gate, all worth naming:

1. **It renders no page.** It fetches `/api/lineage/…`, which `routes.py:4` calls the "JSON twin." No template is exercised. Yet the docstring says *"pages are rendered in-process through TestClient"* and the report says `pages_rendered: 213`.
2. **Its coverage is narrower than the gate.** It reads only `outgoing` and `incoming` — never `unresolved`, never `reasoning_trail`, never `graph_edges`, and never the reader page, whose three narrative sentences are hardcoded literals (`reader/service.py:421/427/436`) bypassing `relation_sentence` entirely.
3. **Check 3 cannot fail unless check 1 already has.** Its filter selects exactly the set check 1 emits as `CONVERSE`. Its real contribution is the sampling stratum and the empty-run guard, not detection.

**Verdict: gate 7 PASSES.** Its report should say *213 API responses compared*, not *213 pages rendered*.

---

## 3. BF-1 — is "the check broke because the product got right" honest?

**Yes.** I verified rather than accepted it, and it holds on all three questions the prompt put.

*Is the reported reason the whole failure?* `runs/20260905T171500Z/W5.json` carries exactly one entry in `reasons`. Alongside it: `page_errors: []`, `console_errors: []`, `failed_requests: []`, `fault_detected: false`, and both `independent_checks` VERIFIED — the probe read two `card.yaml` files off disk and confirmed each declares its `depends_on`.

*Are the flagged values correct?* Both, checked against O8 and not against the build's word. O8: `campaign_child` from = CMP, to = child — so an incoming edge is read from the child's end and **"is campaign child of"** is the true sentence. O8: `cites` from = citing card — so an incoming edge means someone cites this card and **"cited by"** is right. W5 is flagging the two sentences that are true.

*Is the reading honest or convenient?* Honest. `probe_corpus_explorer.py:1956-1962` compares every bucket against the **outgoing** table imported from `explorer.models`. It is my round-1 finding — *"it compares the product against the very constant the product renders from"* — caught failing in the direction that proves it. The failure was accepted in writing at `c861680` **before** round 6 was dispatched, not rationalised afterwards; the preset was left red rather than edited green; the compensating control was built and run. The alternative — keeping a vestigial direction-blind field alive so W5 stayed green — would have made the probe verify something no human sees. Declining that trade was correct.

**Two things the register does not say, and should.** First, W5 is now a *constant-FAIL* preset, so its four still-valid assertions — page/API parity, campaign_child target agreement, trail chronology, and two on-disk card cross-checks — have no automated signal. A future regression arrives as a second string in `reasons` on a preset already red, catchable only by a human reading the JSON. The build read it correctly this time; it has not recorded that reading it is now mandatory. Second, `page_edge_count` is a **set** cardinality and `api_edge_count` a **list** length (21 and 22, under symmetric names), and the parity assertion compares sets — so the duplicate BF-2's double-append produces is deduplicated before comparison, invisible at the one check positioned to see it.

---

## 4. The new instruments, as instruments

**`l1_index_write_check.py` check 2 (SA-4's repair).** Establishes: no `.py` file outside a named licence set contains a line matching `^\s*(?:import|from)\s+(RHACO_corpus_index|RHACO_tool_catalog_librarian)\b`, or `import_module(` / `__import__(` with those names. Appears to establish: that the prose import boundary holds. The gap is smaller than round 1's three instances and is the same gap — the regex does not see `spec_from_file_location` + `exec_module`, **the exact pattern both of the build's own new test files use**. Its six constructed violations are all in forms the regexes already match; none probes the matcher's own boundary. The `tools/`-by-file-not-by-path ruling is genuinely good: a directory allowlist would have hidden a probe that started importing the module.

**SA-4 is not closed on the build's own description of it.** Its `verified_now` names four unchecked things — the import boundary, *"no `sqlite3.connect` check at all"*, read-authority paths, and *"`docs/LAYERS.md` also lists pytest under 'L1 Static', a category slip."* One was repaired. `docs/LAYERS.md:9` still lists `pytest tests/` under **L1 Static**. And the item carries `"still_live": true` while the same object says all five are closed.

**`l4_direction_oracle.py`.** Assessed in §2. One more thing belongs here because of what these instruments were built to end: lines 203-204 read *"through the adapter's own documented queries — never raw SQL from here,"* directly above two hand-written `SELECT` statements on `adapter.connect()`. It breaks no gate and changes no result. It is a false claim in prose about what the code does, inside the instrument commissioned to close the class of false claims in prose about what code does. The instance is trivial. **The recurrence is the datum.**

---

## 5. The ten criteria

Full assessments are in the structured `criteria` block. Compressed:

| Criterion | Reading | Moved? |
|---|---|---|
| Retrieval fidelity | Mechanism unchanged and strong; identifier evidence added; bare 0.700 gone — but the build's own figure now carries a date no run bears | yes |
| Metadata fidelity | Still the best part; ellipsis blemish repaired | yes |
| Relationship fidelity | Moved most, and for real; BF-2 and three unchecked reader literals hold it short | yes |
| Authority-boundary legibility | Unchanged and excellent; O-4 leaves S8 satisfied on one surface, not product-wide | no |
| Browse/search usability | Filter trap closed; column budget; a real global search field | yes |
| Reader comprehension | Content model improved; **layout did not** | yes |
| Lineage comprehension | Strongest surface again; direction-neutral filter chips are unasked-for good work | yes |
| Degradation honesty | Improved from an exemplary base via SA-1; still no run exercises graph under `--disable-vec` | yes |
| Accessibility | The claim is now true; the behaviour is still unexecuted by any layer | yes |
| Performance | Comfortable; the live freshness scan still unmeasured | no |

---

## 6. Ranked issue set — current state

Ranked by consequence to a scientist relying on this tool. Full evidence in the structured block. **Round 2 is longer than round 1 (13 vs 10) and I have not compressed it to signal progress**; five items are carried and ranked low precisely because they are well declared. The load-bearing part is 1–4.

1. **The reader page still overflows, and the record says it was fixed.** *fidelity* — §1.
2. **The search page dates the build's own figure `2026-09-04`; no oracle run bears it, and `SCOPE.md` says so.** *fidelity* — `gold_v1_1_compat.json` `started_utc` is `2026-09-05T17:16:15+00:00`. SCOPE row 16, corrected in the same round, calls that date *"an undated-timezone date … the same class of ambiguity this round removed from the search page"* — and left the page carrying it.
3. **The direction oracle's report describes a stronger observation over a wider surface than it made.** *fidelity* — §2.
4. **`build_state.json` contradicts itself about SA-4's closure; one named sub-defect is untouched.** *fidelity* — §4.
5. **W5 is permanently red, so four valid assertions lost their signal; its parity check is set-based.** *fidelity* — §3.
6. **The import-boundary check misses the dynamic-import form the build's own tests use.** *fidelity* — §4.
7. **The oracle claims it issues no raw SQL, above raw SQL.** *fidelity* — §4.
8. **O-4: the diagnostics rerank figure is still undated.** *polish* — disclosed, not concealed. **Not convergence-blocking.**
9. **The reader's three narrative edge sentences are hardcoded literals outside every check.** *polish* — correct today; the conditions that produced ranked issue 1 persist, and `"campaign child of"` differs from the canonical `"is campaign child of"`.
10. **The live freshness scan is still unmeasured.** *polish* — the only timing on record, W8's `elapsed_s: 0.058`, is a fixture scan.
11. **Keyboard behaviour has never been executed by any layer.** *polish* — stated plainly by build and builder alike.
12. **BF-2: `edges_for` double-appends, unfixed at source.** *fidelity* — ranked low **because** it is correctly declared. That is the point of declaring it.
13. **O-6: `reader.html` asserts a diagnostics state name.** *polish*.

---

## 7. `ref_score` and whether the scale was usable

**8 / 10. ORDINAL, not metrological.** Unchanged from round 1 — and an unchanged digit does not mean an unchanged product.

Above 7: the product moved up, materially. The single defect that most forced an operator to interpret rather than read is gone. Below 8.5: that anchor requires *"minor polish issues only"* and three findings are not polish — a 107 px overflow on the surface a document explorer exists to provide, a wrong evaluation date on the build's own retrieval figure in a provenance tool, and an instrument reporting 213 rendered pages having rendered none. Not lower than 8, because §7 scores *human-facing product quality after the gates*, not bookkeeping, and on the product the movement is upward. Not 8.25, because nothing calibrates that distinction and inventing it is the invented precision the prompt forbids.

**Was the critic scale validly usable? No.** Every condition I recorded in round 1 is still unmet: no calibrated exemplar, no second critic, none from a different model family (MOD-1 pins the orchestrator to `claude-opus-5[1m]`; I am `claude-opus-5[1m]`). The condition someone might mistake for satisfied is *"matched rounds on an unchanged product"* — two scores now exist, but the product changed across seven builder rounds and a contract change between them. Two identical digits from one critic on two different products is not a repeatability floor; it is a coincidence I have no instrument to distinguish from agreement.

**The consequence for §12, as my reading and not a ruling.** §12 conditions PASS on the score reaching 8.5 *"if the critic scale was validly usable."* It was not, so that clause is vacuous — it neither blocks PASS nor licenses it, and **no one should read my 8 as the thing standing between this build and PASS.** What binds unconditionally is the rest: all objective gates pass (they do, all nine), **and** production-path probes pass — which they do not, 11 of 12, W5 declared in advance as BF-1. On §12's own words that is the BOUNDED_FAIL definition, with the probe budget exhausted and not waived. I record this so the score is not made to carry a terminal-state decision it is not calibrated to carry, in either direction.

---

## 8. Convergence

**NOT CONVERGED.**

Read literally, §7's rule returns something uninformative: my set is plainly not unchanged. Six repaired, two partial, two unrepaired, eight new.

**What "unchanged" should mean when every issue was accepted and acted on.** The rule was written to detect a *fixed point* — a state where a fresh review finds what the last one found. It assumes a build that may or may not act. When a build accepts and acts on everything, **the rule inverts**: an unchanged set would mean the repairs did not take, which is the worst outcome, and a changed set means they did, which is the best. In this regime the literal rule cannot distinguish *converged* from *still improving*; it can only distinguish *repairs landed* from *repairs did not*. Against this build it reports that the repairs landed. That is true, and it is not convergence.

**The reading I would defend.** Convergence should mean the *class* distribution is stable and no longer regenerating. Round 1's classes: (a) direction prose stating the converse; (b) a claim in prose that nothing checks against the artifact; (c) layout and keyboard polish; (d) a check narrower than its guarantee. Round 2: **(a) is gone**, genuinely and at the mechanism. (c) persists with its principal instance unmoved. (d) persists, one degree smaller. And **(b) has produced three new instances inside artifacts created after my round-1 review, in direct response to it.**

A build that reproduces the critic's named defect class inside the compensating controls for that class has not reached a fixed point.

**What this does *not* assert:** that the build is in bad shape (it is not — all nine gates pass and the repairs are mostly real and well made), or that eight more rounds should be spent (most of my remaining list would not repay one).

**Is O-4 convergence-blocking? No** — and I decided this on merits, not accommodation. O-4 is an *omission* on a disclosed open item. Ranked issue 2 is an *affirmatively false* date on a live surface, which the build's own scope register already contradicts. If a round is to be spent on a dated figure, it is not that one. The Director's reasoning — that a third integrator text edit would turn a twice-observed pattern into a habit — is right about O-4. I think it is wrong about the four statements in ranked issues 2, 3, 4 and 7, which are not omissions but assertions false about the artifact beside them.

**What a third round would need to find.** Not features. (1) **Measure the reader page's rendered width and fix what the 107 px is** — running the probe costs no builder round, and until someone knows the cause, further CSS is guessing. (2) **Correct four false strings and one ledger field.** (3) **Find out whether class (b) is still regenerating** — every instance I found came from reading a claim and then reading the artifact it describes, and *no layer of this harness does that*. A round that added even a crude claim-audit pass and came back empty would be evidence of a fixed point that neither of my rounds can supply. A round that merely fixed my thirteen items would leave the generator running.

**Not worth the budget:** a diagnostics round for O-4; a fifth probe round; re-litigating BF-1 or BF-2, both correctly declared; and **another critic round from me** — a third pass from the same model that wrote the first two adds no independence and would be the least valuable use of the remaining eight rounds.

---

## 9. What I owe the reader about myself

**Where bias almost won.** On ranked issue 4 I read the disposition, read the CSS, found it plausible, and was writing *"repaired."* I only did not because I had decided to re-derive round 1's *evidence* rather than its *finding*. Every other "repaired" verdict rests on source reading, because for most of them no observable exists that I can reach: they establish that the code now **says** the right thing, not that the product now **does** it.

**Gate 7.** I failed it, asked for a fix, got it, and now pass it — a judgment that flatters my own prior review. The defensible alternative: a critic from another family might hold it at CANNOT-DETERMINE because the oracle never renders a page and never touches the reader surface. I rejected that because I read the template myself. But that confidence comes from my own source reading — the same faculty the build used — and if I am wrong I am wrong in the direction that agrees with the build.

**The pull of total agreement.** The build accepted all ten items and disputed none. My three sharpest new findings all came from checking an artifact against a claim; I did far less of that on the parts I praised in round 1 — the SQL, the evidence disclosures, the degradation vocabulary. I spot-checked those and they held. **If something is wrong in this build, that is where I would look.**

**The sealed audit.** I was told its contents before writing, so my assessment of the SA-1/2/3/5 repairs is not an independent detection — I verified repairs whose targets I had been handed. Only the SA-4 finding is mine, and only because `build_state` contradicted itself in a way visible from two fields of one object.

**And the measurement the seal took does not change.** Four of five sealed defects were missed by four builder waves, 262 tests, twelve green presets, two L4 oracles and a dedicated Opus critic — me. The build's own record says closing them later does not retroactively make the harness adequate. I agree, and I add the round-2 datum: the class those defects belonged to is still producing, and it is now producing inside the instruments built to end it.

---

## Appendix — what I actually read

`docs/rounds/R11_critic.prompt.md` (full, hash-verified); `docs/critique/R06_critic_round_1.report.md` (full); `PROMPT.md` §§5, 7, 9, 12, 13; `CONSTRAINTS.md` (O8–O21 region); `SCOPE.md` (rows 7, 16); `docs/LAYERS.md`; `ARCHITECTURE.md` §4.6; `build_state.json` — `budgets`, `governance_defects`, `open_items` (O-1…O-6), `objective_gates_status` incl. `critic_round_1_disagreement`, `sealed_audit_release` (all six items, tally, remedy_decisions, status_after_round_6), `critic_round_1_dispositions` (all ten), `bounded_fail_register`, `l4_direction_oracle_runs`, `convergence_evidence_set`; `explorer/models.py`, `lineage/service.py` + `routes.py` + template, `reader/service.py` (edge-link region) + template refs, `search/service.py` (mode-standing + identifier region) + template refs, `catalog/service.py` + template, `diagnostics/service.py`, `corpus_adapter/adapter.py` (notice region), `availability.py` (probe region), `sql.py`, `web/templates/base.html`, `web/static/app.css`; `tools/l4_direction_oracle.py` (full), `tools/l1_index_write_check.py` (full), `tools/probe_corpus_explorer.py` (`_run_w5`, preset registry, viewport/screenshot); `tests/integration/test_direction_oracle.py` (full), `tests/integration/test_import_boundary_check.py` (full), `tests/web` inventory; `docs/rounds/R10_web.report.md`; `docs/probe-qualification/direction_oracle.json`, `gold_v1_1_compat.json`, `qualification_ledger.json`; the five known-bad re-qualification runs `20260905T1714{10,13,15,17,20}Z`, the FINAL suite `20260905T171432Z`, and all twelve production observations `20260905T1714*`/`1715*` — plus the IHDR geometry of every `W*.png`, `KG.png` and `diagnostics.png` in the workspace.
