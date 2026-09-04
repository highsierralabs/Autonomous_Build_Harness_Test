# docs/LAYERS.md -- verification layers and shared-dependency register (PROMPT.md section 3)

Written 2026-09-04 at PROMPT.md section 14 step 6 (after the adapter and probe were dispatched). The layers below are **not independent**: L2, L3, and L4 share the substrate, the database, the adapter code, and (for L3) the L2 capture path. Agreement across them is evidence of consistency, not of independent confirmation.

## 1. Layers as built

| Layer | Mechanism in this build | Primary purpose | Runs where |
|---|---|---|---|
| **L1 Static** | `ruff check explorer tools tests` (rules pinned in `ruff.toml`); `pytest tests/` (per-module unit tests, in-process `TestClient`, fake adapters where a module is built ahead of its dependency); `tools/l1_index_write_check.py` (the five index-writing names appear only in `fixtures/build_fixture_index.py`); template render smoke (`base.html` renders with the authority notice) | contract and implementation errors; the index-write prohibition | every builder worktree before its round closes; the integrator after every merge |
| **L2 Runtime probe** | `tools/probe_corpus_explorer.py` (Playwright, Chromium headless, 1280x900) driving the real server, which it launches as its own foreground child; presets W1-W10 plus qualification cases KG, KB1-KB5; per preset a screenshot, a JSON observation (url, mode, selected document, observed result ids, console errors, failed requests, timings), and `run_summary.json` | actual search / navigation / rendering behavior on the production path (live db) and on the fixture path (qualification) | integrator, after each wave; results under `docs/probe-qualification/runs/<utc>/` |
| **L3 Critic** | a separate Opus 5 strand (read-only, Explore type, effort set explicitly per DISPATCH_PARAMETERS.md item I) that writes no code, reads the L2 screenshots + JSON, the templates, and the acceptance-workflow records, scores `ref_score` 0-10 after the objective gates, and returns a ranked issue set; the integrator files it under `docs/critique/` | usability, fidelity, epistemic presentation, missed integration problems | after the acceptance workflows run (PROMPT.md section 14 step 14) |
| **L4 Corpus oracle checks** | `tools/l4_gold_oracle.py`: for each Gold v1.1 row, the adapter's `search_hybrid` ids **and** the module's direct `search_hybrid` ids on the same live index, list equality asserted, Recall@10 computed with `any-target-in-top-10` (honoring `resolve: supersession-head` through the adapter's supersession chain); exact fixture assertions in `tests/probe/test_fixture_builder.py` (identifier -> document, phrase -> line, edge direction, unresolved reference, archive exclusion) | retrieval / relationship correctness against known targets; the adapter did not degrade the module | integrator, after the search module merges and again at closeout |

## 2. Shared dependencies (who depends on what)

| Dependency | L1 | L2 | L3 | L4 | Note |
|---|---|---|---|---|---|
| `C:\RHACO\rhaco\RHACO_corpus_index.py` (module code, sha256 `7548e47e...`) | import-time only (adapter tests) | yes -- every search and lookup on the page | indirectly (reads L2 output) | yes -- both the adapter path and the module-direct path call the same code | A retrieval defect in the module appears identically in L2 and L4; L4's equality check can only show that the adapter matches the module, never that the module is right |
| `C:\RHACO\index\corpus_index.db` (live derived index; open pin `274c1e96...`) | adapter tests read it | yes (production-path presets) | indirectly | yes | One file, reindexed by external actors during the build (CONSTRAINTS O10); a stale or drifted index affects L2 and L4 the same way; freshness is reported, never fixed |
| `fixtures/corpus/` + `fixtures/fixture_index.db` | fixture-builder tests | yes (qualification presets KG, KB1-KB5) | indirectly | yes (fixture exact assertions) | Built by one script from one fixture set; a fixture authoring error is invisible to every layer that uses it |
| Browser capture path (Playwright + Chromium 151; screenshots, DOM reads, console/network capture) | no | yes -- the whole layer | **yes** -- the critic reads L2's screenshots and JSON, so an L2 capture defect propagates into L3 | no | L3 is therefore not independent of L2 |
| Frozen gold set `C:\RHACO\working\eval\gold_queries.yaml` (v1.1, 40 rows, `f20bc6a2...`) | no | W3 uses a gold query | indirectly | yes -- the whole compatibility check | A mis-specified gold target fails L4 without any UI or adapter fault; the set is frozen, so this is detectable but not fixable by the build |
| Card / document filesystem under `C:\RHACO\docs\**` | adapter tests read cards | yes (reader body from disk, card panel) | indirectly | yes (`resolve: supersession-head` walks edges derived from cards) | The record itself; a malformed card is a corpus fact, surfaced, not corrected |
| Ollama embedder at `127.0.0.1:11434` + sqlite-vec | availability probe test | yes (hybrid presets; W7 disables it) | indirectly | yes (hybrid oracle) | Same process on the same host for L2 and L4; unavailability degrades both identically and is a valid state (REFERENCE.md consequence 5) |
| The adapter code (`explorer/corpus_adapter/`) | its own tests | yes (everything goes through it) | indirectly | yes -- with the module-direct path as the only cross-check | The adapter is the single funnel; L4's module-direct comparison is the one place a layer bypasses it |
| The integrator's own wiring (`explorer/app.py`, models) | yes | yes | indirectly | yes | A wiring defect can make every layer agree on a wrong page |

## 3. Independence claims we do not make

- L2 and L4 are **not** independent measurements of retrieval: both call `search_hybrid` on the same db through the same adapter.
- L3 is **not** independent of L2: it evaluates L2's captures.
- Passing L1 says nothing about retrieval correctness; it says the code compiles, lints, and the index-write prohibition holds.
- The fixture path is **not** the production path: qualification on the fixture proves the probe can detect the five known-bad classes; product claims still require the production-path presets (PROMPT.md section 2).

## 4. When layers disagree (PROMPT.md section 3 protocol, as applied here)

1. Record the disagreement in the round report and `build_state.json` (`open_issues`).
2. Identify the shared dependencies from the table above that both layers touch.
3. Distinguish UI defect from retrieval defect: run the module-direct call (`RHACO_corpus_index.search_hybrid` / `search_fts` / `resolve_identifier`) for the same input and compare with the adapter's result (the L4 equality path); if they agree, the defect is above the adapter; if they differ, it is in the adapter.
4. Run the smallest discriminating check (a single query, a single card, a single edge) and record it.
5. Leave the disagreement unresolved, visible, when evidence cannot decide. A broken RHACO retrieval result is not a UI bug and is not "fixed" in this build.
