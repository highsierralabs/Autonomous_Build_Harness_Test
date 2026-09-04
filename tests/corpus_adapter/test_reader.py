"""(j) read_document(the hand card) returns headings with slugs;
is_under_docs_root rejects an out-of-tree path and a `..` escape."""
from __future__ import annotations

from explorer.corpus_adapter import paths


def test_read_document_returns_headings_with_slugs(live_adapter, hand_card_ref):
    hand = live_adapter.card(hand_card_ref)
    assert hand is not None

    doc = live_adapter.read_document(hand)

    assert doc.kind == "markdown"
    assert doc.renderable is True
    assert doc.sha256 and len(doc.sha256) == 64
    assert doc.lines
    assert doc.headings, "expected at least one heading in the hand document"

    seen_slugs = set()
    for h in doc.headings:
        assert 1 <= h.level <= 6
        assert h.line_no >= 1
        assert h.slug
        assert h.slug == h.slug.lower()
        assert " " not in h.slug
        assert h.slug not in seen_slugs, f"duplicate slug {h.slug!r} not disambiguated"
        seen_slugs.add(h.slug)


def test_is_under_docs_root_rejects_data_tree_and_dotdot_escape(live_adapter):
    assert paths.is_under_docs_root(r"C:\RHACO\data\x.md", live_adapter.docs_root) is False

    escape_path = live_adapter.docs_root + r"\..\data\x.md"
    assert paths.is_under_docs_root(escape_path, live_adapter.docs_root) is False

    assert paths.is_under_docs_root(live_adapter.docs_root, live_adapter.docs_root) is True
