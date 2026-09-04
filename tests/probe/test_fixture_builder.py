"""Tests for fixtures/build_fixture_index.py (ARCHITECTURE.md section 4.8; task B2).

Builds the fixture index into tmp_path (never fixtures/fixture_index.db, so the
committed fixture corpus is read-only from these tests) and asserts the shapes
the fixture was hand-crafted to exercise: card count parity with docs_archive
excluded, docs_archive absent from cards/fts_docs, the amendment sharing its
parent's doc_id, the supersedes edge, the unresolved cites edge, and the
"quartz lattice lantern" lexical hit at its recorded line. A final pair of
tests proves the db-path refusal runs BEFORE any write.

Read-only queries here go through RHACO_corpus_index.connect(tmp_db) + plain
SELECTs on the FIXTURE db only -- never the live index. This file never names
any of the five index-writing functions the build's L1 gate greps for (O2);
building the index is entirely delegated to fixtures/build_fixture_index.py's
own build(), the one allowlisted caller.
"""
from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

import pytest

from explorer.config import RHACO_PATH_ENTRIES

# Explicit sys.path setup (mirrors fixtures/build_fixture_index.py) so the two
# imports below do not depend on being written in a particular order.
for _entry in RHACO_PATH_ENTRIES:
    if _entry not in sys.path:
        sys.path.insert(0, _entry)

import RHACO_corpus_index  # noqa: E402

from fixtures.build_fixture_index import build  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_ROOT = REPO_ROOT / "fixtures" / "corpus"

# Known facts about the hand-crafted fixture corpus (docs/rounds/R01_probe.report.md
# carries the full inventory table); each is exercised by exactly one assertion below.
AMENDMENT_DOC_ID = "RHACO-HND-20260115-003"
REF_SUPERSEDED_ID = "RHACO_Fixture_Reference_v1_0"
REF_HEAD_ID = "RHACO_Fixture_Reference_v1_1"
UNRESOLVED_TARGET = "RHACO-ANL-20260101-099"
QUARTZ_PHRASE = "quartz lattice lantern"
QUARTZ_DOC_ID = "RHACO-ANL-20260115-002"
QUARTZ_LINE_NO = 15


def _expected_card_count_outside_docs_archive() -> int:
    return sum(
        1 for p in DOCS_ROOT.rglob("*.card.yaml")
        if "docs_archive" not in p.relative_to(DOCS_ROOT).parts
    )


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


@pytest.fixture(scope="module")
def built_summary(tmp_path_factory) -> dict:
    tmp_path = tmp_path_factory.mktemp("fixture_index")
    db_path = tmp_path / "fixture_index.db"
    return build(str(DOCS_ROOT), str(db_path))


@pytest.fixture(scope="module")
def conn(built_summary):
    connection = RHACO_corpus_index.connect(built_summary["db_path"])
    try:
        yield connection
    finally:
        connection.close()


def test_docs_root_exists():
    # Sanity precondition -- if this fails every other test's failure is noise.
    assert DOCS_ROOT.is_dir()
    assert (DOCS_ROOT / "docs_archive").is_dir()


def test_cards_count_matches_fixture_cards_outside_docs_archive(built_summary, conn):
    expected = _expected_card_count_outside_docs_archive()
    assert expected > 0
    live = conn.execute("SELECT count(*) FROM cards").fetchone()[0]
    assert live == expected == built_summary["cards"]


def test_docs_archive_document_absent_from_cards(conn):
    row = conn.execute(
        "SELECT count(*) FROM cards WHERE yaml_path LIKE ?", ("%docs_archive%",)
    ).fetchone()
    assert row[0] == 0


def test_docs_archive_document_absent_from_fts_docs(conn):
    row = conn.execute(
        "SELECT count(*) FROM fts_docs WHERE path LIKE ?", ("%docs_archive%",)
    ).fetchone()
    assert row[0] == 0


def test_amendment_shares_parent_doc_id_two_card_rows(conn):
    rows = conn.execute(
        "SELECT doc_filename FROM cards WHERE doc_id = ? ORDER BY doc_filename",
        (AMENDMENT_DOC_ID,),
    ).fetchall()
    filenames = [r[0] for r in rows]
    assert len(filenames) == 2, filenames
    assert any("Amendment_A1" in f for f in filenames)
    assert any("Amendment_A1" not in f for f in filenames)


def test_supersedes_edge_v1_0_to_v1_1(conn):
    rows = conn.execute(
        "SELECT resolved FROM edges WHERE relation='supersedes' AND from_id=? AND to_id=?",
        (REF_SUPERSEDED_ID, REF_HEAD_ID),
    ).fetchall()
    assert len(rows) == 1
    assert rows[0][0] == 1


def test_unresolved_cites_edge_exists(conn):
    rows = conn.execute(
        "SELECT from_id, to_id FROM edges WHERE relation='cites' AND resolved=0"
    ).fetchall()
    assert (AMENDMENT_DOC_ID, UNRESOLVED_TARGET) in rows


def test_quartz_lattice_lantern_lexical_hit(built_summary):
    result = RHACO_corpus_index.search_fts(QUARTZ_PHRASE, db_path=built_summary["db_path"])
    assert result["total_matched"] == 1
    match = result["matches"][0]
    assert match["doc_id"] == QUARTZ_DOC_ID
    assert match["line_no"] == QUARTZ_LINE_NO
    assert QUARTZ_PHRASE in match["line"]


def test_build_refuses_default_db_before_any_write(tmp_path):
    default_db = RHACO_corpus_index.DEFAULT_DB
    assert os.path.isfile(default_db), "the live index must exist for this test to be meaningful"
    before = _sha256_file(default_db)

    with pytest.raises(ValueError):
        build(str(DOCS_ROOT), default_db)

    after = _sha256_file(default_db)
    assert before == after, "the live default index db must be byte-identical after a refused build()"


def test_build_refuses_path_under_rhaco_tree_before_any_write(tmp_path):
    forbidden = os.path.join(r"C:\RHACO\index", "b2_probe_refusal_should_not_exist.db")
    assert not os.path.exists(forbidden)

    with pytest.raises(ValueError):
        build(str(DOCS_ROOT), forbidden)

    assert not os.path.exists(forbidden), "build() must not create any file under a RHACO tree"


def test_build_refuses_physical_spelling_of_rhaco_tree_before_any_write(tmp_path):
    forbidden = os.path.join(r"C:\highsierralabs\RHACO\index", "b2_probe_refusal_should_not_exist.db")
    assert not os.path.exists(forbidden)

    with pytest.raises(ValueError):
        build(str(DOCS_ROOT), forbidden)

    assert not os.path.exists(forbidden), "build() must not create any file under the physical RHACO tree spelling"
