# R01C_corpus_adapter -- round report (correction round, strand S4-C2)

## Header

- strand_id: S4-C2
- role: module builder (corpus_adapter), correction round
- model: You are powered by the model named Sonnet 5. The exact model ID is claude-sonnet-5.
- t_start_utc: 2026-09-05T00:09:34Z
- t_end_utc: 2026-09-05T00:14:49Z
- worktree: `C:\highsierralabs\RHACO_Corpus_Explorer\.worktrees\corpus_adapter`
- branch: `build/corpus_adapter`
- base commit: `62685dad6f40f91c6b1b84500a213f0a43ea8673` (main at the round-1 boundary)
- code+tests commit the Evidence section's gate runs were taken against:
  `6a17c194f910dabcbe1cf4692b879e12dc4b6f8c` (one commit before this report
  file was added; the final `git rev-parse HEAD` including this report
  commit is reported in the StructuredOutput return, not pinned here to
  avoid this file citing its own not-yet-computed commit hash)
- dispatch: RHACO-HND-20260903-001 section 2 I as amended by A1.3; task C2
  (ARCHITECTURE.md section 4.1, decision record A9); corpus_adapter module
  round 2 of 4
- prompt of record: `docs/rounds/R01C_corpus_adapter.prompt.md`,
  sha256 `23ef44b5922234b2f560cacc75017b6861431cfeefbe8018e58440cc6ae1e870`
  (8,906 bytes) -- confirmed against the archived file before any other act.

## Change

Task C2 -- criterion-6 guard: `CorpusAdapter.connect()` now re-checks
database existence before delegating to `RHACO_corpus_index.connect()`, on
**every** call, not only at construction.

- `explorer/corpus_adapter/adapter.py`:
  - Added `CorpusAdapter._require_db_exists()` -- the guard body
    (`os.path.isfile(self.db_path)`, else raise `ConfigurationError` naming
    the path and citing O10), factored out so `__init__` and `connect()`
    share one implementation instead of two copies of the same check and
    message.
  - `__init__` now sets `self.db_path` then calls `self._require_db_exists()`
    (same behavior as round 1's inline check, just delegated to the shared
    method).
  - `connect()` now calls `self._require_db_exists()` before
    `self._rhaco_index.connect(self.db_path)` -- this is the actual fix: in
    round 1, `connect()` did no such check and would silently let the RHACO
    module create a missing database on any call after construction.
  - Docstrings updated for accuracy per the task: module header gets an
    "O10 guard" paragraph naming the hazard and stating the check runs both
    at construction and on every `connect()` call; `ConfigurationError`'s
    docstring says the same; `CorpusAdapter` now carries a class-level
    docstring stating the guard is per-call; `connect()`'s own docstring
    says "re-checked on *every* call, not only at construction". The S2
    allowlist comment in the module header (`connect`, `get_meta`,
    `search_fts`, `resolve_identifier`, `search_hybrid`, `search_graph`,
    `freshness_check`, `embed_query_cpu`, `doc_id_from_filename`) was left
    verbatim -- checked against `CONSTRAINTS.md` S2's own list (same eight
    RHACO names) and confirmed still accurate as an allowlist of what is
    *permitted*, not a claim that each name is currently called (see
    "Decisions").
  - No other method's behavior changed.
- `tests/corpus_adapter/test_connect_guard.py` (new): two tests per the
  task's deliverable 2.

## Evidence

Checks actually run, exact commands and tails (all from the worktree root,
after both commits):

```
C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m ruff check explorer tools tests --output-format concise
```
```
All checks passed!
```

```
C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m pytest tests/corpus_adapter -v --tb=short -s
```
```
tests/corpus_adapter/test_cards_and_identity.py::test_cards_for_doc_id_returns_hand_and_amendment
[criterion-6] live db BEFORE: path=C:\RHACO\index\corpus_index.db corpus_cards_sha=9d36e8973132442b631f137232ef29be9bb9c3bb872b24e9ff26a5fe1ca6b40b mtime=1788566291.2718246
PASSED
tests/corpus_adapter/test_cards_and_identity.py::test_card_round_trips_for_hand_and_amendment PASSED
tests/corpus_adapter/test_cards_and_identity.py::test_resolve_identifier_exact_campaign_id PASSED
tests/corpus_adapter/test_catalog.py::test_catalog_cmp_filter_and_lifecycle_state PASSED
tests/corpus_adapter/test_catalog.py::test_facets_global_is_non_empty PASSED
tests/corpus_adapter/test_connect_guard.py::test_connect_raises_after_db_removed_post_construction_and_creates_nothing PASSED
tests/corpus_adapter/test_connect_guard.py::test_connect_still_succeeds_when_db_file_exists PASSED
tests/corpus_adapter/test_construction.py::test_missing_db_path_raises_configuration_error_and_creates_nothing PASSED
tests/corpus_adapter/test_hybrid_degraded_subprocess.py::test_hybrid_degrades_to_lexical_when_vec_disabled PASSED
tests/corpus_adapter/test_index_meta.py::test_index_meta_keys_and_live_counts PASSED
tests/corpus_adapter/test_lineage.py::test_edges_for_hand_has_incoming_campaign_child_from_cmp PASSED
tests/corpus_adapter/test_lineage.py::test_edges_for_amendment_has_outgoing_amends_from_its_own_stem PASSED
tests/corpus_adapter/test_lineage.py::test_supersession_chain_from_a_catalog_located_superseded_card PASSED
tests/corpus_adapter/test_reader.py::test_read_document_returns_headings_with_slugs PASSED
tests/corpus_adapter/test_reader.py::test_is_under_docs_root_rejects_data_tree_and_dotdot_escape PASSED
tests/corpus_adapter/test_search.py::test_search_lexical_has_line_no_and_lexical_hit_excerpts PASSED
tests/corpus_adapter/test_search.py::test_search_hybrid_top_k_and_mode_consistency PASSED[criterion-6] live db AFTER:  path=C:\RHACO\index\corpus_index.db corpus_cards_sha=9d36e8973132442b631f137232ef29be9bb9c3bb872b24e9ff26a5fe1ca6b40b mtime=1788566291.2718246

============================= 17 passed in 4.16s ==============================
```

**Criterion-6 evidence:** `corpus_cards_sha` before and after =
`9d36e8973132442b631f137232ef29be9bb9c3bb872b24e9ff26a5fe1ca6b40b`; `mtime`
before and after = `1788566291.2718246` -- identical, live index untouched
across the full session (the sha differs from round 1's report because a
reindex ran on the live corpus between rounds -- the fixture is external and
expected to move, per O10 itself).

```
C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe tools\l1_index_write_check.py
```
```
l1-index-write-check: hits=6 allowlisted=6 defects=0 verdict=PASS
```
(All 6 hits are the pre-existing `fixtures/build_fixture_index.py` allowlist
entries, unchanged by this round -- 0 defects.)

Test-to-deliverable map:

- `test_connect_guard.py::test_connect_raises_after_db_removed_post_construction_and_creates_nothing`
  -- constructs a `CorpusAdapter` against an empty `tmp_path` file (succeeds,
  since `__init__` only checks `isfile` and computes `active_fault`), deletes
  the file, asserts `adapter.connect()` raises `ConfigurationError`, and
  asserts `os.listdir(tmp_path) == []` afterward -- nothing created (no
  database, no `-journal`, no `-wal`). This is deliverable 2's first test and
  is the one that would have failed against round 1's `connect()` (which had
  no per-call check and would have delegated straight to
  `RHACO_corpus_index.connect()`, which creates the file).
- `test_connect_guard.py::test_connect_still_succeeds_when_db_file_exists`
  -- uses the session-scoped `live_adapter` fixture, calls `.connect()`,
  runs `SELECT count(*) FROM cards` (count > 0), closes the connection in
  `finally`. Deliverable 2's second test: shows the guard is a guard, not a
  break, against the real live index, read-only.
- The pre-existing `test_construction.py::test_missing_db_path_raises_configuration_error_and_creates_nothing`
  still passes unchanged -- the `__init__`-time behavior it covers is
  unchanged (same check, now via the shared `_require_db_exists()` helper).
- The `_live_db_unchanged` session fixture in `conftest.py` (unmodified,
  already in force since round 1) printed the BEFORE/AFTER lines quoted
  above and its own assertions passed -- criterion-6 evidence for the whole
  session, including the two new tests that delete a *different*,
  `tmp_path`-scoped file and never touch the live db.

I re-read `explorer/corpus_adapter/adapter.py` in full, `tests/corpus_adapter/conftest.py`,
`tests/corpus_adapter/test_construction.py`, `docs/rounds/R01_corpus_adapter.report.md`,
`CONSTRAINTS.md` O10 (section B) and S2 (section A), and `ARCHITECTURE.md`
section 4.1 (the `connect` line, the "Adapter rules" paragraph) and decision
record A9 before writing any code, per the task's "Read first" list.

## Material alternatives

- **Where to put the repeated `isfile` check.** Considered (a) duplicating
  the check-and-raise block inline in both `__init__` and `connect()`
  (matching round 1's style exactly, minimal diff); (b) factoring it into a
  shared private method `_require_db_exists()` called from both places.
  Chose (b): the task requires the class-level, method-level, and
  `ConfigurationError` docstrings to all describe the guard as a single
  per-call invariant, and a single method is the natural place to hang that
  description on and to guarantee the raised message stays byte-identical
  between the construction-time and per-call checks (two copies of an
  f-string are exactly the kind of drift this correction round exists to
  prevent). This is not a contract change: `CorpusAdapter.__init__` and
  `CorpusAdapter.connect()` keep their existing signatures and externally
  observable behavior; `_require_db_exists` is a new private method, not
  part of the ARCHITECTURE.md 4.1 public surface.
- **S2 allowlist comment: prune or leave `doc_id_from_filename` and
  `embed_query_cpu`.** Grepped the whole module
  (`grep -rn "doc_id_from_filename" explorer/ tests/`) and found the name
  appears only in this one docstring -- it is not called anywhere in
  `adapter.py`. `embed_query_cpu` likewise is never called in `adapter.py`
  itself (it is called in `availability.py`, a sibling file in the same
  package). Considered (a) pruning the comment to only the names actually
  called directly in `adapter.py`; (b) leaving the list as-is, reading it as
  an allowlist/ceiling (what `CONSTRAINTS.md` S2 calls "retrieval calls are
  limited to") rather than an inventory of calls actually made. Chose (b):
  `CONSTRAINTS.md` S2 (the authoritative, un-editable source for this list)
  states the identical eight names as the permitted set, not as a claim
  every one is used; the docstring's own wording ("every call into the RHACO
  module is one of the S2 allowlist") is consistent with that -- a ceiling,
  not an inventory. Pruning would create a second place that could drift
  from `CONSTRAINTS.md` S2 for no benefit, and the task's instruction was
  "keep it accurate," not "keep it minimal." Left unchanged; verified word-
  for-word against `CONSTRAINTS.md` S2's own list to be sure of "accurate."
- **Whether to also guard `availability.probe()`'s own `connect()` call.**
  `explorer/corpus_adapter/availability.py` line 49 calls
  `rhaco_index.connect(db_path)` directly (not through
  `CorpusAdapter.connect()`), as part of `vector_availability()`'s O4
  procedure -- this call is not covered by the fix in this round and could,
  in principle, also re-create a missing db file if the live index vanished
  between `CorpusAdapter.__init__` and a later `vector_availability()` call.
  I considered fixing this too (`availability.py` is inside my owned path,
  `explorer/corpus_adapter/**`), but the task's deliverable list names only
  `explorer/corpus_adapter/adapter.py` and says "No other behaviour change";
  C2's stated hazard and both required tests are specifically about
  `connect()`. Left unchanged and reported below as unresolved uncertainty
  rather than fixed unasked, so as not to conflate a requested fix with a
  same-shaped one nobody asked for in this round.

## Decisions

- `_require_db_exists()` takes no arguments and reads `self.db_path` --
  matches the existing pattern in this file where every method after
  construction reads adapter-owned state rather than being handed the path
  again (e.g. `index_meta`, `vector_availability` already do this).
- The `ConfigurationError` message text is unchanged
  (`f"configured database does not exist: {self.db_path!r} (the adapter
  never creates a database, O10)"`) -- deliverable 1 asks for a message
  "that names the path and cites O10," which round 1's text already did;
  changing the wording gratuitously would only cost anyone grepping for the
  round-1 message text without adding anything the task asked for.
- Left the `# Subtree is canonical in explorer.models...` comment and every
  other method untouched -- confirmed by re-reading the full file after
  editing that the diff touches only the module docstring,
  `ConfigurationError`'s docstring, the new `CorpusAdapter` class docstring,
  `__init__` (three lines: assign `db_path` before the check, call the new
  method, drop the old inline `if`/`raise`), the new `_require_db_exists`
  method, and `connect()` (docstring plus the one added guard line).

## Result

corpus_adapter round 2 of 4 (this correction round) consumed. All three
gates green in the worktree (see Evidence for full output):

- `ruff check explorer tools tests` -- `All checks passed!`
- `pytest tests/corpus_adapter -q` -- **17 passed**, 0 failed, 0 skipped
  (15 from round 1 + the 2 new C2 tests, as specified).
- `tools/l1_index_write_check.py` -- `verdict=PASS` (hits=6, all
  pre-existing `fixtures/build_fixture_index.py` allowlist entries,
  defects=0).

Live index left byte-for-byte as found: `corpus_cards_sha` and `mtime`
identical before and after the full test session (see Evidence).

Worktree clean after two commits on `build/corpus_adapter`:
- `a34a166` -- the guard fix in `adapter.py`.
- `6a17c194f910dabcbe1cf4692b879e12dc4b6f8c` -- the two new tests.

## Unresolved uncertainty

- **`availability.probe()`'s direct `connect()` call is not covered by this
  round's guard.** `explorer/corpus_adapter/availability.py` line 49 calls
  `rhaco_index.connect(db_path)` directly rather than going through
  `CorpusAdapter.connect()`, so `vector_availability()` (and therefore
  `search_hybrid`/`search_graph`, which call it first) has its own,
  unguarded path to the RHACO module's `connect()`. If the live index file
  is removed between a `CorpusAdapter`'s construction and a later
  `vector_availability()` call, this path would still let
  `RHACO_corpus_index.connect()` re-create it -- the same class of hazard
  C2 fixes for the adapter's own `connect()`, in a different call site. Not
  fixed here: out of this round's stated deliverable (`adapter.py` only,
  "No other behaviour change"), and C2's hazard description, deliverables,
  and both required tests name `connect()` specifically. Flagging for the
  Director/integrator to decide whether a follow-up round should extend the
  same guard to `availability.py`'s call site (it would need either a
  guard-and-raise inside `probe()` itself, changing `vector_availability()`
  from "never raises" to something that can raise, or routing that call
  through `CorpusAdapter.connect()` instead of a bare module call -- a
  design choice, not a mechanical copy of this round's fix).
- Everything already listed as unresolved in
  `docs/rounds/R01_corpus_adapter.report.md` (the vector-availability
  probe's 8 s timeout bound never exercised against a genuinely hung
  Ollama; `campaign_subtree`/`dangling_references` not covered by a
  dedicated pytest test; `wrong_doc_for_id`'s exact fixture semantics not
  yet confirmed against a real fixture index) is unchanged by this round --
  none of it is in scope for C2 and none of it was touched.

## Change requests

None this round. No change to any file outside
`explorer/corpus_adapter/**` / `tests/corpus_adapter/**` was needed, and the
round-1 `Subtree`-in-`models.py` change request is unaffected by this
round's diff (still a local dataclass in `adapter.py`, untouched here).

## Assumptions

- The live-index `corpus_cards_sha` observed in this round
  (`9d36e...ca6b40b`) differs from round 1's report
  (`ed86c3c...368816a30`) because the live corpus was reindexed externally
  between the two rounds -- exactly the O10 scenario this task guards
  against, not a defect in this round's work. Confirmed by the session's
  own BEFORE/AFTER match (both reads in this session agree with each
  other) and by O10's own text ("External actors reindex `corpus_index.db`
  while the explorer runs ... both observed in session 3").
- `Settings(db_path=str(db_file))` with an empty `tmp_path` file is
  sufficient to construct a `CorpusAdapter` without touching
  `active_fault`/fault logic in any way that would interfere with the new
  test -- confirmed by running the test (it passes) rather than by reading
  `faults.py` line-by-line, since round 1's existing
  `test_missing_db_path_raises_configuration_error_and_creates_nothing`
  already established this same construction pattern works.
