"""Unit tests for the wave-2 fault-attribution predicates (task B7 deliverable 4):
`_kb1_verdict`, `_kb2_verdict`, `_kb4_verdict`, `_w10_localhost_check`, and
`_verify_heading_independently`. All are pure functions over synthetic
already-observed values -- no server, no browser, no fixture index. Free of the
five index-writing names (CONSTRAINTS.md O2 / tools/l1_index_write_check.py).
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.probe_corpus_explorer import (  # noqa: E402
    _kb1_verdict,
    _kb2_verdict,
    _kb4_verdict,
    _verify_heading_independently,
    _w10_localhost_check,
)

CORRECT_REF = "handoffs/RHACO-HND-20260115-003_Fixture_Handoff.card.yaml"
FAULT_REF = "handoffs/RHACO-HND-20260115-003_Fixture_Handoff_Amendment_A1.card.yaml"


# --- _kb1_verdict (wrong_doc_for_id) ------------------------------------------


def test_kb1_correct_ref_is_a_clean_pass():
    reasons, detected, cls = _kb1_verdict(CORRECT_REF, CORRECT_REF, FAULT_REF)
    assert reasons == []
    assert detected is False
    assert cls is None


def test_kb1_rotated_ref_is_detected_as_kb1():
    reasons, detected, cls = _kb1_verdict(FAULT_REF, CORRECT_REF, FAULT_REF)
    assert reasons and "wrong_doc_for_id" in reasons[0]
    assert detected is True
    assert cls == "KB1"


def test_kb1_unexpected_ref_fails_without_attribution():
    reasons, detected, cls = _kb1_verdict("something/else.card.yaml", CORRECT_REF, FAULT_REF)
    assert reasons
    assert detected is False
    assert cls is None


def test_kb1_none_observed_fails_without_attribution():
    reasons, detected, cls = _kb1_verdict(None, CORRECT_REF, FAULT_REF)
    assert reasons
    assert detected is False
    assert cls is None


# --- _kb2_verdict (stale_card) -------------------------------------------------


def test_kb2_clean_agreement_is_a_pass():
    reasons, detected, cls = _kb2_verdict("", "Fixture Analysis", "Active", "Fixture Analysis", "Active")
    assert reasons == []
    assert detected is False
    assert cls is None


def test_kb2_page_marker_alone_is_kb2():
    # The page's own data-card-index-mismatch is set even though the probe's
    # independent file comparison happens to agree -- either observable suffices.
    reasons, detected, cls = _kb2_verdict("title,status", "Fixture Analysis", "Active", "Fixture Analysis", "Active")
    assert reasons and "KB2" in reasons[0]
    assert detected is True
    assert cls == "KB2"


def test_kb2_independent_file_disagreement_alone_is_kb2():
    # The page's own marker is NOT set, but the probe's independent read of the
    # card file disagrees with what the index (API) reports -- still KB2.
    reasons, detected, cls = _kb2_verdict("", "Fixture Analysis", "Active", "Fixture Analysis [STALE]", "Draft")
    assert reasons and "KB2" in reasons[0]
    assert detected is True
    assert cls == "KB2"


def test_kb2_both_observables_set_is_still_kb2():
    reasons, detected, cls = _kb2_verdict("title,status", "Fixture Analysis", "Active", "Fixture Analysis [STALE]", "Draft")
    assert reasons
    assert detected is True
    assert cls == "KB2"


# --- _kb4_verdict (broken_jump) ------------------------------------------------


def test_kb4_clean_is_a_pass():
    reasons, detected, cls = _kb4_verdict(False, 0)
    assert reasons == []
    assert detected is False
    assert cls is None


def test_kb4_page_marker_alone_is_kb4():
    reasons, detected, cls = _kb4_verdict(True, 0)
    assert reasons and "KB4" in reasons[0]
    assert detected is True
    assert cls == "KB4"


def test_kb4_independent_mismatch_alone_is_kb4():
    reasons, detected, cls = _kb4_verdict(False, 2)
    assert reasons
    assert detected is True
    assert cls == "KB4"


def test_kb4_both_observables_is_still_kb4():
    reasons, detected, cls = _kb4_verdict(True, 4)
    assert reasons
    assert detected is True
    assert cls == "KB4"


# --- _verify_heading_independently ---------------------------------------------


def test_verify_heading_matches_atx_heading_text():
    lines = ["intro", "## 2. Unique lexical marker", "body"]
    assert _verify_heading_independently(lines, 2, "2. Unique lexical marker") is True


def test_verify_heading_rejects_shifted_line_no():
    lines = ["intro", "## 2. Unique lexical marker", "body"]
    # broken_jump shifts line_no by +50 -- well past the document's own lines.
    assert _verify_heading_independently(lines, 52, "2. Unique lexical marker") is False


def test_verify_heading_rejects_wrong_text_at_the_claimed_line():
    lines = ["intro", "## Something else entirely", "body"]
    assert _verify_heading_independently(lines, 2, "2. Unique lexical marker") is False


# --- _w10_localhost_check (W10) -------------------------------------------------


def test_w10_all_localhost_requests_pass():
    requests = [{"url": "http://127.0.0.1:8765/"}, {"url": "http://127.0.0.1:8765/search?q=x"}]
    reasons, offenders = _w10_localhost_check(requests)
    assert reasons == []
    assert offenders == []


def test_w10_non_localhost_request_fails():
    requests = [
        {"url": "http://127.0.0.1:8765/"},
        {"url": "https://frontier-model.example.com/v1/complete"},
    ]
    reasons, offenders = _w10_localhost_check(requests)
    assert reasons
    assert "W10" in reasons[0]
    assert len(offenders) == 1
    assert offenders[0]["url"] == "https://frontier-model.example.com/v1/complete"
