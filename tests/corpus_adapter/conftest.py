"""Shared fixtures for tests/corpus_adapter (RHACO-HND-20260903-001 B1).

Every test runs against the LIVE index, read-only. The db file itself is
touched only through RHACO_corpus_index.connect() -- via the adapter, the
sole importer (ARCHITECTURE.md section 2) -- so this conftest never opens
`corpus_index.db` directly and never imports RHACO_corpus_index itself. The
session-end no-mutation check (dispatch B1 criterion 6) therefore compares
the module's own `corpus_cards_sha` meta value (a real sha256 digest,
obtained through the adapter's `index_meta()`) plus the db file's mtime (a
filesystem-metadata read via os.stat, not a content read) rather than a raw
hash of the .db file's bytes.
"""
from __future__ import annotations

import os

import pytest

from explorer.config import Settings
from explorer.corpus_adapter.adapter import CorpusAdapter

# Identifiers known to be a shared-doc_id parent/amendment pair on the live
# corpus (RHACO-HND-20260903-001, this build's own dispatch hand and its
# Amendment A1) and the campaign that dispatches it -- verified on disk at
# C:\RHACO\docs\handoffs\ and C:\RHACO\docs\reports\ before writing these
# tests (see docs/rounds/R01_corpus_adapter.report.md, Evidence).
HAND_DOC_ID = "RHACO-HND-20260903-001"
HAND_CARD_REF = "handoffs/RHACO-HND-20260903-001_Corpus_Explorer_Autonomous_Build_Dispatch.card.yaml"
A1_CARD_REF = (
    "handoffs/RHACO-HND-20260903-001_Corpus_Explorer_Autonomous_Build_Dispatch"
    "_Amendment_A1_Cap_Rehome_And_Session_2_Findings.card.yaml"
)
CMP_DOC_ID = "RHACO-CMP-20260903-001"


@pytest.fixture(scope="session")
def live_adapter() -> CorpusAdapter:
    return CorpusAdapter(Settings())


@pytest.fixture(scope="session")
def hand_doc_id() -> str:
    return HAND_DOC_ID


@pytest.fixture(scope="session")
def hand_card_ref() -> str:
    return HAND_CARD_REF


@pytest.fixture(scope="session")
def a1_card_ref() -> str:
    return A1_CARD_REF


@pytest.fixture(scope="session")
def cmp_doc_id() -> str:
    return CMP_DOC_ID


def _fingerprint(adapter: CorpusAdapter) -> tuple[str, str | None, float]:
    meta = adapter.index_meta()
    return adapter.db_path, meta.meta.get("corpus_cards_sha"), os.path.getmtime(adapter.db_path)


@pytest.fixture(scope="session", autouse=True)
def _live_db_unchanged(live_adapter: CorpusAdapter):
    db_path, sha_before, mtime_before = _fingerprint(live_adapter)
    print(f"\n[criterion-6] live db BEFORE: path={db_path} corpus_cards_sha={sha_before} mtime={mtime_before}")
    yield
    # A fresh CorpusAdapter, not `live_adapter` itself: index_meta() caches for
    # <= 5 s (ARCHITECTURE.md A9), and a fast test session can finish inside
    # that window, which would make the "after" read an echo of the cached
    # "before" value instead of a genuine independent re-read. A new instance
    # has its own empty cache, so this always re-queries the live db through
    # the sanctioned connect() path.
    after_adapter = CorpusAdapter(Settings())
    db_path_after, sha_after, mtime_after = _fingerprint(after_adapter)
    print(f"[criterion-6] live db AFTER:  path={db_path_after} corpus_cards_sha={sha_after} mtime={mtime_after}")
    assert db_path_after == db_path
    assert sha_after == sha_before, "corpus_cards_sha changed during the test session"
    assert mtime_after == mtime_before, "corpus_index.db mtime changed during the test session"
