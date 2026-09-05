"""File-content assertions on explorer/web/static/app.js (dispatch task B9
item 4, fourth bullet).

These are FILE-CONTENT assertions, not behavioural evidence: TestClient
never executes JavaScript, so nothing here proves the keyboard navigation,
the aria-live announcement, or the row-selection highlight actually work in
a browser. That is the L2 probe's (round 4) and the L3 critic's job. What
this file proves is narrower and real: the shipped source text has no
network call, imports nothing external, and contains the key bindings and
the form-field early-return the dispatch requires.
"""
from __future__ import annotations

from pathlib import Path

APP_JS = Path(__file__).resolve().parents[2] / "explorer" / "web" / "static" / "app.js"


def _source() -> str:
    return APP_JS.read_text(encoding="utf-8")


def test_no_network_calls():
    src = _source()
    assert "fetch(" not in src
    assert "fetch (" not in src
    assert "XMLHttpRequest" not in src
    assert "WebSocket" not in src


def test_no_external_import():
    src = _source()
    assert "import(" not in src
    assert "import " not in src
    assert "require(" not in src
    assert "http://" not in src
    assert "https://" not in src


def test_binds_the_required_keys():
    src = _source()
    for literal in ['"j"', '"k"', '"Enter"', '"Escape"', '"/"', '"?"', '"ArrowDown"', '"ArrowUp"']:
        assert literal in src, f"app.js does not reference the key literal {literal}"


def test_early_returns_inside_form_fields():
    src = _source()
    assert "isFormField" in src
    assert "INPUT" in src and "TEXTAREA" in src and "SELECT" in src
    assert "isContentEditable" in src
    # the guard is the first thing the keydown handler does and bails out
    assert "if (isFormField(ev.target)) { return; }" in src


def test_uses_the_kbd_status_live_region_and_a_styled_selection_class():
    src = _source()
    assert "kbd-status" in src, "app.js does not announce into #kbd-status"
    assert "kbd-selected" in src, "app.js does not apply a styled selection class"


def test_data_doc_id_is_the_row_selector():
    src = _source()
    assert "data-doc-id" in src, "app.js does not select rows by data-doc-id (ARCHITECTURE.md A19)"
