"""explorer.corpus_adapter -- the read-only adapter over RHACO_corpus_index and
RHACO_tool_catalog_librarian (ARCHITECTURE.md 4.1, section 2). `adapter.py` is
the only file in the workspace that imports either module.
"""
from __future__ import annotations

from explorer.corpus_adapter.adapter import ConfigurationError, CorpusAdapter

__all__ = ["ConfigurationError", "CorpusAdapter"]
