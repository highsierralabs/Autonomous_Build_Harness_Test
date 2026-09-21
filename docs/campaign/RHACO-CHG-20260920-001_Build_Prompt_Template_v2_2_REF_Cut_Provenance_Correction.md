# RHACO-CHG-20260920-001 — Build Prompt Template v2.2 and Guide v2.2: REF Cut Correcting the Upstream-Provenance Statement

*Reno High-Altitude Cosmic Ray Observatory (RHACO) · 5,050 ft ASL · 39°N*
*RadiaCode RC-110-003225 · CsI(Tl) · 30 mm Pb walls / 40 mm Pb lid · sealed castle*

| Field | Value |
|---|---|
| Document type | CHG (Rule / schema codification — REF cut) |
| Status | Baseline |
| Execution route | docs |
| Target campaign | None — the v2.x lineage is a REF family; the build campaign it came from is closed and untouched |
| Predecessor CHG | RHACO-CHG-20260907-004 (v2.1 cut) |
| Priority | MEDIUM — blocks the public prompt-evolution account, which must not repeat a false provenance statement |
| Author | Kris E. Granholm, Director, RHACO |
| Date | 2026-09-20 UTC |
| Naming convention | v1.17 · Style RSG v1.9 · Schema Card YAML v1.9 · CHG Specification v1.0 |

## §1  Rationale

RHACO-ANL-20260920-001, finding S-6(c), measured a provenance error of record. The provenance paragraph of the Build Prompt Template, at line 10 of both the v2.0 and the v2.1 file, states that the upstream `rawprogress/fable-cities` prompt "as retrieved is retained as `working\PROMPT_TEMPLATE.md`, sha256 `d1f2dee6…`". The hash is right for that file and the claim is wrong about what the file is.

Chat re-read the premise on 2026-09-20 rather than carry it from the analysis: `working\PROMPT_TEMPLATE.md` measures 7,908 B, SHA-256 `d1f2dee6dbdbc0a3ef13b3afceb468ef326347baeef98a2c8844763e23e7a36d` (`hash_file`), and its own header reads "Boilerplate derived from the harness structure in `rawprogress/fable-cities/PROMPT.md`. Fill every `{{SLOT}}`." It is the v0 generalisation that the same paragraph describes in its next clause, not the retrieved upstream. The same sentence is present at line 10 of both template files (chat `grep_files`, two matches in four files; the two Guides do not carry it and defer to the template's provenance block).

The analysis also measured what is recoverable, Code-side and not re-measured by chat: the public upstream history is one commit, `aea8b1035030952555395de0c1de14ba693a1427`, committed 2026-09-02T22:47:42Z, some seventeen hours before the recorded access of 2026-09-03 at about 15:30 UTC; its `PROMPT.md` is blob `c2bc981d4af76130f8ad88f2ddd857491c517c72`, 5,742 B, SHA-256 `29815365b64ec65e9c9bbbdb429eb8b8352e21ccaa6887db6a302082f9565972`; no file of that hash or that size exists in the RHACO tree; and the upstream tree carries an MIT licence file, "Copyright (c) 2026 raw". The bound stands as the analysis states it: a rewrite of the upstream history after the access would be undetectable.

The Director ruled on 2026-09-20 to cut v2.2 rather than carry the correction as an erratum alone: the template is the artifact the public Corpus Explorer record will present as the current prompt, and its head should not state something known to be false. Per CHG Specification v1.0 section 8 the correction is a new cut, never an in-place edit. **v2.2 changes no mechanism.** It corrects one paragraph's account of its own sources, pins the upstream, and records the upstream licence.

The Guide is cut in lockstep with no content change, so the companion pointers of both live heads resolve to live heads; the pair has versioned together at every prior cut. A template-only cut was offered as the alternative; the Director ruled for lockstep at ratification on 2026-09-20.

Premise pins (chat `hash_file`, 2026-09-20T20:39Z, full-file): Template v2.1 `6ee71cf7a16a4b63927fb11f30bb8ab07f2ef7ea30c664711dc4f6fa131b5b2d`, 22,742 B, blob `5896b2ed83cc065b1898b895f1975877c33ce7be`; Guide v2.1 `50c397f3bdf8418274d1a0a90e02961030367661270b1cdb3019a2c2e410c3c4`, 18,614 B, blob `4045c8f92be18eedd62d35af87bf27fbf6be4421`. Server 0.28.0, librarian 1.19, NC 1.17, RHACO head `839544857384`, corpus-index card count 1573 (index readback, not a census).

## §2  Change Specification

Edit form throughout, as in the predecessor: each anchor is quoted as it stands in v2.1, one raw line per fence, including the U+2026 ellipsis where one appears; the executor asserts anchor count == 1 in the byte copy before replacing, and a count other than 1 is a HALT. Replacement text lands verbatim. All assertions are made before the first byte is written.

### CS-1  `docs\reference\RHACO_Build_Prompt_Template_v2_2.md` — new REF, from a byte copy of v2.1 with edits T-1 to T-5

**T-1  Header, two lines.** Anchor and replacement for the version line:

```
*Reference Document | Version 2.1 | September 7, 2026*
```
```
*Reference Document | Version 2.2 | September 20, 2026*
```

Anchor and replacement for the companion line:

```
*Companion to: RHACO_Build_Prompt_Template_Guide_v2_1, RHACO_Measurement_Philosophy_v1_4_1*
```
```
*Companion to: RHACO_Build_Prompt_Template_Guide_v2_2, RHACO_Measurement_Philosophy_v1_4_1*
```

**T-2  Provenance paragraph, the retained-copy parenthetical.** Anchor:

```
(commit not captured; the file as retrieved is retained as `working\PROMPT_TEMPLATE.md`, sha256 `d1f2dee6…`).
```

Replacement:

```
(the commit was not recorded at access, and the retrieved bytes were not retained. Measured on 2026-09-20 by RHACO-ANL-20260920-001: the public upstream history is a single commit, `aea8b1035030952555395de0c1de14ba693a1427`, committed 2026-09-02T22:47:42Z, some seventeen hours before the access; its `PROMPT.md` is blob `c2bc981d4af76130f8ad88f2ddd857491c517c72`, 5,742 B, sha256 `29815365b64ec65e9c9bbbdb429eb8b8352e21ccaa6887db6a302082f9565972`, the only version that history carries. A rewrite of the upstream history after the access would leave no trace and cannot be excluded. The upstream tree carries an MIT licence file, Copyright (c) 2026 raw).
```

**T-3  Provenance paragraph, the v0 clause.** Anchor:

```
v0 was that structure generalised; v1 was its rewrite
```

Replacement:

```
v0 was that structure generalised (`working\PROMPT_TEMPLATE.md`, sha256 `d1f2dee6…`, 7,908 B); v1 was its rewrite
```

**T-4  Provenance paragraph, lineage sentence.** After the anchor below, insert one space and the sentence that follows it.

```
three generalisations; no run has yet validated any v2.x mechanism.
```
```
v2.2 corrects this paragraph's own account of what was retained and pins the upstream (RHACO-CHG-20260920-001); it changes no mechanism.
```

**T-5  Version History.** Append one row after the 2.1 row:

```
| 2.2 | 2026-09-20 | Provenance correction only; no normative change. The v2.0 and v2.1 provenance paragraphs stated that the upstream file as retrieved was held at `working\PROMPT_TEMPLATE.md`; that file is the v0 generalisation, and no byte-identical copy of the upstream was kept (RHACO-ANL-20260920-001, finding S-6(c)). The paragraph now says so, places the `d1f2dee6…` pin on v0 where it belongs, pins the upstream's single public commit and its `PROMPT.md` blob as measured on 2026-09-20 with the stated bound, and records the upstream licence. Cut by RHACO-CHG-20260920-001. |
```

Residual checks on the v2.2 template, each written so that no directed text contradicts it: the string `is retained as` occurs zero times; the `{{` count equals the v2.1 file's count, measured on the byte copy before the edits; a line diff of v2.1 against v2.2 touches exactly lines 3, 4 and 10 and adds exactly one line, the 2.2 row; the file is LF with a CR-byte count of zero, measured by byte count and not by pattern.

### CS-2  `docs\reference\RHACO_Build_Prompt_Template_Guide_v2_2.md` — new REF, from a byte copy of v2.1 with edits G-1 and G-2

**G-1  Header, two lines.**

```
*Reference Document | Version 2.1 | September 7, 2026*
```
```
*Reference Document | Version 2.2 | September 20, 2026*
```

```
*Companion to: RHACO_Build_Prompt_Template_v2_1*
```
```
*Companion to: RHACO_Build_Prompt_Template_v2_2*
```

**G-2  Version History.** Append one row after the 2.1 row:

```
| 2.2 | 2026-09-20 | Companion to Template v2.2. No content change. The template's provenance paragraph was corrected (RHACO-CHG-20260920-001) and the pair is cut in lockstep so that each live head names a live companion. |
```

Residual checks on the v2.2 guide: a line diff against v2.1 touches exactly lines 3 and 4 and adds exactly one line; LF with zero CR bytes.

### CS-3  Cards for CS-1 and CS-2 (new, Code)

Two sibling `.card.yaml` files mirroring the field shapes of the live v2.1 REF cards. `current_version` the quoted string `"2.2"`; status `Active` (Channel 1); programs `[Infra]`; `last_human_review` `"2026-09-20"`. `depends_on`: this CHG; the v2.1 predecessor of the same document (note "predecessor cut, superseded by this version"); the Measurement Philosophy v1.4.1. `see_also`: carry the v2.1 card's set forward and add RHACO-CHG-20260907-004 and RHACO-ANL-20260920-001. Abstracts authored from the landed v2.2 bodies, not from this CHG; the template's abstract states that v2.2 is a provenance correction with no normative change.

### CS-4  v2.1 cards to Superseded (in-place, Code)

`RHACO_Build_Prompt_Template_v2_1.card.yaml` and `RHACO_Build_Prompt_Template_Guide_v2_1.card.yaml`: `identity.status: Active` to `Superseded`; `superseded_by: null` to the mapping `{id: RHACO_Build_Prompt_Template_v2_2, note: "v2.2 cut by RHACO-CHG-20260920-001; provenance correction, no normative change; v2.1 retained as filed"}` (Guide: `id: RHACO_Build_Prompt_Template_Guide_v2_2`); `last_human_review` to `"2026-09-20"`; one notes entry naming this CHG. The two fields move together (Channel 1 rule). Bodies untouched.

**Not directed.** The v2.0 pair and its cards: already Superseded, bodies untouched, and the same sentence stands in the v2.0 template as filed; the record of the error is this CHG and the v2.2 version-history row, reached from v2.0 by its supersession chain. The payload copy of that sentence inside RHACO-CHG-20260907-002. Every file under `working\`. The three drafted public documents, which inherit the statement and are corrected chat-side in the public-release work. Any code, test, tool or configuration: chat `grep_files` for the template's filename stem found no hit outside `docs\` and `working\`, so no pin surface names a template version; the executor re-verifies and halts on a hit.

## §3  Changes Directed

None to production code. Executor: Claude Code, route `docs`, on `main`, under the git-governance procedure in force on disk. **Precondition:** the RHACO tree carries untracked governance pairs from this session (the 2026-09-20 handoff and its analysis); they are swept under their own identifiers before this hand opens, and this hand starts from a clean base.

Commits, subjects verbatim, one canonical identifier at position 0, printable ASCII, counted by script at authoring:

```
RHACO-CHG-20260920-001: file build prompt template v2.2 carrier CHG    (67)
RHACO-CHG-20260920-001: land build prompt template and guide v2.2      (65)
RHACO-CHG-20260920-001: supersede v2.1 REF cards and discharge         (62)
```

Commit 0 is this pair, chat-written through the MCP write surface. Commit 1 is CS-1, CS-2 and CS-3. Commit 2 is CS-4, this body's Status to Baseline, the card to Baseline, and a section 5 Execution Record.

Pre-flight: hash the two v2.1 files against the section 1 pins and halt on mismatch; copy each byte-for-byte to its v2.2 name; assert every anchor at count 1 before any write; apply; run the residual checks; re-hash both v2.2 files and record them in section 5. Expected gate: librarian at the census of record at entry plus two; citation auditor at its baseline of record at entry, read live and not carried from any document; an add attributable to this pair or to the two new REF files is attributed and halts, never baselined or waived. Halt-and-report on any pin mismatch, any anchor count other than 1, any residual-check hit, an unexpected auditor member, or a librarian mismatch.

Body lifecycle: Filed at the write; Baseline at commit 2. No Software Changelog row: no production-code version moves. No self-edge pin moves: this record is not an amendment child and its card carries no parent field.

## §4  Cross-references

RHACO-ANL-20260920-001 (finding S-6(c), the measurement this cut answers; S-6(a) and S-6(b) for the upstream pin and its bound) · RHACO-CCX-20260920-001 (the sweep's scope) · RHACO-CHG-20260907-004 (predecessor and this record's template) · RHACO-CHG-20260907-002 (v2.0 cut; carries the sentence in its payload, not edited) · RHACO-ANL-20260907-001 (the review that produced v2.0) · RHACO_Measurement_Philosophy_v1_4_1 · RHACO_CHG_Specification_v1_0 section 8 (REF cuts) · RHACO_Card_YAML_Schema_Specification_v1_9 (Superseded / superseded_by pairing).

## §5  Execution Record

Executed by Claude Code on 2026-09-20, route `docs`, on `main` from clean base `a7056dd`.
All four premise pins of section 1 were re-measured before the first byte was written and
matched exactly: Template v2.1 `6ee71cf7`, 22,742 B, blob `5896b2ed`; Guide v2.1
`50c397f3`, 18,614 B, blob `4045c8f9`. Every directed anchor asserted at count 1 before
any write; no anchor returned a count other than 1 and no halt fired.

### 5.1  Commit ledger

| Step | Commit | Note |
|---|---|---|
| 0 | `80753bd` | Carrier pair filed at status Filed |
| 1 | `30a1011` | CS-1, CS-2, CS-3 - the v2.2 pair and its two cards |
| 2 | (this commit) | CS-4, this record, and both Baseline flips |

### 5.2  Artifact pins as landed

| Artifact | SHA-256 | Bytes |
|---|---|---|
| `RHACO_Build_Prompt_Template_v2_2.md` | `5ff7554cce30d41868e0c0da45ef1991ec637a1a812a29522e90164eed2001e8` | 24,073 |
| `RHACO_Build_Prompt_Template_Guide_v2_2.md` | `000e2aa4a969385624d69bf6c010b441233c13feda8ec073b6d047fa0c8553fc` | 18,839 |

### 5.3  Residual checks

Template: the line diff against v2.1 replaces exactly lines 3, 4 and 10 and inserts
exactly one line, the 2.2 version-history row; the string naming a retained copy occurs
zero times; the slot-opening count is 64, equal to the v2.1 count measured on the byte
copy before the edits; the file is LF with a CR-byte count of zero, measured by byte
count. Guide: the line diff replaces exactly lines 3 and 4 and inserts exactly one line;
LF with zero CR bytes. Every check passed as written.

The CS-4 not-directed clause was re-verified rather than inherited: a tracked-content
search for the template filename stem returned eighteen files, all of them under the
documents tree, and none outside the documents and working trees. No pin surface names a
template version, so no halt fired.

### 5.4  Gate verdicts

Entry state, measured live at pre-flight and not carried from any document: census 1574
cards with missing 0, orphans 3, carded-with-parent 128, carded-with-code 0, broken 0,
errors 0, baseline MATCH; citation auditor exit 0, MATCH; regression 920 passed, 1
skipped, and one failure, the standing exception registered against RHACO-INC-20260829-001
in the regression-gate standing-exception registry.

Exit state after the edits: census 1576 cards, the entry census plus two, with every
membership list unchanged and baseline MATCH - the predicted delta for two paired
document-and-card additions, and the delta this record anticipated in section 3. Citation
auditor exit 0, MATCH; no finding was added, so nothing required attribution and nothing
was waived or baselined. Regression identical to entry, the same single standing-exception
failure at zero delta and no new failure.

### 5.5  Discharge

CS-1, CS-2, CS-3 and CS-4 are discharged as directed, with no deviation and no amendment.
The v2.0 pair is untouched and keeps the uncorrected sentence as filed, per the
not-directed clause. No Software Changelog row: no production-code version moved. This
record is not an amendment child and its card carries no parent field.

Chat-side and outside this hand: the three drafted public documents inherit the
uncorrected sentence and are corrected in the public-release work, not here.

---

*Reno High-Altitude Cosmic Ray Observatory (RHACO) | Kris E. Granholm, Director*
*RadiaCode RC-110-003225 | CsI(Tl) | 30 mm Pb walls / 40 mm Pb lid | 5,050 ft ASL, Reno NV*
