"""L1 static check: the index-write prohibition (CONSTRAINTS.md O2; DISPATCH_PARAMETERS.md
item C as amended by Amendment A1 section A1.5).

PURPOSE
  Grep the workspace for the five index-writing function names of
  RHACO_corpus_index and pass only when every hit lies in the single allowlisted
  file, fixtures/build_fixture_index.py. Any hit elsewhere is a defect recorded
  per round in build_state.json (by the orchestrator).

SCOPE
  Every file under the workspace root except: .git/, .venv/, docs/ (evidence and
  reports), CONSTRAINTS.md (names the functions by design), the three pinned
  instruments PROMPT.md / RATIONALE.md / DISPATCH_PARAMETERS.md (hand text, not
  build code -- recorded interpretation, see docs/rounds), and __pycache__.
  The names are assembled at runtime so this file never matches itself.

USAGE
  python tools/l1_index_write_check.py [--root PATH] [--json]
  exit 0 = pass (no hit outside the allowlist); exit 1 = defect; exit 2 = error.

OUTPUT
  ASCII only. One line per hit: path:line: <text>. Summary line last.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

NAME_PARTS = (
    ("reindex", "full"),
    ("reindex", "pair"),
    ("reindex", "fts", "pair"),
    ("reindex", "vec"),
    ("emit", "gold", "queries"),
)
NAMES = tuple("_".join(p) for p in NAME_PARTS)
ALLOWLIST = ("fixtures/build_fixture_index.py",)
EXCLUDE_DIRS = {".git", ".venv", ".worktrees", "docs", "__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache"}
# .worktrees/ holds builder checkouts (ARCHITECTURE.md A15): each builder runs this check at its own
# worktree root, and merged content is re-checked on main; scanning them from main would report the
# allowlisted fixture script at a non-allowlisted relative path.
EXCLUDE_FILES = {"CONSTRAINTS.md", "PROMPT.md", "RATIONALE.md", "DISPATCH_PARAMETERS.md"}
BINARY_SUFFIXES = {".db", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".pyc", ".woff", ".woff2", ".ico"}


def scan(root: str) -> list[dict]:
    hits: list[dict] = []
    root = os.path.abspath(root)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            rel = os.path.relpath(os.path.join(dirpath, fn), root).replace(os.sep, "/")
            if rel in EXCLUDE_FILES or os.path.splitext(fn)[1].lower() in BINARY_SUFFIXES:
                continue
            full = os.path.join(dirpath, fn)
            try:
                with open(full, encoding="utf-8", errors="replace") as fh:
                    for ln, line in enumerate(fh, 1):
                        for name in NAMES:
                            if name in line:
                                hits.append({"path": rel, "line": ln, "name": name,
                                             "text": line.rstrip("\r\n")[:160],
                                             "allowlisted": rel in ALLOWLIST})
            except OSError as exc:
                hits.append({"path": rel, "line": 0, "name": "<read-error>", "text": str(exc), "allowlisted": False})
    return hits


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--json", action="store_true", help="print a JSON summary instead of text")
    args = ap.parse_args(argv)
    hits = scan(args.root)
    defects = [h for h in hits if not h["allowlisted"]]
    summary = {"root": args.root, "names": list(NAMES), "hits": len(hits),
               "allowlisted_hits": len(hits) - len(defects), "defects": len(defects),
               "defect_list": defects, "verdict": "PASS" if not defects else "FAIL"}
    if args.json:
        print(json.dumps(summary, ensure_ascii=True))
    else:
        for h in hits:
            tag = "allowlisted" if h["allowlisted"] else "DEFECT"
            print(f"{tag}: {h['path']}:{h['line']}: [{h['name']}] {h['text']}".encode("ascii", "replace").decode("ascii"))
        print(f"l1-index-write-check: hits={len(hits)} allowlisted={len(hits) - len(defects)} defects={len(defects)} verdict={summary['verdict']}")
    return 0 if not defects else 1


if __name__ == "__main__":
    sys.exit(main())
