# ARCHITECTURE.md -- RHACO Corpus Explorer (PROMPT.md section 1 step 6)

Written 2026-09-04 by the build orchestrator after `CONSTRAINTS.md`, before any feature code. Constraint ids (S1-S8, O1-O28) refer to `CONSTRAINTS.md`; retrieval facts to `docs/REFERENCE.md`; module facts to the round-0 reports under `docs/rounds/`.

## 1. Product shape

A local, read-only FastAPI + Jinja2 application served on `127.0.0.1` from the workspace venv, reading the RHACO corpus (`C:\RHACO\docs\**`) and the derived index (`C:\RHACO\index\corpus_index.db`) through `RHACO_corpus_index.py`'s public API. Pages: catalog (home), search, reader, lineage, diagnostics. Every page is server-rendered HTML with a JSON twin under `/api/...` that the probe asserts against. No writes anywhere; no LLM anywhere.

## 2. Workspace layout and ownership

| Path | Owner | Contents |
|---|---|---|
| `explorer/__init__.py`, `explorer/app.py`, `explorer/config.py`, `explorer/models.py`, `explorer/faults.py` | **integrator** (orchestrator) | app factory + route registration, `Settings`, shared typed models, fixture-only fault injection hooks |
| `explorer/corpus_adapter/` | builder `corpus_adapter` | `adapter.py` (the only importer of `RHACO_corpus_index` and `RHACO_tool_catalog_librarian`), `sql.py` (the documented read-only queries D-Q1..D-Q11), `paths.py` (junction-aware confinement), `availability.py` (vector-channel probe) |
| `explorer/catalog/` | builder `catalog` | `service.py`, `routes.py`, `templates/catalog/*.html` |
| `explorer/search/` | builder `search` | `service.py`, `routes.py`, `templates/search/*.html` |
| `explorer/reader/` | builder `reader` | `service.py` (markdown rendering, heading slugs, line anchors), `routes.py`, `templates/reader/*.html` |
| `explorer/lineage/` | builder `lineage` | `service.py` (edge sets, chains, subtree), `routes.py`, `templates/lineage/*.html`, `static/lineage.js` (inline-SVG one-hop graph) |
| `explorer/diagnostics/` | builder `diagnostics` | `service.py`, `routes.py`, `templates/diagnostics/*.html` |
| `explorer/web/` | builder `web` | `templates/base.html`, `templates/_partials/*.html`, `static/app.css`, `static/app.js` (keyboard navigation, no framework) |
| `tools/probe_corpus_explorer.py` | builder `probe` | production-path Playwright probe (server lifecycle, presets, screenshots, JSON observations, console + network capture) |
| `tools/l1_index_write_check.py` | integrator | L1 grep for the five index-writing names (O2) |
| `tools/l4_gold_oracle.py` | integrator | Gold v1.1 compatibility oracle (O16) |
| `fixtures/build_fixture_index.py` | builder `probe` (reviewed by integrator) | the **only** file allowed to name the index-writing functions (O2, O3) |
| `fixtures/corpus/` | builder `probe` | frozen fixture documents and cards (docs root for the fixture index) |
| `fixtures/fixture_index.db` | built artifact (gitignored) | produced by the fixture builder, never committed |
| `tests/<module>/` | the module's builder | pytest unit tests; integration tests under `tests/integration/` are the integrator's |
| `docs/LAYERS.md`, `docs/critique/`, `docs/rounds/`, `docs/probe-qualification/`, `docs/REFERENCE.md` | integrator (critic reports land under `docs/critique/` via the integrator; a builder writes only its own `docs/rounds/R<nn>_<module>.report.md`, A17) | evidence artifacts (PROMPT.md section 10) |
| `.worktrees/<module>/` | integrator creates; the module's builder works inside it on branch `build/<module>` | gitignored worktree checkouts (A15) |

Rules: a builder writes only inside its owned paths plus `tests/<module>/`. Anything else (models, config, app wiring, base templates, root dependency files) is a **change request** to the integrator (PROMPT.md section 4: requestor, affected contract/path, evidence, compatibility impact, migration, invalidated tests/probes), recorded in `docs/rounds/`. No mutable path has two owners.

## 3. Shared models (`explorer/models.py`, integrator)

Plain dataclasses (no ORM):

- `CardRow` -- the 21 `cards` columns (I1 section 5) plus `programs: list[str]`, `tags: list[str]`, `card_ref: str` (relative POSIX path of the `.card.yaml` under the docs root, the stable URL key), `doc_ref: str | None` (relative path of the document), `is_amendment: bool` (a `parent` edge exists from this card's filename stem), `frozen: bool` (`status in {Superseded, Archived}`).
- `IndexMeta` -- every `index_meta` key (`index_schema_version`, `librarian_version`, `current_nc_version`, `last_full_reindex_utc`, `corpus_card_count`, `corpus_cards_sha`, `fts_docs_count`, `edges_count`, `id_aliases_count`, `vec_*__<tag>`), live counts, db path, db size and mtime.
- `VectorAvailability` -- `available: bool`, `reason: str` (`ok` | `disabled_by_env` | `sqlite_vec_not_loaded` | `vec_table_missing` | `embedder_unreachable`), `model_tag`, `probe_ms`.
- `ModeResult` -- `query`, `mode_requested`, `mode_effective` (`identifier` | `lexical` | `hybrid` | `hybrid-degraded-lexical` | `graph` | `graph-degraded`), `degradation_notice: str | None`, `items: list[ResultItem]`, `truncated`, `total_matched`.
- `ResultItem` -- `rank`, `doc_id`, `cards: list[CardRow]` (all rows for the id, O7), `evidence: Evidence`.
- `Evidence` -- `exact_identifier_match: bool`, `retrieval_mode`, `returned_rank`, `line_no`, `line`, `context_before`, `context_after`, `excerpt_source` (`lexical-hit` | `lexical-lookup` | `none`), `graph_relation`, `graph_seed`, `degradation_status`, `component_rank: str` (always `"not exposed by current RHACO retrieval API"` for hybrid/graph).
- `Edge` -- `from_id`, `to_id`, `relation`, `source_field`, `from_yaml_path`, `note`, `resolved: bool`, `direction_label` (rendered per relation: `cites` / `is superseded by` / `amends` / `has campaign child`), `target_cards: list[CardRow]`.
- `EdgeSet` -- `outgoing`, `incoming`, `unresolved` (edges whose `to_id` is a literal), `chain_head: CardRow | None`.
- `FreshnessView` -- the module's `FreshnessReport` fields plus `computed_at_utc`, `scan_seconds`, `scope_note` ("card metadata only").
- `DocumentText` -- `path`, `bytes`, `text`, `sha256`, `lines: list[str]`, `headings: list[Heading(level, text, slug, line_no)]`, `renderable: bool` (markdown / text only).

## 4. Module contracts

### 4.1 `corpus_adapter` (read-only; the only RHACO importer)

```
class CorpusAdapter:
    def __init__(self, settings: Settings)                      # verifies settings.db_path exists (O10); imports RHACO_corpus_index via sys.path entries (S2)
    def connect(self) -> sqlite3.Connection                     # RHACO_corpus_index.connect(settings.db_path); one connection per request; caller closes
    def index_meta(self) -> IndexMeta                            # get_meta for each known key + D-Q1 counts; cached <= 5 s (O10)
    def vector_availability(self) -> VectorAvailability          # O4 procedure; cached <= 5 s
    def resolve_identifier(self, q: str) -> list[str]            # RHACO_corpus_index.resolve_identifier
    def cards_for_doc_id(self, doc_id: str) -> list[CardRow]     # D-Q3 (all rows, ordered by yaml_path)
    def card(self, card_ref: str) -> CardRow | None              # D-Q4 (both junction and physical spellings, O13)
    def catalog(self, f: CatalogFilters, sort: str, page: int, page_size: int) -> CatalogPage   # D-Q5 + D-Q6
    def facets(self) -> FacetValues                              # D-Q2 distinct values and counts (O14)
    def search_lexical(self, q, doc_type_filter=None, path_glob=None, context_lines=2, max_results=100) -> ModeResult   # search_fts; mode_effective = lexical
    def search_hybrid(self, q, top_k=10) -> ModeResult           # vector_availability() first; then RHACO_corpus_index.search_hybrid; labels degraded results (O4)
    def search_graph(self, q, top_k=10) -> ModeResult            # likewise via search_graph
    def lexical_excerpt(self, q, doc_ref: str) -> Evidence | None  # search_fts(q, path_glob=<that document>) -- labelled excerpt_source=lexical-lookup (O6)
    def edges_for(self, card: CardRow) -> EdgeSet                 # D-Q7 by doc_id and by filename stem (amends, O8)
    def supersession_chain(self, doc_id: str) -> list[CardRow]    # D-Q9 recursive CTE over supersedes, both directions, cycle-safe (O22, O25)
    def campaign_subtree(self, cmp_id: str, depth: int | None, max_results=200) -> Subtree   # D-Q10 (O25)
    def dangling_references(self, from_doc_type=None, relation=None, max_results=200) -> list[Edge]   # D-Q11 (O25)
    def read_document(self, card: CardRow) -> DocumentText        # disk read, confinement check (O1, O13), UTF-8, headings + slugs (O23)
    def read_card_text(self, card: CardRow) -> str                # the .card.yaml bytes as text
    def freshness(self) -> FreshnessView                          # scan_library(docs_root, output_path=None, logger=null) -> freshness_check(scan, db_path); on demand only (O9)
    def exclusion_sets(self) -> dict                              # {"body_deny_dirs": sorted(BODY_DENY_DIRS), "body_suffixes": list(BODY_SUFFIXES), "librarian_deny_dirs": sorted(DENY_DIRS)} read from the module / librarian constants (O24)
    active_fault: str | None                                      # attribute: explorer.faults.active_fault(settings.fault, db_path) evaluated once at construction (A13)
    db_path: str                                                  # attribute: the resolved database path
    docs_root: str                                                # attribute: the resolved docs root
```

**Documented read-only SQL (all parameterized; the complete list -- adding one is a change request):**

| Id | Purpose | Statement (parameters `?`) |
|---|---|---|
| D-Q1 | live counts and vector extension check | `SELECT count(*) FROM cards`; `... FROM fts_docs`; `... FROM edges`; `... FROM id_aliases`; `SELECT count(*) FROM edges WHERE resolved=0`; `SELECT vec_version()` (raises when sqlite-vec is not loaded -- used only as an availability signal) |
| D-Q2 | facet values | `SELECT doc_type, count(*) FROM cards GROUP BY doc_type ORDER BY doc_type`; same for `status`, `lifecycle_state` (non-null), `project_knowledge`; `SELECT program, count(*) FROM card_programs GROUP BY program`; `SELECT tag, count(*) FROM card_tags GROUP BY tag ORDER BY count(*) DESC, tag LIMIT ?` |
| D-Q3 | cards for an id | `SELECT <21 cols> FROM cards WHERE doc_id = ? ORDER BY yaml_path` + `SELECT program FROM card_programs WHERE yaml_path = ?` + `SELECT tag FROM card_tags WHERE yaml_path = ?` |
| D-Q4 | card by reference | `SELECT <21 cols> FROM cards WHERE yaml_path IN (?, ?)` (junction and physical spellings of the same relative path) |
| D-Q5 | catalog page | `SELECT <21 cols> FROM cards c WHERE 1=1 [AND c.doc_type = ?] [AND c.status = ?] [AND c.lifecycle_state = ?] [AND c.project_knowledge = ?] [AND c.date >= ?] [AND c.date <= ?] [AND EXISTS (SELECT 1 FROM card_programs p WHERE p.yaml_path = c.yaml_path AND p.program = ?)] [AND EXISTS (SELECT 1 FROM card_tags t WHERE t.yaml_path = c.yaml_path AND t.tag = ?)] [AND c.yaml_path LIKE ?] ORDER BY <whitelisted column> <ASC|DESC>, c.yaml_path LIMIT ? OFFSET ?` -- clauses are appended from a fixed whitelist; values are always bound |
| D-Q6 | catalog facet counts under the current filter | D-Q5's `WHERE` reused with `SELECT c.doc_type, count(*) ... GROUP BY c.doc_type` (and status, lifecycle_state, program, project_knowledge) |
| D-Q7 | edges around a card | `SELECT from_id, to_id, relation, source_field, from_yaml_path, note, resolved FROM edges WHERE from_id = ? OR to_id = ? OR from_id = ? OR to_id = ?` (doc_id and filename stem) |
| D-Q8 | body row for a document (reader fallback when the file is missing) | `SELECT doc_id, path FROM fts_docs WHERE doc_id = ?` |
| D-Q9 | supersession chain | `WITH RECURSIVE chain(id, depth) AS (SELECT ?, 0 UNION ALL SELECT e.to_id, depth+1 FROM edges e JOIN chain ON e.from_id = chain.id WHERE e.relation='supersedes' AND depth < 50) SELECT id, depth FROM chain` (and the mirror with `e.to_id = chain.id` for backward); cycle guard = depth cap + visited set in Python |
| D-Q10 | campaign subtree | `WITH RECURSIVE sub(id, depth) AS (SELECT ?, 0 UNION ALL SELECT e.to_id, depth+1 FROM edges e JOIN sub ON e.from_id = sub.id WHERE e.relation='campaign_child' AND (? IS NULL OR depth < ?)) SELECT id, depth FROM sub LIMIT ?` |
| D-Q11 | dangling references | `SELECT from_id, to_id, relation, source_field, from_yaml_path, note FROM edges WHERE resolved = 0 [AND relation = ?] [AND from_id IN (SELECT doc_id FROM cards WHERE doc_type = ?)] LIMIT ?` |

Adapter rules: no other SQL; no string interpolation of user input; every statement lives in `sql.py` with its D-Q id; the connection is opened by `RHACO_corpus_index.connect()` only after `os.path.isfile(db_path)` (O10); `search_hybrid` is always preceded by `vector_availability()` so degraded results are labelled before rendering (O4); `search_hybrid_rerank`, `embed_texts`, and the five index-writing functions listed in `CONSTRAINTS.md` S6 are never called (O2, S3). (The five names are deliberately not spelled in this file: `tools/l1_index_write_check.py` greps every root-level file, and only `CONSTRAINTS.md`, `docs/`, the three pinned instruments, and `fixtures/build_fixture_index.py` are outside its scope.)

### 4.2 `catalog`
`GET /` and `GET /api/catalog` -- facets (D-Q2/D-Q6), filter form (doc_type, date range, status, lifecycle_state as a **separate** control shown only when CMP is among the results or selected, program, tag, project_knowledge, path prefix), sortable list (date, doc_id, title, status; default date desc), page size 50, each row: title, doc_id, doc_filename, doc_type, date, status (frozen marker), programs, lifecycle_state cell (CMP only, else blank), compact abstract, open action (`/doc/<card_ref>`). Total indexed documents and card count from `IndexMeta`. Filtering never fabricates values (O14).

### 4.3 `search`
`GET /search?q=&mode=&...` and `GET /api/search`. Modes: `identifier` (module `resolve_identifier`; lists every card row per id), `lexical` (`search_fts` with `doc_type_filter`, `path_glob`, `context_lines`, `max_results`), `hybrid` (default), `graph`. Mode badge shows `mode_effective`; degraded hybrid renders the notice `Hybrid unavailable: using lexical retrieval. Result ordering is lexical-only.` and never keeps the "Hybrid" label (S3, O4). Facet narrowing on hybrid/graph results is a separate control labelled "narrow results after retrieval (ranking unchanged)" (O5). Each result has an **Evidence** disclosure built from `Evidence` (O6): exact identifier match, active mode, returned rank, matched line/context (lexical hits) or a labelled lexical-lookup excerpt (hybrid/graph, when the query has a literal match), graph relation and seed where the module exposes them (it does not for `search_graph`'s ids -- shown as "expansion of a seed; relation not exposed"), degradation status, `Component rank: not exposed by current RHACO retrieval API`.

### 4.4 `reader`
`GET /doc/<card_ref>[?line=N | #slug]` and `GET /api/doc/<card_ref>`. Layout: canonical body (left/main) rendered from the file on disk; card panel (right) with identity, status, lifecycle_state (CMP), programs, tags, dependencies (`depends_on` / `see_also` from the card text), supersession/amendment state (from edges), local path (junction spelling, copyable), incoming/outgoing lineage links. Body and card are visually distinct regions with headings "Document" and "Card (catalog metadata)". Markdown rendering: `markdown-it-py` (CommonMark) with `html=False` (raw HTML escaped, so no sanitizer is needed), tables and strikethrough enabled, code fences preserved verbatim; every heading gets a GFM slug id and a `data-line` attribute; `?line=N` scrolls to and highlights line N (lexical hits); a `.txt` document renders as preformatted text; `.docx` / `.pdf` / `.ipynb` cards show the card and path only (O15). Reference-document `Superseded` banner links to the chain head (O22). Text is verbatim except rendering (no summaries).

### 4.5 `lineage`
`GET /lineage/<card_ref>[?relation=&hops=1]` and `GET /api/lineage/<card_ref>`. Selected-document-centered; typed, directional edges from D-Q7 with the direction labels of O8; relation filter; one hop by default, controlled expansion to two; two views: inline-SVG graph (vanilla JS, `static/lineage.js`, radial layout, click opens the reader) and a chronological "reasoning trail" list (connected cards ordered by `cards.date`); unresolved targets rendered as literal ids with an "unresolved" marker; supersession chain (D-Q9) and campaign subtree (D-Q10, CMP only) as tabs. No edge is inferred.

### 4.6 `diagnostics`
`GET /diagnostics` and `GET /api/diagnostics`: application version, db path (+ non-authoritative statement), `IndexMeta`, `VectorAvailability` (with reason), active/default mode, degradation state, counts, exclusion sets (module `BODY_DENY_DIRS`, librarian `DENY_DIRS`, read as constants), rerank standing (documented-FAIL; artifact directory present yes/no by `os.path.isdir`, never loaded), last probe run if `docs/probe-qualification/last_run.json` exists, a **Check freshness** action (`POST /diagnostics/freshness` -- the only POST; it computes and displays, writes nothing, O9), and the required authority notice verbatim: **Retrieval is not adjudication.** ...

### 4.7 `web`
`base.html` (header nav: Catalog / Search / Diagnostics; skip-link; landmarks), partials (result card, evidence disclosure, degradation banner, authority notice), `app.css` (system font stack, `#4B286D` accent, high-contrast focus rings, no external asset), `app.js` (keyboard shortcuts: `/` focuses search, `j`/`k` move selection, `Enter` opens, `?` shows the key list). Accessibility: every control labelled; tables with headers; color never the sole signal (frozen marker has text).

### 4.8 `probe` (`tools/probe_corpus_explorer.py`)
Synchronous Playwright, Chromium headless. `--db <path> --docs-root <path> --port <n> --preset <name>|all --out <dir>`. Launches `<venv python> -m uvicorn explorer.app:create_app --factory --host 127.0.0.1 --port <n>` as a foreground child with the configured env (`RHACO_EXPLORER_DB`, `RHACO_EXPLORER_DOCS_ROOT`, optional `RHACO_CORPUS_DISABLE_VEC`, optional `RHACO_EXPLORER_FAULT` -- fixture only), waits on `GET /healthz` (JSON `{"status":"ok","db":..., "vector": ...}`) up to 30 s, runs presets, writes `<out>/<preset>.png` and `<out>/<preset>.json` (url, viewport, active mode, selected doc, observed result ids, console errors, failed requests, timings), terminates the child, exits non-zero if any required observation is missing (O12). Presets = the ten acceptance workflows W1-W10 plus the qualification cases (section 6). Every observation the probe records is read from the DOM **and** cross-checked against the `/api/...` twin.

## 5. Configuration (`explorer/config.py`)

`Settings` from environment with defaults: `RHACO_EXPLORER_DB` (default `RHACO_corpus_index.DEFAULT_DB`), `RHACO_EXPLORER_DOCS_ROOT` (default `RHACO_corpus_index.BODY_SCAN_ROOT`; display + confinement only), `RHACO_EXPLORER_HOST=127.0.0.1`, `RHACO_EXPLORER_PORT=8765`, `RHACO_EXPLORER_PAGE_SIZE=50`, `RHACO_EXPLORER_FAULT` (fixture-only; ignored unless the db path is outside both RHACO trees). Nothing else is configurable (S7).

## 6. Verification design (summary; the register is `docs/LAYERS.md`)

- L1: `ruff` (add as a dev dependency) + `tools/l1_index_write_check.py` + `pytest tests/` + template render smoke tests.
- L2: the probe against the production path (live db) for W1-W10, and against `fixtures/fixture_index.db` for qualification.
- L3: critic (Opus 5, Explore) reads screenshots + JSON + templates; writes nothing; the integrator files the report under `docs/critique/`.
- L4: `tools/l4_gold_oracle.py` -- for each Gold v1.1 row, records the module's direct `search_hybrid` ids and the adapter's ids on the same live index, asserts list equality (the adapter did not degrade the module), computes Recall@10 with `any-target-in-top-10` (honoring `resolve: supersession-head` via D-Q9), and writes `docs/probe-qualification/gold_v1_1_compat.json`. The 0.700 threshold applies to the adapter figure; a module-side figure below 0.700 on today's corpus is a substrate observation recorded in `SCOPE.md` with its cause, never silent (O16).

**Probe qualification fixture** (`fixtures/corpus/`, ~10 documents with cards): a CMP with two `campaign_child` members; a superseded/superseding reference pair; an amendment child sharing its parent's id; an EVT with an `E######` id; a document containing a unique lexical phrase; one `.txt`; a `docs_archive/` sub-tree that must not be indexed. Known-bad cases are produced by `RHACO_EXPLORER_FAULT` values in `explorer/faults.py`, active only when the db path is a fixture db: `wrong_doc_for_id` (identifier resolution returns the neighbouring card), `stale_card` (card panel served from a mutated copy), `reverse_edges` (from/to swapped in the lineage view), `broken_jump` (line anchor off by 50), `console_error` (a template emits `throw new Error(...)`). The probe must flag each.

## 7. Decision records

| # | Decision | Alternatives considered | Evidence / constraint | Rejected because | Evidence that would justify revision |
|---|---|---|---|---|---|
| A1 | Markdown rendered with `markdown-it-py` (`html=False`, tables) -- a new local dependency | (a) Python-Markdown; (b) hand-rolled renderer; (c) serve raw text only | PROMPT.md reader ("render canonical markdown safely"); Standing Constraint 5 (local); O28 typography | (a) enables raw HTML by default and its extensions vary; (b) reimplements a solved problem and risks fidelity; (c) fails the reader's legibility bar | A fidelity defect in `markdown-it-py` on RHACO documents found by the probe or critic |
| A2 | No HTMX; plain forms and full-page renders; vanilla JS only for the graph and keyboard shortcuts | HTMX from a vendored file | PROMPT.md Proposed Stack lists HTMX "where useful"; Standing Constraint 5; O11 | No external asset is allowed and vendoring adds a 15 KB script for interactions the probe can verify more simply as full-page responses | Critic evidence that page reloads impede comprehension in W4/W5 |
| A3 | Catalog facets via documented parameterized SQL over `cards` / `card_programs` / `card_tags` (D-Q2..D-Q6) | (a) load all cards into memory per request and filter in Python; (b) reuse `search_fts` filters only | PROMPT.md corpus_adapter rules (direct SQL allowed for documented read-only facet queries when no API provides them); I1 section 7 (no API filters beyond doc_type/path_glob) | (a) reads 1,442 rows per page view for no benefit; (b) cannot express status / program / tag | A module API that exposes catalog queries |
| A4 | Vector availability decided by the adapter before each hybrid call (env flag, `vec_version()`, vec table meta, one-item `embed_query_cpu` probe; cached 5 s) | Trust the module's silent degradation and infer from result shape | O4; I1 section 6 (degradation raises nothing) | Result shape cannot distinguish a degraded hybrid from a real one; the label would lie | A module API that reports the effective channels of a search call |
| A5 | Document URL key = relative POSIX path of the `.card.yaml` under the docs root (`card_ref`); identifier pages list every row for an id | (a) `doc_id` as the key; (b) `cards.rowid` | O7 (shared ids; PRIMARY KEY `yaml_path`); rowid is rebuilt on every full reindex | (a) ambiguous for amendments and versions; (b) unstable | n/a |
| A6 | `amends` edges mapped to cards via filename stem (`from_id` = stem) | Treat `from_id` as a doc_id | O8 (I2 section 3, `emit_edges` lines 948-955) | The stem is not a doc_id; a doc_id lookup would silently miss every amendment | Module change to edge identity |
| A7 | Hybrid/graph excerpts obtained by a labelled lexical lookup inside the returned document; absent when there is no literal match | (a) reimplement chunk retrieval to show the matched chunk; (b) show nothing | PROMPT.md 5.3 ("directly derived without reconstructing ranking logic"); O6 | (a) reconstructs retrieval internals; (b) loses the "where in the document" answer when a literal match exists | A module API exposing the matched chunk |
| A8 | Freshness computed only on operator request (POST on diagnostics), card-level, never acted on | (a) compute on every diagnostics load; (b) background refresher | O9 (scan reads the whole corpus); O12 (no background processes) | (a) makes diagnostics slow and hits the corpus on every view; (b) violates D-3 | Evidence that the scan costs < 1 s on this host |
| A9 | One `connect()` per request after an `isfile` guard; 5 s cache for meta and availability | Long-lived connection | O10 (index moves; `connect()` creates a missing db) | A long-lived connection can hold stale schema state across an external reindex and cannot guard the create-on-open behaviour | Module `connect()` gaining a `create=False` flag |
| A10 | Path confinement by `realpath` + `normcase` prefix check against the docs root, accepting both junction and physical spellings | String prefix on the junction spelling only | O1, O13 (index rows spelled either way) | Rejects valid physical-path rows and would let `..` segments through | n/a |
| A11 | Hybrid-rerank absent from every UI path; diagnostics reports standing + artifact presence only | Labelled experimental surface that can run it | S3, O17; docs/REFERENCE.md (~26 min/query, FAIL) | A ~26-minute request on an interactive surface is a self-inflicted timeout and would elevate a rejected mode | New ratified RHACO evidence (PROMPT.md section 6) |
| A12 | Fixture index built by `fixtures/build_fixture_index.py`: db path by argument, `BODY_SCAN_ROOT` monkeypatched in-process, path assertion before any write | (a) copy and edit the module; (b) build a fixture index by hand with custom SQL | O3; PROMPT.md section 11 (`BLOCKED`); DISPATCH_PARAMETERS.md item F | (a) blocked; (b) would not be "through the module's own functions" and would drift from the real schema | n/a |
| A13 | Fault injection for probe qualification lives in `explorer/faults.py`, gated by `RHACO_EXPLORER_FAULT` **and** a fixture-db path check | Mutating the fixture corpus files per case | PROMPT.md section 2 ("controlled fault injection ... Do not corrupt the live RHACO corpus or live index") | File mutation is slower, leaves state behind, and cannot produce a runtime console error | n/a |
| A14 | Server-rendered pages plus JSON twins under `/api/` | HTML only | PROMPT.md probe requirements (observed result ids, active mode, selected document) | DOM scraping alone is brittle; the JSON twin lets the probe cross-check what the page claims | n/a |
| A15 | Builders run in separate git worktrees on module branches created by the integrator **inside the workspace root** (`git worktree add .worktrees/<module> -b build/<module>`; `.worktrees/` is gitignored); the integrator merges with `--no-ff`; builders run the main workspace's `.venv` interpreter | (a) Workflow-managed isolation; (b) sibling directories beside the workspace | DISPATCH_PARAMETERS.md items A and J (the workspace root is the only tree the build may mutate); PROMPT.md section 4 | (a) the tool's automatic worktree lifecycle is not observable from the record; (b) a sibling directory is a write outside the workspace root | n/a |
| A17 | Builders may write exactly one file outside their module paths: their round report `docs/rounds/R<nn>_<module>.report.md`; every other `docs/` write is the integrator's | Reports returned only in the strand's final message | PROMPT.md section 10 (builder round reports under `docs/rounds/`) | A report that exists only in a transcript is not an evidence artifact | n/a |
| A18 | In-process tests use FastAPI's `TestClient` (`httpx`, added as a dev dependency); no test launches a server process -- only the probe does | Tests spawning `uvicorn` | O12 / D-3 (foreground child only through the probe) | A test-spawned server is a second launcher of the production process | n/a |
| A19 | **DOM state convention** (round-1 change requests from the probe and diagnostics builders): every page sets `data-mode="<mode_effective>"` and, where it applies, `data-vector="available|unavailable"` on the document root `<html>` through `base.html`'s `{% block html_attrs %}`; the open document's element carries `data-selected-doc-id="<doc_id>"`; every rendered result row carries `data-doc-id="<doc_id>"`; `base.html` also exposes `{% block main_attrs %}` on `<main>`. The probe reads exactly these three observations (section 4.8) | Markup-specific scraping per page | PROMPT.md section 2 (probe records active mode, selected document, observed result ids) | Scraping couples the probe to each template's structure and breaks on any layout change | n/a |
| A20 | Post-merge invalidated tests are repaired by the integrator and recorded as #3 disposition evidence (DISPATCH_PARAMETERS.md item J): round 1 -- three diagnostics tests that relied on the adapter module being unbuilt now use the explicit `explorer.app.ADAPTER_ABSENT` sentinel; one test that relied on no probe-run directory now patches the runs glob to a temporary directory | Leaving the tests red until the owning builder's next round | PROMPT.md section 4 ("Revalidate all dependent evidence after a contract change") | A red integration tree would block every other module's round on a known, mechanical cause | n/a |
| A16 | Dev dependencies added: `markdown-it-py`, `mdit-py-plugins` (tables), `ruff` | -- | PROMPT.md section 11 ("add local dependencies consistent with the stack policy") | -- | -- |

## 8. Dependency waves and round plan (PROMPT.md section 4; budgets 4 rounds/module, 28 total)

- **Wave 1 (round 1):** `corpus_adapter`, `probe`, `diagnostics` -- three Sonnet 5 builders, three worktrees, one wave (the cap). Integrator pre-lands `explorer/app.py` (factory, `/healthz`, template loader), `config.py`, `models.py`, `faults.py` stubs, `requirements.txt`, `tools/l1_index_write_check.py` before dispatch so the contracts are concrete.
- **Wave 2:** `catalog`, `search`, `reader`. **Wave 3:** `lineage`, `web` polish; then the L4 oracle run, acceptance workflows, critic.
- A builder round ends with: L1 (ruff + pytest + index-write grep) green in the worktree, a round report in `docs/rounds/R<nn>_<module>.report.md`, and the integrator's `--no-ff` merge to `main`; `build_state.json` records round, gates, issues, and the dispatch record.
