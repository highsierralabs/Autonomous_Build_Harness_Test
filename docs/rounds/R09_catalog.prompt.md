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
Dispatch record (RHACO-HND-20260903-001 section 2 I as amended by A1.3): strand_id S8-B15; role: module builder (catalog), filter legibility and metadata honesty; tier: mid; model requested: Claude Sonnet 5; agent_type: general-purpose (write-scoped to the worktree below); pattern_primary: #3 candidate (worktree-isolated builder); execution_mode: concurrent (two strands live -- search round 2 is running in its own worktree, under the A1.3 cap of 3); tier_escalation: none; orchestrator_model: claude-opus-5[1m] (Director ruling MOD-1). Round 7 of the RHACO Corpus Explorer autonomous build; catalog module round 2 of 4 -- this strand consumes one builder round of the 28. Director ruling 2026-09-05: dispatched concurrently with search round 2, against a budget ceiling of 20 of 28 for the convergence phase.

Your worktree: C:\highsierralabs\RHACO_Corpus_Explorer\.worktrees\catalog -- a git worktree of the workspace repository on branch build/catalog, checked out at the tip of `main` at dispatch. That tip is a descendant of `6cca928` and it adds this prompt file itself, so this prompt cannot name its own commit: your first git act is `git rev-parse HEAD` -- RECORD what it returns and report it as your base, do not match it against a literal here. What you can verify is that your HEAD contains `6cca928` (`git merge-base --is-ancestor 6cca928 HEAD`); if it does not, STOP and return status BLOCKED. Your round-1 work is merged there along with six later rounds; 290 tests pass, tests/catalog among them. Your interpreter: C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe (the workspace's own venv: Python 3.13; fastapi, uvicorn, jinja2, playwright + chromium, pytest, httpx, pyyaml, sqlite-vec, markdown-it-py, mdit-py-plugins, ruff). Run every command with the worktree as the current directory, e.g. `cd C:\highsierralabs\RHACO_Corpus_Explorer\.worktrees\catalog; C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m pytest tests/catalog -q`.

Working rules:
1. Write only inside your worktree, and there only under your owned paths: `explorer/catalog/**` and `tests/catalog/**`; plus your round report `docs/rounds/R09_catalog.report.md`. Do not modify `explorer/app.py`, `explorer/config.py`, `explorer/models.py`, `explorer/faults.py`, `explorer/corpus_adapter/**`, `explorer/search/**`, `explorer/reader/**`, `explorer/lineage/**`, `explorer/diagnostics/**`, `explorer/web/**`, `tools/**`, `fixtures/**`, `requirements.txt`, `ruff.toml`, `.gitignore`, `PROMPT.md`, `RATIONALE.md`, `DISPATCH_PARAMETERS.md`, `CONSTRAINTS.md`, `ARCHITECTURE.md`, `SCOPE.md`, `build_state.json`, `docs/LAYERS.md`, `docs/REFERENCE.md`, `docs/probe-qualification/**`, or any other module's directory or tests. If you need a change there, record it in a "Change requests" section and code against the current contract. **`explorer/search/**` is being edited by a concurrent strand right now: do not read it as stable and do not touch it.**
2. Outside the worktree you may only READ: C:\RHACO\docs\** (the corpus); C:\RHACO\index\corpus_index.db, and only through `RHACO_corpus_index.connect()`, never opened any other way; C:\RHACO\rhaco\RHACO_corpus_index.py; C:\RHACO\tools\RHACO_tool_catalog_librarian.py; C:\RHACO\working\eval\gold_queries.yaml and gold_queries_v1_2.yaml. Nothing else under C:\RHACO\ or C:\highsierralabs\RHACO\ (C:\RHACO is a junction to C:\highsierralabs\RHACO -- one tree, both spellings out of bounds beyond that list). **Never write to the live index**; never edit the RHACO module; never call the five index-writing functions named in CONSTRAINTS.md S6 (your L1 check greps for them).
3. Processes: only the venv interpreter running workspace code (pytest, ruff, your own scripts). No server process at all: tests use `fastapi.testclient.TestClient` in-process, or call the service directly. Never launch uvicorn -- the probe is the only sanctioned launcher. No `run_in_background`, no detached processes, no sleep-and-poll loops.
4. Git: commit on your branch in small increments with imperative ASCII subjects; `git add` specific paths only, never -A; no amend, no rebase, no push, no checkout of another branch, no merge. Leave the worktree clean when you finish and report `git rev-parse HEAD`.
5. Gate before you finish: (a) `...\.venv\Scripts\python.exe -m ruff check explorer tools tests --output-format concise` clean; (b) `...\.venv\Scripts\python.exe -m pytest tests/catalog -q` green, then `...\.venv\Scripts\python.exe -m pytest tests -q` green as well; (c) `...\.venv\Scripts\python.exe tools/l1_index_write_check.py` PASS (it now runs TWO checks -- the index-write grep and an import boundary; both must pass). Paste the exact commands and their output tails.
6. Evidence discipline: cite file paths and line numbers; every "tested" claim names the test; anything not verified is UNVERIFIED. ASCII-only stdout in any script you write; UTF-8 with LF line endings.
7. Timestamps and identity: run `(Get-Date).ToUniversalTime().ToString("o")` as your FIRST tool call and again when you finish; copy the sentence from your own system prompt that names your model.
8. Return your result through the StructuredOutput tool: the header fields by name, and write your round report to `docs/rounds/R09_catalog.report.md` with the sections Header, Change, Evidence, Material alternatives, Decisions, Result, Unresolved uncertainty, Change requests, Assumptions.

Read first, inside your worktree, in this order: `docs/critique/R06_critic_round_1.report.md` -- ranked issue 6 in section 3, and the `browse_search_usability` and `metadata_fidelity` rows of the section-2 table; `explorer/catalog/service.py` in full, especially the `show_lifecycle_control` computation and `query_string_no_page`; `explorer/catalog/templates/catalog/catalog.html` (the abstract cell and the table header) and `explorer/catalog/static/catalog.css` (`.table-scroll`, `.abstract`); CONSTRAINTS.md O14 (facet vocabularies come only from `adapter.facets()`) and the card-status vs CMP-lifecycle_state distinction wherever it is stated; `tests/catalog/` in full. Then the task.

Task B15 -- three catalog findings from critic round 1, all of them on the surface whose whole job is keeping metadata legible.

**Item 1 -- an active `lifecycle_state` filter can become invisible and unclearable (the critic's ranked issue 6).** Its evidence, verbatim:

> `explorer/catalog/service.py:163` -- `show_lifecycle_control = (filters.doc_type == 'CMP') or bool(catalog_page.facets.lifecycle_states)`, where the facets are computed UNDER the current filter. Submitting `doc_type=ANL` together with any `lifecycle_state` (both controls are present and selectable in one form) yields zero rows, empty lifecycle facets, and therefore a page that applies the filter but does not render its control. The filter also survives in `query_string_no_page` and so is carried onto page-2 links.

The consequence the critic draws is the part that matters: the operator sees "no cards match the current filters" with no visible reason and no way to clear the offending filter except "Clear filters", which discards everything.

Reproduce it first -- against the fixture or the live index, your choice, but reproduce it and paste the evidence before you change anything. Then fix it so that **a filter that is in force is always visible and always individually clearable**. The exact mechanism is yours to choose and to defend in "Decisions"; the invariant is not. Consider at least: rendering the control whenever the filter is ACTIVE regardless of the facet counts under it; and offering a per-filter clear affordance rather than only the all-or-nothing "Clear filters". Do not fix it by silently dropping the filter -- an applied filter that vanishes is the same class of lie, pointing the other way.

Verify the CMP-only reasoning still holds: `lifecycle_state` is a CMP concept, and CONSTRAINTS/the card schema keep card `status` and CMP `lifecycle_state` strictly separate (objective gate 6). Whatever you do must not collapse them, and must not offer `lifecycle_state` as though it applied to every doc_type.

**Item 2 -- every abstract is labelled as truncated, including complete ones.** The critic, under `metadata_fidelity`: `catalog.html:183` appends `' ...'` to EVERY abstract, including abstracts under 200 characters, so a complete abstract is presented as though something had been cut. On a provenance tool that is a small false statement about the record, which is the exact defect class the round-6 work spent itself on (sealed audit SA-1/SA-2/SA-3 were all false claims in prose about behaviour). Show the ellipsis only when the text was actually truncated. Verify against a real short abstract in the corpus or fixture and paste the before/after.

**Item 3 -- the catalog table's header is clipped at the probe's viewport.** The critic, under `browse_search_usability`: at 1280px the W4 capture's header row is clipped after `Prog...`, so Programs, CMP lifecycle state, Abstract and Open all require horizontal scrolling -- and, in its words, *"the CMP lifecycle column being exactly the one W4 exists to make visible."* The table already sits in a `.table-scroll` overflow-x container, so this is not an unbounded-overflow bug like the reader's; it is a column-budget problem inside a scroller.

Improve it within your own module (`catalog.css`, the template's column set and widths). You are NOT required to make nine columns fit 1280px if that would cost legibility -- but the CMP lifecycle column must be reachable without horizontal scrolling at 1280px, because a probe preset exists specifically to make it visible. If you conclude the honest fix is fewer default columns, or a different column order, say so and do it. If any part of this needs `explorer/web/static/app.css`, that is a change request, not an edit.

**Item 4 -- tests in `tests/catalog/`.** At minimum: a test that FAILS before your item-1 fix, driving the exact `doc_type=ANL` + `lifecycle_state` combination and asserting the control is rendered and individually clearable; a test that a complete abstract renders with no trailing ellipsis and a truncated one does with; and whatever you can assert about item 3 without a browser (a template/CSS assertion is legitimate here, but label it as static and do not describe it as behavioural evidence -- L2 is the layer that renders).

**In "Result"** state the module round consumed (**catalog round 2 of 4**) plainly, and give a per-item `landed | not landed` line.

**In "Unresolved uncertainty"** state whether any OTHER filter or control on the catalog can go into force while invisible -- item 1 may be one instance of a class -- with the evidence for your answer. The round-6 lesson, twice over, was that a finding named in one place is usually a population.

Write the report at `docs/rounds/R09_catalog.report.md`.
