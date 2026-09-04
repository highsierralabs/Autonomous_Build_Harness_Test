"""Fixture-only fault injection (integrator-owned). ARCHITECTURE.md A13; PROMPT.md section 2.

A fault is honoured only when BOTH hold: the request names a known fault, and the
resolved db path lies outside both RHACO trees (so a fault can never act on the
live index). Anything else resolves to None and the request is logged as ignored.
"""
from __future__ import annotations

import logging
import os

from explorer.config import RHACO_TREES

FAULTS = (
    "wrong_doc_for_id",   # identifier resolution returns the neighbouring fixture card
    "stale_card",         # card panel served from a mutated copy of the card
    "reverse_edges",      # from/to swapped in the lineage view
    "broken_jump",        # reader line anchor off by 50 lines
    "console_error",      # a template emits a JavaScript throw
)

_log = logging.getLogger("explorer.faults")


def _real(p: str) -> str:
    return os.path.normcase(os.path.realpath(p))


def is_under_rhaco_tree(path: str) -> bool:
    rp = _real(path)
    for tree in RHACO_TREES:
        rt = _real(tree)
        if rp == rt or rp.startswith(rt + os.sep):
            return True
    return False


def active_fault(requested: str | None, resolved_db_path: str) -> str | None:
    """Return the fault to apply, or None. Live-index requests are always refused."""
    if not requested:
        return None
    if requested not in FAULTS:
        _log.warning("fault request ignored: unknown fault %r", requested)
        return None
    if is_under_rhaco_tree(resolved_db_path):
        _log.warning("fault request ignored: db path is inside a RHACO tree (%s)", resolved_db_path)
        return None
    return requested
