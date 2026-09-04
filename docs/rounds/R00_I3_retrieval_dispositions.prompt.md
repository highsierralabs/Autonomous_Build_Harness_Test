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
Dispatch record (RHACO-HND-20260903-001 section 2 I as amended by A1.3): strand_id I3; role: prompt section 1 inspection strand; tier: mid; model requested: Claude Sonnet 5; agent_type: Explore (read-only); pattern_primary: #7 (inspection); execution_mode: concurrent (wave of 3); tier_escalation: none. Round 0 (pre-build inspection) of the RHACO Corpus Explorer autonomous build; dispatched by the build orchestrator.

Working rules for this strand:
1. Read-only. Create, edit, or delete nothing, anywhere. Do not run Python or any script; do not import any module; do not open any database file. Allowed: file reads, text search, directory listing, and exactly two PowerShell timestamp commands -- (Get-Date).ToUniversalTime().ToString("o") -- one when you start and one when you finish.
2. Read only these paths: C:\RHACO\docs\** (the corpus); C:\RHACO\rhaco\RHACO_corpus_index.py; C:\RHACO\tools\RHACO_tool_catalog_librarian.py; C:\RHACO\working\eval\gold_queries.yaml and gold_queries_v1_2.yaml; and, in the build workspace, C:\highsierralabs\RHACO_Corpus_Explorer\PROMPT.md and DISPATCH_PARAMETERS.md. Nothing else under C:\RHACO\ or C:\highsierralabs\RHACO\ -- in particular not C:\RHACO\data\, not any other file under C:\RHACO\rhaco\, and not the repository root.
3. Foreground only: no run_in_background, no detached processes, no sleeping or polling.
4. Evidence discipline: every claim carries a file path and line number(s) (or the section heading for markdown). Quote identifiers, signatures, and vocabularies exactly. Do not infer what you did not read; list anything you could not verify under UNVERIFIED. Prefer reading the named regions in full over sampling.
5. Your final message is data returned to the orchestrator, not a message to a person: return the report in the exact structure requested, with no preamble and no closing remarks. If a StructuredOutput tool is available to you, return the same content through it: the header fields below as the fields of that name, and the numbered sections as the single markdown string `report`.

Report header (the first lines of your report, in this order):
strand_id: I3
model_id: <copy the sentence from your own system prompt that names your model, e.g. "You are powered by the model named X. The exact model ID is Y.">
t_start_utc: <your first Get-Date reading>
t_end_utc: <your last Get-Date reading>
files_read: <paths, one per line>
commands_run: <the commands you executed, verbatim>
deviations: <none, or each rule above you could not honor and why>

Task I3 -- standing retrieval dispositions of record (input to docs/REFERENCE.md and the search module's defaults).

Sources, read in full: C:\RHACO\docs\reports\RHACO-ANL-20260712-001_*.md and its .card.yaml; C:\RHACO\docs\reports\RHACO-CMP-20260628-001_*.md and its card; C:\RHACO\docs\reports\RHACO-CHG-20260712-002_*.md and its card; C:\RHACO\working\eval\gold_queries.yaml and gold_queries_v1_2.yaml (structure and counts). Then search C:\RHACO\docs\** for any later ANL / CHG / CMP that changes the retrieval default or re-evaluates hybrid-rerank or graph after 2026-07-12 (patterns: search_hybrid_rerank, hybrid-rerank, Recall@10, "flat hybrid", "M4 default", search_graph, gold_queries_v1_2) and report whether the standing state has moved since the build prompt was authored. Produce, with line or section references:
1. The accepted default retrieval path and its evidence: mode, Recall@10 aggregate, gold set version, date, the ratifying CHG and what it flipped.
2. hybrid-rerank disposition: score, verdict (negative result / FAIL), the "documented-FAIL batch mode" language, the per-query cost, and where it says the mode must never be on an interactive path.
3. graph disposition: score, "auxiliary lineage mode" language.
4. Filter routing rule for search_corpus ("filters apply to lexical only" or as stated) -- quote the source.
5. Gold v1.1 structure: row count, strata, fields per row (query, targets, hit rule, metric), how a hit is defined; Gold v1.2: row count and its baseline status.
6. Evidence superseding any of the above: cite it, or state none found and list the exact search patterns and directories you used.
7. UNVERIFIED: anything above you could not establish from the texts.
