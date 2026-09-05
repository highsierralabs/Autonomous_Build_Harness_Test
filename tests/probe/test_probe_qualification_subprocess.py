"""Subprocess test for the qualification path (task C1 item 5; item 4(ii)'s scenario).

Runs the probe as a subprocess -- the probe is the ONLY sanctioned launcher of the
explorer server (CONSTRAINTS.md O12) -- against a tmp-built fixture db, with
`--preset diagnostics --fault console_error --ledger <tmp path>`, and asserts the
run_summary fields item 4(ii) specifies, exit code 0, and that the *tmp* ledger (never
the committed one) records KB5. Free of the five index-writing names.
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
from pathlib import Path

import pytest

from fixtures.build_fixture_index import build

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_ROOT = REPO_ROOT / "fixtures" / "corpus"
PROBE_SCRIPT = REPO_ROOT / "tools" / "probe_corpus_explorer.py"
COMMITTED_LEDGER = REPO_ROOT / "docs" / "probe-qualification" / "qualification_ledger.json"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def fixture_db(tmp_path_factory) -> Path:
    tmp_path = tmp_path_factory.mktemp("probe_qual_index")
    db_path = tmp_path / "fixture_index.db"
    build(str(DOCS_ROOT), str(db_path))
    return db_path


def test_probe_diagnostics_console_error_fault_subprocess(fixture_db, tmp_path):
    out_dir = tmp_path / "probe_out"
    ledger_path = tmp_path / "qualification_ledger.json"
    committed_ledger_before = (
        COMMITTED_LEDGER.read_bytes() if COMMITTED_LEDGER.is_file() else None
    )
    port = _free_port()
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    cmd = [
        sys.executable, str(PROBE_SCRIPT),
        "--db", str(fixture_db),
        "--docs-root", str(DOCS_ROOT),
        "--preset", "diagnostics",
        "--fault", "console_error",
        "--port", str(port),
        "--out", str(out_dir),
        "--ledger", str(ledger_path),
        "--timeout", "30",
    ]
    result = subprocess.run(
        cmd, cwd=str(REPO_ROOT), env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=90,
    )

    assert result.returncode == 0, (
        f"probe exited {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )

    summary_path = out_dir / "run_summary.json"
    assert summary_path.is_file(), f"run_summary.json missing; stdout:\n{result.stdout}"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    assert summary["run_kind"] == "qualification"
    assert summary["qualification_state"] == "QUALIFICATION_PASS"
    assert summary["qualified_failure_classes"] == ["KB5"]
    assert summary["product_evidence_eligible"] is False
    assert summary["verdict"] == "PASS"
    assert summary["run_error"] is None
    assert summary["ledger_path"] == str(ledger_path)

    diag = summary["results"]["diagnostics"]
    assert diag["verdict"] == "FAIL"
    assert diag["fault_detected"] is True
    assert diag["fault_class"] == "KB5"

    diagnostics_obs = json.loads((out_dir / "diagnostics.json").read_text(encoding="utf-8"))
    assert diagnostics_obs["verdict"] == "FAIL"
    assert diagnostics_obs["fault_detected"] is True
    assert diagnostics_obs["fault_class"] == "KB5"
    assert diagnostics_obs["ok"] is False

    # The tmp ledger records KB5 ...
    assert ledger_path.is_file()
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert "KB5" in ledger["classes"]
    assert ledger["classes"]["KB5"]["run"]
    assert any(run["classes"] == ["KB5"] for run in ledger["runs"])

    # ... and the committed ledger is untouched by this test.
    committed_ledger_after = (
        COMMITTED_LEDGER.read_bytes() if COMMITTED_LEDGER.is_file() else None
    )
    assert committed_ledger_after == committed_ledger_before
