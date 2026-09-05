# R07 lineage round report -- strand S8-B12 (Task B12: direction-aware rendering)

## Header

| Field | Value |
|---|---|
| Strand | S8-B12, module builder (lineage) |
| Model | Claude Sonnet 5 (dispatch record; orchestrator/integrator `claude-opus-5[1m]`, Director ruling MOD-1) |
| Instruction of record | `docs/rounds/R07_lineage.prompt.md`, sha256 observed `c53f2f9c2ed508cbfa30c2d589cb9553ef0ce8c118de82bab7efcac3312fafe2` (15142 bytes) -- **matches** the pin |
| Window | 2026-09-05T15:27:43.1791437Z -- 2026-09-05T15:45:01.3098688Z |
| Worktree | `C:\highsierralabs\RHACO_Corpus_Explorer\.worktrees\lineage`, branch `build/lineage` |
| Base HEAD (this strand's first `git rev-parse HEAD`) | `3e7521bf7b79cf2d2730ef460052a006d5aa4440` |
| Contains f29bcc9 | yes -- `git merge-base --is-ancestor f29bcc97f4ba7de455fa32f3591e5d3ccf837976 HEAD` succeeded |
| Module round | **lineage round 2 of 4** |
| Task | B12 -- render every typed edge with the sentence true from the end the reader is standing on (critic round 1 gate 7 FAIL, ranked issues 1 and 7) |

## Change

1. **`explorer/lineage/service.py`** (owned module):
   - Import switched from `models.RELATION_LABELS` to `models.relation_sentence`.
   - `_edge_views_from_set` (formerly lines 273/283/292): every `LineageEdgeView.direction_label` is now built via `relation_sentence(e.relation, "outgoing"|"incoming"|"unresolved")` instead of the direction-blind `Edge.direction_label`.
   - `_reasoning_trail` (formerly line 421): direction_label built directly from `relation_sentence(edge.relation, direction)` at the call site itself, not inherited from the upstream `LineageEdgeView.direction_label` field.
   - `_relation_options` (`RelationOption.label`, task item "Line 244"): now uses a new, direction-neutral `RELATION_FILTER_LABELS` dict ("citation" / "supersession" / "amendment" / "campaign relationship") instead of the outgoing-only `RELATION_LABELS` -- the filter selects a relation in either direction, so a directional sentence on the chip was the same defect on a second surface (see Decisions).
   - **O7/O8 self-pointing `amends` edge** (task item 3, critic ranked issue 7 lineage half), two independent, evidence-driven fixes in `_edge_views_from_set` / `_relation_options`:
     - `_self_pointing_incoming_ids(edge_set)`: the adapter's `edges_for` (`explorer/corpus_adapter/adapter.py:513-516`, two independent `if`s, not `elif`) appends the SAME `Edge` object to both `outgoing` and `incoming` when the anchor's own doc_id and filename stem both match one of the edge's endpoints -- true only when the anchor viewed IS the amendment sharing its parent's doc_id. Detected by Python object identity (`id(e)`), not by relation name, so it also covers any future relation that develops the same collision. The degenerate INCOMING copy is suppressed; the OUTGOING rendering is kept.
     - `_other_side_cards(cards, anchor_ref)`: excludes the anchor's own `card_ref` from a resolved endpoint's card list. Discovered while instrumenting deliverable 3 (see Evidence): the amendment's own OUTGOING `amends` edge resolves its target id to BOTH the real parent card and the amendment's own card (O7), which without this fix rendered a link from the page to itself, and (traced further) would also have drawn a degenerate self-loop line in the SVG graph (`compute_layout`'s `other_refs` loop, which does not otherwise guard against the anchor's own ref).
   - `_target_labels(fallback_id, cards)`: when an edge's endpoint resolves to more than one card sharing a doc_id (O7), each rendered link now reads that card's own title (falling back to filename stem, never the shared doc_id) instead of repeating the id -- fixes critic ranked issue 7's "runs of identical links". The single-card case (the large majority of edges) is unchanged.
   - `LineageEdgeView` gained one new field, `target_labels: list[str]` (additive; parallel to `target_card_refs`).

2. **`explorer/lineage/templates/lineage/lineage.html`** (lines 95-105 / 112-122 by old numbering, the Outgoing and Incoming sections): the per-ref anchor text switched from the uniform `{{ e.to_id }}` / `{{ e.from_id }}` to `{{ e.target_labels[loop.index0] }}`. No change to `data-edge-*` attributes, bucket assignment, or the SVG arrow direction (per the dispatch's explicit prohibition).

3. **`tests/lineage/test_direction_sentences.py`** (new file, 7 tests, all fixture-backed via the `client` fixture -- none touch the live index): see Evidence.

No file outside `explorer/lineage/**` / `tests/lineage/**` was modified. `explorer/models.py` was read only (the contract already landed at `c861680`, per the dispatch). `tools/probe_corpus_explorer.py` was not touched.

## Evidence

**Diagnostic (read-only; workspace code only; fixture index built to a tmp dir, no write to `fixtures/fixture_index.db` or any live path)**, run before writing the fix, to ground the exact shape of the O7/O8 defect rather than infer it from code alone:

```
C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe <scratch diagnostic>.py
```

Key output (amendment's own page, `handoffs/RHACO-HND-20260115-003_Fixture_Handoff_Amendment_A1.card.yaml`):

```
outgoing:
  id=... from=RHACO-HND-20260115-003_Fixture_Handoff_Amendment_A1 to=RHACO-HND-20260115-003 rel=amends resolved=True
incoming:
  id=... from=RHACO-CMP-20260115-001 to=RHACO-HND-20260115-003 rel=campaign_child resolved=True
  id=... from=RHACO-HND-20260115-003_Fixture_Handoff_Amendment_A1 to=RHACO-HND-20260115-003 rel=amends resolved=True
overlap count (same Edge object in both buckets): 1
```
(Zero overlap on the parent's own page, `.../RHACO-HND-20260115-003_Fixture_Handoff.card.yaml` -- confirms this is specific to viewing the amendment itself.)

```
OUTGOING amends from RHACO-HND-20260115-003_Fixture_Handoff_Amendment_A1 to RHACO-HND-20260115-003
  target_cards (to_id resolves to): ['handoffs/RHACO-HND-20260115-003_Fixture_Handoff.card.yaml',
                                      'handoffs/RHACO-HND-20260115-003_Fixture_Handoff_Amendment_A1.card.yaml']
```
This is the self-link: the amendment's own outgoing `amends` edge's target list includes the amendment's own card_ref alongside the real parent's.

**Gates, exact commands and tails:**

```
cd C:\highsierralabs\RHACO_Corpus_Explorer\.worktrees\lineage
C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m ruff check explorer tools tests --output-format concise
All checks passed!

C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m pytest tests/lineage -q
29 passed, 2 warnings in 2.77s

C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe -m pytest tests -q
269 passed, 2 warnings in 25.69s

C:\highsierralabs\RHACO_Corpus_Explorer\.venv\Scripts\python.exe tools/l1_index_write_check.py
l1-index-write-check: hits=6 allowlisted=6 defects=0 verdict=PASS
```
(269 = 262 pre-round + 7 new; 29 = 22 pre-round lineage tests + 7 new.)

**Deliverable 6 -- is the class closed product-wide?** Command:

```
grep -rn "direction_label" explorer/
```

Result (paraphrased from the tool's own grep, full paths under this worktree's `explorer/`): every occurrence is now one of (a) the `Edge.direction_label` PROPERTY DEFINITION in `models.py:192` itself, now unused by any caller anywhere in the tree; (b) a dataclass field declaration (`EdgeLink`/`LineageEdgeView`/`TrailEntryView`), whose VALUE is built via `relation_sentence(...)` at every construction site (`reader/service.py:458/463/473`, `lineage/service.py:365/380/390/524`) or, in `reader/service.py`'s hand-written NARRATIVE section (lines 421/427/436), a literal string already correct per direction (the integrator's `c861680` commit message: "the reader's NARRATIVE section was already correct... The module worked out the right sentences; the shared contract did not offer them."); or (c) a template read of one of those already-correct fields (`lineage.html:95,112,129,183`; `reader/reader.html:196,222`). **No remaining call site anywhere under `explorer/` reads the direction-blind `Edge.direction_label` property and renders it to a human.** The class is CLOSED product-wide, not only on this module's surface.

Every new test in `test_direction_sentences.py` runs against the `client` fixture (the fixture corpus, deterministic); none touch the live index. Test names and what each establishes:

- `test_supersession_head_incoming_sentence_is_direction_aware` -- **this is the test that would still fail if `relation_sentence` were reverted to a direction-blind lookup** (it asserts `"is superseded by" not in body` on the supersession HEAD's own page, where a direction-blind revert would reintroduce exactly that string).
- `test_campaign_edge_direction_aware_sentence_parent_vs_child` -- same edge, two ends, two different (and each independently absent-on-the-wrong-page) sentences.
- `test_amends_edge_direction_aware_sentence_amendment_vs_parent` -- same, for `amends`; also asserts the degenerate incoming duplicate is absent from the amendment's own page.
- `test_amendment_own_page_amends_edge_does_not_link_to_itself` -- the self-link defect (task item 3), asserted as exactly one `<a>` in the edge's `<li>`, pointing at the real parent, never at the amendment's own card_ref.
- `test_cmp_outgoing_campaign_child_to_hnd_shows_distinguishable_links` -- ranked issue 7's "identical links" half: both target rows present, with distinguishable exact anchor text (`>Fixture Handoff</a>` vs `>Fixture Handoff -- Amendment A1</a>`).
- `test_relation_filter_chip_label_is_direction_neutral` -- the RelationOption label decision.
- `test_relation_filter_amends_count_not_inflated_by_self_pointing_duplicate` -- the filter's per-relation count is not doubled by the same O7/O8 collision.

## Material alternatives

- **Self-pointing dedupe keyed on relation name (`relation == "amends"`) vs. object identity.** Chose object identity: it generalizes to any future relation that develops the same shared-id collision, and is directly falsifiable against the fixture (verified: exactly one overlap, on the amendment's page only) rather than assumed from O8's current four relations.
- **Always showing title/filename-stem for every target link (single- and multi-card) vs. only when the endpoint resolves to more than one card.** Chose the conditional form: it fixes exactly the reported defect (indistinguishable runs), leaves the single-target rendering (the large majority of edges) byte-identical to before this round, and required touching no other existing assertion.
- **RelationOption label: keep the outgoing-only `RELATION_LABELS`, split into two direction-scoped chips per relation, or a new direction-neutral label.** Rejected the first (recreates gate 7's defect on the filter control, which the critic's own reasoning about "reading" would flag identically). Rejected the second as unscoped: no ranked issue, PROMPT.md passage, or acceptance test asks for a direction split on the filter, and `RelationOption`/`_relation_options` are counted over BOTH directions by design (module comment, unchanged). Chose a single neutral noun per relation.
- **Unresolved edge's sentence: hardcode "outgoing" vs. pass `direction="unresolved"` through to `relation_sentence`.** Both produce the identical string (the function's default branch fires for anything not `"incoming"`), but passing the edge's own `.direction` value literally matches `models.relation_sentence`'s own docstring ("unresolved ... takes the outgoing sentence") without introducing a second, unrelated literal at the call site.

## Decisions

1. **Unresolved edges** call `relation_sentence(e.relation, "unresolved")` (not a hardcoded `"outgoing"`): the outgoing sentence is correct (a `cites` edge is always read from the citing end when its target does not resolve), and `models.relation_sentence`'s own docstring documents this exact input, so the call site says what it means rather than repeating an inferred literal.
2. **`RelationOption.label`** (line 244 in the original numbering) is fed by a new, this-module-owned `RELATION_FILTER_LABELS` dict, deliberately neutral of direction ("citation", "supersession", "amendment", "campaign relationship") -- the filter chip labels the RELATION, which the control selects in either direction; a direction-aware sentence there would be the same defect the critic found, recurring on the filter instead of the edge list.
3. **The O7/O8 self-pointing `amends` edge** is fixed by suppression, not by a "this is a self-reference" label: the degenerate INCOMING bucket duplicate is dropped entirely (object-identity match against the OUTGOING bucket), and the anchor's own card is excluded from any edge's resolved target/source list. Suppression was chosen over labelling because there is nothing true left to say about the degenerate copy once the real (outgoing) edge is rendered correctly -- it is not a second fact, so there is no sentence for it to earn.
4. **Field naming**: `direction_label` is kept as the field name on both `LineageEdgeView` and `TrailEntryView` (not renamed) -- its role (the human sentence shown against an edge) is unchanged; only its construction is. Renaming would have touched every template and dataclass reference for no discriminating benefit.
5. **`target_labels` is additive**, not a replacement for `target_card_refs`: the API contract's required field (task B8 deliverable 2, re-asserted by `test_api_parity.py`) is untouched, so no existing consumer of `target_card_refs` (including the JSON API) changes shape.

## Result

**Lineage module round 2 of 4 consumed.** Deliverables 1-6 of Task B12 are complete: direction-aware sentences at all four named call sites plus the `RelationOption` label; the O7/O8 self-pointing `amends` edge suppressed/de-duplicated at two independent points (bucket duplication, self-referencing card resolution); shared-doc_id links disambiguated; 7 new fixture-backed tests, each tied to a named defect and one explicitly marked as the reversion-catching test; the direction-blind-sentence class confirmed CLOSED product-wide by grep. All three named gates (ruff, `tests/lineage`, `tests`, `l1_index_write_check.py`) pass; command output pasted above, not summarized. W5 is understood to now fail on incoming edges -- expected, accepted, and not compensated for here (`tools/probe_corpus_explorer.py` untouched, per the dispatch's explicit prohibition).

## Unresolved uncertainty

- **Deliverable 6's answer is CLOSED, product-wide** -- see Evidence's `grep -rn "direction_label" explorer/` paragraph above; no surface outside (or inside) `explorer/lineage/**` still renders a direction-blind sentence.
- **The corpus_adapter's double-append remains unfixed at its source** (`adapter.py:513-516`, two independent `if`s). This round suppresses its two symptoms in the VIEW layer per the dispatch's explicit instruction not to touch `explorer/corpus_adapter/**`; the underlying adapter behaviour is the corpus_adapter builder's own surface and, per this round's dispatch, "being dispatched concurrently with you on its last round" -- not re-opened here beyond the Change requests note below.
- **The `_other_side_cards` self-link fix was not a task-item-3-named line number** (the task named the double-bucketing and the identical-link-text symptom; the self-link-to-itself symptom was discovered while instrumenting the fix, per Evidence). It is the same O7/O8 root cause, addressed entirely within `explorer/lineage/**`, and is reported here rather than silently folded in.
- W5's known BOUNDED_FAIL status (probe budget spent, per the dispatch) is unchanged by this round; not verified again here since `tools/probe_corpus_explorer.py` is out of scope for this strand.

## Change requests

- **`explorer/corpus_adapter/adapter.py:513-516`**: `edges_for`'s two independent `if`s append the same `Edge` object to both `outgoing` and `incoming` whenever an anchor's own doc_id and filename stem both match one of an edge's endpoints (O7 doc_id sharing + O8 amends addressing). Recorded as a request for the corpus_adapter builder / integrator, not attempted here: `explorer/corpus_adapter/**` is out of this module's write scope (dispatch working rule 1), and this round's dispatch explicitly instructs "do not attempt to fix it in the adapter." Additive at the adapter level (e.g. `elif`, or a set-based de-dupe before bucket assignment) with no caller depending on the current double-append; the same round's `SCOPE.md` row ("Click-through from an `amends` edge...") already tracks a related `edges_for` gap and may be the natural place to fold this in.

## Assumptions

- The fixture cards' titles ("Fixture Handoff" / "Fixture Handoff -- Amendment A1") are stable, on-disk facts (read directly, not assumed from memory); the new tests key their exact-text assertions on them.
- `RELATION_FILTER_LABELS`'s specific wording is a reasonable, direction-neutral choice; no spec section read dictates exact filter-chip copy, so this is this round's own editorial judgment, stated plainly as such (task instruction: "Decide it explicitly... and do not leave it unaddressed").
- No consumer outside this module (probe, other tests, other pages) depends on `target_card_refs` including a self-referencing ref; a repo-wide grep for `target_card_refs` (pasted under Evidence in the read-first pass) found no such dependency, only this module's own construction/consumption and the API-contract test's key-presence check.
