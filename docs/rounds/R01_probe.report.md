# R01_probe -- round report (task B2)

## Header

- Hand: RHACO-HND-20260903-001 section 2 I as amended by A1.3
- Strand: B2 (module builder, probe), tier mid, agent_type general-purpose write-scoped to the worktree
- Model: You are powered by the model named Sonnet 5. The exact model ID is claude-sonnet-5.
- Worktree: `C:\highsierralabs\RHACO_Corpus_Explorer\.worktrees\probe`
- Branch: `build/probe`
- t_start_utc: 2026-09-04T03:17:53Z (see "Deviations" below -- approximate, not captured at the literal first tool call)
- t_end_utc: 2026-09-04T03:31:20Z (captured via `(Get-Date).ToUniversalTime().ToString("o")`)
- Round: 1 of budget 4 (module), task B2 (build the production-path probe framework and the fixture substrate)

## Change

Landed, inside the worktree, on owned paths only:

1. **`fixtures/corpus/`** -- a nine-document synthetic RHACO-shaped corpus (7 cards outside `docs_archive/` + 1 archived + 1 uncarded `.txt`), Card Schema v1.9-conformant, laid out as `reports/`, `handoffs/`, `reference/`, `docs_archive/`. Full inventory table below.
2. **`fixtures/build_fixture_index.py`** (+ `fixtures/__init__.py` package marker) -- the sole allowlisted caller of the five index-writing functions; CLI (`--docs-root`, `--db`, `--force`) and importable `build(docs_root, db_path, force=False) -> dict`. Path-safety assertion runs before any read or write; `RHACO_corpus_index.BODY_SCAN_ROOT` is monkeypatched in-process only, restored in a `finally` block.
3. **`tools/probe_corpus_explorer.py`** -- the production-path probe: server lifecycle (foreground child, `/healthz` readiness wait bounded at `--timeout`, `terminate()`-then-`kill()` teardown in a `finally` block), a `PRESET_REGISTRY` of 18 entries (`healthz`, `diagnostics`, `W1`-`W10`, `KG`, `KB1`-`KB5`), three preset runner kinds (`json_endpoint`, `page`, `not_implemented`), per-preset JSON + screenshot output, and `run_summary.json`.
4. **`tests/probe/test_fixture_builder.py`** (11 tests) and **`tests/probe/test_probe_smoke.py`** (1 test) -- 12 tests total, all green.
5. **`docs/probe-qualification/README.md`** -- layout and convention documentation for the evidence area.
6. **`docs/probe-qualification/runs/20260904T033047Z/`** -- one canonical `--preset all` evidence run against the fixture index (18 preset outputs + `run_summary.json` + `server.log`).
7. This report.

No file outside the owned paths (`tools/probe_corpus_explorer.py`, `fixtures/**`, `tests/probe/**`, `docs/probe-qualification/**`, this report) was touched. `explorer/app.py`, `explorer/config.py`, `explorer/models.py`, `explorer/faults.py` were read only.

## Evidence

Checks actually run, in order, with results:

| # | Check | Command | Result |
|---|---|---|---|
| 1 | Manual fixture build | `python fixtures/build_fixture_index.py --docs-root fixtures/corpus --db fixtures/fixture_index.db --force` | `cards=7 fts_docs=8 edges=7 edges_unresolved=1 id_aliases=11 orphan_cards=0 missing_cards=0 broken_yamls=0` |
| 2 | Manual DB inspection | ad hoc script: `RHACO_corpus_index.resolve_identifier("E000777", ...)`, `resolve_identifier("RHACO-HND-20260115-003", ...)`, raw `edges`/`cards` SELECTs, `search_fts("quartz lattice lantern", ...)` | `resolve_identifier("E000777") == ["RHACO-EVT-20260115-004"]`; 2 card rows for `RHACO-HND-20260115-003`; `amends` edge `RHACO-HND-20260115-003_Fixture_Handoff_Amendment_A1 -> RHACO-HND-20260115-003`; 2 `campaign_child` edges (CMP->ANL, CMP->HND); 1 unresolved `cites` edge `RHACO-HND-20260115-003 -> RHACO-ANL-20260101-099` (`resolved=0`); 1 `supersedes` edge `RHACO_Fixture_Reference_v1_0 -> RHACO_Fixture_Reference_v1_1`; `search_fts` returns the ANL doc at `line_no=15`; `docs_archive` absent from both `cards` and `fts_docs` (`count=0` both) |
| 3 | Refusal-path manual check | ad hoc script: `build()` against `RHACO_corpus_index.DEFAULT_DB`, against `C:\RHACO\index\evil.db`, against `C:\highsierralabs\RHACO\index\evil2.db` | All three raised `ValueError` before any write; no `evil*.db` files created; live `DEFAULT_DB` size unchanged (115093504 bytes, matches `build_state.json`'s pinned figure) |
| 4 | Probe manual run, `--preset healthz` | `python tools/probe_corpus_explorer.py --db fixtures/fixture_index.db --docs-root fixtures/corpus --preset healthz ...` | exit 0, `verdict=PASS`, `healthz.json` `ok=true http_status=200 body.status="ok"` |
| 5 | Probe manual run, `--preset diagnostics` | same, `--preset diagnostics` | exit 0, `verdict=PASS`; `diagnostics.json` `http_status=404 route_absent=true ok=true` (route not merged into this worktree yet -- the accepted state); one console error and one failed response recorded; screenshot saved |
| 6 | Probe manual run, `--preset all` | same, `--preset all` (18 presets) | exit 0, `verdict=PASS`; all 16 `not_implemented` presets report `status="not_implemented_yet" ok=true`; this is the evidence run committed at `docs/probe-qualification/runs/20260904T033047Z/` |
| 7 | Probe CLI error paths | `--preset bogus` | exit 2, `ERROR: unknown preset 'bogus'. Known presets: ...` (argparse `--db`/`--docs-root` required also verified by omission during iteration) |
| 8 | Gate (a) ruff | `C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m ruff check explorer tools tests --output-format concise` | `All checks passed!` exit 0 |
| 9 | Gate (b) pytest | `C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m pytest tests/probe -q` | `12 passed in 1.69s` exit 0 |
| 10 | Gate (c) L1 index-write check | `C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe tools/l1_index_write_check.py` | `hits=6 allowlisted=6 defects=0 verdict=PASS` exit 0 (all 6 hits are inside `fixtures/build_fixture_index.py`, the sole allowlisted file) |

Every "tested" claim above names the test or command that produced it; every count in the fixture inventory table below was read back from the built index (check #2), not merely asserted.

### Fixture inventory table

Fixture ids are dated `2026-01-xx` (no collision with any real RHACO id). Docs root: `fixtures/corpus/`.

| File | Card id (`doc_id`) | Purpose | Known facts |
|---|---|---|---|
| `reports/RHACO-CMP-20260115-001_Fixture_Campaign.{md,card.yaml}` | `RHACO-CMP-20260115-001` | Campaign root; `status: Active`, `lifecycle_state: OPEN` | 2 `campaign_child` edges point at it as `from_id` (to ANL and HND) |
| `reports/RHACO-ANL-20260115-002_Fixture_Analysis.{md,card.yaml}` | `RHACO-ANL-20260115-002` | Campaign child #1; carries the unique lexical marker; 2 programs + 3 tags | `depends_on` CMP (1 `cites` + 1 `campaign_child` edge); programs `[DetPhys, Radon]`; tags `[fixture-analysis, quartz-lattice, corpus-explorer]`; body line **15** = `the quartz lattice lantern glows only in this fixture document` (verified: `search_fts("quartz lattice lantern")` returns exactly this doc at `line_no=15`) |
| `handoffs/RHACO-HND-20260115-003_Fixture_Handoff.{md,card.yaml}` | `RHACO-HND-20260115-003` | Campaign child #2; carries the unresolved reference; amendment parent | `depends_on` CMP (resolved) + `RHACO-ANL-20260101-099` (deliberately absent -> 1 `cites` edge with `resolved=0`) |
| `handoffs/RHACO-HND-20260115-003_Fixture_Handoff_Amendment_A1.{md,card.yaml}` | `RHACO-HND-20260115-003` (shared with its parent by design, Card Schema v1.9 section 5.9) | Amendment child of the HND | `parent: {id: RHACO-HND-20260115-003}`, `amendment_seq: "A1"`; 2 `cards` rows share `doc_id=RHACO-HND-20260115-003` (verified); 1 `amends` edge `from_id` = the amendment's own filename stem `RHACO-HND-20260115-003_Fixture_Handoff_Amendment_A1`, `to_id=RHACO-HND-20260115-003` |
| `reference/RHACO_Fixture_Reference_v1_0.{md,card.yaml}` | `RHACO_Fixture_Reference_v1_0` (REF -> empty `canonical_id`, falls back to filename stem) | Superseded reference version | `status: Superseded`, `superseded_by: {id: RHACO_Fixture_Reference_v1_1}` -> 1 `supersedes` edge, `resolved=1` |
| `reference/RHACO_Fixture_Reference_v1_1.{md,card.yaml}` | `RHACO_Fixture_Reference_v1_1` | Current reference version (chain head) | `status: Active`, `superseded_by: null` |
| `reports/RHACO-EVT-20260115-004_Fixture_Event_E000777.{md,card.yaml}` | `RHACO-EVT-20260115-004` | Event fixture carrying a logger id | Filename AND title both contain `E000777`; `resolve_identifier("E000777")` returns `["RHACO-EVT-20260115-004"]` (verified) |
| `reports/RHACO_Fixture_Loose_Notes.txt` | none (uncarded, see below) | The one `.txt` body | Picked up by `iter_body_docs()` (`BODY_SUFFIXES = (.md, .txt)`) but invisible to `walk_library()`'s doc list (`LIBRARY_DOC_GLOB_SUFFIXES` has no `.txt`) -- body-indexed, never carded, never a `missing_cards` finding |
| `docs_archive/RHACO-OBS-20260101-001_Fixture_Archived.{md,card.yaml}` | `RHACO-OBS-20260101-001` | Must NOT be indexed | `docs_archive/` is pruned by both `RHACO_tool_catalog_librarian.DENY_DIRS` and `RHACO_corpus_index.BODY_DENY_DIRS` at any depth; verified absent from both `cards` and `fts_docs` (count 0 both) |

Index totals from a fresh `--force` build: `cards=7, fts_docs=8, edges=7 (1 unresolved), id_aliases=11`. `id_aliases=11` reconciles as: 4 canonical-form cards each contribute 2 aliases (canonical + bare `TYPE-DATE-SEQ`) -- CMP, ANL, HND, Amendment = 8; the EVT card contributes 2 (canonical + bare) + 1 deduplicated `event_id` alias (`E000777` harvested from both filename and title, via a `set` union) = 3; total 11. (The two REF cards contribute none -- `canonical_id` is empty for `doc_type: REF`, and alias derivation is gated on the canonical-id regex.)

**REF-pair walk acceptance (task-specified confirmation step).** The task instructed: build the reference pair, confirm the builder's walk accepts it, and only move `v1_0` to `docs_archive/` if it does not. It does: `doc_type: REF` cards have an empty `canonical_id` (`RHACO_tool_catalog_librarian.Card.canonical_id` returns `""` when `doc_type in ("", "REF")`), so `_build_id_index` never indexes them by canonical id and no `seq_collision`-shaped ambiguity is possible; both cards were confirmed present in `scan.cards` with `orphan_cards=0, missing_cards=0, broken_yamls=0` on every build. Both files stay in `reference/`.

## Material alternatives

- **`.txt` fixture: carded vs. uncarded.** Considered giving the `.txt` document its own card (it would land in `orphan_cards` since `LIBRARY_DOC_GLOB_SUFFIXES` has no `.txt`, so `matched_doc` would stay empty). Chose **uncarded** instead: it cleanly demonstrates the real divergence between the librarian's own document-extension list and `RHACO_corpus_index.BODY_SUFFIXES`, without an artificial orphan-card warning muddying the fixture's otherwise-clean scan (`orphan_cards=0`).
- **REF pair placement.** Considered following the task's explicit fallback (move `v1_0` to `docs_archive/` if the walk does not accept the pair). Rejected once direct testing (Evidence #1-2) confirmed the walk *does* accept the pair cleanly -- moving a working fixture into the excluded tree would have been a worse fixture (it would no longer exercise the `supersedes` edge at all, since a `docs_archive/`-resident card is invisible to `scan.cards`).
- **KB1-KB5 <-> `FAULTS` mapping.** Considered leaving the five known-bad qualification cases unordered/generic. Chose a **fixed positional mapping** onto `explorer.faults.FAULTS`'s declared tuple order (`wrong_doc_for_id, stale_card, reverse_edges, broken_jump, console_error` -> `KB1..KB5`) so the mapping is traceable to one source of truth and wave 2's real runners have an unambiguous assignment to fill in.
- **`diagnostics` preset kind.** Considered treating it as a `json_endpoint` preset (like `healthz`) since it 404s today. Chose **`page`** kind instead, because ARCHITECTURE.md section 4.6 specifies diagnostics as a server-rendered HTML page with a JSON twin -- registering it as `page` now means wave 3 does not need to change the preset's `kind`, only its assertions, once the diagnostics module merges.
- **`--db`/`--docs-root` defaults.** Considered defaulting them to the module's own live constants (mirroring `explorer.config.Settings`'s `None -> RHACO_corpus_index.DEFAULT_DB` pattern). Chose **required, no default**: the probe is D-12/O12's sole sanctioned server launcher, and a silent default to the 115 MB live index is exactly the kind of omission that pattern is meant to foreclose. Every invocation must name its database.
- **`sys.path` bootstrap style.** Considered relying on import order between `fixtures.build_fixture_index` (which mutates `sys.path`) and a direct `import RHACO_corpus_index` in the test file. Rejected after `ruff --fix`'s import-sort reordered the two statements and broke this exact dependency in `tests/probe/test_fixture_builder.py` (caught by re-running pytest after the lint pass, Evidence #8-9 sequence during the round); fixed by giving the test file its own explicit, order-independent `sys.path` bootstrap via `explorer.config.RHACO_PATH_ENTRIES`, matching `fixtures/build_fixture_index.py`'s own pattern.

## Decisions

- Fixture corpus and index are fully deterministic given the files on disk; every count in the inventory table above was read back from a fresh `--force` build, not merely asserted.
- `fixtures/build_fixture_index.py` performs the db-path safety assertion (not `DEFAULT_DB`, not under either spelling of the RHACO tree) as the literal first step of `build()`, before the docs-root check, before the librarian scan, before any `connect()` -- proven by the three refusal tests (no stray file, live `DEFAULT_DB` sha256 unchanged).
- The probe's preset registry establishes three DOM attribute conventions (`data-mode` on the document root, `data-selected-doc-id`, `data-doc-id`) for later builders' templates to emit -- see "Change requests" below.
- `--preset all` runs every registry entry in one invocation and exits 0 only when every entry's own "ok" criterion holds (json_endpoint: `status=="ok"`; page: no navigation/extraction exception, a 404 counted as `route_absent` not failure; not_implemented: always clean).

## Result

**COMPLETE.** All three required gates pass with the exact specified commands (Evidence #8-10). 12/12 tests green. The fixture corpus, builder, probe, and tests satisfy every enumerated deliverable in the dispatch (fixture layout and contents, `build_fixture_index.py`'s CLI/import/order-of-operations/summary contract, the probe's CLI/env/readiness/preset-output/registry contract, and both required test files' assertions). Worktree left clean after commit (see `git rev-parse HEAD` in the structured result).

## Unresolved uncertainty

- **W1-W10 / KG / KB1-KB5 are stubs**, by design this round (dispatch: "filled in wave 2"); their real runners, once catalog/search/reader/lineage exist, are UNVERIFIED beyond "reports `not_implemented_yet` cleanly."
- **The `diagnostics` preset's behavior against a real diagnostics page is UNVERIFIED** -- only the current 404 "route absent" path was exercised in this worktree, since the diagnostics builder's work is not merged here.
- **The `data-mode`/`data-selected-doc-id`/`data-doc-id` DOM convention is a proposal, not a ratified contract** -- no template exists yet to confirm it against.
- **t_start_utc is approximate** (see Header) -- the session-start timestamp command was not run at the literal first tool call; the value recorded is the creation timestamp of the first fixture file written, read back via `Get-Item ... .CreationTimeUtc`.
- Whether `healthz`'s "required observation" should also assert `body["db"]`/`body["docs_root"]` match the requested `--db`/`--docs-root` (beyond `status=="ok"`) was a judgment call; ARCHITECTURE.md section 4.8 states readiness as "`GET /healthz` returning status `ok`" only, so the preset's pass criterion mirrors that literally.

## Change requests

- **Requestor:** probe (B2). **Affected contract/path:** `explorer/web/templates/base.html` and every module's own templates (`explorer/catalog/templates/`, `explorer/search/templates/`, `explorer/reader/templates/`, `explorer/lineage/templates/`, `explorer/diagnostics/templates/`) -- none built yet. **Change:** adopt three DOM attribute conventions so the probe (and the wave-2 W1-W10/KB1-KB5 runners built on this framework) can read page state without scraping page-specific markup: `data-mode="<mode_effective>"` on the document root (`<html>`) when a page has an active retrieval mode; `data-selected-doc-id="<doc_id>"` on the element marking the currently-open/selected document; `data-doc-id="<doc_id>"` on every rendered result-row element. **Evidence:** ARCHITECTURE.md section 4.8 already specifies these three observations in exactly this shape ("read the root element's data-mode attribute when present... elements with data-doc-id when present... selected document id"); this request makes the literal attribute names concrete since no template exists yet to originate them, and `tools/probe_corpus_explorer.py`'s `_extract_dom_observations()` already reads them by these names. **Compatibility impact:** none -- additive template attributes only, no behavior change. **Migration:** none (the consuming templates do not exist yet). **Invalidated tests/probes:** none.

## Assumptions

- KB1-KB5 map 1:1, in order, onto `explorer.faults.FAULTS` (`wrong_doc_for_id, stale_card, reverse_edges, broken_jump, console_error`).
- "`build_fixture_index.py` builds into tmp_path" (test spec) means the **index** (db file) is built under `tmp_path`; the fixture **corpus** (`fixtures/corpus/`) stays the committed, read-only tree at its real path -- no per-test copy of the corpus.
- `--db` and `--docs-root` are required CLI arguments with no default, so the probe can never launch against the live index by omission.
- The `healthz` preset's pass criterion is exactly `body.get("status") == "ok"`, matching ARCHITECTURE.md section 4.8's readiness definition verbatim.
- A page preset whose main navigation returns HTTP 404 is a valid, accepted, non-failing observation ("route absent") this round, per the explicit `diagnostics` instruction; only an actual navigation/extraction exception fails a page preset.
