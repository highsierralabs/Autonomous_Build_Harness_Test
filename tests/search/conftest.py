"""Shared fixtures for tests/search (RHACO-HND-20260903-001 B5).

The fixture index (fixtures/corpus/) is built once per test session into a
tmp_path_factory directory via `fixtures.build_fixture_index.build` (never
into fixtures/fixture_index.db, so the committed fixture corpus stays
read-only from these tests) -- the wave-2 convention from ARCHITECTURE.md
4.8 / this dispatch's "Conventions every wave-2 page follows". The fixture
carries NO vector set (docs/rounds/R01_probe.report.md), so `search_hybrid`
and `search_graph` against it are degraded by construction; that degraded
state is exercised directly against this fixture, and a hand-written fake
adapter (tests/search/fake_adapter.py) covers the vector-available path the
fixture cannot produce.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from explorer.app import create_app
from explorer.config import Settings
from explorer.corpus_adapter.adapter import CorpusAdapter
from fixtures.build_fixture_index import build

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DOCS_ROOT = REPO_ROOT / "fixtures" / "corpus"


@pytest.fixture(scope="session")
def fixture_docs_root() -> str:
    return str(FIXTURE_DOCS_ROOT)


@pytest.fixture(scope="session")
def fixture_db_path(tmp_path_factory, fixture_docs_root: str) -> str:
    tmp_dir = tmp_path_factory.mktemp("search_fixture_index")
    db_path = tmp_dir / "fixture_index.db"
    build(fixture_docs_root, str(db_path))
    return str(db_path)


@pytest.fixture(scope="session")
def fixture_settings(fixture_db_path: str, fixture_docs_root: str) -> Settings:
    return Settings(db_path=fixture_db_path, docs_root=fixture_docs_root)


@pytest.fixture()
def fixture_adapter(fixture_settings: Settings) -> CorpusAdapter:
    return CorpusAdapter(fixture_settings)


@pytest.fixture()
def fixture_client(fixture_settings: Settings) -> TestClient:
    app = create_app(fixture_settings)
    return TestClient(app)


def _client_with_adapter(settings: Settings, adapter) -> TestClient:
    app = create_app(settings)
    app.state.adapter = adapter
    return TestClient(app)


@pytest.fixture()
def client_with_adapter(fixture_settings: Settings):
    def _make(adapter) -> TestClient:
        return _client_with_adapter(fixture_settings, adapter)

    return _make


@pytest.fixture()
def client_without_adapter(fixture_settings: Settings) -> TestClient:
    from explorer.app import ADAPTER_ABSENT

    app = create_app(fixture_settings)
    app.state.adapter = ADAPTER_ABSENT
    return TestClient(app)


# -- live-index smoke-test guard (copies tests/corpus_adapter/conftest.py's
# before/after corpus_cards_sha + mtime approach; not imported from there,
# not autouse -- only the one live-index smoke test in test_live_smoke.py
# depends on it, so the rest of this session's tests never touch the live
# index at all). --------------------------------------------------------------


def _fingerprint(adapter: CorpusAdapter) -> tuple[str, str | None, float]:
    meta = adapter.index_meta()
    return adapter.db_path, meta.meta.get("corpus_cards_sha"), os.path.getmtime(adapter.db_path)


@pytest.fixture()
def live_db_unchanged():
    before_adapter = CorpusAdapter(Settings())
    before = _fingerprint(before_adapter)
    print(f"\n[criterion-6] live db BEFORE: path={before[0]} corpus_cards_sha={before[1]} mtime={before[2]}")
    yield
    after_adapter = CorpusAdapter(Settings())
    after = _fingerprint(after_adapter)
    print(f"[criterion-6] live db AFTER:  path={after[0]} corpus_cards_sha={after[1]} mtime={after[2]}")
    assert after[0] == before[0]
    assert after[1] == before[1], "corpus_cards_sha changed during the test"
    assert after[2] == before[2], "corpus_index.db mtime changed during the test"
