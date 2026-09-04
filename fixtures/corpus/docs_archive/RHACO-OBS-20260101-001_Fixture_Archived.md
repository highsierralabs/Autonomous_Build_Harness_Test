# RHACO-OBS-20260101-001 -- Fixture Archived (docs_archive)

## 1. Purpose

Synthetic fixture document deliberately placed under `docs_archive/`, which
both `RHACO_tool_catalog_librarian.DENY_DIRS` and
`RHACO_corpus_index.BODY_DENY_DIRS` exclude from every walk. This document
and its card must NOT appear in the fixture index (no cards row, no
fts_docs row) -- the probe framework's fixture-builder tests assert its
absence.
