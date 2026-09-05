"""Integration contract test (integrator-owned; ARCHITECTURE.md section 2, decision A22).

Guards the one contract that spans the `web` module and every page module: the keyboard
shortcuts `explorer/web/static/app.js` actually binds must be the shortcuts each page's
`#keyhelp` block advertises to the operator. Nothing else enforces this -- `tests/web/`
cannot reach another module's template, and each page module cannot see `app.js`'s
bindings -- which is exactly how wave 3 merged with `app.js` binding six keys while all
four pages still advertised two (round-3 change request from strand S6-B9).

This is a STATIC contract test over repository files. It executes no JavaScript and
renders no template, so it proves the documentation matches the source, never that the
key handling works in a browser. Behavioural verification of the keys is L2's job
(`tools/probe_corpus_explorer.py`) and L3's; see docs/LAYERS.md.
"""
from __future__ import annotations

import os
import re

import pytest

WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APP_JS = os.path.join(WORKSPACE, "explorer", "web", "static", "app.js")

# Every page template that carries a #keyhelp block. A new page module with a #keyhelp
# block must be added here; test_every_keyhelp_page_is_registered below fails if one is missed.
KEYHELP_TEMPLATES = (
    os.path.join("explorer", "catalog", "templates", "catalog", "catalog.html"),
    os.path.join("explorer", "search", "templates", "search", "search.html"),
    os.path.join("explorer", "reader", "templates", "reader", "reader.html"),
    os.path.join("explorer", "diagnostics", "templates", "diagnostics", "diagnostics.html"),
    os.path.join("explorer", "lineage", "templates", "lineage", "lineage.html"),
)

# The binding contract of record (ARCHITECTURE.md 4.7). Each entry is
# (token as it appears in app.js, the <kbd> label the page must show).
BINDINGS = (
    ('"/"', "/"),
    ('"?"', "?"),
    ('"j"', "j"),
    ('"k"', "k"),
    ('"Enter"', "Enter"),
    ('"Escape"', "Escape"),
)

_KEYHELP_RE = re.compile(r'<div id="keyhelp".*?</div>', re.DOTALL)
_KBD_RE = re.compile(r"<kbd>([^<]*)</kbd>")


def _read(rel: str) -> str:
    with open(os.path.join(WORKSPACE, rel), encoding="utf-8") as fh:
        return fh.read()


@pytest.fixture(scope="module")
def app_js() -> str:
    with open(APP_JS, encoding="utf-8") as fh:
        return fh.read()


@pytest.mark.parametrize("token,label", BINDINGS)
def test_app_js_binds_every_documented_key(app_js: str, token: str, label: str) -> None:
    """app.js really contains each key of the contract (the source side)."""
    assert token in app_js, f"app.js does not bind {label!r} (looked for {token})"


@pytest.mark.parametrize("template", KEYHELP_TEMPLATES)
def test_keyhelp_documents_every_bound_key(template: str) -> None:
    """Each page's #keyhelp advertises every key app.js binds (the documentation side)."""
    block = _KEYHELP_RE.search(_read(template))
    assert block, f"{template}: no #keyhelp block found"
    shown = {k.strip() for k in _KBD_RE.findall(block.group(0))}
    missing = [label for _tok, label in BINDINGS if label not in shown]
    assert not missing, (
        f"{template}: #keyhelp does not document {missing}; it shows {sorted(shown)}. "
        "app.js binds these keys, so the page must say so (round-3 change request S6-B9)."
    )


@pytest.mark.parametrize("template", KEYHELP_TEMPLATES)
def test_keyhelp_advertises_nothing_it_does_not_bind(template: str) -> None:
    """The converse: a page must not advertise a key app.js does not bind."""
    block = _KEYHELP_RE.search(_read(template))
    assert block
    shown = {k.strip() for k in _KBD_RE.findall(block.group(0))}
    # Down / Up are the documented aliases of j / k (app.js binds ArrowDown / ArrowUp).
    allowed = {label for _tok, label in BINDINGS} | {"Down", "Up"}
    extra = sorted(shown - allowed)
    assert not extra, f"{template}: #keyhelp advertises {extra}, which app.js does not bind"


def test_every_keyhelp_page_is_registered() -> None:
    """No page module carries a #keyhelp block that this test does not cover."""
    found = []
    for root, _dirs, files in os.walk(os.path.join(WORKSPACE, "explorer")):
        for name in files:
            if not name.endswith(".html"):
                continue
            path = os.path.join(root, name)
            with open(path, encoding="utf-8") as fh:
                if 'id="keyhelp"' in fh.read():
                    found.append(os.path.relpath(path, WORKSPACE))
    assert sorted(found) == sorted(KEYHELP_TEMPLATES), (
        f"#keyhelp blocks on disk: {sorted(found)}; registered here: {sorted(KEYHELP_TEMPLATES)}. "
        "A new page with a keyhelp block must be added to KEYHELP_TEMPLATES."
    )
