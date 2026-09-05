"""Error paths (task B8 deliverable 2 / 5): an unknown card_ref, a
docs_archive card_ref (never indexed -- CONSTRAINTS.md O24), and a `..`
traversal all 404 on both the page and the API; adapter-absent is 503 on
both, via the ADAPTER_ABSENT sentinel (ARCHITECTURE.md A20)."""
from __future__ import annotations

from tests.lineage.conftest import CMP_CARD_REF, DOCS_ARCHIVE_CARD_REF


def test_unknown_card_ref_404_page_and_api(client):
    resp = client.get("/lineage/reports/RHACO-NOPE-99999999-999_Nothing.card.yaml")
    assert resp.status_code == 404
    assert "no card at" in resp.text

    resp_api = client.get("/api/lineage/reports/RHACO-NOPE-99999999-999_Nothing.card.yaml")
    assert resp_api.status_code == 404
    assert resp_api.json() == {"error": "card not found"}


def test_docs_archive_card_ref_404(client):
    """docs_archive/ is walk-excluded from the index (CONSTRAINTS.md O24) --
    `adapter.card()` finds no row for it, so build_view already returns None
    without any lineage-specific special-casing."""
    resp = client.get(f"/lineage/{DOCS_ARCHIVE_CARD_REF}")
    assert resp.status_code == 404

    resp_api = client.get(f"/api/lineage/{DOCS_ARCHIVE_CARD_REF}")
    assert resp_api.status_code == 404


def test_dot_dot_traversal_404(client):
    """The dots are percent-encoded (%2e%2e) so the HTTP client's own URL
    normalizer does not collapse the `..` segment before the request is even
    sent (verified empirically: an unencoded `../../` is resolved client-side
    and never reaches the server as a literal traversal at all -- see this
    round's report, Evidence). Percent-encoded, the literal `..` segment
    reaches `explorer.corpus_adapter.paths.abs_path_from_rel_ref`, which
    rejects it before any filesystem or index access."""
    traversal_ref = f"reports/%2e%2e/{CMP_CARD_REF}"
    resp = client.get(f"/lineage/{traversal_ref}")
    assert resp.status_code == 404
    assert "no card at" in resp.text

    resp_api = client.get(f"/api/lineage/{traversal_ref}")
    assert resp_api.status_code == 404
    assert resp_api.json() == {"error": "card not found"}


def test_adapter_absent_503_page_and_api(adapter_absent_client):
    resp = adapter_absent_client.get(f"/lineage/{CMP_CARD_REF}")
    assert resp.status_code == 503
    assert "corpus_adapter not built" in resp.text

    resp_api = adapter_absent_client.get(f"/api/lineage/{CMP_CARD_REF}")
    assert resp_api.status_code == 503
    assert resp_api.json() == {"error": "corpus_adapter not built"}
