"""Shell contract tests for explorer/web (RHACO-HND-20260903-001 S6-B9,
dispatch task B9 item 4, first bullet).

Exercises the shared base.html shell through every already-merged page via
FastAPI's TestClient against the fixture index (no server process,
ARCHITECTURE.md A18): catalog (`/`), search (`/search?q=fixture`), reader
(`/doc/reports/RHACO-ANL-20260115-002_Fixture_Analysis.card.yaml`), and
diagnostics (`/diagnostics`). Each is asserted for: HTTP 200; the skip-link;
the three shell landmarks (header, main, footer -- "nav" lives inside
"header" and is checked separately by nav-link count, matching the
dispatch's own "three landmarks" / "three nav links" phrasing); the three
primary nav links; `aria-current="page"` on exactly one nav item; the
verbatim PROMPT.md 5.6 authority-notice sentence with its bolded lead; and
both /static/web/app.css and /static/web/app.js linked.

Decision this test locks in (docs/rounds/R03_web.report.md, Decisions):
base.html has no per-page override for which nav item is "active" --
ARCHITECTURE.md 4.7's nav is Catalog/Search/Diagnostics only (dispatch item
41 forbids a bare Lineage link; there is likewise no Reader link), so
base.html derives the active item from `request.url.path` (always present
in a Jinja2Templates context -- starlette.templating.Jinja2Templates.
TemplateResponse calls `context.setdefault("request", request)`, verified
this round against the installed starlette 1.6.0): "/" and any "/doc/..." or
"/lineage/..." path mark Catalog active (document reading is reached from
the catalog, which is also why the reader already links "lineage view" per
document instead of the nav carrying it), "/search..." marks Search,
"/diagnostics..." marks Diagnostics.
"""
from __future__ import annotations

import re

import pytest

AUTHORITY_SENTENCE_PLAIN = (
    "Retrieval is not adjudication. This application helps locate and "
    "traverse RHACO documents. The canonical documents and their governed "
    "metadata remain the record; search rank does not establish scientific "
    "correctness or authority."
)
AUTHORITY_SENTENCE_RENDERED = (
    "<strong>Retrieval is not adjudication.</strong> This application helps "
    "locate and traverse RHACO documents. The canonical documents and their "
    "governed metadata remain the record; search rank does not establish "
    "scientific correctness or authority."
)

READER_CARD_REF = "reports/RHACO-ANL-20260115-002_Fixture_Analysis.card.yaml"

PAGES = [
    ("/", "Catalog"),
    ("/search?q=fixture", "Search"),
    (f"/doc/{READER_CARD_REF}", "Catalog"),
    ("/diagnostics", "Diagnostics"),
]


@pytest.mark.parametrize("path, expected_active", PAGES, ids=[p for p, _ in PAGES])
def test_shell_renders_on_every_merged_page(fixture_client, path, expected_active):
    resp = fixture_client.get(path)
    assert resp.status_code == 200, f"{path} -> {resp.status_code}: {resp.text[:500]}"
    body = resp.text

    assert 'class="skip-link"' in body, "skip-link missing"
    assert re.search(r"<header\b", body), "header landmark missing"
    assert re.search(r"<main\b", body), "main landmark missing"
    assert re.search(r"<footer\b", body), "footer landmark missing"

    assert re.search(r'<a[^>]*\shref="/"', body), "Catalog nav link missing"
    assert 'href="/search"' in body, "Search nav link missing"
    assert 'href="/diagnostics"' in body, "Diagnostics nav link missing"

    current_count = body.count('aria-current="page"')
    assert current_count == 1, f"expected exactly one aria-current=page, got {current_count} for {path}"

    active_pattern = re.compile(
        r'<a href="[^"]*"\s+aria-current="page">' + re.escape(expected_active) + r"<"
    )
    assert active_pattern.search(body), (
        f"aria-current=page was not on the {expected_active!r} nav link for {path}\n"
        f"...{body[body.find('site-header'):body.find('site-header') + 400]}..."
    )

    assert AUTHORITY_SENTENCE_RENDERED in body, "authority notice not rendered verbatim with bolded lead"

    assert 'href="/static/web/app.css"' in body, "app.css not linked"
    assert 'src="/static/web/app.js"' in body, "app.js not linked"


def test_authority_sentence_matches_prompt_5_6_word_for_word(fixture_client):
    """The bolded lead plus the rest must reconstruct PROMPT.md 5.6's sentence
    exactly (this is the behavioural counterpart to the file-content check in
    test_base_template_source.py: it proves the *rendered* page, not just the
    template source, carries the required words)."""
    body = fixture_client.get("/diagnostics").text
    stripped = body.replace("<strong>", "").replace("</strong>", "")
    assert AUTHORITY_SENTENCE_PLAIN in stripped
