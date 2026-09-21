# RHACO-HND-20260903-001 | Corpus Explorer Autonomous Build — Dispatch Hand (M0 completion, harness execution, terminal-state handback)

*Reno High-Altitude Cosmic Ray Observatory (RHACO) · 5,050 ft ASL · 39°N*
*RadiaCode RC-110-003225 · CsI(Tl) · 30 mm Pb walls / 40 mm Pb lid · sealed castle*

| Field | Value |
|---|---|
| Document type | HND (Class C — gated multi-part execution) |
| Parent campaign | RHACO-CMP-20260903-001, Milestones 0–2 |
| Governing instrument | `PROMPT.md` in the workspace repo — the frozen autonomous build prompt; this hand supplies the parameters the prompt leaves undesignated and adds nothing to its execution loop |
| Governing subagent rule | RHACO_Subagent_Pattern_Application_Guide_v1_3 (D-13; cut by RHACO-CHG-20260903-001 — §0 gates 2–3) |
| Execution route | `ops` |
| execution_mode | sequential-rounds (resumable at builder-round boundaries via `build_state.json`; HND Spec v1.1 §5.13) |
| Target | Claude Code, observatory PC |
| Status | READY |
| Author | Kris E. Granholm, Director, RHACO |
| Date | 2026-09-03 UTC |
| Naming convention | v1.17 · Style RSG v1.9 · Schema Card YAML v1.9 |

Route note. Every RHACO-tree write-target of this hand is under `working\`
(the handback and resumption notes). The build's own outputs land in a
separate repository outside the routed tree, and the CMP §8 entries this hand
earns ride the next docs hand, not this one — so the full RHACO-side target
set is operational one-shot output and the route is `ops`, on the
HND-20260825-002 precedent. The workspace repository is declared out-of-tree
in §2 and is not a route input.

## §0 Pre-flight verification (BLOCKING — full-file reads; halt on any mismatch; write `working\preflight_findings_HND-20260903-001.md`)

### §0.1 Instruments and governance (BLOCKING)

1. **Charter.** `docs\reports\RHACO-CMP-20260903-001_Corpus_Explorer_Autonomous_Build_Harness.md`
   sha256 `c1250711f961dfaacbd265e03d9c6541c0b5bfa39ecb0b57fcfa5ed22c285d7b`
   (15,028 B), or a successor whose diff is §8-append-only (verify, re-pin,
   record). Card `lifecycle_state` OPEN or ACTIVE.
2. **CHG-20260903-001** sha256
   `6a6fdbb5831bfd5cda2362da8341126f4ba4d84027bc32b9afca2beb645d14b0`
   (9,773 B) — **executed**: body Status `Baseline`. If still `Filed`, execute
   it first under `/ho` (route `docs`, its own commit), then resume this §0.
3. **Guide v1.3** present at `docs\reference\RHACO_Subagent_Pattern_Application_Guide_v1_3.md`
   with D-13 (grep `D-13 Model-tier declaration`) and the §6 `model` /
   `effort` / `tier_escalation` lines; v1.2 card `Superseded`. Pin v1.3
   full-file sha256 in the findings file.
4. **Retrieval dispositions of record unchanged.** `RHACO-ANL-20260712-001`
   sha256 `78891a81f2ba581f761f8cddcc82f561391671e6680d19c0515d07431ef6af87`;
   `RHACO-CMP-20260628-001` card `lifecycle_state: CLOSED`. If either has
   moved, halt: the prompt's own §6 rule (current ratified evidence
   supersedes prompt text) is a Director disposition, not this hand's.
5. **Substrate pins.** `rhaco\RHACO_corpus_index.py` full-file sha256 recorded
   (118,123 B expected; `rhaco\` is a path entry, not a package — no
   `__init__.py` on disk, confirmed 2026-09-03). `tools\RHACO_tool_catalog_librarian.py`
   sha256 recorded, `LIBRARIAN_VERSION` = 1.19 expected. `C:\RHACO\index\corpus_index.db`
   sha256 + mtime recorded (the criterion-6 open pin). Gold sets present:
   `working\eval\gold_queries.yaml` and `working\eval\gold_queries_v1_2.yaml`,
   sha256 recorded.
6. **Repo state.** `main` = `origin/main` = `32195e1` or descendant;
   `git status --porcelain` shows no tracked modifications; untracked set is
   exactly the CMP-20260903-001 pair, the CHG-20260903-001 pair (if not yet
   committed by gate 2), and this hand's pair. Anything else: halt.

### §0.2 Workspace and environment (BLOCKING unless marked)

7. **Workspace repo** exists at `C:\highsierralabs\RHACO_Corpus_Explorer\`,
   is a git repository with a private `origin` under `highsierralabs`,
   clean tree, and is **not** under `C:\highsierralabs\RHACO\` or `C:\RHACO\`.
   (Director act; Code verifies, never creates.)
8. **Prompt and rationale landed** by the Director at the workspace root as
   `PROMPT.md` and `RATIONALE.md`. Record full-file sha256 + byte length of
   each as the **pins of record**. Chat-side provenance:
   `dd75dd2ebf6a641bd223acf47289e0f3dd5b5b70c2b506b70d0c986cded98d0d`
   (28,665 B) and `3070c961b08aa90bdfc6da0d87b806f3e97b98f95fba032d3f6617506d372a6b`
   (26,151 B). A byte-length delta equal to the file's line count is
   CRLF normalization — record and proceed; any other delta: halt. Content
   sanity: `PROMPT.md` line 1 is `# RHACO Corpus Explorer — Autonomous Build Prompt`
   and its last non-empty line is `Start now.`
9. **Claude Code identity and surfaces — explicit values, never "default."**
   Record `claude --version`; the client-reported session model string;
   effort and thinking configuration. Verify LIVE: (a) the per-subagent
   model-pin surface exists in this release and how it is expressed (agent
   definition `model` field, dispatch-time parameter, or both) — record the
   exact mechanism; (b) `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` and
   `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` are honored (set 1 and 3, spawn a
   trivial read-only probe strand, confirm a nested spawn is refused and a
   fourth concurrent is queued); (c) the three tier models resolve to
   client-reported identifiers — record the strings. Any of (a)–(c)
   unverifiable: halt (CMP §4 blocker; D-13 last clause).
10. **Suppression not inherited.** No `--disallowed-tools` argument, no
    settings-scope tool suppression, no session hook that removes
    `Task`/`Agent`-class tools. Verify by listing the tool surface at session
    open; record.
11. **WAN / provisioning** (BLOCKING): in the workspace, in a fresh venv on
    the Anaconda interpreter (`C:\Users\kgran\anaconda3\python.exe -m venv`),
    `pip install fastapi uvicorn jinja2 playwright pytest` succeeds and
    `playwright install chromium` completes. Failure: halt (INC-20260827-001
    gate not cleared for this hand).
12. **RHACO import path** (BLOCKING): from the venv, with
    `sys.path.insert(0, r"C:\RHACO\rhaco")` and `r"C:\RHACO\tools"`,
    `import RHACO_corpus_index` and `import RHACO_tool_catalog_librarian`
    succeed; `RHACO_corpus_index.DEFAULT_DB` equals
    `C:\RHACO\index\corpus_index.db`. `[VERIFY: whether `connect()` accepts a
    db path argument and whether `BODY_SCAN_ROOT` / `DEFAULT_DB` can be
    redirected without editing the module — via read_corpus on the module's
    `def connect` and constants block. The fixture strategy in §2 item F
    depends on the answer; record it in `CONSTRAINTS.md`.]`
13. **Vector channel state** (ANNOTATABLE): with the venv, call
    `RHACO_corpus_index.search_hybrid("firmware transfer function", top_k=5)`
    and record whether the engine reports vec available or `VecUnavailable`
    (Ollama reachability). Either is a valid starting state; the build's
    diagnostics must report whichever it is. Then set
    `RHACO_CORPUS_DISABLE_VEC=1` in a child process and confirm the typed
    degradation fires — this is the W7 mechanism and must be proven before
    W7 is exercised.

### §0.3 Device safety (BLOCKING)

14. Confirm the production logger and sidecars are running (`observatory_status`
    or psutil by cmdline) and record their PIDs. This hand and every strand
    it spawns leave them untouched (§3 D-12 text). No strand is dispatched
    before the findings file records this gate.

## §1 Part A — M0 completion (single-pass, before any builder round)

1. Write `working\HND-20260903-001_report.md` with the §0 findings summary
   and the pins-of-record block (charter, CHG, Guide v1.3, substrate,
   `PROMPT.md`, `RATIONALE.md`, DB open pin, gold sets, Claude Code identity,
   surface-verification results, tier-model strings).
2. In the workspace repo, commit `PROMPT.md` and `RATIONALE.md` unchanged as
   the first build commit (subject: `Land frozen build prompt and rationale`;
   the workspace repo carries no RHACO commit-msg hook). The prompt is now
   the instrument: **any later edit to `PROMPT.md` is a halt**, never a
   commit.
3. Copy this hand's §2 dispatch-parameter block verbatim into the workspace
   as `DISPATCH_PARAMETERS.md` and commit it. The orchestrator reads
   `DISPATCH_PARAMETERS.md` first, then `PROMPT.md`; the prompt's "Start now"
   executes under those parameters.

M0 is complete when items 1–3 are done and the report records it. The CMP
§8 M0-closure entry is queued to the next docs hand (§6).

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
- **C. Index write prohibition (mechanical form of prompt §11).** The build
  never calls `reindex_full`, `reindex_pair`, `reindex_fts_pair`,
  `reindex_vec`, or `emit_gold_queries`, and never opens
  `corpus_index.db` outside the module's own `connect`. L1 static check:
  a grep over the workspace for those five names outside `CONSTRAINTS.md`
  / `docs/` returns zero hits; recorded per round in `build_state.json`.
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
- **F. Fixture substrate.** Fixture corpus and fixture index live under the
  workspace (`fixtures/`). Build them through the module's own functions
  against a fixture docs root and a fixture db path per the §0 item 12
  answer. If the module cannot be pointed at a fixture root without editing
  it, the fixture index is built by a fixture-only script that monkeypatches
  the module's path constants in-process (never on disk), and this is
  recorded in `CONSTRAINTS.md` as a user-invisible constraint. Editing the
  module is `BLOCKED` (prompt §11).
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
  gate, recorded in `build_state.json` as `tier_escalation`. Caps:
  `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1`,
  `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS=3`, set in the session environment
  before the first spawn. Every dispatch record in `build_state.json`
  carries `role, model (client-reported), effort, pattern_primary,
  agent_type, execution_mode, tier_escalation`. A dispatch without all seven
  is a governance defect the closeout must report.
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

## §3 Part B — Harness execution

Read `DISPATCH_PARAMETERS.md`, then `PROMPT.md`, then execute the prompt from
"Start now" under its own execution loop (§14), budgets (28 total builder
rounds, 4 per module, 2-round convergence window), and terminal-state rules
(§12). This hand adds no step to that loop. Halts the prompt does not define
follow HND Spec v1.1 §5.13: no retry, no rollback, no silent continuation.

Standing halts specific to this hand: any need to edit `PROMPT.md`; any
proposal to change `RHACO_corpus_index.py` retrieval semantics or to reindex
the live index (prompt §11 — `BLOCKED`); any strand prompt dispatched without
the §2 L text; any spawn outside the §2 I tier map; any write outside the
workspace; a Claude Code version or session-model change between sessions.

## §4 Part C — Terminal state and handback

On PASS / BOUNDED_FAIL / BLOCKED / INVALID: complete §2 N; commit the
workspace; write the handback's final status table; report per §7. The
harness-evaluation ANL (CMP criterion 4) is chat-authored downstream from the
handback and the workspace record — this hand writes no ANL.

## §5 Invariants

No write outside `C:\highsierralabs\RHACO_Corpus_Explorer\` except the
handback and findings files under `C:\RHACO\working\`; no RHACO-repo commit;
no edit to `PROMPT.md` or `RATIONALE.md` after §1 item 2; no call to the five
index-writing functions; no process other than the workspace interpreter; no
device transport; no `C:\RHACO\data\` access; no strand without D-12 text,
tier, and caps; no LLM in the explorer's normal operating path; the frozen
retrieval dispositions unaltered; nothing force-pushed, amended, or rewritten
in either repository.

## §6 Outputs, commits, and report

Workspace repo: the build commits autonomously per prompt §11, on module
branches merged to `main` by the integrator; `PROMPT.md`, `RATIONALE.md`,
`DISPATCH_PARAMETERS.md` land first. RHACO repo: **no commits by this hand.**
This hand's doc+card pair, the CMP-20260903-001 §8 entries (M0 closure; M1
Wave-1/probe-qualification closure; M2 terminal state), and the Guide v1.3
§9 QUEUED-line resolution ride the next docs hand. Handback:
`C:\RHACO\working\HND-20260903-001_report.md` — §0 findings summary, pins of
record, per-part status table, resumption log, dispatch record table, D-12
application note, terminal state with the prompt's closeout verbatim,
criterion-6 close pins.

## §7 Reporting discipline

Substantive output to `C:\RHACO\working\HND-20260903-001_report.md`. CLI
reply at each session end: path + per-part status + current round / budget
consumed + terminal state if reached + any halt. A halt surfaces the trigger
and the smallest discriminating next check; it proposes no fix.

## §8 Acceptance criteria

1. §0 discharged with the findings file written; every pin recorded from a
   full-file read; gates 9(a)–(c), 11, 12, 13 evidenced with command output.
2. M0 complete: `PROMPT.md` and `RATIONALE.md` pinned on disk and committed
   unchanged; `DISPATCH_PARAMETERS.md` byte-identical to §2 of this hand.
3. Prompt §1 artifacts (`CONSTRAINTS.md`, `ARCHITECTURE.md`) exist before any
   feature code, and `SCOPE.md` exists from the first build commit after
   them.
4. Probe qualification complete before any product claim: known-good and all
   five known-bad classes under `docs/probe-qualification/`, each with the
   probe's JSON observation showing detection (CMP criterion 3).
5. `docs/LAYERS.md` names the shared dependencies (module, live db, browser
   path, gold set, filesystem) and claims no independence among L2–L4.
6. Every dispatch in `build_state.json` carries the seven governance fields;
   models are client-reported strings; zero spawns outside the tier map;
   zero nested spawns; escalations, if any, logged with the two-failed-round
   evidence (CMP criterion 5).
7. Every strand prompt archived under `docs/rounds/` begins with the §2 L
   text verbatim.
8. The L1 index-write grep is zero-hit in every round record.
9. Gold v1.1 compatibility computed by the L4 oracle from module-returned
   ids: ≥ 0.700 aggregate, or a `SCOPE.md` row evidencing the regression and
   its cause; never silent.
10. Terminal state declared exactly once, with the prompt's closeout verbatim
    in the handback; BOUNDED_FAIL, BLOCKED, and INVALID reported with the
    prompt's §12 fields, never upgraded.
11. Criterion-6 close pins recorded and clean: no RHACO commit, module sha
    unchanged, `docs\` unchanged, db change (if any) reconciled to a
    librarian reindex.
12. §5 invariants held throughout; the D-12 application note and the #3
    disposition evidence pointer present in the handback.

## §9 Out of scope

The harness-evaluation ANL (chat, M3); the Pattern #3 promotion ruling
(Director, M3); any Guide, prompt, or harness revision; any edit to
`RHACO_corpus_index.py`, the librarian, the live index, or the corpus; V1
exclusions per prompt §9; the CMP §8 entries and this pair's commit (next
docs hand); any external or public deployment of the explorer; any second
build run.

## §10 Cross-references

RHACO-CMP-20260903-001 (parent; §3 criteria 1–6; §4 governance table) ·
RHACO-CHG-20260903-001 (Guide v1.3 cut; §0 gate 2) ·
RHACO_Subagent_Pattern_Application_Guide_v1_3 (D-1, D-3, D-4, D-9, D-12,
D-13; §6 handback schema) · RHACO-ANL-20260712-001 (dispositions of record) ·
RHACO-CHG-20260712-002 (M4 default flip) · RHACO-CMP-20260628-001 (CLOSED;
substrate campaign) · RHACO-CMP-20260624-001 (index) · RHACO-HND-20260825-002
(structural precedent: frozen-instrument gated multi-part hand, `ops` route,
resumable rounds) · RHACO-CMP-20260815-002 (model-identity ruling; caps) ·
RHACO-CMP-20260815-001 (live surface verification) · RHACO-INC-20260827-001
(WAN gate) · RHACO_HND_Specification_v1_1 + A1 (§5.13 halt/resume; §5.14
authoring verification) · RHACO_Measurement_Philosophy_v1_4_1.

---

*Reno High-Altitude Cosmic Ray Observatory (RHACO) | Kris E. Granholm, Director*
