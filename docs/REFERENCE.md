# docs/REFERENCE.md -- standing retrieval dispositions of record

Written at build start (PROMPT.md section 6; RHACO-HND-20260903-001 section 2 D seed) from the round-0 inspection strand I3 (`docs/rounds/R00_I3_retrieval_dispositions.report.md`) and strand I1 (`docs/rounds/R00_I1_corpus_index_contracts.report.md`), 2026-09-04. Every figure below is a RHACO campaign result; the explorer preserves these dispositions and re-evaluates none of them.

## 1. State of record (as of 2026-09-04; no superseding evidence found)

| Configuration | Module function | Disposition | Evidence |
|---|---|---|---|
| **Flat hybrid** (FTS5 + nomic-embed-text budget-packed chunks, RRF k=60, identifier short-circuit) | `search_hybrid(query, model_tag=CPU_FLOOR_TAG, top_k=10, db_path=DEFAULT_DB)` | **ACCEPTED -- the operational default** (live `search_corpus` default since server v0.22.0) | RHACO-ANL-20260712-001 line 34: Recall@10 **0.700** aggregate on Gold v1.1 (40 rows; S1 1.000 / S2 1.000 / S3 0.500 / S4 0.833 / S5 0.375; MRR 0.382; NDCG 0.448). Default flipped by RHACO-CHG-20260712-002 section 2.1 (mode `None` resolves to `hybrid` unless a filter is supplied); activation certified PASS by RHACO-ANL-20260712-003 lines 14-27; campaign RHACO-CMP-20260628-001 CLOSED 2026-07-12 |
| **Hybrid-rerank** (cross-encoder `bge-reranker-v2-m3`, depth 100, CPU fp32 single-thread) | `search_hybrid_rerank(query, model_tag, top_k=10, depth=RERANK_DEPTH, db_path)` | **NEGATIVE RESULT -- FAIL, documented-FAIL batch mode; never on an interactive path** | RHACO-ANL-20260712-001 line 16: Recall@10 **0.575** vs threshold >= 0.700 (Criterion 1 FAIL); line 48: ~440 pairs/query at 454 s per 128-pair batch = **~26 min/query serial**; "never an interactive MCP tool -- it is a batch instrument"; section 5 item 4 line 61: "retained as a documented-FAIL batch mode -- pinned, deterministic, off the default path" |
| **Graph** (identifier short-circuit + top-5 hybrid seeds, one-hop typed-edge expansion) | `search_graph(query, top_k=10, model_tag, db_path)` | **AUXILIARY lineage mode** (retained on the live surface; not a ranking improvement) | RHACO-ANL-20260712-001 line 36: Recall@10 **0.575** on Gold v1.1 (S4 0.667, below flat hybrid's 0.833); section 5 item 3 line 60: "retained as auxiliary lineage mode ... fast, edge-native"; RHACO-ANL-20260712-003 line 55: "its retrieval value is the expansions, not the ranking" |
| **Lexical / FTS5** (exact substring hit-set, bm25 order) | `search_fts(query, doc_type_filter=None, path_glob=None, context_lines=2, max_results=100, db_path)` | Available; **the only channel that accepts filters** | RHACO-ANL-20260712-001 line 34: fts5 0.200 aggregate (the hybrid comparison baseline); RHACO-CHG-20260712-002 section 2.1 lines 33-36: "`doc_type_filter` or `path_glob` supplied -> resolve `'lexical'` ... **filters apply to lexical only**" |
| **Identifier / direct** | `resolve_identifier(query, db_path)` | Available; pure exact alias lookup, returns every matching doc_id sorted | RHACO_corpus_index.py lines 1285-1311 (I1 section 8) |

**Reported, not gated:** on Gold v1.2 (43 rows) hybrid reports 0.721 aggregate (S4 0.889) and graph 0.581 -- RHACO-ANL-20260712-003 lines 39-48; RHACO-CHG-20260712-003 lines 78-79: "v1.2 recall/MRR/NDCG are REPORTED, not gated". Gold v1.1's 0.700 remains the pass/fail-defining figure (DISPATCH_PARAMETERS.md item E).

## 2. Consequences binding this build

1. **Default search mode = flat hybrid.** The search surface's default is `search_hybrid`; the active mode is always displayed (PROMPT.md 5.2).
2. **Hybrid-rerank is not offered interactively.** It stays off every UI path. Diagnostics may *report* its standing (documented-FAIL batch mode, ~26 min/query) and whether the pinned reranker artifact is present, but the explorer never invokes `search_hybrid_rerank`. Listed in `SCOPE.md` as a deliberate V1 exclusion with this evidence.
3. **Graph is the lineage/auxiliary mode**, labelled as such; its expansions are typed edges from the `edges` table, never inferred.
4. **Filters apply to lexical only.** No module search function other than `search_fts` accepts any filter (I1 section 7: `search_hybrid`, `search_hybrid_rerank`, `search_graph` carry only `query, model_tag, top_k[, depth], db_path`; `search_fts` accepts `doc_type_filter` and `path_glob` only). Any facet narrowing of hybrid or graph results in the UI is a **post-hoc narrowing of returned doc_ids by card metadata**, must be labelled as such, and must never be presented as retrieval-side filtering. Status / lifecycle_state / program / tag filters are catalog-side (parameterized read-only SQL over `cards`, `card_programs`, `card_tags`), not retrieval-side.
5. **Degradation is per channel, no raise** (I1 section 6): with `RHACO_CORPUS_DISABLE_VEC=1` (or sqlite-vec / Ollama unavailable) `search_hybrid` returns identifier short-circuit + FTS5 ordering only, and `search_graph`'s seed channel degrades identically. The UI must relabel the mode ("Hybrid unavailable: using lexical retrieval ...") whenever the vector channel is unavailable (PROMPT.md 5.2; W7).
6. **Component evidence is not exposed.** `search_hybrid` returns doc_ids only; per-channel FTS / vector ranks and RRF scores are internal. The result evidence panel shows `Component rank: not exposed by current RHACO retrieval API` for hybrid results (PROMPT.md 5.3). Lexical results do carry `line_no`, `line`, `context_before`, `context_after` (I1 section 4, `search_fts` return shape).

## 3. Gold sets

| Set | Path | Rows | Strata | Scoring | Status |
|---|---|---|---|---|---|
| Gold v1.1 | `C:\RHACO\working\eval\gold_queries.yaml` (sha256 `f20bc6a27885088803541cb568589a9b4d8a5883e615ee492b01eed5624bc16c`, 5,381 B) | 40 | S1 Exact-ID 8 / S2 Title-fragment lexical 6 / S3 Semantic paraphrase 12 / S4 Lineage-graph 6 / S5 Constants-analytical 8 | `metric: recall@10`, `hit_rule: any-target-in-top-10`; rows carry `id, stratum, query, targets[, resolve][, mode]` | **Gate set** for the compatibility check (DISPATCH_PARAMETERS.md item E): adapter hybrid Recall@10 >= 0.700 aggregate, computed by the build's L4 oracle from module-returned doc ids |
| Gold v1.2 | `C:\RHACO\working\eval\gold_queries_v1_2.yaml` (sha256 `d456f9816dbca1bc3522c94a34d81bf382608e2c73a50690cd2e13b952a58256`, 6,727 B) | 43 | S1 8 / S2 6 / S3 12 / S4 9 / S5 8 | adds `targets_mode: subtree` rows (hit iff >= 3 distinct frozen members in top-10, `SUBTREE_HIT_MIN = 3`, harness v1.3) | **Profile only, never gated** (no accepted baseline of record) |

The gold source of record for v1.1 is RHACO-ANL-20260711-001 (freeze pin `GOLD_SOURCE_SHA256` in the module, I1 section 2); `emit_gold_queries` regenerates the YAML from it and is one of the five index-writing names the build never calls.

## 4. Superseding-evidence search (PROMPT.md section 6 escape hatch)

Strand I3 searched `C:\RHACO\docs\**` for `search_hybrid_rerank | hybrid-rerank | Recall@10 | "flat hybrid" | "M4 default" | search_graph | gold_queries_v1_2` (42 files). Every post-2026-07-12 hit either certifies the flip (ANL-20260712-002/-003, CHG-20260712-003), cites the standing state in passing (CHG-20260716-002 line 17: "hybrid retrieval live (Recall@10 ~= 0.72)"), belongs to the unrelated narrator campaign (CMP-20260628-002 "Narrator Golden Set"), or is this build's own dispatch material. **No change to the retrieval default, the rerank verdict, or the graph disposition was found.** Boundary of the search: the seven literal patterns; the 42 matches were triaged by date and title, not all read in full (I3 section 7).

## 5. Module facts the search surface depends on (from I1)

- `search_hybrid` order: identifier short-circuit hits first (all aliases matched, sorted), then RRF fusion of the FTS5 doc ranking and the vector doc ranking (`RRF_K = 60`); `top_k` default 10; `MAX_SEARCH_RESULTS = 200` bounds `search_fts`.
- `search_fts`: the authoritative hit-set is an exact substring scan (smart-case) of every stored body; FTS5 `bm25('porter unicode61')` supplies order only; a literal query never raises an FTS5 syntax error; returns `{"matches": [...], "total_matched", "returned", "truncated"}`.
- Vector channel: `MODEL_REGISTRY` tags `nomic-embed-text` (CPU floor, dim 768), `bge-m3`, `qwen3-embedding-0.6b`; `OLLAMA_HOST` default `http://127.0.0.1:11434`, `OLLAMA_TIMEOUT_S = 300`; query embedding CPU-forced for determinism.
- Rerank: `RERANK_MODEL_DIR = C:\RHACO\models\bge-reranker-v2-m3`, sha256-pinned (`RERANK_MODEL_PIN`); `RerankModelPinMismatch` is a HALT that propagates; `RerankUnavailable` degrades to plain hybrid. The explorer never reaches either path (consequence 2).
