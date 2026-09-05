# R05_reader -- round report (task B11)

## Header

- Dispatch: RHACO-HND-20260903-001 section 2 I as amended by A1.3.
- Strand: S6-B11, reader builder, production-path defect repair, tier mid,
  agent_type general-purpose write-scoped to the worktree.
- Model: You are powered by the model named Sonnet 5. The exact model ID is
  claude-sonnet-5.
- Worktree: `C:\highsierralabs\RHACO_Corpus_Explorer\.worktrees\reader`.
- Branch: `build/reader`. Base commit `e36d9d69ec5e915bd554b658c3cbcc82fe5c1f4f`
  (the integrator's placement) -- confirmed by `git -C .worktrees\reader
  rev-parse HEAD` **before** any other action, per the dispatch's "first git
  act"; it matched, so no fast-forward was needed.
- Round: **reader module round 2 of 4** (task B11's own item 4 requirement to
  state this plainly).
- Prompt of record: `docs/rounds/R05_reader.prompt.md`, sha256
  `38cf028a84cbe1b10f042b366cbf1c4eb08e07655a020a2b2bfea1abc763e1ef` -- confirmed
  via `Get-FileHash -Algorithm SHA256` (case-insensitive match to the dispatch
  header) before reading the file's content or acting on it.
- t_start_utc: `2026-09-05T04:46:45Z` (first tool call,
  `(Get-Date).ToUniversalTime().ToString("o")`).
- t_end_utc: see the structured result (same command, run again at close).

## Change

Landed, inside the worktree, on owned paths only
(`explorer/reader/**`, `tests/reader/**`, this report):

1. **`explorer/reader/service.py`** -- the serialization repair (task
   deliverable 1):
   - `_json_safe(value)` (new, ~line 245): a recursive, pure conversion of any
     structure `yaml.safe_load` can produce into one `json.dumps` can always
     serialize. `datetime.date` / `datetime.datetime` / `datetime.time`
     (the native types PyYAML resolves an **unquoted** ISO-shaped scalar to)
     become their own `.isoformat()` text; dicts and lists recurse; any other
     non-JSON-native leaf (`bytes` from `!!binary`, `set` from `!!set`, ...)
     falls back to `str()`. `str`, `int`, `float`, `bool` and `None` pass
     through unchanged.
   - `_parse_card_yaml` (line ~282) now returns `_json_safe(data)` instead of
     the raw `yaml.safe_load` result, applied **once**, immediately after
     parsing and before `identity`, `card_parsed`, `_index_mismatch`, or any
     `CardPanelView` field derived from `parsed` is built. Because both
     surfaces (`reader.html`'s `{{ view.card_parsed | tojson }}` and
     `routes.py`'s `JSONResponse(dataclasses.asdict(view))`, which Starlette
     serializes with plain `json.dumps`, no `default=` handler) consume the
     same `view.card_parsed` / the same `CardPanelView` fields built from the
     same `identity` dict, one conversion point fixes every field on both
     surfaces at once -- `card_panel.date`, `card_panel.last_human_review`,
     and the full `card_parsed` dump alike.
   - Two new module-level constants, `_TEMPORAL_TYPES` and
     `_JSON_NATIVE_LEAF_TYPES`, document the type sets by name.
   - `raw_text` (the `<details>` "Card source (.card.yaml)" block, O19/O28)
     is untouched: it is read by `adapter.read_card_text(card)` and passed to
     `_build_card_panel` **before** `_parse_card_yaml` ever runs, and
     `_json_safe` is never applied to it -- verified by inspection (it is a
     separate local variable in `build_view`, `service.py` lines 186-208) and
     by the end-to-end test's literal-text assertion (Evidence #9).
   - No change to `_index_mismatch` itself (task deliverable 2 -- see
     "Decisions" and Evidence #7/#8 for why none was needed).
2. **`tests/reader/test_service_unit.py`** -- six new unit-level tests (task
   deliverable 3, level 1): `_json_safe` over `date`/`datetime`/`time`, over
   nested dicts and lists, over a non-temporal exotic leaf (fallback `str()`),
   and over already-JSON-native leaves (pass-through); `_parse_card_yaml`
   over a literal unquoted `date:`/`last_human_review:` scalar (parse-level
   integration of the helper); and a direct `_index_mismatch` test answering
   task deliverable 2 (Evidence #7/#8, Decisions).
3. **`tests/reader/test_native_date_defect.py`** (new file) -- the end-to-end
   fixture test (task deliverable 3, level 2): copies `fixtures/corpus` into
   `tmp_path`, rewrites the ANL fixture card's `date:`/`last_human_review:` to
   the unquoted form, builds a fresh index over the copy via
   `fixtures.build_fixture_index.build`, and drives both `/doc/...` and
   `/api/doc/...`, asserting HTTP 200 on each, the rendered ISO text, no
   Python-repr leak, no false index-mismatch, and the raw source block still
   carrying the tmp copy's own literal (unquoted) characters. `fixtures/corpus/`
   itself is never modified -- only a `tmp_path` copy.
4. **`tests/reader/test_live_smoke.py`** -- two new tests (task deliverable 3,
   level 3): a live-index smoke on the exact document the probe's W6 run
   failed on, `reference/RHACO_Card_YAML_Schema_Specification_v1_8.card.yaml`,
   asserting HTTP 200 on both `/doc/...` and `/api/doc/...` and a non-empty
   card panel (the rendered `Date` field, not merely a 200 status), guarded by
   the same session-scoped `corpus_cards_sha` + mtime no-mutation check the
   existing live-smoke fixture already uses (`conftest.py`, unmodified this
   round).
5. This report.

No file outside these paths was modified. `explorer/app.py`, `explorer/config.py`,
`explorer/models.py`, `explorer/faults.py`, `explorer/web/**`,
`explorer/corpus_adapter/**`, `explorer/diagnostics/**`, `tools/**`,
`fixtures/**`, every other module's directory and tests, and every governance
document (`PROMPT.md`, `RATIONALE.md`, `CONSTRAINTS.md`, `ARCHITECTURE.md`,
`SCOPE.md`, `build_state.json`, `docs/LAYERS.md`, `docs/REFERENCE.md`,
`docs/probe-qualification/**`) were read only. `git status --short` before
either commit showed only files under `explorer/reader/` and `tests/reader/`.

## Evidence

Checks actually run, in order, with results:

| # | Check | Command | Result |
|---|---|---|---|
| 1 | Prompt hash verification | `Get-FileHash -Algorithm SHA256 docs/rounds/R05_reader.prompt.md` | `38CF028A84CBE1B10F042B366CBF1C4EB08E07655A020A2B2BFEA1ABC763E1EF` -- matched the dispatch header (case-insensitive) |
| 2 | Worktree base-commit confirmation | `git -C .worktrees\reader rev-parse HEAD` | `e36d9d69ec5e915bd554b658c3cbcc82fe5c1f4f` -- matched exactly; no fast-forward needed |
| 3 | Baseline gate before any change | `.venv\Scripts\python.exe -m ruff check explorer tools tests --output-format concise` then `-m pytest tests/reader -q` | `All checks passed!`; `34 passed` (the round-1 baseline, unchanged) |
| 4 | Root-cause confirmation (read-only, permitted path) | `cat "C:\RHACO\docs\reference\RHACO_Card_YAML_Schema_Specification_v1_8.card.yaml"` | `identity.date: 2026-06-24` and `identity.last_human_review: 2026-06-24`, both bare (no quotes) -- exactly the shape `yaml.safe_load` resolves to `datetime.date` |
| 5 | Blast-radius grep re-verified independently this round (read-only `find`/`grep` over `C:\RHACO\docs`, no db opened, no process spawned beyond `find`/`grep`) | `find . -iname "*.card.yaml" \| wc -l`; `grep -rlE '^\s*(date\|last_human_review):\s*[0-9]{4}-[0-9]{2}-[0-9]{2}\s*$' --include=*.card.yaml .` | `total_cards=1449 date_unquoted=870 last_human_review_unquoted=870 either_unquoted=872` -- matches `docs/rounds/R04_probe.report.md` Evidence #16 exactly (60.2% of the corpus) |
| 6 | Gate (a) ruff, after the fix + all new tests | `.venv\Scripts\python.exe -m ruff check explorer tools tests --output-format concise` | `All checks passed!` exit 0 |
| 7 | Gate (b) pytest (module), after the fix + all new tests | `.venv\Scripts\python.exe -m pytest tests/reader -q` | `44 passed` (34 pre-existing + 10 new: 6 `_json_safe`/`_parse_card_yaml`/`_index_mismatch` unit tests, 2 end-to-end fixture tests, 2 live-index smoke tests) exit 0 |
| 8 | `_index_mismatch` direct evidence (task item 2) | `test_index_mismatch_no_false_positive_for_native_date_vs_index_string` (part of gate 7) | **PASS** -- `_index_mismatch(card, {"date": datetime.date(2026,6,24), ...})` returns `[]`; no false "date" mismatch, proven directly against the unmodified `_index_mismatch` function, independent of this round's upstream `_json_safe` fix |
| 9 | End-to-end fixture proof (task item 3, level 2) | `test_reader_page_returns_200_and_shows_iso_text_for_unquoted_date`, `test_api_doc_returns_200_and_agrees_with_the_page` (part of gate 7) | **PASS** -- both `/doc/...` and `/api/doc/...` return 200 against a `tmp_path` copy of the fixture with an unquoted `date:`; rendered value `"2026-01-15"` (identical characters to what the tmp file says minus the quotes it never had); `"datetime.date"` and `"not JSON serializable"` both absent from the body; `data-card-index-mismatch=""`; the raw source block still literally contains `date: 2026-01-15` (unquoted, unchanged) |
| 10 | Live-index smoke on the exact failing document (task item 3, level 3) | `test_live_native_date_card_page_no_longer_500s`, `test_live_native_date_card_api_no_longer_500s` (part of gate 7), guarded by `conftest.py`'s session-scoped `corpus_cards_sha` + mtime check | **PASS** -- `GET /doc/reference/RHACO_Card_YAML_Schema_Specification_v1_8.card.yaml` -> 200 (was 500); `GET /api/doc/...` -> 200 (was 500); `data-selected-doc-id="RHACO_Card_YAML_Schema_Specification_v1_8"`; `<dt>Date</dt><dd>2026-06-24</dd>` present (non-empty card panel, not merely a 200); JSON twin's `card_panel.date == "2026-06-24"` and `card_parsed.identity.date == "2026-06-24"`; `corpus_cards_sha`/mtime unchanged before/after the whole session (autouse fixture assertion did not fail) |
| 11 | Gate (c) L1 index-write check | `.venv\Scripts\python.exe tools/l1_index_write_check.py` | `hits=6 allowlisted=6 defects=0 verdict=PASS` (all 6 hits inside `fixtures/build_fixture_index.py`, unmodified this round) |
| 12 | Full-tree regression | `.venv\Scripts\python.exe -m pytest tests -q` | `262 passed` (252 baseline across every module + 10 new reader tests) -- no interference with `corpus_adapter`, `catalog`, `search`, `lineage`, `web`, `diagnostics`, or `probe`'s own suites |
| 13 | Git cleanliness | `git status --short` after both commits | empty -- worktree clean |
| 14 | Commits | `git log --oneline -3` | `5c359d3 tests(reader): regression coverage for the native-date defect (B11)`; `d5f18f0 reader: make card-parsed view JSON-safe (fix native date/time 500)`; `e36d9d6` (base) |

Every "tested" claim above names the test or command that produced it. No
uvicorn process and no probe run were launched from this worktree (D-12/D-3):
every claim about the live corpus, including the exact card the probe's W6
run failed on, is re-derived here through `fastapi.testclient.TestClient`
in-process against the live index (`Settings()` defaults), per the dispatch's
own working rule 3 and the "Foreground only" / device-safety header.

### Item 4's other required statement: does any card-parse path outside `explorer/reader/**` share the defect?

`explorer/reader/service.py` is the only card-YAML parse path inside the
application (confirmed: the only other module that reads a `.card.yaml` file
directly is `explorer/corpus_adapter/adapter.py`'s `read_card_text`, which
returns raw *text*, never calls `yaml.safe_load`, and is out of this round's
scope to modify regardless). `tools/probe_corpus_explorer.py` (out of this
round's write scope; read-only inspection) has its own
`_parse_card_yaml_file` (line 861) which also calls bare `yaml.safe_load`
with no type conversion, so it **shares the same root-cause pattern** and
would produce the identical native `datetime.date`/`datetime.datetime` for an
unquoted scalar. By direct inspection of every one of its three call sites
(line 1349, KG(c) fixture check; line 1512, KB2 fixture check; line 1994, W5
independent check), **none of them currently extracts or serializes a
`date`/`last_human_review` field** from the parsed result -- only `title`,
`status`, and `depends_on[].id` (all already strings) are read out, and
`_run_w6` (the runner that failed) never calls `_parse_card_yaml_file` at
all, it only navigates pages and calls `/api/lineage`. So the defect is **not
currently reproduced** anywhere in `tools/probe_corpus_explorer.py` -- the
pattern is shared, the crash is not -- filed as an informational Change
Request below rather than fixed (out of this round's owned paths, working
rule 1).

## Material alternatives

- **Convert once at parse time vs. convert at each display site.** Considered
  leaving `_parse_card_yaml` returning the raw `yaml.safe_load` result and
  instead converting only the specific fields the template/API touch (e.g. a
  `_display_date(identity.get("date"))` call at each of `CardPanelView.date`,
  `.last_human_review`, and inside the `card_parsed | tojson` filter itself).
  Rejected: task requirement 3 ("apply it to BOTH surfaces... must agree")
  and requirement 2 ("total: any other non-JSON-native leaf... must also be
  rendered") are both satisfied for free by converting the whole parsed
  structure exactly once, immediately after `yaml.safe_load`, before any
  downstream consumer (`identity`, `_index_mismatch`, every `CardPanelView`
  field, the raw `card_parsed` dump) ever sees a native type -- one point of
  truth instead of N call sites that could individually drift, and it also
  answers task item 2 for free (see Decisions) rather than needing a second,
  separate fix.
- **Fallback for an unnamed exotic leaf: `str()` vs. a structured
  `{"__unrepresentable__": type_name, "repr": ...}` marker.** Considered a
  structured marker so a future consumer could distinguish "genuinely a
  string" from "we gave up and stringified something." Rejected: task
  requirement 2 says plainly "surface it plainly," and `raw_text` (the
  verbatim `<details>` block) already carries the actual original
  characters for anyone who needs to know exactly what the file said, so the
  parsed-fields dump's job is just to not crash and to show *something*
  legible -- a bare `str()` does that with no schema for callers to track,
  and matches the pattern already used one line up in `_norm()` for the
  index-comparison side (`str(value).strip()`).
- **Whether `_index_mismatch` needed a code change (task item 2).** Two
  candidate fixes were considered before writing the direct test the task
  requires: (a) change `_norm()` to special-case `datetime.date`/`datetime`
  explicitly (`.isoformat()` instead of `str()`), or (b) change nothing and
  rely on the fact that the upstream `_json_safe` conversion now means
  `_index_mismatch` never receives a native type in the first place. Direct
  test evidence (#8) showed a **third** fact that made the choice easy:
  `_index_mismatch`'s existing `_norm()` (`str(value).strip()`) was *already*
  correct for this case even before any fix, because `str(datetime.date(...))`
  IS `.isoformat()` for a `date` (Python's `date.__str__` is defined as
  `isoformat()`) -- and `RHACO_corpus_index._norm_date` (verified by reading
  `C:\RHACO\rhaco\RHACO_corpus_index.py` lines 575-590) stores the index's
  `date` column in that exact canonical form. So (a) would have been a
  no-op change to an already-correct function, and (b) required no change at
  all -- `_index_mismatch` is untouched this round; only its *input* is now
  guaranteed pre-converted as a side effect of the item-1 fix, which is
  belt-and-suspenders, not a fix to a bug that was found not to exist.

## Decisions

- **Task item 2's answer, stated plainly: the mismatch bug did NOT exist.**
  `_index_mismatch(card, identity)` compares `_norm(getattr(card, name))`
  against `_norm(identity.get(name))` for `name in INDEX_COMPARISON_FIELDS =
  ("title", "status", "lifecycle_state", "date", "doc_type")`. Of these, only
  `date` can ever be a native temporal type on the `identity` (card-file)
  side (a `.card.yaml`'s `title`/`status`/`lifecycle_state`/`doc_type` are
  never unquoted-ISO-shaped, so PyYAML never resolves them to a `date`).
  `_norm`'s `str(value).strip()`, applied to a `datetime.date`, produces
  exactly `.isoformat()` -- Python defines `date.__str__` that way -- which
  is exactly the canonical `'YYYY-MM-DD'` form `RHACO_corpus_index._norm_date`
  already normalizes the index's own `date` column to at index-build time.
  The two sides were therefore always equal for this corpus's data shape (a
  plain, time-free ISO date, confirmed the *only* shape present by the R04
  probe round's own grep, which this round independently re-ran and matched:
  Evidence #5), proven directly by `test_index_mismatch_no_false_positive_
  for_native_date_vs_index_string` (Evidence #8) against the **unmodified**
  `_index_mismatch` function, before any consideration of this round's
  upstream fix. **Zero mismatch fields were affected** by the bug this item
  asks about, because it never actually fired. This round's item-1 fix
  additionally guarantees `identity` is always string-only by the time
  `_index_mismatch` runs, closing off even the *possibility* going forward
  (e.g. if the corpus ever grew a `date:` scalar with a time component,
  which would have produced a `datetime.datetime` whose `str()` includes a
  `T...` suffix `_norm_date` strips via `.date().isoformat()` -- a case that
  does NOT occur in the present corpus per Evidence #5, but is now moot
  either way since `identity["date"]` is a plain ISO-date string in every
  case before comparison, not a native object).
- The JSON-safety conversion (`_json_safe`) is applied **once**, inside
  `_parse_card_yaml`, rather than at each of the several places `parsed`'s
  values reach a surface (`card_panel.date`, `.last_human_review`,
  `.schema_version`, the raw `card_parsed` dump, `_index_mismatch`'s
  `identity` argument) -- see "Material alternatives" for why.
- `raw_text` (the "Card source (.card.yaml)" `<details>` block) is
  structurally incapable of being affected by this fix: it is a separate
  local variable (`adapter.read_card_text(card)`, `service.py` line 186)
  read *before* `_parse_card_yaml` is even called, and `_json_safe` is never
  applied to it. O19/O28 fidelity for the raw block was therefore never at
  risk, and Evidence #9 confirms it directly (the tmp fixture's literal
  unquoted `date: 2026-01-15` text is still present verbatim in the
  rendered page).
- The end-to-end fixture test (Evidence #9) copies the **entire**
  `fixtures/corpus` tree into `tmp_path` rather than hand-authoring a
  minimal single-card fixture, so the rebuilt index's edges/programs/tags
  context (depends_on the CMP, etc.) stays consistent with every other
  reader test that already exercises the ANL fixture card -- one rewritten
  card in an otherwise-intact corpus, not a bespoke, narrower fixture that
  could silently diverge from what `test_reader_page.py`/`test_api.py`
  already assert about that same document.

## Result

**COMPLETE.** All four deliverables from the dispatch are done:

1. The serialization repair (`_json_safe` + `_parse_card_yaml`) is
   fidelity-preserving (Evidence #9: the tmp fixture's literal ISO text is
   what renders, not a Python repr), total (unit-tested against a
   non-temporal exotic leaf, Evidence #7), applied to both surfaces
   (Evidence #9, #10: page and API both 200 and agree), and leaves the raw
   `<details>` block untouched (Decisions, Evidence #9).
2. Task item 2's mismatch question is answered by direct test, not
   conjecture: **the bug did not exist** (Evidence #8, Decisions) -- zero
   mismatch fields were ever affected, because `_norm()`'s existing
   `str()`-based comparison already produced the canonical ISO form for a
   native `datetime.date`, matching the index's own `_norm_date`-normalized
   storage exactly.
3. Regression tests at all three required levels: unit (`_json_safe` over
   date/datetime/time/nested structures/an exotic leaf, plus
   `_parse_card_yaml` and `_index_mismatch` directly, 6 tests), end-to-end
   fixture (2 tests, a `tmp_path` copy with one card's dates unquoted, never
   touching the committed `fixtures/corpus/`), and live-index smoke on the
   exact failing document (2 tests, guarded by the existing
   `corpus_cards_sha` + mtime check).
4. Reported plainly: this is **reader round 2 of 4**; the item-2 mismatch bug
   did **not** exist (proven, not assumed); `tools/probe_corpus_explorer.py`
   shares the same unguarded-`yaml.safe_load` *pattern* but does not
   currently *reproduce* the defect at any of its three call sites (checked
   directly, filed as an informational Change Request below).

Gates: (a) ruff clean (Evidence #6), (b) 44/44 reader pytest (Evidence #7),
(c) L1 index-write check PASS (Evidence #11); full-tree regression 262/262
(Evidence #12). Worktree clean after two commits
(`d5f18f0`, `5c359d3`); `git rev-parse HEAD` = `5c359d3e39a5be5021a7a056f2ef6026751d5789`
recorded in the structured result.

**The production card named in the dispatch now returns 200 on both
surfaces**, verified in-process against the live index (never via a launched
server, per D-12/D-3): `GET /doc/reference/RHACO_Card_YAML_Schema_
Specification_v1_8.card.yaml` -> 200 (was 500); `GET /api/doc/...` -> 200
(was 500). This is the specific observable the probe's W6 run recorded as
`unexpected_http_status[reader_v1_8]: 500`.

## Unresolved uncertainty

- **Whether the probe's own W6 browser-driven workflow will now record
  `PRODUCT_EVIDENCE_PASS` is UNVERIFIED from this worktree.** This round is
  barred from launching uvicorn or the probe (D-12/D-3, "the probe is the
  only sanctioned server launcher") and the probe module's own last round is
  already spent (`docs/rounds/R04_probe.report.md`: "probe module round 4 of
  4 -- the last round," no round 5 exists). Every claim this report makes
  about the exact failing document is re-derived through
  `fastapi.testclient.TestClient` in-process (Evidence #10), which exercises
  identical application code to what a real HTTP request through uvicorn
  would run, but is not literally a re-run of `tools/probe_corpus_
  explorer.py --preset W6` against a live server. Re-running that preset (no
  code change needed on the probe side; the integrator or a future strand
  can do this at no additional probe budget, per R04's own Change Request 1)
  would close this out conclusively.
- **Whether every one of the 872 corpus cards with an unquoted `date`/
  `last_human_review` scalar renders correctly, individually, is UNVERIFIED
  beyond the one named production card and the one rewritten fixture card.**
  The fix is general (any `datetime.date`/`datetime`/`time` anywhere in the
  parsed structure converts identically, not special-cased to this one
  card), and the unit tests exercise the general helper directly against
  nested structures, so there is no code-level reason to expect a different
  outcome for the other 871 cards -- but this round did not iterate every
  one of them against a live server (out of scope, and would require the
  probe's own launcher).
- **Whether a `.card.yaml` could carry a YAML scalar this round's fallback
  handles by `str()` alone (e.g. `!!binary`, `!!set`) is UNVERIFIED against
  any real corpus card** -- no such construct was found or is expected in
  this corpus's cards (they are hand- and tool-authored YAML mappings of
  strings/lists/scalars), so the fallback branch is unit-tested
  (Evidence #7, `test_json_safe_falls_back_to_str_for_a_non_temporal_exotic_
  leaf`) but not exercised end-to-end against a real file.

## Change requests

1. **Requestor:** reader (B11), informational only -- no crash currently
   reproduced. **Affected contract/path:** `tools/probe_corpus_
   explorer.py`'s `_parse_card_yaml_file` (line 861: bare `yaml.safe_load`,
   no type conversion). **Change:** consider reusing the same
   `_json_safe`-shaped conversion (or importing an equivalent) if a future
   probe runner ever extracts a `date`/`last_human_review` (or any other
   temporal) field from a parsed card and serializes it into a run's JSON
   evidence file (`_write_json` calls `json.dumps` with no `default=`
   handler either, the identical failure mode this round's dispatch
   diagnosed in the reader). **Evidence:** direct inspection this round of
   all three current call sites (KG(c) line 1349, KB2 line 1512, W5 line
   1994) -- none currently reads a temporal field from the parsed result, so
   nothing is broken today; this is a preventive suggestion, not a defect
   report. **Compatibility impact:** none either way -- purely additive if
   ever adopted. **Migration:** none. **Invalidated tests/probes:** none.

## Assumptions

- "The mismatch bug of item 2" is read as scoped to the five fields
  `_index_mismatch` actually compares (`INDEX_COMPARISON_FIELDS`), of which
  only `date` can ever carry a native temporal type from the card-file side
  on this corpus (per the R04 probe round's grep, independently re-verified
  this round, Evidence #5) -- `last_human_review` is parsed and can also be a
  native `datetime.date`, but it is not one of the five compared fields, so
  it was in scope for item 1's serialization fix but not for item 2's
  mismatch question.
- "the string form the card file itself uses" (task item 1) is read as "the
  canonical ISO-8601 text for the value the file's unquoted scalar denotes"
  -- for the plain-date case that is present throughout this corpus (per
  Evidence #5, every instance is a bare `YYYY-MM-DD` line with no time
  component), `.isoformat()` reproduces the file's own characters exactly;
  for a hypothetical `datetime.datetime` with a space-separated (non-`T`)
  original spelling, `.isoformat()` would render the standard `T`-separated
  form rather than byte-for-byte reproduce the original spelling -- no such
  case exists in the corpus today (Evidence #5's grep found only pure-date
  lines), so this was not something to resolve further, and the raw
  `<details>` block (untouched by this fix) remains the byte-for-byte
  record of what the file actually said regardless.
- The end-to-end fixture test (Evidence #9) rewrites the ANL fixture card
  specifically (rather than the HND, CMP, or reference cards) because it is
  the card every existing `tests/reader/test_reader_page.py`/`test_api.py`
  test already exercises in the clean state, so the new test's assertions
  about its rendered shape (doc_id, edges, no mismatch) can be cross-checked
  against those existing tests' expectations for the same document, giving
  higher confidence that the unquoted-date rewrite is the ONLY thing that
  changed about its rendering.
