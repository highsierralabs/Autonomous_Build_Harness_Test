"""L1 static checks: the index-write prohibition, and the import boundary.

CHECK 1 -- index-write prohibition (CONSTRAINTS.md O2; DISPATCH_PARAMETERS.md
item C as amended by Amendment A1 section A1.5).
  Grep the workspace for the five index-writing function names of
  RHACO_corpus_index and pass only when every hit lies in the single allowlisted
  file, fixtures/build_fixture_index.py. Any hit elsewhere is a defect recorded
  per round in build_state.json (by the orchestrator).

CHECK 2 -- import boundary (sealed audit SA-4; Director ruling 2026-09-05).
  SA-4's finding was that L1 established only the five-name grep while being
  READ as establishing more -- in particular the "sole RHACO importer" invariant
  that SA-3 then found false in the merged tree. A prose invariant checked by
  nothing is the class this check closes.

  The invariant is stated as an ENUMERATION WITHIN A DECLARED SCOPE, because
  that is the only form a static check can assert. In the PRODUCT TREE
  (explorer/** + fixtures/**) exactly three files may import RHACO_corpus_index
  or RHACO_tool_catalog_librarian, each licensed by an orchestrator dispatch and
  named in ARCHITECTURE.md 4.1:

      explorer/corpus_adapter/adapter.py    both        the adapter itself
      explorer/diagnostics/service.py       index only  O17, a constant read
      fixtures/build_fixture_index.py       both        O3, the fixture builder

  A fourth importer in the product tree is a defect.

  Instruments live outside the product tree and outside the invariant, and are
  licensed at two DIFFERENT GRANULARITIES on purpose (Director ruling
  2026-09-05, which narrowed a wider proposal this build had made):

      preflight/                  BY PATH   hand section 0 items 12/13
      tests/                      BY PATH   test code
      tools/l4_gold_oracle.py     BY FILE   AC-4 design: the oracle must call
                                            the module directly, because
                                            comparing the adapter against the
                                            module IS the measurement

  tools/ is deliberately NOT licensed as a directory. tools/probe_corpus_explorer.py
  lives there, and the probe is barred from importing either module and from
  opening the database at all -- it drives the product through a browser and
  compares against fixture sources on disk. A directory-level allowlist on tools/
  would make a probe that began importing the module invisible to this check,
  which is precisely the SA-4 failure mode repeated one level up.

  Both static imports and importlib/__import__ of the two modules are matched.
  A licensed importer that no longer imports is reported as an unused licence --
  informational, not a defect: it means ARCHITECTURE 4.1's enumeration has drifted
  the other way and should be re-derived.

SCOPE
  Every file under the workspace root except: .git/, .venv/, .worktrees/, docs/
  (evidence and reports), CONSTRAINTS.md (names the functions by design), the
  three pinned instruments PROMPT.md / RATIONALE.md / DISPATCH_PARAMETERS.md
  (hand text, not build code), and the cache dirs. Check 2 reads .py files only.
  Every name this file searches for is assembled at runtime, so the file never
  matches itself.

USAGE
  python tools/l1_index_write_check.py [--root PATH] [--json]
  exit 0 = both checks pass; exit 1 = a defect in either; exit 2 = error.

OUTPUT
  ASCII only. One line per hit, then one summary line per check.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

# Assembled at runtime, like NAME_PARTS below, so this file never matches itself.
MODULE_PARTS = (
    ("RHACO", "corpus", "index"),
    ("RHACO", "tool", "catalog", "librarian"),
)
MODULES = tuple("_".join(p) for p in MODULE_PARTS)

# ARCHITECTURE.md 4.1: the product tree, and the three files licensed to import
# inside it. A fourth is a defect.
PRODUCT_TREE_PREFIXES = ("explorer/", "fixtures/")
LICENSED_PRODUCT_IMPORTERS = (
    "explorer/corpus_adapter/adapter.py",
    "explorer/diagnostics/service.py",
    "fixtures/build_fixture_index.py",
)

# Instruments, outside the product tree and outside the invariant. Two
# granularities, deliberately (Director ruling 2026-09-05): tools/ is NOT a
# licensed directory -- see the module docstring, CHECK 2.
INSTRUMENT_PATH_PREFIXES = ("preflight/", "tests/")
INSTRUMENT_FILES = ("tools/l4_gold_oracle.py",)

_IMPORT_RE = re.compile(
    r"^\s*(?:import|from)\s+(" + "|".join(re.escape(m) for m in MODULES) + r")\b"
)
_DYNAMIC_RE = re.compile(r"(?:import_module|__import__)\s*\(")

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


def _classify(rel: str) -> tuple[bool, str]:
    """(licensed, class) for a file that imports one of the two RHACO modules."""
    if rel.startswith(PRODUCT_TREE_PREFIXES):
        if rel in LICENSED_PRODUCT_IMPORTERS:
            return True, "product-tree (licensed, ARCHITECTURE 4.1)"
        return False, "product-tree (UNLICENSED -- a fourth importer)"
    if rel.startswith(INSTRUMENT_PATH_PREFIXES):
        return True, "instrument (licensed by path)"
    if rel in INSTRUMENT_FILES:
        return True, "instrument (licensed by file)"
    return False, "outside every licensed scope"


def scan_imports(root: str) -> list[dict]:
    """CHECK 2: every .py file that imports either RHACO module, classified."""
    hits: list[dict] = []
    root = os.path.abspath(root)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), root).replace(os.sep, "/")
            try:
                with open(os.path.join(dirpath, fn), encoding="utf-8", errors="replace") as fh:
                    for ln, line in enumerate(fh, 1):
                        m = _IMPORT_RE.match(line)
                        kind = None
                        if m:
                            module, kind = m.group(1), "static"
                        elif _DYNAMIC_RE.search(line) and any(mod in line for mod in MODULES):
                            module = next(mod for mod in MODULES if mod in line)
                            kind = "dynamic"
                        if kind is None:
                            continue
                        licensed, klass = _classify(rel)
                        hits.append({"path": rel, "line": ln, "module": module, "kind": kind,
                                     "text": line.rstrip("\r\n")[:160],
                                     "licensed": licensed, "class": klass})
            except OSError as exc:
                hits.append({"path": rel, "line": 0, "module": "<read-error>", "kind": "error",
                             "text": str(exc), "licensed": False, "class": "read error"})
    return hits


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--json", action="store_true", help="print a JSON summary instead of text")
    args = ap.parse_args(argv)
    hits = scan(args.root)
    defects = [h for h in hits if not h["allowlisted"]]

    imports = scan_imports(args.root)
    import_defects = [h for h in imports if not h["licensed"]]
    importer_files = {h["path"] for h in imports}
    unused_licences = [p for p in LICENSED_PRODUCT_IMPORTERS if p not in importer_files]

    summary = {
        "root": args.root,
        "index_write": {"names": list(NAMES), "hits": len(hits),
                        "allowlisted_hits": len(hits) - len(defects), "defects": len(defects),
                        "defect_list": defects, "verdict": "PASS" if not defects else "FAIL"},
        "import_boundary": {"modules": list(MODULES), "hits": len(imports),
                            "licensed_hits": len(imports) - len(import_defects),
                            "defects": len(import_defects), "defect_list": import_defects,
                            "product_tree_importers": sorted(
                                p for p in importer_files if p.startswith(PRODUCT_TREE_PREFIXES)),
                            "unused_licences": unused_licences,
                            "verdict": "PASS" if not import_defects else "FAIL"},
    }
    summary["verdict"] = "PASS" if not (defects or import_defects) else "FAIL"

    if args.json:
        print(json.dumps(summary, ensure_ascii=True))
    else:
        for h in hits:
            tag = "allowlisted" if h["allowlisted"] else "DEFECT"
            print(f"{tag}: {h['path']}:{h['line']}: [{h['name']}] {h['text']}".encode("ascii", "replace").decode("ascii"))
        print(f"l1-index-write-check: hits={len(hits)} allowlisted={len(hits) - len(defects)} defects={len(defects)} verdict={summary['index_write']['verdict']}")
        for h in imports:
            tag = "licensed" if h["licensed"] else "DEFECT"
            print(f"{tag}: {h['path']}:{h['line']}: [{h['module']}, {h['kind']}] {h['class']}".encode("ascii", "replace").decode("ascii"))
        for p in unused_licences:
            print(f"note: licensed product-tree importer no longer imports: {p} (ARCHITECTURE 4.1 enumeration has drifted; re-derive it)")
        print(f"l1-import-boundary: hits={len(imports)} licensed={len(imports) - len(import_defects)} defects={len(import_defects)} unused_licences={len(unused_licences)} verdict={summary['import_boundary']['verdict']}")
    return 0 if not (defects or import_defects) else 1


if __name__ == "__main__":
    sys.exit(main())
