# RHACO-HND-20260903-001 — Amendment §A1: Concurrency Cap Re-homed, D-3 Strand Prefix, Fixture Carve-out, Refusal Rule, Session-2 Findings

*Reno High-Altitude Cosmic Ray Observatory (RHACO) · 5,050 ft ASL · 39°N*

| Field | Value |
|---|---|
| Document type | HND Amendment (Class F) |
| Amends | RHACO-HND-20260903-001 Corpus Explorer Autonomous Build Dispatch, as filed 2026-09-03 (sha256 `ed01fa5412238767a55f30108844295a10bedc0ab6d1f7e5aca4c373c206ff6f`, 23,306 B) |
| Amendment number | §A1 |
| Execution route | `ops` (unchanged from parent; no new RHACO-tree target) |
| Status | READY |
| Author | Kris E. Granholm, Director, RHACO |
| Date | 2026-09-04 UTC |
| Naming convention | v1.17 · Style RSG v1.9 · Schema Card YAML v1.9 |

## §A1.0  Interpretive context (no spec change)

D-13's last clause requires the cap variables to be verified live, never
assumed. Session 2 did so and found the concurrency half unenforced in the
running client. That is the discipline working: the surface was measured
before it was relied on. This amendment re-homes the wave cap to the layer
that can enforce it and records the measurement; it does not weaken the cap
or the spawn-depth guard.

## §A1.1  Reason for amendment

Session 2 (resumption entry 2, `working\HND-20260903-001_report.md`) halted
at parent §0.2 item 9(b): with `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS=3` in the
client process, a fourth concurrently dispatched strand ran at once in every
measured form (18-strand probe record, `working\preflight_findings_HND-20260903-001.md`).
The spawn-depth half holds in the strongest form — a depth-1 strand has no
spawn tool. Every other §0 item passed. Three findings surfaced alongside the
halt bear on the parent's text: the client's sleep rail steers strands to
background execution unless the prompt forbids it (a D-3 / F-1 hazard the
parent's §2 L text does not cover); an Explore-typed strand refused a
governance-framed prompt as suspected injection while general-purpose strands
complied (§2 I types the critic and inspection strands Explore); and §2 C's
zero-hit grep and §2 F's module-built fixture index are in tension. Director
disposition 2026-09-03: amend, do not hold.

## §A1.2  Patch — replace parent §0.2 item 9(b)

**Disposition for executor:** Apply instead of parent §0.2 item 9(b).

Parent text (abridged): "…(b) `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` and
`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` are honored (set 1 and 3, spawn a
trivial read-only probe strand, confirm a nested spawn is refused and a fourth
concurrent is queued)…"

Replacement (b): both variables present in the client environment at launch,
values 1 and 3, recorded. Spawn depth verified live: a depth-1 probe strand
has no spawn tool (session-2 result; re-verify per §2 M on any client-version
change). Concurrency: record whether the client enforces the variable; in
2.1.260 it does not (session-2 record). Non-enforcement is recorded, not a
halt — the wave cap is enforced under §2 I as amended by §A1.3. Gate 9(b)
passes when both variables are present and the spawn-depth check holds.

## §A1.3  Patch — replace the caps paragraph of parent §2 I

**Disposition for executor:** Apply instead of parent §2 I, caps paragraph
only (from "Caps:" to the end of the item). The tier table, escalation rule,
and the seven-field dispatch record are unchanged except as extended here.

Replacement: Caps. `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` and
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

## §A1.4  Patch — extend parent §2 L strand prefix

**Disposition for executor:** Apply instead of parent §2 L. The D-12 block is
retained verbatim; a second block is appended immediately after it and is
part of the text carried at the top of every strand prompt.

> Foreground only (RHACO Guide v1.3 D-3). Do not use `run_in_background`,
> do not detach, do not sleep-and-poll a background job. Work that exceeds
> your budget is walked in sequential foreground invocations or returned as
> WAITING. A backgrounded process is a halt, not a retry.

Reason of record: the client's sleep rail steers strands into background
execution absent an explicit prohibition (session-2 finding); F-1 is the
prior instance of this shape.

## §A1.5  Patch — reconcile parent §2 C and §2 F

**Disposition for executor:** Apply instead of parent §2 C and §2 F.

§2 C, replacement: the L1 static check greps the workspace for the five
index-writing names outside `CONSTRAINTS.md` / `docs/` and allowlists
exactly one file, `fixtures/build_fixture_index.py`; the check passes only
when every hit is in that file. Any hit elsewhere is a defect recorded per
round in `build_state.json`. `corpus_index.db` is never opened outside the
module's own `connect`.

§2 F, replacement: fixture corpus and fixture index live under `fixtures/`.
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

## §A1.6  Patch — strand-refusal rule under parent §3

**Disposition for executor:** Apply after parent §3 completes (additive to
the standing-halt list; adds no step to the prompt's execution loop).

A strand that declines its prompt — as suspected injection or otherwise
returning no work — is recorded in `docs/rounds/` as a round outcome
`REFUSED` with the refusal text verbatim. The orchestrator may re-dispatch
once with the task stated first and the §2 L text (as amended) retained
verbatim after it — never removed, never paraphrased. A second refusal on the
same strand objective is a halt. Refusals consume round budget. §2 I's
agent types are unchanged: the critic and the §1 inspection strands stay
Explore.

## §A1.7  Patch — parent §8 acceptance criteria 2 and 6

**Disposition for executor:** Apply instead of parent §8 items 2 and 6.

Item 2: M0 complete: `PROMPT.md` and `RATIONALE.md` pinned on disk and
committed unchanged; `DISPATCH_PARAMETERS.md` byte-identical to parent §2 as
amended — parent §2 with items C, F, the §2 I caps paragraph, and L replaced
by §A1.5, §A1.5, §A1.3, and §A1.4 respectively; the assembled text is
recorded in the handback with its sha256.

Item 6: every dispatch in `build_state.json` carries the seven governance
fields and both timestamps; models are client-reported strings; zero spawns
outside the tier map; zero nested spawns; zero `concurrency_exceedance`;
escalations, if any, logged with the two-failed-round evidence (CMP
criterion 5).

## §A1.8  Session-2 facts of record (no spec change)

Tier strings of record, client 2.1.260: `claude-sonnet-5`,
`claude-opus-5[1m]`, `claude-haiku-4-5-20251001`. The `opus` pin resolving to
`claude-opus-5[1m]` repeats the CCX-20260825-002 §4 item 5 exemplar; the
handback carries the captured string. R-A8 closed: the 00:16:28Z npm rewrite
of 2.1.260 was the Director's manual update, auto-updater disabled. R-A10:
the SessionStart hook remains excised and its restoration is a
CMP-20260815-002 pilot-close item, not this hand's. Workspace at session-2
close: git repository, no commits, `PROMPT.md` and `RATIONALE.md` untracked
and byte-identical to their pins, `preflight\` (two evidence scripts)
untracked, `.venv` self-ignored. `preflight\` is committed with the first
build commit as evidence, not product.

## §A1.9  No other changes

Sections of the parent not listed above remain authoritative as written,
including §0 items 1–8, 9 identity, 9(a), 9(c), 10–14, §1, §2 A–B, D–E,
G–H, J–K, M–N, §3 (extended only), §4–§7, §8 items 1, 3–5, 7–12, §9–§10.
Session 3 re-enters per §2 M at §0 item 9(b) as amended, then opens §1.

## §A1.10  Disposition

Retain permanently as amendment. The parent is a single-run hand; no full
revision is planned.

## Cross-references

RHACO-HND-20260903-001 (parent) · RHACO-CMP-20260903-001 (§4 caps; §6 REVIEW
triggers not fired — no cap violation, a mechanism finding) ·
RHACO_Subagent_Pattern_Application_Guide_v1_3 (D-3, D-9, D-12, D-13) ·
RHACO-CCX-20260903-001 §4 (filing convention for halts) ·
RHACO-CCX-20260825-002 §4 item 5 (asserted-vs-captured) ·
RHACO_HND_Specification_v1_1 §4.6, §5.7.

---

*Reno High-Altitude Cosmic Ray Observatory (RHACO) | Kris E. Granholm, Director*
