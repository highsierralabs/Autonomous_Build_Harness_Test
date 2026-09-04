## §2 Dispatch parameters (the prompt's undesignated inputs — verbatim into `DISPATCH_PARAMETERS.md`)

**Precedence.** `PROMPT.md` governs execution: its goal, constraints, budgets,
module contracts, probe qualification, layers, critic, acceptance workflows,
scope rules, evidence artifacts, authority boundary, terminal states,
invariants, and execution loop are binding as written. This block supplies
only what the prompt leaves undesignated. Where the two appear to conflict,
the orchestrator halts in `BLOCKED` and reports the conflict; it does not
resolve it.

- **A. Workspace.** The designated build workspace is the repository root
  `C:\highsierralabs\RHACO_Corpus_Explorer\`. All prompt-authorized
  autonomous file operations and commits are confined to it. It is the only
  tree the build may mutate.
- **B. RHACO read paths.** Read-only access is authorized to
  `C:\RHACO\docs\**` (the corpus), `C:\RHACO\index\corpus_index.db` (the
  derived index), `C:\RHACO\rhaco\RHACO_corpus_index.py`,
  `C:\RHACO\tools\RHACO_tool_catalog_librarian.py`, and
  `C:\RHACO\working\eval\gold_queries*.yaml`. Nothing else under `C:\RHACO\`
  or `C:\highsierralabs\RHACO\` is read or written; in particular
  `C:\RHACO\data\**` and every `rhaco\` module other than the corpus index
  are out of bounds. Import form: path entries `C:\RHACO\rhaco` and
  `C:\RHACO\tools`; `import RHACO_corpus_index`,
  `import RHACO_tool_catalog_librarian`. The module's hard-coded `C:\RHACO`
  paths resolve through the NTFS junction; do not rewrite them.
- **C. Index write prohibition (mechanical form of prompt §11).** the L1 static check greps the workspace for the five
  index-writing names outside `CONSTRAINTS.md` / `docs/` and allowlists
  exactly one file, `fixtures/build_fixture_index.py`; the check passes only
  when every hit is in that file. Any hit elsewhere is a defect recorded per
  round in `build_state.json`. `corpus_index.db` is never opened outside the
  module's own `connect`.
- **D. Standing retrieval state (prompt §6 `docs/REFERENCE.md` seed).**
  RHACO-ANL-20260712-001: flat `hybrid` Recall@10 0.700 aggregate on Gold
  v1.1 (default, flipped at M4 via CHG-20260712-002); `hybrid-rerank` 0.575
  FAIL, documented-FAIL batch mode (~26 min/query — never on an interactive
  path); `graph` 0.575, auxiliary lineage mode. `search_corpus`
  filter-routing: filters apply to lexical only.
- **E. Gold set and baseline for the objective gate.** Gold v1.1 =
  `C:\RHACO\working\eval\gold_queries.yaml` (40 rows). Gate: Recall@10
  through the adapter's hybrid path is not below 0.700 aggregate on the same
  40 rows, computed by the build's own L4 oracle script from the module's
  returned doc ids — a *compatibility* check that the adapter did not
  degrade the module's result, not a re-evaluation of the module. Gold
  v1.2 (`gold_queries_v1_2.yaml`) is available but has no accepted baseline
  of record; it may be profiled, never gated.
- **F. Fixture substrate.** fixture corpus and fixture index live under `fixtures/`.
  The fixture index is built only by `fixtures/build_fixture_index.py`, which
  (i) if the §0 item 12 answer is that `connect()` / the path constants accept
  a db path and docs root without editing the module, passes the fixture paths
  that way; otherwise monkeypatches the module's path constants in-process
  before any call, never on disk; (ii) in either case asserts before any write
  that the resolved db path is not `C:\RHACO\index\corpus_index.db` and lies
  under neither `C:\RHACO\` nor `C:\highsierralabs\RHACO\`, refusing to run
  otherwise; (iii) is recorded in `CONSTRAINTS.md`, with the monkeypatch case
  recorded as a user-invisible constraint. Editing the module remains `BLOCKED`
  (prompt §11).
- **G. W7 mechanism.** Semantic-channel disable = `RHACO_CORPUS_DISABLE_VEC=1`
  in the server's environment (typed `VecUnavailable`, degradation to
  identifier short-circuit + FTS5). Rerank disable =
  `RHACO_CORPUS_DISABLE_RERANK=1`. No other mechanism is sanctioned.
- **H. Freshness.** `freshness_check(scan)` takes a librarian scan; the
  adapter obtains the scan via the librarian's own walk function (read-only)
  and reports freshness from the module's return value. Freshness is
  reported, never acted on: the UI does not rebuild.
- **I. Subagent governance (D-13; Guide v1.3).** Tier map for this hand,
  product names; the handback records client-reported strings from §0.9(c):

  | Role | Tier | Model | Pattern / type |
  |---|---|---|---|
  | Orchestrator / integrator (prompt §4) | session | Claude Fable 5.1 (the session model) | main thread; all synthesis, all contract changes (D-1) |
  | Module builders (`corpus_adapter`, `catalog`, `search`, `reader`, `lineage`, `diagnostics`, `web`, `probe`) | mid | Claude Sonnet 5 | write-scoped; one worktree per builder; #3 candidate |
  | Critic (prompt §7) | judgment, ≠ builders | Claude Opus 5 | read-only (Explore); writes only under `docs/critique/` via the orchestrator |
  | Probe qualification runs, lint, fixture mechanics, L1 static checks | small | Claude Haiku 4.5 | read-only or fixture-scoped; #1 / #5 |
  | Prompt §1 inspection strands (constraints, schema, dispositions) | mid | Claude Sonnet 5 | read-only (Explore); #7 |

  Escalation one tier up only after two failed rounds on the same objective
  gate, recorded in `build_state.json` as `tier_escalation`. Caps. `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` and
  `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS=3` are set in the client environment
  before launch. Spawn depth 1 is structural (depth-1 strands carry no spawn
  tool). The concurrency cap of 3 (one wave) is hand-declared and
  orchestrator-enforced: the orchestrator dispatches no strand while three are
  live, and the environment variable is recorded in the handback as inert for
  the client version measured. Every dispatch record in `build_state.json`
  carries the seven governance fields (`role, model (client-reported), effort,
  pattern_primary, agent_type, execution_mode, tier_escalation`) plus
  `dispatched_utc` and `returned_utc`. The cap is audited post hoc from those
  intervals: any instant with four overlapping live strands is a
  `concurrency_exceedance`, a governance defect the closeout must report
  alongside any missing-field defect — never silently. Zero nested spawns
  remains structural.
- **J. Worktree isolation (#3 candidate).** Each builder runs in its own git
  worktree of the workspace repo on a module branch; the integrator merges
  to `main`. Two builders never share a worktree. Disposition evidence for
  the Guide's #3 question — merge conflicts, contract-change requests,
  invalidated evidence after merge — is recorded per wave in
  `docs/rounds/`.
- **K. D-3 satisfaction.** No background processes, no `run_in_background`.
  The probe (`tools/probe_corpus_explorer.py`) spawns the explorer server as
  a child of its own foreground process, waits on the readiness endpoint,
  runs presets, and tears the server down before exit. No other component
  launches the server.
- **L. D-12 text — carried verbatim at the top of every strand prompt,
  builders and critic included:**

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

  This narrows D-12(a) from "no process" to "workspace interpreter only,"
  which is the honest form for a software build on the observatory host;
  the narrowing is recorded in the handback as a D-12 application note.
- **M. Session resumption.** A session ends at a builder-round boundary. On
  ending: `build_state.json` is committed in the workspace; the handback
  gains a resumption note (session index, last completed round, next
  action, open halts). On re-entry: re-run §0 items 1, 5, 6, 7, 8 (pins),
  9 (identity — a model or version change is a halt: CMP §6 REVIEW
  trigger), 14; read `build_state.json`; resume at the recorded next action.
  Every resumption is a numbered entry in the handback.
- **N. Terminal-state obligations.** The prompt's closeout (§14 step 20) is
  copied verbatim into the handback with the declared state. The handback
  also records: the criterion-6 close pins (RHACO `git log` since §0.6 shows
  no build commits; `RHACO_corpus_index.py` sha unchanged; `git status` in
  RHACO shows no change under `docs\`; `corpus_index.db` sha/mtime at close,
  with any change reconciled against `docs\logs\catalog_librarian_validation.log`
  reindex entries — a change not explained by a librarian reindex is a
  criterion-6 failure); the D-12 application note; the #3 disposition
  evidence pointer; the full dispatch record table from `build_state.json`.
