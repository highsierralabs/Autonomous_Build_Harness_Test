"""Smoke test for tools/probe_corpus_explorer.py (ARCHITECTURE.md section 4.8;
task B2).

Runs the probe as a subprocess -- the probe is the ONLY sanctioned launcher of
the explorer server (CONSTRAINTS.md O12); this test never imports or spawns
uvicorn itself -- against a tmp-built fixture db, with --preset healthz, and
asserts run_summary.json exists and reports success.
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


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def fixture_db(tmp_path_factory) -> Path:
    tmp_path = tmp_path_factory.mktemp("probe_smoke_index")
    db_path = tmp_path / "fixture_index.db"
    build(str(DOCS_ROOT), str(db_path))
    return db_path


def test_probe_healthz_preset_subprocess(fixture_db, tmp_path):
    out_dir = tmp_path / "probe_out"
    port = _free_port()
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    cmd = [
        sys.executable, str(PROBE_SCRIPT),
        "--db", str(fixture_db),
        "--docs-root", str(DOCS_ROOT),
        "--preset", "healthz",
        "--port", str(port),
        "--out", str(out_dir),
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
    assert summary["verdict"] == "PASS"
    assert summary["run_error"] is None
    assert summary["presets_run"] == ["healthz"]
    assert summary["results"]["healthz"]["ok"] is True
    assert summary["results"]["healthz"]["http_status"] == 200
    assert summary["healthz"] is not None
    assert summary["healthz"]["status"] == "ok"

    healthz_json_path = out_dir / "healthz.json"
    assert healthz_json_path.is_file()
    healthz_obs = json.loads(healthz_json_path.read_text(encoding="utf-8"))
    assert healthz_obs["ok"] is True
    assert healthz_obs["http_status"] == 200

    server_log_path = out_dir / "server.log"
    assert server_log_path.is_file()
