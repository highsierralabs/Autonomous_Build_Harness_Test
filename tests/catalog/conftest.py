"""Shared fixtures for tests/catalog (task B4 item 4).

Builds the fixture index once per test session into tmp_path_factory (never
`fixtures/fixture_index.db` -- the committed fixture corpus stays read-only
from these tests) via `fixtures.build_fixture_index.build`, then constructs
one `explorer.app.create_app(Settings(db_path=..., docs_root=...))` shared by
every test in this package and driven with `fastapi.testclient.TestClient`
(ARCHITECTURE.md A18: no test launches a server process).

The fixture inventory (7 cards outside docs_archive/) is documented in
docs/rounds/R01_probe.report.md; the exact catalog-shaped facts asserted in
this package's tests were independently re-derived from a fresh fixture
build before being written into any test (not merely copied from that
report), and are also covered by test_catalog_fixture_facts_match_report
below.

The live-index guard mirrors tests/corpus_adapter/conftest.py's approach
(the module's own `corpus_cards_sha` meta value plus the db file's mtime,
read only through the adapter's sanctioned `connect()` path) -- copied here,
not imported, per task B4's testing conventions.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from explorer.app import ADAPTER_ABSENT, create_app
from explorer.config import Settings
from explorer.corpus_adapter.adapter import CorpusAdapter
from fixtures.build_fixture_index import build

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DOCS_ROOT = str(REPO_ROOT / "fixtures" / "corpus")


@pytest.fixture(scope="session")
def fixture_docs_root() -> str:
    return FIXTURE_DOCS_ROOT


@pytest.fixture(scope="session")
def fixture_db_path(tmp_path_factory, fixture_docs_root: str) -> str:
    db_path = str(tmp_path_factory.mktemp("catalog_fixture_index") / "fixture_index.db")
    build(fixture_docs_root, db_path, force=True)
    return db_path


@pytest.fixture(scope="session")
def fixture_settings(fixture_db_path: str, fixture_docs_root: str) -> Settings:
    return Settings(db_path=fixture_db_path, docs_root=fixture_docs_root, page_size=50)


@pytest.fixture(scope="session")
def fixture_app(fixture_settings: Settings):
    return create_app(fixture_settings)


@pytest.fixture()
def client(fixture_app) -> TestClient:
    return TestClient(fixture_app)


@pytest.fixture()
def client_adapter_absent(fixture_settings: Settings) -> TestClient:
    """A separate app instance with app.state.adapter set to the sentinel
    (explorer.app.ADAPTER_ABSENT) so the 503 path is exercised explicitly,
    without disturbing the session-scoped fixture_app other tests share."""
    app = create_app(fixture_settings)
    app.state.adapter = ADAPTER_ABSENT
    return TestClient(app)


# -- live-index no-mutation guard (copied approach, not import, from
# tests/corpus_adapter/conftest.py -- task B4 conventions paragraph) ---------

def _fingerprint(adapter: CorpusAdapter) -> tuple[str, str | None, float]:
    meta = adapter.index_meta()
    return adapter.db_path, meta.meta.get("corpus_cards_sha"), os.path.getmtime(adapter.db_path)


@pytest.fixture(scope="session", autouse=True)
def _live_db_unchanged():
    live_adapter = CorpusAdapter(Settings())
    db_path, sha_before, mtime_before = _fingerprint(live_adapter)
    print(f"\n[criterion-6] live db BEFORE: path={db_path} corpus_cards_sha={sha_before} mtime={mtime_before}")
    yield
    # A fresh CorpusAdapter, not `live_adapter` itself: index_meta() caches for
    # <= 5 s (ARCHITECTURE.md A9), and a fast test session can finish inside
    # that window, which would make the "after" read an echo of the cached
    # "before" value instead of a genuine independent re-read.
    after_adapter = CorpusAdapter(Settings())
    db_path_after, sha_after, mtime_after = _fingerprint(after_adapter)
    print(f"[criterion-6] live db AFTER:  path={db_path_after} corpus_cards_sha={sha_after} mtime={mtime_after}")
    assert db_path_after == db_path
    assert sha_after == sha_before, "corpus_cards_sha changed during the test session"
    assert mtime_after == mtime_before, "corpus_index.db mtime changed during the test session"
