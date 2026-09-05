"""Integration test for the L4 direction oracle (integrator-owned; docs/LAYERS.md L4).

The oracle in `tools/l4_direction_oracle.py` is gate 7's compensating control for
BOUNDED_FAIL BF-1: the probe's W5 preset compares the product against the constant
the product renders from, so it cannot fail on the defect it appears to guard, and
the probe is exhausted and cannot be repaired.

A compensating control that has never been observed to fail is worth nothing, and
this oracle's own first two drafts proved the point twice: it reported PASS after
rendering zero pages (an absolute path used where a card_ref belongs), and its
supersession-head check was dead code for a key name that does not exist in the
API. Both are fixed; these tests are what keeps them fixed.

`evaluate()` is driven here against synthetic payloads, so the tests are fast,
deterministic, and independent of the live corpus.
"""
from __future__ import annotations

import importlib.util
import os
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ORACLE = os.path.join(REPO_ROOT, "tools", "l4_direction_oracle.py")


@pytest.fixture(scope="module")
def oracle():
    spec = importlib.util.spec_from_file_location("l4_direction_oracle", ORACLE)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["l4_direction_oracle"] = mod
    spec.loader.exec_module(mod)
    return mod


class _Resp:
    def __init__(self, payload, status=200):
        self._payload = payload
        self.status_code = status

    def json(self):
        return self._payload


class _Client:
    """Minimal stand-in for TestClient: one payload per card_ref."""

    def __init__(self, pages):
        self._pages = pages

    def get(self, url):
        ref = url.split("/api/lineage/", 1)[1]
        payload = self._pages.get(ref)
        if payload is None:
            return _Resp(None, 404)
        return _Resp(payload)


def _page(centre, outgoing=(), incoming=(), chain=()):
    return {
        "center": {"doc_id": centre},
        "outgoing": list(outgoing),
        "incoming": list(incoming),
        "chain": list(chain),
    }


def _edge(relation, label, from_id="A", to_id="B"):
    return {"relation": relation, "direction_label": label, "from_id": from_id, "to_id": to_id}


def test_correct_sentences_produce_no_findings(oracle):
    pages = {"r.card.yaml": _page(
        "B",
        outgoing=[_edge("cites", "cites"), _edge("amends", "amends")],
        incoming=[_edge("cites", "cited by"), _edge("campaign_child", "is campaign child of")],
    )}
    out = oracle.evaluate(_Client(pages), ["r.card.yaml"])
    assert out["findings"] == []
    assert out["edges_checked"] == 4
    assert out["pages_rendered"] == 1


def test_the_critics_defect_is_caught_and_named_CONVERSE(oracle):
    """An incoming edge rendered with the outgoing sentence -- gate 7's FAIL."""
    pages = {"r.card.yaml": _page(
        "B", incoming=[_edge("campaign_child", "has campaign child")],
    )}
    out = oracle.evaluate(_Client(pages), ["r.card.yaml"])
    assert len(out["findings"]) == 1
    f = out["findings"][0]
    assert f["verdict"] == "CONVERSE"
    assert f["expected"] == "is campaign child of"
    assert f["sentence"] == "has campaign child"


def test_a_supersession_head_rendered_as_superseded_is_caught(oracle):
    """The critic derived this case rather than observing it; the oracle observes it."""
    pages = {"v9.card.yaml": _page(
        "V9",
        incoming=[_edge("supersedes", "is superseded by", from_id="V8", to_id="V9")],
        chain=[{"card": {"doc_id": "V8"}, "is_head": False},
               {"card": {"doc_id": "V9"}, "is_head": True}],
    )}
    out = oracle.evaluate(_Client(pages), ["v9.card.yaml"])
    verdicts = {f["verdict"] for f in out["findings"]}
    assert "HEAD_REPORTED_SUPERSEDED" in verdicts
    assert out["head_checks"] and out["head_checks"][0]["is_chain_head"] is True


def test_a_head_with_the_correct_sentence_is_clean_but_still_counted(oracle):
    """The head check must RUN on a correct head, not only on a broken one --
    otherwise head coverage would be indistinguishable from head absence."""
    pages = {"v9.card.yaml": _page(
        "V9",
        incoming=[_edge("supersedes", "supersedes", from_id="V8", to_id="V9")],
        chain=[{"card": {"doc_id": "V9"}, "is_head": True}],
    )}
    out = oracle.evaluate(_Client(pages), ["v9.card.yaml"])
    assert out["findings"] == []
    assert len(out["head_checks"]) == 1


def test_an_unknown_relation_is_a_finding_not_a_silent_skip(oracle):
    pages = {"r.card.yaml": _page("B", outgoing=[_edge("invented_relation", "whatever")])}
    out = oracle.evaluate(_Client(pages), ["r.card.yaml"])
    assert [f["verdict"] for f in out["findings"]] == ["UNKNOWN_RELATION"]


def test_a_sentence_matching_neither_end_is_MISMATCH(oracle):
    pages = {"r.card.yaml": _page("B", outgoing=[_edge("cites", "refers vaguely to")])}
    out = oracle.evaluate(_Client(pages), ["r.card.yaml"])
    assert [f["verdict"] for f in out["findings"]] == ["MISMATCH"]


def test_a_page_that_will_not_render_is_a_finding(oracle):
    out = oracle.evaluate(_Client({}), ["missing.card.yaml"])
    assert [f["verdict"] for f in out["findings"]] == ["PAGE_ERROR"]
    assert out["pages_rendered"] == 0


def test_the_expectations_are_not_imported_from_the_product(oracle):
    """The independence that makes this an oracle. If these are ever sourced from
    explorer.models, the oracle can no longer disagree with the product and the
    W5 tautology has simply been relocated."""
    source = open(ORACLE, encoding="utf-8").read()
    assert "from explorer.models import" not in source
    assert "RELATION_LABELS" not in source.split("THE INDEPENDENCE")[1].split('"""')[1]
    assert oracle.EXPECTED_SENTENCES["supersedes"] == ("is superseded by", "supersedes")
    assert oracle.EXPECTED_SENTENCES["campaign_child"] == ("has campaign child", "is campaign child of")
