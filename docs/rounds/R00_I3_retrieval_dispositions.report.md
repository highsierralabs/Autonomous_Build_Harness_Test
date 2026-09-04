# R00_I3_retrieval_dispositions -- strand report (round 0 inspection)

strand_id: I3
agent_id: a355d02935d603388
workflow_run: wf_c2507f3a-9da
model_id: You are powered by the model named Sonnet 5. The exact model ID is claude-sonnet-5.
t_start_utc: 2026-09-04T02:33:51.8885024Z
t_end_utc: 2026-09-04T02:36:50.9111602Z
transcript_last_write_utc: 2026-09-04T02:39:06+00:00
files_read:
  - C:\RHACO\docs\reports\RHACO-ANL-20260712-001_M3_Gate_Evaluation_And_Disposition.md
  - C:\RHACO\docs\reports\RHACO-ANL-20260712-001_M3_Gate_Evaluation_And_Disposition.card.yaml
  - C:\RHACO\docs\reports\RHACO-CMP-20260628-001_Corpus_RAG_Retrieval_Layer.md
  - C:\RHACO\docs\reports\RHACO-CMP-20260628-001_Corpus_RAG_Retrieval_Layer.card.yaml
  - C:\RHACO\docs\reports\RHACO-CHG-20260712-002_M4_Hybrid_Default_Flip.md
  - C:\RHACO\docs\reports\RHACO-CHG-20260712-002_M4_Hybrid_Default_Flip.card.yaml
  - C:\RHACO\working\eval\gold_queries.yaml
  - C:\RHACO\working\eval\gold_queries_v1_2.yaml
  - C:\RHACO\docs\reports\RHACO-ANL-20260712-002_Corpus_RAG_Gold_Query_Set_v1_2_Freeze.md
  - C:\RHACO\docs\reports\RHACO-ANL-20260712-003_M4_Acceptance_And_Campaign_Closure_Evaluation.md
  - C:\RHACO\docs\reports\RHACO-CHG-20260712-003_M4_Gold_v1_2_Harness_v1_3_Eval_And_Certification.md
  - C:\RHACO\docs\reports\RHACO-CHG-20260716-002_M5_Closeout_Style_Guide_v1_9_And_Campaign_Close.md (grep-context only, line 17)
  - C:\RHACO\docs\reports\RHACO-CMP-20260903-001_Corpus_Explorer_Autonomous_Build_Harness.md (grep-context only)
  - C:\RHACO\docs\reports\RHACO-CCX-20260903-001_Corpus_Explorer_Build_Dispatch_Handoff.md (grep-context only)
  - C:\RHACO\docs\handoffs\RHACO-HND-20260903-001_Corpus_Explorer_Autonomous_Build_Dispatch.md (grep-context only)
  - C:\highsierralabs\RHACO_Corpus_Explorer\PROMPT.md (grep + targeted reads lines 520-534, 560-579)
  - C:\highsierralabs\RHACO_Corpus_Explorer\DISPATCH_PARAMETERS.md (grep-context only)
commands_run:
  - (Get-Date).ToUniversalTime().ToString("o")  [PowerShell, start]
  - (Get-Date).ToUniversalTime().ToString("o")  [PowerShell, end]
  - ls -la /c/RHACO/
  - ls -la /c/highsierralabs/RHACO_Corpus_Explorer/
  - ls -la /c/RHACO/docs/ ; ls -la /c/RHACO/docs/reports/
  - ls -la /c/RHACO/working/eval/
  - ls -la /c/RHACO/rhaco/ | grep -i corpus_index ; ls -la /c/RHACO/tools/ | grep -i librarian
  - ls -la /c/RHACO/docs/reports/ | grep -E "20260712-001|20260628-001|20260712-002"
  - Grep tool: pattern 'search_hybrid_rerank|hybrid-rerank|Recall@10|flat hybrid|M4 default|search_graph|gold_queries_v1_2' over C:\RHACO\docs (files_with_matches, 42 hits)
  - ls -la /c/RHACO/docs/reports/ | grep -E "ANL-20260712-003|ANL-20260712-002|CHG-20260712-003"
  - ls -la /c/RHACO/docs/reports/ | grep -iE "20260716|20260715"
  - powershell -NoProfile -Command "Get-Item C:\RHACO | Select-Object LinkType,Target"
  - Grep tool: same pattern with content mode + context on RHACO-CHG-20260716-002, RHACO-CMP-20260903-001, RHACO-CCX-20260903-001, RHACO-HND-20260903-001, PROMPT.md, DISPATCH_PARAMETERS.md
  - ls -la reports/handoffs piped through awk/grep to date-filter Jul17-Sep filenames for retrieval-related titles
deviations: Two clarifications, no rule actually broken: (1) Rule 2 named a specific path list, but the task body explicitly instructs searching C:\RHACO\docs\** for later ANL/CHG/CMP evidence (section 6) and requires the M4 acceptance/closure story for section 1 -- this required reading three files outside the literal enumerated list (RHACO-ANL-20260712-002, RHACO-ANL-20260712-003, RHACO-CHG-20260712-003), all under the explicitly-authorized C:\RHACO\docs\ tree; I read only their .md bodies, not their .card.yaml companions, since those three were not in the mandatory "read in full" set. (2) `C:\RHACO` is a Windows directory junction to `C:\highsierralabs\RHACO` (verified: `Get-Item C:\RHACO` -> LinkType Junction, Target `C:\highsierralabs\RHACO`). Every read/search in this strand was issued against `C:\RHACO\...` paths as instructed; the Grep tool's raw output resolves and displays those same files under `C:\highsierralabs\RHACO\...` because that is the junction's physical target -- it is one on-disk location, not a second tree. Flagging this since rule 2 lists the two roots as if distinct. No RHACO_corpus_index.py / RHACO_tool_catalog_librarian.py content was read (not required by the task's 7 deliverables; permitted but unused). No Python was run, nothing was imported, no database was opened, nothing was created/edited/deleted, and only the two PowerShell timestamp commands were executed.

---

## 1. Accepted default retrieval path and its evidence

**Mode:** flat `hybrid` (FTS5 + nomic-embed-text, budget-packed contextual chunking, plain unweighted RRF k=60, identifier short-circuit) -- this is the live `search_corpus` default as of server v0.22.0.

**Recall@10 aggregate (gating number):** **0.700** on Gold v1.1 (40 rows) -- RHACO-ANL-20260712-001_M3_Gate_Evaluation_And_Disposition.md line 34 (six-configuration table, `hybrid` row: S1 1.000/S2 1.000/S3 0.500/S4 0.833/S5 0.375/**Agg 0.700**/MRR 0.382/NDCG 0.448); restated as the closure figure at RHACO-CMP-20260628-001_Corpus_RAG_Retrieval_Layer.md lines 102-106 ("hybrid Recall@10 0.700 vs fts5 0.200 on frozen Gold v1.1 (3.5x...)").

A second, non-gated report figure exists: **0.721** aggregate (S4 0.889) on Gold v1.2 (43 rows) -- RHACO-ANL-20260712-003_M4_Acceptance_And_Campaign_Closure_Evaluation.md lines 39-48 ("v1.2 results (reported -- the closure measurement)... hybrid | 0.700 | 0.721 | 0.889"). This number is explicitly non-gating: RHACO-CHG-20260712-003_M4_Gold_v1_2_Harness_v1_3_Eval_And_Certification.md line 78-79, gate item 6: "v1.2 recall/MRR/NDCG are REPORTED, not gated -- the closure measurement, no post-hoc target." The 0.700-on-Gold-v1.1 figure remains the standing accepted baseline/threshold.

**Date:** disposition 2026-07-12 (RHACO-ANL-20260712-001_...card.yaml line 4, `date: "2026-07-12"`); ratifying CHG design ratified 2026-07-12 PDT (RHACO-CHG-20260712-002_M4_Hybrid_Default_Flip.md line 4); campaign RHACO-CMP-20260628-001 CLOSED 2026-07-12 (RHACO-CMP-20260628-001_Corpus_RAG_Retrieval_Layer.md line 5, and §8 log line 96 "2026-07-12 | CLOSED | M4 CLOSED PASS per ANL-20260712-003").

**The ratifying CHG and what it flipped:** RHACO-CHG-20260712-002_M4_Hybrid_Default_Flip.md. §2.1 (lines 27-41): `search_corpus`'s `mode` parameter became nullable-sentinel (`mode: str | None = None`); resolution when omitted -- `doc_type_filter` or `path_glob` supplied -> resolves `'lexical'`; otherwise -> resolves `'hybrid'` ("the flip"). Server bumped v0.21.0 -> v0.22.0 (§2.2, lines 43-47). This is query-time dispatch only -- no index change, no re-embed, no chunking change (line 1, line 22-23). Terminal acceptance/activation is certified PASS in a separate, later document: RHACO-ANL-20260712-003_M4_Acceptance_And_Campaign_Closure_Evaluation.md lines 14-27: "M4: PASS... AC7 activation -- post-reinstall live round-trip 2026-07-12 ~19:58 UTC: server_info -> v0.22.0... default (no filters) -> engine=hybrid... the running default is hybrid." Campaign closure recommended and executed same document §6 / RHACO-CMP-20260628-001 §9 (lines 98-121).

## 2. hybrid-rerank disposition

**Score:** aggregate Recall@10 = **0.575** vs the required threshold >= 0.700 (RHACO-ANL-20260712-001.md line 16, Criterion-1 row of the verdict table).

**Verdict:** **FAIL -- Criterion 1** (line 12: "**FAIL -- Criterion 1.** Conjunctive gate; five of six criteria pass"). Recorded as a negative result: card abstract (RHACO-ANL-20260712-001_...card.yaml lines 34-39) "M3 CLOSED with the negative result recorded"; campaign closure statement (RHACO-CMP-20260628-001.md line 112) "Negative results recorded honestly: cross-encoder rerank FAILED recall on the RHACO canonicality task at best-in-table rank quality and unusable latency."

**"Documented-FAIL batch mode" language:** RHACO-ANL-20260712-001.md §5 item 4, line 61: "`hybrid-rerank` retained as a documented-FAIL batch mode -- pinned, deterministic, off the default path; available to future batch/offline experiments without re-provisioning." Echoed at RHACO-CHG-20260712-003.md line 49 ("`hybrid-rerank` is EXCLUDED: no decision rides on it (documented-FAIL stands on M3 evidence)").

**Per-query cost:** RHACO-ANL-20260712-001.md line 48: "~17,593 pairs / 40 queries ~= 440 pairs/query; at the measured 454 s per 128-pair batch (CPU, threads=1, fp32) ~= **26 min/query serial**."

**"Must never be on an interactive path":** same line 48: "Even on a PASS, `mode='hybrid-rerank'` was never an interactive MCP tool -- it is a batch instrument. The live-surface case for rerank was dead on latency alone; the gate result makes the point moot on the default path." Also §6 (line 67): "`mode='hybrid-rerank'` deliberately not probed live (§3 latency -- an interactive call is a self-inflicted timeout)."

## 3. graph disposition

**Score:** aggregate Recall@10 = **0.575** on Gold v1.1 (RHACO-ANL-20260712-001.md line 36, `graph` row: S1 1.000/S2 0.833/S3 0.333/S4 0.667/S5 0.250/Agg 0.575/MRR 0.366/NDCG 0.404); reported (not gated) as **0.581** on Gold v1.2 (RHACO-ANL-20260712-003.md line 42). Note S4 0.667 (v1.1) is *below* flat hybrid's 0.833 on the same stratum (RHACO-ANL-20260712-001.md line 50); on the traversal-true v1.2 S4 stratum, graph still does not beat hybrid (RHACO-ANL-20260712-003.md lines 50-56).

**"Auxiliary lineage mode" language:** RHACO-ANL-20260712-001.md §5 item 3, line 60: "`graph` retained as auxiliary lineage mode on the live surface (fast, edge-native); its measurement instrument is the M4 Gold v1.2 traversal stratum." Reaffirmed at RHACO-ANL-20260712-003.md line 55: "Graph remains auxiliary lineage mode per disposition ANL-20260712-001 §5.3; its retrieval value is the expansions, not the ranking."

## 4. Filter routing rule for search_corpus

Quoted verbatim from RHACO-CHG-20260712-002_M4_Hybrid_Default_Flip.md §2.1, lines 33-36:

> "`doc_type_filter` or `path_glob` supplied -> resolve **`'lexical'`** -- every existing filtered mode-less call is preserved byte-for-byte (**filters apply to lexical only**; a silent filter drop is the named blast-radius defect this rule closes)... otherwise -> resolve **`'hybrid'`** (the flip)."

## 5. Gold set structure

**Gold v1.1** (`C:\RHACO\working\eval\gold_queries.yaml`): **40 rows** total. Strata (yaml lines 12-27): S1 Exact-ID (8), S2 Title-fragment lexical (6), S3 Semantic paraphrase (12), S4 Lineage/graph mode (6), S5 Constants & analytical (8) = 40. Fields per row (e.g. lines 29-33, 105-111, 165-171): `id`, `stratum`, `query`, `targets` (list of one or more doc IDs), plus optional `resolve` (e.g. `supersession-head`, row 16 line 111) and optional `mode` (e.g. `graph`, row 27 line 171). Scoring block (lines 9-11): `metric: recall@10`, `hit_rule: any-target-in-top-10`. A hit is therefore defined as: any one of a row's listed target document IDs appearing within that query's top-10 ranked retrieval results.

**Gold v1.2** (`C:\RHACO\working\eval\gold_queries_v1_2.yaml`): **43 rows**. Strata (yaml lines 12-27): S1 (8), S2 (6), S3 (12), **S4 (9)**, S5 (8) = 43 -- one more S4 row than v1.1 net of the row-29 re-encode plus rows 41-43 new (confirmed also at RHACO-ANL-20260712-002_...md line 28: "Strata: S1 8 / S2 6 / S3 12 / S4 9 / S5 8 = 43 rows"). New field: `targets_mode: subtree` (rows 29, 41), with a distinct hit rule -- "hit iff >= 3 distinct frozen members (root included) appear in top-10 (`SUBTREE_HIT_MIN = 3`, harness v1.3)" (RHACO-ANL-20260712-002.md lines 35-37; mechanics also at RHACO-CHG-20260712-003.md lines 43-46). **Baseline status:** Gold v1.2 metrics are explicitly *reported, not gated* -- RHACO-CHG-20260712-003.md line 78-79: "v1.2 recall/MRR/NDCG are REPORTED, not gated -- the closure measurement, no post-hoc target." It supersedes v1.1 as the instrument going forward for reporting purposes (RHACO-ANL-20260712-002.md lines 60-63: "closure headline, traversal-stratum, and systematic-free numbers anchor v1.2; all future work anchors v1.2") but Gold v1.1's 0.700 remains the pass/fail-defining figure ratified into the flip. This is also how the build's own dispatch record frames it -- `C:\highsierralabs\RHACO_Corpus_Explorer\DISPATCH_PARAMETERS.md` lines 43-45: "Gold v1.2 (`gold_queries_v1_2.yaml`) is available but has no accepted baseline of record; it may be profiled, never gated."

## 6. Evidence superseding the above (post-2026-07-12 search)

Searched `C:\RHACO\docs\**` (Grep, pattern `search_hybrid_rerank|hybrid-rerank|Recall@10|flat hybrid|M4 default|search_graph|gold_queries_v1_2`), 42 files matched. Findings:

- **RHACO-ANL-20260712-002** (Gold v1.2 Freeze), **RHACO-CHG-20260712-003** (M4 Gold v1.2 + Harness v1.3 Eval and Certification), and **RHACO-ANL-20260712-003** (M4 Acceptance and Campaign Closure Evaluation) -- all dated 2026-07-12, chronologically *after* CHG-20260712-002 in the campaign log sequence (RHACO-CMP-20260628-001.md §8, lines 92-96). These do not change the default mode; they **certify** the flip (ANL-20260712-003.md line 16: "M4: PASS... campaign closure is recommended") and close the campaign. Already folded into sections 1 and 5 above.
- **RHACO-CHG-20260716-002** (M5 Closeout -- Style Guide v1.9 and Campaign Close, 2026-07-15/16, a *different* campaign/milestone) references the standing state only as a gating precondition in passing: "Gate satisfied: M4 closed, server stable at v0.22.0, hybrid retrieval live (Recall@10 ~= 0.72)." (line 17). No re-evaluation, no change.
- No further ANL/CHG/CMP dated 2026-07-17 through 2026-09-02 addresses corpus retrieval mode, hybrid-rerank, or graph search in this sense. The only other "M4"/"gold" hits in that window (e.g. RHACO-ANL-20260802-001, RHACO-CHG-20260802-007, RHACO-ANL-20260801-001 "Narrator Golden Set") belong to the unrelated sibling campaign RHACO-CMP-20260628-002 (Automated Observatory Digest & Event Triage, narration work) and its own distinct "Narrator Golden Set" evaluation instrument -- not the corpus-RAG gold set.
- The build's own 2026-09-03 dispatch materials -- RHACO-CMP-20260903-001, RHACO-CCX-20260903-001, RHACO-HND-20260903-001 (`C:\RHACO\docs\...`), and this workspace's `PROMPT.md` / `DISPATCH_PARAMETERS.md` -- independently cite the identical standing disposition (flat hybrid default / 0.700 on Gold v1.1 gated / hybrid-rerank FAIL documented-FAIL batch mode / graph auxiliary / Gold v1.2 profile-only). `PROMPT.md` lines 526-532 states its own expectation and escape hatch: "Expected standing state at prompt authorship: flat hybrid accepted... graph retained as auxiliary lineage mode; hybrid-rerank recorded as a negative result... **If repository state has changed since this prompt was authored, the current ratified evidence supersedes this expectation.**"

**Conclusion for section 6:** no evidence found that the standing retrieval disposition has moved since the build prompt was authored; the state described in sections 1-5 above is current as of this inspection.

## 7. UNVERIFIED

- `RHACO_corpus_index.py` and `RHACO_tool_catalog_librarian.py` source were not opened; all mode-resolution and dispatch mechanics above are taken from the CHG/ANL prose, not cross-checked against source code.
- `RHACO-ANL-20260712-002.card.yaml`, `RHACO-ANL-20260712-003.card.yaml`, and `RHACO-CHG-20260712-003.card.yaml` were not read (only the `.md` bodies) -- exact `date`/`status` identity fields for those three documents are taken from in-body text ("2026-07-12" appears in each `.md`), not confirmed against their card headers.
- The full 42-file grep match list was not individually opened; files not already covered by the mandatory reading list or by the section-6 date/topic filtering above were triaged by filename/date only, not read in full. I judge this sufficient given the literal search patterns specified in the task, but flag it as a boundary of this inspection.
- No broader free-text sweep of `RHACO_Software_Behavioral_Reference.md` or other non-report reference docs was performed; the task scoped the search to the seven literal patterns, which I honored exactly.
