"""Shared fixtures for tests/reader (RHACO-HND-20260903-001 B6).

The fixture index is built once per test session into a tmp_path_factory
directory via `fixtures.build_fixture_index.build` (ARCHITECTURE.md A12,
conventions block); the committed fixture corpus at fixtures/corpus/ (builder
probe's owned path) is read but never copied or modified. Fault-flavoured
clients build a second Settings with `fault=...` against the SAME fixture db
path -- the fault is honoured because that path lies outside both RHACO trees
(explorer/faults.py).

The live-index smoke fixture and its before/after corpus_cards_sha + mtime
guard mirror tests/corpus_adapter/conftest.py's approach (dispatch B6
conventions block: "copy that fixture's approach into your own conftest; do
not import theirs") without importing that file.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from explorer.app import ADAPTER_ABSENT, create_app
from explorer.config import RHACO_PATH_ENTRIES, Settings
from explorer.corpus_adapter.adapter import CorpusAdapter

for _entry in RHACO_PATH_ENTRIES:
    if _entry not in sys.path:
        sys.path.insert(0, _entry)

from fixtures.build_fixture_index import build  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DOCS_ROOT = str(REPO_ROOT / "fixtures" / "corpus")

# Live-corpus identifiers (this build's own dispatch hand and its amendment;
# verified on disk at C:\RHACO\docs\handoffs\ -- mirrors
# tests/corpus_adapter/conftest.py's HAND_* constants).
LIVE_HAND_DOC_ID = "RHACO-HND-20260903-001"
LIVE_HAND_CARD_REF = "handoffs/RHACO-HND-20260903-001_Corpus_Explorer_Autonomous_Build_Dispatch.card.yaml"


@pytest.fixture(scope="session")
def fixture_db_path(tmp_path_factory) -> str:
    tmp_path = tmp_path_factory.mktemp("reader_fixture_index")
    db_path = tmp_path / "fixture_index.db"
    build(FIXTURE_DOCS_ROOT, str(db_path))
    return str(db_path)


@pytest.fixture(scope="session")
def fixture_settings(fixture_db_path: str) -> Settings:
    return Settings(db_path=fixture_db_path, docs_root=FIXTURE_DOCS_ROOT)


@pytest.fixture()
def client(fixture_settings: Settings) -> TestClient:
    return TestClient(create_app(fixture_settings))


def _fault_client(fixture_db_path: str, fault: str) -> TestClient:
    settings = Settings(db_path=fixture_db_path, docs_root=FIXTURE_DOCS_ROOT, fault=fault)
    return TestClient(create_app(settings))


@pytest.fixture()
def stale_card_client(fixture_db_path: str) -> TestClient:
    return _fault_client(fixture_db_path, "stale_card")


@pytest.fixture()
def broken_jump_client(fixture_db_path: str) -> TestClient:
    return _fault_client(fixture_db_path, "broken_jump")


@pytest.fixture()
def adapter_absent_client(fixture_settings: Settings) -> TestClient:
    app = create_app(fixture_settings)
    app.state.adapter = ADAPTER_ABSENT
    return TestClient(app)


@pytest.fixture(scope="session")
def live_client() -> TestClient:
    return TestClient(create_app(Settings()))


def _fingerprint(adapter: CorpusAdapter) -> tuple[str, str | None, float]:
    meta = adapter.index_meta()
    return adapter.db_path, meta.meta.get("corpus_cards_sha"), os.path.getmtime(adapter.db_path)


@pytest.fixture(scope="session", autouse=True)
def _live_db_unchanged():
    before_adapter = CorpusAdapter(Settings())
    db_path, sha_before, mtime_before = _fingerprint(before_adapter)
    print(f"\n[criterion-6] live db BEFORE: path={db_path} corpus_cards_sha={sha_before} mtime={mtime_before}")
    yield
    # A fresh CorpusAdapter, not `before_adapter` itself: index_meta() caches
    # for <= 5 s (ARCHITECTURE.md A9), and a fast test session can finish
    # inside that window -- a new instance always re-queries the live db.
    after_adapter = CorpusAdapter(Settings())
    db_path_after, sha_after, mtime_after = _fingerprint(after_adapter)
    print(f"[criterion-6] live db AFTER:  path={db_path_after} corpus_cards_sha={sha_after} mtime={mtime_after}")
    assert db_path_after == db_path
    assert sha_after == sha_before, "corpus_cards_sha changed during the test session"
    assert mtime_after == mtime_before, "corpus_index.db mtime changed during the test session"
