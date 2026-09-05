"""Integration test for the L1 import-boundary check (integrator-owned; sealed
audit SA-4; Director ruling 2026-09-05).

SA-4's finding was that L1 established only the five-name grep while being READ
as establishing more -- and SA-3 was exactly the invariant it did not check. The
repair adds an import-boundary check to `tools/l1_index_write_check.py`.

This test exists because a check that has never been observed to fail is the same
pathology the round-6 work exists to end: critic round 1 named three instances of
it (W5's direction_label assertion, W3's regression pin, string-matched keyboard
handling), and the sealed audit named a fourth. So this file does not merely
assert that the boundary check passes on the real tree -- it BUILDS violations in
a temporary tree and asserts the check reports each one, which is the only
evidence that a green run means anything.

Static: it runs the checker over synthetic directory trees. It imports nothing
from RHACO and touches neither the live index nor the real workspace.
"""
from __future__ import annotations

import importlib.util
import os
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHECKER = os.path.join(REPO_ROOT, "tools", "l1_index_write_check.py")

# The two module names, assembled so this test file is not itself a hit if the
# checker is ever pointed at the real tests/ directory with a stricter licence.
_INDEX_MODULE = "_".join(("RHACO", "corpus", "index"))
_LIBRARIAN_MODULE = "_".join(("RHACO", "tool", "catalog", "librarian"))


@pytest.fixture(scope="module")
def checker():
    spec = importlib.util.spec_from_file_location("l1_index_write_check", CHECKER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["l1_index_write_check"] = mod
    spec.loader.exec_module(mod)
    return mod


def _write(root, rel, text):
    path = os.path.join(root, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def _tree(root):
    """The licensed baseline: exactly the three product-tree importers plus the
    three instrument forms ARCHITECTURE 4.1 names."""
    _write(root, "explorer/corpus_adapter/adapter.py", f"import {_INDEX_MODULE}\nimport {_LIBRARIAN_MODULE}\n")
    _write(root, "explorer/diagnostics/service.py", f"import {_INDEX_MODULE}\n")
    _write(root, "fixtures/build_fixture_index.py", f"import {_INDEX_MODULE}\n")
    _write(root, "preflight/item12_import.py", f"import {_INDEX_MODULE}\n")
    _write(root, "tests/probe/test_fixture_builder.py", f"import {_INDEX_MODULE}\n")
    _write(root, "tools/l4_gold_oracle.py", f"import {_INDEX_MODULE}\n")
    # Present, and must stay invisible to the check: it imports nothing.
    _write(root, "tools/probe_corpus_explorer.py", "import json\n")
    _write(root, "explorer/search/service.py", "import sqlite3\n")


def _defect_paths(mod, root):
    return sorted({h["path"] for h in mod.scan_imports(root) if not h["licensed"]})


def test_licensed_baseline_is_clean(checker, tmp_path):
    root = str(tmp_path)
    _tree(root)
    hits = checker.scan_imports(root)
    assert _defect_paths(checker, root) == []
    assert len(hits) == 7
    product = sorted({h["path"] for h in hits if h["path"].startswith(checker.PRODUCT_TREE_PREFIXES)})
    assert product == sorted(checker.LICENSED_PRODUCT_IMPORTERS)


def test_a_fourth_product_tree_importer_is_a_defect(checker, tmp_path):
    """The SA-3 case: a new importer inside explorer/** that no dispatch licensed."""
    root = str(tmp_path)
    _tree(root)
    _write(root, "explorer/search/service.py", f"import sqlite3\nimport {_INDEX_MODULE}\n")
    assert _defect_paths(checker, root) == ["explorer/search/service.py"]


def test_a_tools_importer_that_is_not_the_gold_oracle_is_a_defect(checker, tmp_path):
    """The reason tools/ is licensed BY FILE and not BY PATH (Director ruling
    2026-09-05). The probe is barred from importing the module at all; a
    directory-level allowlist on tools/ would hide exactly this."""
    root = str(tmp_path)
    _tree(root)
    _write(root, "tools/probe_corpus_explorer.py", f"import json\nimport {_INDEX_MODULE}\n")
    assert _defect_paths(checker, root) == ["tools/probe_corpus_explorer.py"]


def test_an_importer_outside_every_licensed_scope_is_a_defect(checker, tmp_path):
    root = str(tmp_path)
    _tree(root)
    _write(root, "scratch/helper.py", f"import {_INDEX_MODULE}\n")
    assert _defect_paths(checker, root) == ["scratch/helper.py"]


def test_a_dynamic_import_is_caught_too(checker, tmp_path):
    """A static-import grep that importlib walks around would be a check narrower
    than its apparent guarantee -- the SA-4 class itself."""
    root = str(tmp_path)
    _tree(root)
    _write(root, "explorer/catalog/service.py",
           f'import importlib\nmod = importlib.import_module("{_INDEX_MODULE}")\n')
    assert _defect_paths(checker, root) == ["explorer/catalog/service.py"]


def test_a_licensed_importer_that_stops_importing_is_reported_but_not_a_defect(checker, tmp_path):
    """Drift the other way: the enumeration is exact, so a licence nobody uses
    means ARCHITECTURE 4.1 should be re-derived. Informational, not a failure."""
    root = str(tmp_path)
    _tree(root)
    _write(root, "explorer/diagnostics/service.py", "import os\n")
    hits = checker.scan_imports(root)
    importer_files = {h["path"] for h in hits}
    unused = [p for p in checker.LICENSED_PRODUCT_IMPORTERS if p not in importer_files]
    assert unused == ["explorer/diagnostics/service.py"]
    assert _defect_paths(checker, root) == []


def test_the_real_workspace_passes_both_checks(checker):
    """The live assertion. Kept last so the synthetic cases above have already
    established that a failure is reachable."""
    assert _defect_paths(checker, REPO_ROOT) == []
    write_defects = [h for h in checker.scan(REPO_ROOT) if not h["allowlisted"]]
    assert write_defects == []
