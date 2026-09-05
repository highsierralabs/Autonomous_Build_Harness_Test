"""Subprocess tests for the wave-2 workflow presets (task B7 deliverable 4).

The probe is the ONLY sanctioned launcher of the explorer server
(CONSTRAINTS.md O12) -- both tests run it as a subprocess against a
tmp-built fixture db (free port, tmp `--ledger`), exactly like
tests/probe/test_probe_qualification_subprocess.py's precedent. Free of the
five index-writing names.
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
    tmp_path = tmp_path_factory.mktemp("probe_workflow_index")
    db_path = tmp_path / "fixture_index.db"
    build(str(DOCS_ROOT), str(db_path))
    return db_path


def _run_probe(fixture_db: Path, out_dir: Path, ledger_path: Path, extra_args: list[str]) -> subprocess.CompletedProcess:
    port = _free_port()
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    cmd = [
        sys.executable, str(PROBE_SCRIPT),
        "--db", str(fixture_db),
        "--docs-root", str(DOCS_ROOT),
        "--port", str(port),
        "--out", str(out_dir),
        "--ledger", str(ledger_path),
        "--timeout", "30",
        *extra_args,
    ]
    return subprocess.run(
        cmd, cwd=str(REPO_ROOT), env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=90,
    )


def test_probe_kg_subprocess_is_framework_smoke_pass(fixture_db, tmp_path):
    out_dir = tmp_path / "kg_out"
    ledger_path = tmp_path / "kg_ledger.json"
    result = _run_probe(fixture_db, out_dir, ledger_path, ["--preset", "KG"])

    assert result.returncode == 0, f"probe exited {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"

    summary = json.loads((out_dir / "run_summary.json").read_text(encoding="utf-8"))
    assert summary["run_kind"] == "smoke"
    assert summary["qualification_state"] == "FRAMEWORK_SMOKE_PASS"
    assert summary["verdict"] == "PASS"
    assert summary["run_error"] is None

    kg = json.loads((out_dir / "KG.json").read_text(encoding="utf-8"))
    assert kg["ok"] is True
    assert kg["verdict"] == "PASS"
    assert kg["reasons"] == []
    assert kg["fault_detected"] is False
    obs = kg["observations"]
    assert obs["identifier_first_doc_id"] == "RHACO-EVT-20260115-004"
    assert obs["lexical_api_line_no"] == 15
    assert obs["reader_card_index_mismatch"] == ""

    # a KG run never touches the qualification ledger (no fault -> no QUALIFICATION_PASS).
    assert not ledger_path.is_file()


def test_probe_kb2_stale_card_fault_subprocess_qualifies(fixture_db, tmp_path):
    out_dir = tmp_path / "kb2_out"
    ledger_path = tmp_path / "kb2_ledger.json"
    committed_ledger_before = COMMITTED_LEDGER.read_bytes() if COMMITTED_LEDGER.is_file() else None

    result = _run_probe(fixture_db, out_dir, ledger_path, ["--preset", "KB2", "--fault", "stale_card"])

    assert result.returncode == 0, f"probe exited {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"

    summary = json.loads((out_dir / "run_summary.json").read_text(encoding="utf-8"))
    assert summary["run_kind"] == "qualification"
    assert summary["qualification_state"] == "QUALIFICATION_PASS"
    assert summary["qualified_failure_classes"] == ["KB2"]
    assert summary["verdict"] == "PASS"
    assert summary["run_error"] is None

    kb2 = json.loads((out_dir / "KB2.json").read_text(encoding="utf-8"))
    assert kb2["verdict"] == "FAIL"
    assert kb2["fault_detected"] is True
    assert kb2["fault_class"] == "KB2"
    obs = kb2["observations"]
    assert obs["page_card_index_mismatch"]
    assert obs["indexed_title"] != obs["file_title"] or obs["indexed_status"] != obs["file_status"]

    # the tmp ledger gains KB2 ...
    assert ledger_path.is_file()
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert "KB2" in ledger["classes"]
    assert any(run["classes"] == ["KB2"] for run in ledger["runs"])

    # ... and the committed ledger is untouched by this test.
    committed_ledger_after = COMMITTED_LEDGER.read_bytes() if COMMITTED_LEDGER.is_file() else None
    assert committed_ledger_after == committed_ledger_before
