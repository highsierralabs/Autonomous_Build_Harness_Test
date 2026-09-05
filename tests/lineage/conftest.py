"""Shared fixtures for tests/lineage (RHACO-HND-20260903-001 section 2 I,
strand S6-B8; dispatch "Conventions every wave-2 page follows").

The fixture index (fixtures/corpus/, builder probe's owned, read-only tree)
is built once per test session into a tmp_path_factory directory via
`fixtures.build_fixture_index.build` -- never into fixtures/fixture_index.db.
Fault-flavoured clients build a second Settings with `fault=...` against the
SAME fixture db path; the fault is honoured because that path lies outside
both RHACO trees (explorer/faults.py).

The live-index smoke fixture and its before/after corpus_cards_sha + mtime
guard mirror tests/corpus_adapter/conftest.py's approach (copied, not
imported, per the dispatch's conventions block).
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

# Fixture card_refs (docs/rounds/R01_probe.report.md fixture inventory table).
CMP_CARD_REF = "reports/RHACO-CMP-20260115-001_Fixture_Campaign.card.yaml"
ANL_CARD_REF = "reports/RHACO-ANL-20260115-002_Fixture_Analysis.card.yaml"
HND_CARD_REF = "handoffs/RHACO-HND-20260115-003_Fixture_Handoff.card.yaml"
AMENDMENT_CARD_REF = "handoffs/RHACO-HND-20260115-003_Fixture_Handoff_Amendment_A1.card.yaml"
REF_V1_0_CARD_REF = "reference/RHACO_Fixture_Reference_v1_0.card.yaml"
REF_V1_1_CARD_REF = "reference/RHACO_Fixture_Reference_v1_1.card.yaml"
EVT_CARD_REF = "reports/RHACO-EVT-20260115-004_Fixture_Event_E000777.card.yaml"
DOCS_ARCHIVE_CARD_REF = "docs_archive/RHACO-OBS-20260101-001_Fixture_Archived.card.yaml"

CMP_DOC_ID = "RHACO-CMP-20260115-001"
ANL_DOC_ID = "RHACO-ANL-20260115-002"
HND_DOC_ID = "RHACO-HND-20260115-003"
AMENDMENT_STEM = "RHACO-HND-20260115-003_Fixture_Handoff_Amendment_A1"
UNRESOLVED_TARGET = "RHACO-ANL-20260101-099"
REF_V1_0_DOC_ID = "RHACO_Fixture_Reference_v1_0"
REF_V1_1_DOC_ID = "RHACO_Fixture_Reference_v1_1"

# Live-corpus identifiers (this build's own dispatch campaign; verified via
# the adapter, session 6, strand S6-B8 -- see this round's report Evidence).
LIVE_CMP_CARD_REF = "reports/RHACO-CMP-20260903-001_Corpus_Explorer_Autonomous_Build_Harness.card.yaml"
LIVE_CMP_DOC_ID = "RHACO-CMP-20260903-001"
LIVE_CMP_CHILD_DOC_ID = "RHACO-HND-20260903-001"


@pytest.fixture(scope="session")
def fixture_db_path(tmp_path_factory) -> str:
    tmp_path = tmp_path_factory.mktemp("lineage_fixture_index")
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
def reverse_edges_client(fixture_db_path: str) -> TestClient:
    return _fault_client(fixture_db_path, "reverse_edges")


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
