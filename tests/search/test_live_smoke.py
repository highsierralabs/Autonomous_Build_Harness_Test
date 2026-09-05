"""Read-only smoke test against the LIVE index (Settings() defaults), task B5
deliverable 5. Asserts shape only (HTTP 200, one non-empty result) -- guarded
by the live_db_unchanged fixture's before/after corpus_cards_sha + mtime
check (tests/search/conftest.py, copied from tests/corpus_adapter/conftest.py's
approach, not imported from it).

RHACO-CMP-20260903-001 is this build's own dispatching campaign, verified
present on the live corpus by the corpus_adapter builder (docs/rounds/
R01_corpus_adapter.report.md) and reused here as a known-good identifier.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from explorer.app import create_app
from explorer.config import Settings

CMP_DOC_ID = "RHACO-CMP-20260903-001"


def test_live_identifier_search_returns_one_result(live_db_unchanged):
    del live_db_unchanged  # fixture only for its before/after guard
    app = create_app(Settings())
    client = TestClient(app)

    resp = client.get("/search", params={"q": CMP_DOC_ID, "mode": "identifier"})
    assert resp.status_code == 200
    body = resp.text
    assert f'data-doc-id="{CMP_DOC_ID}"' in body
    assert "no card row in the index" not in body

    data = client.get("/api/search", params={"q": CMP_DOC_ID, "mode": "identifier"}).json()
    assert data["mode_effective"] == "identifier"
    assert len(data["identifier_rows"]) == 1
    assert data["identifier_rows"][0]["doc_id"] == CMP_DOC_ID
    assert data["identifier_rows"][0]["cards"], "expected at least one card row for the live CMP id"
