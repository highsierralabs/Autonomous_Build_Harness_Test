"""Unit tests for tools/probe_corpus_explorer.evaluate_page (task C1 item 1).

evaluate_page is a pure function: no server, no browser, no fixture index --
these tests construct synthetic observation dicts and PresetSpecs directly.
Free of the five index-writing names (CONSTRAINTS.md O2 / tools/l1_index_write_check.py).
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.probe_corpus_explorer import (  # noqa: E402
    CONSOLE_ERROR_FAULT_TEXT,
    PresetSpec,
    evaluate_page,
)

BASE_SPEC = PresetSpec(name="X", kind="page", label="test preset", path="/x")


def _obs(**overrides) -> dict:
    base = {
        "error": None,
        "http_status": 200,
        "console_errors": [],
        "failed_requests": [],
        "mode": None,
        "vector": None,
        "title": "A Title",
    }
    base.update(overrides)
    return base


# --- rule (a): navigation/extraction error ----------------------------------

def test_rule_a_navigation_error_fails():
    v = evaluate_page(_obs(error="TimeoutError: boom"), BASE_SPEC)
    assert v.ok is False
    assert any("navigation_or_extraction_error" in r for r in v.reasons)
    assert v.fault_detected is False
    assert v.fault_class is None


def test_clean_observation_passes():
    v = evaluate_page(_obs(), BASE_SPEC)
    assert v.ok is True
    assert v.reasons == []
    assert v.fault_detected is False
    assert v.fault_class is None


# --- rule (b): http_status >= 400 unless expected_status matches ------------

def test_rule_b_404_fails_when_not_expected():
    v = evaluate_page(_obs(http_status=404), BASE_SPEC)
    assert v.ok is False
    assert any("unexpected_http_status" in r for r in v.reasons)


def test_rule_b_expected_status_exception():
    spec = PresetSpec(name="X", kind="page", label="l", path="/x", expected_status=404)
    v = evaluate_page(_obs(http_status=404), spec)
    assert v.ok is True
    assert v.reasons == []


def test_rule_b_expected_status_does_not_forgive_a_different_status():
    spec = PresetSpec(name="X", kind="page", label="l", path="/x", expected_status=404)
    v = evaluate_page(_obs(http_status=500), spec)
    assert v.ok is False
    assert any("unexpected_http_status: 500" in r for r in v.reasons)


def test_rule_b_status_below_400_never_fails():
    v = evaluate_page(_obs(http_status=200), BASE_SPEC)
    assert v.ok is True


# --- rule (c): console errors + fault attribution ----------------------------

def test_rule_c_unrelated_console_error_fails_without_attribution():
    v = evaluate_page(_obs(console_errors=[{"type": "error", "text": "ReferenceError: foo is not defined"}]),
                       BASE_SPEC)
    assert v.ok is False
    assert v.fault_detected is False
    assert v.fault_class is None
    assert any("console_error" in r for r in v.reasons)


def test_rule_c_console_error_matching_fault_marker_attributes_kb5():
    v = evaluate_page(
        _obs(console_errors=[{"type": "pageerror", "text": CONSOLE_ERROR_FAULT_TEXT}]),
        BASE_SPEC,
    )
    assert v.ok is False
    assert v.fault_detected is True
    assert v.fault_class == "KB5"
    assert any("KB5" in r for r in v.reasons)


def test_rule_c_fault_marker_as_substring_still_attributes():
    text = f"Uncaught Error: {CONSOLE_ERROR_FAULT_TEXT}"
    v = evaluate_page(_obs(console_errors=[{"type": "pageerror", "text": text}]), BASE_SPEC)
    assert v.fault_detected is True
    assert v.fault_class == "KB5"


# --- rule (d): failed requests ------------------------------------------------

def test_rule_d_failed_request_fails():
    v = evaluate_page(
        _obs(failed_requests=[{"source": "response", "url": "http://x/y", "status": 500}]),
        BASE_SPEC,
    )
    assert v.ok is False
    assert any("failed_request" in r for r in v.reasons)
    assert v.fault_detected is False


# --- rule (e): declarative data-* assertions ---------------------------------

def test_rule_e_data_mode_in_violation():
    spec = PresetSpec(name="X", kind="page", label="l", path="/x", data_mode_in={"hybrid"})
    v = evaluate_page(_obs(mode="hybrid-degraded-lexical"), spec)
    assert v.ok is False
    assert any(r.startswith("data_mode_in") for r in v.reasons)


def test_rule_e_data_mode_in_satisfied():
    spec = PresetSpec(name="X", kind="page", label="l", path="/x",
                       data_mode_in={"hybrid", "hybrid-degraded-lexical"})
    v = evaluate_page(_obs(mode="hybrid-degraded-lexical"), spec)
    assert v.ok is True


def test_rule_e_data_vector_in_violation():
    spec = PresetSpec(name="X", kind="page", label="l", path="/x", data_vector_in={"available"})
    v = evaluate_page(_obs(vector="unavailable"), spec)
    assert v.ok is False
    assert any(r.startswith("data_vector_in") for r in v.reasons)


def test_rule_e_require_title_violation():
    spec = PresetSpec(name="X", kind="page", label="l", path="/x", require_title=True)
    v = evaluate_page(_obs(title=""), spec)
    assert v.ok is False
    assert any(r.startswith("require_title") for r in v.reasons)


def test_rule_e_require_title_satisfied():
    spec = PresetSpec(name="X", kind="page", label="l", path="/x", require_title=True)
    v = evaluate_page(_obs(title="Diagnostics"), spec)
    assert v.ok is True


def test_diagnostics_shaped_spec_all_assertions_together():
    spec = PresetSpec(
        name="diagnostics", kind="page", label="l", path="/diagnostics",
        data_mode_in={"hybrid", "hybrid-degraded-lexical"},
        data_vector_in={"available", "unavailable"},
        require_title=True,
    )
    v = evaluate_page(_obs(mode="hybrid-degraded-lexical", vector="unavailable", title="Diagnostics"), spec)
    assert v.ok is True
    assert v.reasons == []
