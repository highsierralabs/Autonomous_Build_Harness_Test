"""C2 -- criterion-6 guard: CorpusAdapter.connect() re-checks database
existence before delegating to RHACO_corpus_index.connect(), on every call,
not only at construction (CONSTRAINTS.md O10; ARCHITECTURE.md 4.1/A9).

Round-1 checked `os.path.isfile` once in `__init__`; a live-index file
removed after a CorpusAdapter is constructed (an external reindex, a
misconfigured restart) was then re-created by the explorer the next time
something called `connect()`, because `RHACO_corpus_index.connect()` creates
the parent directory and the database file (and applies DDL) if absent. This
is a build write to the live index, forbidden by DISPATCH_PARAMETERS.md
items B/C and criterion 6. These two tests show the guard now holds per
call, and that it is a guard, not a break.
"""
from __future__ import annotations

import os

from explorer.config import Settings
from explorer.corpus_adapter import ConfigurationError, CorpusAdapter


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
