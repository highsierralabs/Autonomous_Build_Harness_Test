"""C2/C3 -- criterion-6 guard: no path in this package lets
RHACO_corpus_index.connect() create a missing database (CONSTRAINTS.md O10;
ARCHITECTURE.md 4.1/A9).

Round-1 checked `os.path.isfile` once in `__init__`; a live-index file
removed after a CorpusAdapter is constructed (an external reindex, a
misconfigured restart) was then re-created by the explorer the next time
something called `connect()`, because `RHACO_corpus_index.connect()` creates
the parent directory and the database file (and applies DDL) if absent. This
is a build write to the live index, forbidden by DISPATCH_PARAMETERS.md
items B/C and criterion 6. Round 2 (C2) put the guard on
`CorpusAdapter.connect()` itself -- the first two tests below show that
guard holds per call, and that it is a guard, not a break.

Round 3 (C3) closes a second, independent instance of the same hazard:
`explorer/corpus_adapter/availability.py`'s `probe()` calls
`rhaco_index.connect()` directly, not through `CorpusAdapter.connect()`, so
`vector_availability()` (and therefore `search_hybrid`/`search_graph`, which
call it first) had its own unguarded path to the RHACO module's `connect()`.
The last three tests below cover that fix: the hazard itself (through the
adapter's public `vector_availability()`), that the fix is a guard and not a
break against the live index, and that `probe()`'s own guard short-circuits
before `connect()` is ever reached rather than merely catching its failure
afterwards.
"""
from __future__ import annotations

import os

from explorer.config import Settings
from explorer.corpus_adapter import ConfigurationError, CorpusAdapter, availability


def test_connect_raises_after_db_removed_post_construction_and_creates_nothing(tmp_path):
    db_file = tmp_path / "live.db"
    db_file.write_bytes(b"")  # construction only needs os.path.isfile to see a file
    assert db_file.exists()

    adapter = CorpusAdapter(Settings(db_path=str(db_file)))
    assert adapter.db_path == str(db_file)

    os.remove(db_file)
    assert not db_file.exists()

    raised = False
    try:
        adapter.connect()
    except ConfigurationError:
        raised = True
    assert raised, "connect() must re-check os.path.isfile and raise ConfigurationError, not delegate"

    assert os.listdir(tmp_path) == [], (
        "connect() must never let RHACO_corpus_index.connect() create a database "
        "(or a -journal/-wal file) for a path that no longer exists (O10)"
    )


def test_connect_still_succeeds_when_db_file_exists(live_adapter):
    conn = live_adapter.connect()
    try:
        assert conn.execute("SELECT count(*) FROM cards").fetchone()[0] > 0
    finally:
        conn.close()


def test_vector_availability_reports_db_unavailable_and_creates_nothing_when_db_removed(tmp_path):
    """C3 hazard test. Before this round, `availability.probe()` called
    `rhaco_index.connect(db_path)` directly with no isfile guard, so this
    call sequence -- construct against a file, then remove it, then trigger
    a vector-availability probe -- would have let
    `RHACO_corpus_index.connect()` create a fresh, empty database at the
    now-missing path (and, on a real corpus_index.db, applied its DDL)."""
    db_file = tmp_path / "live.db"
    db_file.write_bytes(b"")  # construction only needs os.path.isfile to see a file
    assert db_file.exists()

    adapter = CorpusAdapter(Settings(db_path=str(db_file)))
    assert adapter.db_path == str(db_file)

    os.remove(db_file)
    assert not db_file.exists()

    result = adapter.vector_availability()

    assert result.available is False
    assert result.reason == "db_unavailable"
    assert os.listdir(tmp_path) == [], (
        "availability.probe() must never let RHACO_corpus_index.connect() create a "
        "database (or a -journal/-wal file) for a path that no longer exists (O10)"
    )


def test_vector_availability_against_live_index_is_read_only(live_adapter):
    """C3 guard-is-not-a-break test: vector_availability() through the
    adapter, against the real live index, read-only -- the O10 fix must not
    change vector_availability()'s behaviour for a database that actually
    exists, and must not mutate the live db in any observable way."""
    before_sha = live_adapter.index_meta().meta.get("corpus_cards_sha")
    before_mtime = os.path.getmtime(live_adapter.db_path)

    result = live_adapter.vector_availability()

    assert result.reason in {
        "ok",
        "disabled_by_env",
        "sqlite_vec_not_loaded",
        "vec_table_missing",
        "embedder_unreachable",
        "db_unavailable",
    }

    # A fresh adapter, not `live_adapter` itself: index_meta() caches for
    # <= 5 s (ARCHITECTURE.md A9), so re-reading through the same instance
    # inside that window would echo the cached "before" value instead of
    # genuinely re-querying the live db (same rationale as conftest.py's
    # session-scoped no-mutation fixture).
    after_sha = CorpusAdapter(Settings()).index_meta().meta.get("corpus_cards_sha")
    assert after_sha == before_sha, "corpus_cards_sha changed across a vector_availability() call"
    assert os.path.getmtime(live_adapter.db_path) == before_mtime, "corpus_index.db mtime changed"


def test_probe_short_circuits_before_connect_when_db_missing(tmp_path):
    """C3 short-circuit test: a hand-written fake `rhaco_index` whose
    `connect` raises if it is ever called proves the isfile guard runs
    *before* `connect()` is reached, not that it merely catches whatever
    `connect()` raises for a missing path afterwards."""

    class _ConnectMustNotBeCalled:
        VEC_DISABLE_ENV = "RHACO_CORPUS_DISABLE_VEC"
        CPU_FLOOR_TAG = "nomic-embed-text"

        @staticmethod
        def connect(db_path):
            raise AssertionError("connect must not be called")

    missing_db = tmp_path / "does_not_exist.db"
    assert not missing_db.exists()
    assert not os.environ.get(_ConnectMustNotBeCalled.VEC_DISABLE_ENV)

    result = availability.probe(_ConnectMustNotBeCalled, str(missing_db))

    assert result.available is False
    assert result.reason == "db_unavailable"
    assert os.listdir(tmp_path) == []
