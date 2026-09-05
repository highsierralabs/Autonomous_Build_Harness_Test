"""Live-index smoke test for explorer/web (dispatch task B9 item 4, fifth
bullet): asserts shape only against the real, running RHACO corpus index --
`/` returns 200, non-empty, with the shell present -- guarded by the
corpus_cards_sha + mtime before/after check so the test proves it read the
live db and never wrote to it (device-safety prohibition; CONSTRAINTS.md
O10). This is the only test in tests/web that touches the live index; every
other test in this package runs entirely against the fixture index built
into tmp_path (conftest.fixture_client)."""
from __future__ import annotations

from fastapi.testclient import TestClient

from explorer.app import create_app
from explorer.config import Settings


def test_catalog_home_against_the_live_index(live_db_unchanged):
    app = create_app(Settings())
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    assert len(resp.text) > 0
    assert 'class="skip-link"' in resp.text
    assert "RHACO Corpus Explorer" in resp.text
