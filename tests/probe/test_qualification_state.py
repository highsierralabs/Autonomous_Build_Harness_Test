"""Unit tests for tools/probe_corpus_explorer.derive_qualification (task C1 item 2;
Director ruling AC-3). Synthetic preset-result dicts only -- no server, no browser,
no fixture index. Free of the five index-writing names (CONSTRAINTS.md O2).
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.probe_corpus_explorer import derive_qualification  # noqa: E402


def _page(name, verdict="PASS", fault_detected=False, fault_class=None):
    return {"preset": name, "kind": "page", "ok": verdict == "PASS",
            "verdict": verdict, "fault_detected": fault_detected, "fault_class": fault_class}


def _json_ok(name="healthz"):
    return {"preset": name, "kind": "json_endpoint", "ok": True, "status": None}


def _not_implemented(name):
    return {"preset": name, "kind": "not_implemented", "ok": True, "status": "not_implemented_yet"}


# --- INCOMPLETE ---------------------------------------------------------------

def test_any_not_implemented_preset_is_incomplete_even_if_run_kind_would_pass():
    results = {"healthz": _json_ok(), "W1": _not_implemented("W1")}
    q = derive_qualification(results, "smoke", None, {"classes": {}, "runs": []})
    assert q["qualification_state"] == "INCOMPLETE"
    assert q["incomplete_presets"] == ["W1"]


# --- qualification run_kind ---------------------------------------------------

def test_qualification_with_detection_passes():
    results = {"diagnostics": _page("diagnostics", verdict="FAIL", fault_detected=True, fault_class="KB5")}
    q = derive_qualification(results, "qualification", "console_error", {"classes": {}, "runs": []})
    assert q["qualification_state"] == "QUALIFICATION_PASS"
    assert q["qualified_failure_classes"] == ["KB5"]
    assert q["product_evidence_eligible"] is False


def test_qualification_without_detection_fails():
    # The page preset came back clean -- the probe did not detect the known-bad.
    results = {"diagnostics": _page("diagnostics", verdict="PASS")}
    q = derive_qualification(results, "qualification", "console_error", {"classes": {}, "runs": []})
    assert q["qualification_state"] == "FAIL"
    assert q["qualified_failure_classes"] == []
    assert q["reasons"]


def test_qualification_wrong_fault_class_attribution_fails():
    # Detected *something*, but attributed to the wrong class -- still not a pass.
    results = {"diagnostics": _page("diagnostics", verdict="FAIL", fault_detected=True, fault_class="KB1")}
    q = derive_qualification(results, "qualification", "console_error", {"classes": {}, "runs": []})
    assert q["qualification_state"] == "FAIL"


def test_qualification_other_preset_must_also_pass():
    results = {
        "diagnostics": _page("diagnostics", verdict="FAIL", fault_detected=True, fault_class="KB5"),
        "healthz": {"preset": "healthz", "kind": "json_endpoint", "ok": False, "status": None},
    }
    q = derive_qualification(results, "qualification", "console_error", {"classes": {}, "runs": []})
    assert q["qualification_state"] == "FAIL"


def test_qualification_no_page_preset_selected_fails():
    results = {"healthz": _json_ok()}
    q = derive_qualification(results, "qualification", "console_error", {"classes": {}, "runs": []})
    assert q["qualification_state"] == "FAIL"


# --- smoke run_kind ------------------------------------------------------------

def test_smoke_clean_passes():
    results = {"healthz": _json_ok(), "diagnostics": _page("diagnostics", verdict="PASS")}
    q = derive_qualification(results, "smoke", None, {"classes": {}, "runs": []})
    assert q["qualification_state"] == "FRAMEWORK_SMOKE_PASS"
    assert q["qualified_failure_classes"] == []
    assert q["product_evidence_eligible"] is False


def test_smoke_any_fail_fails():
    results = {"healthz": _json_ok(), "diagnostics": _page("diagnostics", verdict="FAIL")}
    q = derive_qualification(results, "smoke", None, {"classes": {}, "runs": []})
    assert q["qualification_state"] == "FAIL"


# --- product run_kind ----------------------------------------------------------

def test_product_uncovered_preset_yields_smoke_pass_blocked():
    results = {"healthz": _json_ok(), "diagnostics": _page("diagnostics", verdict="PASS")}
    # diagnostics.required_classes == ("KB5",) in PRESET_REGISTRY; empty ledger -> uncovered.
    q = derive_qualification(results, "product", None, {"classes": {}, "runs": []})
    assert q["qualification_state"] == "FRAMEWORK_SMOKE_PASS"
    assert q["product_evidence_eligible"] is False
    assert "diagnostics" in q["product_evidence_blocked_by"]


def test_product_fully_covered_by_ledger_passes():
    results = {"healthz": _json_ok(), "diagnostics": _page("diagnostics", verdict="PASS")}
    ledger = {"classes": {"KB5": {"run": "runs/x", "recorded_utc": "2026-01-01T00:00:00+00:00"}}, "runs": []}
    q = derive_qualification(results, "product", None, ledger)
    assert q["qualification_state"] == "PRODUCT_EVIDENCE_PASS"
    assert q["product_evidence_eligible"] is True
    assert q["qualified_failure_classes"] == ["KB5"]


def test_product_any_fail_fails_regardless_of_ledger():
    results = {"healthz": _json_ok(), "diagnostics": _page("diagnostics", verdict="FAIL")}
    ledger = {"classes": {"KB5": {"run": "runs/x", "recorded_utc": "t"}}, "runs": []}
    q = derive_qualification(results, "product", None, ledger)
    assert q["qualification_state"] == "FAIL"
