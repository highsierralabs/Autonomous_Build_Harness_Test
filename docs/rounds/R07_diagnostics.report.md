# R07 -- diagnostics (task B13, path-order conformance)

## Header

- Strand: S8-B13, role module builder (diagnostics), tier mid, model Claude Sonnet 5
  (`claude-sonnet-5`), pattern #3 candidate (worktree-isolated builder), round 6 of
  the build (three concurrent builders, the A1.3 cap). Diagnostics module round 2
  of 4.
- Worktree: `C:\highsierralabs\RHACO_Corpus_Explorer\.worktrees\diagnostics`, branch
  `build/diagnostics`, base commit `3e7521bf7b79cf2d2730ef460052a006d5aa4440`
  (`git rev-parse HEAD`, first git act; contains `f29bcc9` per
  `git merge-base --is-ancestor`, confirmed).
- Interpreter: `C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe`
  (Python 3.13).
- t_start: 2026-09-05T15:27:46Z UTC. t_end: see StructuredOutput `t_end_utc`.
- Head commit at close: see StructuredOutput `head_commit`.

## Change

Single defect closed, in the owned paths only (`explorer/diagnostics/**`,
`tests/diagnostics/**`, this report). No other file touched.

- `explorer/diagnostics/service.py`:
  - `_rerank_artifact_present()` no longer reimplements the RHACO `sys.path`
    setup loop. It now calls
    `explorer.corpus_adapter.paths.ensure_rhaco_importable()`, which appends
    (never inserts at position 0) each entry in `RHACO_PATH_ENTRIES`, guarded by
    `if entry not in sys.path`. The prior code did
    `sys.path.insert(0, entry)` -- inserting the RHACO directories at the front
    of `sys.path`, giving `C:\RHACO\rhaco` / `C:\RHACO\tools` import priority
    over the workspace's own modules for the rest of the process. That is the
    conformance defect this round closes (S2; the rule as stated in
    `explorer/corpus_adapter/paths.py` lines 30-37's own docstring).
  - The now-unused `import sys` and `from explorer.config import
    RHACO_PATH_ENTRIES` were removed (the delegated function owns both); a new
    `from explorer.corpus_adapter.paths import ensure_rhaco_importable` import
    was added.
  - The function's docstring was rewritten to state the delegation and the
    path-order rule it now follows, and to restate idempotence in terms of the
    delegated guard rather than a locally reimplemented one.
- `tests/diagnostics/test_rerank_path_order.py` (new file): two tests --
  `test_rhaco_entries_do_not_precede_a_preexisting_workspace_entry` (the ORDER
  assertion the task requires) and
  `test_second_call_is_idempotent_and_mutates_sys_path_no_further` (task item 3).
- `docs/rounds/R07_diagnostics.report.md` (this report).

## Evidence

Checks actually run, exact commands and output tails:

```
$ cd C:\highsierralabs\RHACO_Corpus_Explorer\.worktrees\diagnostics
$ git rev-parse HEAD
3e7521bf7b79cf2d2730ef460052a006d5aa4440

$ git merge-base --is-ancestor f29bcc97f4ba7de455fa32f3591e5d3ccf837976 HEAD && echo ANCESTOR_OK
ANCESTOR_OK

$ C:/highsierralabs/RHACO_Corpus_Explorer/.venv/Scripts/python.exe -m ruff check explorer tools tests --output-format concise
All checks passed!

$ C:/highsierralabs/RHACO_Corpus_Explorer/.venv/Scripts/python.exe -m pytest tests/diagnostics -q
...........................                                              [100%]
27 passed, 2 warnings in 1.19s
(warnings are the pre-existing StarletteDeprecationWarning/DeprecationWarning
from the fastapi/starlette install itself, unrelated to this round's code --
present in the R01 report too)

$ C:/highsierralabs/RHACO_Corpus_Explorer/.venv/Scripts/python.exe -m pytest tests -q
........................................................................ [ 27%]
........................................................................ [ 54%]
........................................................................ [ 81%]
................................................                         [100%]
264 passed, 2 warnings in 25.58s

$ C:/highsierralabs/RHACO_Corpus_Explorer/.venv/Scripts/python.exe tools/l1_index_write_check.py
l1-index-write-check: hits=6 allowlisted=6 defects=0 verdict=PASS
```

27 = the 25 pre-existing `tests/diagnostics` tests (R01 baseline, confirmed
unchanged in content) plus the 2 new tests in `test_rerank_path_order.py`. 264 =
the 262-test baseline the dispatch names plus the same 2 new tests, confirming
no other module's tests regressed from this file's changed imports (the dispatch's
stated reason for running the full suite: "a `sys.path` change can affect any
module that imports the RHACO modules").

Test-by-test claims:

- `test_rhaco_entries_do_not_precede_a_preexisting_workspace_entry` -- asserts
  that a sentinel path entry inserted at `sys.path[0]` **before** the call keeps
  index 0 **after** the call, and that every `RHACO_PATH_ENTRIES` entry lands at
  a **higher** index than the sentinel. This is the assertion that distinguishes
  the two implementations (see "Decisions" and inline docstring): against the
  pre-fix `sys.path.insert(0, entry)` code, both parts of this assertion fail
  (the sentinel is displaced to a higher index, and the RHACO entries end up at
  indices 0/1, below the sentinel). I ran the test against the actual pre-fix
  code (temporarily restored, then put back) to confirm it actually fails on
  the defect it targets, rather than only reasoning about it -- exact commands
  and output below.
- `test_second_call_is_idempotent_and_mutates_sys_path_no_further` -- asserts a
  second `_rerank_artifact_present()` call, once the RHACO entries are already
  present, produces byte-for-byte the same `sys.path` list as the first call
  (task item 3).

Manual confirmation that the new test actually fails against the pre-fix code
(distinguishing power; the fixed file was backed up, HEAD's pre-fix version
written in its place, the test run, then the fixed file restored -- the final
diff is unaffected, confirmed by `git diff --stat` and re-running all three
gates afterward, both reproduced in this section):

```
$ cp explorer/diagnostics/service.py "$TEMP/service_fixed_backup.py"
$ git show HEAD:explorer/diagnostics/service.py > explorer/diagnostics/service.py
$ C:/highsierralabs/RHACO_Corpus_Explorer/.venv/Scripts/python.exe -m pytest tests/diagnostics/test_rerank_path_order.py -q
...
>           assert sentinel_index_after == sentinel_index_before, (
E           AssertionError: a pre-existing workspace entry must not be displaced by the RHACO path setup -- it was, which means an entry was inserted ahead of it
E           assert 2 == 0
FAILED tests/diagnostics/test_rerank_path_order.py::test_rhaco_entries_do_not_precede_a_preexisting_workspace_entry
1 failed, 1 passed in 0.10s
$ cp "$TEMP/service_fixed_backup.py" explorer/diagnostics/service.py   # restore the fix
```

Then re-ran all three required gates against the restored (fixed) file to
confirm nothing was disturbed by the revert/restore -- identical results to
the ones already pasted above (`ruff`: All checks passed!; `tests/diagnostics`:
27 passed; `tests`: 264 passed; `l1_index_write_check.py`: hits=6
allowlisted=6 defects=0 verdict=PASS), and `git diff --stat
explorer/diagnostics/service.py` unchanged at `1 file changed, 14
insertions(+), 6 deletions(-)`.

Everything else in this report not covered by a named command/test above is
UNVERIFIED.

## Material alternatives

- **Delegate to `ensure_rhaco_importable()` vs. fix the local loop in place.**
  The task's own text names this as the obvious move and asks it be considered
  first. Considered keeping a local, corrected loop
  (`sys.path.append(entry)` inline in `service.py`) instead of importing
  `explorer.corpus_adapter.paths`. Rejected in favor of delegation -- see
  "Decisions" for the reasoning; this is the one substantive choice this round
  makes, so it is recorded in both sections rather than one.
- **Where the new test lives.** Considered adding the two new tests to the
  existing `tests/diagnostics/test_service.py` (which already imports
  `_rerank_artifact_present` indirectly via `build_view`) versus a new file.
  Chose a new file, `test_rerank_path_order.py`: the two tests mutate and
  restore process-global `sys.path`, which is a materially different hazard
  class from `test_service.py`'s pure-dataclass assertions (a bug in the
  save/restore `finally` block would leak state into every other test module in
  the same pytest process, not just this one) -- isolating it by filename makes
  that hazard visible to a reviewer without reading the whole file, and keeps
  `test_service.py` free of `sys` as an import.
- **Sentinel value form.** Considered using one of the real
  `RHACO_PATH_ENTRIES` strings' sibling directories, or an empty string, as the
  "pre-existing workspace entry". Chose a fabricated, obviously-fake path
  (`C:\fake\workspace\sentinel`) that cannot collide with anything really on
  `sys.path` in this venv (verified by asserting `sentinel_index_before == 0`
  immediately after insertion, i.e., it was not already present elsewhere).

## Decisions

- **Took the recommended move: delegate to
  `explorer.corpus_adapter.paths.ensure_rhaco_importable()`.** Reasoning:
  - One rule, one implementation -- the task's own stated rationale. A second,
    independently-typed loop in `service.py` would need to be kept in sync with
    `paths.py` by discipline alone (exactly the failure mode that produced this
    round's defect: two copies of "the same" loop drifted, one insert, one
    append, and no test caught it).
  - No circular-import risk: verified by reading, not merely assuming.
    `explorer/corpus_adapter/adapter.py` (imported eagerly by
    `explorer/corpus_adapter/__init__.py`) imports only `explorer.faults`,
    `explorer.config`, `explorer.corpus_adapter.{availability,paths,sql}`, and
    `explorer.models` at module level (`adapter.py` lines 20-31) -- nothing in
    `explorer.corpus_adapter`'s import chain imports `explorer.diagnostics`, so
    `explorer.diagnostics.service` importing `explorer.corpus_adapter.paths`
    creates no cycle. `RHACO_corpus_index` itself is imported lazily, inside a
    method (`adapter.py` line 121, "deliberate post-sys.path-append import
    (S2)"), not at module import time, so importing the `corpus_adapter`
    package from `diagnostics` has no side effect beyond ordinary class/function
    definition -- it does not itself touch `C:\RHACO`.
  - This is not new coupling of the kind ARCHITECTURE.md 4.1 licenses
    separately: `diagnostics/service.py`'s licensed act is importing
    `RHACO_corpus_index` directly (O17, for the one constant read) -- that import
    is unchanged by this round. What changed is *how sys.path is prepared*
    before that already-licensed import runs, and `paths.py` is the one module
    in the product tree whose job is exactly that (its own docstring: "Pure
    path-string and sys.path logic"). Reusing it does not make diagnostics a
    RHACO importer through the adapter; the RHACO import is still direct, in
    `service.py`, as ARCHITECTURE.md 4.1's table already documents.
  - I did not take the fallback (a corrected local `sys.path.append` loop)
    because the task's own text is explicit that keeping a second copy requires
    a stated reason for why one rule now lives in two places and what keeps
    them in step -- I found no such reason; the risk the fallback would carry
    (silent redrift) is exactly what delegation removes.
- **Docstring rewrite** states the delegation, the rule in one sentence
  (append, never insert at 0, so workspace code shadows first), and idempotence
  in terms of the delegated guard -- so a future reader of `service.py` alone,
  without cross-referencing `paths.py`, still gets the rule correctly, while the
  single source of truth for *enforcing* it stays in `paths.py`.
- **Test design: assert order via a pre-existing sentinel, not membership.**
  Membership (`entry in sys.path`) passes on both the defective and fixed code,
  as the task states explicitly -- worthless here. The assertion that
  distinguishes them is relative position against something that was on
  `sys.path` *before* the call: `sys.path.insert(0, entry)` necessarily pushes
  every already-present entry to a higher index (or, if inserting multiple
  entries, further still); `sys.path.append(entry)` necessarily leaves every
  already-present entry's index untouched. I verified this distinguishing power
  empirically against the actual pre-fix code (Evidence section) rather than
  only reasoning about it.
- **Cleanup helper (`_strip_rhaco_entries`).** Other tests in this suite
  (`test_service.py`'s `build_view`-based tests) call `_rerank_artifact_present`
  too, and `sys.path` mutation is process-global and not undone between test
  modules by pytest itself -- so by the time this test file's tests run in the
  full-suite invocation, `RHACO_PATH_ENTRIES` may already be present on
  `sys.path` from an earlier test in the same process. Both new tests strip
  those entries first so each starts from a known, deterministic state
  regardless of run order or what ran before it.

## Result

Module round consumed: **diagnostics round 2 of 4.** The round's scope was the
path-order fix only -- no other change was made to `explorer/diagnostics/**` or
`tests/diagnostics/**` beyond what "Change" describes above. All three required
gates pass (Evidence section, exact commands and output above): ruff clean over
`explorer tools tests`; `tests/diagnostics` 27/27 passed; the full suite `tests`
264/264 passed; `tools/l1_index_write_check.py` PASS (hits=6, all
allowlisted, defects=0 -- unchanged from before this round's edit, since this
round touches no index-writing function name). The worktree is clean at close
(see StructuredOutput `worktree_clean`).

## Unresolved uncertainty

- **Does any other file in the workspace mutate `sys.path` in a
  non-conformant way?** Established by:
  `grep -rn "sys\.path" --include="*.py" . | grep -v "\.venv" | grep -v "__pycache__"`
  run from the worktree root. Yes -- several, in two distinct classes:
  1. **`fixtures/build_fixture_index.py`** (lines 44-55): does
     `sys.path.insert(0, _WORKSPACE_ROOT)` and, in a loop over what appears to
     be the same RHACO path entries, `sys.path.insert(0, _entry)` -- the same
     insert-at-0 shape as this round's defect. This file matters more than the
     others below: ARCHITECTURE.md 4.1 names it as one of the *three licensed
     product-tree RHACO importers* (the same table this round's dispatch cites
     for `diagnostics/service.py`), so it is arguably in scope for the same S2
     rule, not merely an instrument. It is outside my owned paths
     (`explorer/diagnostics/**`, `tests/diagnostics/**`) -- filed as a change
     request below rather than fixed here.
  2. **Instrument/test code, outside the product-tree invariant** (per
     ARCHITECTURE.md 4.1's own carve-out: "`preflight/`... `tests/`... and
     `tools/`... are hand instruments, test code and integrator oracles -- not
     product"): `preflight/item12_import.py` and `item13_vec.py`
     (`sys.path.insert(0, ...)` / `insert(1, ...)`), `tools/l4_card_agreement_check.py`,
     `tools/l4_gold_oracle.py`, `tools/probe_corpus_explorer.py` (each
     `sys.path.insert(0, WORKSPACE)`), and `tests/lineage/conftest.py`,
     `tests/reader/conftest.py`, `tests/probe/test_evaluate_page.py`,
     `tests/probe/test_fixture_builder.py`, `tests/probe/test_qualification_state.py`,
     `tests/probe/test_workflow_verdicts.py` (each `sys.path.insert(0, ...)`
     for either the workspace root or an RHACO path). None of these are in my
     owned paths; I changed nothing in them. Whether the S2 append-not-insert
     rule was ever intended to bind instrument/test code the way it binds
     product code is itself a question for the integrator, not something I
     decided here -- I report the grep result plainly and take no position on
     it beyond what ARCHITECTURE.md 4.1 already states about scope.
  - `explorer/corpus_adapter/paths.py` and `explorer/diagnostics/service.py`
    (this round's fix) are the only two hits that use `sys.path.append` /
    delegate to it; every other hit above uses `insert(0, ...)` or
    `insert(1, ...)`.

## Change requests

- **Requestor:** diagnostics (B13).
  **Affected contract/path:** `fixtures/build_fixture_index.py` lines 44-55
  (integrator/O3-owner-owned; outside `explorer/diagnostics/**` and
  `tests/diagnostics/**`).
  **Evidence:** the file does
  `sys.path.insert(0, _WORKSPACE_ROOT)` (line 49) and, in a loop, `sys.path.insert(0,
  _entry)` (line 55) for what its own comment (lines 44-46) describes as making the
  RHACO directories importable -- the same insert-at-front shape this round's
  dispatch identified as the S2 conformance defect in `diagnostics/service.py`.
  Unlike the instrument/test hits in "Unresolved uncertainty," this file is one of
  the three ARCHITECTURE.md 4.1 licensed product-tree importers, so it is the one
  other candidate for the same class of finding.
  **Compatibility impact:** unknown without reading the full file's call order and
  intent (I did not read past what the grep context shows, since the file is
  outside my owned paths and reading more would not change what I am permitted to
  do with it) -- a build-time-only script inserting at position 0 may or may not
  carry the same "shadows a production import" risk that a request-path service
  function does; that assessment is for the file's owner.
  **Migration:** if the owner agrees the same rule should bind here, the fix is
  structurally identical to this round's: append (or delegate to
  `explorer.corpus_adapter.paths.ensure_rhaco_importable()`, if this script's own
  execution context can import that module) instead of inserting at 0.
  **Invalidated tests/probes:** none known -- I did not run or read this file's own
  tests; any fix here would need its own owner-run regression check, not one I can
  supply from this worktree per my write scope.

## Assumptions

- `RHACO_PATH_ENTRIES` and `ensure_rhaco_importable`'s guard (`if entry not in
  sys.path`) continue to use plain string equality (not `os.path.normcase` or
  `os.path.realpath`) as `paths.py` already implements it; this round's test
  relies on that same equality semantics (`entry in sys.path`,
  `sys.path.index(entry)`) and would need revisiting if `paths.py` ever starts
  normalizing entries before the membership check.
- The full-suite run (264 passed) is read as confirming no other module's tests
  regressed from this file's changed top-level imports (removing `sys`, removing
  `RHACO_PATH_ENTRIES`, adding `ensure_rhaco_importable`) and from the changed
  runtime behavior of `_rerank_artifact_present` itself (now appending instead of
  inserting) -- I did not additionally audit every one of the 264 tests
  individually for a dependency on RHACO-vs-workspace import priority; the
  suite-level green is the evidence, not a claim that I traced each test's
  import graph by hand.
