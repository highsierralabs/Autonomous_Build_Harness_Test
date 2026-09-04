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
Dispatch record (RHACO-HND-20260903-001 section 2 I as amended by A1.3): strand_id I2; role: prompt section 1 inspection strand; tier: mid; model requested: Claude Sonnet 5; agent_type: Explore (read-only); pattern_primary: #7 (inspection); execution_mode: concurrent (wave of 3); tier_escalation: none. Round 0 (pre-build inspection) of the RHACO Corpus Explorer autonomous build; dispatched by the build orchestrator.

Working rules for this strand:
1. Read-only. Create, edit, or delete nothing, anywhere. Do not run Python or any script; do not import any module; do not open any database file. Allowed: file reads, text search, directory listing, and exactly two PowerShell timestamp commands -- (Get-Date).ToUniversalTime().ToString("o") -- one when you start and one when you finish.
2. Read only these paths: C:\RHACO\docs\** (the corpus); C:\RHACO\rhaco\RHACO_corpus_index.py; C:\RHACO\tools\RHACO_tool_catalog_librarian.py; C:\RHACO\working\eval\gold_queries.yaml and gold_queries_v1_2.yaml; and, in the build workspace, C:\highsierralabs\RHACO_Corpus_Explorer\PROMPT.md and DISPATCH_PARAMETERS.md. Nothing else under C:\RHACO\ or C:\highsierralabs\RHACO\ -- in particular not C:\RHACO\data\, not any other file under C:\RHACO\rhaco\, and not the repository root.
3. Foreground only: no run_in_background, no detached processes, no sleeping or polling.
4. Evidence discipline: every claim carries a file path and line number(s) (or the section heading for markdown). Quote identifiers, signatures, and vocabularies exactly. Do not infer what you did not read; list anything you could not verify under UNVERIFIED. Prefer reading the named regions in full over sampling.
5. Your final message is data returned to the orchestrator, not a message to a person: return the report in the exact structure requested, with no preamble and no closing remarks. If a StructuredOutput tool is available to you, return the same content through it: the header fields below as the fields of that name, and the numbered sections as the single markdown string `report`.

Report header (the first lines of your report, in this order):
strand_id: I2
model_id: <copy the sentence from your own system prompt that names your model, e.g. "You are powered by the model named X. The exact model ID is Y.">
t_start_utc: <your first Get-Date reading>
t_end_utc: <your last Get-Date reading>
files_read: <paths, one per line>
commands_run: <the commands you executed, verbatim>
deviations: <none, or each rule above you could not honor and why>

Task I2 -- card-schema fields as used by the index (input to the catalog facets and the reader's card panel in ARCHITECTURE.md).

Sources: C:\RHACO\docs\reference\RHACO_Card_YAML_Schema_Specification_v1_9.md (read in full); in C:\RHACO\rhaco\RHACO_corpus_index.py the card-to-row mapping (the functions that build cards / card_programs / card_tags / edges / id_aliases rows -- look for _card_row, _card_id_aliases, emit_edges, and the DDL); in C:\RHACO\tools\RHACO_tool_catalog_librarian.py only: VALID_PROGRAMS, DENY_DIRS, DEFAULT_ROOT, the status vocabulary, the lifecycle_state rules, and the naming-convention regex. Produce, with line numbers:
1. Card schema v1.9 field inventory: every top-level and nested key (identity.*, parent.*, amendment_seq, abstract, tags, programs, depends_on[], see_also[], superseded_by, location.*, notes, and any others), required vs optional, and allowed values -- the status vocabulary, the lifecycle_state vocabulary and its CMP-only rule, the programs vocabulary, project_knowledge values, the doc_type codes.
2. Materialization: which card keys the index stores (table.column <- card key), which are dropped, and how multi-valued fields (programs, tags) are stored.
3. Edges: the relations materialized (cites, supersedes, amends, campaign_child, others), their source_field, the direction convention (what from_id -> to_id means for each relation), the meaning of the resolved flag, and how unresolved targets are retained.
4. Identity: the doc_id format; how amendment children share their parent's doc_id (RHACO-HND-20260903-001 currently has two cards: the hand and its Amendment A1) and which column disambiguates rows; the consequence for a UI that asks for "the document with id X".
5. status vs lifecycle_state: quote the specification text that separates the two channels and list which document types carry lifecycle_state.
6. Facet candidates in the data model: document type, date, status, lifecycle_state, program, tags, project_knowledge, path/location -- for each, whether it comes from the card, the index, or the filesystem.
7. UNVERIFIED: anything above you could not establish from the texts.
