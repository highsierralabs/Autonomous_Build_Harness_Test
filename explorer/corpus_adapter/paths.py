"""Junction-aware path handling for the corpus adapter.

ARCHITECTURE.md 4.1 (paths.py bullet); CONSTRAINTS.md O1 / O13; decision A10.

Pure path-string and sys.path logic -- this module never imports
RHACO_corpus_index or RHACO_tool_catalog_librarian (adapter.py is the sole
importer, ARCHITECTURE.md section 2).

`C:\\RHACO` is an NTFS junction to `C:\\highsierralabs\\RHACO` (O13): the two
spellings are the same physical location, and index rows can carry either one
(the module's own constants use the junction spelling; a row written before
the junction existed, or written by a tool that resolved it, can carry the
physical spelling). `os.path.realpath` resolves a junction on this host to the
physical spelling with no `\\\\?\\` prefix (verified empirically against both
spellings of the live docs root before writing this module); combined with
`os.path.normcase` it also collapses any `..` segment and any case difference,
which is what makes `is_under_docs_root` both junction-proof and traversal-proof
in one check (decision A10).
"""
from __future__ import annotations

import os
import sys

from explorer.config import RHACO_PATH_ENTRIES, RHACO_TREES

RHACO_JUNCTION, RHACO_PHYSICAL = RHACO_TREES


def ensure_rhaco_importable() -> None:
    """Append the module's own directories to sys.path (S2 / DISPATCH_PARAMETERS
    item B: import form is path entries, not a package). Appended, never
    inserted at position 0, so workspace code always shadows a same-named
    module first. Idempotent -- safe to call more than once."""
    for entry in RHACO_PATH_ENTRIES:
        if entry not in sys.path:
            sys.path.append(entry)


def _real(path: str) -> str:
    return os.path.realpath(path)


def _real_normcase(path: str) -> str:
    return os.path.normcase(_real(path))


def both_spellings(path: str) -> tuple[str, str]:
    """(junction_spelling, physical_spelling) of `path`'s resolved location, as
    two absolute Windows paths (CONSTRAINTS O13). A path outside the RHACO tree
    entirely has nothing to dual-spell and both entries come back identical."""
    real = _real(path)
    try:
        rel = os.path.relpath(real, RHACO_PHYSICAL)
    except ValueError:
        return real, real  # different drive -- cannot be expressed relative to RHACO_PHYSICAL
    if rel == os.curdir:
        return RHACO_JUNCTION, real
    if rel.startswith(os.pardir):
        return real, real  # not under the RHACO tree
    junction = os.path.normpath(os.path.join(RHACO_JUNCTION, rel))
    return junction, real


def is_under_docs_root(path: str, docs_root: str) -> bool:
    """True iff `path` resolves at or under `docs_root` -- accepts either RHACO
    tree spelling (O13) and rejects any `..` escape (O1), because realpath
    resolves both before the string comparison ever runs (decision A10)."""
    try:
        real_path = _real_normcase(path)
        real_root = _real_normcase(docs_root)
    except (OSError, ValueError):
        return False
    return real_path == real_root or real_path.startswith(real_root + os.sep)


def rel_ref_from_abs_path(abs_path: str, docs_root: str) -> str:
    """Relative POSIX path of `abs_path` under `docs_root` -- the stable URL key
    for a card (`card_ref`, decision A5) or a document (`doc_ref`). Junction-
    spelling-independent: both `abs_path` and `docs_root` are resolved with
    `realpath` before the relative path is computed."""
    real = _real(abs_path)
    root = _real(docs_root)
    rel = os.path.relpath(real, root)
    return rel.replace(os.sep, "/")


def abs_path_from_rel_ref(rel_ref: str, docs_root: str) -> str:
    """Inverse of `rel_ref_from_abs_path`: an absolute path in `docs_root`'s own
    spelling. Rejects an absolute-looking or `..`-escaping ref before ever
    touching the filesystem; callers must still confirm the result with
    `is_under_docs_root` (defense in depth -- this function alone cannot see a
    symlink introduced after the string check)."""
    if not rel_ref or rel_ref.startswith(("/", "\\")) or ":" in rel_ref:
        raise ValueError(f"invalid reference path: {rel_ref!r}")
    parts = rel_ref.split("/")
    if any(p in ("", ".", "..") or "\\" in p for p in parts):
        raise ValueError(f"invalid reference path: {rel_ref!r}")
    return os.path.normpath(os.path.join(docs_root, *parts))


# ARCHITECTURE.md 4.1 names these two specifically for the card <-> card_ref
# round trip; they are the general functions above under the names the
# contract uses.
card_ref_from_yaml_path = rel_ref_from_abs_path
yaml_path_from_card_ref = abs_path_from_rel_ref
