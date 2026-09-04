"""Settings (integrator-owned). ARCHITECTURE.md section 5; CONSTRAINTS.md S7.

Only the knobs listed here are configurable. Defaults for the db path and the
docs root are `None`, meaning "use the RHACO module's own constants"; the
adapter resolves them (this module never imports RHACO code -- S2 makes the
adapter the only importer).
"""
from __future__ import annotations

import os
from dataclasses import dataclass

# DISPATCH_PARAMETERS.md item B: import form = path entries, not a package.
RHACO_PATH_ENTRIES = (r"C:\RHACO\rhaco", r"C:\RHACO\tools")
# CONSTRAINTS.md O1 / O13: the two spellings of the RHACO tree (junction + physical).
RHACO_TREES = (r"C:\RHACO", r"C:\highsierralabs\RHACO")

ENV_DB = "RHACO_EXPLORER_DB"
ENV_DOCS_ROOT = "RHACO_EXPLORER_DOCS_ROOT"
ENV_HOST = "RHACO_EXPLORER_HOST"
ENV_PORT = "RHACO_EXPLORER_PORT"
ENV_PAGE_SIZE = "RHACO_EXPLORER_PAGE_SIZE"
ENV_FAULT = "RHACO_EXPLORER_FAULT"


@dataclass(frozen=True)
class Settings:
    db_path: str | None = None          # None -> RHACO_corpus_index.DEFAULT_DB (resolved by the adapter)
    docs_root: str | None = None        # None -> RHACO_corpus_index.BODY_SCAN_ROOT (display + confinement only)
    host: str = "127.0.0.1"
    port: int = 8765
    page_size: int = 50
    fault: str | None = None            # fixture-only fault injection request; see explorer/faults.py
    app_version: str = "0.1.0"

    @classmethod
    def from_env(cls, env: dict | None = None) -> Settings:
        e = os.environ if env is None else env

        def _int(name: str, default: int) -> int:
            raw = e.get(name)
            if raw is None or str(raw).strip() == "":
                return default
            try:
                return int(raw)
            except ValueError:
                return default

        return cls(
            db_path=e.get(ENV_DB) or None,
            docs_root=e.get(ENV_DOCS_ROOT) or None,
            host=e.get(ENV_HOST) or "127.0.0.1",
            port=_int(ENV_PORT, 8765),
            page_size=max(1, min(500, _int(ENV_PAGE_SIZE, 50))),
            fault=e.get(ENV_FAULT) or None,
        )
