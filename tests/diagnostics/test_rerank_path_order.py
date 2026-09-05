"""Path-order conformance for _rerank_artifact_present's sys.path handling
(R07 diagnostics round 2; CONSTRAINTS.md S2; DISPATCH_PARAMETERS.md item B;
explorer/corpus_adapter/paths.py ensure_rhaco_importable docstring).

S2's import form requires RHACO_PATH_ENTRIES to be APPENDED to sys.path, never
inserted at position 0 -- so workspace code already on sys.path keeps priority
over a same-named RHACO module for every subsequent import in the process. The
pre-fix code did `sys.path.insert(0, entry)`; a membership-only test ("the
entries are present") passes on both the defective and the fixed code and
proves nothing about order. These tests assert ORDER: a workspace entry
already on sys.path before the call must still precede every RHACO_PATH_ENTRIES
entry after the call.
"""
from __future__ import annotations

import sys

from explorer.config import RHACO_PATH_ENTRIES
from explorer.diagnostics.service import _rerank_artifact_present

_SENTINEL = r"C:\fake\workspace\sentinel"


def _strip_rhaco_entries() -> None:
    """Remove every occurrence of RHACO_PATH_ENTRIES from sys.path so each test
    starts from a known state, regardless of what an earlier test in the same
    process already appended (build_view's own tests call
    _rerank_artifact_present, which mutates process-global sys.path)."""
    for entry in RHACO_PATH_ENTRIES:
        while entry in sys.path:
            sys.path.remove(entry)


def test_rhaco_entries_do_not_precede_a_preexisting_workspace_entry():
    """The distinguishing assertion (task item 2): after the call, a workspace
    entry that was already on sys.path keeps a lower index than every
    RHACO_PATH_ENTRIES entry. sys.path.insert(0, entry) -- the pre-fix
    behavior -- pushes the sentinel to a higher index and lands the RHACO
    entries ahead of it, failing both assertions below; sys.path.append(entry)
    -- the fix -- leaves the sentinel's index untouched and lands the RHACO
    entries after it, passing both."""
    saved = list(sys.path)
    try:
        _strip_rhaco_entries()
        sys.path.insert(0, _SENTINEL)
        sentinel_index_before = sys.path.index(_SENTINEL)
        assert sentinel_index_before == 0

        _rerank_artifact_present()

        sentinel_index_after = sys.path.index(_SENTINEL)
        assert sentinel_index_after == sentinel_index_before, (
            "a pre-existing workspace entry must not be displaced by the RHACO "
            "path setup -- it was, which means an entry was inserted ahead of it"
        )
        for entry in RHACO_PATH_ENTRIES:
            assert entry in sys.path
            assert sys.path.index(entry) > sentinel_index_after, (
                f"{entry!r} precedes the pre-existing workspace entry {_SENTINEL!r} "
                "in sys.path -- S2 requires RHACO entries to be appended, not inserted "
                "at position 0"
            )
    finally:
        sys.path[:] = saved


def test_second_call_is_idempotent_and_mutates_sys_path_no_further():
    """Idempotence (task item 3): the diagnostics page can be loaded many times
    in one process, so a second call must add nothing and reorder nothing once
    the RHACO entries are already present."""
    saved = list(sys.path)
    try:
        _strip_rhaco_entries()

        _rerank_artifact_present()
        path_after_first_call = list(sys.path)
        for entry in RHACO_PATH_ENTRIES:
            assert path_after_first_call.count(entry) == 1

        _rerank_artifact_present()

        assert sys.path == path_after_first_call
    finally:
        sys.path[:] = saved
