"""Direct unit tests of explorer.reader.service's pure helpers -- no adapter,
fake or real (states like a markdown fidelity edge case are exercised at this
level rather than by fabricating adapter behaviour the fixture already
covers; see the round report's "Material alternatives").
"""
from __future__ import annotations

import datetime as dt

from explorer.models import CardRow, Heading
from explorer.reader import service


class _Exotic:
    """A non-temporal leaf `yaml.safe_load` cannot itself produce, standing in
    for one (task B11 item 1's "any other non-JSON-native leaf") -- exercises
    `_json_safe`'s final `str()` fallback branch."""

    def __str__(self) -> str:
        return "exotic-value"


def test_json_safe_converts_date_datetime_time_to_their_own_iso_text():
    # task B11 item 1: fidelity-preserving -- the ISO string is what an
    # unquoted card scalar already said, just without PyYAML's attached type.
    assert service._json_safe(dt.date(2026, 6, 24)) == "2026-06-24"
    assert service._json_safe(dt.datetime(2026, 6, 24, 10, 30, 0)) == "2026-06-24T10:30:00"
    assert service._json_safe(dt.time(10, 30, 0)) == "10:30:00"


def test_json_safe_recurses_through_nested_dicts_and_lists():
    value = {
        "identity": {"date": dt.date(2026, 6, 24), "tags": ["a", dt.date(2026, 1, 1)]},
        "history": [{"reviewed": dt.datetime(2026, 6, 24, 9, 0, 0)}],
    }
    assert service._json_safe(value) == {
        "identity": {"date": "2026-06-24", "tags": ["a", "2026-01-01"]},
        "history": [{"reviewed": "2026-06-24T09:00:00"}],
    }


def test_json_safe_falls_back_to_str_for_a_non_temporal_exotic_leaf():
    assert service._json_safe(_Exotic()) == "exotic-value"
    assert service._json_safe({"weird": _Exotic()}) == {"weird": "exotic-value"}


def test_json_safe_passes_native_json_types_through_unchanged():
    assert service._json_safe(None) is None
    assert service._json_safe(True) is True
    assert service._json_safe(3) == 3
    assert service._json_safe(3.5) == 3.5
    assert service._json_safe("s") == "s"


def test_parse_card_yaml_converts_an_unquoted_date_scalar_to_iso_text():
    # The exact defect shape: `date: 2026-06-24` with no quotes resolves to a
    # native datetime.date under plain yaml.safe_load; _parse_card_yaml must
    # hand back a plain, JSON-safe string instead (task B11 item 1).
    raw = "identity:\n  date: 2026-06-24\n  last_human_review: 2026-06-24\n"
    parsed, error = service._parse_card_yaml(raw)
    assert error is None
    assert parsed["identity"]["date"] == "2026-06-24"
    assert isinstance(parsed["identity"]["date"], str)
    assert parsed["identity"]["last_human_review"] == "2026-06-24"
    assert isinstance(parsed["identity"]["last_human_review"], str)


def test_index_mismatch_no_false_positive_for_native_date_vs_index_string():
    """Task B11 item 2: does `_index_mismatch` report a false 'date' mismatch
    when `identity['date']` is the native `datetime.date` PyYAML produces for
    an unquoted scalar (the pre-conversion shape, tested here directly against
    `_index_mismatch` itself, independent of this round's upstream
    `_json_safe` fix in `_parse_card_yaml`) while the index's `CardRow.date`
    is already the canonical ISO string `RHACO_corpus_index._norm_date`
    stores (verified by reading `C:\\RHACO\\rhaco\\RHACO_corpus_index.py`
    lines 575-590 this round: `_norm_date` maps a `datetime.date` to
    `.isoformat()`, the same canonical 'YYYY-MM-DD' form)?

    Answer, direct evidence: NO -- `str(datetime.date(...))` (what `_norm`
    applies to the file side) already equals `.isoformat()` (what the index
    side already is), so the two sides compare equal without any change to
    `_index_mismatch` itself. The bug this item asks about does not exist for
    the `date` field on this corpus's data shape."""
    card = CardRow(
        yaml_path=r"C:\fake\x.card.yaml", doc_id="RHACO-REF-1",
        title="T", status="Baseline", lifecycle_state=None,
        date="2026-06-24", doc_type="REF",
    )
    identity = {
        "title": "T", "status": "Baseline", "doc_type": "REF",
        "date": dt.date(2026, 6, 24),
    }
    assert service._index_mismatch(card, identity) == []


def test_verify_heading_line_true_for_matching_atx_line():
    heading = Heading(level=2, text="Section One", slug="section-one", line_no=3)
    lines = ["# Title", "", "## Section One", "body"]
    assert service._verify_heading_line(lines, heading) is True


def test_verify_heading_line_false_when_shifted_out_of_range():
    heading = Heading(level=2, text="Section One", slug="section-one", line_no=53)
    lines = ["# Title", "", "## Section One", "body"]
    assert service._verify_heading_line(lines, heading) is False


def test_verify_heading_line_false_when_text_does_not_match():
    heading = Heading(level=2, text="Section One", slug="section-one", line_no=3)
    lines = ["# Title", "", "## Something Else", "body"]
    assert service._verify_heading_line(lines, heading) is False


def test_index_mismatch_reports_only_differing_fields():
    card = CardRow(
        yaml_path=r"C:\fake\x.card.yaml", doc_id="RHACO-ANL-20260101-001",
        title="Real Title", status="Active", lifecycle_state=None,
        date="2026-01-01", doc_type="ANL",
    )
    identity = {
        "title": "Real Title", "status": "Draft", "lifecycle_state": None,
        "date": "2026-01-01", "doc_type": "ANL",
    }
    assert service._index_mismatch(card, identity) == ["status"]


def test_index_mismatch_empty_when_everything_agrees():
    card = CardRow(
        yaml_path=r"C:\fake\x.card.yaml", doc_id="RHACO-ANL-20260101-001",
        title="T", status="Active", lifecycle_state=None, date="2026-01-01", doc_type="ANL",
    )
    identity = {"title": "T", "status": "Active", "date": "2026-01-01", "doc_type": "ANL"}
    assert service._index_mismatch(card, identity) == []


def test_render_markdown_injects_id_and_data_line_and_preserves_table_strikethrough():
    class _Doc:
        text = "# My Heading\n\n~~gone~~ and a table:\n\n| a | b |\n|---|---|\n| 1 | 2 |\n"
        lines = text.splitlines()
        headings = [Heading(level=1, text="My Heading", slug="my-heading", line_no=1)]

    html = service._render_markdown(_Doc())
    assert '<h1 id="my-heading" data-line="1">My Heading</h1>' in html
    assert "<s>gone</s>" in html
    assert "<table>" in html
    assert "data-line-verified" not in html  # the one heading verifies cleanly


def test_render_markdown_marks_data_line_verified_false_on_mismatch():
    class _Doc:
        text = "# My Heading\n\nbody\n"
        lines = text.splitlines()
        headings = [Heading(level=1, text="My Heading", slug="my-heading", line_no=99)]

    html = service._render_markdown(_Doc())
    assert 'data-line-verified="false"' in html


def test_lifecycle_label_cmp_vs_non_cmp_vs_absent():
    assert service._lifecycle_label("CMP", "OPEN") == "CMP lifecycle state"
    assert service._lifecycle_label("ANL", "OPEN") == "informational (non-CMP)"
    assert service._lifecycle_label("ANL", None) is None
    assert service._lifecycle_label("CMP", None) is None


def test_parse_card_yaml_reports_error_on_invalid_yaml():
    parsed, error = service._parse_card_yaml("identity: [unterminated")
    assert parsed == {}
    assert error is not None


def test_parse_card_yaml_reports_error_when_not_a_mapping():
    parsed, error = service._parse_card_yaml("- just\n- a\n- list\n")
    assert parsed == {}
    assert error == "card file did not parse to a mapping"
