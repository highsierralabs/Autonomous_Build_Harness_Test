"""HND-20260903-001 section 0 item 12 -- RHACO import path from the workspace venv.

Read-only. Imports the two sanctioned RHACO modules via path entries (never a
package import) and reports the constants the fixture strategy depends on.
Exit 0 iff both imports succeed and DEFAULT_DB equals the expected live path.
"""
import sys

sys.path.insert(0, r"C:\RHACO\rhaco")
sys.path.insert(1, r"C:\RHACO\tools")

print("python:", sys.version.split()[0], sys.executable)
import RHACO_corpus_index as ci  # noqa: E402
import RHACO_tool_catalog_librarian as lib  # noqa: E402

EXPECTED_DB = r"C:\RHACO\index\corpus_index.db"
print("RHACO_corpus_index.__file__ =", ci.__file__)
print("RHACO_tool_catalog_librarian.__file__ =", lib.__file__,
      "| LIBRARIAN_VERSION =", lib.LIBRARIAN_VERSION)
print("DEFAULT_DB =", ci.DEFAULT_DB, "| equals expected:", ci.DEFAULT_DB == EXPECTED_DB)
print("BODY_SCAN_ROOT =", ci.BODY_SCAN_ROOT)
print("INDEX_SCHEMA_VERSION =", ci.INDEX_SCHEMA_VERSION,
      "| CPU_FLOOR_TAG =", ci.CPU_FLOOR_TAG, "| MODEL_TAGS =", ci.MODEL_TAGS)
print("VEC_DISABLE_ENV =", ci.VEC_DISABLE_ENV, "| RERANK_DISABLE_ENV =", ci.RERANK_DISABLE_ENV,
      "| OLLAMA_HOST =", ci.OLLAMA_HOST, "| OLLAMA_TIMEOUT_S =", ci.OLLAMA_TIMEOUT_S)
print("RRF_K =", ci.RRF_K, "| RERANK_DEPTH =", ci.RERANK_DEPTH, "| MAX_SEARCH_RESULTS =", ci.MAX_SEARCH_RESULTS)
print("librarian DEFAULT_ROOT =", lib.DEFAULT_ROOT, "| DENY_DIRS =", sorted(lib.DENY_DIRS))
import sqlite3  # noqa: E402
import sqlite_vec  # noqa: E402
import yaml  # noqa: E402
print("sqlite_vec:", getattr(sqlite_vec, "__version__", "present"),
      "| yaml:", yaml.__version__, "| sqlite3 library:", sqlite3.sqlite_version)
print("sys.path[0:2] =", sys.path[0:2])
ok = ci.DEFAULT_DB == EXPECTED_DB
print("ITEM12_IMPORTS_OK" if ok else "ITEM12_DEFAULT_DB_MISMATCH")
sys.exit(0 if ok else 1)
