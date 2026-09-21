# RHACO-CHG-20260907-002 — Build Prompt Template v2.0 and Guide v2.0: REF Cut from the CMP-20260903-001 Review, and Docs Tail

*Reno High-Altitude Cosmic Ray Observatory (RHACO) · 5,050 ft ASL · 39°N*
*RadiaCode RC-110-003225 · CsI(Tl) · 30 mm Pb walls / 40 mm Pb lid · sealed castle*

| Field | Value |
|---|---|
| Document type | CHG (Rule / schema codification — REF cut; with a docs tail) |
| Status | Baseline |
| Execution route | `docs` |
| Target campaign | None — discharges the last section 9 queue item of RHACO-CMP-20260903-001 (CLOSED; charter stays CLOSED, card untouched) |
| Predecessor CHG | RHACO-CHG-20260906-003 (docs tail of record; section 5 chat-side P-21 instances) |
| Priority | MEDIUM |
| Author | Kris E. Granholm, Director, RHACO |
| Date | 2026-09-07 UTC |
| Naming convention | v1.17 · Style RSG v1.9 · Schema Card YAML v1.9 · CHG Specification v1.0 |

## §1  Rationale

RHACO-ANL-20260907-001 reviewed the Charter-aligned domain-agnostic build-prompt template against the RHACO-CMP-20260903-001 record under nine adoption criteria ratified before the evidence map. Result: the template is indicted on all five prompt-design ledger rows (P-1, P-2, P-8, P-13, P-21), carries four criteria-derived absences (terminal states, dispatch records at dispatch, an `UNVERIFIED` value, a claim-audit layer) and one contrary text (it asserts per-layer independence), and the seven structural sections the campaign's positive results rest on were instantiation additions the template never had. The Director adopted the ANL's revision proposal R1–R10 as listed on 2026-09-07, with two R10 rulings: GL is dropped as a section warrant (the Charter is not this hand's target; a Charter cut is a separate carrier), and the structural provenance is pinned by access date (the base was taken 2026-09-03 ~15:30 UTC from `https://github.com/rawprogress/fable-cities/blob/main/PROMPT.md`; commit not captured).

The revised template and its companion guide leave `working\` (ops, grey-zone, outside the census walk) and become REF documents under `docs\reference\` with cards, per CHG Specification v1.0 section 8 (REF version bumps are new cuts triggered by a CHG). Version lineage: v0 — the `rawprogress/fable-cities` structure as generalised (`working\PROMPT_TEMPLATE.md`, never filed); v1 — the Charter rewrite (`working\PROMPT_TEMPLATE_CHARTER.md`, never filed); **v2.0 — this cut**, the first filed version. The Guide is cut at v2.0 to match, since v1 of the guide never existed (HOW_TO_USE was companion to v0).

Same hand, docs tail: the ANL's body and card flip to Baseline (its finding absorbed by this cut); a dated DISCHARGED line for the template review on RHACO-CMP-20260903-001 section 9.

Pins (chat full-file unless marked): `working\PROMPT_TEMPLATE_CHARTER.md` `7d6b39e1…` 10,153 B; `working\HOW_TO_USE.md` `4ac3ebda…` 12,736 B; `working\PROMPT_TEMPLATE.md` `d1f2dee6…` 7,908 B; RHACO-ANL-20260907-001 body 23,460 B [VERIFY full-file hash at pre-flight — chat read was ranged] and card [VERIFY]; RHACO-CMP-20260903-001 `39505d6c…` 23,632 B. Server 0.22.1, librarian 1.19, NC 1.17, head `c76a810` plus the uncommitted pairs (CCX-20260907-001, CHG-20260907-001, ANL-20260907-001, this CHG); census 1465.

## §2  Change Specification

### CS-1  `docs\reference\RHACO_Build_Prompt_Template_v2_0.md` (new REF; payload A below, landed verbatim)

### CS-2  `docs\reference\RHACO_Build_Prompt_Template_Guide_v2_0.md` (new REF; payload B below, landed verbatim)

### CS-3  Cards for CS-1 and CS-2

Two sibling `.card.yaml` per Card Schema v1.9 reference-doc conventions, modelled on a live REF card at the cut (executor: `get_card` a recent `RHACO_*_v*` reference card and mirror its field shapes; [VERIFY] the `current_version` string quoted `"2.0"`; status `Active`; programs `[Infra]`; `depends_on` → RHACO-ANL-20260907-001, RHACO_Measurement_Philosophy_v1_4_1; `see_also` → RHACO-CMP-20260903-001, this CHG; abstract from payload header).

### CS-4  RHACO-ANL-20260907-001 → Baseline (in-place, Code)

Body header row `| Status | Active |` → `| Status | Baseline |` (anchor count == 1 [VERIFY]; the body's section 2 also contains the word Active in prose — match the header row only). Card `identity.status: Active` → `Baseline`; `last_human_review` → `"2026-09-07"`; append a notes entry: `"Baselined 2026-09-07 by RHACO-CHG-20260907-002: revision R1-R10 absorbed by RHACO_Build_Prompt_Template_v2_0 and Guide v2_0."`

### CS-5  RHACO-CMP-20260903-001 section 9 — template-review DISCHARGED line (in-place, Code)

Anchor, count == 1 [VERIFY]: the paragraph ending `the body citing the tree sha; landed at f3a14fc.` Append immediately after it, one blank line between (executor copies verbatim; one paragraph):

```
**Template review DISCHARGED 2026-09-07** by RHACO-ANL-20260907-001 (evidence
map, criteria T1-T9, revision R1-R10 adopted) and RHACO-CHG-20260907-002
(RHACO_Build_Prompt_Template_v2_0 and Guide v2_0 cut to docs\reference).
Section 9 queue empty.
```

Charter stays CLOSED; card untouched; `last_human_review` not rewritten.

Not directed: the `working\` copies (retained as the v0/v1 record; not deleted, not edited); the Measurement Philosophy (GL stays parked there); RHACO-CHG-20260907-001; any code.

## §3  Changes Directed

None to production code. Executor: Claude Code under `/ho`, route `docs`, on `main`, Rule-2 commits, one doc-id at position 0 (this CHG's); gate-then-amend-before-push per RHACO-SOP-20260708-001 v4 Amendment A1, each body citing the tree sha its gate measured. Client identity read at entry as the P-19 conjunction including effort and the settings-file sha (against the RHACO-CHG-20260906-003 section 1 item 4 re-pin: `f5166920…` / 9,098 B); a sha change is a HALT for a ruling.

| # | Commit subject (ASCII, ≤72) | Content |
|---|---|---|
| 0 | `RHACO-CHG-20260907-002: file build prompt template v2 carrier CHG` (65) | this pair (chat-written via MCP) |
| 1 | `RHACO-CHG-20260907-002: land build prompt template v2 REF cuts` (62) | CS-1, CS-2, CS-3 |
| 2 | `RHACO-CHG-20260907-002: mark CMP section 9 template review discharged` (69) | CS-5 |
| 3 | `RHACO-CHG-20260907-002: baseline the review ANL and discharge` (61) | CS-4; this CHG body Status → Baseline, card → Baseline, section 5 Execution Record |

Pre-flight: hash every pinned file; the two payloads are written byte-for-byte from this CHG's §2 fenced blocks with the outer four-backtick fence stripped and LF endings; after landing, re-hash each REF and record in section 5. At commit 0, read this pair's `mcp_validate.log` instrument line before any librarian run; `in_scope: False` on the doc half is expected (RHACO-CHG-20260907-001 unlanded) and recorded, not halted on. Expected gate: librarian MATCH at 1465 + 2 = 1467 after commit 1; auditor 314 MATCH or +N attributable to this pair and the two REFs — attribute, do not baseline, do not waive; regression red on the two INC-owned members only. Halt-and-report on any VERIFY mismatch, any anchor count ≠ 1, an unexpected auditor member, or a librarian MISMATCH.

## §4  Cross-references

RHACO-ANL-20260907-001 (the review; criteria T1–T9; R1–R10) · RHACO-CMP-20260903-001 (section 9 queue, this item) · RHACO-ANL-20260905-001 + Amendment A1 (evaluation of record; ledger P-1…P-24 via the HND-20260903-001 handback) · RHACO-CHG-20260906-003 (predecessor; P-21 chat-side instances) · RHACO-CCX-20260907-001 (receiving scope) · RHACO_Measurement_Philosophy_v1_4_1 (P1–P7; GL remains a parked candidate there) · RHACO_CHG_Specification_v1_0 section 8 (REF cuts) · RHACO_Card_YAML_Schema_Specification_v1_9 · RHACO-SOP-20260708-001 v4 Amendment A1 (commit form).

## §5  Execution Record

Executed 2026-09-07 UTC by Claude Code under `/ho`, route `docs`, on `main`;
Director-ratified. Five commits, gate-then-amend-before-push at each per
RHACO-SOP-20260708-001 v4 Amendment A1, each body citing the tree sha its own
gate measured -- preceded by a two-commit SOP-20260708-001 P4 sweep ratified at
the same STOP.

**Client identity of record, re-pinned.** Read at entry as the P-19 conjunction
including effort: Claude Code 2.1.260, model `claude-opus-5[1m]`,
`switchModelsOnFlag` false, settings-file sha
`c4964b786a6aa3c341799a3089e4ccefd650c9a240e3a8eb96f31341202cb0b3` / 9,096 B,
mtime 2026-09-07T02:59:12.108Z. That is a **MISMATCH** against the section 1
pin `f51669201bf9e6b53efe7ed228c85987f621e392c1b3541644fa89d59d40b152` /
9,098 B carried from RHACO-CHG-20260906-003 section 1 item 4, and the section 3
halt fired at entry, before any edit. **Director ruling 2026-09-07: Option 1 --
re-pin as measured**, on the ground that this is a docs edit and not part of the
test harness the closed campaign was run on. Effort reads `xhigh` at top level
and under `modelSettings` for `claude-opus-5[1m]`, and `high` under
`modelSettings` for `claude-opus-5`; this session's own `/effort` at open
reported setting `high` and is the probable cause of the -2 B delta. The
`f5166920...` bytes are **not recoverable on disk** -- all three
`settings.json.bak*` files predate them -- so the two states were compared
endpoint to endpoint and never diffed; the byte the delta consists of is
unattributed and is recorded as such. Legs (i) and (ii) carried the conjunction;
per-request `message.model` was not read this hand.

### 5.1  Commits

| # | Commit | Tree | Content |
|---|---|---|---|
| S1 | `b567b4a` | -- | P4 sweep: RHACO-CCX-20260907-001 pair (undirected residue) |
| S2 | `7a613fe` | -- | P4 sweep: RHACO-CHG-20260907-001 pair (undirected residue) |
| 0 | `a939f31` | `52a9692` | This pair, chat-written via the MCP canonical write path 03:07:17.927Z |
| 1 | `6371884` | `e3ece76` | CS-1, CS-2, CS-3: the two REF cuts and their cards |
| 2 | `513a9cb` | `b3dfed2` | CS-5: RHACO-CMP-20260903-001 section 9 DISCHARGED paragraph |
| 3 | `7d3fbc8` | `3c019cf` | CS-4; this body and card to Baseline; the first cut of this Execution Record |
| 4 | (this commit) | (this commit) | D5 forward fix: the D4 rewrite, this ledger row, and the commit 3 gate row |

The S1/S2 sweep commits carry no A1 gate tuple by design: the sweep's own gate
deferred to this hand's closeout because the tree was not clean until commit 3,
and a tuple measured over a later tree would misdescribe them.

### 5.2  Artifacts

| Artifact | Before | After |
|---|---|---|
| `RHACO_Build_Prompt_Template_v2_0.md` | absent | `3e248533...` 19,562 B |
| `RHACO_Build_Prompt_Template_Guide_v2_0.md` | absent | `c5146bf7...` 16,639 B |
| `RHACO_Build_Prompt_Template_v2_0.card.yaml` | absent | 3,256 B |
| `RHACO_Build_Prompt_Template_Guide_v2_0.card.yaml` | absent | 2,809 B |
| RHACO-CMP-20260903-001 body | `39505d6c...` 23,632 B | `2ab4c20b...` 23,880 B |
| RHACO-ANL-20260907-001 body | `bb733873...` 23,460 B | `09bb5408...` 23,462 B |
| RHACO-ANL-20260907-001 card | `2c6ad40b...` 2,932 B | `4d5c1601...` 3,065 B |

Both payloads were extracted programmatically from this document's section 2
fenced blocks under transactional preconditions -- fence lines asserted at 78 /
250 / 254 / 466, both targets asserted absent -- with the outer four-backtick
fence stripped, written LF, UTF-8 no BOM, and re-hashed after landing. No fence
byte leaked into either file. The three `working\` pins hashed at pre-flight and
all three matched: `PROMPT_TEMPLATE_CHARTER.md` `7d6b39e1...` 10,153 B,
`HOW_TO_USE.md` `4ac3ebda...` 12,736 B, `PROMPT_TEMPLATE.md` `d1f2dee6...`
7,908 B. The two section 1 `[VERIFY]` items resolved to the values recorded
above. The `working\` copies were not deleted and not edited.

### 5.3  Deviations

**D1 -- census pin off by one, non-gating.** Section 1 pins census 1465; the
measured T0 was **1466**, and the section 3 arithmetic `1465 + 2 = 1467`
re-bases to **1468**. The difference is one card, consistent with the chat-side
count having been taken before this pair's own card landed at 03:07Z. The
librarian verdict compares membership, not totals, so `baseline=MATCH` held
throughout and no acceptance criterion moved.

**D2 -- one directed edit was already satisfied.** CS-4 directs
`last_human_review` to `"2026-09-07"` on the ANL card; that was already the
on-disk value, so the assignment is a no-op. Recorded, not skipped; the status
flip and the notes entry landed as directed.

**D3 -- undirected residue swept before commit 0.** The RHACO-CCX-20260907-001
and RHACO-CHG-20260907-001 pairs were uncommitted with no hand owning them.
`/ho` surfaces and never sweeps, so the condition was put to the Director at the
execution STOP; **ruling: sweep first** (option a). Both landed under their own
ids as Rule-2 commits S1 and S2. RHACO-CHG-20260907-001 remains **Filed and
unexecuted**, route `code`; its execution routes to `/patch` and is not part of
this hand.

**D4 -- one standing auditor add, attributed not cleared.** The gate's auditor
member ran `MISMATCH +1/-0` at the T0 pre-flight before any edit and at
commits 0 through 2. The single add is an `anchor_not_found` finding sourced
from RHACO-CCX-20260907-001, whose target is the Spec Family Modernization
campaign (RHACO-CMP-20260717-001) at a milestone anchor that document does
not carry -- a finding of the swept CCX, not of this cut. Per section 3 it is
**attributed, not baselined, not waived**; the waiver registry was never opened
and `citation_auditor_baseline.json` was not written. The two REF cuts and the
CMP paragraph added **zero** gating findings of their own, for which the
invariant `+1/-0` across commits 0 through 2 is the evidence.

**D5 -- the record emitted the finding it described; forward-fixed.** At
commit 3 the auditor moved to `+2/-0`. The second add was manufactured by this
Execution Record: the first cut of D4 quoted the finding as a literal tuple,
and the auditor's milestone grammar -- `MILESTONE_RE`, scanned in the window
following any resolved CMP target -- read the quoted target and its anchor
token back out of this document and emitted a second copy of the finding the
paragraph was describing. That is an unexpected auditor member and therefore a
section 3 halt: it was reported to the Director and not absorbed, and the
commit 3 body carries the `+2/-0` tuple as measured. **Director ruling
2026-09-07: forward-fix.** Commit 4 rewrites D4 in prose with the anchor
spelled out -- the remedy of record for this instrument class, following the
RHACO-CHG-20260906-003 Ruling C line-218 precedent -- restoring the auditor to
`+1/-0`. No baseline write and no waiver at any point. The general result,
that quoting an auditor finding verbatim inside a governed document emits that
finding again, is deliberately left unfiled here: it is rule-level and belongs
to its own carrier, not to this hand.

**No other deviation.** Every anchor count directed `[VERIFY]` measured exactly
1 before its edit: the ANL body Status row (the section 2 prose "Active" is a
different string and was not matched), the ANL card `status`, and the CMP
paragraph ending `landed at f3a14fc.`

**Instrument note.** The citation auditor's `--root` is the **docs** root
(`C:\RHACO\docs`), not the repository root. Invoked with the repository root it
returns `waived=0 baseline=ABSENT exit=2` and silently loads neither the waiver
registry nor the membership baseline; its class counts also shift between the
`C:\RHACO` and `C:\highsierralabs\RHACO` spellings. That is the
RHACO-CHG-20260907-001 junction defect observable in the instrument itself, and
it is why every tuple recorded here was measured through the gate rather than by
a hand invocation.

### 5.4  Gates

| Gate | Started | librarian | regression | auditor | structure-guard | git-status-clean |
|---|---|---|---|---|---|---|
| commit 0 | 03:33:20Z | PASS 13.8s, 1468, MATCH | FAIL 34.8s, 2/824/1 | FAIL 19.8s, +1/-0 | PASS 13/13 | FAIL |
| commit 1 | 03:35:58Z | PASS 13.8s, 1468, MATCH | FAIL 32.5s, 2/824/1 | FAIL 19.8s, +1/-0 | PASS 13/13 | FAIL |
| commit 2 | 03:38:04Z | PASS 13.7s, 1468, MATCH | FAIL 32.4s, 2/824/1 | FAIL 19.9s, +1/-0 | PASS 13/13 | FAIL |
| commit 3 | 03:44:26Z | PASS 13.7s, 1468, MATCH | FAIL 32.2s, 2/824/1 | FAIL 19.8s, +2/-0 | PASS 13/13 | PASS |
| commit 4 | (this commit) | tuple carried in this commit's own body post-amend | | | | |

Census held at **1468 cards, `baseline=MATCH`, broken=0, errors=0** at every
gate -- the predicted delta of a hand that adds two carded REF pairs and
otherwise edits in place, and the observed one. `git-status-clean` is red at
commits 0 through 2 by this CHG's own section 3 sequencing, which lands the
RHACO-ANL-20260907-001 pair last; it clears at commit 3. Regression is the two
INC-owned members -- `test_corpus_index_self_edges` (RHACO-INC-20260830-001) and
`test_required_claim_floor_v9::test_no_other_renderer_behaviour_changed_across_the_archived_corpus`
(RHACO-INC-20260829-001) -- at zero delta from the pre-flight baseline;
`docs\regression_baseline.json` membership is empty and carries neither, which
is why the member names only the second as new. Neither INC is in scope here.
The auditor member reads `+1/-0` at commits 0 through 2 and again at commit 4;
the `+2/-0` at commit 3 is the D5 self-emission, cleared by the forward fix.

### 5.5  Acceptance

| # | Criterion (section 3) | Verdict | Evidence |
|---|---|---|---|
| A1 | Every pinned file hashed at pre-flight | PASS | Three `working\` pins and the CMP pin matched; both `[VERIFY]` items resolved (section 5.2) |
| A2 | Payloads written byte-for-byte, fence stripped, LF | PASS | Transactional extraction, fences asserted, zero fence leakage, CR=0 and no BOM on all four new files |
| A3 | Both REFs re-hashed after landing and recorded | PASS | Section 5.2 |
| A4 | `mcp_validate.log` instrument line read at commit 0 before any librarian run | PASS | `in_scope: False` on the doc half, expected while RHACO-CHG-20260907-001 is unlanded; recorded, not halted on |
| A5 | Librarian MATCH after commit 1 | PASS | 1468, `baseline=MATCH`, on the D1 re-based arithmetic |
| A6 | Auditor MATCH or +N attributable; not baselined, not waived | PASS | +1/-0 at closeout, attributed to the swept CCX; the commit 3 excursion to +2/-0 was self-emitted by the record and forward-fixed (D4, D5); registry unopened, no baseline write |
| A7 | Regression red on the two INC-owned members only | PASS | 2 failed / 824 passed / 1 skipped, zero delta, exactly those node ids |
| A8 | Halt on any VERIFY mismatch, anchor count not equal to 1, unexpected auditor member, or librarian MISMATCH | PASS | Two halts fired; both were reported, ruled and recorded, neither absorbed: the identity halt at entry and the unexpected auditor member at commit 3 (D5). No VERIFY mismatch, no anchor count other than 1, and no librarian MISMATCH arose |
| A9 | Charter stays CLOSED, card untouched, `last_human_review` not rewritten | PASS | Only the section 9 paragraph was appended; five inserted lines, no other byte changed |
| A10 | Nothing not directed was touched | PASS | The `working\` copies, the Measurement Philosophy, RHACO-CHG-20260907-001 and all code are unchanged; D3 records the swept residue as a separately ratified act |

**Out of scope, operator/chat-pending:** none. The section 9 queue of
RHACO-CMP-20260903-001 is empty and the campaign remains CLOSED.

---

## Payload A — `RHACO_Build_Prompt_Template_v2_0.md`

````markdown
# RHACO Build Prompt Template — Self-Verifying Build Prompt

*Reference Document | Version 2.0 | September 7, 2026*
*Companion to: RHACO_Build_Prompt_Template_Guide_v2_0, RHACO_Measurement_Philosophy_v1_4_1*

---

## Provenance and lineage

Structure derived from `rawprogress/fable-cities` — `https://github.com/rawprogress/fable-cities/blob/main/PROMPT.md`, accessed 2026-09-03 ~15:30 UTC (commit not captured; the file as retrieved is retained as `working\PROMPT_TEMPLATE.md`, sha256 `d1f2dee6…`). v0 was that structure generalised; v1 was its rewrite against Measurement Philosophy v1.4.1 (`working\PROMPT_TEMPLATE_CHARTER.md`, sha256 `7d6b39e1…`); neither was filed. v2.0 applies the revisions R1–R10 of RHACO-ANL-20260907-001, from one run of one instantiation (RHACO-CMP-20260903-001; n = 1). Each section names the Charter principle it operationalizes (P1–P7); a label is a claim the section's mechanism must support. Fill every `{{SLOT}}`; delete `<!-- -->` comments before use.

---

# Goal

Build a {{TARGET_CLASS}} in {{STACK}}, from this empty folder.
The bar is {{QUALITY_BAR}}. Never {{ANTI_PATTERN}}.

Wherever a choice exists between the easier path and the more rigorous path, take the rigorous path. Where rigor is impossible, name the limitation in `SCOPE.md` (step 7) rather than working around it silently.

# How to work

## 1. Constraints first, then architecture. *(P1 Architectural Acceptance; P6)*

Before any feature code, write `CONSTRAINTS.md`: every known limitation of {{STACK}}, the runtime, the data sources, the budget, and the authority boundary (below) — {{KNOWN_CONSTRAINTS}}. Each constraint is an **input to the design**, not an obstacle. Where a constraint suppresses the obvious approach, the design lives downstream of the constraint in what remains uncorrupted. Never fight a constraint with a workaround that pretends it is absent; if a constraint is later removed, that is an explicit, versioned event with its own validation.

Then write `ARCHITECTURE.md`:
- one folder per subsystem: {{MODULE_LIST}}
- a shared {{CORE_DATA_MODEL}} every module reads from and writes to
- the public API each module exposes and the events it emits
- **ownership of every shared thing** — markup, vocabulary, contract, asset — assigned to the shell or the integrator by rule, decided here and never later by round cost; each shared block guarded by a contract test that fails when a copy diverges
- conventions: {{UNITS_AND_CONVENTIONS}}
- determinism: {{DETERMINISM_POLICY}}
- performance budget: {{PERF_BUDGET}}
- asset/data policy: {{ASSET_DATA_POLICY}}
- for every non-obvious design decision: the alternatives considered and why each was rejected, with specific reasoning *(P6)*

Isolate module failures so one broken module never takes the whole {{ARTIFACT_NOUN}} down.

<!-- KNOWN_CONSTRAINTS: e.g. "no WebGPU on target browser; 4 GB RAM ceiling; API rate limit 60/min; reference dataset has 30-min cadence only". These become the first entries in SCOPE.md. -->

## 2. The artifact observes itself. *(P2 The Instrument Observes Itself)*

Build the verification loop before the {{ARTIFACT_NOUN}}. Write `{{PROBE_TOOL}}`: a headless tool that {{PROBE_ACTION}}, waits until ready, applies a named {{PRESET_KIND}}, and writes {{PROBE_OUTPUT}} plus a JSON log containing {{PROBE_LOG_FIELDS}}.

**The probe must exercise the production path.** No mocks, stubs, fixtures-only branches, or instrumentation-only code paths: the probe observes the same build, the same data flow, and the same rendering or execution path the deliverable uses. Health telemetry ({{PROBE_LOG_FIELDS}}) is derived from that same stream, not from a separate monitoring layer with its own failure modes. If the probe is wrong about the artifact, it must be wrong for the same reasons the artifact is wrong — that coupling is the point.

**The probe's verdict is a fault predicate, not a capture predicate.** A run is FAIL when any PROBE_LOG_FIELD violates its declared bound, when any required capture is missing, or when the artifact's own error channel is non-empty. Successful capture is never `ok` by itself.

**Qualify the probe before trusting it.** Before any product claim cites a probe result, demonstrate on a frozen fixture or under controlled fault injection — never on the production data — that the probe passes one known-good case and fails each of {{KNOWN_BAD_CLASSES}}. Every qualification case asserts on the **rendered, user-facing observable**, never on a substrate attribute alone: a case that reads an attribute while the operator reads a sentence qualifies nothing the operator sees. Evidence lives under `docs/probe-qualification/`. Qualification is **progressive**: a known-bad class is qualified when the surface it needs first exists, and no product claim may cite a probe result for a surface whose class is unqualified. A probe that cannot separate known-good from known-bad is repaired before anything downstream is evaluated.

**A fixture is derived, not authored.** Where the probe uses a fixture, sample it from the production corpus's loader-resolved types and value shapes, and record a fixture-versus-production type census as a round-0 inspection output; a hand-authored fixture reproduces its authors' conventions, not the corpus's variance.

**Budget the instrument separately.** The probe is not a product module: it carries {{PROBE_ROUNDS}} of its own plus one extension round for every wave that adds a surface it must qualify.

Every module ships a **showcase mode** that stages a representative minimal instance of just that module through the production code, so it can be probed in isolation.

**No agent may claim anything it has not run the probe on and inspected.**

<!-- KNOWN_BAD_CLASSES: the fault classes the deliverable must be shown to expose, e.g. "wrong record for a known key; stale displayed metadata; reversed relation direction; broken deep link; console/runtime error". PROBE_ROUNDS: usually the per-module MAX_ROUNDS plus the wave extensions. -->

## 3. Verification layers and the shared-dependency register. *(P3 Layered Self-Filtering)*

The build is checked by five layers. Each carries its own version, its own validation criteria and its own **shared dependencies** in `docs/LAYERS.md`; none is claimed independent of the others.

| Layer | Mechanism | Catches | Shared dependencies (declared, not denied) |
|---|---|---|---|
| L1 Static | {{STATIC_CHECKS}} — types, lint, contract/schema validation, run on every commit | Contract violations before anything executes | the build tree; the schema |
| L2 Probe | `{{PROBE_TOOL}}` per step 2, run by the builder | Runtime failures, budget violations, visibly wrong output, unqualified surfaces | the build; the data; the capture path |
| L3 Critic | Separate agent per step 5, runs its own probes | What the builder saw and rationalized | the probe; the reference corpus; the model family |
| L4 Blind gate | External judge per step 6, sees only A/B artifacts | What the critic has grown used to | the probe output medium; the reference corpus |
| L5 Claim audit | Separate agent per step 5a, reads claims against referents | True code with false prose about it | the artifact tree; the record |

`docs/LAYERS.md` records: the shared dependencies above, filled in for this build; the sentence "independence claims we do not make"; and, for L5, which claim classes have a mechanical grammar and which remain a reader's. When layers disagree: record the disagreement; name the shared dependencies; distinguish an artifact defect from an instrument defect where evidence permits; run the smallest discriminating check; leave it unresolved if evidence cannot decide. A finding surfaced by a lower layer that a higher layer missed is logged as a gap in `{{STATE_FILE}}`, not silently absorbed. Upgrades stay local to one layer.

<!-- STATIC_CHECKS: e.g. "tsc --strict, eslint, JSON-schema validation of the core data model, folder-ownership check". -->

## 4. Fan out under explicit ownership. *(P6 Reasoning as Artifact)*

Use {{ORCHESTRATION_MECHANISM}}. One builder agent per module, owning only its folder. Waves ordered by dependency:
- Wave 1: {{WAVE_1_MODULES}}
- Wave 2: {{WAVE_2_MODULES}}
- Wave 3: {{WAVE_3_MODULES}}

Between waves, exactly one **integrator agent** — the only agent allowed to touch `{{CORE_PATH}}` and the shared things assigned in `ARCHITECTURE.md` — applies builders' core-change requests and revalidates every dependent after a contract change. Every accepted core change is recorded with the request, the alternatives, and the reason the integrator chose as it did. Ownership is never re-decided under budget pressure: a repair that crosses an ownership line waits for the owner's round if the defect is an omission, and is repaired at once **with a control** (a test that fails when the repair regresses) only if the defect is an affirmatively false statement about the artifact beside it.

Before every dispatch, record in `{{STATE_FILE}}` — before the strand returns — its role, model, effort, pattern, agent type, execution mode and `dispatched_utc`; any text carried verbatim into a dispatch is diffed against its archive at dispatch time; generated prompt text carries no round-specific and no self-referential literal.

<!-- ORCHESTRATION_MECHANISM: name what your environment provides — a subagent/task tool, one worktree per module driven by a script, a CI matrix, or "sequential waves in one session". -->

## 5. Differential critic. *(P4 Differential Measurement; P5 Measurement Defines Category)*

After each builder round, a separate **critic agent** — {{CRITIC_PERSONA}}, who writes no code — runs its own probes across several {{PRESET_KIND}} values, checks the API contract and {{PROBE_LOG_FIELDS}}, and scores each module.

**Scoring is differential, not absolute.** Three numbers per module per round:
- `ref_gap`: distance from {{REFERENCE_CORPUS}} on the anchored 0–10 scale — 10 = {{ANCHOR_10}}, 8.5 = {{ANCHOR_8_5}}, 7 = {{ANCHOR_7}}, 5 = {{ANCHOR_5}}
- `round_delta`: change since the previous round on the same presets — converging, oscillating, or thrashing, which the absolute score buries
- `iso_vs_integrated`: showcase-mode score minus integrated-mode score — non-zero is a seam problem for the integrator, not a module problem for the builder

**The reference corpus carries provenance.** *(P6)* Before scoring, the critic records in `docs/REFERENCE.md` what {{REFERENCE_CORPUS}} is, where each item was obtained, its version or date, the access date, and which properties are compared. A reference without provenance is not a reference.

**Anchors are calibrated empirically.** *(P5)* Before wave 1 completes, the critic scores {{CALIBRATION_ARTIFACTS}} and records the results in `docs/REFERENCE.md`. If the anchors do not reproduce on known artifacts, rewrite the anchors, not the scores; thereafter the anchor text is frozen. If no calibration artifacts exist for the domain, record in `SCOPE.md` that the scale is ordinal and uncalibrated, and never read PASS from it.

Pass = `ref_gap` ≥ {{PASS_THRESHOLD}} with {{ZERO_TOLERANCE_CONDITION}} and every objective gate green. Below that, the builder receives the ranked issue list and goes again, up to {{MAX_ROUNDS}} rounds. A module at {{MAX_ROUNDS}} with `round_delta` ≈ 0 is escalated to the integrator as a suspected contract problem, not given more rounds.

<!-- CALIBRATION_ARTIFACTS: three things of known quality — the reference itself (should score 10), a deliberately degraded copy (~5), an existing equivalent of known quality. -->

## 5a. Claim audit. *(P2; P6)*

After each integrator merge, a separate **claim-audit agent** — who writes no code and did not author the claims — reads every prose behaviour claim in the tree and the record (docstrings, notices, `ARCHITECTURE.md` and `CONSTRAINTS.md` sentences, round reports, `{{STATE_FILE}}` entries, critic reports) against the artifact it describes and returns, per claim, MATCH / MISMATCH / UNVERIFIABLE with the referent cited. A MISMATCH is a ranked issue to the owning builder; an UNVERIFIABLE claim is tagged `UNVERIFIED` in place. When an audit names a claim defect, the full extent of the claim across the tree is re-derived before the remedy is scoped — the named site is a sample. Every prose behaviour claim in the shipped tree carries either a named check or an `UNVERIFIED` tag; there is no third state.

## 6. Blind final gate. *(P4 — the paired comparison with the project's frame removed)*

A whole-{{ARTIFACT_NOUN}} critic scores {{END_TO_END_TARGET}} with the same three numbers. Then **blind judges** receive pairs of probe outputs labelled only A and B (ours vs. {{REFERENCE_CORPUS}}, order shuffled) and state which is better and why. Report the margin per round; a loss with narrowing margin is a result, not a failure to report. If no external artefact of the same medium exists, drop this gate and say so in `SCOPE.md`; never fake a reference.

## 7. Honest scope. *(P7 Honest Scope)*

Maintain `SCOPE.md` from the first commit: a normative table of every capability the {{ARTIFACT_NOUN}} does **not** provide, its status, the evidence for the limit, its consequence, the path to addressing it if one exists, and the validation required to remove it. Seed it from `CONSTRAINTS.md`. Any claim outside this table cites the module, probe result or audit verdict that supports it; any claim inside it states the limit explicitly. A capability leaving the table is a versioned event with its own validation criteria. Unmet bars — including a {{PASS_THRESHOLD}} never reached — are recorded here at the end of every run, plainly.

## 8. Reasoning as artifact, then loop. *(P6 Reasoning as Artifact)*

Persist to `{{STATE_FILE}}`: per module, `ref_gap`, `round_delta`, `iso_vs_integrated`, round count, open issues, assumptions, invalidated evidence, and every `UNVERIFIED` a builder reported — **`UNVERIFIED` is a first-class value that survives integration**; the integrator may overrule it only with a cited check, never by omission. Also: the dispatch records of step 4; the identity record of the executing client at every round boundary (Rules); layer gaps; the terminal state. Every critic report, claim-audit report and blind-judge response is stored unedited under `docs/critique/`; every builder round produces `docs/rounds/{{module}}-{{n}}.md` stating what was tried, what was rejected and why, and which probe outputs the claims rest on. Evidence paths are append-only: no round overwrites another's report.

Loop until every critic passes and the claim audit is clean, or `SCOPE.md` records why it cannot; then declare a terminal state (step 9). Each iteration resumes from the module with the largest `ref_gap`.

## 9. Terminal states. *(P7)*

End in exactly one state, declared once, from the record.

- **PASS** — only if every required capability exists, every objective gate passes from probe data, production-path probes pass, the claim audit is clean, `ref_gap` reaches {{PASS_THRESHOLD}} on a calibrated scale, no `SCOPE.md` row contradicts a required capability, and the authority boundary is intact.
- **BOUNDED_FAIL** — the artifact is usable but a required bar is unmet after convergence or budget exhaustion. Report: achieved capabilities; failed presets; best observed quality; whether the limit lies in the artifact, the substrate, the architecture, the instrument, or an external dependency; unresolved alternative explanations; the next discriminating action. Budget exhaustion is always this state, never PASS.
- **BLOCKED** — progress requires human authority or an unavailable mandatory dependency.
- **INVALID** — the verification path cannot support trustworthy claims about the artifact. INVALID is preferable to a PASS resting on an unqualified probe.

# Authority boundary *(P7; P1)*

Agents may autonomously: create, edit and delete files inside the workspace; refactor; change internal architecture and contracts through the integrator; add local dependencies consistent with the stack policy; run tests, probes and audits; read {{SUBSTRATE_PATHS}}; commit inside the workspace.

Stop in BLOCKED before: writing anywhere under {{SUBSTRATE_PATHS}}; changing {{PROTECTED_CONTRACTS}}; lowering {{PASS_THRESHOLD}} or changing anchor text after calibration; changing the meaning of an objective gate; removing a `SCOPE.md` row without its validation; any external deployment or credential exposure; redefining a required capability out of scope without qualifying evidence.

At closeout, a hand outside the build verifies the substrate untouched — hash of every {{SUBSTRATE_PATHS}} artifact before and after, commit census, write-mode census — and records it. The build asserts nothing here; it is measured.

<!-- SUBSTRATE_PATHS: the corpus, database, service or repository the artifact reads and must never write. PROTECTED_CONTRACTS: CORE_DATA_MODEL, public APIs, the accepted default configuration of any upstream system. -->

# Rules

- Never inflate scores. Report real numbers, failed rounds, negative deltas, and what is still missing. *(P7)*
- Never edit another module's folder. Core and shared changes go through the integrator and are recorded with reasoning. *(P6)*
- Never probe through a mock. If the production path cannot be probed, that is a `SCOPE.md` entry, not a reason to probe something else. *(P2)*
- Never claim a comparison against a reference whose provenance is not in `docs/REFERENCE.md`. *(P6)*
- Never state a behaviour in prose without a named check or an `UNVERIFIED` tag; never record a builder's `UNVERIFIED` as verified. *(P2)*
- **Identity of the executing client is a measurement variable.** At every round boundary read and record the conjunction of {{IDENTITY_SURFACES}}; any change from the value of record is BLOCKED until ratified; configure the client's automatic model-switch behaviour to halt, never to retry-and-continue. *(P5)*
- Keep {{LIVE_CONDITION}} at all times; other agents are probing it.
- {{HUMAN_GATE_POLICY}}

<!-- IDENTITY_SURFACES: e.g. "the client config file's sha and its model key; the system-prompt model sentence; the per-request model field read as a family/generation check". No single surface is sufficient: config is precise but static, the prompt is stale after a switch, the per-request field is live but may be truncated.
     HUMAN_GATE_POLICY — recommended default under P6: "Make routine decisions yourself and log assumptions and rejected alternatives to STATE_FILE and docs/rounds/. Stop and request ratification before any Authority-boundary item. Otherwise keep going." State which of autonomous / gated / reviewed is in force. -->

Start now.

---

## Version History

| Version | Date | Notes |
|---|---|---|
| 2.0 | 2026-09-07 | First filed version. Applies RHACO-ANL-20260907-001 R1–R10 to the v1 Charter rewrite: terminal states (9); probe qualification, fault predicate, progressive sequencing, separate instrument budget, derived fixtures (2); L5 claim audit and the shared-dependency register replacing the independence claim (3, 5a); structural shared ownership and dispatch records at dispatch (4); authority boundary with closeout verification; UNVERIFIED as a first-class state value (8); client identity as a measurement variable (Rules); labels resolved to mechanisms, GL dropped as a warrant, provenance pinned. Cut by RHACO-CHG-20260907-002. |

---

*Reno High-Altitude Cosmic Ray Observatory (RHACO) | Kris E. Granholm, Director*
````

## Payload B — `RHACO_Build_Prompt_Template_Guide_v2_0.md`

````markdown
# RHACO Build Prompt Template Guide — Running the Self-Verifying Build Prompt

*Reference Document | Version 2.0 | September 7, 2026*
*Companion to: RHACO_Build_Prompt_Template_v2_0*

Structure credited to `rawprogress/fable-cities` (accessed 2026-09-03; see the template's provenance block). Wording, generalisation and the v2.0 additions are RHACO's; the additions are drawn from one run (RHACO-CMP-20260903-001, n = 1) and are structural, not performance claims.

## 1. What this prompt is

A single instruction that turns an agentic coding tool into a small organisation: builders who own folders, one integrator who owns core and every shared thing, critics who score against an external reference and write no code, a claim auditor who reads prose against artifacts, and a persisted state file the whole thing loops on until it declares one of four terminal states.

Three components carry most of the value. If you adopt nothing else, adopt these:

1. **A qualified probe the builder must run before saying "done"**, whose output the critic can look at, and which has been shown to fail on known-bad cases.
2. **A separate critic** that never touches code and scores against something outside the project.
3. **A separate claim audit** that reads every prose behaviour claim against the artifact it describes. Without it the harness produces true code and false prose about it, and cannot see that it is doing so (RHACO-ANL-20260905-001 section 6.2).

Everything else (waves, integrator, blind gate, state file) reduces cost and thrash.

## 2. When to use it — and when not

Use it when all of the following hold: the deliverable splits into 8–15 subsystems with real interfaces; a script can produce an inspectable artefact from the current build (screenshot, rendered page, benchmark table, golden diff, test report); a concrete external reference exists to score against; you can afford the budget — the source project consumed ~20M output tokens across six runs and did not clear its own bar; the RHACO run consumed 20 of 28 builder rounds and ended BOUNDED_FAIL.

Do not use it for single-module tasks, for outputs judged only subjectively with no comparable artefact, or where "keep going without asking" is unacceptable — unless the gated or reviewed human-gate policy (section 6) is selected.

## 3. Filling the slots

Work top to bottom. Slots marked ★ determine whether the harness functions at all.

### Goal block

| Slot | What goes in it | Weak | Strong |
|---|---|---|---|
| `TARGET_CLASS` | A named external product/standard the output is measured against | "a good city builder" | "a Cities: Skylines II–class city builder" |
| `STACK` | Language, framework, build tooling, module system | "JavaScript" | "Three.js (latest) + Vite, plain ES modules" |
| `QUALITY_BAR` | 3–6 observable properties | "high quality" | "PBR materials, plausible sun/sky/shadows, believable traffic" |
| `ANTI_PATTERN` | The one thing that fails the project on sight | "bugs" | "programmer art" / "hand-written SQL in handlers" |

### Architecture block

| Slot | Notes |
|---|---|
| `KNOWN_CONSTRAINTS` | Every limit of stack, runtime, data, budget and authority; each becomes a CONSTRAINTS.md row with basis, design consequence and user-visible limitation. |
| `MODULE_LIST` | 8–15 nouns. Each becomes a folder, a builder, a showcase mode, a critic target. Group by data ownership. |
| `CORE_DATA_MODEL` | The one shared schema. Only the integrator edits it. |
| Shared things | Name every shared block (markup, vocabulary, contract) in ARCHITECTURE.md with its owner. The RHACO run's integrator crossed ownership lines three times, every time because a shared thing had no owner by rule. |
| `UNITS_AND_CONVENTIONS`, `DETERMINISM_POLICY`, `PERF_BUDGET`, `ASSET_DATA_POLICY` | As before. PERF_BUDGET numbers appear in PROBE_LOG_FIELDS so the critic sees them without trusting the builder. |

### ★ Verification block

Your `PROBE_OUTPUT` must pass one test: **is it directly comparable to `REFERENCE_CORPUS`, and can a second agent inspect it without running the build?**

| Domain | `PROBE_ACTION` | `PRESET_KIND` | `PROBE_OUTPUT` | `PROBE_LOG_FIELDS` | `KNOWN_BAD_CLASSES` |
|---|---|---|---|---|---|
| Web/3D app | load in headless browser | camera + time of day / route + viewport | PNG | console errors, fps, draw calls | missing asset; wrong shader; stalled frame |
| Data pipeline | run on fixture set F | fixture + config profile | golden-output diff, summary stats | exit code, stderr, wall time, peak RSS, schema validation | wrong join; dropped rows; stale schema |
| HTTP service | boot, run golden request set | request set + load profile | response diff, latency histogram | 5xx count, p50/p95/p99 | wrong record for key; stale cache; auth bypass |
| Document generator | render to PDF/HTML | page + viewport | rendered page image | lint errors, broken links | missing section; wrong cross-ref; overflow |
| Corpus explorer (RHACO run) | drive the local app | preset + retrieval mode | screenshot + JSON observations | console errors, failed requests, result ids | wrong doc for id; stale card; reversed edge; broken jump; runtime error |

`PROBE_ROUNDS`: the per-module MAX_ROUNDS plus one per wave that adds a surface. In the RHACO run the probe spent three of four rounds before the surface it had to qualify existed.

Fault predicate: the probe FAILs on any bound violation, missing capture, or non-empty error channel. The RHACO run's first probe returned `ok: true` on a 404 with a console error because `ok` meant "captured".

Fixtures: derive from the production corpus's loader-resolved types; census fixture-vs-production types at round 0. The RHACO run's hand-authored fixture quoted every date; 60% of the live corpus did not, and four green rounds could not see the crash.

### Orchestration block

| Slot | Notes |
|---|---|
| `ORCHESTRATION_MECHANISM` | Name what exists in your environment. Sequential waves preserve the critic/builder separation, which is the part that matters. |
| `WAVE_1/2/3_MODULES` | Wave 1: no upstream dependencies (include the probe and the diagnostics surface). Wave 2: consumes wave-1 APIs. Wave 3: integration. |
| `CORE_PATH` | Integrator-only. |
| Dispatch discipline | Every dispatch is recorded in STATE_FILE before the strand returns (three RHACO strands ran with no record and were reconstructed after the fact). Text carried verbatim into a dispatch is diffed against its archive at dispatch time (a retyped apostrophe drifted one dispatch). A proposed control is shown executable on the surface that will run it before it is recorded (a Workflow script had no filesystem access). Generated prompt boilerplate carries no round-specific or self-referential literal (a hard-coded `R02_` told later rounds to overwrite an earlier report). |

### ★ Critic and audit block

| Slot | Notes |
|---|---|
| `CRITIC_PERSONA` | A named professional role with a reputation to protect and no stake in the code. "Writes no code" removes the incentive to defend anything. |
| `REFERENCE_CORPUS` | Real, external, concrete, with provenance in REFERENCE.md. |
| `CALIBRATION_ARTIFACTS` | Three things of known quality. Without them the scale is ordinal: say so in SCOPE.md and never read PASS from it. |
| `ANCHOR_10 / 8.5 / 7 / 5` | Each recognisable from the probe output alone. |
| `PASS_THRESHOLD` | Aspirational (drives quality, expect to fail) or achievable (drives closure). State which. |
| `ZERO_TOLERANCE_CONDITION` | Zero console errors / failing tests / schema violations. |
| `MAX_ROUNDS` | 3–5. Past that the fix is a contract change, not another round. |
| Claim audit (5a) | A separate agent after each merge. State in LAYERS.md which claim classes have a mechanical grammar (a citation auditor, a docstring-vs-signature check) and which remain a reader's. Every prose behaviour claim ends up with a named check or an `UNVERIFIED` tag. |

### Authority and identity block

| Slot | Notes |
|---|---|
| `SUBSTRATE_PATHS` | The corpus, database, service or repository the artifact reads and must never write. Verified by a closeout hand with hashes, never asserted by the build. |
| `PROTECTED_CONTRACTS` | CORE_DATA_MODEL, public APIs, the accepted default configuration of any upstream system. |
| `IDENTITY_SURFACES` | Config-file sha + model key; system-prompt model sentence; per-request model field as a family check. In the RHACO run a client safeguard swapped the orchestrator's model mid-session on the build's own fault-injection vocabulary, the system prompt still named the old model two changes later, and the per-request field stripped the context-window suffix — no single surface would have caught it. Set the client's switch behaviour to halt. |

### Rules block

| Slot | Notes |
|---|---|
| `LIVE_CONDITION` | Dev server up; fixtures runnable from clean checkout; main green. |
| `HUMAN_GATE_POLICY` | Section 6. |

## 4. State file schema

```json
{
  "run": 7,
  "updated": "2026-09-07T02:00:00Z",
  "client": { "identity_of_record": {"config_sha": "...", "model": "...", "effort": "..."},
              "history": [ {"round": 6, "config_sha": "...", "model": "...", "prompt_model": "...", "request_model": "..."} ] },
  "dispatch_records": [ {"strand": "S3-B1", "role": "builder", "model": "...", "effort": "...", "pattern": "...",
                          "agent_type": "...", "execution_mode": "concurrent", "dispatched_utc": "...", "returned_utc": null} ],
  "modules": {
    "terrain": { "ref_gap": 8.1, "round_delta": 0.4, "iso_vs_integrated": 0.0, "rounds": 3, "status": "open",
                 "issues": ["LOD pop at 400 m"], "unverified": ["fits 1280 px as rendered — no browser in strand"] },
    "sky":     { "ref_gap": 8.6, "round_delta": 0.1, "iso_vs_integrated": 0.0, "rounds": 2, "status": "pass", "issues": [], "unverified": [] }
  },
  "integrator_queue": ["roads -> core: add lane-count to RoadSegment"],
  "assumptions": ["Using metres, +Y up per ARCHITECTURE.md 2"],
  "layer_gaps": [ {"found_by": "L3", "missed_by": "L2", "item": "..."} ],
  "claim_audit": { "last_run": "...", "match": 169, "mismatch": 0, "unverifiable": 8 },
  "final_gate": { "whole_ref_gap": null, "blind_ab": [] },
  "terminal_state": null
}
```

`unverified` entries are never deleted by the integrator; they are retired only by a cited check. "Resume from the weakest module" is `min(ref_gap)` over `status == open`. The "never inflate" rule applies to this file first.

## 5. Running it

1. Fill every slot. Grep for `{{` — zero hits before launch.
2. Delete the guidance comments; they cost tokens on every turn. v2.0 is roughly twice the length of v1; budget for it.
3. Start from an empty folder.
4. Expect the first run to end at a usage limit partway through wave 1; the state file makes run 2 cheap.
5. Read `ARCHITECTURE.md` after the first run and before the second — the cheapest point to correct.
6. Read the critic and claim-audit outputs raw. Rounds where scores go down are the signal that the critic is working; a claim audit that finds nothing on a fresh tree is the signal that it is not.
7. When a module hits `MAX_ROUNDS` without passing, do not add rounds. Look for a contract problem and route it through the integrator.
8. At every round boundary, read the identity surfaces before reading anything else.

## 6. Human-gate policy

- **Autonomous.** Assumptions land in the state file for post-hoc review. Suitable when the cost of a wrong routine decision is a redo, not a loss.
- **Gated.** Autonomous except for Authority-boundary items. Recommended default for anything you will maintain.
- **Reviewed.** Nothing starts a new wave until a human ratifies the previous state file. Appropriate when outputs feed a governed record or a two-instance workflow with a human ratifying authority between instances.

Pick one and delete the others.

## 7. Cost and threshold calibration

Source project: six runs, ~20M output tokens, best module 2.5 points below the 8.5 bar, blind judging lost every round. RHACO run: one run, 20 of 28 rounds, nine objective gates PASS, 11 of 12 presets, BOUNDED_FAIL on an uncalibrated scale and an unconverged claim class. Both harnesses produced honestly-scored results; neither met its own goal. Budget by wave; if closure matters more than ceiling, set `PASS_THRESHOLD` where a strong module lands on round 2 and let the anchors carry the quality signal; check the reference corpus before lowering the bar.

## 8. Failure modes to watch

| Symptom | Likely cause | Fix |
|---|---|---|
| Every module passes round 1 | Critic is scoring the builder's description, not the probe output | Enforce "critic runs its own probe"; check `PROBE_OUTPUT` is inspectable |
| Probe green, product broken on real data | Fixture reproduces the authors' conventions | Derive the fixture from loader-resolved production types; type census at round 0 |
| Docstrings, notices and design docs disagree with the code | No layer reads claims against referents | Run the claim audit after every merge; tag or check every prose claim |
| A builder's "unverified" vanishes at integration | State schema has no first-class UNVERIFIED | Add it; integrator may retire only with a cited check |
| Scores oscillate without converging | Contract problem disguised as a quality problem | Route through integrator; freeze the API |
| Integrator editing builder folders | Shared things with no owner by rule | Assign in ARCHITECTURE.md; contract test per shared block |
| Critic scores drift between rounds | Anchors not specific, or scale uncalibrated | Calibrate on known artifacts; freeze anchor text |
| Model or effort changed and nobody noticed | Identity read from one surface, or client set to retry | Read the conjunction each round; set the client to halt |
| Blind judge always picks the reference | Expected for a novel build | Track margin over runs |
| Agent asks questions despite autonomous policy | Slot left vague | Fill it |

## 9. Minimal worked instance (non-visual)

- `TARGET_CLASS`: "a dbt-class transformation layer"
- `PROBE_TOOL`: `tools/probe.py`, runs the DAG on `fixtures/small/` (derived from production types) and `fixtures/skew/`
- `PROBE_OUTPUT`: golden-output diff + summary-stats table per model
- `PROBE_LOG_FIELDS`: exit code, stderr, wall time, peak RSS, schema-validation result
- `KNOWN_BAD_CLASSES`: wrong join key; dropped rows; stale schema; silent null coercion
- `REFERENCE_CORPUS`: a published dbt project of comparable scope and its documented outputs (provenance in REFERENCE.md)
- `CRITIC_PERSONA`: principal data engineer doing a production-readiness review, writes no code
- `ANCHOR_8_5`: "all models idempotent, documented, tested; diff vs. golden empty; one reviewer nit per model"
- `SUBSTRATE_PATHS`: the warehouse schemas the layer reads
- `IDENTITY_SURFACES`: client config sha + model key; system-prompt sentence; per-request model
- `ZERO_TOLERANCE_CONDITION`: zero failing tests, zero schema violations
- `LIVE_CONDITION`: `make probe` runs green from a clean checkout

## 10. Pre-launch checklist

- [ ] No `{{` remains
- [ ] `PROBE_OUTPUT` and `REFERENCE_CORPUS` are the same medium
- [ ] Critic can run the probe without the builder's help
- [ ] `KNOWN_BAD_CLASSES` enumerated; each asserts on a rendered observable
- [ ] `PROBE_ROUNDS` budgeted separately from module rounds
- [ ] `CALIBRATION_ARTIFACTS` named, or the scale declared ordinal in SCOPE.md
- [ ] `REFERENCE.md` provenance fields planned (source, version/date, access date, properties compared)
- [ ] Claim-audit grammar boundary stated in LAYERS.md
- [ ] `SUBSTRATE_PATHS` named; closeout hand assigned
- [ ] `IDENTITY_SURFACES` named; client switch behaviour set to halt
- [ ] Every shared thing has an owner in ARCHITECTURE.md
- [ ] One human-gate policy selected, others deleted
- [ ] `ORCHESTRATION_MECHANISM` names something that exists in this environment
- [ ] `STATE_FILE` path exists and is git-tracked; dispatch records written before strands return
- [ ] Token budget for wave 1 estimated and acceptable

---

## Version History

| Version | Date | Notes |
|---|---|---|
| 2.0 | 2026-09-07 | First filed version, companion to Template v2.0. Adds the claim audit as the third core component, the known-bad-classes / probe-rounds / substrate / identity slots, the state-file schema with three numbers, UNVERIFIED, dispatch records and identity history, dispatch discipline, and five failure-mode rows drawn from the RHACO-CMP-20260903-001 run. Cut by RHACO-CHG-20260907-002. |

---

*Reno High-Altitude Cosmic Ray Observatory (RHACO) | Kris E. Granholm, Director*
````

---

*Reno High-Altitude Cosmic Ray Observatory (RHACO) | Kris E. Granholm, Director*
