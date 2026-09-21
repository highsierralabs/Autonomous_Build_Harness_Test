# RHACO-ANL-20260905-001 — Amendment A1: Gate-Caught Class (b) Instance and the Guide v1.4 Residual

*Reno High-Altitude Cosmic Ray Observatory (RHACO) · 5,050 ft ASL · 39°N*

| Field | Value |
|---|---|
| Document type | ANL Amendment |
| Amends | RHACO-ANL-20260905-001 Corpus Explorer Harness Evaluation, as filed 2026-09-05 at `f38e61a` (sha256 `c6b6421c5734e797de1f01476f15b61c90f40569c1dd4d95548dde5f58c04b03`, 31,386 B) |
| Amendment number | A1 |
| Author | Kris E. Granholm, Director, RHACO |
| Date | 2026-09-05 UTC |
| Naming convention | v1.17 · Style RSG v1.9 · Schema Card YAML v1.9 |

## A1.1  Reason for amendment

Two instances of the parent's class (b) — a claim in prose that nothing checks against the artifact — arose after the parent was filed, in the documents that closed the campaign. The parent's section 6.5 counts three chat-side instances and section 8 leaves the claim-audit question to a downstream ratification; the evidence below bears on both and has no other governed home. The parent's bytes are not edited.

## A1.2  The two instances

**Instance 4 — caught by a gate.** The RHACO-CHG-20260905-003 section 5 Execution Record, authored by Claude Code at discharge, tabulated the four baselined citation mis-bindings with the target and anchor in adjacent cells, `| RHACO-CHG-20260905-001 | §8 | … |`. The auditor read each row as a citation of a section that does not exist and returned MISMATCH +3 (312 → 315) at the discharge gate, every finding citing the record at its own lines 242–244. Corrected to the prose form the CHG bodies use (`section N`), re-measured to 312 MATCH exit 0, folded into the unpushed commit; recorded in the Execution Record rather than repaired silently. The record about anchors binding to the nearest preceding identifier had bound three anchors to the nearest preceding identifier. This is the same class as the parent's section 6.5 rows and the parent's own line 181; it differs in one respect only, and that respect is the finding: it was found before it left the machine, by an instrument, not after ratification by a reader.

**Instance 5 — not caught by anything mechanical.** Guide v1.4 section 3 opens "Note the corrected #4 definition and the held status of #3." above a table whose row 3 now records promotion. The v1.3 sentence survived because RHACO-CHG-20260905-002 CS-1 enumerated nine Before/After strings and this sentence was not among them; the executor applied the nine exactly and the gate passed, because no instrument reads a sentence about a table against the table. Found by the receiving chat's full-file read of the cut at session close; corrected by Guide v1.4 Amendment A1 (Code-side, REF amendment path).

## A1.3  What the pair adds to section 8

The parent records that no harness layer audits a claim against its referent, and reserves the claim-audit layer to a downstream ratification. Instances 4 and 5 are a matched pair on that question: one claim fell inside the citation auditor's anchor grammar and was caught by a gate; one fell outside every grammar the repository has and was caught by a reader. The auditor is therefore already a claim-audit layer — a narrow one, for one claim class, with a grammar that defines what it can see (Charter: measurement defines category). The design question a claim-audit layer poses is not whether to build one but which claim classes to give a grammar to, and which remain a reader's; the day's five instances split four to one. Nothing here changes the parent's classification, its layer separation, or its section 9 reservations.

## A1.4  No other changes

Sections of the parent not named above remain authoritative as filed. Era-correct preservation: the parent's line 181 remains on disk as filed and is baselined at 312.

## Cross-references

RHACO-ANL-20260905-001 (parent) · RHACO-CHG-20260905-003 section 5 (instance 4 of record) · RHACO-CHG-20260905-002 CS-1 (the nine-edit list) · RHACO_Subagent_Pattern_Application_Guide_v1_4 (instance 5; corrected by its Amendment A1) · RHACO-CMP-20260903-001 section 9 (claim-audit layer as downstream item).

---

*Reno High-Altitude Cosmic Ray Observatory (RHACO) | Kris E. Granholm, Director*
