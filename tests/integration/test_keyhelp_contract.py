"""Integration contract test (integrator-owned; ARCHITECTURE.md section 2, decision A22).

Guards the one contract that spans the `web` module and every page: the keyboard
shortcuts `explorer/web/static/app.js` actually binds must be the shortcuts the
`#keyhelp` block advertises to the operator.

HISTORY, because the shape of this test is the history of the defect it guards.
It was written at round 3 against FIVE page templates, each carrying a
byte-identical copy of the block -- and it earned its keep immediately, catching
the newly merged lineage page which had copied a stale two-key version inside the
very wave that created it. But the duplication was always the real defect (open
item O-2), and web round 2 moved the block into `base.html` once and deleted the
five copies. This file's five-template constant went red at that merge, exactly as
the round's dispatch anticipated; the builder filed a change request rather than
editing an integrator-owned file, and this is the integrator applying it.

WHAT CHANGED, AND WHY THE GUARD IS NOW STRONGER. The old registration test
asserted that the set of files carrying a `#keyhelp` block equalled a hard-coded
list of five. The new one asserts that `base.html` is the ONLY file under
`explorer/` that carries one. That is a strictly tighter invariant: under the old
form a sixth page could be added to the constant and pass; under the new form ANY
re-introduced copy fails, anywhere, which is precisely the defect's own history.

WHAT THIS TEST STILL DOES NOT DO, unchanged and worth restating. It is a STATIC
contract test over repository files. It executes no JavaScript and renders no
template, so it proves the documentation matches the source -- never that the key
handling works in a browser. As of web round 2 the keyboard behaviour of this
build has still never been executed by ANY layer: no test presses a key, and the
probe, which is the only sanctioned launcher, is exhausted at 4 of 4 with its
budget not waived (critic round 1, blind spot 4; BOUNDED_FAIL register). The
render-time half -- that every page really emits exactly one hidden block with all
six keys -- is covered by `tests/web/test_keyhelp_shell.py`, which does render.
"""
from __future__ import annotations

import os
import re

import pytest

WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APP_JS = os.path.join(WORKSPACE, "explorer", "web", "static", "app.js")

# The single source of truth for the #keyhelp block since web round 2 (O-2).
# It lives in the shell, which is web-owned, and nowhere else.
KEYHELP_SHELL_TEMPLATE = os.path.join("explorer", "web", "templates", "base.html")

# The binding contract of record (ARCHITECTURE.md 4.7). Each entry is
# (token as it appears in app.js, the <kbd> label the shell must show).
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


def test_keyhelp_documents_every_bound_key() -> None:
    """The shell's #keyhelp advertises every key app.js binds (the documentation side)."""
    block = _KEYHELP_RE.search(_read(KEYHELP_SHELL_TEMPLATE))
    assert block, f"{KEYHELP_SHELL_TEMPLATE}: no #keyhelp block found"
    shown = {k.strip() for k in _KBD_RE.findall(block.group(0))}
    missing = [label for _tok, label in BINDINGS if label not in shown]
    assert not missing, (
        f"{KEYHELP_SHELL_TEMPLATE}: #keyhelp does not document {missing}; it shows "
        f"{sorted(shown)}. app.js binds these keys, so the shell must say so."
    )


def test_keyhelp_advertises_nothing_it_does_not_bind() -> None:
    """The converse: the shell must not advertise a key app.js does not bind."""
    block = _KEYHELP_RE.search(_read(KEYHELP_SHELL_TEMPLATE))
    assert block
    shown = {k.strip() for k in _KBD_RE.findall(block.group(0))}
    # Down / Up are the documented aliases of j / k (app.js binds ArrowDown / ArrowUp).
    allowed = {label for _tok, label in BINDINGS} | {"Down", "Up"}
    extra = sorted(shown - allowed)
    assert not extra, (
        f"{KEYHELP_SHELL_TEMPLATE}: #keyhelp advertises {extra}, which app.js does not bind"
    )


def test_the_shell_is_the_only_file_carrying_a_keyhelp_block() -> None:
    """No page module may re-introduce its own copy.

    This replaces the round-3 registration test, which compared the files on disk
    against a hard-coded list of five and would have passed a sixth copy simply by
    adding it to the constant. Re-introduction is the defect's own history -- a
    stale copy appeared in the lineage page inside the wave that created the
    original control -- so the invariant is now that there is exactly ONE.
    """
    found = []
    for root, _dirs, files in os.walk(os.path.join(WORKSPACE, "explorer")):
        for name in files:
            if not name.endswith(".html"):
                continue
            path = os.path.join(root, name)
            with open(path, encoding="utf-8") as fh:
                if 'id="keyhelp"' in fh.read():
                    found.append(os.path.relpath(path, WORKSPACE))
    assert found == [KEYHELP_SHELL_TEMPLATE], (
        f"#keyhelp blocks on disk: {sorted(found)}; expected exactly one, in the shell "
        f"({KEYHELP_SHELL_TEMPLATE}). A page module carrying its own copy re-introduces "
        "open item O-2, which web round 2 closed by moving the block into base.html."
    )
