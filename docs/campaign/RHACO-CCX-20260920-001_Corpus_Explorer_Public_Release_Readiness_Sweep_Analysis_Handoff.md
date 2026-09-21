# RHACO-CCX-20260920-001 · Corpus Explorer Public-Release Readiness Sweep — Session Handoff to the Read-Only Sweep Instance (Claude Code)

*Reno High-Altitude Cosmic Ray Observatory (RHACO) · 5,050 ft ASL · 39°N*
*RadiaCode RC-110-003225 · CsI(Tl) · 40 mm Pb Castle (3.5π geometry)*

| Field | Value |
|---|---|
| Document type | CCX — session handoff (per CCX Specification v1.1) |
| Session scope | Scoping session for making the `RHACO_Corpus_Explorer` repository public as a documented build case study: what campaign material to include, how to package it, and what must be measured before the visibility change. Closed with a curated-snapshot recommendation and this sweep brief. |
| Session output handed forward | One falsifiable question and nine sweep items (section 4); chat-side observations as pointers (section 5); the snapshot candidate list (section 3). |
| Receiving instance | Claude Code, resume route, read-only. Primary focus: measure what a visibility change would publish and what the snapshot candidates carry. Output: one ANL plus a handback under `working\`. No secondary scope. |
| Author | Kris E. Granholm, Director, Reno High-Altitude Cosmic Ray Observatory (RHACO) |
| Date | 2026-09-20 UTC |
| Status | Filed; closes the 2026-09-20 Corpus Explorer public-release scoping session |

## §0 Pre-flight verification

Before reading the rest of this CCX, the executing instance verifies on-disk and halts on any mismatch:

1. **Repository state, RHACO.** Record `repo_head` for the RHACO tree. Chat read `839544857384` on `main` from `server_info` at 2026-09-20T19:34Z (server 0.28.0, librarian 1.19, NC 1.17).
2. **Repository state, Explorer.** `C:\highsierralabs\RHACO_Corpus_Explorer` HEAD is `a87d2594813233e53e7f56005636843ee3def098` on `main`, equal to `origin/main`; 560 index entries; eight local `build/*` branches and eight worktrees; no packed refs. Chat read this with `git_state`, whose index pass is a heuristic and detects no untracked files. Confirm with real `git status` and `git branch -a`.
3. **No open hand.** Two HNDs were filed in the RHACO tree today (HND-20260920-001 and -002). Confirm neither is executing in a way this read-only session would collide with. This session writes nothing to the Explorer tree and only the ANL pair and `working\` files to the RHACO tree.
4. **Snapshot candidates exist** at the section 3 paths with the listed sizes (chat read via `find_files`, sizes only; bodies unread by chat).
5. **The three drafted public documents** are chat uploads, not yet in either tree. If the Director has placed them on disk, verify the section 3 SHA-256 pins; if not, skip item S-8(a) and say so.
6. **Tool availability.** Record which of `git`, `gh`, `gitleaks` (or equivalent) are present with versions. A missing scanner is reported, not substituted silently; state the substitute pattern set in full if one is used.

## 1  Session summary

The Director proposed making the Corpus Explorer repository public to show what it is for, why it is built as it is, and the process that built it, not for adoption. Three public-facing documents were drafted outside this session (README, HOW_IT_WORKS, BUILD_CASE_STUDY). This session:

- Recommended a **curated, hash-pinned snapshot** of campaign records under `docs/campaign/` in the Explorer repository, non-canonical by banner, rather than the whole campaign subtree (21 indexed children, of which roughly a third tell the build story).
- Recommended a new `docs/PROMPT_EVOLUTION.md` tracing the frozen prompt to Template v2.0 and v2.1 through the template-review ANL.
- Adopted the Laconic_tests licence pattern by Director decision: `LICENSE` CC BY 4.0 for documents and data, `LICENSE-CODE` MIT for code, plus `CITATION.cff`.
- Identified that a visibility change publishes history, captures and fixtures, not just HEAD, and that none of that surface has been measured. This CCX scopes that measurement.

No governed document other than this CCX was produced.

## 2  Campaign state at session close

The Corpus Explorer build campaign is reported closed: the title of RHACO-CHG-20260905-003 records card `status: Baseline` (Channel 1) and `lifecycle_state: CLOSED` (Channel 3). Chat inferred this from that title in the derived index and did not read the campaign card; the receiving instance confirms it from the card. This work is **not** filed as a member of that campaign: the card cites it laterally through `see_also`. No campaign state changes in this session and none is requested of the receiving instance.

## 3  Data artifacts available for the receiving chat

**Sweep target (read-only):** `C:\highsierralabs\RHACO_Corpus_Explorer` — top level holds `ARCHITECTURE.md`, `CONSTRAINTS.md`, `SCOPE.md`, `PROMPT.md`, `RATIONALE.md`, `DISPATCH_PARAMETERS.md`, `build_state.json` (313,306 B), `requirements.txt`, `ruff.toml`, `.gitignore`, and directories `docs`, `explorer`, `fixtures`, `preflight`, `tests`, `tools`. No `README.md` and no licence file at HEAD.

**Snapshot candidates (RHACO tree, read-only).** Tier 1 is the recommended inclusion set; Tier 2 is conditional on this sweep.

| Tier | Path under the RHACO root | Size (B) |
|---|---|---|
| 1 | `docs\reports\RHACO-CMP-20260903-001_Corpus_Explorer_Autonomous_Build_Harness.md` | 23,880 |
| 1 | `docs\handoffs\RHACO-HND-20260903-001_Corpus_Explorer_Autonomous_Build_Dispatch.md` | 23,306 |
| 1 | `docs\handoffs\RHACO-HND-20260903-001_..._Amendment_A1_Cap_Rehome_And_Session_2_Findings.md` | 9,698 |
| 1 | `docs\handoffs\RHACO-HND-20260903-001_..._Amendment_A2_Convergence_Rulings_Ledger_And_Identity_Pin.md` | 13,899 |
| 1 | `docs\handoffs\RHACO-HND-20260903-001_..._Amendment_A3_Criterion_6_Reconciliation_Mechanism_Correction.md` | 3,962 |
| 1 | `working\HND-20260903-001_report.md` (Code's handback; ungoverned working artifact) | 196,366 |
| 1 | `docs\reports\RHACO-ANL-20260905-001_*.md` (harness evaluation; resolve the full name on disk) | unread |
| 1 | `docs\reports\RHACO-ANL-20260907-001_Build_Prompt_Template_Review.md` | 23,462 |
| 1 | `docs\reference\RHACO_Build_Prompt_Template_v2_0.md` and `..._Guide_v2_0.md` | 19,562 / 16,639 |
| 1 | `docs\reference\RHACO_Build_Prompt_Template_v2_1.md` and `..._Guide_v2_1.md` | 22,742 / 18,614 |
| 1 | `docs\reports\RHACO-CHG-20260907-004_Build_Prompt_Template_v2_1_REF_Cut.md` | 28,879 |
| 1? | `docs\reports\RHACO-CHG-20260907-002_Build_Prompt_Template_v2_0_REF_Cut.md` | 55,746 |
| 2 | `docs\reports\RHACO-CCX-20260904-001_*.md`, `RHACO-CCX-20260905-001_*.md`, `RHACO-CCX-20260905-002_*.md` (shepherding handoffs) | unread |
| 2 | `working\preflight_findings_HND-20260903-001.md` | 111,637 |
| 2 | `working\S7_halt_records_DRAFT_HND-20260903-001.md`, `working\sealed_audit_HND-20260903-001_S4.md`, `working\S4_launch_note_HND-20260903-001.md` | 16,563 / 6,138 / 9,793 |

**Drafted public documents (chat uploads; pins are SHA-256 of the uploaded bytes):**

| File | Size (B) | SHA-256 |
|---|---|---|
| `README.md` | 9,358 | `57b69c5a147a16955a18f71737379b0ad779ca4ffc4f1d13580a1af86476fc1f` |
| `HOW_IT_WORKS.md` | 12,493 | `7114de5f3c5c8f3d42313d5c1d50c9202b0b0fe9048cc6180c8ab02200a62a44` |
| `BUILD_CASE_STUDY.md` | 18,419 | `09fe3c90b6e2b9b8e16d7ef9a7b2d11b558a14f693090e78a77a55f4de05d02a` |

**Licence pattern of record:** `C:\highsierralabs\Laconic_tests\LICENSE` (18,658 B), `LICENSE-CODE` (1,233 B, SHA-256 `8aacd8f9cbb9c593b606f5a3d445376cb0c81d5e4c5553cf45a8fc2fc8fe283f`, MIT scoped to `scripts/`, stating documents and data are CC BY 4.0), `CITATION.cff` (443 B).

## 4  Receiving-chat scope statement

**The one question.** If the Explorer repository's visibility were changed to public exactly as it stands, and the section 3 snapshot candidates were copied into it unedited, what content outside the intended disclosure would be published — by class, by location, and by whether it lives at HEAD, in history only, or both?

Intended disclosure is: the application source, the build's own records, the frozen prompt and rationale, and the campaign's process record. Everything else is a finding to enumerate. **The ANL reports evidence only** (CCX Specification v1.1, no-framing-decisions directive): it does not recommend history rewrite versus fresh export, does not rule any document in or out of the snapshot, and does not classify any RHACO science content as releasable. The Director decides from the tables.

**Content classes** for every finding: **G** governance or process text; **S** science content (measured values, event data, figures, unpublished findings); **I** infrastructure or security (host paths, account names, hostnames, addresses, ports, remote-access detail, credentials or tokens); **P** personal or third-party (names, emails, correspondence); **T** third-party copyrighted material.

**Sweep items.** Each reports method, tool and version, counts, and a location table. A null is reported as "absent under these patterns", with the patterns stated.

- **S-1 Publication surface.** What a visibility change exposes: refs present on the remote (`git ls-remote origin`; do not fetch), whether the eight `build/*` branches are local-only, commit count reachable from `origin/main`, every distinct author and committer identity across all history, the twenty largest blobs in history, and every path ever added then deleted.
- **S-2 Secrets, full history.** Scanner over all reachable history and the working tree. Class I.
- **S-3 Host and identity leakage.** Working tree and history: Windows account paths, hostnames, IP addresses, ports, tailnet or remote-access names, emails. Chat's partial read is in section 5; extend it to history and to the other patterns.
- **S-4 Corpus-content exposure census.** (a) The 77 PNG captures under `docs/probe-qualification/runs/`: classify each run as fixture-backed or live-corpus-backed from its own JSON (`db_path`, `docs_root`), and for live-backed runs list the RHACO document ids and titles the capture renders, from the sibling JSON observations first, by viewing the image only where the JSON is silent. (b) The JSON captures and `server.log` files: document ids, titles, excerpts. (c) `build_state.json`, `docs/rounds/`, `docs/critique/`, `preflight/`: quoted corpus text. (d) `fixtures/` and `tests/`: provenance of every fixture card and document, synthetic versus copied or derived from a real card, with the real id where derived. (e) Whether the 40-query gold set and its target ids are in the tree. Report the exposed RHACO documents as a table by doc type, program and class G/S/I/P.
- **S-5 Third-party content.** Any copy or substantial excerpt of the fable-cities prompt in tree or history (class T); vendored JS, CSS or fonts under `explorer/web/`; licences of the `requirements.txt` dependencies.
- **S-6 Upstream pin attempt.** Locate the retained fable-cities `PROMPT.md` copy in RHACO working material; record its path, SHA-256 and git blob SHA-1. Clone the public upstream to a temporary directory outside both repositories, list every commit touching `PROMPT.md` with its blob id and commit time, and report whether the retained copy's blob id matches any commit, and which. The drafts currently state the upstream commit was not captured; this item measures whether it is recoverable. Report a no-match as a no-match.
- **S-7 Snapshot-candidate sweep.** For every section 3 candidate: class I, P and S hits with counts and line numbers; the count of RHACO ids cited that are outside the candidate set (dangling on copy); and SHA-256 plus git blob SHA-1 with the creating commit, as MANIFEST inputs.
- **S-8 Draft-document checks.** (a) Count and list the cross-repository links to the RHACO GitHub repository in the three drafts (chat counted 11 by pattern). (b) Report the RHACO and Explorer remotes' current visibility if `gh` can read it; otherwise report unknown. (c) Compare the README repository guide against the actual tree (chat observed `preflight/`, `fixtures/` and `DISPATCH_PARAMETERS.md` on disk and absent from the guide). (d) Spot-check every quantitative claim in the three drafts against its primary record (terminal state, nine gates, 11 of 12 presets, 333 tests, 0.675 versus 0.700 on 40 queries, round budgets 4 / 28 / 2, template dates) and report each as matched, unmatched or unlocatable, with the referent.
- **S-9 Licence scoping inventory.** Enumerate Explorer paths as code versus documents-and-data so an MIT notice can be scoped as Laconic_tests scopes it. Enumerate; do not decide.

**Deliverables.** `RHACO-ANL-20260920-NNN_Corpus_Explorer_Public_Release_Readiness_Sweep.md` with card in `docs\reports\` (SEQ 001 was free at 19:40Z; re-verify at write), and a handback under `working\`. Driver scripts are grey-zone tools under `working\`, no Tool Reference row, no card.

**Hard boundaries.** No write, stage, commit, fetch, gc, branch or worktree operation in the Explorer tree; no output files placed there. No push, visibility change, history rewrite or remote setting change anywhere. No edits to any candidate document. Sensitive strings found under S-2 are reported by location and class with the value redacted.

## 5  Empirical observations for the receiving chat (pointers, not interpretations)

All chat-side, 2026-09-20, via the MCP read surface. Each is a starting point to re-measure, not a result.

| # | Observation | Source and limit |
|---|---|---|
| O-1 | The campaign subtree holds 21 indexed children: ANL 2, CCX 9, CHG 8, HND 1, SOP 1. CHG-20260907-004 is not among them. | `traverse_campaign_subtree`; derived index, may lag |
| O-2 | 77 PNG files under `docs/probe-qualification/runs/`, roughly 32 MB; largest are `W1` and `W9` captures at 1.1 to 1.3 MB each. Names follow `W*`, `KB*`, `KG`, `diagnostics`. | `find_files`; content unviewed |
| O-3 | The Windows account name appears on 21 lines in 6 working-tree files: four `W8.json` captures (temp-directory fixture paths), one `server.log` traceback, and `docs/rounds/R04_probe.report.md` line 145. Zero hits for a `DESKTOP-` hostname pattern. 481 files scanned, 78 skipped as binary. | `grep_files`, working tree only; history unmeasured |
| O-4 | Commit identities in the last five commits use the GitHub noreply address. | `git_state` n=5; full history unmeasured |
| O-5 | Remote-tracking refs show `origin/main` only; the eight `build/*` heads have no remote counterpart locally recorded. | `git_state`; remote not queried |
| O-6 | Template v2.0 and v2.1 files carry mtimes of 2026-09-07 03:22Z and 19:36Z. | `find_files` mtimes; not authored dates |
| O-7 | The upstream fable-cities `PROMPT.md` page showed no licence text; its note invites copying the file and swapping the domain. The repository-level licence was not read. | single `web_fetch`, 2026-09-20 |
| O-8 | The three drafts contain 11 links matching the RHACO GitHub repository pattern. | pattern count over the uploads |

## 7  Out-of-scope items / queued follow-ons

| Item | Status | Owner |
|---|---|---|
| Building `docs/campaign/`, `MANIFEST.md`, relinking the three drafts, adding licence files and `CITATION.cff` | QUEUED, gated on the ANL | A later HND, `ops` route (sibling-workspace class, with its verification gate) |
| `docs/PROMPT_EVOLUTION.md` authoring | QUEUED | Chat, after the ANL |
| History rewrite versus fresh-history export versus publish as-is | DEFERRED to the Director | Director, from the ANL tables |
| Which RHACO documents are releasable science content | DEFERRED to the Director | Director |
| The visibility change itself | DEFERRED | Director, manually |
| RHACO repository visibility | ONGOING, out of scope | Director |
| Correcting the drafts' content | QUEUED | Chat, from S-8 |
| Campaign membership for this work | CLOSED — Director ruling 2026-09-20: left off the closed build campaign; Corpus Explorer work continues as an observatory fixture, not a running campaign | Director |

## 8  Glossary — session-specific vocabulary the receiving chat will need

- **Publication surface** — everything a visibility change exposes: all refs on the remote and every object reachable from them, not the HEAD tree. Defined here for this sweep only.
- **Snapshot candidate** — a RHACO-tree document proposed for an unedited, hash-pinned, explicitly non-canonical copy in the Explorer repository. The RHACO tree remains the record of authority.
- **Live-corpus-backed / fixture-backed capture** — a probe run whose own JSON names the real index and document root, versus a temporary fixture index. Category is set by that measurement, not by the workflow's name.
- **BOUNDED_FAIL**, **PARTIALLY SUPPORTED** — the build's terminal state and the harness evaluation's verdict; distinct findings. Canonical in RHACO-ANL-20260905-001; not restated here.

## 9  Cross-references

Primary inputs: RHACO-ANL-20260905-001; RHACO-ANL-20260907-001.
Lateral: RHACO-CMP-20260903-001; RHACO-HND-20260903-001; RHACO-CHG-20260907-002; RHACO-CHG-20260907-004; Build Prompt Template v2.0 and v2.1 with Guides.
Governing specification: RHACO_CCX_Specification_v1_1 (section 6 omitted as permitted: no methodological reframing).
Predecessor CCX: none.

Receiving-instance priority read order:

1. This CCX, section 0 then section 4.
2. `C:\highsierralabs\RHACO_Corpus_Explorer\SCOPE.md`, then `docs\LAYERS.md`, for what the build says its captures and fixtures are.
3. One `W*` run directory and one `KB*` run directory under `docs\probe-qualification\runs\`, JSON before PNG, to fix the live-versus-fixture test before the census.
4. `C:\highsierralabs\Laconic_tests\LICENSE-CODE` and `README.md` for the licence-scoping pattern.
5. The section 3 candidates, only as S-7 reaches them.

---

*Reno High-Altitude Cosmic Ray Observatory (RHACO) | Kris E. Granholm, Director*
*RadiaCode RC-110-003225 | CsI(Tl) | 40 mm Pb Castle, 3.5π geometry | 5,050 ft ASL, Lemmon Valley NV*
