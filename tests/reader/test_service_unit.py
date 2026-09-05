"""Direct unit tests of explorer.reader.service's pure helpers -- no adapter,
fake or real (states like a markdown fidelity edge case are exercised at this
level rather than by fabricating adapter behaviour the fixture already
covers; see the round report's "Material alternatives").
"""
from __future__ import annotations

from explorer.models import CardRow, Heading
from explorer.reader import service


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
