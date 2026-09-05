"""Shared fixtures for tests/web (RHACO-HND-20260903-001 S6-B9).

Mirrors tests/search/conftest.py's convention: the fixture index is built
once per test session into a tmp_path_factory directory via
`fixtures.build_fixture_index.build`, never into fixtures/fixture_index.db,
so the committed fixture corpus stays read-only from these tests. Every test
in this package renders real merged pages (catalog, search, reader,
diagnostics) through explorer.app.create_app + TestClient -- no test in this
package spawns a server process (ARCHITECTURE.md A18).

The one exception is tests/web/test_live_smoke.py, which reads the LIVE
corpus index through explorer.corpus_adapter.CorpusAdapter (the sole
sanctioned path, per this strand's dispatch working rule 2) and asserts
shape only. `live_db_unchanged` copies the corpus_cards_sha + mtime
before/after guard from tests/corpus_adapter/conftest.py (not imported from
there -- each test package owns its own conftest, matching tests/search's
precedent) so that smoke test can prove it never wrote to the live index.
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
    tmp_dir = tmp_path_factory.mktemp("web_fixture_index")
    db_path = tmp_dir / "fixture_index.db"
    build(fixture_docs_root, str(db_path))
    return str(db_path)


@pytest.fixture(scope="session")
def fixture_settings(fixture_db_path: str, fixture_docs_root: str) -> Settings:
    return Settings(db_path=fixture_db_path, docs_root=fixture_docs_root)


@pytest.fixture()
def fixture_client(fixture_settings: Settings) -> TestClient:
    app = create_app(fixture_settings)
    return TestClient(app)


# -- live-index smoke-test guard (see module docstring) ---------------------


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
