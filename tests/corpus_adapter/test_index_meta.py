"""(b) index_meta() carries the ARCHITECTURE.md section 3 IndexMeta keys with
live counts > 0 on the live corpus."""
from __future__ import annotations


def test_index_meta_keys_and_live_counts(live_adapter):
    meta = live_adapter.index_meta()

    assert meta.db_path == live_adapter.db_path
    assert meta.db_bytes > 0
    assert meta.db_mtime_utc

    expected_meta_keys = {
        "index_schema_version", "librarian_version", "current_nc_version",
        "last_full_reindex_utc", "corpus_card_count", "corpus_cards_sha",
        "fts_docs_count", "edges_count", "id_aliases_count",
    }
    assert expected_meta_keys <= set(meta.meta.keys())

    expected_count_keys = {"cards", "fts_docs", "edges", "id_aliases", "edges_unresolved"}
    assert expected_count_keys == set(meta.live_counts.keys())
    for key in ("cards", "fts_docs", "edges", "id_aliases"):
        assert meta.live_counts[key] > 0, f"live_counts[{key!r}] should be > 0 on the live corpus"

    assert meta.non_authoritative_notice
