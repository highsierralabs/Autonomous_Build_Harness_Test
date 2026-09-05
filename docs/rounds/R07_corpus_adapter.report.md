# R07_corpus_adapter -- round report (Round 6 of the build; corpus_adapter round 4 of 4, the LAST round)

## Header

- strand_id: S8-C4
- role: module builder (corpus_adapter)
- model: You are powered by the model named Sonnet 5. The exact model ID is claude-sonnet-5.
- t_start_utc: 2026-09-05T15:27:45Z
- t_end_utc: 2026-09-05T15:47:10Z
- worktree: `C:\highsierralabs\RHACO_Corpus_Explorer\.worktrees\corpus_adapter`
- branch: `build/corpus_adapter`
- base commit (this session's own `git rev-parse HEAD`, first git act): `3e7521bf7b79cf2d2730ef460052a006d5aa4440`
- `git merge-base --is-ancestor f29bcc97f4ba7de455fa32f3591e5d3ccf837976 HEAD`: exit 0 (confirmed before any edit)
- dispatch: RHACO-HND-20260903-001 section 2 I as amended by A1.3; task C4, one batched round, four items in Director-ruled priority order
- prompt sha256 verified: `c0ce0841192189811a3332ab38c2d587b486c3233ac9dd3adab1fcdb26668f3b` (matched)

## Change

Four items, worked in the ruled priority order (1, 2, 3, then 4). All four landed. Commits, in order:

- `a769481` -- `explorer/corpus_adapter/sql.py`: adds D-Q12 (`Q12_CARDS_BY_FILENAME_STEM` +
  `filename_stem_like_pattern`), a card lookup keyed on `cards.doc_filename` rather than
  `doc_id`. Corrects the file's own "adapter.py is the sole importer" docstring claim.
- `2f0bfe6` -- `explorer/corpus_adapter/adapter.py`: `GRAPH_DEGRADED_NOTICE` rewritten;
  `search_graph`'s degraded `mode_effective` changed from `"graph-degraded"` to
  `"graph-degraded-semantic-seed"`; `HYBRID_DEGRADED_NOTICE` examined and left unchanged
  (with a comment recording why); `edges_for` resolves an `amends` edge's `source_cards`
  through the new `_cards_for_filename_stem` (D-Q12) instead of the doc_id-keyed
  `_cards_for_doc_id`. Corrects the module docstring's "the only module in the workspace"
  claim.
- `40994c4` -- `explorer/corpus_adapter/availability.py`: `probe()`'s embed-call bound
  rewritten from `ThreadPoolExecutor(max_workers=1)` (joined on `with`-exit) to a plain
  `threading.Thread(daemon=True)`, waited on via `threading.Event.wait(timeout=
  PROBE_BUDGET_S)`, never joined. Corrects the module docstring's "the sole importer"
  claim and its false "one-shot daemon-thread call" description of the old code.
- `d7fbfba` -- three new test files (below).

No file outside `explorer/corpus_adapter/**` / `tests/corpus_adapter/**` was touched.
`build_state.json`, `ARCHITECTURE.md`, `SCOPE.md`, `explorer/models.py`, and everything
under `explorer/search/**` and `explorer/lineage/**` are unedited.

## Evidence

### Item 1 (SA-1) -- the graph-degraded notice

Read `RHACO_corpus_index.py` directly (`C:/RHACO/rhaco/RHACO_corpus_index.py`, an
allowlisted read) to ground the claim before touching anything:

- `search_hybrid` (lines 1387-1410): under `VecUnavailable`, `rankings = [fts_rank]` --
  a single ranking list -- so `_rrf_fuse` reduces to the FTS order, with the identifier
  short-circuit ahead of it. The fused ordering genuinely collapses to lexical-only.
  **`HYBRID_DEGRADED_NOTICE` is correct as written; left unchanged** (recorded in a
  comment at its definition, `adapter.py`).
- `search_graph` (lines 1559-1573+): seeds = identifier short-circuit UNION top-5
  `search_hybrid` (this is the part that degrades); expansion = 1 hop over the `edges`
  table ONLY, `VecUnavailable` never touches it. The graph itself is not unavailable, and
  the surviving expansion still shapes the final order (seeds first, then expansions by
  anchor-seed rank and relation priority -- not a lexical rank). Both halves of the old
  `GRAPH_DEGRADED_NOTICE` were false.

Fixed `GRAPH_DEGRADED_NOTICE` and the `mode_effective` token (`adapter.py:509-521`);
grepped the whole workspace for every literal consumer of `mode_effective` /
`"graph-degraded"` before deciding the token was safe to change (see "Decisions" and
"Change requests" -- two out-of-scope callers break, both filed).

Tested by `tests/corpus_adapter/test_graph_degraded_subprocess.py` (new): a bounded
(120s) foreground subprocess with `RHACO_CORPUS_DISABLE_VEC=1`, asserting the exact new
token and notice text against a live `search_graph` call. **This is the first thing in
this build's harness to exercise graph mode under `--disable-vec` at all** (the audit's
own motivating observation).

### Item 2 (SA-2) -- the probe budget

Read `availability.py` in full (already required reading) and confirmed by direct
inspection of Python's `concurrent.futures` contract: `ThreadPoolExecutor.__exit__` calls
`shutdown(wait=True)`, which joins every submitted worker regardless of whether
`future.result(timeout=...)` already raised `TimeoutError` in the calling thread. Fixed
with a plain `threading.Thread(daemon=True)` + `threading.Event`, never joined (see
"Decisions" for the two alternatives considered and rejected).

Tested by `tests/corpus_adapter/test_probe_budget.py` (new): a fake `rhaco_index` whose
`embed_query_cpu` sleeps 2.0s, against a monkeypatched `PROBE_BUDGET_S = 0.2`. The
load-bearing assertion is on the CALLER's own `elapsed` wall-clock time
(`elapsed < shortened_budget + 1.0` and `elapsed < SLEEP_S / 2`), not merely on
`result.reason == "embedder_unreachable"` -- the old code already produced that reason
correctly while still blocking for the embed call's full duration. Against the OLD code,
this test would have measured `elapsed` close to 2.0s (the fake's `SLEEP_S`), not close to
0.2s, because `ThreadPoolExecutor.__exit__` would have joined the worker before `probe()`
could return -- that specific comparison is not re-run side-by-side (the old
implementation no longer exists in this file to run), it is stated here as what the old,
documented behaviour would have produced.

### Item 3 -- the deferred amends click-through

Grounded in the live corpus before writing any code, using the conftest.py-documented
shared-`doc_id` parent/amendment pair (`RHACO-HND-20260903-001` and its Amendment A1):

```
$env:PYTHONPATH = "C:\highsierralabs\RHACO_Corpus_Explorer\.worktrees\corpus_adapter"
& "C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe" <probe script>
```

BEFORE the fix:

```
hand doc_id: RHACO-HND-20260903-001 stem: RHACO-HND-20260903-001_Corpus_Explorer_Autonomous_Build_Dispatch
a1   doc_id: RHACO-HND-20260903-001 stem: RHACO-HND-20260903-001_..._Amendment_A1_Cap_Rehome_And_Session_2_Findings
shared doc_id: True
--- hand page ---
IN  amends from_id=<a1 stem> to_id=RHACO-HND-20260903-001 source_cards=[] target_cards=[hand.md, a1.md]
--- a1 page ---
OUT amends from_id=<a1 stem> to_id=RHACO-HND-20260903-001 source_cards=[] target_cards=[hand.md, a1.md]
IN  amends from_id=<a1 stem> to_id=RHACO-HND-20260903-001 source_cards=[] target_cards=[hand.md, a1.md]
```

This confirms, against live data, both the row's own repro (`source_cards=[]` on the
parent's incoming edge -- no link) **and** the caution the dispatch named: the amendment
shares its `doc_id` with its parent, and its own `amends` edge is classified into BOTH
`outgoing` and `incoming` on its own page (the pre-existing double-classification defect,
lineage round-1 open issue / critic ranked issue 7) -- independent of anything this round
touches.

AFTER the fix (same probe, same live data):

```
--- hand page ---
IN  amends ... source_cards=[a1.md] target_cards=[hand.md, a1.md]
--- a1 page ---
OUT amends ... source_cards=[a1.md] target_cards=[hand.md, a1.md]
IN  amends ... source_cards=[a1.md] target_cards=[hand.md, a1.md]
```

The parent page's incoming edge now links to the amendment (the row closed). The
double-classification itself is unchanged (still both `outgoing` and `incoming` on the
amendment's own page -- that classification logic in `edges_for` was not touched), but its
previously-empty `source_cards` on the incoming copy now resolves to the amendment's own
card -- **a self-link where there was previously no link at all**. Stated plainly per the
dispatch's caution: the fix does not fix or worsen the double-classification, but it does
turn the incoming half of that degenerate self-edge into a live self-pointing link.

Tested by `tests/corpus_adapter/test_amends_stem_resolution.py` (new), against the live
corpus, pinning both the fixed behaviour (parent page) and the documented
before/after on the degenerate case (amendment's own page), so the lineage builder does
not have to re-derive either.

### Item 4 -- docstring corrections

Three claims corrected to match ARCHITECTURE.md 4.1's now-enumerated three licensed
importers (commit `f29bcc9`): `adapter.py` lines 2-3, `availability.py` line 22-24 (now
23-29), `sql.py` line 9 (now 9-16). Docstrings only, verified by re-reading each file
after editing; no code changed for this item.

### Gates (exact commands and output tails)

```
cd C:\highsierralabs\RHACO_Corpus_Explorer\.worktrees\corpus_adapter
C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m ruff check explorer tools tests --output-format concise
```
```
All checks passed!
```

```
C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m pytest tests/corpus_adapter -v --tb=short
```
```
collected 24 items
tests/corpus_adapter/test_amends_stem_resolution.py::test_parent_page_incoming_amends_edge_now_links_to_the_amendment PASSED
tests/corpus_adapter/test_amends_stem_resolution.py::test_amendments_own_page_degenerate_self_classification_is_unchanged_by_the_fix PASSED
tests/corpus_adapter/test_cards_and_identity.py::test_cards_for_doc_id_returns_hand_and_amendment PASSED
tests/corpus_adapter/test_cards_and_identity.py::test_card_round_trips_for_hand_and_amendment PASSED
tests/corpus_adapter/test_cards_and_identity.py::test_resolve_identifier_exact_campaign_id PASSED
tests/corpus_adapter/test_catalog.py::test_catalog_cmp_filter_and_lifecycle_state PASSED
tests/corpus_adapter/test_catalog.py::test_facets_global_is_non_empty PASSED
tests/corpus_adapter/test_connect_guard.py::test_connect_raises_after_db_removed_post_construction_and_creates_nothing PASSED
tests/corpus_adapter/test_connect_guard.py::test_connect_still_succeeds_when_db_file_exists PASSED
tests/corpus_adapter/test_connect_guard.py::test_vector_availability_reports_db_unavailable_and_creates_nothing_when_db_removed PASSED
tests/corpus_adapter/test_connect_guard.py::test_vector_availability_against_live_index_is_read_only PASSED
tests/corpus_adapter/test_connect_guard.py::test_probe_short_circuits_before_connect_when_db_missing PASSED
tests/corpus_adapter/test_construction.py::test_missing_db_path_raises_configuration_error_and_creates_nothing PASSED
tests/corpus_adapter/test_graph_degraded_subprocess.py::test_graph_degrades_to_named_seed_channel_when_vec_disabled PASSED
tests/corpus_adapter/test_hybrid_degraded_subprocess.py::test_hybrid_degrades_to_lexical_when_vec_disabled PASSED
tests/corpus_adapter/test_index_meta.py::test_index_meta_keys_and_live_counts PASSED
tests/corpus_adapter/test_lineage.py::test_edges_for_hand_has_incoming_campaign_child_from_cmp PASSED
tests/corpus_adapter/test_lineage.py::test_edges_for_amendment_has_outgoing_amends_from_its_own_stem PASSED
tests/corpus_adapter/test_lineage.py::test_supersession_chain_from_a_catalog_located_superseded_card PASSED
tests/corpus_adapter/test_probe_budget.py::test_probe_bounds_callers_own_elapsed_time_when_embedder_hangs PASSED
tests/corpus_adapter/test_reader.py::test_read_document_returns_headings_with_slugs PASSED
tests/corpus_adapter/test_reader.py::test_is_under_docs_root_rejects_data_tree_and_dotdot_escape PASSED
tests/corpus_adapter/test_search.py::test_search_lexical_has_line_no_and_lexical_hit_excerpts PASSED
tests/corpus_adapter/test_search.py::test_search_hybrid_top_k_and_mode_consistency PASSED
============================= 24 passed in 5.34s ==============================
```

```
C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m pytest tests -q
```
```
........................................................................ [ 27%]
........................................................................ [ 54%]
........................................................................ [ 81%]
................F.................................                       [100%]
================================== FAILURES ===================================
_______________________ test_graph_degrades_on_fixture ________________________
    def test_graph_degrades_on_fixture(fixture_client):
        resp = fixture_client.get("/search", params={"q": "quartz lattice lantern", "mode": "graph"})
        assert resp.status_code == 200
        body = resp.text
>       assert 'data-mode="graph-degraded"' in body
E       assert 'data-mode="graph-degraded"' in '<!doctype html>\n<html lang="en" data-mode="graph-degraded-semantic-seed" data-vector="unavailable">...'
tests\search\test_hybrid_graph_degraded.py:43: AssertionError
=========================== short test summary info ===========================
FAILED tests/search/test_hybrid_graph_degraded.py::test_graph_degrades_on_fixture
1 failed, 265 passed in 26.04s
```

**This one failure is expected, understood, and NOT weakened or worked around.** It is the
direct, foreseen consequence of Item 1's `mode_effective` token change landing in a file
(`tests/search/test_hybrid_graph_degraded.py`) outside this module's owned paths, exactly
as the dispatch's own item-1 text anticipated ("if changing the token would break one,
file it as a change request rather than editing their file"). It is filed below as a
change request, not silenced, not edited, and not disposed by this round.

```
C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe tools\l1_index_write_check.py
```
```
allowlisted: fixtures/build_fixture_index.py:8: [reindex_full] ...
allowlisted: fixtures/build_fixture_index.py:28: [reindex_vec] ...
allowlisted: fixtures/build_fixture_index.py:113: [reindex_full] ...
allowlisted: fixtures/build_fixture_index.py:118: [reindex_full] ...
allowlisted: fixtures/build_fixture_index.py:141: [reindex_full] ...
allowlisted: fixtures/build_fixture_index.py:184: [reindex_vec] ...
l1-index-write-check: hits=6 allowlisted=6 defects=0 verdict=PASS
```

## Material alternatives

- **Item 1 token.** Considered leaving `mode_effective` as `"graph-degraded"` and fixing
  only the notice text, to avoid breaking the two out-of-scope callers found by the grep
  sweep. Rejected: the dispatch is explicit that `mode_effective` itself "must name the
  channel," and a notice/token pair that disagree (prose says "seed channel degraded,"
  token still says bluntly "graph-degraded") is the same class of false-claim defect the
  item exists to remove, just relocated. Chose `graph-degraded-semantic-seed` (the
  dispatch's own suggested shape) and filed change requests for the two breaks instead.
- **Item 2 thread strategy.** Considered (a) a long-lived, module-level, shared single-
  worker `ThreadPoolExecutor` reused across calls, never shut down. Rejected: with
  `max_workers=1`, a hung call occupies the one worker indefinitely, so every subsequent
  probe's task queues behind it and never even starts running until the hang resolves (if
  ever) -- each call would still correctly time out at the caller (since `future.result
  (timeout=...)` times out whether or not the task has started), but tasks would pile up
  unboundedly in the executor's queue for the life of a sustained outage. Considered (b)
  `ThreadPoolExecutor(max_workers=1)` per call without the `with` statement, relying on
  garbage collection instead of an explicit `shutdown()`. Rejected on inspection of
  `concurrent.futures.thread`: the module registers an `atexit` hook that joins ALL
  `ThreadPoolExecutor` worker threads at interpreter exit regardless of whether
  `shutdown()` was ever called -- so this would still block a clean process shutdown for
  up to `OLLAMA_TIMEOUT_S` per hung probe, just not the individual `probe()` call. Chose a
  plain `threading.Thread(daemon=True)`, which sidesteps both hazards: independent per
  call (no shared-queue backlog) and never joined at any point, including interpreter
  exit (daemon threads are simply not joined by the runtime).
- **Item 3 resolution strategy.** Considered a fallback pattern ("try `_cards_for_doc_id`
  first; if empty, try the stem lookup") instead of branching on `relation == "amends"`.
  Rejected: CONSTRAINTS.md O8 states the `amends` relation's `from_id` is ALWAYS a stem,
  never a doc_id, so the direct branch is both more precise (no risk of a doc_id ever
  coincidentally matching a stem pattern, however unlikely) and more legible (the code
  reads as "amends' from_id is a stem" rather than "try one thing, then another").

## Decisions

- `GRAPH_DEGRADED_NOTICE`'s new text and the `mode_effective` token
  `"graph-degraded-semantic-seed"` were chosen to name the specific surviving channel (the
  hybrid seed degrades; the edges-table expansion does not) rather than a vaguer
  "graph-partial" or similar -- matching the dispatch's own suggested shape and staying
  literal about the mechanism (`search_graph` -> `search_hybrid` for seeds -> 1-hop
  `edges` expansion), so a reader does not have to infer which of the two channels is
  named.
- `HYBRID_DEGRADED_NOTICE` was examined against RHACO_corpus_index.search_hybrid's own
  code (not just its docstring) and found correct; it is unchanged, and the reasoning is
  recorded in a comment at its definition so a future reader does not have to re-derive it.
- The Item 2 fix's abandoned-worker safety argument: `embed_query_cpu` performs a
  stateless, read-only HTTP call to a local Ollama embedding endpoint; there is no
  transaction, lock, or shared mutable state it could corrupt by being abandoned mid-flight,
  and the module's own `OLLAMA_TIMEOUT_S=300` still bounds how long it can run before it
  self-terminates (successfully or by raising) even when nothing is waiting on it anymore.
- Item 3's stem-aware resolution is additive and precise (branches only on
  `relation == "amends"`), so no existing caller's behaviour for `cites`/`supersedes`/
  `campaign_child` edges changes; `target_cards` (the `to_id` side) is untouched for every
  relation, since O8 states `to_id` is always a normal doc_id, including for `amends`.
- Where a fix required a change outside this module's owned paths (ARCHITECTURE.md's
  `mode_effective` enum and D-Q table, `explorer/models.py`'s enum comment,
  `explorer/search/templates/search/search.html`'s literal-string checks,
  `tests/search/test_hybrid_graph_degraded.py`'s assertions), the fix was still made
  correctly here and the break was filed as a change request rather than either (a)
  silently weakening the fix to avoid the break, or (b) editing a file outside scope.

## Result

Module round consumed: **corpus_adapter round 4 of 4, the last round this module gets.**
No round 5 exists; nothing here was deferred on the assumption of a future round.

| Item | Disposition | Note |
|---|---|---|
| 1 -- SA-1, graph-degraded notice | **landed** | Notice + `mode_effective` token both corrected; `HYBRID_DEGRADED_NOTICE` examined and confirmed correct; new subprocess test. Breaks two out-of-scope callers (filed as change requests) and one out-of-scope test now fails in the full suite (`tests -q`: 1 failed, 265 passed) -- expected, understood, not weakened. |
| 2 -- SA-2, probe budget | **landed** | Real wall-clock bound via an unjoined daemon thread; docstring's false daemon-thread claim corrected; new test asserts the caller's own elapsed time, not just the return value. |
| 3 -- amends click-through | **landed** | D-Q12 + stem-aware `edges_for` resolution; verified live (before/after) against the corpus's own shared-doc_id parent/amendment pair; the pre-existing double-classification caution addressed explicitly (unchanged by this fix, but its incoming copy's `source_cards` now self-resolves) and pinned by a new test. |
| 4 -- sole-importer docstrings | **landed** | All three docstrings (`adapter.py`, `availability.py`, `sql.py`) corrected to match ARCHITECTURE.md 4.1's three-importer enumeration; docstrings only, no code. |

All four items landed; nothing was declared BOUNDED_FAIL. Gates: ruff clean;
`pytest tests/corpus_adapter -q` 24/24 green; `pytest tests -q` 265/266 green with the one
documented, expected, out-of-scope failure above; `l1_index_write_check.py` PASS.

## Unresolved uncertainty

- **What a fifth round would have done, if one existed** (this is a record, not a
  request -- there is no round 5): it would (a) actually edit
  `explorer/search/templates/search/search.html`'s two `in (...)` tuple checks and
  `tests/search/test_hybrid_graph_degraded.py`'s assertions to the new token/text, and
  file the matching update to `ARCHITECTURE.md` 4.1's `mode_effective` enum and D-Q table
  and `explorer/models.py`'s enum comment -- all four are change requests here rather than
  fixes, since all four are outside `explorer/corpus_adapter/**`/`tests/corpus_adapter/**`;
  (b) extend the graph-mode regression to the HTML/template layer directly (this round's
  `test_graph_degraded_subprocess.py` proves the adapter's own `mode_effective`/notice, but
  does not reach the search page's rendered `data-mode` attribute the way
  `tests/search/test_hybrid_graph_degraded.py` does -- that layer is owned by the search
  module, not this one); (c) resolve the pre-existing double-classification defect on an
  amendment's own lineage page (unchanged by this round, pinned by
  `test_amends_stem_resolution.py`'s second test) -- that is lineage-classification logic
  in `edges_for`'s `outgoing`/`incoming` branching, not this round's stem-resolution
  target, and is recorded as the lineage builder's concern per the dispatch's own framing;
  (d) a genuinely slow (not merely sleeping-in-a-fake) embedder run against a real,
  artificially-throttled Ollama endpoint, to close the very last sliver of "verified by
  code reading and a fake, not an observed real slow run" that round 1 originally flagged
  -- this round's `test_probe_budget.py` closes the load-bearing half (the caller's own
  elapsed time is bounded) but still uses a fake `rhaco_index`, not a real embedder
  process.
- The exact scope of `explorer/search/templates/search/search.html`'s rendering
  degradation from the token change was read (two `{% if evidence.retrieval_mode in
  (...) %}` checks, lines ~44 and ~50) but not run end-to-end through that template in
  this round (that would require touching the search module's own test harness, out of
  scope) -- the effect is stated from reading the template, not from an observed render;
  labelled here as UNVERIFIED-by-behavior for that specific template, though the
  `data-mode-effective` attribute interpolation itself (which just prints the value
  verbatim) WAS observed to carry the new token correctly through the full `pytest tests
  -q` run above.

## Change requests

1. **Requestor:** corpus_adapter (S8-C4, item 1).
   **Affected path:** `ARCHITECTURE.md` section 4.1, the `ModeResult.mode_effective` line
   (`identifier | lexical | hybrid | hybrid-degraded-lexical | graph | graph-degraded`).
   **Evidence:** `explorer/corpus_adapter/adapter.py`'s `search_graph` now emits
   `"graph-degraded-semantic-seed"`, not `"graph-degraded"`, for the degraded case
   (commit `2f0bfe6`).
   **Compatibility impact:** the documented enum is stale; any reader of ARCHITECTURE.md
   4.1 would derive the wrong token.
   **Migration:** replace `graph-degraded` with `graph-degraded-semantic-seed` in that
   line.
   **Invalidated tests/probes:** none directly (this is prose), but see request 3 below.

2. **Requestor:** corpus_adapter (S8-C4, item 1).
   **Affected path:** `explorer/models.py` line 170, the `ModeResult.mode_effective`
   inline comment (same enum, same staleness as request 1).
   **Evidence:** same as request 1.
   **Compatibility impact:** documentation only; `explorer/models.py` is
   integrator-owned and outside this module's writable paths.
   **Migration:** update the comment's enum to include
   `graph-degraded-semantic-seed` in place of `graph-degraded`.
   **Invalidated tests/probes:** none.

3. **Requestor:** corpus_adapter (S8-C4, item 1).
   **Affected path:** `explorer/search/templates/search/search.html`, lines ~44 and ~50
   (`{% if evidence.retrieval_mode in ("graph", "graph-degraded") %}` and the four-tuple
   variant including `"hybrid-degraded-lexical"`).
   **Evidence:** `Evidence.retrieval_mode` is set from `mode_effective`
   (`adapter.py::_items_from_doc_ids`), so these Jinja checks stop matching once
   `mode_effective` is `"graph-degraded-semantic-seed"`; some evidence-panel markup
   gated by these checks would stop rendering for degraded graph-mode results.
   **Compatibility impact:** a rendering regression in the search module, not a crash;
   this file is outside this module's owned paths (`explorer/search/**`).
   **Migration:** add `"graph-degraded-semantic-seed"` to both tuples (or replace
   `"graph-degraded"` with it, if the old token is never produced again after request 4
   below lands).
   **Invalidated tests/probes:** request 4 (below) is the test that currently fails
   because of this.

4. **Requestor:** corpus_adapter (S8-C4, item 1).
   **Affected path:** `tests/search/test_hybrid_graph_degraded.py`,
   `test_graph_degrades_on_fixture` (lines ~43-45): asserts
   `'data-mode="graph-degraded"'`, `'data-mode-effective="graph-degraded"'`, and the old
   `GRAPH_NOTICE` module-level constant (line ~9) against the fixture's degraded graph
   search.
   **Evidence:** this test now fails -- confirmed by the `pytest tests -q` run pasted
   above (`FAILED tests/search/test_hybrid_graph_degraded.py::test_graph_degrades_on_fixture`).
   This is the ONE test failure in the full-suite gate, foreseen and not worked around.
   **Compatibility impact:** the test correctly encoded the old, false behaviour; it now
   needs to encode the corrected one. This file is outside this module's owned paths
   (`tests/search/**`).
   **Migration:** update `GRAPH_NOTICE` to the new text (see `GRAPH_DEGRADED_NOTICE` in
   `explorer/corpus_adapter/adapter.py`) and the two assertions to
   `graph-degraded-semantic-seed`.
   **Invalidated tests/probes:** itself; no other test in `tests/search/**` was observed
   to fail.

5. **Requestor:** corpus_adapter (S8-C4, item 3).
   **Affected path:** `ARCHITECTURE.md` section 4.1's documented D-Q1..D-Q11 SQL table
   (and its own "adding a twelfth is a change request" framing, both in that file and
   mirrored in `sql.py`'s module docstring, which this round corrected on its own side).
   **Evidence:** `explorer/corpus_adapter/sql.py` now defines
   `Q12_CARDS_BY_FILENAME_STEM` (commit `a769481`), the twelfth statement, per
   SCOPE.md's own named path to closing its deferred amends click-through row.
   **Compatibility impact:** documentation only; no behavior depends on the table being
   exhaustive at eleven.
   **Migration:** add a `D-Q12` row to ARCHITECTURE.md 4.1's table: purpose "card by
   document filename stem (amends resolution, O8)"; statement
   `SELECT <21 cols> FROM cards WHERE doc_filename LIKE ? ESCAPE '\' ORDER BY yaml_path`.
   **Invalidated tests/probes:** none.

6. **Requestor:** corpus_adapter (S8-C4, item 3, informational -- not a defect).
   **Affected path:** lineage module (the `edges_for` `outgoing`/`incoming`
   classification logic itself, not this round's stem-resolution change).
   **Evidence:** `test_amends_stem_resolution.py::
   test_amendments_own_page_degenerate_self_classification_is_unchanged_by_the_fix`,
   and the live before/after probe in this report's Evidence section: an amendment
   sharing its `doc_id` with its parent has its own `amends` edge classified into BOTH
   `outgoing` and `incoming` on its own lineage page (pre-existing; lineage round-1 open
   issue, critic ranked issue 7). This round's fix does not touch that classification
   logic, but it DOES change what the incoming copy's `source_cards` resolves to: from
   empty (no link) to the amendment's own card (a self-link).
   **Compatibility impact:** a rendering change for this one degenerate case, on a
   surface (lineage's HTML rendering) this module does not own.
   **Migration:** the lineage builder should decide whether a self-pointing "amended by"
   link is acceptable, worth suppressing, or worth fixing at the classification root
   (not resolving it here, since it is not this round's target and the classification
   code is outside this module).
   **Invalidated tests/probes:** none; this is new coverage, not a break.

## Assumptions

- The dispatch's suggested token shape (`graph-degraded-semantic-seed`) was taken as a
  concrete, adoptable value rather than merely an illustrative example, since it names
  the channel precisely and no better alternative presented itself during the grep sweep
  for consumers.
- `explorer/corpus_adapter/**` and `tests/corpus_adapter/**` are read as the complete set
  of this module's writable paths per the dispatch's working rule 1; the round report
  path (`docs/rounds/R07_corpus_adapter.report.md`) is explicitly named as an additional
  writable path in that same rule and is treated as such.
- The live corpus's `RHACO-HND-20260903-001` / Amendment A1 shared-`doc_id` pair (already
  used by `conftest.py` for other tests) was re-verified directly against the live index
  through the adapter (read-only) before being used to ground both the Item 3 fix and its
  caution, rather than trusted from the dispatch text or `conftest.py`'s comment alone.
- `pytest tests -q`'s single failure (`tests/search/test_hybrid_graph_degraded.py::
  test_graph_degrades_on_fixture`) is assumed to be the ONLY casualty of the Item 1 token
  change workspace-wide; this was checked by grepping the full workspace (not just
  `tests/search/`) for `"graph-degraded"` and `mode_effective` literal consumers before
  making the change, and confirmed by the full-suite run showing exactly one failure and
  265 passes.
