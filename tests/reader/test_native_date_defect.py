"""End-to-end regression for the card-YAML native-type defect (task B11).

Every card in `fixtures/corpus/` quotes its `date:`/`last_human_review:`
scalars (`date: "2026-01-15"`), so `yaml.safe_load` always returns a plain
`str` for them there and the committed fixture corpus can never, by itself,
produce the native `datetime.date` that broke the reader on the live corpus
(docs/rounds/R05_reader.report.md's "why no test caught it"). This module
closes that fixture-representativeness gap directly: it copies the whole
fixture corpus into `tmp_path`, rewrites ONE card's two date scalars to the
UNQUOTED form the real failing production card uses, builds a fresh index
over that copy (`fixtures/build_fixture_index.build`), and drives both
`/doc/...` and `/api/doc/...` against it -- never touching the committed
`fixtures/corpus/` tree itself (owned by builder `probe`, out of this round's
write scope; working rule 1 / task B11 item 3).
"""
from __future__ import annotations

import shutil
from pathlib import Path

from fastapi.testclient import TestClient

from explorer.app import create_app
from explorer.config import Settings
from fixtures.build_fixture_index import build

# Computed independently rather than imported from conftest.py (no
# `tests/reader/__init__.py` package boundary exists for a relative import to
# resolve against; mirrors this repo's own "written independently, not
# imported" precedent for cross-file fixture paths).
_REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DOCS_ROOT = str(_REPO_ROOT / "fixtures" / "corpus")

CARD_REF = "reports/RHACO-ANL-20260115-002_Fixture_Analysis.card.yaml"
ISO_DATE = "2026-01-15"


def _build_unquoted_date_client(tmp_path: Path) -> TestClient:
    docs_root = tmp_path / "corpus"
    shutil.copytree(FIXTURE_DOCS_ROOT, docs_root)

    card_path = docs_root / CARD_REF
    text = card_path.read_text(encoding="utf-8")
    unquoted = text.replace('date: "2026-01-15"', "date: 2026-01-15")
    assert unquoted != text, "the quoted date: line was not found to rewrite"
    unquoted = unquoted.replace('last_human_review: "2026-01-15"', "last_human_review: 2026-01-15")
    assert 'date: "2026-01-15"' not in unquoted
    assert 'last_human_review: "2026-01-15"' not in unquoted
    card_path.write_text(unquoted, encoding="utf-8", newline="\n")

    db_path = tmp_path / "unquoted_date_index.db"
    build(str(docs_root), str(db_path))
    settings = Settings(db_path=str(db_path), docs_root=str(docs_root))
    return TestClient(create_app(settings))


def test_reader_page_returns_200_and_shows_iso_text_for_unquoted_date(tmp_path):
    client = _build_unquoted_date_client(tmp_path)
    resp = client.get(f"/doc/{CARD_REF}")
    assert resp.status_code == 200
    body = resp.text

    assert 'data-selected-doc-id="RHACO-ANL-20260115-002"' in body
    # Card panel (Identity section): the exact file characters, no repr leak.
    assert "<dt>Date</dt><dd>2026-01-15</dd>" in body
    # "Parsed card fields (complete)" <pre>...tojson...</pre> dump: same text.
    assert '"date": "2026-01-15"' in body
    assert '"last_human_review": "2026-01-15"' in body
    assert "datetime.date" not in body
    assert "not JSON serializable" not in body
    # item 2: no false index-mismatch from comparing a native date to a string.
    assert 'data-card-index-mismatch=""' in body
    # O19/O28: the raw source block is byte-for-byte the tmp copy's own text,
    # unquoted date and all -- never reformatted by this round's fix.
    assert "date: 2026-01-15" in body


def test_api_doc_returns_200_and_agrees_with_the_page(tmp_path):
    client = _build_unquoted_date_client(tmp_path)
    resp = client.get(f"/api/doc/{CARD_REF}")
    assert resp.status_code == 200
    payload = resp.json()

    assert payload["card_panel"]["date"] == ISO_DATE
    assert payload["card_panel"]["last_human_review"] == ISO_DATE
    assert payload["card_parsed"]["identity"]["date"] == ISO_DATE
    assert payload["card_parsed"]["identity"]["last_human_review"] == ISO_DATE
    assert payload["index_mismatch_fields"] == []
