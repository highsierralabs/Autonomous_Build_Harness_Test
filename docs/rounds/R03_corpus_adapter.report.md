# R03_corpus_adapter -- round report (strand S6-C3)

## Header

- strand_id: S6-C3
- role: module builder (corpus_adapter), criterion-6 hard-floor round
- model: You are powered by the model named Sonnet 5. The exact model ID is claude-sonnet-5.
- t_start_utc: 2026-09-05T03:19:28Z
- t_end_utc: 2026-09-05T03:25:17Z
- worktree: `C:\highsierralabs\RHACO_Corpus_Explorer\.worktrees\corpus_adapter`
- branch: `build/corpus_adapter`
- base commit: `6a8353705a2933cdd4696391da904ed3c680b398` (the round-2 boundary;
  round-1/round-2 work merged there; 181 tests pass)
- code+tests commit the Evidence section's final gate runs were taken
  against: `8d7ba3c9c4f94d9a2a664563c3216e5080f842e1` (one commit before
  this report file was added; the final `git rev-parse HEAD` including this
  report commit is reported in the StructuredOutput return, not pinned here
  to avoid this file citing its own not-yet-computed commit hash)
- dispatch: RHACO-HND-20260903-001 section 2 I as amended by A1.3; task C3
  (ARCHITECTURE.md section 4.1, decision records A4/A9; CONSTRAINTS.md O10,
  O4); corpus_adapter module round 3 of 4
- prompt of record: `docs/rounds/R03_corpus_adapter.prompt.md`,
  sha256 `5549f6d5860d3892f83729a279ffe844893b4b8a0471a5a5b849d1418dbf1032`
  (12,374 bytes) -- confirmed against the archived file (both `sha256sum`
  and `Get-FileHash -Algorithm SHA256`) before any other act.

## Change

Task C3 -- close the second instance of the O10 create-on-open hazard:
`explorer/corpus_adapter/availability.py`'s `probe()` called
`RHACO_corpus_index.connect(db_path)` directly, bypassing the per-call
`os.path.isfile` guard round 2 (C2) put on `CorpusAdapter.connect()`. Every
hybrid/graph search and every diagnostics page load reaches `probe()` via
`adapter.vector_availability()` (`adapter.py` line 201), so if the live
index were absent or mid-replacement, one such call would have let
`RHACO_corpus_index.connect()` create a fresh, empty `corpus_index.db` at
the live path -- a build write to the live index forbidden by
DISPATCH_PARAMETERS.md items B/C and criterion 6.

- `explorer/corpus_adapter/availability.py`:
  - Added an `os.path.isfile(db_path)` check immediately after the
    `VEC_DISABLE_ENV` short-circuit and **before** `rhaco_index.connect(db_path)`
    is ever called. On failure, returns
    `VectorAvailability(available=False, reason="db_unavailable", model_tag=tag,
    probe_ms=..., detail="database file does not exist: <path> (the adapter
    never creates a database, O10)")` -- no model change needed, since
    `db_unavailable` was already in `explorer/models.py`'s `VectorAvailability.reason`
    vocabulary (used by the pre-existing `connect()`-failure `except` branch).
  - The existing `try: conn = rhaco_index.connect(db_path) except Exception:
    return _result(False, "db_unavailable", ...)` block is left in place,
    now unreachable for a missing file (the new isfile check short-circuits
    first) but still catching other `connect()` failures (e.g. a locked or
    corrupt file at a path that does exist) -- that is a different failure
    mode than O10 and this task does not ask to remove it.
  - `probe()`'s contract ("never raises; every failure path is reported
    through `VectorAvailability.reason`") is unchanged: the new branch
    returns, it does not raise.
  - The `VEC_DISABLE_ENV` short-circuit stays first, unchanged, so a
    deliberately disabled channel still reports `disabled_by_env` even
    against a missing database.
  - Module docstring and `probe()`'s docstring updated to state the guard
    accurately (see the diff in Evidence).
- `tests/corpus_adapter/test_connect_guard.py`: three new tests (below);
  module docstring extended to describe both C2's and C3's guards.
- No other file touched. `explorer/models.py`'s `VectorAvailability` was not
  changed (task said none was needed, and none was: `db_unavailable` already
  present).

## Evidence

Checks actually run, exact commands and tails, all from the worktree root,
against `8d7ba3c9c4f94d9a2a664563c3216e5080f842e1` (both commits of this
round):

```
C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m ruff check explorer tools tests --output-format concise
```
```
All checks passed!
```

```
C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m pytest tests/corpus_adapter -q -s
```
```
[criterion-6] live db BEFORE: path=C:\RHACO\index\corpus_index.db corpus_cards_sha=9d36e8973132442b631f137232ef29be9bb9c3bb872b24e9ff26a5fe1ca6b40b mtime=1788566291.2718246
....................[criterion-6] live db AFTER:  path=C:\RHACO\index\corpus_index.db corpus_cards_sha=9d36e8973132442b631f137232ef29be9bb9c3bb872b24e9ff26a5fe1ca6b40b mtime=1788566291.2718246

20 passed in 3.64s
```

**Criterion-6 evidence:** `corpus_cards_sha` before and after =
`9d36e8973132442b631f137232ef29be9bb9c3bb872b24e9ff26a5fe1ca6b40b`; `mtime`
before and after = `1788566291.2718246` -- identical (both unchanged from
round 2's report: no reindex ran on the live corpus between R02C and this
round), live index untouched across the full session including the two new
tests that delete a `tmp_path`-scoped file and never touch the live db.

```
C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m pytest tests -q
```
```
184 passed, 2 warnings in 17.36s
```
(warnings are pre-existing fastapi/starlette deprecation notices, unrelated
to this round's diff)

```
C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe tools\l1_index_write_check.py
```
```
l1-index-write-check: hits=6 allowlisted=6 defects=0 verdict=PASS
```
(all 6 hits are the pre-existing `fixtures/build_fixture_index.py`
allowlist entries, unchanged by this round)

Test-to-deliverable map:

- `test_connect_guard.py::test_vector_availability_reports_db_unavailable_and_creates_nothing_when_db_removed`
  -- **the hazard test.** Constructs a `CorpusAdapter` against an empty
  `tmp_path` file (succeeds), removes the file, calls
  `adapter.vector_availability()`, asserts `available is False`,
  `reason == "db_unavailable"`, and `os.listdir(tmp_path) == []` afterward.
  This is the test that would have failed before this round: pre-round,
  `probe()` would have called `rhaco_index.connect(db_path)` on the removed
  path, and `RHACO_corpus_index.connect()` creates the parent directory and
  the file (applying DDL) when absent -- `os.listdir(tmp_path)` would have
  been non-empty.
- `test_connect_guard.py::test_vector_availability_against_live_index_is_read_only`
  -- **the guard-is-not-a-break test.** Against the real, live index through
  the adapter, read-only: asserts `vector_availability()`'s `reason` is one
  of the six documented values, and that `corpus_cards_sha`
  (`9d36e8973132442b631f137232ef29be9bb9c3bb872b24e9ff26a5fe1ca6b40b`) and
  the db file's mtime are unchanged across the call (read through a fresh
  `CorpusAdapter` instance to avoid an echo of `index_meta()`'s <=5s cache,
  same pattern as `conftest.py`'s session fixture).
- `test_connect_guard.py::test_probe_short_circuits_before_connect_when_db_missing`
  -- **the short-circuit test.** Calls `availability.probe(fake_module,
  missing_path)` directly with a hand-written fake whose `connect` staticmethod
  raises `AssertionError("connect must not be called")`; the probe returns
  `available=False, reason="db_unavailable"` and creates nothing, proving the
  `os.path.isfile` guard runs *before* `connect()` is reached, not that it
  merely catches whatever `connect()` would have raised for a missing path.
- The pre-existing 17 `tests/corpus_adapter` tests (round 1 + C2's two)
  still pass unchanged -- none of their behavior was touched; total is now
  20, exactly as the task specified ("expect 20").
- `conftest.py`'s session-scoped `_live_db_unchanged` autouse fixture
  (unmodified) printed the BEFORE/AFTER lines quoted above and its own
  assertions passed -- criterion-6 evidence for the whole session.

I re-read, per the task's "Read first" list, before writing any code:
`CONSTRAINTS.md` O10 and O4; `ARCHITECTURE.md` section 4.1 (the `connect`
line and "Adapter rules" paragraph) and decision records A4 and A9;
`explorer/corpus_adapter/availability.py` in full; `explorer/corpus_adapter/adapter.py`
lines 110-160 and 197-203; `tests/corpus_adapter/conftest.py` and
`tests/corpus_adapter/test_connect_guard.py`; `docs/rounds/R01C_corpus_adapter.report.md`
(which had already flagged this exact gap in its own "Unresolved
uncertainty" section, one round early).

**"Last instance" evidence (deliverable 2).** Ran
`grep -rn "sqlite3\.connect\|rhaco_index\.\|import RHACO_corpus_index" explorer/ tools/ fixtures/`
across the whole workspace (not only `explorer/corpus_adapter/`) and
`grep -rn "connect(" explorer/` separately. Findings:
- `explorer/corpus_adapter/adapter.py`: every `conn = self.connect()` call
  (8 sites: `index_meta`, `_row_to_card`'s callers via `card`/`cards_for_doc_id`/
  `catalog`/`facets`/`edges_for`/`supersession_chain`/`campaign_subtree`/
  `dangling_references`) goes through `CorpusAdapter.connect()`, which calls
  `self._require_db_exists()` before `self._rhaco_index.connect(...)` (C2,
  round 2) -- already guarded.
- `explorer/corpus_adapter/availability.py`: the one direct
  `rhaco_index.connect(db_path)` call, now guarded by this round's fix
  (line 74, preceded by the isfile check at line 67).
- `explorer/diagnostics/service.py:85`: `import RHACO_corpus_index as
  rhaco_corpus_index` -- read the surrounding function
  (`_rerank_artifact_present`) in full; it only does
  `os.path.isdir(getattr(rhaco_corpus_index, "RERANK_MODEL_DIR", None))` --
  no `connect()` call, no DB access at all.
- `tools/l4_gold_oracle.py:131`: `import RHACO_corpus_index as ci` -- grepped
  `\bci\.` in that file; the only use is
  `ci.search_hybrid(q, top_k=args.top_k, db_path=adapter.db_path)` at line
  165 (a read-only search call, not `connect`), and the file otherwise
  builds and uses its own `CorpusAdapter` (already guarded).
- `fixtures/build_fixture_index.py:145`: `conn = RHACO_corpus_index.connect(resolved_db)`
  -- a direct, unguarded call, but this file is (a) outside my owned/writable
  paths this round (`fixtures/**` is explicitly listed as off-limits in
  working rule 1) and (b) a structurally different case from O10: it is the
  designated, allowlisted fixture-index *builder* (the one file
  `tools/l1_index_write_check.py` permits to call the five index-writing
  functions at all), and its own docstring and code assert
  `resolved_db` is neither `RHACO_corpus_index.DEFAULT_DB` nor under either
  spelling of the RHACO tree, raising `ValueError` otherwise, *before* this
  `connect()` line is reached -- it cannot reach the live index by
  construction, so leaving it uncreate-guarded is not the O10 hazard this
  task closes (see "Unresolved uncertainty" for the caveat on this reading).
- No `sqlite3.connect` anywhere in `explorer/`, `tools/`, or `fixtures/`.

So, within `explorer/corpus_adapter/**` (my owned paths, and the only
module CONSTRAINTS.md/ARCHITECTURE.md identify as importing
`RHACO_corpus_index`), this was the last unguarded instance.

## Material alternatives

- **Where to put the guard: inside `probe()` itself, or route
  `availability.py`'s call through `CorpusAdapter.connect()`.** R01C's
  "Unresolved uncertainty" section named both options as a design choice for
  a follow-up round. This task's deliverable 1 specifies the first option in
  detail (an `os.path.isfile` check inside `probe()`, returning the existing
  `db_unavailable` outcome) and explicitly forbids the second's consequence
  ("`probe()`'s contract is 'never raises' ... do not introduce a raise
  here"): routing through `CorpusAdapter.connect()` would mean catching
  `ConfigurationError` inside `probe()` to preserve the no-raise contract,
  which is strictly more code for the same outcome and would also require
  `probe()` to take a `CorpusAdapter` (or its `_require_db_exists` method)
  rather than the `(rhaco_index, db_path)` pair it is called with today from
  two different tests (the module-level short-circuit test needs a bare
  function taking a fake module). Implemented the task's specified shape: a
  same-package, same-signature `os.path.isfile` check, matching
  `CorpusAdapter._require_db_exists()`'s check exactly but returning instead
  of raising, since `probe()` and `connect()` have different contracts by
  design (A4 vs A9).
- **Keep or drop the existing `try/except` around `rhaco_index.connect(db_path)`.**
  Considered removing the now-technically-redundant-for-missing-files
  `except Exception: return _result(False, "db_unavailable", ...)` block,
  since the new isfile check makes a `FileNotFoundError` from `connect()`
  unreachable. Kept it: it still catches other `connect()` failure modes at
  a path that *does* exist (e.g. a locked file mid-write by an external
  reindexer, a corrupt/truncated db, a permissions error) -- exactly the
  kind of "connect failure means unavailable, not a crash" case the
  pre-existing `noqa: BLE001` comment documents, and the task's instruction
  was to add the guard, not to narrow this except's existing scope. Removing
  it would be an unrequested behavior change under "this round is the guard
  only."
- **Where to add the new tests.** The task offered "extending
  `test_connect_guard.py` or in a sibling file." Chose to extend
  `test_connect_guard.py`: its existing docstring and both existing tests
  are about exactly this hazard class (O10 create-on-open) on a sibling call
  site (`CorpusAdapter.connect()`), so grouping C2's and C3's tests in one
  file keeps every O10-guard test discoverable from one place and let the
  module docstring narrate the two rounds' relationship directly, rather
  than splitting one hazard's story across two files.

## Decisions

- The `db_unavailable` detail string for the new branch
  (`f"database file does not exist: {db_path!r} (the adapter never creates a
  database, O10)"`) deliberately echoes `CorpusAdapter._require_db_exists()`'s
  existing `ConfigurationError` message wording ("configured database does
  not exist ... the adapter never creates a database, O10") rather than
  inventing new phrasing, so a log or diagnostics page shows the same voice
  for the same root cause regardless of which call site (adapter or probe)
  observed it.
- Placed the new isfile check immediately after the `VEC_DISABLE_ENV`
  short-circuit and before the `try/except` around `connect()`, not
  interleaved inside that `try` block -- keeps "is the channel disabled" and
  "does the database exist" as two independent, sequential gates, matching
  the task's own ordering ("Keep the `VEC_DISABLE_ENV` short-circuit first,
  as now").
- Did not touch `search_lexical`'s `doc_type_filter` argument shape (O29)
  per the task's explicit instruction that this is a Director-side CHG
  finding, not a build item.
- Did not add a change request for `explorer/models.py`: the task confirmed
  `db_unavailable` was already in the reason vocabulary, and I verified this
  by reading `explorer/models.py`'s `VectorAvailability` dataclass directly
  (`reason` comment lists `ok | disabled_by_env | sqlite_vec_not_loaded |
  vec_table_missing | embedder_unreachable | db_unavailable`).

## Result

corpus_adapter round 3 of 4 (this round) consumed. All three gates green in
the worktree (see Evidence for full output):

- `ruff check explorer tools tests` -- `All checks passed!`
- `pytest tests/corpus_adapter -q` -- **20 passed**, 0 failed, 0 skipped (17
  from rounds 1-2 + the 3 new C3 tests, as specified).
- `pytest tests -q` -- **184 passed** (181 from rounds 1-2 across every
  module + the 3 new C3 tests), 0 failed.
- `tools/l1_index_write_check.py` -- `verdict=PASS` (hits=6, all
  pre-existing `fixtures/build_fixture_index.py` allowlist entries,
  defects=0).

Live index left byte-for-byte as found: `corpus_cards_sha` and `mtime`
identical before and after the full test session (see Evidence).

Worktree clean after two commits on `build/corpus_adapter`:
- `9aa6545` -- the guard fix in `availability.py`.
- `8d7ba3c` -- the three new tests in `test_connect_guard.py`.

`git rev-parse HEAD` at report-writing time (before this report file's own
commit): `8d7ba3c9c4f94d9a2a664563c3216e5080f842e1`.

## Unresolved uncertainty

- **Whether any db-opening path outside `explorer/corpus_adapter/` remains
  unguarded, workspace-wide.** My reading is: no path that can reach the
  *live* index remains unguarded. Every call into `RHACO_corpus_index` from
  `explorer/diagnostics/service.py` and `tools/l4_gold_oracle.py` is either
  import-only or a read (`search_hybrid`) through an already-guarded
  `CorpusAdapter`, confirmed by grep (see Evidence). The one remaining
  direct, unguarded `RHACO_corpus_index.connect()` call in the whole
  workspace is `fixtures/build_fixture_index.py:145`, which is outside my
  owned/writable paths this round and is protected by a *different*
  mechanism (a path-identity assertion that raises `ValueError` before
  `connect()` is ever reached if the target is the live db or under the
  RHACO tree at all, rather than an isfile-before-connect check). I read
  this as a deliberate, already-safety-checked builder script rather than an
  instance of the O10 class this task closes, but I did not modify it (out
  of scope) and did not write a test that exercises its `ValueError` path
  (also out of scope: `fixtures/**` is untouchable). If the integrator reads
  "the O10 class is closed workspace-wide" more strictly -- i.e., wanting
  every `connect()` call site to carry the *same* isfile-style guard,
  regardless of what other protection it has -- then this file is still an
  outstanding instance and would need a Director-side CHG or a future round
  with `fixtures/**` in scope, since I cannot write there. I verified the
  grep is complete (whole-workspace `sqlite3.connect`/`rhaco_index.`/`import
  RHACO_corpus_index` scan, not scoped to `explorer/`) but did not exhaustively
  read every one of the hundreds of files under `tools/` line-by-line beyond
  what the grep surfaced -- the grep itself is the evidence, not a manual
  read of files it found no hits in.
- Everything already listed as unresolved in
  `docs/rounds/R01C_corpus_adapter.report.md` that is not this task's
  subject (the vector-availability probe's 8s timeout bound never exercised
  against a genuinely hung Ollama; `campaign_subtree`/`dangling_references`
  not covered by a dedicated pytest test; `wrong_doc_for_id`'s exact fixture
  semantics not yet confirmed against a real fixture index) is unchanged by
  this round -- none of it was in scope for C3 and none of it was touched.
  R01C's specific "unresolved" item about `availability.probe()`'s unguarded
  `connect()` call is now resolved by this round.

## Change requests

None this round. No change to any file outside
`explorer/corpus_adapter/**` / `tests/corpus_adapter/**` was needed or made.
The O29 non-normalization instruction was followed (no touch to
`search_lexical`'s `doc_type_filter` or `explorer/search/service.py`).

## Assumptions

- The live-index `corpus_cards_sha`
  (`9d36e8973132442b631f137232ef29be9bb9c3bb872b24e9ff26a5fe1ca6b40b`) and
  mtime (`1788566291.2718246`) observed in this round are identical to round
  2's report -- read as "no reindex ran on the live corpus between R02C and
  this round," not a defect, and confirmed by this round's own session-start
  vs session-end match (both reads agree with each other, matching the
  session-scoped `_live_db_unchanged` fixture's design intent).
- `os.path.isfile(db_path)` immediately before `rhaco_index.connect(db_path)`
  is an adequate guard against the O10 hazard as described (an external
  actor removing or replacing the file while the explorer is idle or between
  calls), matching the identical assumption already accepted for
  `CorpusAdapter.connect()` in round 2 (a TOCTOU race in the few
  milliseconds between the `isfile` check and the `connect()` call itself is
  not addressed by either guard, and was not asked to be -- both are
  "never create on a path we can see doesn't exist right now," not a lock
  against concurrent external mutation mid-check).
