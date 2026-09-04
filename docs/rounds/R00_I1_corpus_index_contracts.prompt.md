> Device-safety prohibition (RHACO Guide v1.3 D-12, applied to a
> non-device build). You may launch only the workspace's own Python
> interpreter running workspace code — tests, lint, the explorer server
> via the probe. You must not launch, spawn, import as a process, or
> invoke any `RHACO_logger_*`, `RHACO_sidecar_*`, `RHACO_launcher*`,
> `RHACO_tool_*` (other than importing `RHACO_tool_catalog_librarian` for
> read-only walk/scan calls), or anything under `C:\RHACO\rhaco\` other
> than importing `RHACO_corpus_index`. You must not open any device on
> any transport (USB, BLE, serial). You must not read or write anything
> under `C:\RHACO\data\`. "Verify" means re-derive from files on disk or
> from the fixture; it never means run an acquisition or restart a
> production process. Violation is a halt, not a retry.

> Foreground only (RHACO Guide v1.3 D-3). Do not use `run_in_background`,
> do not detach, do not sleep-and-poll a background job. Work that exceeds
> your budget is walked in sequential foreground invocations or returned as
> WAITING. A backgrounded process is a halt, not a retry.

---
Dispatch record (RHACO-HND-20260903-001 section 2 I as amended by A1.3): strand_id I1; role: prompt section 1 inspection strand; tier: mid; model requested: Claude Sonnet 5; agent_type: Explore (read-only); pattern_primary: #7 (inspection); execution_mode: concurrent (wave of 3); tier_escalation: none. Round 0 (pre-build inspection) of the RHACO Corpus Explorer autonomous build; dispatched by the build orchestrator.

Working rules for this strand:
1. Read-only. Create, edit, or delete nothing, anywhere. Do not run Python or any script; do not import any module; do not open any database file. Allowed: file reads, text search, directory listing, and exactly two PowerShell timestamp commands -- (Get-Date).ToUniversalTime().ToString("o") -- one when you start and one when you finish.
2. Read only these paths: C:\RHACO\docs\** (the corpus); C:\RHACO\rhaco\RHACO_corpus_index.py; C:\RHACO\tools\RHACO_tool_catalog_librarian.py; C:\RHACO\working\eval\gold_queries.yaml and gold_queries_v1_2.yaml; and, in the build workspace, C:\highsierralabs\RHACO_Corpus_Explorer\PROMPT.md and DISPATCH_PARAMETERS.md. Nothing else under C:\RHACO\ or C:\highsierralabs\RHACO\ -- in particular not C:\RHACO\data\, not any other file under C:\RHACO\rhaco\, and not the repository root.
3. Foreground only: no run_in_background, no detached processes, no sleeping or polling.
4. Evidence discipline: every claim carries a file path and line number(s) (or the section heading for markdown). Quote identifiers, signatures, and vocabularies exactly. Do not infer what you did not read; list anything you could not verify under UNVERIFIED. Prefer reading the named regions in full over sampling.
5. Your final message is data returned to the orchestrator, not a message to a person: return the report in the exact structure requested, with no preamble and no closing remarks. If a StructuredOutput tool is available to you, return the same content through it: the header fields below as the fields of that name, and the numbered sections as the single markdown string `report`.

Report header (the first lines of your report, in this order):
strand_id: I1
model_id: <copy the sentence from your own system prompt that names your model, e.g. "You are powered by the model named X. The exact model ID is Y.">
t_start_utc: <your first Get-Date reading>
t_end_utc: <your last Get-Date reading>
files_read: <paths, one per line>
commands_run: <the commands you executed, verbatim>
deviations: <none, or each rule above you could not honor and why>

Task I1 -- corpus-index public contract inventory (input to the corpus_adapter module of ARCHITECTURE.md).

Inspect C:\RHACO\rhaco\RHACO_corpus_index.py (118,123 bytes): the retrieval substrate the explorer must reuse and never reimplement. Produce, with line numbers:
1. Module header: purpose statement and the version-history lines at the top of the file.
2. Constants block: every module-level constant with its value (DEFAULT_DB, _INDEX_DIR, BODY_SCAN_ROOT, INDEX_SCHEMA_VERSION, MODEL_TAGS, CPU_FLOOR_TAG, OLLAMA_HOST, OLLAMA_TIMEOUT_S, RRF_K, RERANK_DEPTH, MAX_SEARCH_RESULTS, VEC_DISABLE_ENV, RERANK_DISABLE_ENV, and any others).
3. Classes: every class (name, base, line, first docstring line) -- exceptions such as VecUnavailable, and any dataclass / NamedTuple used as a return row (list its fields).
4. Public functions (no leading underscore), each with: exact signature including defaults; line; docstring summary; return shape (row/field names); whether it writes the database, calls Ollama, or reads the filesystem; environment switches honored. Cover at least connect, reindex_full, reindex_pair, reindex_fts_pair, reindex_vec, emit_gold_queries, search_fts, resolve_identifier, search_hybrid, search_hybrid_rerank, search_graph, freshness_check, iter_body_docs, and every other public def you find.
5. DDL: the schema created by connect() -- every table and virtual table (cards, card_programs, card_tags, edges, fts_docs, id_aliases, index_meta, vec_items__*), columns, keys / uniqueness, FTS5 tokenizer and options, and how index_meta keys are written.
6. Degradation: exactly what search_hybrid and search_graph do when VecUnavailable is raised (which channels remain, what is returned); how RERANK_DISABLE_ENV is read; what search_hybrid_rerank does, its dependencies (reranker model, path), and any cost notes in comments or docstrings.
7. Filter routing: which functions accept filters (doc_type, status, lifecycle_state, program, tag, date, ...), the parameter names, and which channel (lexical / vector / graph) each filter applies to.
8. Identifier handling: how resolve_identifier normalizes an input (RHACO-TYPE-YYYYMMDD-SEQ, versioned reference names, aliases table), what it returns for no match and for multiple matches.
9. Output side effects: anything the module prints or logs, and every hard-coded Windows path.
10. UNVERIFIED: anything above you could not establish from the file text.
