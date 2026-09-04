# R00_I1_corpus_index_contracts -- strand report (round 0 inspection)

strand_id: I1
agent_id: a90ad98060d049c2c
workflow_run: wf_c2507f3a-9da
model_id: You are powered by the model named Sonnet 5. The exact model ID is claude-sonnet-5.
t_start_utc: 2026-09-04T02:33:57.1668619Z
t_end_utc: 2026-09-04T02:34:23.4015391Z
transcript_last_write_utc: 2026-09-04T02:39:15+00:00
files_read:
  - C:\RHACO\rhaco\RHACO_corpus_index.py (full file, lines 1-2377, read in two passes: 1-1200 and 1200-2377)
commands_run:
  - PowerShell: (Get-Date).ToUniversalTime().ToString("o")  [start, 2026-09-04T02:33:57Z]
  - Bash: ls -la "C:\RHACO\rhaco\RHACO_corpus_index.py" 2>&1; echo "---"; wc -l "C:\RHACO\rhaco\RHACO_corpus_index.py" 2>&1
  - Grep pattern ^[A-Za-z_][A-Za-z0-9_]*\s*=\s* over C:\RHACO\rhaco\RHACO_corpus_index.py (module-level assignment sweep)
  - Grep pattern ^(def |class |    def ) over C:\RHACO\rhaco\RHACO_corpus_index.py (complete def/class inventory)
  - PowerShell: (Get-Date).ToUniversalTime().ToString("o")  [end, 2026-09-04T02:34:23Z]
deviations: None. All reads stayed inside C:\RHACO\rhaco\RHACO_corpus_index.py (the sole file this task, I1, was scoped to). No Python was run, no module was imported, no database file was opened; only Read/Grep/Bash(ls,wc)/PowerShell(Get-Date) were used. The file was 118,123 bytes / 2377 lines exactly as the dispatch stated, confirmed via `ls -la` and `wc -l` before reading. One scope note (not a rule violation, listed under UNVERIFIED in the report body): several functions in this file lazily import and call into RHACO_tool_catalog_librarian.py, but task I1 itself only requested inspection of RHACO_corpus_index.py, so that librarian module's internals were not read for this report.

---

## 1. Module header

**Purpose statement** — docstring lines 1-231 (`"""..."""`); PURPOSE block is lines 7-24:

> `PURPOSE:   Derived SQLite index over the cards-as-database corpus (the .card.yaml companions the catalog librarian already parses) PLUS the full-text body index over the document tree.` (l.7-9)
> `- Metadata tables (cards / card_programs / card_tags): one row per card, CARD-driven from the librarian walk (query_catalog parity).` (l.11-12)
> `- fts_docs (FTS5 body index): WALK-driven over the SAME document scope search_corpus uses (CHG-20260628-003 Amendment A1)...` (l.13-16)
> `- edges (relationship graph): populated at M3 (emit_edges) with the typed relations cites / supersedes / amends / campaign_child.` (l.17-18)
> `The index is DERIVED, REBUILDABLE, and NON-AUTHORITATIVE (CMP-20260624-001 §7): the librarian walk is always the authority. The index accelerates query; it never holds record and is never read into any correctness verdict. Deleting the .db and re-running the librarian reproduces an identical index.` (l.20-24)

USAGE block, l.26-36 (import name, `reindex_full`, `search_fts`, `search_hybrid`, `resolve_identifier`, `freshness_check`, and 5 CLI invocation forms `--stats/--rebuild/--freshness/--reindex-vec/--emit-gold`). OUTPUT line 38-39: `C:\RHACO\index\corpus_index.db (single SQLite file, OUTSIDE the librarian walk root C:\RHACO\docs\ — never a corpus member).`

**VERSION HISTORY** (l.41-230), 6 entries, each with a one-line date/id header:
- `v1.0  2026-06-28  Initial build (RHACO-CMP-20260624-001 M1, RHACO-HND-20260628-002).` (l.42-43) — schema cut once; API `connect, reindex_full, reindex_pair, freshness_check`; `INDEX_SCHEMA_VERSION = 1`.
- `v1.1  2026-06-28  M2 FTS5 body index + search (...CHG-20260628-003 + Amendment A1, Option 1 walk-driven).` (l.51-52) — fts_docs (doc_id, path, body) schema, WALK-driven population, `search_fts()` behavior, `reindex_fts_pair(doc_path)`, "Finding 2: PRAGMA auto_vacuum=INCREMENTAL ... + incremental_vacuum after each full reindex."
- `v1.2  2026-06-28  M3 relationship graph (...CHG-20260628-004).` (l.71-72) — `emit_edges()` populates edges inside the reindex_full transaction; four typed relations described; "The librarian is UNCHANGED (stays v1.13)."
- `v1.3  2026-07-10  M1 vector substrate (...CHG-20260710-003, ...HND-20260710-002).` (l.98-99) — sqlite-vec vec0 tables, local Ollama pipeline, per-model_tag tables, `embed_texts`, chunking, `reindex_vec`, typed `VecUnavailable` degradation, `emit_gold_queries()`.
- `v1.4  2026-07-11  M2 hybrid retrieval (...CHG-20260711-002, ...HND-20260711-002).` (l.142-143) — id_aliases table, structure-aware budget-packed chunking, `search_hybrid(...)`, emit_gold_queries retarget to gold_set_version 1.1.
- `v1.5  2026-07-11  M3 rerank + graph retrieval (...CHG-20260711-006, ...HND-20260711-003).` (l.187-188) — `search_hybrid_rerank`, `search_graph`, model pin check, CLI `--rerank`/`--graph`.

## 2. Constants block (module level)

All values quoted exactly, with defining line(s):

| Constant | Line | Value |
|---|---|---|
| `INDEX_SCHEMA_VERSION` | 251 | `1` |
| `_NULL_LOG` | 256-258 | `logging.getLogger("rhaco_corpus_index_edges")`, `NullHandler` added, `propagate=False` |
| `_INDEX_DIR` | 264 | `os.path.join(r"C:\RHACO", "index")` → `C:\RHACO\index` |
| `DEFAULT_DB` | 265 | `os.path.join(_INDEX_DIR, "corpus_index.db")` → `C:\RHACO\index\corpus_index.db` |
| `BODY_SCAN_ROOT` | 272 | `os.path.join(r"C:\RHACO", "docs")` → `C:\RHACO\docs` |
| `BODY_DENY_DIRS` | 273-276 | `frozenset({".git","__pycache__","deprecated","docs_archive","drafts","logs","templates","_staging"})` |
| `BODY_SUFFIXES` | 277 | `(".md", ".txt")` |
| `BODY_MAX_LINE` | 278 | `1000` |
| `MAX_SEARCH_CONTEXT` | 279 | `5` |
| `MAX_SEARCH_RESULTS` | 280 | `200` |
| `_CANONICAL_FILENAME_RE` | 285-286 | `r"^RHACO-([A-Z]+)-(\d{8})-(\d+)(?:_[^.]*)?\.(md|docx|pdf|ipynb)$"` (IGNORECASE) |
| `_ALIAS_CANONICAL_RE` | 292 | `r"^RHACO-([A-Z]+)-(\d{8})-(\d+)$"` |
| `_EVENT_ID_RE` | 293 | `r"(?<![0-9A-Za-z])E\d{6}(?![0-9A-Za-z])"` |
| `_RESOLVE_FULL_RE` | 294 | `r"^RHACO-[A-Z]+-\d{8}-\d+$"` |
| `_RESOLVE_BARE_RE` | 295 | `r"^[A-Z]+-\d{8}-\d+$"` |
| `_RESOLVE_EVENT_RE` | 296 | `r"^E\d{6}$"` |
| `RRF_K` | 301 | `60` |
| `_CARDS_COLUMNS` | 305-311 | 21-item tuple: `yaml_path, doc_id, doc_type, date, seq, title, status, project_knowledge, current_version, schema_version, naming_convention_version, lifecycle_state, last_human_review, reviewer, doc_filename, doc_path, local_path, abstract, card_sha256, card_mtime_utc, indexed_at_utc` |
| `VEC_DISABLE_ENV` | 327 | `"RHACO_CORPUS_DISABLE_VEC"` |
| `OLLAMA_HOST` | 330 | `os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")` (default `http://127.0.0.1:11434`) |
| `OLLAMA_EMBED_PATH` | 331 | `"/api/embed"` |
| `OLLAMA_TIMEOUT_S` | 332 | `300` |
| `_QWEN_QUERY_INSTRUCT` | 336-338 | `"Instruct: Given a search query, retrieve relevant RHACO observatory documents that answer it\nQuery: "` |
| `MODEL_REGISTRY` | 345-374 | dict of 3 tags: `nomic-embed-text` (ollama=`nomic-embed-text`, dim=768, prefix_query=`"search_query: "`, prefix_document=`"search_document: "`, ctx_tokens=8192, options=`{"num_gpu":0}`); `bge-m3` (ollama=`bge-m3`, dim=1024, prefixes `""`/`""`, ctx=8192, options=`{}`); `qwen3-embedding-0.6b` (ollama=`qwen3-embedding:0.6b`, dim=1024, prefix_query=`_QWEN_QUERY_INSTRUCT`, prefix_document=`""`, ctx=32768, options=`{}`) |
| `MODEL_TAGS` | 375 | `tuple(MODEL_REGISTRY)` → `("nomic-embed-text", "bge-m3", "qwen3-embedding-0.6b")` |
| `CPU_FLOOR_TAG` | 376 | `"nomic-embed-text"` |
| `EMBED_ROLES` | 377 | `("query", "document")` |
| `CHUNK_TOKEN_BUDGET` | 383 | `6000` |
| `_CHARS_PER_TOKEN` | 384 | `4` |
| `CHUNK_CHAR_BUDGET` | 385 | `CHUNK_TOKEN_BUDGET * _CHARS_PER_TOKEN` = `24000` |
| `_HEADER_SPLIT_RE` | 386 | `r"(?m)^#{1,6}[ \t]"` |
| `RERANK_DISABLE_ENV` | 394 | `"RHACO_CORPUS_DISABLE_RERANK"` |
| `RERANK_MODEL_DIR` | 395 | `os.path.join(r"C:\RHACO", "models", "bge-reranker-v2-m3")` → `C:\RHACO\models\bge-reranker-v2-m3` |
| `RERANK_SAFETENSORS` | 396 | `"model.safetensors"` |
| `RERANK_MODEL_PIN` | 399 | `"d9e3e081faff1eefb84019509b2f5558fd74c1a05a2c7db22f74174fcedb5286"` |
| `RERANK_DEPTH` | 400 | `100` |
| `_METADATA_DDL` | 438-505 | (SQL text, see §5) |
| `_FTS_DDL` | 509-516 | (SQL text, see §5) |
| `SCHEMA_DDL` | 518 | `_METADATA_DDL + _FTS_DDL` |
| `_TOKEN_RE` | 1163 | `re.compile(r"\w+", re.UNICODE)` |
| `_RERANKER` | 1419 | `None` (module-cached FlagReranker, lazy) |
| `_GRAPH_REL_PRIORITY` | 1556 | `{"supersedes": 0, "amends": 1, "campaign_child": 2, "cites": 3}` |
| `_SECTION_HEADER_RE` | 1734 | `r"(?m)^(#{1,3})[ \t]+(.+?)[ \t]*$"` |
| `GOLD_SOURCE_SHA256` | 2035 | `"f4d88993fef8ff6af930f79f8bca44351823c934ac11230607a33bd4c56efdc1"` |
| `GOLD_ANL_PATH` | 2036-2038 | `os.path.join(BODY_SCAN_ROOT, "reports", "RHACO-ANL-20260711-001_Corpus_RAG_Gold_Query_Set_v1_1_Freeze.md")` → `C:\RHACO\docs\reports\RHACO-ANL-20260711-001_Corpus_RAG_Gold_Query_Set_v1_1_Freeze.md` |
| `_EVAL_DIR` | 2039 | `os.path.join(r"C:\RHACO", "working", "eval")` → `C:\RHACO\working\eval` |
| `GOLD_QUERIES_PATH` | 2040 | `os.path.join(_EVAL_DIR, "gold_queries.yaml")` → `C:\RHACO\working\eval\gold_queries.yaml` |
| `_GOLD_STRATA` | 2042-2048 | `(("S1","Exact-ID",8),("S2","Title-fragment lexical",6),("S3","Semantic paraphrase",12),("S4","Lineage / graph mode",6),("S5","Constants & analytical",8))` |
| `_GOLD_QUERY_ROWS` | 2050-2139 | list of 40 dicts (`id, stratum, query, targets[, resolve][, mode]`) — the frozen gold query set, ids 1-40 |

A module-level `import` block precedes these at l.235-247 (`argparse, datetime as dt, fnmatch, hashlib, logging, math, os, re, sqlite3, struct, sys, time`, plus `from dataclasses import dataclass, field`); `from __future__ import annotations` at l.233.

## 3. Classes

Confirmed by full-file grep (`^(def |class |    def )`) — exactly 4 exception classes + 2 dataclasses; no other classes exist.

- **`VecUnavailable(RuntimeError)`** — l.403. First docstring line (l.404): `"Raised by a vector code path when the substrate is unavailable -- the"` (continues: sqlite-vec extension failed/declined to load, or `VEC_DISABLE_ENV`, or Ollama unreachable; typed/catchable; "connect() and every v1.2 path never raise it," l.405-408).
- **`GoldPinMismatch(RuntimeError)`** — l.411. First docstring line (l.412): `"Raised by emit_gold_queries when the RHACO-ANL-20260710-001 freeze pin no"` (continues: "longer matches the on-disk source -- the frozen gold set drifted (HALT, CHG 2.6).", l.413-414).
- **`RerankUnavailable(RuntimeError)`** — l.417. First docstring line (l.418): `"Degradation (M3, CHG-20260711-006 §2.1a): the reranker artifact is absent,"` (continues through l.422: runtime import failure or `RHACO_CORPUS_DISABLE_RERANK`; "search_hybrid_rerank catches this and returns the plain search_hybrid result -- an AVAILABILITY failure (charter 3.3)").
- **`RerankModelPinMismatch(RuntimeError)`** — l.425. First docstring line (l.426): `"HALT (M3, CHG-20260711-006 §2.1a): the reranker artifact is PRESENT but its"` (continues through l.430: sha256 != `RERANK_MODEL_PIN` → tampered/wrong model; "deliberately NOT swallowed by the degradation path ... propagates through the MCP server surface too").

Dataclasses (return rows):
- **`ReindexReport`** (`@dataclass`, l.523-534, no base class shown / implicit `object`, no docstring). Fields: `cards_written:int, programs_written:int, tags_written:int, fts_docs_written:int, edges_written:int, aliases_written:int, corpus_cards_sha:str, corpus_card_count:int, elapsed_s:float, db_path:str`.
- **`FreshnessReport`** (`@dataclass`, l.537-550, no docstring). Fields: `fresh:bool, corpus_card_count_live:int, corpus_card_count_index:int, corpus_cards_sha_live:str, corpus_cards_sha_index:str, added:list=field(default_factory=list), removed:list=field(default_factory=list), sha_changed:list=field(default_factory=list)`; plus a `@property status(self) -> str` (l.548-550): `return "FRESH" if self.fresh else "DRIFT"`.

## 4. Public functions (no leading underscore)

Complete inventory (19 total), confirmed against the full `def`/`class` grep — every non-underscore top-level `def` is listed; all are covered below.

**`doc_id_from_filename(name: str) -> str`** — l.626. Docstring (l.627-628): "canonical_id parsed from the filename, else the filename stem. Equals the server's _doc_id_for(path)..." Returns a `str` doc_id. Pure regex/string function — no DB, no filesystem, no Ollama, no env.

**`iter_body_docs(root: str | None = None)`** — l.652, generator. Docstring l.653-657: yields `(path, doc_id, body)` for every in-scope document body, same walk `search_corpus` uses; `root` defaults to `BODY_SCAN_ROOT` read at call time. Reads filesystem (`os.walk` + file opens under `BODY_SCAN_ROOT`/`root`); no DB, no Ollama, no env switch.

**`connect(db_path: str = DEFAULT_DB) -> sqlite3.Connection`** — l.779. Docstring l.780-782: "Open (creating the parent dir + file if absent), enable FK enforcement, set incremental auto-vacuum on a fresh DB (Finding 2), and apply the full DDL idempotently." Writes the DB file (creates dir/file, `PRAGMA foreign_keys=ON`, `PRAGMA auto_vacuum=INCREMENTAL` if fresh, executes `SCHEMA_DDL`, `_ensure_fts_schema`); calls `_load_sqlite_vec(conn)` (l.799) which honors `VEC_DISABLE_ENV`. No Ollama call, no non-DB filesystem read.

**`get_meta(conn: sqlite3.Connection, key: str)`** — l.812. No docstring. Returns the `value` column for `key` in `index_meta`, or `None`. DB read only.

**`reindex_full(scan, db_path=DEFAULT_DB, librarian_version=None, nc_version=None, analytics=None) -> ReindexReport`** — l.820-821. Docstring l.822-837 (quoted in module header notes above). Returns `ReindexReport`. Writes DB (single transaction: truncate+rebuild `cards/card_programs/card_tags/fts_docs`, `INSERT INTO fts_docs(fts_docs) VALUES('optimize')`, `emit_edges`, truncate+rebuild `id_aliases`, `_set_meta` writes, then `PRAGMA incremental_vacuum`). Reads filesystem (`iter_body_docs` body walk; `_sha256_file`/`_mtime_utc` per card). Calls `emit_edges`, which lazily imports `RHACO_tool_catalog_librarian`. No Ollama call. `scan` is duck-typed — only `scan.cards` is consumed (l.833-834).

**`emit_edges(conn: sqlite3.Connection, scan, index=None) -> int`** — l.934. Docstring l.935-963 lists the four relations verbatim: `cites` ("every depends_on/see_also ref ... resolved=0 IFF the ref would be an unresolved_reference finding", l.937-943), `supersedes` ("superseded_by mapping, emitted only when it resolves to a DISTINCT target", l.944-947), `amends` ("amendment child ... -> parent. from_id is the amendment's DISTINCT filename stem", l.948-955), `campaign_child` ("depends_on -> a CMP that resolves (ratified DECISION-1)", l.956-959). Returns row-count `int`. Writes `edges` table (`DELETE` + `executemany INSERT`, l.1029-1032). Lazily `import RHACO_tool_catalog_librarian as _lib` (l.964) and calls `_lib._build_id_index`, `_lib._resolve_reference`, `_lib.EXTERNAL_REFS`, `_lib.is_amendment_of` — those symbols were not verified against the librarian source (out of this task's scope; see §10). Malformed cards are swallowed by a bare `except Exception: continue` (l.1026-1027) — "non-authoritative; never break a census". No Ollama.

**`reindex_pair(doc_id_or_yaml_path: str, db_path: str = DEFAULT_DB) -> dict`** — l.1040. Docstring l.1041-1046: "Upsert a single card ... from disk, then refresh the index_meta rollup ... Does NOT touch fts_docs (see reindex_fts_pair)." Returns `{"yaml_path", "doc_id", "programs_written", "tags_written"}`. Writes DB (delete+insert one card's rows in `cards/card_programs/card_tags`, refresh `corpus_card_count`/`corpus_cards_sha` meta). Reads filesystem via `_load_card` (opens/parses `.card.yaml`) and `_card_row`'s `_sha256_file`/`_mtime_utc`. Raises `ValueError` if the argument resolves to neither a `.card.yaml` path nor a unique indexed `doc_id` (l.1050-1053).

**`reindex_fts_pair(doc_path: str, db_path: str = DEFAULT_DB) -> dict`** — l.1134. Docstring l.1135-1138: "Refresh the fts_docs row for ONE document body by path ... Fired by the canonical document write tools after their atomic write (write_document_canonical / promote_staged Shape P)." Returns `{"path", "indexed", "in_scope"}`. Writes DB (delete + conditional insert of one `fts_docs` row, refresh `fts_docs_count` meta). Reads filesystem (opens `doc_path` if `_in_body_scope` and file exists).

**`search_fts(query: str, doc_type_filter=None, path_glob=None, context_lines: int = 2, max_results: int = 100, db_path: str = DEFAULT_DB) -> dict`** — l.1189-1191. Docstring l.1192-1204: authoritative hit-set is an exact substring scan (smart-case) of every stored body — "byte-for-byte parity with the python-walk baseline, INCLUDING mid-word substrings ... and .txt bodies"; FTS5 MATCH + `bm25('porter unicode61')` supplies ORDER only; "A literal query NEVER raises a 'fts5: syntax error'". Returns `{"matches": [{"path","doc_id","line_no","line","context_before","context_after"}], "total_matched", "returned", "truncated"}`. Raises `ValueError` on empty query (l.1205-1206). DB read only (`fts_docs` MATCH + full scan of `doc_id, path, body`). No filesystem read outside the DB, no Ollama, no env switch honored directly.

**`resolve_identifier(query: str, db_path: str = DEFAULT_DB) -> list`** — l.1306. Docstring l.1307-1309: "Resolve an identifier-form query to matching doc_ids (sorted ascending); [] for a prose / non-identifier query ... Pure lexical lookup against id_aliases -- no classification, no LLM." Returns `list[str]` doc_ids or `[]`. DB read only (`id_aliases`).

**`search_hybrid(query: str, model_tag: str = CPU_FLOOR_TAG, top_k: int = 10, db_path: str = DEFAULT_DB) -> list`** — l.1387-1388. Docstring l.1389-1398 (see §6). Returns up to `top_k` doc_ids. DB read (`fts_docs` via `search_fts`; vec table via `_vec_doc_ranking`). Calls Ollama via `embed_query_cpu` inside `_vec_doc_ranking` (l.1362) unless `VecUnavailable` is raised first. Honors `VEC_DISABLE_ENV` indirectly (via `_load_sqlite_vec`/`_require_vec` inside `connect`/`_vec_doc_ranking`). Raises `ValueError` on empty query (l.1399-1400).

**`search_hybrid_rerank(query, model_tag: str = CPU_FLOOR_TAG, top_k: int = 10, depth: int = RERANK_DEPTH, db_path: str = DEFAULT_DB) -> list`** — l.1500-1501. Docstring l.1502-1518 (see §6). Returns up to `top_k` doc_ids. DB read (fts/vec/chunk_text); calls Ollama (via `_vec_doc_ranking`); loads local reranker model from `RERANK_MODEL_DIR` and runs CPU inference (torch/FlagEmbedding). Honors `RERANK_DISABLE_ENV` (via `_load_reranker`) and `VEC_DISABLE_ENV` indirectly. Raises `ValueError` on empty query; propagates `RerankModelPinMismatch` (not caught).

**`search_graph(query, top_k: int = 10, model_tag: str = CPU_FLOOR_TAG, db_path: str = DEFAULT_DB) -> list`** — l.1559-1560. Docstring l.1561-1573 (see §6/§7). Returns up to `top_k` doc_ids (seeds + expansions). DB read only (`edges` table plus everything `search_hybrid` touches, including a possible Ollama call inside `search_hybrid`'s vector ranking). No DB write. Honors `VEC_DISABLE_ENV` indirectly via `search_hybrid`.

**`embed_texts(model_tag: str, texts, role: str) -> list`** — l.1932. Docstring l.1933-1936: "Embed texts under a model_tag and role -> list of float vectors, with the asymmetric prefixes applied (CHG 2.3)." Calls Ollama (`_ollama_embed`, stdlib `urllib`). No DB, no filesystem. Raises `ValueError` on bad tag/role (via `_embed_payload`), `VecUnavailable` on transport failure.

**`embed_query_cpu(model_tag: str, texts) -> list`** — l.1943. Docstring l.1944-1949: "Embed QUERY texts CPU-FORCED (num_gpu:0) regardless of the tag's default options -- so retrieval-side query embedding is bit-DETERMINISTIC for EVERY tag." Calls Ollama. No DB/filesystem.

**`reindex_vec(model_tag: str, db_path: str = DEFAULT_DB, batch_size: int = 64) -> dict`** — l.1969. Docstring l.1970-1975: "(Re)build ONE model's vector set over the document-body corpus ... Idempotent (CHG 2.4)." Returns `{"model_tag","table","dim","chunks","rows","content_hash","elapsed_s","db_path"}`. Writes DB (`_ensure_vec_table`, truncate+`executemany INSERT` into `vec_items__{tag}`, `_set_meta` per-tag stats). Reads filesystem via `_iter_chunks`→`iter_body_docs` and `_sibling_card_meta`. Calls Ollama via `embed_texts` per batch. Honors `VEC_DISABLE_ENV` via `_require_vec`. Raises `ValueError` on unknown tag, `VecUnavailable` if sqlite-vec/embedder unavailable or embedding count mismatches chunk count (l.1992-1994).

**`emit_gold_queries(out_path: str = GOLD_QUERIES_PATH, anl_path: str = GOLD_ANL_PATH) -> dict`** — l.2142-2143. Docstring l.2144-2149: "Re-reads the ANL and verifies its freeze pin BEFORE writing; a mismatch is a HALT ... The YAML is derived; on any disagreement the ANL governs." Returns `{"path","rows","strata_counts","source_sha256","pin_ok"}`. Reads filesystem (`_sha256_file(anl_path)`); **writes** filesystem — creates parent dir if absent and writes `out_path` (header comment l.2167-2172 + `yaml.safe_dump`), then re-opens and re-reads it to build the report (l.2173-2178). No DB access, no Ollama. Raises `GoldPinMismatch` (HALT) on sha256 mismatch (l.2152-2155).

**`freshness_check(scan, db_path: str = DEFAULT_DB) -> FreshnessReport`** — l.2193. Docstring l.2194-2199: "Compare the live librarian walk (scan.cards) against the index. PURE READ — never mutates." Returns `FreshnessReport`. DB read (`cards` table, `index_meta` `corpus_cards_sha`) plus filesystem reads (`_sha256_file` per `scan.cards[i].yaml_path`). No writes, no Ollama.

**`main(argv=None) -> int`** — l.2243. No docstring; `argparse` CLI dispatcher (mutually-exclusive group `--rebuild/--freshness/--stats/--search/--reindex-vec/--emit-gold/--hybrid/--resolve-id/--rerank/--graph`, l.2248-2266). Returns process exit code. Prints extensively to stdout (see §9). Depending on the flag, may call any of `reindex_full / freshness_check / search_fts / reindex_vec / emit_gold_queries / resolve_identifier / search_hybrid / search_hybrid_rerank / search_graph`, so transitively can write the DB, call Ollama, write `eval/gold_queries.yaml`, and read the whole corpus via `_cli_scan()` (l.2234-2240, which lazily imports `RHACO_tool_catalog_librarian` and calls `_lib.scan_library(_lib.DEFAULT_ROOT, _lib.DEFAULT_OUTPUT, logger)`).

## 5. DDL (schema created by `connect()`)

`SCHEMA_DDL = _METADATA_DDL + _FTS_DDL` (l.518), executed via `conn.executescript(SCHEMA_DDL)` inside `connect()` (l.793), then `_ensure_fts_schema` migrates an old empty `fts_docs`.

`_METADATA_DDL` (l.438-505):
- **`cards`** (l.439-461): `yaml_path TEXT PRIMARY KEY`, `doc_id TEXT NOT NULL`, then `doc_type, date, seq, title, status, project_knowledge, current_version` (TEXT), `schema_version INTEGER`, `naming_convention_version, lifecycle_state, last_human_review, reviewer, doc_filename, doc_path, local_path, abstract, card_sha256, card_mtime_utc, indexed_at_utc` (TEXT). Indexes (l.462-465): `ix_cards_doc_id(doc_id)`, `ix_cards_doc_type(doc_type)`, `ix_cards_status(status)`, `ix_cards_date(date)`.
- **`card_programs`** (l.467-472): `yaml_path TEXT NOT NULL REFERENCES cards(yaml_path) ON DELETE CASCADE`, `program TEXT NOT NULL`, `PRIMARY KEY (yaml_path, program)`; index `ix_cardprog_program(program)`.
- **`card_tags`** (l.474-479): same shape as `card_programs` with `tag`; `PRIMARY KEY (yaml_path, tag)`; index `ix_cardtag_tag(tag)`.
- **`edges`** (l.481-492): `from_id TEXT NOT NULL, to_id TEXT NOT NULL, relation TEXT NOT NULL, source_field TEXT, from_yaml_path TEXT, note TEXT, resolved INTEGER NOT NULL DEFAULT 0` — no primary key. Indexes: `ix_edges_from(from_id)`, `ix_edges_to(to_id)`, `ix_edges_rel(relation)`.
- **`id_aliases`** (l.494-499): `alias TEXT NOT NULL, doc_id TEXT NOT NULL, kind TEXT` — no primary key. Index `ix_id_aliases_alias(alias)`.
- **`index_meta`** (l.501-504): `key TEXT PRIMARY KEY, value TEXT`.

`_FTS_DDL` (l.509-516): `CREATE VIRTUAL TABLE IF NOT EXISTS fts_docs USING fts5(doc_id UNINDEXED, path UNINDEXED, body, tokenize = 'porter unicode61');` — only `body` is a searchable FTS column; tokenizer is `porter unicode61`.

`vec_items__*` (per-model_tag, not part of `SCHEMA_DDL` — created on demand by `_ensure_vec_table`, l.1671-1683, only if the `vec0` extension loaded): table name from `_vec_table(model_tag)` (l.1664-1668: non-alnum chars in `model_tag` replaced with `_`, lowercased) → `vec_items__nomic_embed_text`, `vec_items__bge_m3`, `vec_items__qwen3_embedding_0_6b`. DDL: `CREATE VIRTUAL TABLE IF NOT EXISTS {tbl} USING vec0(chunk_id TEXT PRIMARY KEY, +doc_id TEXT, +path TEXT, +chunk_index INTEGER, +chunk_text TEXT, embedding FLOAT[{dim}])` where `dim` is 768 (nomic) / 1024 (bge-m3) / 1024 (qwen3) per `MODEL_REGISTRY`.

**`index_meta` key writes** (all via `_set_meta`, l.804-809, an upsert `INSERT ... ON CONFLICT(key) DO UPDATE`):
- `reindex_full` (l.892-901): `index_schema_version, librarian_version, current_nc_version, last_full_reindex_utc, corpus_card_count, corpus_cards_sha, fts_docs_count, edges_count, id_aliases_count`.
- `reindex_pair` (l.1076-1079): `corpus_card_count, corpus_cards_sha`.
- `reindex_fts_pair` (l.1155): `fts_docs_count`.
- `reindex_vec` (l.2006-2012): `vec_model__{tag}, vec_dim__{tag}, vec_rows__{tag}, vec_hash__{tag}, vec_reindex_utc__{tag}`.

## 6. Degradation

**`search_hybrid`** (l.1404-1410): builds `fts_rank = _fts_doc_ranking(...)` unconditionally, then `try: rankings = [fts_rank, _vec_doc_ranking(...)] except VecUnavailable: rankings = [fts_rank]`. On `VecUnavailable`, only the FTS5 ranking feeds `_rrf_fuse`; the identifier short-circuit (`resolve_identifier`) is unaffected either way. Docstring (l.1396-1398): "A VecUnavailable substrate degrades to short-circuit + FTS5 with NO raise (charter 3.3)." So the remaining channels are: identifier short-circuit + FTS5 lexical; the vector channel is dropped and nothing is raised.

**`search_graph`** (l.1559-1623): seeds = identifier short-circuit ∪ top-5 `search_hybrid` (l.1577-1578) — since `search_hybrid` itself degrades on `VecUnavailable`, the seed channel silently becomes short-circuit + FTS-only top-5 when vec is unavailable, per docstring l.1572-1573: "A VecUnavailable substrate degrades the hybrid seed channel exactly as search_hybrid (no raise)." The 1-hop expansion logic (l.1592-1620) reads only the `edges` table and is unaffected by `VecUnavailable`.

**`RERANK_DISABLE_ENV`** — read in `_load_reranker` (l.1439-1440): `if os.environ.get(RERANK_DISABLE_ENV): raise RerankUnavailable(...)`, checked *before* the artifact-file-existence check (l.1441-1443) and the pin check (l.1444-1448).

**`search_hybrid_rerank`** (l.1500-1552) dependencies/behavior:
- Reranker model: local cross-encoder `bge-reranker-v2-m3` at `RERANK_MODEL_DIR` = `C:\RHACO\models\bge-reranker-v2-m3`, weight file `model.safetensors`, sha256-pinned to `RERANK_MODEL_PIN`; loaded lazily via `_load_reranker` (l.1422-1457), which imports `torch` + `FlagEmbedding.FlagReranker` only at call time ("NO torch/FlagEmbedding import at module import time", l.1424-1425) and sets `KMP_DUPLICATE_LIB_OK` before importing torch, `torch.set_num_threads(1)`, `use_fp16=False`, `devices="cpu"` (l.1449-1456).
- Cost notes in comments/docstrings: `RERANK_DEPTH = 100` "ADR A4 over-retrieval depth = 10x default top_k (fixed)" (l.400); docstring l.194-196 repeats "taken to depth=100 candidates (ADR A4, 10x top_k, fixed not tuned)"; determinism cost is explicit — CPU-forced + `set_num_threads(1)` + fp32 "for the x2 bit-identical determinism invariant (HND-20260711-003 §0.7)" (l.189-191, 1427-1430).
- On `RerankUnavailable` (l.1522-1525) **or** `VecUnavailable` from `_vec_doc_ranking` (l.1529-1534), it returns the plain `search_hybrid(...)` result — "Uniform per-channel degradation (charter 3.3) ... each unavailable channel knocks out exactly itself, NO raise" (l.1513-1516). A `RerankModelPinMismatch` is explicitly **not** caught here (only `RerankUnavailable` is), so it propagates as a HALT (l.1517-1518, 1522-1523 comment "RerankModelPinMismatch propagates (HALT)").
- Chunk text source: `_chunk_texts_for_docs` reads stored M2 chunk text **only** from the vec0 store — "there is no runtime chunker fallback" (l.1471-1479).

## 7. Filter routing

Only **`search_fts`** exposes filter parameters, and only against the lexical/body channel:
- `doc_type_filter` (l.1189, applied l.1212, 1235-1237): a set of uppercased doc-type codes; matched via `_doc_type_from_filename(os.path.basename(path))` parsed from the filename — a per-row filter over `fts_docs` rows, i.e. the lexical channel.
- `path_glob` (l.1189, applied l.1239-1240): `_glob_match(path, path_glob)` (fnmatch against posix path and basename) — also lexical-channel-only.

No function accepts `status`, `lifecycle_state`, `program`, `tag`, or a date-range filter parameter — confirmed by grep (`status_filter|lifecycle_state|program_filter|tag_filter|date_from|date_to|date_range`): the only hits are the `lifecycle_state` **column** in `_CARDS_COLUMNS`/DDL/`_card_row` (storage only) and `_date_from_filename` (a filename-date parser, not a search filter). `search_hybrid`, `search_hybrid_rerank`, and `search_graph` accept no filter parameters at all (only `query, model_tag, top_k[, depth], db_path`) — their signatures carry no doc_type/status/program/tag/date arguments, so filtering by those facets is unavailable on the vector/hybrid/graph channels through this module's public API.

## 8. Identifier handling

`resolve_identifier(query, db_path=DEFAULT_DB)` (l.1306) short-circuits via `_is_identifier_query` (l.1285-1291): the **whole trimmed** query must match one of three anchored regexes — `_RESOLVE_FULL_RE` (full canonical `RHACO-TYPE-YYYYMMDD-SEQ`), `_RESOLVE_BARE_RE` (bare `TYPE-YYYYMMDD-SEQ`), or `_RESOLVE_EVENT_RE` (`E######`). A non-matching (prose) query returns `[]` immediately without opening a connection (l.1310-1311).

Normalization/lookup is a **pure exact-match** against the `id_aliases` table (`_aliases_lookup`, l.1294-1303): `SELECT DISTINCT doc_id FROM id_aliases WHERE alias=? ORDER BY doc_id`. Docstring: "Pure lookup, no classification" (l.152-153, module version-history v1.4 note) / "Pure lexical lookup against id_aliases -- no classification, no LLM" (l.1309).

The `id_aliases` table is populated by `_card_id_aliases` (l.742-764) at `reindex_full` time, deriving from each card's `doc_id` (via `_ALIAS_CANONICAL_RE` split into type/date/seq): `(canonical_id, canonical_id, "canonical")`, `("TYPE-DATE-SEQ", canonical_id, "bare_seq")`, and for `EVT`-type docs, every `E######` harvested from the filename and the card title as `(eid, canonical_id, "event_id")` (l.756-763). A non-canonical (REF-style) `doc_id` that doesn't match `_ALIAS_CANONICAL_RE` yields no alias rows ("unresolvable by construction", l.750).

**No match**: `resolve_identifier` returns `[]` (l.1303's `rows` is empty → `[r[0] for r in rows]` is `[]`; also short-circuited to `[]` up-front for non-identifier-form queries).
**Multiple matches**: returns **all** matching `doc_id`s, sorted ascending (`ORDER BY doc_id`, l.1301) — e.g. the same alias can point at several `doc_id`s when multiple filename versions share one canonical id (the `(?:_[^.]*)?` version-suffix group in `_CANONICAL_FILENAME_RE`, l.286, is not captured, so `..._v1.md` and `..._v2.md` both resolve to the same canonical `doc_id`... more generally distinct docs can register the same alias). In `search_hybrid`/`search_hybrid_rerank`/`search_graph` these are all placed at ranks 1..n as an authoritative "short-circuit" ahead of any fused ranking (l.1402-1403, 1526-1527, 1577).

## 9. Output side effects

**Print statements** are confined to `main()`'s CLI dispatch (l.2243-2373) — no `print` calls exist anywhere else in the file (only `main`'s branches print): `--stats` (l.2271-2296, dumps `index_meta` k/v pairs, per-table row counts, per-relation edge breakdown, `edges[resolved=0]`, `vec_available`, per-tag vector stats), `--search` (l.2303-2306), `--reindex-vec` (l.2311-2314), `--emit-gold` (l.2319-2321), `--resolve-id` (l.2326), `--hybrid` (l.2331-2333), `--rerank` (l.2340, 2342-2345, including a HALT-path print at l.2340 for pin mismatch), `--graph` (l.2349-2351), and the default rebuild/freshness path (l.2359-2373).

**Logging**: `_NULL_LOG` (l.256-258) is a `logging.getLogger("rhaco_corpus_index_edges")` with a `NullHandler` and `propagate=False` — used only as the `logger` argument passed into the librarian's `_resolve_reference` calls inside `emit_edges` (l.997, 1012); comment states this is deliberate so edge derivation "must NEVER emit into a census/validation log." No other `logging` calls appear in the file (the CLI's `_cli_scan`, l.2236-2239, also builds a `NullHandler`-only logger for the standalone librarian walk).

**File-write side effect** (the only one in the module): `emit_gold_queries` writes `out_path` (default `GOLD_QUERIES_PATH`) — creates the parent dir if absent, writes a 5-line header comment (l.2167-2172) plus `yaml.safe_dump(doc, ...)` (l.2173-2176), then reopens the file to re-parse it for the return report (l.2177-2178).

**Hard-coded Windows paths** (all under `C:\RHACO`, all built from `r"C:\RHACO"` literals via `os.path.join`):
- `_INDEX_DIR` = `C:\RHACO\index` (l.264); `DEFAULT_DB` = `C:\RHACO\index\corpus_index.db` (l.265; also stated in the docstring OUTPUT line 38-39 as `C:\\RHACO\\index\\corpus_index.db`).
- `BODY_SCAN_ROOT` = `C:\RHACO\docs` (l.272).
- `RERANK_MODEL_DIR` = `C:\RHACO\models\bge-reranker-v2-m3` (l.395).
- `GOLD_ANL_PATH` = `C:\RHACO\docs\reports\RHACO-ANL-20260711-001_Corpus_RAG_Gold_Query_Set_v1_1_Freeze.md` (l.2036-2038, built from `BODY_SCAN_ROOT`).
- `_EVAL_DIR` = `C:\RHACO\working\eval` (l.2039); `GOLD_QUERIES_PATH` = `C:\RHACO\working\eval\gold_queries.yaml` (l.2040).

## 10. UNVERIFIED

- **Behavior of `RHACO_tool_catalog_librarian` symbols referenced by this module** — `_lib._build_id_index`, `_lib._resolve_reference`, `_lib.EXTERNAL_REFS`, `_lib.is_amendment_of`, `_lib.Card`, `_lib.LIBRARY_DOC_GLOB_SUFFIXES`, `_lib.DEFAULT_ROOT`, `_lib.DEFAULT_OUTPUT`, `_lib.scan_library`, `_lib.LIBRARIAN_VERSION`, `_lib.CURRENT_NC_VERSION` (used in `emit_edges` l.964-1025, `_load_card` l.1101-1129, `_cli_scan` l.2234-2240, `main` l.2354-2358) — this task (I1) scoped inspection to `RHACO_corpus_index.py` only; I did not read `RHACO_tool_catalog_librarian.py` for this report, so their exact contracts are unverified here (only how this module calls them is verified).
- **Runtime behavior** (actual DDL execution, actual `search_fts`/`search_hybrid` output, actual index_meta contents) was not verified empirically — per the read-only mandate, no Python was run and no database file was opened; everything above is derived from static reading of the source text only.
- Everything else requested in the task (module header, constants, classes, all 19 public functions, DDL, degradation paths, filter routing, identifier handling, output side effects/hard-coded paths) was directly verifiable from the file text and is reported above with line numbers.
