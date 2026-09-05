"""SA-1 (dispatch R07 item 1): with RHACO_CORPUS_DISABLE_VEC=1, search_graph
must report the corrected mode_effective token and notice text -- naming the
channel that actually degraded (the hybrid seed) rather than the old bare
"graph-degraded" token, which named no surviving channel. No layer of this
build's harness had exercised graph mode under --disable-vec before this
round (the audit motivating item 1); this is the first.

Runs the venv interpreter as a bounded (120 s) FOREGROUND subprocess
(subprocess.run, no Popen/background/sleep-poll) -- the only process this
test file starts, per Foreground-only (RHACO Guide v1.3 D-3). Mirrors
test_hybrid_degraded_subprocess.py's pattern exactly.
"""
from __future__ import annotations

import os
import subprocess
import sys

_PROBE_SCRIPT = """
from explorer.config import Settings
from explorer.corpus_adapter import CorpusAdapter

adapter = CorpusAdapter(Settings())
result = adapter.search_graph("firmware transfer function", top_k=5)
print("MODE_EFFECTIVE=" + str(result.mode_effective))
print("DEGRADATION_NOTICE=" + str(result.degradation_notice))
"""

_WORKTREE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_graph_degrades_to_named_seed_channel_when_vec_disabled():
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
    assert "MODE_EFFECTIVE=graph-degraded-semantic-seed" in proc.stdout, proc.stdout
    # The old token must be gone, not merely a prefix match away -- the whole
    # point of SA-1 is that "graph-degraded" alone named no surviving channel.
    assert "MODE_EFFECTIVE=graph-degraded\n" not in proc.stdout, proc.stdout
    expected_notice = (
        "DEGRADATION_NOTICE=Graph seed channel degraded: hybrid seeding fell back to "
        "identifier resolution plus lexical (FTS) search. The graph expansion itself "
        "-- one hop over the typed edges table -- is unaffected and still shapes "
        "result ordering."
    )
    assert expected_notice in proc.stdout, proc.stdout
