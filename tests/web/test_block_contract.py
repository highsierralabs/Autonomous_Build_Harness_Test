"""Block-contract regression guard for explorer/web (dispatch task B9 item 4,
third bullet): every block name another module's template relies on still
exists in base.html, and each merged page's own `data-mode` still reaches
the `<html>` tag through `html_attrs`.

The block-name check is a file-content assertion on base.html's own source
(labelled honestly as such -- it proves the block *names* survived this
round's edit, not that Jinja resolves them correctly at render time; the
`data-mode` checks below are the behavioural proof of that, via TestClient
against the real merged templates).
"""
from __future__ import annotations

import re
from pathlib import Path

BASE_HTML = Path(__file__).resolve().parents[2] / "explorer" / "web" / "templates" / "base.html"

REQUIRED_BLOCKS = ["title", "html_attrs", "main_attrs", "head_extra", "content", "scripts"]


def test_base_html_keeps_every_block_other_templates_depend_on():
    """File-content assertion (UNVERIFIED as render behavior): base.html's
    source still declares every block name catalog.html, search.html,
    reader.html and diagnostics.html override or extend."""
    src = BASE_HTML.read_text(encoding="utf-8")
    for name in REQUIRED_BLOCKS:
        assert re.search(r"\{%-?\s*block\s+" + re.escape(name) + r"\b", src), (
            f"base.html no longer declares {{% block {name} %}}"
        )


def test_html_attrs_hook_still_carries_data_mode_on_html_tag_catalog(fixture_client):
    resp = fixture_client.get("/")
    html_tag = re.search(r"<html\b[^>]*>", resp.text).group(0)
    assert 'data-mode="catalog"' in html_tag


def test_html_attrs_hook_still_carries_data_mode_on_html_tag_search(fixture_client):
    resp = fixture_client.get("/search?q=fixture")
    html_tag = re.search(r"<html\b[^>]*>", resp.text).group(0)
    assert re.search(r'data-mode="[^"]+"', html_tag), f"no data-mode on <html>: {html_tag}"
    assert re.search(r'data-vector="(available|unavailable)"', html_tag)


def test_html_attrs_hook_still_carries_data_mode_on_html_tag_reader(fixture_client):
    resp = fixture_client.get(
        "/doc/reports/RHACO-ANL-20260115-002_Fixture_Analysis.card.yaml"
    )
    html_tag = re.search(r"<html\b[^>]*>", resp.text).group(0)
    assert 'data-mode="reader"' in html_tag


def test_html_attrs_hook_still_carries_data_mode_on_html_tag_diagnostics(fixture_client):
    resp = fixture_client.get("/diagnostics")
    html_tag = re.search(r"<html\b[^>]*>", resp.text).group(0)
    assert re.search(r'data-mode="[^"]+"', html_tag), f"no data-mode on <html>: {html_tag}"
    assert re.search(r'data-vector="(available|unavailable)"', html_tag)
