# RHACO-ANL-20260920-001 | Corpus Explorer Public-Release Readiness Sweep — What a Visibility Change Would Publish

*Reno High-Altitude Cosmic Ray Observatory (RHACO) · 5,050 ft ASL · 39°N*
*RadiaCode RC-110-003225 · CsI(Tl) · 30 mm Pb walls / 40 mm Pb lid · sealed castle*

| Field | Value |
|---|---|
| Document type | ANL (Discrete analysis report — release-surface measurement) |
| Status | Active |
| Target campaign | None. The Corpus Explorer build campaign is closed and untouched; this work is lateral to it by Director ruling of 2026-09-20 |
| Object under evaluation | The `RHACO_Corpus_Explorer` repository at HEAD and across all reachable history; the snapshot candidates named in RHACO-CCX-20260920-001; the three drafted public documents |
| Evidence base | Read-only measurement by Claude Code, 2026-09-20 UTC. Five grey-zone drivers under `working\CCX-20260920-001\`; six machine-readable artefacts; the live corpus index opened read-only |
| Data | No observatory data stream consumed. The live derived index was read through a `mode=ro` URI for identifier resolution only |
| Author | Kris E. Granholm, Director, RHACO (executed by Claude Code, RHACO-CCX-20260920-001 receiving session) |
| Date | 2026-09-20 UTC |
| Naming convention | v1.17 · Style RSG v1.9 · Schema Card YAML v1.9 · ANL Specification v1.0 |

**What this document does and does not do.** It reports evidence. Per the receiving scope
it does not recommend history rewrite versus fresh export versus publish-as-is, does not
rule any document into or out of the snapshot, and does not classify any RHACO science
content as releasable. Those are the Director's calls from the tables below.

---

## 0  Pre-flight pins

Executed by Claude Code against on-disk state; every value below was measured this
session, not carried forward from the handoff.

| Pin | Value | Note |
|---|---|---|
| RHACO repo head | `8395448` on `main` | Matches the handoff's chat-side pin `839544857384` |
| RHACO working tree | Two untracked paths: the handoff pair itself | Explained; not swept (a session-open sweep owns it) |
| Explorer repo head | `a87d2594813233e53e7f56005636843ee3def098` on `main`, equal to `origin/main` | Real `git status --porcelain` empty — the handoff's heuristic reading confirmed |
| Explorer index entries | 560 | — |
| Explorer local branches | `main` plus eight `build/*`; eight linked worktrees | — |
| Open hands | None. Both 2026-09-20 hands closed, reports on disk, closure commits in the log | — |
| Snapshot candidates | 22 of 22 present at the handoff's stated sizes | Two globbed names resolved on disk (section 4) |
| Three drafted documents | Present in `working\`; all three SHA-256 equal the handoff pins | Item S-8(a) therefore executable |
| `git` | 2.55.0.windows.5 | — |
| `gh` | 2.96.0, authenticated, scopes `gist read:org repo workflow` | — |
| **Secret scanner** | **`gitleaks` ABSENT; `trufflehog` ABSENT** | Substitute pattern set declared in full in section 3 |
| Interpreter | Anaconda 3.13.9 | — |

Drafted-document identity, re-measured:

| File | Bytes | SHA-256 | Pin |
|---|---|---|---|
| `working\README.md` | 9,358 | `57b69c5a147a16955a18f71737379b0ad779ca4ffc4f1d13580a1af86476fc1f` | MATCH |
| `working\HOW_IT_WORKS.md` | 12,493 | `7114de5f3c5c8f3d42313d5c1d50c9202b0b0fe9048cc6180c8ab02200a62a44` | MATCH |
| `working\BUILD_CASE_STUDY.md` | 18,419 | `09fe3c90b6e2b9b8e16d7ef9a7b2d11b558a14f693090e78a77a55f4de05d02a` | MATCH |

**Pre-flight verdict: PASS-WITH-NOTES.** One item is genuinely absent from the host — a
dedicated secret scanner. No value was assumed; no check is reported that was not run.

---

## 1  Publication surface (S-1)

Measured with `git ls-remote origin` (no fetch), `rev-list`, `cat-file --batch-check`,
and a per-commit tree walk.

| Quantity | Measurement |
|---|---|
| Refs present on the remote | `HEAD` and `refs/heads/main`, both at `a87d2594…`. Nothing else |
| The eight `build/*` branches | Local-only (zero remote refs each) **and** fully merged: each is 0 commits ahead of `origin/main` |
| Commits reachable from `origin/main` | 163 |
| Commits reachable from all local refs | 163 — identical, confirming the branch result |
| Distinct author identities, all history | 1 — `Kris E. Granholm <292265287+highsierralabs@users.noreply.github.com>`, on all 163 |
| Distinct committer identities, all history | 1 — the same identity |
| Blobs reachable from all refs | 631, totalling 33,314,871 B (31.8 MB); `.git` on disk 27 MB |
| Paths present in any historical tree | 560 |
| Paths present at HEAD | 560 |
| **Paths added then deleted** | **0** |
| Renames / copies in history | 0 |
| Modification events | 122, across 50 distinct paths |

**Finding S-1.** A visibility change would publish 163 commits under one identity, no
branch beyond `main`, and no path that is not also present at HEAD. The history's only
addition over the HEAD tree is 71 superseded blob versions of 50 currently-tracked files.
The twenty largest blobs in history are all probe captures under
`docs/probe-qualification/runs/` (1.32 MB down to 345 KB) except the twentieth,
`build_state.json` at 313,306 B.

The author identity is the GitHub noreply address, which does not disclose a personal
mailbox. It does disclose the account number and the account name.

---

## 2  Corpus-content exposure census (S-4)

This is the largest finding and is reported before the smaller ones.

### 2.1  Probe runs classified by their own measurement

Category is set by each run's `run_summary.json` `db_path` and `docs_root`, not by the
preset's name.

| Backing | Runs | PNG captures | PNG bytes | JSON captures |
|---|---|---|---|---|
| **Live-corpus-backed** | **52** | **48** | **26,746,059 (25.5 MB)** | 69 |
| Fixture-backed | 19 | 29 | 6,214,185 (5.9 MB) | 63 |
| Total | 71 | 77 | 32,960,244 (31.4 MB) | 132 |

Distinct backing paths observed, with run counts:

| `db_path` | Runs |
|---|---|
| `C:\highsierralabs\RHACO\index\corpus_index.db` | 52 |
| `…\RHACO_Corpus_Explorer\.worktrees\probe\fixtures\fixture_index.db` | 12 |
| `…\RHACO_Corpus_Explorer\fixtures\fixture_index.db` | 7 |

`docs_root` partitions identically: 52 runs against `C:\highsierralabs\RHACO\docs`, 19
against a fixture corpus.

By capture name, the live/fixture split is clean and structural: every `W1`–`W10` capture
is live-backed (43 PNGs) and every `KG`/`KB1`–`KB5` capture is fixture-backed (24 PNGs).
`W8` appears once fixture-backed and three times live-backed; `diagnostics` splits six
live to four fixture.

### 2.2  RHACO identifiers named in the tree

| Surface | Files scanned | Id occurrences | Distinct ids | Distinct non-fixture ids |
|---|---|---|---|---|
| `docs/probe-qualification` (top level) | 5 | 819 | 244 | **244** |
| `docs/rounds` | 50 | 230 | 37 | 30 |
| `tests/` | 73 | 69 | 14 | 8 |
| `fixtures/` | 19 | 19 | 7 | **0** |
| `build_state.json` | 1 | 11 | 5 | 4 |
| root `*.md` | 6 | 13 | 6 | 6 |
| `docs/critique` | 2 | 2 | 1 | 1 |
| `explorer/` | 37 | 3 | 1 | 1 |
| `preflight/` | 2 | 0 | 0 | 0 |
| **Whole tree** | — | — | **284** | **277** |

Of the 277 non-fixture identifiers, **269 resolve against the live corpus index**; 8 do
not. Seven of those eight are synthetic test doubles in `tests/search/fake_adapter.py`
and siblings, plus the probe's own injected drift card. The eighth,
`RHACO-EVT-20260420-002`, is a gold-set target that no longer resolves in the live index —
a corpus fact, recorded, not repaired here.

The 269 resolved documents, classified from their own cards:

| Doc type | Count |  | Program | Count |  | Card status | Count |
|---|---|---|---|---|---|---|---|
| ANL | 70 |  | DetPhys | 160 |  | Active | 134 |
| HND | 54 |  | Infra | 130 |  | Baseline | 117 |
| CCX | 35 |  | CR/EAS | 83 |  | Draft | 12 |
| EVT | 35 |  | Radon | 45 |  | Superseded | 4 |
| CHG | 32 |  | Cross | 24 |  | Archived | 2 |
| DLB | 19 |  | Helio | 21 |  | (unresolved) | 8 |
| CMP | 14 |  | (unresolved) | 8 |  | | |
| RDM 3 · INC 2 · MTN 2 · SOP 2 · OBS 1 | 10 |  | | |  | | |

Program totals exceed 269 because a card may carry several programs.

**Class assignment.** The identifier set is class G by construction (governance and
process identifiers). The program distribution establishes that it is **also class S**:
160 DetPhys, 83 CR/EAS, 45 Radon and 21 Helio documents are science-program records, and
twelve carry card status `Draft`.

### 2.3  What the captures actually render

The JSON captures are comparatively thin. Across all 69 live-backed capture JSONs there
are 111 excerpt-bearing string fields — 99 page titles, and 4 each of `disk_line_text`,
`target_excerpt` and `target_path` — yielding **two distinct verbatim corpus strings**:
one document's first heading line, and one absolute path under `C:\RHACO\docs\reports\`.
Thirty-one of the 52 live runs name at least one real identifier in their own JSON or
server log; 19 runs have a `server.log` that names one.

**The PNG captures are a different matter, and the JSON does not describe them.** Two
were viewed directly, the JSON being silent on rendered titles and body text.

- A reader capture (`W9`, 1.32 MB) renders the **complete body** of a governed maintenance
  record: its restart record with detector serial and event identifiers, the castle lid
  modification detail including a materials table with brand, product and quantity, a
  post-restart observations table with baseline values and interpretations, known
  limitations, recommendations, cross-references, and a raw log excerpt — together with
  the full card metadata panel and the document's `C:\RHACO\docs\reports\…` local path.
- A search capture (`W2`, 667 KB) renders roughly 29 result rows, each with its absolute
  disk path and its descriptive filename, spanning radon, SUPER-EAS, tungsten-putty
  composition, spectrum and baseline-settling documents, plus the mode-standing text
  quoting two retrieval figures with their source analyses.

**Finding S-4.** A live-corpus-backed capture publishes governed RHACO document content
verbatim, as a bitmap. This exposure is **invisible to every text-based scan of the
repository**, including every scan in this analysis: the identifier census of section 2.2
measures what the JSON and markdown name, and the rendered image carries more. Forty-eight
such captures totalling 25.5 MB are present at HEAD and in history.

### 2.4  Fixture and test provenance

`fixtures/corpus/` holds eight synthetic documents across four directories. Each one's own
first section declares it synthetic ("It is not a real RHACO analysis and carries no
scientific content", and equivalents). **None is copied from or derived from a real card**;
no real identifier appears anywhere under `fixtures/`. `fixtures/fixture_index.db` contains
7 card rows and 8 FTS rows over exactly those documents.

In `tests/`, the 8 non-fixture identifiers are the build's own campaign and dispatch ids,
the July retrieval evaluation, and four synthetic doubles minted in the `2026090x-1xx`
range.

### 2.5  The gold set (S-4e)

`C:\RHACO\working\eval\gold_queries.yaml` is **not** present in the Explorer tree. Its
contents are nonetheless present in substance: `docs/probe-qualification/gold_v1_1_compat.json`
carries all 40 rows with each row's **query string, target identifiers, stratum, and
accepted set**, plus the ten adapter and ten module identifiers returned per row, and the
set's own provenance — source document name and source SHA-256. Two files match a
`gold` name pattern in the tree: that report and `tools/l4_gold_oracle.py`.

`docs/probe-qualification/card_agreement.json` additionally publishes 120 sampled card
references with doc ids and dates, and the live corpus census of the day: 1,444 rows, of
which 866 bare-date and 578 quoted-date.

---

## 3  Secrets, full history (S-2)

**No dedicated scanner exists on this host.** The substitute is a 22-rule pattern set, run
over 483 working-tree text files (77 binary skipped) and 122 historical text blobs not
present at HEAD. The rules, stated in full so the null is interpretable:

`aws_access_key_id`, `aws_secret_shape`, `github_token`, `github_pat_fine`, `openai_key`,
`anthropic_key`, `google_api_key`, `slack_token`, `stripe_key`, `npm_token`, `pypi_token`,
`jwt`, `private_key_block`, `putty_key`, `ssh_authorized`, `pfx_pem_cert`, `conn_string_pw`,
`basic_auth_url`, `assigned_secret`, `netrc_line`, `env_secret_line`, `high_entropy_b64`.
The regular expression for each is recorded in `working\CCX-20260920-001\s2_secret_scan.json`.

**Twenty of the 22 rules returned zero matches.** The two that fired are both false
positives, each confirmed by reading its match:

- `env_secret_line`, 6 matches in 3 locations — all the Python lines
  `tokens = _MD.parse(doc.text)` and `token = tokens[idx]` in the reader service and its
  two historical versions. The rule is case-insensitive, so a lowercase identifier
  satisfied its uppercase environment-variable shape.
- `high_entropy_b64`, 1,084 matches in 75 locations — 1,061 are 64-character hexadecimal
  SHA-256 digests (the build's own hash pins, 52 of them in `build_state.json` alone) and
  23 are a 54-character path string ending `…diagnostics`.

**Finding S-2. Credentials: absent under these patterns**, at HEAD and across all reachable
history. This is a bounded result: a secret that matches none of the 22 rules, or that
lives in one of the 77 binary files, would not have been found.

---

## 4  Host and identity leakage (S-3)

Same two-scope method: working tree plus every historical blob not at HEAD.

| Class | Pattern | Total | Working tree | History-only | Locations |
|---|---|---|---|---|---|
| I | `abs_c_path` | 938 | 791 | 147 | 111 |
| I | `port_bind` (loopback) | 952 | 945 | 7 | 171 |
| I | `credential_kw` | 222 | 60 | 162 | 38 |
| I | `win_account` (`kgran`) | 21 | 21 | **0** | 6 |
| I | `win_user_path` | 5 | 5 | **0** | 2 |
| I | `hostname` | 0 | 0 | 0 | — |
| I | `hostname_class` (`DESKTOP-…`) | 0 | 0 | 0 | — |
| I | `tailnet` / `ts.net` / tailscale | 0 | 0 | 0 | — |
| I | `ipv4` (non-loopback) | 0 | 0 | 0 | — |
| I | token shapes | 0 | 0 | 0 | — |
| I | private key blocks | 0 | 0 | 0 | — |
| P | `email` | 0 | 0 | 0 | — |

**Finding S-3(a).** History contributes **no additional** account-name, host-name, tailnet,
address or email occurrence. Every one of the 21 `kgran` occurrences is in the working tree
at HEAD: four `W8.json` captures carrying `C:\Users\kgran\AppData\Local\Temp\probe_w8_*`
fixture paths (lines 10, 15, 20, 21 of each), one `server.log` traceback at lines 117–124
naming `C:\Users\kgran\anaconda3\Lib\json\…`, and `docs/rounds/R04_probe.report.md` line 145
naming a temp directory. The handoff's chat-side count of 21 lines in 6 files is confirmed,
and the history question it left open is answered: zero.

**Finding S-3(b).** The absolute-path exposure is the substantial one: 938 occurrences in
111 locations, of which 147 exist only in superseded blob versions. By path root:
`C:\RHACO\docs` 163, `C:\highsierralabs\RHACO_Corpus_Explorer` 93, `C:\RHACO` 23,
`C:\RHACO\rhaco` 23, `C:\RHACO\working` 17, `C:\RHACO\index` 14, `C:\RHACO\data` 13,
`C:\RHACO\tools` 6, `C:\Users\kgran` 4, `C:\RHACO\models` 3. The heaviest single files are
`docs/rounds/R00_I4_corpus_conventions.report.md` (47),
`docs/probe-qualification/runs/20260905T043147Z/server.log` (38) and
`docs/rounds/R00_I3_retrieval_dispositions.report.md` (32).

**Finding S-3(c).** The 222 `credential_kw` matches are 217 occurrences of the English word
"token" — overwhelmingly discussing a string literal named `mode_effective` — and 5 of
"authorization" in governance prose about an authority boundary. No credential. The 952
`port_bind` matches are loopback binds.

---

## 5  Third-party content (S-5)

| Question | Measurement |
|---|---|
| Copy or substantial excerpt of the upstream prompt, tree or history | **Absent.** Every "fable" occurrence in the tree is the model identifier `claude-fable-5-1` in build records. Three distinctive upstream phrases were searched across both repositories: none present |
| Vendored JS, CSS or fonts under `explorer/web/` | **None.** `explorer/web/` holds exactly three files: `static/app.css` (12,387 B), `static/app.js` (4,539 B), `templates/base.html`. Across all of `explorer/`, six static assets totalling under 25 KB, all hand-written. No font, no minified bundle, no vendor directory |
| Dependency licences | 11 pinned packages in `requirements.txt`: fastapi 0.141.1, uvicorn 0.52.4, Jinja2 3.1.6, playwright 1.62.0, pytest 9.1.1, PyYAML 6.0.3, sqlite-vec 0.1.9, markdown-it-py 4.2.0, mdit-py-plugins 0.6.1, ruff 0.16.6, httpx 0.28.1. All are mainstream permissive-licensed Python packages; none is vendored into the tree |

**Finding S-5. Class T: absent** under the patterns stated, at HEAD and in history.

---

## 6  Upstream pin attempt (S-6)

Executed by cloning the public upstream bare into a temporary directory outside both
repositories.

| Measurement | Value |
|---|---|
| Commits in the upstream repository, all refs | **1** |
| The single commit | `aea8b1035030952555395de0c1de14ba693a1427`, committed `2026-09-03T00:47:42+02:00` = `2026-09-02T22:47:42Z` |
| Commits touching `PROMPT.md` | 1 — that same commit |
| `PROMPT.md` blob | `c2bc981d4af76130f8ad88f2ddd857491c517c72`, 5,742 B |
| `PROMPT.md` SHA-256 | `29815365b64ec65e9c9bbbdb429eb8b8352e21ccaa6887db6a302082f9565972` |
| Upstream repository licence | **MIT**, "Copyright (c) 2026 raw (github.com/rawprogress)" |

**Finding S-6(a): a no-match, reported as a no-match.** A content-hash walk of the RHACO
tree found **no file** whose SHA-256 equals the upstream blob's, and none of 5,742 bytes.
No retained byte-identical copy of the upstream `PROMPT.md` exists on disk.

**Finding S-6(b): the upstream is nonetheless recoverable.** The upstream history is a
single squashed commit dated roughly seventeen hours before the recorded access of
2026-09-03 at about 15:30 UTC. Only one version of `PROMPT.md` has ever existed in the
public history, and it is retrievable now under the identity pinned above. The drafts'
statement that the upstream commit "was not captured" is accurate as a statement about
what RHACO recorded at the time; it understates what is recoverable today. **Bound:** a
force-push or re-squash performed after the access would have erased the evidence of any
intermediate state, and that possibility cannot be excluded from here.

**Finding S-6(c): a provenance error of record in a snapshot candidate.** The Build Prompt
Template v2.0 provenance paragraph states that the upstream file "as retrieved is retained
as `working\PROMPT_TEMPLATE.md`, sha256 `d1f2dee6…`". The hash is correct for that file —
measured `d1f2dee6dbdbc0a3ef13b3afceb468ef326347baeef98a2c8844763e23e7a36d`, 7,908 B — but
the file is not the retrieved upstream. It is 7,908 B of slot-bearing boilerplate whose own
header reads "Boilerplate derived from the harness structure in `rawprogress/fable-cities/PROMPT.md`.
Fill every `{{SLOT}}`", i.e. the v0 generalisation described in the very next clause of the
same paragraph. The retrieved upstream is 5,742 B of Cities-domain instruction text. The
companion pin is internally consistent: `working\PROMPT_TEMPLATE_CHARTER.md` measures
`7d6b39e138bcadd9a569890bb00751eb429b6987bfa5211f1dd68529654268fa`, 10,153 B, matching its
stated `7d6b39e1…`.

The three drafts inherit this: they state that "a copy of that source was retained in
RHACO's working material". No such copy was found.

---

## 7  Snapshot-candidate sweep (S-7)

Twenty-two candidates, all present. Five are untracked `working\` artefacts.

### 7.1  Class hits, aggregate across the candidate set

| Class | Pattern | Occurrences | Note |
|---|---|---|---|
| I | `abs_c_path` | 134 | Heaviest: the preflight findings file (55), the dispatch hand (28) |
| I | `win_account` / `win_user_path` | 4 / 4 | Dispatch hand line 92; preflight findings lines 115, 285, 686 |
| I | `port_bind` | 3 | Preflight findings, loopback |
| P | `person_name` | 37 | The Director's name, in header and signature blocks throughout |
| P | `email` | 3 | Preflight findings lines 429, 466, 556 |
| S | `altitude` | 13 | The site altitude in the standard document header line |
| S | `detector_serial` | 10 | The primary detector serial in the standard header line |
| S | `event_id` | 1 | The dispatch handback, line 381 |
| I | hostname, tailnet, non-loopback IPv4, Bluetooth MAC, named API key | 0 | Absent under these patterns |
| S | CPS value, coordinates, site address | 0 | Absent under these patterns |

Per-candidate counts with line numbers are in `working\CCX-20260920-001\s7_candidates.json`.
The concentration is sharp: `working\preflight_findings_HND-20260903-001.md` alone carries
55 of the 134 absolute paths, 3 of the 4 account-name occurrences, and all 3 emails.

### 7.2  Dangling citations on copy

The candidate set cites **45 distinct RHACO identifiers** and provides **9** of them.
**36 dangle** — that is, 36 identifiers would be cited by the copied set without any
member of the set resolving them. The heaviest are the change records of the build's own
week (eleven, ten, ten and nine occurrences for four of them), the July retrieval
evaluation (8), the git-governance procedure (6), and two incident records (6 each).
The full list with occurrence counts is in the JSON artefact.

### 7.3  MANIFEST inputs

Every candidate carries a measured SHA-256 and git blob SHA-1. For the 17 tracked
candidates, the creating commit was resolved, the worktree blob equals the HEAD blob, and
`git diff HEAD` is empty — so blob identity is provable against the creating commit for
each. **The five untracked `working\` candidates have no git blob identity and no creating
commit**; a manifest row for those can carry a full-file hash only. The complete table is
in `working\CCX-20260920-001\s7_candidates.json` and is reproduced in the handback.

---

## 8  Draft-document checks (S-8)

### 8.1  Cross-repository links, and the reason they matter

**Eleven links** to `github.com/highsierralabs/RHACO`, confirming the handoff's chat-side
count: 2 in `README.md` (lines 83, 84), 2 in `HOW_IT_WORKS.md` (line 124), 7 in
`BUILD_CASE_STUDY.md` (lines 13, 45, 128, 141). They resolve to four distinct URLs — the
campaign charter, the harness evaluation, the template v2.0 and its guide. Three further
links point at the upstream prompt. No other external links exist in the three drafts.

**Repository visibility, read through `gh`:**

| Repository | Visibility | Licence |
|---|---|---|
| `highsierralabs/RHACO` | **private** | MIT |
| `highsierralabs/RHACO_Corpus_Explorer` | **private** | none |
| `highsierralabs/Laconic_tests` | public | CC-BY-4.0 |
| `rawprogress/fable-cities` | public | NOASSERTION (MIT file present in-tree) |

**Finding S-8(a)+(b).** All eleven cross-repository links point into a private repository.
On a visibility change they would return 404 for every public reader. The drafts
acknowledge this partially — `README.md` line 81 says the records "may require separate
access" — but `BUILD_CASE_STUDY.md` presents its four links as ordinary citations without
that qualification.

### 8.2  README repository guide versus the tree

Every target the guide names exists, **except** `docs/HOW_IT_WORKS.md` and
`docs/BUILD_CASE_STUDY.md`, which are the drafts themselves and are not yet placed. The
guide's `explorer/config.py` reference resolves.

Present on disk and **absent from the guide**: `preflight/`, `fixtures/`,
`DISPATCH_PARAMETERS.md`, `ruff.toml`, `.gitignore`. The first three confirm the handoff's
chat-side observation; the last two extend it.

### 8.3  Quantitative claims against their primary records

| Claim | Referent | Result |
|---|---|---|
| Terminal state `BOUNDED_FAIL` | `build_state.json` `terminal_state.state` | **MATCHED** |
| Nine objective gates pass | `terminal_state.prompt_section_12_reasoning`: "All nine objective gates pass" | **MATCHED** |
| 11 of 12 acceptance presets | Same field, and five further occurrences in `build_state.json` | **MATCHED** |
| 333 tests | `terminal_state.prompt_section_12_required_fields.achieved_functions`: "333 tests, ruff clean" | **MATCHED** |
| Recall@10 0.675 versus 0.700 on 40 queries | `gold_v1_1_compat.json`: `recall_at_10_adapter` 0.675, `recall_at_10_module_direct` 0.675, `threshold` 0.700, `rows` 40 | **MATCHED** |
| Round budgets 4 / 28 / 2 | `build_state.json` `budgets`: `builder_rounds_per_module_max` 4, `builder_rounds_total_max` 28, `convergence_window_rounds` 2 | **MATCHED** |
| Template v2.0 dated September 7, 2026 | The document's own header line: "Version 2.0 \| September 7, 2026" | **MATCHED** |
| Template v2.1 a later revision | Its header: "Version 2.1 \| September 7, 2026" — same calendar date, later creating commit | **MATCHED**, with the nuance that both carry the same date |
| PARTIALLY SUPPORTED | The harness evaluation's classification paragraph, which returns that value by the letter of its criteria and records the alternative reading as the Director's | **MATCHED** |
| Seven target behaviours holding at terminal | Same paragraph: "(a)–(g) all hold at terminal" | **MATCHED** |

**Finding S-8(d). Every quantitative claim spot-checked matched its primary record.**
None was unmatched; none was unlocatable. The drafts' careful distinction between the
software's terminal state and the harness evaluation's verdict is faithful to both
records.

The one non-quantitative correction is S-6(c): the retained-copy provenance statement.

---

## 9  Licence scoping inventory (S-9)

Enumeration only. The Laconic_tests pattern scopes its MIT notice by naming one directory
("Applies to the code in `scripts/`"); the equivalent enumeration here is:

| Class | Files | Bytes |
|---|---|---|
| CODE | 120 | 714,621 (0.7 MB) |
| DOCUMENTS-AND-DATA | 440 | 34,964,089 (33.3 MB) |
| Unclassified | 0 | — |

CODE by top-level directory: `tests/` 73 files (254,621 B), `explorer/` 37 (249,970 B),
`tools/` 5 (198,801 B), `fixtures/` 2 (9,915 B), repository root 3 (1,314 B — the lint,
dependency and ignore configuration).

DOCUMENTS-AND-DATA by top-level directory: `docs/` 414 files (34,494,081 B — of which the
probe captures dominate), repository root 7 (451,819 B, chiefly `build_state.json`),
`fixtures/` 17 (13,585 B, the synthetic corpus and its index), `preflight/` 2 (4,604 B).

**Boundary cases, for the Director to scope.** Only two files are CODE inside an otherwise
DATA tree: `fixtures/__init__.py` and `fixtures/build_fixture_index.py`. No DATA file sits
inside a CODE tree. A directory-scoped MIT notice naming `explorer/`, `tools/`, `tests/`
and the two `fixtures/` builder sources would cover all 120 CODE files with no exception
list; a notice naming only `explorer/` would leave 83 files uncovered.

`explorer/` contains HTML templates, counted here as CODE because they are application
source rather than corpus documents. That classification is a judgement this analysis
makes explicit rather than silently; it is reversible.

---

## 10  Boundaries observed

No write, stage, commit, fetch, garbage-collection, branch or worktree operation was
performed in the Explorer tree, and no output file was placed there. No push, visibility
change, history rewrite or remote-setting change was performed anywhere. No candidate
document was edited. The live corpus index was opened through a read-only URI. The
upstream clone is bare and lives in the session scratchpad, outside both repositories.

Sensitive strings are reported by location and class. The two false-positive rules in
section 3 are quoted because their matches are ordinary source identifiers and English
words, not secrets; no matched value elsewhere required redaction, because none was
sensitive.

---

## 11  Measurement limits

1. **The bitmap gap.** Section 2.3 is the finding, and it is also the limit: two captures
   were viewed. The other 46 live-backed PNGs were classified by their run's own declared
   backing, not by reading their pixels. Their content class is inferred from the preset
   they belong to and from the two that were read. A complete enumeration of what every
   capture renders would require viewing all 48.
2. **The secret scan is pattern-bounded.** Section 3's null holds for 22 stated rules over
   text. Seventy-seven binary files at HEAD were not scanned for embedded strings.
3. **The identifier census is pattern-bounded.** It counts canonical
   `RHACO-TYPE-DATE-SEQ` identifiers. Documents named only by title, by filename stem, or
   by a `RHACO_Name_vN_M` reference are not in the 277. The `RHACO_`-prefixed reference
   names were counted separately per surface and are in the census artefact.
4. **One boundary defect was found and fixed mid-sweep, and is recorded.** The
   candidate-set driver initially reported zero self-provided identifiers, because a
   regular-expression word boundary does not fire between a sequence number and the
   underscore that follows it in a filename stem — both are word characters. This is the
   same boundary class the corpus's own numeric-token sweep rule warns about. Corrected;
   the dangling count moved from a spurious 45 to the reported 36. A second such defect
   was found in the leakage driver: a per-pattern sample cap truncated history findings
   out of the reported sample while the counts stayed correct, which briefly made history
   look clean. Corrected by counting per scope before sampling. Both are recorded because
   an instrument defect that produces a clean-looking result is the failure mode this
   sweep exists to avoid.
5. **`gh`-read visibility is a point-in-time reading** of 2026-09-20 and is not a durable
   property.

---

## 12  Artefacts

All under `working\CCX-20260920-001\` — grey-zone drivers and outputs, outside the census
walk, no Tool Reference row, no companion cards.

| File | Role |
|---|---|
| `ccx920_s2_secret_scan.py` / `s2_secret_scan.json` | S-2, with the 22 rules recorded in the output |
| `ccx920_s3_leak_sweep.py` / `s3_leak_findings.json` | S-3, scope-separated counts |
| `ccx920_s4_census.py` / `s4_census.json` | S-4 run classification and identifier census |
| `ccx920_s4_join.py` / `s4_exposure_table.json`, `s4_excerpts.json` | S-4 index join and excerpt harvest |
| `ccx920_s7_candidates.py` / `s7_candidates.json` | S-7 candidate sweep and MANIFEST inputs |
| `ccx920_s9_licence_inventory.py` / `s9_licence_inventory.json` | S-9 enumeration |
| `s1_deleted_paths.txt` | S-1 historical-path difference (empty, by measurement) |

---

## 13  Cross-references

Receiving scope: RHACO-CCX-20260920-001.
Lateral: RHACO-CMP-20260903-001; RHACO-HND-20260903-001 with its three amendments;
RHACO-ANL-20260905-001 with Amendment A1; RHACO-ANL-20260907-001;
RHACO-CHG-20260907-002; RHACO-CHG-20260907-004.
Pattern of record for licence scoping: the Laconic_tests dual-licence files.
Governing specification: the ANL Specification and Report Style Guide in force on disk.

---

*Reno High-Altitude Cosmic Ray Observatory (RHACO) | Kris E. Granholm, Director*
*RadiaCode RC-110-003225 | CsI(Tl) | 30 mm Pb walls / 40 mm Pb lid, sealed castle | 5,050 ft ASL, Lemmon Valley NV*
