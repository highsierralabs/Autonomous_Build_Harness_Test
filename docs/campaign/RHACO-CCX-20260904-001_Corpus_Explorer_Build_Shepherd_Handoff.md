# RHACO-CCX-20260904-001 · Corpus Explorer Build Shepherd — Session Handoff to the Session-4-Onward Shepherding Chat

*Reno High-Altitude Cosmic Ray Observatory (RHACO) · 5,050 ft ASL · 39°N*
*RadiaCode RC-110-003225 · CsI(Tl) · 30 mm Pb walls / 40 mm Pb lid · sealed castle*

| Field | Value |
|---|---|
| Document type | CCX — session handoff (per CCX Specification v1.1) |
| Session scope | Opened against RHACO-CCX-20260903-001 §4: sequencing guard, CHG-20260903-001 dispatch and closure, HND-20260903-001 dispatch and §0 halt disposition. Closed at the HND's first builder-round boundary (session 3 of the hand) with Amendment A1 filed and two Director rulings recorded. |
| Session output handed forward | RHACO-HND-20260903-001 Amendment A1 (filed, committed, pushed); the hand's live state at session 3 close; a rulings ledger (O-1, AC-4); the session-4 launch procedure |
| Receiving instance | Primary: shepherd HND-20260903-001 sessions 4 → terminal state, disposition halts, hold the rulings ledger, then author A2 and the docs tail. Secondary: M3 ANL only after a terminal state exists. |
| Author | Kris E. Granholm, Director, Reno High-Altitude Cosmic Ray Observatory (RHACO) |
| Date | 2026-09-04 UTC |
| Status | Filed; closes the 2026-09-03/04 CHG-execution, HND-dispatch, and session-1–3 shepherding session |

## §0 Pre-flight verification

Before reading the rest of this CCX, the executing instance verifies on-disk:

1. `server_info`: server 0.22.0, librarian 1.19, NC 1.17, `repo_head` = `3b860bf` **or a descendant** (Code commits the CCX pair and later docs-tail items on top). Record the observed head.
2. `validate_catalog`: broken=0, errors=0. At close: 1442 cards (this CCX pair makes 1444), orphans 3, cwp 128, `unresolved_reference` 413, `stale_version_pin` 1 (CLAUDE.md line 73, R-1, expected until the docs tail).
3. Full-file pins (Code-verified unless marked chat-verified):
   - `docs\handoffs\RHACO-HND-20260903-001_Corpus_Explorer_Autonomous_Build_Dispatch_Amendment_A1_Cap_Rehome_And_Session_2_Findings.md` — sha256 `167771c75575ceef2d07e21a9fbfb6f00a24776ca619514cc9b9a216414be99a`, 9,698 B (chat-verified)
   - parent HND `…Build_Dispatch.md` — `ed01fa5412238767a55f30108844295a10bedc0ab6d1f7e5aca4c373c206ff6f`, 23,306 B (chat-verified)
   - `docs\reference\RHACO_Subagent_Pattern_Application_Guide_v1_3.md` — `fdd1c5f68ecfbd3b613370a3d9abfef1c2c2ab3277d2f48902d1ed5a7aac65a9`, 19,842 B (chat-verified); v1.2 card `Superseded`
   - `docs\reports\RHACO-CHG-20260903-001_….md` — body `Baseline`, card `Baseline` (chat-verified)
   - `docs\reports\RHACO-CMP-20260903-001_….md` — `c7104f1a…`, 15,216 B post-§8-M0-line (Code-reported; re-pin)
4. Workspace (MCP-invisible; verify via Code at re-entry): `C:\highsierralabs\RHACO_Corpus_Explorer\` on `main` = `origin/main` = `62685da`, 20 commits, tree clean; `DISPATCH_PARAMETERS.md` sha256 `f6e9cd3ee7e7b23bcc9057f402ed33210f738d677a9b3e26cf752ec713edad51`, 9,730 B.
5. Criterion-6 (live index untouched by the build) reconciliation sources of record: chat-side MCP writes (`docs\logs\mcp_validate.log`) and closeout-gate librarian runs (production validation log). **This CCX's own filing is such a write**; its timestamp is in `mcp_validate.log` and Code reconciles it at session-4 re-entry. Open pin at session 3 close: `274c1e96…`, 115,093,504 B, 02:10:08Z (Code-reported).
6. Untracked in the RHACO tree at filing: this CCX pair only. Session 4 takes its Rule-2 commit before HND §0 item 6 reads the tree (§4.1).

If any verification fails, surface the discrepancy and pause.

## 1  Session summary

Resumed CCX-20260903-001. Sequencing guard: four Rule-2 commits (`2d8258b` CMP, `4fc46ea` CHG, `b9ed835` HND, `376f5d6` CCX). CHG-20260903-001 executed under `/ho` in `0243874`: Guide v1.3 cut (D-13, handback schema, count line `Thirteen` ratified as deviation D-1 on the v1.1→v1.2 precedent), v1.2 card Superseded, CMP §8 M0 line, CHG to Baseline; all AC PASS. Push ratified red, attribution-closed (three inherited reds, delta 0/0/0), `main` → `origin/main` at `0243874`.

HND-20260903-001 session 1: §0 halt at item 7 (workspace not a git repo). Director created `highsierralabs/RHACO_Corpus_Explorer` (private) and initialised the local repo with `autocrlf false`, remote empty. Session 2: §0 halt at item 9(b) — concurrency cap present in the client environment, not enforced by Claude Code 2.1.260; spawn depth holds structurally. Director ruled amend-not-hold; Amendment A1 drafted and filed (delta clean, 1442 cards), committed `3b860bf`, pushed. Session 3: §0 passes as amended; item 12 VERIFY answered (A1.5 branch (i) for db path, in-process monkeypatch for `BODY_SCAN_ROOT`); M0 complete (`e9c9539`, `8da0712`); Part B rounds 0–1 built, merged, integrated; first workspace push per ruling O-1. Two rulings recorded in handback section D: O-1 (workspace push cadence) and AC-4 (recall criterion read differentially). Chat MCP writes held silent from A1 filing to this CCX.

## 2  Campaign state at session close

**CMP-20260903-001** (Corpus Explorer Autonomous Build Harness): OPEN; M0 CLOSED on disk in the workspace (2026-09-04T02:24:07Z) but its §8 line and the M1 line are docs-tail items not yet written. M1 (Part B) in progress: rounds consumed 3 of 28, wave 1 (I1–I4 inspection) returned, wave 2 (catalog, search, reader) next as round 2 from `62685da`. §6 REVIEW triggers: none fired — the 9(b) result is a mechanism finding, not a cap violation. Criterion 5 escalations: none. Criterion 6 open pin per §0.5.

**CMP-20260808-001**: untouched. Its act (a) (`regression_baseline.json` schema v1 cannot carry the INC-20260829-001 §7 exception) is why the RHACO closeout gate cannot go green from this arc; every push this session was attribution-closed red.

**CMP-20260815-002**: untouched; scoring hand still deferred behind INC-20260827-001; A8/A10 host residuals recorded (auto-update pin still set, SessionStart hook still excised — restoration is a pilot-close item, and the hook can no longer be copy-back restored).

## 3  Data artifacts available for the receiving chat

| Artifact | Location | Use |
|---|---|---|
| HND-20260903-001 + A1 | `docs\handoffs\` | The hand and its live patches; §2 as amended is what `DISPATCH_PARAMETERS.md` carries |
| Handback | `C:\RHACO\working\HND-20260903-001_report.md` (gitignored) | Section A pushed-red record; section D rulings ledger and resumption entries 1–3; J.4 assembly procedure; J.5 index reconciliations |
| Findings file | `C:\RHACO\working\preflight_findings_HND-20260903-001.md` (gitignored) | §0 command output per item, 18-strand probe record, R-A8/R-A10 |
| Workspace | `C:\highsierralabs\RHACO_Corpus_Explorer\` (`origin` private) | `PROMPT.md`, `RATIONALE.md`, `DISPATCH_PARAMETERS.md`, `build_state.json`, `docs/rounds/`, `docs/REFERENCE.md`, `CONSTRAINTS.md` (O3 = monkeypatch constraint), `ARCHITECTURE.md`, `SCOPE.md` (row 27), `fixtures/build_fixture_index.py`, `preflight\` (evidence) |
| Guide v1.3 | `docs\reference\` | D-13 tier map and caps rule; §9 QUEUED line still to resolve in the docs tail |
| Auditor attribution tables | handback section A (33 rows) + session-3 entry (+2) | Become §2 of the re-seed CHG |
| MCP validate log | `docs\logs\mcp_validate.log` | Criterion-6 reconciliation of chat-side writes (A1 at 01:50:53Z; this CCX at its filing timestamp) |

## 4  Receiving-chat scope statement

**Primary — shepherd HND-20260903-001 to a terminal state.** Sessions 4 → N: launch Code per §4.1, receive handbacks at halts and builder-round boundaries, disposition per the hand's §3 standing halts and §2 M. Hold the rulings ledger (O-1, AC-4, and any new ruling) in handback section D; a ruling that changes an acceptance criterion or a §2 parameter goes into A2 at terminal state — do not file per-ruling amendments. Author no ANL until `build_state.json` declares a terminal state. Make no MCP writes during the build; if one is unavoidable, timestamp it to Code as a criterion-6 source.

**At terminal state, in order:** (1) A2 — AC-4 differential reading plus whatever accumulated; (2) docs tail as one hand: CMP §8 lines for M0 close, M1 progress/close, terminal state; Guide v1.3 §9 QUEUED line resolution; CLAUDE.md line 73 pin → v1.3 (clears `stale_version_pin`); the auditor re-seed CHG carrying the attribution tables (route per the baseline file's home; `--write-baseline` is its own ratified act); INC-20260830-001 §5 items 1–2 placed with CMP-20260808-001 or filed here, Director's call; (3) M3 ANL (harness effectiveness), carrying the row-27 module observation and the 9(b) client finding as harness-environment notes.

**Secondary, gated:** the cap=1 discriminating check (does the concurrency variable gate anything at any value) — only if the M3 ANL wants it; not before terminal state.

**Filing convention:** halts that change the hand → Class F amendments A2, A3… with standalone child cards under `docs\handoffs\`; rulings that don't change the hand → handback section D only.

### 4.1  Code session launch procedure (each session)

1. Exit the previous Code session (it closes at a halt or boundary with nothing running).
2. Fresh PowerShell, `cd C:\highsierralabs\RHACO` (same cwd as sessions 1–3; the handback and findings live under its `working\`).
3. Caps, process scope only:
   ```
   $env:CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH = "1"
   $env:CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS = "3"
   Get-ChildItem Env:CLAUDE_CODE_MAX*
   ```
   Both must print back. If the Code surface is the desktop app rather than a terminal, stop: process-scope env will not reach it, and User-scope vars are a recorded host change needing explicit ratification.
4. `claude --version` → `2.1.260`. Anything else is an HND §2 M halt before launch (auto-updater is disabled at User scope, so drift means a manual act).
5. `claude --dangerously-skip-permissions` — the session-1 cmdline; do not add flags (HND §0 item 10 recorded it).
6. First message, session 4:

   > Rule-2 commit for the untracked CCX pair, subject `RHACO-CCX-20260904-001: file build shepherd session handoff` (single id, ASCII, under 72), push. Reconcile the CCX's MCP write from `docs\logs\mcp_validate.log` as a criterion-6 source. Re-enter RHACO-HND-20260903-001 per §2 M with Amendment A1 (`167771c7…`, 9,698 B, full-file read): re-pin items 1, 5, 6, 8, 9, 14. Dispatch wave 2 (catalog, search, reader) as round 2 from `62685da`; probe builder fills W1–W10 and the qualification presets. Push at session close per ruling O-1. Report at the next halt or builder-round boundary.

   Later sessions: same launch; first message = "Re-enter RHACO-HND-20260903-001 per §2 M with A1 [and A2…] applied; continue from `next_action` in `build_state.json`; report at the next halt or boundary."

## 5  Empirical observations for the receiving chat (pointers, not interpretations)

- §0 item 9(b), session 2: cap variable present at value 3 in the client process (name occurs in the 2.1.260 binary); a fourth concurrent strand ran at once in every measured form (Agent-tool idle waits, Workflow surface, concurrent generation turns); depth-1 strands carry no spawn tool. 18-strand probe record in the findings file.
- Session-2 findings: Explore-typed sonnet strand refused a governance-framed probe as suspected injection, general-purpose complied; client sleep rail steers strands to background absent an explicit prohibition; `opus` pin resolves to `claude-opus-5[1m]`. Tier strings of record: `claude-sonnet-5`, `claude-opus-5[1m]`, `claude-haiku-4-5-20251001`.
- Item 12 VERIFY: every public entry point takes `db_path`; `BODY_SCAN_ROOT` is a module constant read at call time and `reindex_full` passes no root.
- Session 3, integrated `main`: 52 tests pass; L1 grep 6 hits, all in the allowlisted fixture builder; probe production run PASS (healthz, diagnostics on the live index, read-only); L4 oracle adapter-vs-module identical ids 40/40; Recall@10 0.675 for both; standing July figure 0.700; the shortfall is one row (27, "current version of the card schema"): live head moved v1_8 → v1_9 after July and hybrid top-10 still surfaces v1_8. SCOPE.md row with cause; no re-rank, no re-index.
- Deviations recorded in the handback: two builders captured opening timestamps late; I4 treated junction-spelled grep hits as out of scope (corrected from the corpus listing); four diagnostics tests invalidated by the merge, repaired by the integrator (A20; Pattern #3 evidence). Builder rounds 3 of 28 consumed.
- RHACO closeout gate at every push this session: regression FAIL (`test_required_claim_floor_v9…archived_corpus` → INC-20260829-001; `test_corpus_index_self_edges` → INC-20260830-001), auditor MISMATCH (+33 at `0243874`: 25 backlog + 8 guard, 0 from the commit; +35 at `3b860bf`: +2 from A1 citing the gitignored handback path), librarian / structure-guard / git-status-clean PASS. Standing-exception registry empty since 2026-08-21.
- Host: `DISABLE_AUTOUPDATER=1` at User scope and in-process; the 00:16:28Z 2026-09-04 npm rewrite of 2.1.260 was the Director's manual update (R-A8 closed). SessionStart hook excised; `settings.json` changed since the excision, so restoration is a re-insert, not a copy-back (R-A10).

## 6  Methodological framing for the receiving chat

The harness is the object; the browser is the fixture (CMP §1). "The instrument observes itself": adapter-vs-module identity on the pinned index is the load-bearing retrieval check, not the absolute recall figure — hence ruling AC-4 (differential over absolute). "Measurement defines category": D-13's live-verification clause produced the 9(b) result; it is a mechanism finding about the client, not a governance violation, and the wave cap is now enforced at the layer that can enforce it (A1.3). Asserted-vs-captured (CCX-20260825-002 §4 item 5): model strings are what the client reports. The prompt is the frozen instrument (D-11): the hand adds no step to its loop; refusals, background steering, and cap enforcement are handled around it, never by editing it. Push-red discipline: attribution-closed with delta-attributable stated per red; the gate's inability to carry a ratified exception is CMP-20260808-001's finding, not this arc's to fix. Three-layer discipline for the M3 ANL: client behaviour / harness governance / build outcome kept distinct.

## 7  Out-of-scope items / queued follow-ons

| Item | Status | Owner |
|---|---|---|
| Auditor baseline re-seed (`--write-baseline`) with attribution tables | QUEUED | Docs tail CHG after terminal state |
| INC-20260830-001 §5 items 1–2 (self-edge re-pin, diagnostic fix) | DEFERRED | Director placement: CMP-20260808-001 or this arc's docs tail |
| `regression_baseline.json` schema for the INC-20260829-001 §7 exception | DEFERRED | CMP-20260808-001 act (a); CCX-20260903-001 §7 partition holds |
| CLAUDE.md line 73 Guide pin → v1.3 (R-1) | QUEUED | Docs tail |
| CMP §8 lines (M0 close, M1, terminal) and stale "Remaining M0 items" text (R-2) | QUEUED | Docs tail |
| Guide v1.3 §9 QUEUED line resolution; Guide §9 pattern-table refresh from harness evidence | QUEUED | Docs tail; M3 |
| Row-27 hybrid ranking of superseded version head | QUEUED | M3 ANL observation (module finding, not build) |
| Cap=1 discriminating check | DEFERRED | M3 ANL, if wanted |
| A8 auto-update pin restoration; A10 hook re-insert | ONGOING | CMP-20260815-002 pilot close |
| CMP-20260815-002 scoring hand resume | DEFERRED | CCX-20260829-001 after INC-20260827-001 gate |
| Archive-tool junction canonicalization CHG | QUEUED | Before next archive act (memory item; unchanged) |

## 8  Glossary — session-specific vocabulary

- **Wave cap** — the concurrency cap of 3, one wave; hand-declared and orchestrator-enforced, audited from `dispatched_utc`/`returned_utc` intervals (HND A1.3).
- **`concurrency_exceedance`** — any instant with four overlapping live strands; a governance defect the closeout reports (A1.3).
- **`REFUSED`** — round outcome for a strand that declines its prompt; one task-first re-dispatch permitted, second refusal halts (A1.6).
- **Ruling O-1** — workspace push at each session boundary and terminal state, fast-forward only (handback section D).
- **Ruling AC-4** — acceptance = identical ids adapter-vs-module and Recall@10 equal to the module on the same pinned index; 0.700 is the July reference (handback section D; A2 at terminal state).
- **Criterion-6 reconciliation source** — a non-build writer of the live index whose touch is explained from a log: chat-side MCP writes (`mcp_validate.log`), gate librarian runs (production log) (handback J.5).
- **Push-red, attribution-closed** — push over a red closeout gate with every red filed and delta-attributable stated per member (handback section A; Director ratification 2026-09-03).
- **Deviation D-1** — CHG-20260903-001 §4 count line `Twelve` → `Thirteen`, ratified on the v1.1→v1.2 precedent (CHG §5).

## 9  Cross-references

Primary deliverable: RHACO-HND-20260903-001 Amendment A1. Co-travelling: RHACO-CHG-20260903-001 (Baseline), RHACO_Subagent_Pattern_Application_Guide_v1_3, RHACO-CMP-20260903-001. Foundations: RHACO-CCX-20260825-002 (asserted-vs-captured; sequencing guard), RHACO-HND-20260825-002 + A8/A10 (host residuals), RHACO-INC-20260829-001 and RHACO-INC-20260830-001 (closeout-gate reds), RHACO-ANL-20260712-001 (retrieval oracle). Predecessor CCX: RHACO-CCX-20260903-001.

Priority read order: (1) this CCX §0–§4; (2) RHACO-HND-20260903-001 then Amendment A1 (read §2 as amended); (3) `working\HND-20260903-001_report.md` section D (rulings, resumption entries) and section A; (4) RHACO-CMP-20260903-001 §4–§6; (5) Guide v1.3 D-3, D-11, D-12, D-13; (6) CCX-20260903-001 §7 (the out-of-scope partition still holds).

---

*Reno High-Altitude Cosmic Ray Observatory (RHACO) | Kris E. Granholm, Director*
