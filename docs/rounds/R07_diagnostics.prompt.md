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
Dispatch record (RHACO-HND-20260903-001 section 2 I as amended by A1.3): strand_id S8-B13; role: module builder (diagnostics), S2 path-order conformance round; tier: mid; model requested: Claude Sonnet 5; agent_type: general-purpose (write-scoped to the worktree below); pattern_primary: #3 candidate (worktree-isolated builder); execution_mode: concurrent (round 6 = three builders, the A1.3 cap); tier_escalation: none; orchestrator_model: claude-opus-5[1m] (Director ruling MOD-1). Round 6 of the RHACO Corpus Explorer autonomous build; diagnostics module round 2 of 4 -- this strand consumes one builder round of the 28.

Your worktree: C:\highsierralabs\RHACO_Corpus_Explorer\.worktrees\diagnostics -- a git worktree of the workspace repository on branch build/diagnostics, checked out at the tip of `main` at dispatch. That tip is a descendant of f29bcc97f4ba7de455fa32f3591e5d3ccf837976 which adds this prompt file itself, so this prompt cannot name its own commit: your first git act is `git rev-parse HEAD` -- RECORD what it returns and report it as your base, do not match it against a literal here. What you can verify is that your HEAD contains f29bcc9 (`git merge-base --is-ancestor f29bcc97f4ba7de455fa32f3591e5d3ccf837976 HEAD`); if it does not, STOP and return status BLOCKED. (your round-1 work is merged there, along with five later rounds; 262 tests pass, tests/diagnostics 25 of them). Your interpreter: C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe (the workspace's own venv: Python 3.13; fastapi, uvicorn, jinja2, playwright + chromium, pytest, httpx, pyyaml, sqlite-vec, markdown-it-py, mdit-py-plugins, ruff). Run every command with the worktree as the current directory, e.g. `cd C:\highsierralabs\RHACO_Corpus_Explorer\.worktrees\diagnostics; C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m pytest tests/diagnostics -q`.

Working rules:
1. Write only inside your worktree, and there only under your owned paths: `explorer/diagnostics/**` and `tests/diagnostics/**`; plus your round report `docs/rounds/R07_diagnostics.report.md`. Do not modify `explorer/app.py`, `explorer/config.py`, `explorer/models.py`, `explorer/faults.py`, `explorer/corpus_adapter/**`, `explorer/catalog/**`, `explorer/search/**`, `explorer/reader/**`, `explorer/lineage/**`, `explorer/web/**`, `tools/**`, `fixtures/**`, `requirements.txt`, `ruff.toml`, `.gitignore`, `PROMPT.md`, `RATIONALE.md`, `DISPATCH_PARAMETERS.md`, `CONSTRAINTS.md`, `ARCHITECTURE.md`, `SCOPE.md`, `build_state.json`, `docs/LAYERS.md`, `docs/REFERENCE.md`, `docs/probe-qualification/**`, or any other module's directory or tests. If you need a change there, record it in a "Change requests" section and code against the current contract. `explorer/corpus_adapter/**` and `explorer/lineage/**` are being edited by concurrent strands this round: read `paths.py` for its rule, but do not depend on any other current text there and do not treat it as stable.
2. Outside the worktree you may only READ: C:\RHACO\docs\** (the corpus); C:\RHACO\index\corpus_index.db, and only through `RHACO_corpus_index.connect()`, never opened any other way; C:\RHACO\rhaco\RHACO_corpus_index.py; C:\RHACO\tools\RHACO_tool_catalog_librarian.py; C:\RHACO\working\eval\gold_queries.yaml and gold_queries_v1_2.yaml. Nothing else under C:\RHACO\ or C:\highsierralabs\RHACO\ (C:\RHACO is a junction to C:\highsierralabs\RHACO -- one tree, both spellings out of bounds beyond that list). **Never write to the live index**; never edit the RHACO module; never call the five index-writing functions named in CONSTRAINTS.md S6 (your L1 check greps for them).
3. Processes: only the venv interpreter running workspace code (pytest, ruff, your own scripts). No server process at all: tests use `fastapi.testclient.TestClient` in-process, or call the service directly. Never launch uvicorn -- the probe is the only sanctioned launcher. No `run_in_background`, no detached processes, no sleep-and-poll loops.
4. Git: commit on your branch in small increments with imperative ASCII subjects; `git add` specific paths only, never -A; no amend, no rebase, no push, no checkout of another branch, no merge. Leave the worktree clean when you finish and report `git rev-parse HEAD`.
5. Gate before you finish: (a) `...\.venv\Scripts\python.exe -m ruff check explorer tools tests --output-format concise` clean; (b) `...\.venv\Scripts\python.exe -m pytest tests/diagnostics -q` green, then `...\.venv\Scripts\python.exe -m pytest tests -q` green as well, because a `sys.path` change can affect any module that imports the RHACO modules; (c) `...\.venv\Scripts\python.exe tools/l1_index_write_check.py` PASS. Paste the exact commands and their output tails.
6. Evidence discipline: cite file paths and line numbers; every "tested" claim names the test; anything not verified is UNVERIFIED. ASCII-only stdout in any script you write; UTF-8 with LF line endings.
7. Timestamps and identity: run `(Get-Date).ToUniversalTime().ToString("o")` as your FIRST tool call and again when you finish; copy the sentence from your own system prompt that names your model.
8. Return your result through the StructuredOutput tool: the header fields by name, and write your round report to `docs/rounds/R07_diagnostics.report.md` with the sections Header, Change, Evidence, Material alternatives, Decisions, Result, Unresolved uncertainty, Change requests, Assumptions.

Read first, inside your worktree, in this order: `explorer/diagnostics/service.py` lines 70-95 -- `_rerank_artifact_present`, the function that owns the defect; `explorer/corpus_adapter/paths.py` `ensure_rhaco_importable` (lines 30-40) -- the rule of record and its stated reason, in the module that defines `RHACO_PATH_ENTRIES`; CONSTRAINTS.md S2 (the import form) and O17 (the licence under which diagnostics imports the module at all); ARCHITECTURE.md 4.1's NEW licensed-importer table, which now names your file explicitly. Then the task.

Task B13 -- make the diagnostics import path-order conformant with S2. **This is the whole of your scope. Nothing else in this round.**

**The finding, precisely.** The released sealed audit's SA-3 has two halves. The first -- that ARCHITECTURE 4.1 and the `corpus_adapter` package docstring falsely claimed `adapter.py` was the only importer in the workspace -- was an integrator text edit and landed at commit `f29bcc9`; your import is licensed under O17 and is not the defect. The second half is code, in a file you own, and is this round:

`explorer/diagnostics/service.py` line 83 does

    sys.path.insert(0, entry)

while `explorer/corpus_adapter/paths.py` line 37 does

    sys.path.append(entry)

and states the rule in its own docstring: "Appended, never inserted at position 0, so workspace code always shadows a same-named module first." That is the S2 import form. Inserting the RHACO directories at the FRONT of `sys.path` gives `C:\RHACO\rhaco` and `C:\RHACO\tools` priority over the workspace's own modules for every subsequent import in the process -- so a name collision between a RHACO module and a workspace module would resolve, silently, to the RHACO one. The diagnostics page is loaded on the production path, so this is not a test-only concern.

No layer of this harness detected it: L1 greps only for the five index-writing names, no test asserts anything about `sys.path` order, and critic round 1 did not test the claim. It was found by an external reader.

Deliver:

1. **`explorer/diagnostics/service.py`**: make `_rerank_artifact_present`'s path handling conform to the S2 rule. The obvious and probably right move is to call `explorer.corpus_adapter.paths.ensure_rhaco_importable()` rather than reimplementing the loop -- one rule, one implementation, and the rule then cannot drift again. Consider it first and say in "Decisions" whether you took it and why. If you decide an import of the adapter package from diagnostics is unwanted coupling, the fallback is a local `sys.path.append` that matches the rule exactly; either is acceptable, but the choice must be reasoned rather than defaulted, and if you keep a local loop, say why one rule now lives in two places and what keeps them in step. Update the function's docstring so it states the path-order rule it now follows.
2. **A test in `tests/diagnostics/`** that would have failed before this round. Assert the ORDER, not merely that the entries are present: after `_rerank_artifact_present()` runs against a `sys.path` you control in the test (save and restore it), the RHACO entries must not precede workspace entries that were already there. A test that only checks membership passes on the defective code and is worth nothing here. Say in the report exactly which assertion is the one that distinguishes the two implementations.
3. **Idempotence, kept.** Both the current code and `ensure_rhaco_importable` guard with `if entry not in sys.path`. Whatever you do must remain safe to call repeatedly -- the diagnostics page can be loaded many times in one process -- and a test should show that a second call adds nothing.
4. **In "Result"** state the module round consumed (**diagnostics round 2 of 4**) plainly, and state that the round's scope was the path-order fix only.
5. **In "Unresolved uncertainty"** state whether any other file in the workspace mutates `sys.path` in a non-conformant way, with the command that establishes your answer (a grep for `sys.path` across the tree is the obvious one). Report what you find; do not fix anything outside your owned paths, file it as a change request instead.

**Explicitly out of scope this round, by Director ruling.** Critic round 1's ranked issue 10 -- the live freshness scan's duration is never measured -- is a real diagnostics finding and is ACCEPTED by the build, but it is **not** in this round. Do not implement it, and do not fold it in as an easy extra. Diagnostics has two rounds left after this one and it is queued for one of them. Also out of scope: SA-5 (ARCHITECTURE 4.6 naming `last_run.json` where the implementation reads `runs/*/run_summary.json`) is an ARCHITECTURE text fix, integrator-owned; note it if you like, change nothing.

The scope of this round is deliberately narrow. A small, complete, well-tested change that closes a real conformance defect is the whole deliverable, and padding it would make the round harder to accept, not easier.

Write the report at `docs/rounds/R07_diagnostics.report.md`.
