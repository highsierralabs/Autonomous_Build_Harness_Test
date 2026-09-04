"""Build the RHACO Corpus Explorer probe fixture index (builder probe; ARCHITECTURE.md
section 2 table, item 4.8; CONSTRAINTS.md O2/O3; A12).

PURPOSE
  The ONLY file in this workspace allowed to name RHACO_corpus_index's five
  index-writing functions (CONSTRAINTS.md O2; tools/l1_index_write_check.py
  enforces this every round). Builds a small SQLite index over the synthetic
  fixture corpus at fixtures/corpus/ by calling RHACO_corpus_index.reindex_full
  through the module's own public API -- never hand-written SQL, never a copy
  of the module. Deterministic given the fixture files on disk.

  Safety: before any read or write, the resolved db path is asserted to be
  neither RHACO_corpus_index.DEFAULT_DB nor a path under either spelling of
  the RHACO tree (C:\\RHACO, C:\\highsierralabs\\RHACO -- the junction and its
  physical target are the SAME tree, O13). A path that fails this check raises
  ValueError (CLI: prints "REFUSED: ..." and exits 2) BEFORE the librarian scan
  runs and BEFORE RHACO_corpus_index.connect() is ever called -- the live index
  can never be reached from this file, by construction, not by convention.

USAGE
  python fixtures/build_fixture_index.py --docs-root fixtures/corpus --db fixtures/fixture_index.db [--force]
  from fixtures.build_fixture_index import build
  build("fixtures/corpus", "fixtures/fixture_index.db")   # -> summary dict

OUTPUT
  A SQLite file at --db (gitignored, fixtures/*.db; never committed) plus an
  ASCII summary on stdout (cards, fts_docs, edges, id_aliases, db path). No
  vector set is built (reindex_vec is never called: there is no local Ollama
  dependency for the fixture) -- RHACO_corpus_index.search_hybrid against this
  db degrades to identifier short-circuit + FTS5 lexical ordering, a known and
  documented fixture state (ARCHITECTURE.md A12), not a defect.

VERSION HISTORY
  v1.0  2026-09-04  Initial build (RHACO-HND-20260903-001 strand B2, round 1).
"""
from __future__ import annotations

import argparse
import logging
import os
import sys

# --- make `explorer` importable regardless of how this file is invoked -----
# (`python fixtures/build_fixture_index.py` sets sys.path[0] to fixtures/, not
# the workspace root; `python -m pytest` from the worktree root already has
# the root on sys.path, so this insert is idempotent in that case).
_WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, _WORKSPACE_ROOT)

from explorer.config import RHACO_PATH_ENTRIES, RHACO_TREES  # noqa: E402

for _entry in RHACO_PATH_ENTRIES:
    if _entry not in sys.path:
        sys.path.insert(0, _entry)

import RHACO_corpus_index  # noqa: E402
import RHACO_tool_catalog_librarian  # noqa: E402

_FIXTURE_LOGGER_NAME = "rhaco_corpus_explorer.fixture_build"


def _null_logger() -> logging.Logger:
    """A logger that swallows every record -- the librarian scan's findings are
    not this script's concern (the fixture is deliberately hand-crafted; its
    findings, if any, are inspected via scan.orphan_cards / .missing_cards /
    .broken_yamls in the returned summary, not via log output)."""
    log = logging.getLogger(_FIXTURE_LOGGER_NAME)
    log.handlers.clear()
    log.addHandler(logging.NullHandler())
    log.propagate = False
    log.setLevel(logging.CRITICAL)
    return log


def _resolve_and_assert_fixture_db_path(db_path: str) -> str:
    """Resolve db_path and refuse (raise ValueError) if it is the module's own
    DEFAULT_DB or lies under either spelling of the RHACO tree. Runs BEFORE any
    other step in build() -- no scan, no connect(), no write happens first."""
    resolved = os.path.realpath(db_path)
    resolved_n = os.path.normcase(resolved)

    default_n = os.path.normcase(os.path.realpath(RHACO_corpus_index.DEFAULT_DB))
    if resolved_n == default_n:
        raise ValueError(
            f"refusing to touch the live default index db (RHACO_corpus_index.DEFAULT_DB): {resolved}"
        )

    for tree in RHACO_TREES:
        tree_n = os.path.normcase(os.path.realpath(tree))
        if resolved_n == tree_n or resolved_n.startswith(tree_n + os.sep):
            raise ValueError(
                f"refusing to write a fixture index under a RHACO tree ({tree}): {resolved}"
            )

    return resolved


def build(docs_root: str, db_path: str, force: bool = False) -> dict:
    """Build a fixture RHACO_corpus_index.db from the synthetic docs tree at
    docs_root. Order of operations (ARCHITECTURE.md section 4.8; CONSTRAINTS.md
    O3):

      1. Resolve db_path and assert it is safe -- BEFORE any read or write
         (_resolve_and_assert_fixture_db_path; raises ValueError on failure).
      2. Resolve docs_root and confirm it exists.
      3. Run the librarian's own read-only scan (scan_library) over docs_root.
         output_path="" so _read_prior_version_history reads nothing (no prior
         catalog file exists or is touched); a NullHandler logger discards
         every finding the scan emits. This step writes nothing to disk.
      4. Monkeypatch RHACO_corpus_index.BODY_SCAN_ROOT to docs_root IN-PROCESS
         ONLY (never written to the module's source file -- BLOCKED per
         PROMPT.md section 11) because reindex_full's fts_docs pass calls
         iter_body_docs() with no root argument, and iter_body_docs reads the
         BODY_SCAN_ROOT module constant at call time (not at def time), so
         this is the only way to point the body scan at the fixture tree. The
         prior value is restored in a finally block even on exception.
      5. Call RHACO_corpus_index.reindex_full(scan, db_path=resolved_db) --
         the only index-writing call in this file, and only ever reached after
         step 1 has proven db_path is outside every RHACO tree.

    Returns a summary dict (also printed to stdout as ASCII)."""
    resolved_db = _resolve_and_assert_fixture_db_path(db_path)

    if force and os.path.exists(resolved_db):
        os.remove(resolved_db)
        journal = resolved_db + "-journal"
        if os.path.exists(journal):
            os.remove(journal)

    resolved_docs_root = os.path.realpath(docs_root)
    if not os.path.isdir(resolved_docs_root):
        raise ValueError(f"docs root does not exist or is not a directory: {resolved_docs_root}")

    log = _null_logger()
    scan = RHACO_tool_catalog_librarian.scan_library(resolved_docs_root, "", log)

    prior_root = RHACO_corpus_index.BODY_SCAN_ROOT
    RHACO_corpus_index.BODY_SCAN_ROOT = resolved_docs_root
    try:
        report = RHACO_corpus_index.reindex_full(scan, db_path=resolved_db)
    finally:
        RHACO_corpus_index.BODY_SCAN_ROOT = prior_root

    conn = RHACO_corpus_index.connect(resolved_db)
    try:
        edges_unresolved = conn.execute("SELECT count(*) FROM edges WHERE resolved=0").fetchone()[0]
    finally:
        conn.close()

    summary = {
        "db_path": resolved_db,
        "docs_root": resolved_docs_root,
        "cards": report.cards_written,
        "fts_docs": report.fts_docs_written,
        "edges": report.edges_written,
        "edges_unresolved": edges_unresolved,
        "id_aliases": report.aliases_written,
        "programs_written": report.programs_written,
        "tags_written": report.tags_written,
        "corpus_cards_sha": report.corpus_cards_sha,
        "elapsed_s": report.elapsed_s,
        "orphan_cards": len(scan.orphan_cards),
        "missing_cards": len(scan.missing_cards),
        "broken_yamls": len(scan.broken_yamls),
    }
    _print_summary(summary)
    return summary


def _print_summary(summary: dict) -> None:
    print("RHACO Corpus Explorer -- fixture index build summary")
    print(f"  db_path          = {summary['db_path']}")
    print(f"  docs_root        = {summary['docs_root']}")
    print(f"  cards            = {summary['cards']}")
    print(f"  fts_docs         = {summary['fts_docs']}")
    print(f"  edges            = {summary['edges']}")
    print(f"  edges_unresolved = {summary['edges_unresolved']}")
    print(f"  id_aliases       = {summary['id_aliases']}")
    print(f"  orphan_cards     = {summary['orphan_cards']}")
    print(f"  missing_cards    = {summary['missing_cards']}")
    print(f"  broken_yamls     = {summary['broken_yamls']}")
    print(f"  elapsed_s        = {summary['elapsed_s']:.4f}")
    print("NOTE: no vector set is built (reindex_vec is never called -- there is no")
    print("      local Ollama dependency in this fixture); search_hybrid against this")
    print("      db degrades to identifier short-circuit + FTS5 lexical ordering. This")
    print("      is a documented known fixture state (ARCHITECTURE.md A12), not a defect.")


def main(argv: list[str] | None = None) -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description="Build the RHACO Corpus Explorer probe fixture index.")
    ap.add_argument("--docs-root", default=os.path.join(here, "corpus"),
                     help="fixture docs root (default: fixtures/corpus)")
    ap.add_argument("--db", default=os.path.join(here, "fixture_index.db"),
                     help="fixture db path (default: fixtures/fixture_index.db)")
    ap.add_argument("--force", action="store_true",
                     help="delete an existing fixture db (and its journal) before building")
    args = ap.parse_args(argv)
    try:
        build(args.docs_root, args.db, force=args.force)
    except ValueError as exc:
        print(f"REFUSED: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
