"""CorpusAdapter: the read-only adapter over RHACO_corpus_index and
RHACO_tool_catalog_librarian (ARCHITECTURE.md 4.1). One of three licensed
product-tree importers of either module (ARCHITECTURE.md 4.1's importer
table; the other two are `explorer/diagnostics/service.py` under O17 and
`fixtures/build_fixture_index.py` under O3) -- corrected from the earlier,
false "the only module in the workspace" claim (ARCHITECTURE.md 4.1, SA-3;
this round's item 4).

Every SQL statement this file runs is one of D-Q1..D-Q11 in `sql.py`; every
call into the RHACO module is one of the S2 allowlist (`connect`, `get_meta`,
`search_fts`, `resolve_identifier`, `search_hybrid`, `search_graph`,
`freshness_check`, `embed_query_cpu`, `doc_id_from_filename`) plus the
librarian's read-only `scan_library`. No index-writing function is ever named
or called here (CONSTRAINTS.md O2 / S6 -- enforced per round by
tools/l1_index_write_check.py).

O10 guard: the live index can be removed or replaced out from under the
explorer while it runs, and `RHACO_corpus_index.connect()` creates the parent
directory and the database file (applying DDL) if the path is absent. So the
adapter never delegates to that `connect()` without first re-confirming
`os.path.isfile(db_path)` itself -- once at construction (`__init__`) and
again on *every* `connect()` call, not only the first -- raising
`ConfigurationError` instead of ever creating a database (round 2 / C2
correction; round 1 only checked at construction).
"""
from __future__ import annotations

import hashlib
import logging
import os
import re
import time
from dataclasses import replace
from datetime import UTC, datetime

from explorer import faults
from explorer.config import Settings
from explorer.corpus_adapter import availability, paths, sql
from explorer.models import (
    CARDS_COLUMNS,
    COMPONENT_RANK_NOT_EXPOSED,
    CardRow,
    CatalogFilters,
    CatalogPage,
    DocumentText,
    Edge,
    EdgeSet,
    Evidence,
    FacetValues,
    FreshnessView,
    Heading,
    IndexMeta,
    ModeResult,
    ResultItem,
    Subtree,
    VectorAvailability,
)

# Checked against RHACO_corpus_index.search_hybrid's own docstring/body (module
# lines 1387-1410): under VecUnavailable, `rankings = [fts_rank]` -- a single
# ranking list -- so `_rrf_fuse` reduces to the FTS order, and the identifier
# short-circuit precedes it; the fused ordering really does collapse to
# lexical-only here. This notice is examined (dispatch R07 item 1) and found
# CORRECT as written; left unchanged.
HYBRID_DEGRADED_NOTICE = "Hybrid unavailable: using lexical retrieval. Result ordering is lexical-only."

# Checked against RHACO_corpus_index.search_graph's own docstring/body (module
# lines 1559-1573+): graph mode seeds from search_hybrid (which degrades to
# identifier + FTS under VecUnavailable, exactly as HYBRID_DEGRADED_NOTICE
# describes) and then expands 1 hop, reading ONLY the `edges` table -- a step
# `VecUnavailable` never touches. So the graph itself is not unavailable, and
# the surviving edge-expansion still shapes the final ordering (seeds first,
# then expansions ordered by anchor-seed rank and relation priority -- not a
# lexical rank). The old wording asserted both those things falsely (SA-1,
# dispatch R07 item 1); this corrects it to name what actually degraded (the
# hybrid seed channel) and what survives (the graph expansion).
GRAPH_DEGRADED_NOTICE = (
    "Graph seed channel degraded: hybrid seeding fell back to identifier "
    "resolution plus lexical (FTS) search. The graph expansion itself -- one "
    "hop over the typed edges table -- is unaffected and still shapes result "
    "ordering."
)

_BASE_META_KEYS = (
    "index_schema_version", "librarian_version", "current_nc_version",
    "last_full_reindex_utc", "corpus_card_count", "corpus_cards_sha",
    "fts_docs_count", "edges_count", "id_aliases_count",
)
_VEC_META_SUFFIXES = ("vec_model", "vec_dim", "vec_rows", "vec_hash", "vec_reindex_utc")

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
_SLUG_STRIP_RE = re.compile(r"[^\w\s-]", re.UNICODE)
_SLUG_WS_RE = re.compile(r"\s+")


class ConfigurationError(RuntimeError):
    """The adapter refused to open the configured index because the database
    file does not exist (O10) -- a misconfigured or since-removed path must
    never create a database, so `os.path.isfile(db_path)` is checked before
    every delegation to `RHACO_corpus_index.connect()`: once in `__init__`
    and again, independently, on every `CorpusAdapter.connect()` call for
    the life of the instance (not a one-time construction-only check)."""


# Subtree is canonical in explorer.models since the round-1 integration (the builder's
# change request); the local stand-in was removed by the integrator.


def _utc_now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _mtime_iso(mtime: float) -> str:
    return datetime.fromtimestamp(mtime, tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _gfm_slug(text: str) -> str:
    s = text.strip().lower()
    s = _SLUG_STRIP_RE.sub("", s)
    s = _SLUG_WS_RE.sub("-", s)
    return s


def _filename_stem(doc_filename: str | None) -> str:
    name = doc_filename or ""
    return name.rsplit(".", 1)[0] if "." in name else name


def _all_meta_keys(rhaco_index) -> tuple[str, ...]:
    vec_keys = tuple(
        f"{suffix}__{tag}" for tag in rhaco_index.MODEL_TAGS for suffix in _VEC_META_SUFFIXES
    )
    return _BASE_META_KEYS + vec_keys


class CorpusAdapter:
    """Read-only adapter over RHACO_corpus_index / RHACO_tool_catalog_librarian
    (ARCHITECTURE.md 4.1). Db-exists guard (O10): `os.path.isfile(db_path)` is
    required both at construction and on *every* `connect()` call for the
    life of the instance -- the live index can be removed or replaced by an
    external actor mid-run, and `RHACO_corpus_index.connect()` would silently
    create a missing database, which is exactly what this guard prevents on
    every call, not only the first."""

    def __init__(self, settings: Settings) -> None:
        paths.ensure_rhaco_importable()
        import RHACO_corpus_index as rhaco_index  # deliberate post-sys.path-append import (S2)

        self._rhaco_index = rhaco_index
        self._librarian = None  # imported lazily by freshness()/exclusion_sets()

        db_path = settings.db_path or rhaco_index.DEFAULT_DB
        self.db_path = db_path
        self._require_db_exists()  # O10: construction-time check (also re-run on every connect())
        self.docs_root = settings.docs_root or rhaco_index.BODY_SCAN_ROOT
        self.active_fault = faults.active_fault(settings.fault, self.db_path)

        self._settings = settings
        self._index_meta_cache: tuple[float, IndexMeta] | None = None
        self._vector_cache: tuple[float, VectorAvailability] | None = None

    # -- connection -----------------------------------------------------

    def _require_db_exists(self) -> None:
        """O10 guard body, shared by `__init__` and `connect()`: raise
        ConfigurationError instead of ever letting `RHACO_corpus_index.connect()`
        create a missing database. Never opens or creates anything itself --
        `os.path.isfile` only."""
        if not os.path.isfile(self.db_path):
            raise ConfigurationError(
                f"configured database does not exist: {self.db_path!r} "
                "(the adapter never creates a database, O10)"
            )

    def connect(self):
        """RHACO_corpus_index.connect(db_path); the isfile guard (O10) is
        re-checked on *every* call, not only at construction -- a live index
        removed mid-run is refused, never re-created. One connection per
        request, closed by the caller (ARCHITECTURE.md 4.1)."""
        self._require_db_exists()
        return self._rhaco_index.connect(self.db_path)

    def _librarian_module(self):
        if self._librarian is None:
            import RHACO_tool_catalog_librarian as librarian  # lazy, read-only walk/scan calls only (O12)

            self._librarian = librarian
        return self._librarian

    # -- index meta / vector availability --------------------------------

    def index_meta(self) -> IndexMeta:
        now = time.monotonic()
        if self._index_meta_cache and now - self._index_meta_cache[0] < availability.CACHE_TTL_S:
            return self._index_meta_cache[1]
        conn = self.connect()
        try:
            meta = {}
            for key in _all_meta_keys(self._rhaco_index):
                value = self._rhaco_index.get_meta(conn, key)
                if value is not None:
                    meta[key] = value
            live_counts = {
                "cards": conn.execute(sql.Q1_COUNT_CARDS).fetchone()[0],
                "fts_docs": conn.execute(sql.Q1_COUNT_FTS_DOCS).fetchone()[0],
                "edges": conn.execute(sql.Q1_COUNT_EDGES).fetchone()[0],
                "id_aliases": conn.execute(sql.Q1_COUNT_ID_ALIASES).fetchone()[0],
                "edges_unresolved": conn.execute(sql.Q1_COUNT_EDGES_UNRESOLVED).fetchone()[0],
            }
        finally:
            conn.close()
        st = os.stat(self.db_path)
        result = IndexMeta(
            db_path=self.db_path,
            db_bytes=st.st_size,
            db_mtime_utc=_mtime_iso(st.st_mtime),
            meta=meta,
            live_counts=live_counts,
        )
        self._index_meta_cache = (now, result)
        return result

    def vector_availability(self) -> VectorAvailability:
        now = time.monotonic()
        if self._vector_cache and now - self._vector_cache[0] < availability.CACHE_TTL_S:
            return self._vector_cache[1]
        result = availability.probe(self._rhaco_index, self.db_path)
        self._vector_cache = (now, result)
        return result

    def exclusion_sets(self) -> dict:
        librarian = self._librarian_module()
        return {
            "body_deny_dirs": sorted(self._rhaco_index.BODY_DENY_DIRS),
            "body_suffixes": list(self._rhaco_index.BODY_SUFFIXES),
            "librarian_deny_dirs": sorted(librarian.DENY_DIRS),
        }

    # -- card row assembly ------------------------------------------------

    def _row_to_card(self, conn, row) -> CardRow:
        values = dict(zip(CARDS_COLUMNS, row, strict=True))
        yaml_path = values["yaml_path"]
        programs = [r[0] for r in conn.execute(sql.Q3_PROGRAMS_FOR_YAML_PATH, (yaml_path,)).fetchall()]
        tags = [r[0] for r in conn.execute(sql.Q3_TAGS_FOR_YAML_PATH, (yaml_path,)).fetchall()]
        card_ref = paths.card_ref_from_yaml_path(yaml_path, self.docs_root)
        doc_path = values.get("doc_path") or None
        doc_ref = paths.card_ref_from_yaml_path(doc_path, self.docs_root) if doc_path else None
        schema_version = values.get("schema_version")
        if schema_version is not None:
            try:
                schema_version = int(schema_version)
            except (TypeError, ValueError):
                pass
        stem = _filename_stem(values.get("doc_filename"))
        is_amendment = self._has_amends_edge_from(conn, values["doc_id"], stem)
        return CardRow(
            yaml_path=yaml_path,
            doc_id=values["doc_id"],
            doc_type=values.get("doc_type"),
            date=values.get("date"),
            seq=values.get("seq"),
            title=values.get("title"),
            status=values.get("status"),
            project_knowledge=values.get("project_knowledge"),
            current_version=values.get("current_version"),
            schema_version=schema_version,
            naming_convention_version=values.get("naming_convention_version"),
            lifecycle_state=values.get("lifecycle_state"),
            last_human_review=values.get("last_human_review"),
            reviewer=values.get("reviewer"),
            doc_filename=values.get("doc_filename"),
            doc_path=doc_path,
            local_path=values.get("local_path"),
            abstract=values.get("abstract"),
            card_sha256=values.get("card_sha256"),
            card_mtime_utc=values.get("card_mtime_utc"),
            indexed_at_utc=values.get("indexed_at_utc"),
            programs=programs,
            tags=tags,
            card_ref=card_ref,
            doc_ref=doc_ref,
            is_amendment=is_amendment,
        )

    def _has_amends_edge_from(self, conn, doc_id: str, stem: str) -> bool:
        """O7/O8: True iff an `amends` edge exists with from_id == stem. Reuses
        D-Q7 (already the documented "edges touching this card" query) rather
        than adding a twelfth statement."""
        if not stem:
            return False
        rows = conn.execute(sql.Q7_EDGES_FOR, (doc_id, doc_id, stem, stem)).fetchall()
        return any(relation == "amends" and from_id == stem for from_id, _to, relation, *_r in rows)

    def _cards_for_doc_id(self, conn, doc_id: str) -> list[CardRow]:
        rows = conn.execute(sql.Q3_CARDS_FOR_DOC_ID, (doc_id,)).fetchall()
        cards = [self._row_to_card(conn, r) for r in rows]
        if self.active_fault == "wrong_doc_for_id" and len(cards) > 1:
            # Fixture-only fault (ARCHITECTURE.md 6): rotate the id's own rows
            # by one, so a lookup for the correct id returns its sibling
            # instead (e.g. a hand card's request answered with its
            # amendment's row). A single-row id has no "following" row within
            # its own result set and is left unchanged -- a documented
            # limitation, see this round's report.
            cards = cards[1:] + cards[:1]
        return cards

    def cards_for_doc_id(self, doc_id: str) -> list[CardRow]:
        conn = self.connect()
        try:
            return self._cards_for_doc_id(conn, doc_id)
        finally:
            conn.close()

    def _cards_for_filename_stem(self, conn, stem: str) -> list[CardRow]:
        """O8/D-Q12: resolve a card by its document filename stem -- the form
        an `amends` edge's `from_id` takes, and which never matches a `doc_id`
        (D-Q3). Additive per this round's item 3 (SCOPE.md's deferred amends
        click-through row): no existing caller depended on this list being
        empty, since nothing called it before this round."""
        if not stem:
            return []
        rows = conn.execute(
            sql.Q12_CARDS_BY_FILENAME_STEM, (sql.filename_stem_like_pattern(stem),)
        ).fetchall()
        return [self._row_to_card(conn, r) for r in rows]

    def _card_by_yaml_paths(self, conn, junction: str, physical: str) -> CardRow | None:
        row = conn.execute(sql.Q4_CARD_BY_YAML_PATH, (junction, physical)).fetchone()
        if row is None:
            return None
        card = self._row_to_card(conn, row)
        if self.active_fault == "stale_card":
            card = replace(card, title=(card.title or "") + " [STALE]", status="Draft")
        return card

    def card(self, card_ref: str) -> CardRow | None:
        try:
            abs_path = paths.yaml_path_from_card_ref(card_ref, self.docs_root)
        except ValueError:
            return None
        if not paths.is_under_docs_root(abs_path, self.docs_root):
            return None
        junction, physical = paths.both_spellings(abs_path)
        conn = self.connect()
        try:
            return self._card_by_yaml_paths(conn, junction, physical)
        finally:
            conn.close()

    # -- catalog / facets ---------------------------------------------------

    def catalog(self, f: CatalogFilters, sort: str, page: int, page_size: int) -> CatalogPage:
        page = max(1, page)
        page_size = max(1, page_size)
        conn = self.connect()
        try:
            count_sql, count_params = sql.build_catalog_count_query(f)
            total = conn.execute(count_sql, count_params).fetchone()[0]
            query_sql, query_params = sql.build_catalog_query(f, sort, page, page_size)
            rows = conn.execute(query_sql, query_params).fetchall()
            cards = [self._row_to_card(conn, r) for r in rows]
            facets = self._facets_under_filter(conn, f)
        finally:
            conn.close()
        return CatalogPage(filters=f, sort=sort, page=page, page_size=page_size, total=total, rows=cards, facets=facets)

    def _facets_under_filter(self, conn, f: CatalogFilters) -> FacetValues:
        def counts(column: str) -> list[tuple]:
            q, params = sql.build_catalog_facet_column_query(f, column)
            return [tuple(r) for r in conn.execute(q, params).fetchall()]

        program_q, program_params = sql.build_catalog_facet_program_query(f)
        programs = [tuple(r) for r in conn.execute(program_q, program_params).fetchall()]
        return FacetValues(
            doc_types=counts("doc_type"),
            statuses=counts("status"),
            lifecycle_states=counts("lifecycle_state"),
            programs=programs,
            tags=[],  # D-Q6 does not cover tags (ARCHITECTURE.md 4.1); use facets() for the global tag facet
            project_knowledge=counts("project_knowledge"),
        )

    def facets(self) -> FacetValues:
        conn = self.connect()
        try:
            doc_types = conn.execute(sql.Q2_DOC_TYPE_COUNTS).fetchall()
            statuses = conn.execute(sql.Q2_STATUS_COUNTS).fetchall()
            lifecycle_states = conn.execute(sql.Q2_LIFECYCLE_STATE_COUNTS).fetchall()
            project_knowledge = conn.execute(sql.Q2_PROJECT_KNOWLEDGE_COUNTS).fetchall()
            programs = conn.execute(sql.Q2_PROGRAM_COUNTS).fetchall()
            tags = conn.execute(sql.Q2_TAG_COUNTS, (sql.TAG_FACET_LIMIT,)).fetchall()
        finally:
            conn.close()
        return FacetValues(
            doc_types=[tuple(r) for r in doc_types],
            statuses=[tuple(r) for r in statuses],
            lifecycle_states=[tuple(r) for r in lifecycle_states],
            programs=[tuple(r) for r in programs],
            tags=[tuple(r) for r in tags],
            project_knowledge=[tuple(r) for r in project_knowledge],
        )

    # -- search ---------------------------------------------------------

    def resolve_identifier(self, q: str) -> list[str]:
        return self._rhaco_index.resolve_identifier(q, db_path=self.db_path)

    def search_lexical(
        self, q: str, doc_type_filter=None, path_glob=None, context_lines: int = 2, max_results: int = 100
    ) -> ModeResult:
        raw = self._rhaco_index.search_fts(
            q,
            doc_type_filter=doc_type_filter,
            path_glob=path_glob,
            context_lines=context_lines,
            max_results=max_results,
            db_path=self.db_path,
        )
        items = []
        for rank, m in enumerate(raw["matches"], start=1):
            doc_id = m["doc_id"]
            cards = self.cards_for_doc_id(doc_id)
            evidence = Evidence(
                retrieval_mode="lexical",
                returned_rank=rank,
                line_no=m["line_no"],
                line=m["line"],
                context_before=m["context_before"],
                context_after=m["context_after"],
                excerpt_source="lexical-hit",
            )
            items.append(ResultItem(rank=rank, doc_id=doc_id, cards=cards, evidence=evidence, path=m["path"]))
        return ModeResult(
            query=q,
            mode_requested="lexical",
            mode_effective="lexical",
            items=items,
            truncated=raw["truncated"],
            total_matched=raw["total_matched"],
            returned=raw["returned"],
        )

    def lexical_excerpt(self, q: str, doc_ref: str) -> Evidence | None:
        if not q or not q.strip() or not doc_ref:
            return None
        basename = doc_ref.rsplit("/", 1)[-1]
        raw = self._rhaco_index.search_fts(
            q, path_glob=basename, context_lines=2, max_results=1, db_path=self.db_path
        )
        matches = raw.get("matches") or []
        if not matches:
            return None
        m = matches[0]
        return Evidence(
            retrieval_mode="lexical-lookup",
            returned_rank=1,
            line_no=m["line_no"],
            line=m["line"],
            context_before=m["context_before"],
            context_after=m["context_after"],
            excerpt_source="lexical-lookup",
        )

    def _items_from_doc_ids(self, q: str, doc_ids: list[str], mode_effective: str, degradation_status: str) -> list[ResultItem]:
        identifier_hits = set(self._rhaco_index.resolve_identifier(q, db_path=self.db_path))
        items = []
        for rank, doc_id in enumerate(doc_ids, start=1):
            cards = self.cards_for_doc_id(doc_id)
            doc_ref = cards[0].doc_ref if cards else None
            excerpt = self.lexical_excerpt(q, doc_ref) if doc_ref else None
            evidence = Evidence(
                retrieval_mode=mode_effective,
                returned_rank=rank,
                exact_identifier_match=doc_id in identifier_hits,
                degradation_status=degradation_status,
                component_rank=COMPONENT_RANK_NOT_EXPOSED,
            )
            if excerpt is not None:
                evidence.line_no = excerpt.line_no
                evidence.line = excerpt.line
                evidence.context_before = excerpt.context_before
                evidence.context_after = excerpt.context_after
                evidence.excerpt_source = excerpt.excerpt_source
            items.append(ResultItem(rank=rank, doc_id=doc_id, cards=cards, evidence=evidence))
        return items

    def search_hybrid(self, q: str, top_k: int = 10) -> ModeResult:
        vec = self.vector_availability()
        doc_ids = self._rhaco_index.search_hybrid(q, top_k=top_k, db_path=self.db_path)
        if vec.available:
            mode_effective, notice, degradation_status = "hybrid", None, "none"
        else:
            mode_effective, notice, degradation_status = "hybrid-degraded-lexical", HYBRID_DEGRADED_NOTICE, vec.reason
        items = self._items_from_doc_ids(q, doc_ids, mode_effective, degradation_status)
        return ModeResult(
            query=q,
            mode_requested="hybrid",
            mode_effective=mode_effective,
            items=items,
            degradation_notice=notice,
            returned=len(items),
            vector=vec,
        )

    def search_graph(self, q: str, top_k: int = 10) -> ModeResult:
        vec = self.vector_availability()
        doc_ids = self._rhaco_index.search_graph(q, top_k=top_k, db_path=self.db_path)
        if vec.available:
            mode_effective, notice, degradation_status = "graph", None, "none"
        else:
            # SA-1 (dispatch R07 item 1): names the channel that actually
            # degraded (the hybrid seed) rather than the bare "graph-degraded"
            # token, which named no surviving channel and, read literally,
            # claimed the whole graph mode was unavailable (GRAPH_DEGRADED_NOTICE
            # above). ARCHITECTURE.md 4.1's mode_effective enum and the
            # explorer.models.ModeResult.mode_effective comment still list the
            # old token -- filed as a change request (see this round's report)
            # rather than edited here, since both files are outside this
            # module's owned paths.
            mode_effective, notice, degradation_status = (
                "graph-degraded-semantic-seed", GRAPH_DEGRADED_NOTICE, vec.reason,
            )
        items = self._items_from_doc_ids(q, doc_ids, mode_effective, degradation_status)
        return ModeResult(
            query=q,
            mode_requested="graph",
            mode_effective=mode_effective,
            items=items,
            degradation_notice=notice,
            returned=len(items),
            vector=vec,
        )

    # -- lineage ----------------------------------------------------------

    def edges_for(self, card: CardRow) -> EdgeSet:
        doc_id = card.doc_id
        stem = card.filename_stem
        conn = self.connect()
        try:
            rows = conn.execute(sql.Q7_EDGES_FOR, (doc_id, doc_id, stem, stem)).fetchall()
            outgoing: list[Edge] = []
            incoming: list[Edge] = []
            unresolved: list[Edge] = []
            for from_id, to_id, relation, source_field, from_yaml_path, note, resolved in rows:
                edge = Edge(
                    from_id=from_id,
                    to_id=to_id,
                    relation=relation,
                    source_field=source_field,
                    from_yaml_path=from_yaml_path,
                    note=note,
                    resolved=bool(resolved),
                )
                if self.active_fault == "reverse_edges":
                    edge = replace(edge, from_id=edge.to_id, to_id=edge.from_id)
                if not edge.resolved:
                    unresolved.append(edge)
                    continue
                edge.target_cards = self._cards_for_doc_id(conn, edge.to_id)
                if edge.relation == "amends":
                    # O8: this edge's from_id is the amendment's filename
                    # stem, never a doc_id -- D-Q3 can never match it (this
                    # round's item 3; SCOPE.md's deferred click-through row).
                    edge.source_cards = self._cards_for_filename_stem(conn, edge.from_id)
                else:
                    edge.source_cards = self._cards_for_doc_id(conn, edge.from_id)
                if edge.from_id in (doc_id, stem):
                    outgoing.append(edge)
                if edge.to_id in (doc_id, stem):
                    incoming.append(edge)
        finally:
            conn.close()
        return EdgeSet(center=card, outgoing=outgoing, incoming=incoming, unresolved=unresolved, chain_head=None)

    def supersession_chain(self, doc_id: str) -> list[CardRow]:
        conn = self.connect()
        try:
            forward = conn.execute(sql.Q9_CHAIN_FORWARD, (doc_id,)).fetchall()
            backward = conn.execute(sql.Q9_CHAIN_BACKWARD, (doc_id,)).fetchall()
            ordered_ids: list[str] = []
            seen: set[str] = set()
            # Python-side visited-set cycle guard (O22/O25), on top of the
            # SQL depth cap: oldest predecessor first, through doc_id, to the
            # newest successor last.
            for id_, _depth in sorted(backward, key=lambda t: -t[1]):
                if id_ not in seen:
                    seen.add(id_)
                    ordered_ids.append(id_)
            for id_, _depth in sorted(forward, key=lambda t: t[1]):
                if id_ not in seen:
                    seen.add(id_)
                    ordered_ids.append(id_)
            cards: list[CardRow] = []
            for id_ in ordered_ids:
                cards.extend(self._cards_for_doc_id(conn, id_))
        finally:
            conn.close()
        return cards

    def campaign_subtree(self, cmp_id: str, depth: int | None, max_results: int = 200) -> Subtree:
        conn = self.connect()
        try:
            rows = conn.execute(sql.Q10_CAMPAIGN_SUBTREE, (cmp_id, depth, depth, max_results)).fetchall()
            seen: set[str] = set()  # Python-side cycle guard, same as supersession_chain
            nodes: list[tuple[CardRow, int]] = []
            for id_, d in rows:
                if id_ in seen:
                    continue
                seen.add(id_)
                for card in self._cards_for_doc_id(conn, id_):
                    nodes.append((card, d))
            counts: dict = {}
            for card, _d in nodes:
                key = card.doc_type or "?"
                counts[key] = counts.get(key, 0) + 1
        finally:
            conn.close()
        return Subtree(
            root_id=cmp_id,
            depth_limit=depth,
            max_results=max_results,
            truncated=len(rows) >= max_results,
            nodes=nodes,
            counts_by_doc_type=counts,
        )

    def dangling_references(self, from_doc_type=None, relation=None, max_results: int = 200) -> list[Edge]:
        query_sql, params = sql.build_dangling_query(relation, from_doc_type, max_results)
        conn = self.connect()
        try:
            rows = conn.execute(query_sql, params).fetchall()
        finally:
            conn.close()
        return [
            Edge(from_id=r[0], to_id=r[1], relation=r[2], source_field=r[3], from_yaml_path=r[4], note=r[5], resolved=False)
            for r in rows
        ]

    # -- documents ----------------------------------------------------------

    def _headings(self, lines: list[str]) -> list[Heading]:
        slug_counts: dict[str, int] = {}
        headings: list[Heading] = []
        in_fence = False
        fence_marker = ""
        for i, line in enumerate(lines, start=1):
            stripped = line.lstrip()
            if stripped[:3] in ("```", "~~~"):
                marker = stripped[:3]
                if not in_fence:
                    in_fence, fence_marker = True, marker
                elif marker == fence_marker:
                    in_fence = False
                continue
            if in_fence:
                continue
            m = _HEADING_RE.match(line)
            if not m:
                continue
            level = len(m.group(1))
            text = m.group(2).rstrip("#").strip()
            slug = _gfm_slug(text)
            if slug in slug_counts:
                slug_counts[slug] += 1
                slug = f"{slug}-{slug_counts[slug]}"
            else:
                slug_counts[slug] = 0
            headings.append(Heading(level=level, text=text, slug=slug, line_no=i))
        return headings

    def read_document(self, card: CardRow) -> DocumentText:
        if not card.doc_path:
            raise ConfigurationError(f"card {card.card_ref!r} has no document path (ORPHAN card)")
        abs_path = card.doc_path
        if not paths.is_under_docs_root(abs_path, self.docs_root):
            raise ConfigurationError(f"refusing to read outside the docs root: {abs_path!r}")
        with open(abs_path, "rb") as fh:
            raw = fh.read()
        sha256 = hashlib.sha256(raw).hexdigest()
        suffix = os.path.splitext(abs_path)[1].lower()
        if suffix == ".md":
            kind = "markdown"
        elif suffix == ".txt":
            kind = "text"
        else:
            kind = "binary"
        if kind == "binary":
            text, lines, headings = "", [], []
        else:
            text = raw.decode("utf-8", errors="replace")
            lines = text.splitlines()
            headings = self._headings(lines)
            if self.active_fault == "broken_jump":
                headings = [replace(h, line_no=h.line_no + 50) for h in headings]
        return DocumentText(
            path=abs_path,
            size_bytes=len(raw),
            sha256=sha256,
            text=text,
            lines=lines,
            headings=headings,
            renderable=(kind != "binary"),
            kind=kind,
        )

    def read_card_text(self, card: CardRow) -> str:
        if not paths.is_under_docs_root(card.yaml_path, self.docs_root):
            raise ConfigurationError(f"refusing to read outside the docs root: {card.yaml_path!r}")
        with open(card.yaml_path, encoding="utf-8", errors="replace") as fh:
            return fh.read()

    # -- freshness ------------------------------------------------------

    def freshness(self) -> FreshnessView:
        librarian = self._librarian_module()
        logger = logging.getLogger("explorer.corpus_adapter.freshness")
        logger.propagate = False
        if not logger.handlers:
            logger.addHandler(logging.NullHandler())
        # output_path: scan_library only READS this path (os.path.isfile +
        # read_text_safe, to diff a prior "Version history" table if one is
        # present) -- write_catalog is a distinct function scan_library never
        # calls (verified by reading RHACO_tool_catalog_librarian.py around
        # line 1665 and grepping every "output_path" occurrence in the file
        # before writing this method). The librarian's own generated catalog
        # under docs_root/reference is safe to pass here even when it exists:
        # it is read-only input, and this works unchanged when docs_root is a
        # fixture root where the file does not exist (isfile -> False,
        # prior_version_history -> [], no error either way).
        output_path = os.path.join(self.docs_root, "reference", "RHACO_Document_Catalog.md")
        t0 = time.perf_counter()
        scan = librarian.scan_library(self.docs_root, output_path, logger)
        report = self._rhaco_index.freshness_check(scan, self.db_path)
        scan_seconds = time.perf_counter() - t0
        return FreshnessView(
            fresh=report.fresh,
            status=report.status,
            corpus_card_count_live=report.corpus_card_count_live,
            corpus_card_count_index=report.corpus_card_count_index,
            corpus_cards_sha_live=report.corpus_cards_sha_live,
            corpus_cards_sha_index=report.corpus_cards_sha_index,
            added=list(report.added),
            removed=list(report.removed),
            sha_changed=list(report.sha_changed),
            computed_at_utc=_utc_now_iso(),
            scan_seconds=scan_seconds,
        )
