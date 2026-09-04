# RHACO Corpus Explorer — Autonomous Build Prompt

**Purpose:** Execute a bounded autonomous build of a local, human-facing comprehension layer over the existing RHACO document corpus and `corpus_index.db`.

**Methodological basis:** Adapted from the RHACO Measurement Philosophy and the autonomous self-qualifying build-prompt template. This prompt is intended to test whether that harness can build a trustworthy human interface over RHACO's existing machine-retrieval infrastructure without collapsing retrieval, interpretation, and authority.

**Repository basis inspected before drafting:**

- `rhaco/RHACO_corpus_index.py`
- `RHACO_mcp_observatory_server.py`
- `docs/reports/RHACO-CMP-20260628-001_Corpus_RAG_Retrieval_Layer.md`
- `docs/reports/RHACO-ANL-20260712-001_M3_Gate_Evaluation_And_Disposition.md`
- `docs/reference/RHACO_Card_YAML_Schema_Specification_v1_9.md`
- `RHACO_Measurement_Philosophy_v1_4_1`

---

# Goal

Build a **local, read-only RHACO Corpus Explorer** that allows a human operator to browse, search, read, and traverse the RHACO document corpus without requiring a frontier model.

The application must use the existing RHACO corpus infrastructure rather than creating a parallel knowledge database.

The required product is a local browser application that makes RHACO's reasoning artifacts navigable as an interconnected research record.

The quality bar is:

1. A human can browse RHACO documents by structured card metadata.
2. A human can search the corpus using the existing deterministic/local retrieval channels.
3. A human can open the canonical document at the relevant section or line and inspect its sibling card metadata.
4. A human can traverse document relationships and campaign/reasoning lineage.
5. The application clearly distinguishes corpus authority, derived retrieval, and UI interpretation.
6. The application remains useful when semantic/vector retrieval is unavailable.
7. Search and navigation claims are backed by deterministic probes against known corpus targets.
8. The application is understandable and useful without any LLM in its normal operating path.

Never:

- turn the application into an AI chat interface;
- create a second authoritative document database;
- reimplement RHACO retrieval algorithms when an existing RHACO API/function is available;
- silently treat the derived SQLite index as the source of record;
- infer or generate relationships that are not present in RHACO data;
- present generated summaries as if they were document content;
- promote a retrieval configuration that RHACO's existing evaluation has rejected;
- write to the RHACO document corpus from the UI.

The build is autonomous within the authority boundary below.

---

# Standing RHACO Constraints

These constraints are architectural inputs.

1. **Authoritative corpus boundary.** Sibling `.card.yaml` files and canonical documents under the RHACO library remain the record. The derived SQLite corpus index accelerates retrieval but is non-authoritative and rebuildable.
2. **Existing retrieval substrate.** Reuse `rhaco/RHACO_corpus_index.py` and, where appropriate, the same public retrieval behavior exposed by `RHACO_mcp_observatory_server.py`.
3. **Current empirically accepted default.** Flat hybrid retrieval is the accepted default retrieval path from the completed corpus-RAG campaign. Graph retrieval is auxiliary lineage retrieval. Hybrid reranking was retained as an implemented negative result and must not silently replace the accepted flat-hybrid default.
4. **Card semantics.** Preserve the distinction between `identity.status` and CMP-only `identity.lifecycle_state`; they are separate channels and must remain separate in filtering, display, and query logic.
5. **Local-first operation.** Normal browsing and search must work locally without a frontier model. Local embedding/model dependencies may be used only through existing RHACO retrieval paths.
6. **Read-only V1 surface.** The first version may read RHACO corpus/index state but must not edit documents, cards, index rows, tags, relationships, or classifications through the UI.
7. **Windows host assumptions.** RHACO currently uses local Windows paths such as `C:\RHACO\docs\` and `C:\RHACO\index\corpus_index.db`. Do not hard-code more path assumptions than existing RHACO code already establishes; expose configuration where practical.
8. **No hidden epistemic uplift.** Search rank means retrieval relevance, not correctness, authority, truth, publication readiness, or scientific validity.

Before feature code, write `CONSTRAINTS.md` containing these constraints plus any newly observed constraints. For each, record its basis, design consequence, and whether it creates a user-visible limitation.

Do not place a constraint into `SCOPE.md` unless it produces an unresolved capability/claim limitation.

---

# Proposed Stack

Default unless repository inspection establishes a materially better fit:

- Python 3
- FastAPI for the local application server
- Jinja2 server-rendered templates
- HTMX for incremental interaction where useful
- minimal vanilla JavaScript for graph/interaction features that require it
- CSS without a heavy frontend framework unless evidence justifies one
- Playwright for production-path browser probes
- existing RHACO Python modules for corpus/index access

If the build changes this stack, document the reason in `ARCHITECTURE.md` and show what evidence or repository constraint justified the change.

Do not choose a framework merely because it is familiar.

---

# Hard Budgets

- Maximum builder rounds per module: **4**
- Maximum total builder rounds: **28**
- Convergence window: **2 matched rounds**
- Do not lower acceptance criteria because a round budget is exhausted.
- No paid external services.
- No external deployment.
- No mutation of files outside the designated build workspace except ordinary read access to RHACO paths required to operate the explorer.

Budget exhaustion produces `BOUNDED_FAIL`, not a pass.

---

# 1. Constraints first, then architecture
*(P1 Architectural Acceptance; P6 Reasoning as Artifact)*

Before feature code:

1. inspect the current RHACO corpus-index interfaces;
2. inspect current card-schema fields used by the database;
3. inspect the existing retrieval campaign's standing dispositions;
4. inspect any existing RHACO local-viewer conventions that materially affect implementation;
5. write `CONSTRAINTS.md`;
6. write `ARCHITECTURE.md`.

`ARCHITECTURE.md` must define explicit ownership and contracts for these logical modules. The exact folder names may change if justified, but the responsibilities must remain distinct:

## `corpus_adapter`

Read-only adapter over existing RHACO corpus/index APIs.

Responsibilities:

- connection/configuration;
- index metadata;
- identifier resolution;
- FTS/lexical search;
- accepted hybrid search;
- graph retrieval;
- document/card lookup;
- freshness/health state;
- typed translation from RHACO return values into UI-facing models.

Rules:

- Do not duplicate ranking logic from `RHACO_corpus_index.py`.
- Do not add text-to-SQL.
- Do not issue arbitrary SQL from user input.
- Direct SQL is permitted only for documented read-only metadata/facet queries when an existing RHACO API does not provide the data; every such query must be parameterized and documented.

## `catalog`

Structured browsing and filtering.

Required facets where present in current corpus data:

- document type;
- date;
- `identity.status`;
- CMP `identity.lifecycle_state`;
- program;
- tags;
- project-knowledge residency;
- path/location.

Status and lifecycle_state must remain separate filters.

## `search`

Human search surface over existing retrieval modes.

Required modes:

- identifier/direct lookup;
- lexical/FTS;
- flat hybrid — default;
- graph/lineage — auxiliary.

Hybrid-rerank may be shown only in an explicitly labelled diagnostic/experimental surface if repository inspection confirms it remains available. It must be labelled with its standing negative-result status and must not become the default.

Search results must not claim evidence the backend does not expose.

## `reader`

Canonical document and card reader.

Required:

- render canonical markdown safely;
- display document identity;
- display relevant card fields;
- jump to a search hit's resolved line/section when the backend provides it;
- preserve the document text verbatim except rendering;
- distinguish document body from card metadata;
- provide obvious access to the underlying local path.

No generated summary is required for V1.

## `lineage`

Relationship and reasoning-navigation surface.

Required:

- typed edges only;
- support at minimum the relations the corpus index currently materializes: `cites`, `supersedes`, `amends`, `campaign_child`;
- directional relationships must be displayed directionally;
- unresolved relationships remain visibly unresolved;
- provide both graph and chronological/list representations where practical;
- selecting a node opens the canonical document.

Do not infer missing edges.

## `diagnostics`

Make the state of the comprehension instrument visible.

Required:

- corpus index path;
- corpus/index version metadata if exposed;
- index freshness status if available;
- vector/semantic availability state;
- active search mode;
- graceful-degradation notice;
- document/card counts where supported;
- explicit non-authoritative notice.

## `web`

Routes, templates, UI state, accessibility, keyboard navigation, layout.

## `probe`

Deterministic verification of the production UI and retrieval path.

No mutable path may have ambiguous ownership.

For each non-obvious architectural decision record:

- decision;
- alternatives considered;
- evidence/constraint;
- rejected alternatives;
- what evidence would justify revision.

---

# 2. Build and qualify the measurement path before substantive UI work
*(P2 The Instrument Observes Itself; P3 Layered Self-Filtering)*

Create a production-path probe, default name:

`tools/probe_corpus_explorer.py`

Use Playwright or an equivalent browser-driving tool against the actual local application.

The probe must:

- launch or connect to the production local server;
- wait for a defined readiness endpoint/condition;
- execute named presets;
- save screenshots;
- save machine-readable JSON observations;
- capture browser console errors;
- capture failed network requests;
- record page URL, viewport, active retrieval mode, selected document id, and observed result ids;
- fail explicitly if required observations cannot be collected.

The probe may use controlled test corpus/index fixtures for qualification, but production claims must also be exercised against the actual production application path.

## Probe qualification

Before the probe can support build claims, demonstrate at least:

### Known-good case

A frozen small test corpus/index where:

- an exact identifier resolves to the expected document;
- a known lexical phrase returns the expected document;
- a known typed relationship is rendered in the correct direction;
- reader body and card metadata match the fixture sources.

### Known-bad cases

At minimum qualify detection of:

1. wrong document returned for a known identifier;
2. stale/mismatched displayed card metadata;
3. relationship direction reversed;
4. broken reader jump/line target;
5. browser console/runtime error.

Use a temporary/fixture substrate or controlled fault injection. Do not corrupt the live RHACO corpus or live index to qualify the probe.

Store evidence under:

`docs/probe-qualification/`

If the probe cannot distinguish known-good from known-bad behavior, repair the probe before trusting downstream evaluation.

---

# 3. Verification layers and shared-dependency register
*(P3 Layered Self-Filtering)*

Create `docs/LAYERS.md`.

Use these layers:

| Layer | Mechanism | Primary purpose |
|---|---|---|
| L1 Static | typing, lint, route/model checks, template checks, dependency checks | contract and implementation errors |
| L2 Runtime probe | production browser probe | actual search/navigation/rendering behavior |
| L3 Critic | separate non-coding evaluator | usability, fidelity, epistemic presentation, missed integration problems |
| L4 Corpus oracle checks | frozen RHACO gold queries + exact fixture assertions | retrieval/relationship correctness against known targets |

For this build, do **not** claim L2–L4 are independent merely because separate agents run them.

Document shared dependencies, especially:

- `RHACO_corpus_index.py`;
- the same derived SQLite database;
- browser capture path;
- frozen gold set;
- card/document filesystem.

When layers disagree:

1. record disagreement;
2. identify shared dependencies;
3. distinguish UI defect from retrieval defect where evidence permits;
4. run the smallest discriminating check;
5. leave unresolved if evidence cannot decide.

A broken existing RHACO retrieval result is not automatically a UI bug.

---

# 4. Fan out under explicit ownership
*(P3 structural; P6)*

Use the orchestration mechanism available in the coding environment.

Builders own only their declared paths.

Suggested dependency waves:

### Wave 1 — substrate and contracts

- `corpus_adapter`
- `probe`
- `diagnostics`

### Wave 2 — primary human surfaces

- `catalog`
- `search`
- `reader`

### Wave 3 — comprehension integration

- `lineage`
- `web` integration/polish

One integrator owns:

- shared application models;
- shared configuration;
- root dependencies;
- routing registration;
- integration contracts;
- shared templates/assets when ownership cannot be isolated.

Cross-boundary changes require a recorded change request containing:

- requestor;
- affected contract/path;
- evidence;
- compatibility impact;
- migration;
- invalidated tests/probes.

Internal architecture may change autonomously if the goal and authority boundary remain fixed. Revalidate all dependent evidence after a contract change.

---

# 5. Required product behavior

## 5.1 Home / catalog browse

The home screen must answer:

> What is in the RHACO corpus?

Required:

- total indexed documents where supported;
- structured filter controls;
- sortable result list;
- title, canonical id/filename, document type, date, status, program(s);
- CMP lifecycle state shown separately from document status;
- compact abstract where available;
- direct open action.

Filtering must not fabricate values missing from cards.

## 5.2 Search

The search screen must answer:

> Where did I write about this?

Required:

- query box;
- visible active retrieval mode;
- default mode = accepted flat hybrid;
- explicit lexical mode;
- explicit identifier/direct mode;
- graph/lineage mode;
- filters compatible with the selected path;
- result rank/order;
- canonical id;
- title/path;
- matching excerpt/line where backend provides it.

If a backend mode degrades, say so visibly.

Example:

`Hybrid unavailable: using lexical retrieval. Result ordering is lexical-only.`

Do not silently preserve the label "Hybrid" after degradation.

## 5.3 Result evidence

Each result must have an **Evidence** or **Why this result** disclosure.

It may show only information actually observed from existing RHACO functions or directly derived without reconstructing ranking logic.

Possible fields:

- exact identifier match;
- active retrieval mode;
- returned rank;
- matched line/section;
- graph relation and seed where exposed;
- degradation status;
- index/model tag if exposed.

If component-level FTS/vector/RRF scores or ranks are not exposed by the existing interface, display:

`Component rank: not exposed by current RHACO retrieval API`

Do not reimplement the retrieval internals merely to populate the UI.

## 5.4 Document reader

The reader must answer:

> What does this artifact actually say, and what is its catalog identity?

Required layout:

- canonical document body;
- card metadata;
- identity and lifecycle;
- tags/programs;
- dependencies/cross-references;
- supersession/amendment state;
- local path;
- incoming/outgoing lineage links if available.

The body is the document.
The card is structured catalog metadata.
Do not visually collapse the two.

## 5.5 Lineage / reasoning navigator

The lineage screen must answer:

> How did this work develop, and what reasoning artifacts connect it?

Required:

- selected-document-centered view;
- typed, directional edges;
- relation filter;
- one-hop view by default;
- controlled expansion;
- chronological/list fallback;
- click-through to documents;
- explicit unresolved relations.

Recommended views:

1. **Graph view** — topology.
2. **Reasoning trail** — chronological sequence of connected artifacts.

The graph is a projection of recorded RHACO relationships, not a generated theory of influence.

## 5.6 Diagnostics

The diagnostics screen must answer:

> What does this comprehension instrument currently know about its own state?

Display observable information including:

- application version;
- corpus-index path;
- index/retrieval version metadata if exposed;
- freshness status if callable;
- vector semantic availability;
- active/default retrieval mode;
- degradation state;
- document/index counts where supported;
- last successful probe run if persisted;
- explicit authority notice.

Required authority notice:

> **Retrieval is not adjudication.** This application helps locate and traverse RHACO documents. The canonical documents and their governed metadata remain the record; search rank does not establish scientific correctness or authority.

---

# 6. Retrieval fidelity and empirical precedence
*(P4 Differential Measurement; P5 Measurement Defines Category)*

The explorer must preserve existing empirical retrieval dispositions.

At build start, inspect the current campaign/ANL state and record the standing accepted and rejected retrieval configurations in `docs/REFERENCE.md`.

Expected standing state at prompt authorship:

- flat hybrid accepted as the operational/default candidate and later default path;
- graph retained as auxiliary lineage mode;
- hybrid-rerank recorded as a negative result for the canonical batch retrieval gate.

If repository state has changed since this prompt was authored, the current ratified evidence supersedes this expectation. Record the change rather than silently following stale prompt text.

Do not "improve" the UI by elevating a rejected retrieval mode because it appears sophisticated.

---

# 7. Critic and calibration

Use a separate critic who writes no production code.

Critic persona:

> Senior research-software librarian and information-retrieval engineer reviewing a provenance-sensitive scientific document explorer. The critic has no stake in the implementation and must distinguish visual polish from retrieval fidelity.

The critic evaluates:

1. retrieval fidelity;
2. metadata fidelity;
3. relationship fidelity;
4. legibility of authority boundaries;
5. browse/search usability;
6. reader comprehension;
7. lineage comprehension;
8. degradation honesty;
9. accessibility;
10. performance sufficient for local interactive use.

## Objective gates

The following are not subjective scores:

- exact identifier fixture targets correct;
- gold-query retrieval compatibility does not regress beyond the standing accepted RHACO baseline unless explicitly scoped and evidenced;
- no write path to corpus from UI;
- no arbitrary text-to-SQL;
- zero unresolved template/runtime exceptions in acceptance probes;
- card `status` and CMP `lifecycle_state` never collapsed;
- typed relation direction preserved;
- flat hybrid remains default unless newer ratified evidence says otherwise;
- semantic-unavailable degradation is explicit and functional.

## Critic score

Use a 0–10 `ref_score` for human-facing product quality only after objective gates.

Anchors:

- **10** — RHACO corpus structure, retrieval state, lineage, and authority distinctions are immediately legible; navigation is fast and coherent; no material usability defect; evidence presentation is exact and appropriately bounded.
- **8.5** — professional local research tool; all core workflows are clear and reliable; minor polish issues only.
- **7** — functionally competent but important workflows require interpretation, lineage/search evidence is awkward, or the interface materially impedes comprehension.
- **5** — core features operate but the tool is primarily a developer interface, hides important epistemic distinctions, or is cumbersome enough that filesystem/manual search remains preferable.
- **0** — cannot reliably browse/search/read the corpus or misrepresents authority/retrieval state.

Pass threshold: **8.5**, with all objective gates passing.

If no credible calibrated exemplars exist for this UI class, record that score precision is ordinal rather than metrological. Do not invent repeatability precision.

For convergence, use matched workflow evaluations across rounds. If repeated critic scoring cannot establish a meaningful numeric repeatability floor, define convergence qualitatively using unchanged ranked issue sets across two rounds and record that limitation.

---

# 8. Acceptance workflow set

Freeze a workflow set before iterative critic scoring.

At minimum:

### W1 — Exact known document

Search a canonical RHACO document id.
Expected: exact/direct result → open correct document → correct card.

### W2 — Lexical phrase

Search a phrase known to exist in a frozen target.
Expected: target found, excerpt/line consistent with source.

### W3 — Semantic inquiry

Run an existing frozen gold semantic query.
Expected: accepted hybrid retrieval behavior preserved relative to current RHACO baseline.

### W4 — Campaign lifecycle browse

Filter to CMP documents.
Expected: `status` and `lifecycle_state` both visible and independently filterable.

### W5 — Reasoning lineage

Open a campaign or analysis with known typed relationships.
Expected: edges match indexed relationships and direction.

### W6 — Supersession/amendment

Navigate a known versioned/superseded artifact.
Expected: historical artifact remains visible; replacement relationship is clear.

### W7 — Degraded semantic channel

Disable semantic/vector availability through the sanctioned RHACO mechanism.
Expected: application remains usable through lexical/direct retrieval and tells the operator exactly what degraded.

### W8 — Staleness

Exercise a fixture where index freshness differs from corpus state.
Expected: diagnostics expose the condition; application does not silently describe stale derived state as authoritative current state.

### W9 — Reader provenance

Open search hit at a specific line/section.
Expected: reader renders actual canonical document content and labels card metadata separately.

### W10 — No-LLM operation

Run the complete standard workflow with no frontier model access.
Expected: all core functions remain available.

Persist workflow results per round.

---

# 9. Honest scope
*(P7 Honest Scope)*

Maintain `SCOPE.md` from the first commit.

Use:

| Capability/claim | Status | Evidence for limit | Consequence | Path to addressing | Validation required to remove |
|---|---|---|---|---|---|

Likely V1 exclusions unless implementation evidence justifies safe inclusion:

- no corpus editing;
- no card editing;
- no relationship authoring;
- no AI-generated summaries;
- no natural-language synthesis across documents;
- no authoritative scientific conclusions;
- no arbitrary SQL console;
- no replacement for librarian validation;
- no automatic correction of stale or malformed corpus state.

Do not put an item in scope merely because implementation is difficult.

If the build cannot implement a required browse/search/reader/lineage function, revisit architecture before declaring it out of scope.

---

# 10. Reasoning and evidence as build artifacts
*(P6 Reasoning as Artifact)*

Persist run state to:

`build_state.json`

Per module record:

- owner;
- status;
- round;
- objective gates;
- `ref_score` if applicable;
- open issues;
- assumptions;
- blocked dependencies;
- invalidated evidence;
- probe artifacts;
- scope references.

Store:

- critic reports → `docs/critique/`
- builder round reports → `docs/rounds/`
- probe qualification → `docs/probe-qualification/`
- retrieval/reference disposition → `docs/REFERENCE.md`
- verification dependency map → `docs/LAYERS.md`

Builder reports contain decision-relevant reasoning, not hidden chain-of-thought.

Record:

- change;
- evidence;
- material alternatives;
- decision;
- checks actually run;
- result;
- unresolved uncertainty.

---

# 11. Human authority boundary

Agents may autonomously:

- create/edit/delete files inside the build workspace;
- refactor the application;
- change internal architecture;
- add local dependencies consistent with the stack policy;
- run tests/probes;
- read the RHACO corpus/index;
- use sanctioned RHACO retrieval functions;
- create local fixture corpora/indexes;
- change internal contracts through the integrator;
- generate screenshots/reports;
- commit build work under the existing repository policy.

Stop in `BLOCKED` before:

- changing the RHACO corpus or `.card.yaml` records;
- changing `RHACO_corpus_index.py` retrieval semantics merely to satisfy the UI;
- changing the accepted retrieval default;
- rebuilding/re-embedding the live index as part of a UI workaround unless separately authorized;
- lowering the quality threshold;
- changing the meaning of objective gates;
- adding an LLM dependency to normal operation;
- adding write authority;
- creating an external/public deployment;
- exposing credentials;
- performing destructive actions outside the build workspace;
- redefining a requested capability out of scope without qualifying evidence.

A missing UI convenience is not permission to change the scientific/retrieval substrate.

---

# 12. Terminal states

End in exactly one state.

## PASS

Only if:

- required browse/search/read/lineage/diagnostics functions exist;
- all objective gates pass;
- production-path probes pass;
- degradation behavior passes;
- critic score reaches 8.5 if the critic scale was validly usable;
- no `SCOPE.md` item contradicts a required capability;
- authority notice and boundaries are correct.

## BOUNDED_FAIL

Use if the application is usable but a required bar remains unmet after convergence or budget exhaustion.

Report:

- achieved functions;
- failed workflows;
- best observed quality;
- whether limitation appears in UI, retrieval substrate, architecture, measurement, or external dependency;
- unresolved alternative explanations;
- next discriminating action.

## BLOCKED

Use when further progress requires human authority or an unavailable mandatory dependency.

## INVALID

Use when the verification path cannot support trustworthy claims about the explorer.

An `INVALID` result is preferable to claiming success based on an unqualified probe.

---

# 13. Invariants

- Never report an unrun check as passed.
- Never call correlated checks independent without evidence.
- Never hide retrieval degradation.
- Never collapse `status` and `lifecycle_state`.
- Never infer a relationship not recorded in RHACO data.
- Never describe the index as authoritative.
- Never use search rank as a correctness verdict.
- Never reconstruct unavailable retrieval evidence just to make the UI look explanatory.
- Never overwrite document text with generated interpretation.
- Never elevate a historically rejected retrieval mode without new ratified evidence.
- Never alter the corpus to make the UI pass.
- Never preserve a conclusion after new evidence invalidates it.
- Prefer explicit unresolved state to fabricated certainty.

---

# 14. Execution loop

1. Inspect standing RHACO corpus/retrieval contracts.
2. Write `CONSTRAINTS.md`.
3. Write `ARCHITECTURE.md` and ownership map.
4. Build read-only `corpus_adapter`.
5. Build and qualify the production browser probe.
6. Create `docs/LAYERS.md`.
7. Freeze acceptance workflows and current retrieval/reference state.
8. Build diagnostics and application shell.
9. Fan out browse/search/reader modules.
10. Probe each module through the production path.
11. Integrate.
12. Build lineage/reasoning navigation.
13. Run objective acceptance workflows.
14. Run critic review.
15. Iterate the lowest-quality/highest-impact unresolved workflow.
16. Revalidate evidence invalidated by integration.
17. Exercise semantic-unavailable degradation.
18. Reconcile all claims against `SCOPE.md`.
19. Declare `PASS`, `BOUNDED_FAIL`, `BLOCKED`, or `INVALID`.
20. Produce an evidence-backed closeout.

Start now.
