# RHACO-HND-20260903-001 — Amendment §A2: Convergence Rulings Ledger, Identity Pin of Record, Closeout Extensions

*Reno High-Altitude Cosmic Ray Observatory (RHACO) · 5,050 ft ASL · 39°N*

| Field | Value |
|---|---|
| Document type | HND Amendment (Class F) |
| Amends | RHACO-HND-20260903-001 Corpus Explorer Autonomous Build Dispatch, as filed 2026-09-03 (sha256 `ed01fa5412238767a55f30108844295a10bedc0ab6d1f7e5aca4c373c206ff6f`, 23,306 B), as amended by §A1 (sha256 `167771c75575ceef2d07e21a9fbfb6f00a24776ca619514cc9b9a216414be99a`, 9,698 B) |
| Amendment number | §A2 |
| Execution route | `ops` (unchanged from parent; no new RHACO-tree target) |
| Status | CLOSED |
| Author | Kris E. Granholm, Director, RHACO |
| Date | 2026-09-05 UTC |
| Naming convention | v1.17 · Style RSG v1.9 · Schema Card YAML v1.9 |

## §A2.0  Interpretive context (no spec change)

This amendment restates the Director rulings issued during sessions 3–8 of the
parent hand; it re-decides nothing. Every ruling was applied at the session it
was issued and is recorded in `working\HND-20260903-001_report.md` (sections D,
J.5, K.4, L, M) and in the workspace `build_state.json`. A2 is the governed
carrier: a rule that changed an acceptance criterion or a §2 parameter lives
here, so a reader of the hand sees the criterion the build was actually held to.
The build declared **BOUNDED_FAIL** at 20 of 28 builder rounds (PROMPT.md §12;
handback M.10). This amendment does not restate the terminal state; the handback
and the workspace record are its home.

## §A2.1  Reason for amendment

Between sessions 3 and 8 the Director issued rulings that (a) read one
acceptance criterion progressively, (b) extended the resumption protocol,
(c) narrowed one invariant by application note, (d) changed the orchestrator
identity pin after a client safeguard degraded the session model on the build's
own tool output, (e) extended the L1 static check and the closeout
reconciliation sources, and (f) set the disposition rule for integrator edits
to builder-owned files. Each was recorded at issue; none was carried as a
per-ruling amendment, by the CCX-20260905-001 §4 convention that rulings ride
A2 at terminal.

## §A2.2  Patch — replace parent §8 item 4 (progressive criterion 3; ruling AC-3)

**Disposition for executor:** Apply instead of parent §8 item 4 (applied
session 4, K.4).

Parent text: "Probe qualification complete before any product claim: known-good
and all five known-bad classes under `docs/probe-qualification/`, each with the
probe's JSON observation showing detection (CMP criterion 3)."

Replacement: probe qualification is progressive at the point an observable
becomes measurable — Q0 mechanism, Q1 search surfaces (KG, KB1, KB2), Q2 reader
(KB4), Q3 lineage (KB3), FINAL (the complete suite before the critic's first
round and before any PASS / BOUNDED_FAIL declaration). No L2 result is
acceptance evidence for a capability until the probe is qualified for that
capability's failure classes. Result-state vocabulary: `FRAMEWORK_SMOKE_PASS |
QUALIFICATION_PASS | PRODUCT_EVIDENCE_PASS | FAIL | INCOMPLETE`; each run
records `qualification_state`, `product_evidence_eligible`,
`qualified_failure_classes`. Reason of record: PROMPT.md §14 step 5 precedes
step 8, but §4 wave 1 co-dispatches probe and diagnostics and KB1–KB4 need
wave-2/3 surfaces (ledger P-1). Criterion 3 became satisfiable at probe round 4
(session 6).

## §A2.3  Patch — extend parent §2 M (workspace push cadence; ruling O-1)

**Disposition for executor:** Apply after parent §2 M (applied from the
session-3 boundary).

Push workspace `main` to `origin` at each session boundary with the
`build_state.json` commit and at terminal state; fast-forward only; each push
recorded in the resumption entry (range, `origin/main` after, fast-forward
confirmed). A boundary push that does not happen is recorded as a missed push
at the next entry, never back-dated (session 6's boundary push landed in
session 8 as 40 commits; handback M).

## §A2.4  Patch — extend parent §5 (temp-directory application note; ruling 3, session 5)

**Disposition for executor:** Apply after parent §5.

The invariant "no write outside `C:\highsierralabs\RHACO_Corpus_Explorer\`
except the handback and findings files under `C:\RHACO\working\`" is read as
**no write to any governed tree**. Writes by test tooling (`tmp_path` fixture
indexes), builder scratch files, W8's temporary corpus, and probe scratch
launches under the OS temporary directory are permitted and are not
deviations. The prohibition on `C:\RHACO\data\`, `docs\`, the live index, and
the RHACO repository is unchanged.

## §A2.5  Patch — replace the orchestrator row of parent §2 I and extend §2 M item 9 (identity pin of record; rulings MOD-1 and A; finding P-19)

**Disposition for executor:** Apply instead of parent §2 I orchestrator row;
apply after parent §2 M identity clause (MOD-1 applied session 6; A applied
session 8).

Orchestrator / integrator model of record: `claude-opus-5[1m]`, effort
`xhigh`, from session 6 (ruling MOD-1). Cause: at 2026-09-05T02:25:02Z the
client's safeguard fired on the build's own tool output (the probe's
fault-injection vocabulary and headless-browser driving) and swapped the
session model `claude-fable-5-1` → `claude-opus-4-8` without regenerating the
system prompt (ledger P-9, P-10). Sessions 1–5 ran under `claude-fable-5-1`;
this is a recorded model change across the build, not separable at n = 1
(`docs/LAYERS.md` §3 shared-model-family caveat). Session 7 re-entered on
Fable after a Director settings edit; the Director ruled option A (restore
MOD-1, restart) over MOD-2 (re-pin Fable); session 7 wrote records only, tagged
`authored session 7 under claude-fable-5-1, identity halt open`, and dispatched
nothing. Both `settings.json` rewrites of 2026-09-05 (06:02Z to Fable; 14:36:20Z
back to `claude-opus-5[1m]`) were Director acts.

Settings pin of record (handback D row 7): sha256
`06f37244dda720a925b1a237d04a30a172b11444713a792de6d25d4e153cd279`, 9,097 B,
2026-09-05T14:36:20Z; supersedes `831dbfb9…` [VERIFY: sha and size against
the file at commit time via `Get-FileHash`].

Identity check at every re-entry (P-19, ratified session 8): the identity of
record is the **conjunction** of (i) `settings.json` sha256 and its `model`
key — the only surface carrying the `[1m]` suffix; (ii) the system-prompt
model sentence, precise but regenerated only at client start; (iii) the
per-request `message.model` field, live but suffix-stripped
(`claude-opus-5` under the `[1m]` pin; 255/255 in session 6). A predicate on
(iii) alone that expects the suffixed string halts every conformant session.
A model, effort, version, or settings-sha change at re-entry is a halt unless a
Director ruling pre-dispositions it. `switchModelsOnFlag: false` in force from
session 6: a classifier flag pauses the session rather than swapping the model.

## §A2.6  Patch — extend parent §2 C as amended by §A1.5 (import-boundary check; rulings SA-3 (b), SA-4)

**Disposition for executor:** Apply after parent §2 C as amended by §A1.5
(applied session 8).

The L1 static check gains an **import-boundary check**: every file importing
`RHACO_corpus_index` or `RHACO_tool_catalog_librarian` must be in the licensed
set. Licensed product-tree importers: `explorer/corpus_adapter/adapter.py`,
`fixtures/build_fixture_index.py` (O3), `explorer/diagnostics/service.py`
(O17). Instrument allowlist: `tools/l4_gold_oracle.py` by file (AC-4 compares
adapter ids to module ids by design), `preflight/` and `tests/` by path. Not a
directory allowlist on `tools/`: the probe is barred from importing the module
or opening the db, and a directory allowlist would hide that class. SA-3 remedy
(b): ARCHITECTURE 4.1 and the package docstring enumerate the licensed set; the
"sole importer" claim is retired. The check's licensed set is stated explicitly
in its source. Scope note of record: an L1 pass establishes only the properties
L1 checks (SA-4); `sqlite3.connect` outside the module's `connect()` and
read-authority paths remain unchecked and are register entries, not claims.

## §A2.7  Patch — extend parent §3 (integrator edits to builder-owned files; findings P-13, instances 1–3)

**Disposition for executor:** Apply after parent §3 (rule set session 4,
amended session 8).

An integrator edit to a builder-owned file is a P-13 instance: disclosed, never
absorbed, and carried with a compensating control that is proven to fail
(instance 1: `#keyhelp` contract test; instance 2: `search.html` prefix match,
verified live under `RHACO_CORPUS_DISABLE_VEC=1`; instance 3: the search-page
provenance date derived from `gold_v1_1_compat.json` with a contract test).
Rule of record: **omissions wait for a builder round; statements affirmatively
false about the artifact beside them are repaired with a control.** Structural
lesson carried to the template: shared vocabulary or markup with no single
owner belongs to the shell by rule, never by round cost.

## §A2.8  Patch — extend parent §3 standing halts (deviation and budget rulings 1, 2, 4; refusal of O-4 / O-6 rounds)

**Disposition for executor:** Apply after parent §3 (rulings 1, 2, 4 of
session 5; O-4 / O-6 of session 8).

1. A strand's disclosed conduct deviation (S4-B7 scratch launch of uvicorn
   against the fixture, not via the probe) is recorded in
   `build_state.json` `strand_deviations_of_record` and the handback; it does
   not invalidate evidence the probe and the integrator independently
   reproduced, and no retroactive act follows.
2. `availability.py`'s direct module `connect()` (O10 class) was a hard floor
   before FINAL, spent at adapter round 3.
3. Module round budgets are never waived. The probe's round 4 carried Q3 and
   FINAL; any further need is BOUNDED_FAIL, never a lowered bar (P-8). O-4
   (diagnostics undated standing figure) and O-6 (reader `data-diagnostics-state`
   attribute) were held as open items for critic round 2 and, on its ranking,
   left in the register rather than repaired by a 21st round or an integrator
   edit. Eight rounds closed unspent.

## §A2.9  Patch — extend parent §8 item 6 as amended by §A1.7 (reconstructed dispatch records; GD-1)

**Disposition for executor:** Apply after parent §8 item 6 as amended by
§A1.7 (applied session 8).

A dispatch whose seven governance fields were not written at dispatch time is
a criterion-5 governance defect even when later rebuilt from primary evidence.
Rebuilt rows carry `record_provenance` (source artifact per field, no field
estimated) and the closeout reports the defect with the repair beside it, never
the repair alone. Instance of record: GD-1 — S6-B10, S6-B11, S6-CR1 (session 6
ended without writing them; rebuilt session 8 from transcript timestamps,
workflow run records, and git log). Basis: Guide v1.3 §8 (dispatch-time capture
because a fresh instance cannot reconstruct).

## §A2.10  Patch — extend parent §2 N (closeout reconciliation sources; finding P-7)

**Disposition for executor:** Apply after parent §2 N (applied from session 4).

Criterion-6 reconciliation of `corpus_index.db` reads both
`docs\logs\catalog_librarian_validation.log` (librarian reindex entries,
including the closeout gate's librarian member) and the chat-side MCP census
log **including its rotated files** `docs\logs\mcp_validate.log.YYYY-MM-DD`
(a pair-write census can rotate out of the live log before the next session
opens). Every chat-side census, read-only or pair-write, is listed in the
launch or handoff note that precedes the Code session; an unlisted entry is a
recorded discrepancy, not a halt.

## §A2.11  Rulings recorded without a parent patch (for the ledger and the M3 ANL)

- CMP-20260903-001 §6 REVIEW trigger fired twice (session-5 safeguard swap;
  session-7 Fable re-entry); dispositions MOD-1 and A, both above.
- Adapter round-4 batch order: SA-1 → SA-2 → amends click-through → SA-3
  docstrings (lowest), per-item `landed | not landed`. All four landed.
- Seal comparison (P-SEAL-RELEASED): SA-1, SA-2, SA-3, SA-4 missed by harness
  and critic; SA-5 found by both; SA-6 satisfied unprompted. The M3 ANL reads
  the miss, not the repair.
- No claim-audit layer in-flight: a layer the prompt does not define is a
  harness revision (CMP §6), carried to M3 as ledger P-21 and the primary
  template item.
- No third critic round: same model adds no independence; the 2-round
  convergence window forbids drift. Scale-validity clause of PROMPT.md §12 read
  as vacuous (no exemplar, no second scorer, two products scored); PASS
  unavailable on that route regardless of score.
- BF-1 stated as an instrument disagreement resolved by the L4 direction
  oracle's independent expectation, not as the product validating the check's
  retirement.
- Record-integrity finding P-22 (a builder's UNVERIFIED qualifier dropped by the
  ledger) stands as its own row.
- O29 (`search_fts` bare-string filter) and the bare-date card policy (872
  cards) are RHACO-side CHG candidates, not build items.

## §A2.12  No other changes

Sections of the parent not listed above, and every §A1 patch, remain
authoritative as written. Route `ops` unchanged.

## §A2.13  Disposition

Retain permanently as amendment. The parent is a single-run hand at terminal
state; no full revision is planned.

## Cross-references

RHACO-HND-20260903-001 (parent) · §A1 · RHACO-CMP-20260903-001 (§3 criteria
3, 5, 6; §6 REVIEW) · RHACO-CCX-20260904-001, RHACO-CCX-20260905-001 (§4
filing convention; §6 rulings ledger) · RHACO_Subagent_Pattern_Application_Guide_v1_3
(D-3, D-12, D-13; §8) · RHACO-CCX-20260825-002 (asserted-vs-captured;
extended by P-9, P-19) · RHACO_HND_Specification_v1_1 §4.6, §5.7.

---

*Reno High-Altitude Cosmic Ray Observatory (RHACO) | Kris E. Granholm, Director*
