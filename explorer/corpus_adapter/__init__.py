"""explorer.corpus_adapter -- the read-only adapter over RHACO_corpus_index and
RHACO_tool_catalog_librarian (ARCHITECTURE.md 4.1, section 2).

`adapter.py` is the RETRIEVAL importer of those two modules, and one of exactly
three licensed importers in the product tree (`explorer/**` + `fixtures/**`):

  - `explorer/corpus_adapter/adapter.py`   -- this package; all retrieval
  - `explorer/diagnostics/service.py`      -- O17; import only, reads the
                                              RERANK_MODEL_DIR constant, no calls
  - `fixtures/build_fixture_index.py`      -- O3; builds the fixture index through
                                              the module's own writer functions

A fourth importer under those roots is a defect. Instrument importers under
`preflight/`, `tests/` and `tools/` are outside the product tree and outside this
invariant. The earlier wording -- "the only file in the workspace that imports
either module" -- was false in the merged tree and is corrected here (sealed audit
SA-3); `tools/l1_index_write_check.py` asserts the enumeration mechanically.
"""
from __future__ import annotations

from explorer.corpus_adapter.adapter import ConfigurationError, CorpusAdapter

__all__ = ["ConfigurationError", "CorpusAdapter"]
