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
Dispatch record (RHACO-HND-20260903-001 section 2 I as amended by A1.3): strand_id I4; role: prompt section 1 inspection strand; tier: mid; model requested: Claude Sonnet 5; agent_type: Explore (read-only); pattern_primary: #7 (inspection); execution_mode: sequential (after the wave of 3 returns); tier_escalation: none. Round 0 (pre-build inspection) of the RHACO Corpus Explorer autonomous build; dispatched by the build orchestrator.

Working rules for this strand:
1. Read-only. Create, edit, or delete nothing, anywhere. Do not run Python or any script; do not import any module; do not open any database file. Allowed: file reads, text search, directory listing, and exactly two PowerShell timestamp commands -- (Get-Date).ToUniversalTime().ToString("o") -- one when you start and one when you finish.
2. Read only these paths: C:\RHACO\docs\** (the corpus); C:\RHACO\rhaco\RHACO_corpus_index.py; C:\RHACO\tools\RHACO_tool_catalog_librarian.py; C:\RHACO\working\eval\gold_queries.yaml and gold_queries_v1_2.yaml; and, in the build workspace, C:\highsierralabs\RHACO_Corpus_Explorer\PROMPT.md and DISPATCH_PARAMETERS.md. Nothing else under C:\RHACO\ or C:\highsierralabs\RHACO\ -- in particular not C:\RHACO\data\, not any other file under C:\RHACO\rhaco\, and not the repository root.
3. Foreground only: no run_in_background, no detached processes, no sleeping or polling.
4. Evidence discipline: every claim carries a file path and line number(s) (or the section heading for markdown). Quote identifiers, signatures, and vocabularies exactly. Do not infer what you did not read; list anything you could not verify under UNVERIFIED. Prefer reading the named regions in full over sampling.
5. Your final message is data returned to the orchestrator, not a message to a person: return the report in the exact structure requested, with no preamble and no closing remarks. If a StructuredOutput tool is available to you, return the same content through it: the header fields below as the fields of that name, and the numbered sections as the single markdown string `report`.

Report header (the first lines of your report, in this order):
strand_id: I4
model_id: <copy the sentence from your own system prompt that names your model, e.g. "You are powered by the model named X. The exact model ID is Y.">
t_start_utc: <your first Get-Date reading>
t_end_utc: <your last Get-Date reading>
files_read: <paths, one per line>
commands_run: <the commands you executed, verbatim>
deviations: <none, or each rule above you could not honor and why>

Task I4 -- existing RHACO conventions a local document explorer must respect (input to CONSTRAINTS.md, the reader, and the catalog).

Sources under C:\RHACO\docs\reference\ (read the relevant sections in full and cite them): the Naming Convention v1.17 document (identifier grammar, type codes and their homes, versioned reference-document names, amendment-child naming); the Report Style Guide v1.9 (heading and section conventions, anchors, house typography); RHACO-SOP-20260526-001_MCP_Server_Tool_Surface_Management_v2.md and the Tool Reference v1.35 (the documented public corpus / retrieval tool surface -- tool names, parameters, return shapes, and which module function each wraps, as documented; this is the "public retrieval behavior" the explorer should mirror); the Data Architecture Reference v1.0 (where documents live in the tree); the Document Catalog (what it lists and how). Then grep C:\RHACO\docs\** for any existing viewer or browse tool and its conventions (patterns: viewer, "Event Viewer", browse, read_corpus, search_corpus, resolve_identifier, lineage, catalog). Produce, with line or section references:
1. Identifier grammar at regex level; the type-code list with each type's home directory; versioned reference-document naming; amendment-child naming and how children relate to parents.
2. The documented MCP corpus tool surface: each tool name, its parameters, its return shape, and the module function it wraps.
3. Section-anchor conventions used in citations (for example "section 4.2", "M1", "A1.3") that a reader jump-to-section feature must resolve, with examples.
4. Frozen / live partition rules (docs_archive, deprecated, _staging, DENY_DIRS, status values that mean frozen) that affect what the explorer should show or label.
5. Any existing viewer or browse tool (for example the event viewer extraction tool) and the conventions it established that a document explorer should follow or must not confuse.
6. House typography and encoding facts relevant to rendering (UTF-8, em dashes, section signs, box drawing, code fences with Windows paths).
7. UNVERIFIED: anything above you could not establish from the texts.
