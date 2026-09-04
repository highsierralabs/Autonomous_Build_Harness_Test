"""(k) Child-process test: with RHACO_CORPUS_DISABLE_VEC=1, search_hybrid must
report mode_effective == "hybrid-degraded-lexical" and the exact degradation
notice text. Runs the venv interpreter as a bounded (120 s) FOREGROUND
subprocess (subprocess.run, no Popen/background/sleep-poll) -- the only
process this test file starts, per Foreground-only (RHACO Guide v1.3 D-3).
"""
from __future__ import annotations

import os
import subprocess
import sys

_PROBE_SCRIPT = """
from explorer.config import Settings
from explorer.corpus_adapter import CorpusAdapter

adapter = CorpusAdapter(Settings())
result = adapter.search_hybrid("firmware transfer function", top_k=5)
print("MODE_EFFECTIVE=" + str(result.mode_effective))
print("DEGRADATION_NOTICE=" + str(result.degradation_notice))
"""

_WORKTREE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_hybrid_degrades_to_lexical_when_vec_disabled():
    env = dict(os.environ)
    env["RHACO_CORPUS_DISABLE_VEC"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    proc = subprocess.run(
        [sys.executable, "-c", _PROBE_SCRIPT],
        cwd=_WORKTREE_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )

    assert proc.returncode == 0, f"child process failed: stdout={proc.stdout!r} stderr={proc.stderr!r}"
    assert "MODE_EFFECTIVE=hybrid-degraded-lexical" in proc.stdout, proc.stdout
    expected_notice = "DEGRADATION_NOTICE=Hybrid unavailable: using lexical retrieval. Result ordering is lexical-only."
    assert expected_notice in proc.stdout, proc.stdout
