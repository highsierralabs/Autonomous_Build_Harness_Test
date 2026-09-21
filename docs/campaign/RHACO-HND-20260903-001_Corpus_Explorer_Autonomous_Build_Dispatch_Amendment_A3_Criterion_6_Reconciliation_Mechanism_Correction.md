# RHACO-HND-20260903-001 — Amendment §A3: Criterion-6 Reconciliation Mechanism Correction

*Reno High-Altitude Cosmic Ray Observatory (RHACO) · 5,050 ft ASL · 39°N*

| Field | Value |
|---|---|
| Document type | HND Amendment (Class F) |
| Amends | RHACO-HND-20260903-001 as amended by §A1 and §A2 (§A2 sha256 `34ee0c2dca4749f02082286bb1e20032c8ced34d9d12c17af66af6a6afd8fc15`, 13,899 B, commit `30613bc`) |
| Amendment number | §A3 |
| Execution route | `ops` (unchanged) |
| Status | CLOSED |
| Author | Kris E. Granholm, Director, RHACO |
| Date | 2026-09-05 UTC |
| Naming convention | v1.17 · Style RSG v1.9 · Schema Card YAML v1.9 |

## §A3.1  Reason for amendment

§A2.10 directs criterion-6 reconciliation of `corpus_index.db` to the rotated
MCP census logs on the premise that a chat-side canonical pair write produces a
census entry that may rotate out of the live log. Measured 2026-09-05 (Code,
commit `30613bc` report; two instances, one observed live): a canonical MCP
write reindexes the pair through `_index_after_canonical_write`
(`RHACO_mcp_observatory_server.py:621`, `reindex_pair` / `reindex_fts_pair`,
failures swallowed by contract) and **logs nothing**; the `MCP census summary`
line is emitted only by `validate_catalog`, which never reindexes. The two
never co-occur. The census lines reconciled in J.5 and K.3 were explicit
post-write `validate_catalog` calls by the writing chat, not a property of the
write. §A2.10's remedy cannot reach a line that was never written.

## §A3.2  Patch — replace §A2.10 (criterion-6 reconciliation sources)

**Disposition for executor:** Apply instead of §A2.10 (which extended parent
§2 N).

Criterion-6 reconciliation of `corpus_index.db` reads three sources, each
matched to its mechanism:

1. **Librarian reindex entries** in `docs\logs\catalog_librarian_validation.log`
   (librarian runs, including the closeout gate's librarian member — a full
   reindex; the working tree is walked, so an uncommitted pair is indexed).
2. **Chat-side censuses** — explicit `validate_catalog` calls only — in
   `docs\logs\mcp_validate.log` and its rotated files
   `mcp_validate.log.YYYY-MM-DD`. Read-only; never a reindex.
3. **Chat-side canonical writes** — evidenced by the pair mtimes, an index
   mtime within ~10 s of them, and the new `cards` row read through the
   module's `connect()`; **no log line exists for this path.**

The note that precedes a Code session lists every chat-side write with its
write-result timestamp and, separately, every census with its call time. An
index change matching none of the three is a criterion-6 failure; one matching
source 3 without a listed write is a recorded discrepancy, not a halt. Chat
holds canonical writes while a Code task is open (the 18:36:26Z CHG pair
write during the A2 commit task is the instance of record).

## §A3.3  Findings recorded (ledger)

- Next ledger id (P-23 expected): writes reindex without logging; censuses
  log without reindexing (server 0.22.0, by design). Class: harness /
  measurement design. Template item: a reconciliation rule names the
  mechanism that produces each evidence class; a log-reading remedy is only
  as good as the logging that precedes it.
- Queued (Director, `mcp` route): CHG candidate — `_index_after_canonical_write`
  emits one log line on success and one on swallowed failure, so the write
  path observes itself (Charter Principle 2). Not directed here.

## §A3.4  No other changes

§A1, §A2 (all sections but §A2.10), and the parent remain authoritative as
written.

## §A3.5  Disposition

Retain permanently as amendment.

## Cross-references

RHACO-HND-20260903-001 · §A1 · §A2 · RHACO-CMP-20260903-001 §3 criterion 6 ·
RHACO-CHG-20260905-001 (execution record cites this correction) ·
RHACO-CMP-20260526-001 (observatory server; the queued logging CHG's home).

---

*Reno High-Altitude Cosmic Ray Observatory (RHACO) | Kris E. Granholm, Director*
