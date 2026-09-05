# R08 search round 2 report (strand S8-B14)

## Header

| Field | Value |
|---|---|
| Strand | S8-B14, module builder (search), round 7 of the build (search round 2 of 4) |
| Instruction of record | `docs/rounds/R08_search.prompt.md`, sha256 observed `92DB48ABE3CEB4CCBC361932B0A6D02743EF61F2E1A631232E91E777D5DF5546` -- **matches** the pin in the dispatch |
| Model | Claude Sonnet 5 (system-prompt sentence: "You are powered by the model named Sonnet 5. The exact model ID is claude-sonnet-5.") |
| Window | 2026-09-05T16:05:46.9711217Z -- 2026-09-05T16:19:18.3439542Z (both timestamps captured as the first and a later tool call, per working rule 7) |
| Worktree | `C:\highsierralabs\RHACO_Corpus_Explorer\.worktrees\search`, branch `build/search` |
| HEAD observed | `git rev-parse HEAD` -> `26816db131626c4b241f20046792edbddd5337b4` (this prompt's own commit, per the dispatch's own note that it cannot name itself) |
| Round-6 boundary | `git merge-base --is-ancestor 6aaea9d HEAD` succeeded -- HEAD contains `6aaea9d` |
| Owned paths touched | `explorer/search/service.py`, `explorer/search/templates/search/search.html`, `tests/search/test_identifier.py`, `tests/search/test_recall_figures_attributed.py` (new), this report |
| `SCOPE.md` | Read, **not edited** (rule 1's bold warning honored). Item 3 below is a change request only. |

---

## Change

**Item 1 -- stop presenting July's Gold v1.1 figures as today's standing (critic ranked issue 2; CONSTRAINTS.md S8).**

`explorer/search/service.py` had four bare `Recall@10` figures, established by grep (Evidence below), not just the one the critic named:

1. `MODE_EXPLANATIONS` lexical standing: `Recall@10 0.200 aggregate on Gold v1.1.`
2. `MODE_EXPLANATIONS` hybrid standing (the critic's finding): `Recall@10 0.700 aggregate on Gold v1.1.`
3. `MODE_EXPLANATIONS` graph standing: `Recall@10 0.575 on Gold v1.1.`
4. `HYBRID_RERANK_NOTE`: `Recall@10 0.575 vs threshold 0.700, ~26 min/query`.

All four are `RHACO-ANL-20260712-001` figures, evaluated 2026-07-12, shown with no date and no source. Per S8 the choice for each figure is attribute-and-date, or remove -- never bare. I chose **attribute-and-date for all four**, not removal, because (per the task's own note) the mode explanations exist to help an operator choose a mode, a comparative sense across modes is genuinely useful, and stripping every number to nothing would be a worse page than one that is honest about when a number is from. Each of the four now names `RHACO-ANL-20260712-001` and states `evaluated 2026-07-12` next to the figure.

The hybrid figure is the one item's fix that goes further than dating: it is not just stale, it is **contradicted** by this build's own oracle (`tools/l4_gold_oracle.py`, `docs/probe-qualification/gold_v1_1_compat.json`: 0.675, 27/40, on today's corpus) and `SCOPE.md` already carries that as an evidenced regression with a stated cause (corpus evolution, not the adapter). I did not silently prefer the July figure and hide the current one, and I did not remove the July figure and leave only the current one (removing the accepted-default's official disposition would itself be a claim -- that the RHACO-ANL-20260712-001 acceptance no longer holds -- which is not this build's call to make, PROMPT.md section 11/6). Instead the hybrid standing text now states **both**, each dated: the July `RHACO-ANL-20260712-001` figure (0.700, evaluated 2026-07-12) and this build's own oracle figure (0.675, run 2026-09-04), with a pointer to `SCOPE.md`'s row for the cause. New module constants: `GOLD_V1_1_SOURCE`, `GOLD_V1_1_EVAL_DATE`, `HYBRID_CURRENT_MEASURE`.

**Item 2 -- identifier mode's evidence disclosure (critic ranked issue 5).**

`IdentifierRow` (service.py) gained an `evidence: Evidence | None` field. `_run_identifier` now builds one `Evidence` per doc_id row (never per card row -- see the O7 note below) with:
- `retrieval_mode="identifier"`
- `exact_identifier_match` = whether `resolve_identifier` itself returned this id (True), vs. the literal-query fallback used when nothing resolved (False) -- previously this distinction existed in the code (`if not ids: ids = [q]`) but was never surfaced to the page at all.
- `degradation_status` = a fixed, verified sentence: identifier mode cannot degrade because it never touches the vector channel (verification in Evidence below).
- `component_rank` = a fixed sentence stating there is no fusion in this mode, so there is no component rank to expose or withhold (distinct from hybrid/graph's `COMPONENT_RANK_NOT_EXPOSED`, which means "the API withholds it" -- identifier mode has no such API to withhold from).
- `returned_rank=0` -- a placeholder int (the field is a required `int` on `models.Evidence`, which I did not edit); the template never renders this number for identifier mode.

`search.html` gained a dedicated `identifier_evidence_details` macro (deliberately not a call into the existing `evidence_details` macro, whose Rank/Component-rank lines assume a meaningful rank and a fused channel neither of which this mode has) and one call per `IdentifierRow`, after its card list. Its "Rank" line states plainly: exact alias lookup, no ranking, and that every card row shown for the id is listed with none preferred over another (O7 -- the disclosure must not imply the page picked one, CONSTRAINTS.md O7 / SCOPE.md "Unique document per identifier").

---

## Evidence

**Item 1 grep, establishing the full set (not just the critic's one instance):**
```
$ Grep "Recall@10|MRR|NDCG|threshold|aggregate.*Gold|Gold v1|recall_at_10" explorer/
explorer/diagnostics/service.py:36:    "Recall@10 0.575; ~26 min/query); not offered interactively"
explorer/search/service.py:54:# on Gold v1.1 (40 rows); this module re-evaluates none of them.
explorer/search/service.py:64:    "mode (RHACO-ANL-20260712-001: Recall@10 0.575 vs threshold 0.700, ~26 min/query; "
explorer/search/service.py:87:            "bm25 order only (Recall@10 0.200 aggregate on Gold v1.1)."
explorer/search/service.py:93:        standing="ACCEPTED -- the operational default. Recall@10 0.700 aggregate on Gold v1.1.",
explorer/search/service.py:100:            "improvement. Recall@10 0.575 on Gold v1.1."
```
(line numbers are pre-fix; the four `explorer/search/service.py` hits are the four figures fixed. The `diagnostics/service.py:36` hit is addressed under Unresolved uncertainty -- it is not mine to edit.)

**Item 1, the hybrid figure's own contradiction (read, not re-derived):** `docs/probe-qualification/gold_v1_1_compat.json` -- `"recall_at_10_adapter": 0.675`, `"hits_adapter": 27`, `"threshold": 0.7`, `"verdict": {"threshold_met": false, "overall": "SCOPE"}`. `SCOPE.md` row "Gold v1.1 compatibility ...": "`tools/l4_gold_oracle.py` run 2026-09-04 ... Recall@10 = 0.675 (27/40) for the adapter and for the module itself, against the standing 0.700 ... evaluated 2026-07-12."

**Item 2, the "identifier mode cannot degrade" claim, verified rather than assumed** (task's explicit instruction): read `explorer/corpus_adapter/adapter.py`.
- `resolve_identifier` (line 406-407): `return self._rhaco_index.resolve_identifier(q, db_path=self.db_path)` -- no call to `vector_availability()` or anything vector-related.
- `cards_for_doc_id` (line 308-313) calls `_cards_for_doc_id` (line 295-306), which runs `Q3_CARDS_FOR_DOC_ID` and builds each row via `_row_to_card` (line 241-284), which reads `Q3_PROGRAMS_FOR_YAML_PATH`, `Q3_TAGS_FOR_YAML_PATH`, and (for `is_amendment`) `Q7_EDGES_FOR` -- again no vector-channel call anywhere in this path.
- Contrast: `search_hybrid` (line 488) and `search_graph` (line 506) both open with `vec = self.vector_availability()`. Neither `resolve_identifier` nor `cards_for_doc_id` has an equivalent line. This is the basis for `IDENTIFIER_DEGRADATION_TEXT`.

**Tests, behavioral (all actually run; see Gates below for the exact commands and tails):**
- `tests/search/test_recall_figures_attributed.py::test_no_bare_recall_figure_on_search_page` -- scans the rendered `/search` page for a `Recall@10 <number>` shape with no ISO date within 140 characters; **FAILS against the pre-fix code** (confirmed by `git stash`-ing `explorer/search/service.py` and `explorer/search/templates/search/search.html` and re-running -- see the transcript below) and **passes after the fix**. This is the test that would have caught the critic's finding directly (it does not depend on the four specific strings; a fifth bare figure added later would also be caught).
- `tests/search/test_recall_figures_attributed.py::test_recall_figures_are_attributed_to_the_source_anl_and_date` -- belt-and-suspenders on the specific fix (exact source/date/current-measurement text). Also confirmed to fail pre-fix.
- `tests/search/test_identifier.py::test_identifier_evidence_discloses_exact_match_no_ranking_no_fusion_no_degradation`, `::test_identifier_shared_id_evidence_appears_once_and_never_picks_a_row`, `::test_identifier_unknown_id_evidence_discloses_no_exact_match` -- all three confirmed to fail pre-fix (no `Evidence` existed on `IdentifierRow` at all, so `"Why this result"` was absent from every identifier-mode page).

Pre-fix failure transcript (`git stash push -- explorer/search/service.py explorer/search/templates/search/search.html`, then `pytest tests/search/test_recall_figures_attributed.py tests/search/test_identifier.py -q`, then `git stash pop` to restore -- UNVERIFIED beyond this session's own run, but it is a real run, not a code-reading inference):
```
FAILED tests/search/test_recall_figures_attributed.py::test_no_bare_recall_figure_on_search_page
FAILED tests/search/test_recall_figures_attributed.py::test_recall_figures_are_attributed_to_the_source_anl_and_date
FAILED tests/search/test_identifier.py::test_identifier_evidence_discloses_exact_match_no_ranking_no_fusion_no_degradation
FAILED tests/search/test_identifier.py::test_identifier_shared_id_evidence_appears_once_and_never_picks_a_row
FAILED tests/search/test_identifier.py::test_identifier_unknown_id_evidence_discloses_no_exact_match
5 failed, 4 passed, 2 warnings in 0.80s
```

---

## Material alternatives

**Item 1:**
- *Remove all four figures instead of dating them.* Rejected per the task's own note and reasoning above: a comparative sense of the modes helps an operator choose one, and attributed-and-dated numbers serve that better than silence, provided the reader can tell they are historical.
- *Remove only the hybrid figure (the contradicted one), date the other three.* Considered, since the hybrid figure is the worst offender. Rejected because removing it entirely would itself read as a claim -- that the July acceptance no longer stands -- which is a RHACO evidentiary disposition this build does not own (PROMPT.md section 11/6); dating it alongside the build's own contradicting measurement is more honest than silence in either direction.
- *Move the hybrid standing/regression detail to the diagnostics page instead of the search page.* The task explicitly allows this as a change request rather than an edit. I did not take it: the mode-standing section's whole purpose is to help an operator pick a retrieval mode on the search page itself, and the diagnostics page is not shown at the point that decision is made.

**Item 2:**
- *Reuse the existing `evidence_details` macro for identifier rows* (true "same shape," literally one macro). Rejected: that macro's Rank line reads `evidence.returned_rank` as a real number and its Component-rank line is gated on `retrieval_mode.startswith(("hybrid","graph"))`, so identifier mode would either fall through both gates silently (reintroducing "says nothing" for those two facts) or need `returned_rank` to carry a placeholder the macro would render as a bare, misleading number ("retrieval rank in mode identifier: 0"). A dedicated macro that states the facts in words is the honest version of "same shape."
- *Put the identifier evidence disclosure per card row instead of per doc_id.* Rejected per O7: the several rows exist because of corpus structure (an amendment shares its parent's `doc_id`), not because the retrieval step produced several answers; one disclosure per doc_id is the shape that cannot be read as "the page picked one" or "the page ran the lookup twice."

---

## Decisions

1. Attribute-and-date all four figures rather than removing any of them (Item 1; defended above and in Material alternatives).
2. State the hybrid figure's July value *and* this build's own current oracle value together, both dated, rather than picking one (Item 1).
3. Give identifier mode its own evidence macro rather than reusing `evidence_details` (Item 2; defended in Material alternatives).
4. Evidence disclosure is per `IdentifierRow` (per doc_id), not per `CardLine` (per card row) (Item 2; O7).
5. `exact_identifier_match` on the identifier evidence is computed from whether `resolve_identifier` actually matched, not hardcoded `True` -- the unmatched/literal-fallback path (`ids = [q]`) now honestly reports `False`.
6. Did not edit `SCOPE.md` (Item 3) -- see Change requests.

---

## Result

**Search round 2 of 4 consumed.** Both dispatched items (critic ranked issues 2 and 5) are addressed with behavioral tests; item 3 is a change request only, per the rule against editing `SCOPE.md`.

### Gates (exact commands and tails)

**(a) ruff** (`explorer tools tests`):
```
$ C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m ruff check explorer tools tests --output-format concise
All checks passed!
```

**(b) pytest tests/search, then pytest tests:**
```
$ python -m pytest tests/search -q
...........................                                              [100%]
27 passed, 2 warnings in 1.91s

$ python -m pytest tests -q
........................................................................ [ 25%]
........................................................................ [ 51%]
........................................................................ [ 77%]
................................................................         [100%]
280 passed, 2 warnings in 27.80s
```
(280 = the dispatch's stated baseline of 275 plus the 5 new/extended tests this round adds -- 2 in the new `test_recall_figures_attributed.py` file, 3 added to `test_identifier.py`.)

**(c) L1 index-write check:**
```
$ python tools/l1_index_write_check.py
allowlisted: fixtures/build_fixture_index.py:8: [reindex_full] ...
allowlisted: fixtures/build_fixture_index.py:28: [reindex_vec] ...
allowlisted: fixtures/build_fixture_index.py:113: [reindex_full] ...
allowlisted: fixtures/build_fixture_index.py:118: [reindex_full] ...
allowlisted: fixtures/build_fixture_index.py:141: [reindex_full] ...
allowlisted: fixtures/build_fixture_index.py:184: [reindex_vec] ...
l1-index-write-check: hits=6 allowlisted=6 defects=0 verdict=PASS
```

All three gates green; every command above was actually run this session (not reconstructed from memory).

---

## Unresolved uncertainty

**Does any OTHER page present a retrieval figure, threshold, or other measured quantity with no attribution?** Established by:
```
Grep "\b0\.\d{2,4}\b|\bRecall\b|threshold|~\d+\s*(ms|s|min)|\d+\s*ms\b" explorer/**/*.py
Grep "0\.382|0\.448|0\.721|0\.581|MRR|NDCG" explorer/**/*
```
Result: **yes, one other surface, and it is the same shape of problem, not attributed at all vs. attributed-but-undated.** `explorer/diagnostics/service.py:34-37` (`RERANK_STANDING_TEXT`):
```python
RERANK_STANDING_TEXT = (
    "hybrid-rerank: documented-FAIL batch mode (RHACO-ANL-20260712-001: "
    "Recall@10 0.575; ~26 min/query); not offered interactively"
)
```
rendered verbatim at `explorer/diagnostics/templates/diagnostics/diagnostics.html:107` (`<dd>{{ view.rerank.text }}</dd>`) with no surrounding date in either the string or the template. This is **better** than the pre-fix search page (it does name the source ANL id, which the pre-fix hybrid/lexical/graph figures did not), but on the same strict reading this round's task applies to the search page -- an ANL id alone does not tell a reader *when* it was evaluated -- it is not fully dated either. I did not touch it: `explorer/diagnostics/**` is not my owned path (rule 1), and this round's mandate is the search page. Flagging it here is the point of this section: **S8 is not yet satisfied product-wide, only where I looked plus this one adjacent finding** -- the MRR/NDCG/0.721/0.581 figures from `docs/REFERENCE.md` do not appear anywhere in `explorer/` at all (second grep above, zero hits), so those are not a live concern, but the diagnostics rerank line is, and the round-6 sealed-audit lesson the dispatch names (a claim found in one place is usually in several) held here too.

I did not exhaustively read every `.html` template's static prose (only grepped `explorer/**/*.py`, where every dynamic string used by a template lives, plus a template-level check for the one hit found) -- a number embedded directly as literal template prose rather than a Python constant would not be caught by these two greps. I judge this residual risk low given every other page's dynamic text is assembled in its `service.py` (the pattern this build follows throughout, per the module docstrings I read), but it is UNVERIFIED beyond the greps shown.

---

## Change requests

**To `explorer/diagnostics/**` (not filed as a task, offered per the Unresolved uncertainty finding above; the integrator may decline or defer it):** `RERANK_STANDING_TEXT` (`explorer/diagnostics/service.py:34-37`) names `RHACO-ANL-20260712-001` but carries no explicit evaluation date, the same gap this round closed on the search page's `HYBRID_RERANK_NOTE`. A parallel fix (add `evaluated 2026-07-12`) would bring diagnostics into the same attributed-and-dated state.

**To `SCOPE.md` (item 3 -- reported, not made, per the rule against editing it):**

The "Gold v1.1 compatibility" row's Consequence cell currently ends:

> "The compatibility claim the build owns holds (the adapter does not degrade the module); the aggregate figure on today's corpus is below the July threshold for a reason outside the adapter. **The search page states neither number as a quality claim (S8)**."

That last sentence is false as of this round's fix, in the same direction it was false before it (the task states it was already false pre-fix, since the page stated 0.700 bare): the page now states **both** numbers -- 0.700 and 0.675 -- more explicitly than before, not fewer. **The original sentence does NOT become true on its own after my item-1 changes; if anything it becomes more clearly false**, since a bare reading of "states neither number" was arguably arguable pre-fix (only one number, 0.700, was stated, and 0.675 was not on the page at all) and is not arguable post-fix (both are now stated, in words, on the page). What changed is not whether the page states the numbers, but *how* -- attributed to source and date rather than as an unqualified present-tense claim. The cell's wording needs to say that, not "neither."

Proposed exact replacement text for the Consequence cell (quotable verbatim):

> "The compatibility claim the build owns holds (the adapter does not degrade the module); the aggregate figure on today's corpus is below the July threshold for a reason outside the adapter. The search page's hybrid mode-standing text states both numbers -- the July RHACO-ANL-20260712-001 figure (0.700, evaluated 2026-07-12) and this build's own oracle figure (0.675, this row) -- each attributed to its source and evaluation date rather than as a bare, undated quality claim (S8; explorer/search/service.py MODE_EXPLANATIONS and HYBRID_CURRENT_MEASURE, RHACO-HND-20260903-001 round R08 item 1)."

---

## Assumptions

1. **The "run 2026-09-04" / JSON-timestamp reconciliation.** `SCOPE.md`'s row text says the oracle "run 2026-09-04"; `docs/probe-qualification/gold_v1_1_compat.json` itself carries `started_utc: 2026-09-05T04:46:55+00:00`. These are consistent, not contradictory, if the run date in `SCOPE.md` is a local-Pacific calendar day (2026-09-05T04:46 UTC = 2026-09-04 ~21:46 PDT), which matches this workspace's general UTC-in-artifacts/Pacific-in-narrative convention. I did not resolve this myself (the JSON is a report file, not mine to edit, and `SCOPE.md` is integrator-owned); I used `SCOPE.md`'s own stated date ("2026-09-04") on the search page, since `SCOPE.md` is the integrator-accepted evidentiary record this page's text points a reader to, rather than re-deriving a date from the JSON's raw UTC timestamp myself.
2. Jinja2 autoescaping is active for `.html` templates (`explorer/app.py:44`, `autoescape=select_autoescape(["html", "xml"])`) -- confirmed the hard way (an early draft used possessive apostrophes in `HYBRID_CURRENT_MEASURE`, which rendered as `&#39;` and broke a test's literal substring check). All page-facing strings this round were reworded to avoid apostrophes rather than relying on HTML-entity-aware test assertions, to match the plain `in body` substring-check convention already used throughout `tests/search/`.
3. `returned_rank=0` on identifier-mode `Evidence` is a placeholder to satisfy the required (no-default) `int` field on `models.Evidence`, which I did not edit. It is never rendered by the template (`identifier_evidence_details` does not read it), but it is visible as a raw `0` to any caller of `/api/search` in identifier mode. I judged this an acceptable, honest-enough compromise given `models.py` is out of my owned paths; flagged here rather than silently accepted.
