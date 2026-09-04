"""(a) A missing db path raises ConfigurationError and creates nothing."""
from __future__ import annotations

import os

from explorer.config import Settings
from explorer.corpus_adapter import ConfigurationError, CorpusAdapter


def test_missing_db_path_raises_configuration_error_and_creates_nothing(tmp_path):
    missing_db = tmp_path / "does_not_exist.db"
    assert not missing_db.exists()

    raised = False
    try:
        CorpusAdapter(Settings(db_path=str(missing_db)))
    except ConfigurationError:
        raised = True
    assert raised, "CorpusAdapter must raise ConfigurationError for a missing db path"

    assert os.listdir(tmp_path) == [], "the adapter must never create a database (O10)"
