# RHACO Corpus Explorer — Build Rationale and Prompt Design Notes

## 1. Executive summary

The RHACO Corpus Explorer is a strong first RHACO-native test of the edited autonomous build prompt because it solves a real operational problem while exercising nearly every part of the Measurement-Philosophy-derived harness.

RHACO already has a mature machine-facing corpus substrate. The existing `RHACO_corpus_index.py` is a derived SQLite index over the card/document corpus, with metadata, full-text search, local semantic retrieval, hybrid retrieval, and typed relationship edges. The completed Corpus RAG campaign explicitly constrains this layer to *find-and-describe*: retrieval is non-authoritative, the librarian/corpus remains the correctness authority, and the normal retrieval path does not require a frontier LLM.

The missing capability is human comprehension.

The proposed explorer therefore should not be another RAG system. It should be a **local comprehension instrument** over the system that already exists.

Its central purpose is:

> Make RHACO's reasoning artifacts directly navigable by the human operator without requiring a frontier model to mediate access.

This changes "Reasoning as Artifact" from a storage/documentation principle into an operational interface: campaigns, deliberations, analyses, changes, handoffs, supersessions, amendments, and citations can be traversed as a visible reasoning record.

---

## 2. What exists already

The build prompt is deliberately downstream of existing RHACO infrastructure.

### 2.1 The corpus index is derived, rebuildable, and non-authoritative

`rhaco/RHACO_corpus_index.py` describes the SQLite index as a derived layer over:

- sibling `.card.yaml` metadata;
- full document bodies;
- typed relationship edges.

Its stated architectural rule is that the index accelerates retrieval but does not become the record.

That distinction must survive into the UI.

The Corpus Explorer may say:

- "this document ranked first";
- "the index contains this relationship";
- "the semantic channel is unavailable";
- "the index appears stale."

It may not say:

- "this claim is correct";
- "this document is authoritative because it ranked first";
- "this relationship probably exists";
- "the index has corrected the source record."

### 2.2 RHACO already has multiple retrieval channels

The corpus-index evolution created:

- exact identifier resolution;
- FTS5 lexical retrieval;
- local semantic/vector retrieval;
- flat hybrid retrieval;
- graph retrieval;
- cross-encoder reranking.

The completed retrieval campaign also produced empirical dispositions among those channels. Flat hybrid retrieval became the accepted operational/default candidate. Graph retrieval remained an auxiliary mode. Cross-encoder reranking was retained as an implemented negative result after failing the canonical batch gate.

This matters for the browser.

A generic software team might see a reranker and assume it is "better." RHACO has already measured that question. The browser should inherit the empirical result rather than the prestige of the technique.

That is Measurement Philosophy Principle 5 applied directly to UI architecture.

### 2.3 The cards already encode human-navigation structure

The current card schema provides structured fields for:

- canonical identity;
- document type;
- date;
- title;
- document status;
- CMP investigation lifecycle state;
- programs;
- abstract;
- tags;
- dependencies;
- cross-references;
- supersession;
- location.

The current schema explicitly separates `status` from CMP-only `lifecycle_state`.

This separation is especially valuable in a browser because it can become visually obvious:

- **status** answers: what is the editorial/library state of this file?
- **lifecycle_state** answers: what state is the campaign/investigation in?

A generic document browser could easily collapse them into one "Status" badge. The prompt prohibits that.

---

## 3. The build hypothesis

The proposed build tests two things at once.

### Product hypothesis

> A local, non-LLM browser over RHACO's existing corpus index can materially improve the operator's ability to find, inspect, and traverse the observatory's reasoning record.

### Harness hypothesis

> The Measurement-Philosophy-derived autonomous build prompt can construct that comprehension layer while preserving RHACO's authority boundaries, empirical retrieval dispositions, and evidence discipline.

The second hypothesis is the more interesting methodological experiment.

A successful build is not merely one that produces an attractive interface. It should demonstrate that the autonomous harness can:

- inspect existing constraints before architecture;
- preserve semantic distinctions already present in the corpus;
- qualify its own verification tools;
- distinguish shared verification failure modes;
- use empirical evidence to choose retrieval behavior;
- retain negative results;
- document reasoning and rejected alternatives;
- stop with bounded failure where the evidence does not support a pass.

---

## 4. Why this is better than building a second RAG interface

A conversational RAG interface would recreate the exact dependency the operator wants to avoid.

The problem is not that RHACO lacks a way for a model to retrieve documents. That capability already exists.

The problem is that human access is mediated by an LLM.

A direct browser provides a second comprehension path:

```text
Canonical corpus
      │
      ├───────────────► Frontier-model / MCP retrieval
      │
      └───────────────► Human Corpus Explorer
                              │
                              ├─ browse
                              ├─ lexical search
                              ├─ local hybrid search
                              ├─ read
                              └─ lineage traversal
```

The two consumers share the same underlying RHACO retrieval/corpus substrate but do not depend on each other.

This is methodologically useful. If a frontier model tells the operator that a certain document or lineage is important, the operator can inspect the corpus directly rather than asking the same model to explain its own retrieval.

The Explorer becomes a **comprehension cross-check**, not another inference layer.

---

## 5. Measurement Philosophy mapping

### 5.1 Principle 1 — Architectural Acceptance

The most important inherited constraint is that `corpus_index.db` is derived and non-authoritative.

The build should not fight that architecture by making the database editable or treating it as a canonical document store.

Instead, the browser lives downstream:

```text
Canonical docs + card YAML
          │
          ▼
   derived corpus index
          │
          ▼
   Corpus Explorer
```

If the index is stale, the correct response is not to hide the condition. The UI exposes it.

If the semantic channel is unavailable, the browser degrades visibly to deterministic lexical/direct retrieval.

The limitation becomes part of the observable.

### 5.2 Principle 2 — The Instrument Observes Itself

For software, this principle cannot be copied literally from the CsI(Tl) detector case without care.

The adapted requirement is that the explorer exposes observable health from the same production system it uses:

- current retrieval mode;
- index metadata;
- freshness state;
- semantic availability;
- degradation state;
- document/index counts;
- application version.

But the verification probe should **not** share every failure mode with the application.

The production path and observation path are therefore separated:

- probe the real application;
- observe it externally through a browser driver;
- qualify the probe against known-good and known-bad cases.

This preserves the useful part of self-observation without creating circular verification.

### 5.3 Principle 3 — Layered Self-Filtering

The explorer provides a concrete test of whether the edited prompt correctly handles correlated verification layers.

A possible shared failure is:

```text
corpus_index defect
      │
      ├─ UI displays wrong result
      ├─ builder probe sees wrong result
      └─ critic sees wrong result
```

Three agents agreeing does not create three independent observations if all use the same defective substrate.

The prompt therefore requires `docs/LAYERS.md` to document shared dependencies.

A separate corpus-oracle layer uses frozen identifiers, fixture relationships, and existing RHACO gold queries to test cases where the expected target is independently fixed.

The aim is not impossible perfect independence. It is visible failure-mode accounting.

### 5.4 Principle 4 — Differential Measurement

This application makes several useful differentials visible.

#### Search-channel differential

The operator can run or compare:

- identifier;
- lexical;
- hybrid;
- graph.

This makes retrieval behavior inspectable rather than hidden behind an LLM.

#### Isolated vs integrated differential

A search component may work correctly in isolation but fail when UI filters, routes, or state are integrated.

The prompt's module showcase/probe structure lets that difference be measured.

#### Before/after build differential

The product can eventually be evaluated against the current manual workflow:

- filesystem browsing;
- grep/CLI search;
- model-mediated retrieval.

That comparison can measure whether the human comprehension layer actually changes operator access.

### 5.5 Principle 5 — Measurement Defines Category

This may be the most important principle for the build.

The corpus campaign already measured competing retrieval approaches.

The UI must inherit the result:

- accepted flat hybrid remains default;
- graph remains auxiliary;
- failed reranking remains a negative result unless new evidence changes its status.

The interface should not choose categories such as "Advanced search = reranker" based on theoretical sophistication.

Likewise, critic thresholds and probe results should be based on what the build actually demonstrates.

If evaluator precision cannot be calibrated, the score remains ordinal.

### 5.6 Principle 6 — Reasoning as Artifact

This is where the project becomes more than a search UI.

RHACO already records reasoning across document classes.

The explorer turns that infrastructure into a navigable object.

Examples:

```text
CMP
 │
 ├── depends_on ──► ANL
 ├── campaign_child ──► CHG
 │                         │
 │                         └──► HND
 │
 └──► later acceptance ANL
```

or:

```text
Document v1
   │
   └─ superseded_by
          ▼
Document v2
```

or:

```text
Amendment
   │
   └─ amends
        ▼
     Parent
```

The lineage view does not synthesize an explanation of the relationship. It makes the recorded relationship directly traversable.

The distinction is important:

> The explorer renders the reasoning artifacts and their recorded connections; it does not replace the reasoning with generated narrative.

That is why "comprehension instrument" is a better description than "knowledge assistant."

### 5.7 Principle 7 — Honest Scope

The V1 browser should explicitly not claim to be:

- a document editor;
- an adjudicator;
- a scientific analysis engine;
- a card-authoring tool;
- a classifier;
- an LLM summarizer;
- a replacement for librarian validation.

These are not defects.

They are scope boundaries that protect the role of the tool.

---

## 6. Why the Evidence drawer matters

A conventional search UI tries to hide implementation details.

RHACO benefits from selectively exposing them.

Every result should be able to answer:

> Why is this item on my screen?

The answer should be mechanical and bounded.

Examples:

```text
Retrieval mode: Hybrid
Returned rank: 2
Resolved document: RHACO-ANL-...
Matched line: 147
Semantic channel: available
```

or:

```text
Retrieval mode: Graph
Relation: supersedes
Seed: RHACO-CHG-...
Direction: outbound
```

If the current RHACO API does not expose component FTS/vector/RRF ranks, the interface should say so.

That restraint is important.

Reimplementing ranking internals purely to produce an impressive "explanation" would create a second retrieval implementation whose output could diverge from the actual result path.

The Evidence drawer should therefore expose **observed retrieval provenance**, not retrospective rationalization.

---

## 7. Why lineage is the key differentiator

Browsing and search solve ordinary library problems.

Lineage solves a RHACO-specific problem.

The observatory's documents are not merely a pile of reports. They form a structured sequence of:

- questions;
- measurements;
- deliberations;
- implementation changes;
- acceptance tests;
- negative results;
- supersessions;
- amendments;
- campaign evolution.

A filesystem hides most of this structure.

An LLM can reconstruct parts of it, but that makes comprehension dependent on retrieval quality and model interpretation.

A lineage interface makes the structure itself the observable.

That is the core vision:

> Reasoning as Artifact becomes reasoning as navigable infrastructure.

---

## 8. Proposed V1 user workflows

### 8.1 Browse the observatory

The operator selects:

- `doc_type = ANL`;
- `program = DetPhys`;
- `status = Baseline`.

The Explorer returns the matching carded corpus.

No semantic search is needed.

### 8.2 Ask a local semantic question

The operator searches:

`firmware averaging behavior after saturation`

The accepted local hybrid retrieval finds semantically relevant artifacts.

The human reads the source documents directly.

No LLM summarizes them.

### 8.3 Follow a campaign

Open a CMP.

The side panel shows:

- lifecycle state;
- dependencies;
- campaign children;
- downstream analyses/changes as recorded.

Select "Reasoning trail."

The application projects the typed graph into a chronological traversal.

### 8.4 Inspect a negative result

Search for the corpus reranker work.

The lineage exposes:

- build;
- gate analysis;
- negative result;
- later default-flip decision.

This is a particularly strong demonstration of RHACO's epistemic style because a failed technique remains visible in the reasoning history rather than disappearing behind the surviving implementation.

### 8.5 Work offline from frontier models

Disconnect frontier-model access.

The operator can still:

- browse;
- lexical search;
- identifier search;
- hybrid search if the local semantic substrate is available;
- traverse edges;
- read documents.

That directly satisfies the motivating use case.

---

## 9. Why the proposed stack fits the experiment

The prompt suggests:

- Python;
- FastAPI;
- Jinja2;
- HTMX;
- minimal JavaScript;
- Playwright.

This is a design recommendation, not an existing RHACO requirement.

The rationale is:

1. RHACO's existing retrieval layer is Python.
2. A local HTTP application is easy to run and inspect.
3. Server-rendered HTML keeps state/control flow legible.
4. HTMX can provide responsive filtering without requiring a large client-side architecture.
5. Vanilla JavaScript is sufficient for a graph projection if needed.
6. Playwright can exercise the actual production interface externally.
7. The stack remains small enough that autonomous build failures remain inspectable.

A heavier SPA framework may still be justified by implementation evidence, especially if graph interaction becomes dominant. The prompt permits that change but requires the builder to record why.

---

## 10. Verification philosophy

The hardest part of an autonomous build prompt is not producing code.

It is establishing what "done" means.

The Corpus Explorer is unusually useful because RHACO already possesses known targets.

### Deterministic checks

Examples:

- identifier X must open document X;
- phrase Y occurs at line/section Z;
- edge A → B has relation `amends`;
- CMP status/lifecycle fields remain distinct;
- vector disable produces lexical degradation;
- stale fixture produces a visible stale diagnostic.

These are objective.

### Human-facing critic checks

Other properties need judgment:

- Is the corpus understandable?
- Does the interface make lineage legible?
- Are authority boundaries visible without becoming intrusive?
- Does the reader help the operator stay oriented?
- Is it easier than using the filesystem directly?

These should be critic-scored only after deterministic fidelity gates.

The critic should never be allowed to compensate for an incorrect retrieval result by giving the interface a high usability score.

---

## 11. Probe qualification

The revised autonomous prompt added an important rule absent from many agentic build harnesses:

> Verify the verifier.

For this project, the production probe is likely a browser-driving tool.

A screenshot existing does not establish that the correct document was displayed.

The probe should therefore collect both visual and machine-readable state.

Example observation:

```json
{
  "workflow": "W5_lineage",
  "query": "RHACO-CMP-20260628-001",
  "selected_doc_id": "RHACO-CMP-20260628-001",
  "active_mode": "identifier",
  "visible_edges": [
    {
      "relation": "depends_on",
      "target": "RHACO-ANL-20260628-001"
    }
  ],
  "console_errors": [],
  "failed_requests": []
}
```

Qualification then intentionally gives the probe wrong states and checks whether it notices.

This is the software equivalent of calibrating an instrument before relying on its observations.

---

## 12. Useful deliberate failure injections

The build would be a better harness test if its verification layer is deliberately challenged.

Use fixture-only fault injection, never the live corpus.

Candidate failures:

1. **Wrong canonical document**
   - result card says document A;
   - reader serves document B.

2. **Metadata cross-wire**
   - document body A;
   - card metadata B.

3. **Lifecycle collapse**
   - CMP `status` displayed as campaign lifecycle.

4. **Reversed edge**
   - `amends` parent/child direction reversed.

5. **Stale-index condition**
   - fixture corpus timestamp/hash differs from fixture index.

6. **Semantic failure**
   - vector channel unavailable.

7. **Silent degradation**
   - backend drops to lexical but UI still says "Hybrid."

8. **Broken line navigation**
   - result reports line 80;
   - reader highlights line 60.

9. **Runtime failure**
   - one route emits browser console exception.

10. **Authority-language defect**
    - UI labels top-ranked result "Most authoritative."

The probe/critic layers should catch different subsets.

That produces real evidence about the autonomous harness's layered-verification behavior.

---

## 13. Suggested evaluation of the autonomous prompt itself

The application build should create an evaluation record for the prompt, not just the product.

At close, review:

### Architecture behavior

- Did agents inspect RHACO before coding?
- Did they reuse existing retrieval APIs?
- Did they avoid duplicating retrieval logic?
- Did they preserve read-only authority?

### Measurement behavior

- Was the probe qualified before being trusted?
- Did known-bad cases fail?
- Did agents distinguish a UI defect from a substrate defect?
- Were shared dependencies recorded?

### Epistemic behavior

- Was the reranker negative result preserved?
- Did the agents resist collapsing `status` and `lifecycle_state`?
- Did they report unavailable evidence as unavailable?
- Did they create unjustified scope exclusions?
- Did they retain failed rounds and unresolved findings?

### Autonomous behavior

- Did agents make reversible implementation decisions without unnecessary stalls?
- Did they stop at the actual authority boundary?
- Were architectural changes revalidated?
- Did the build terminate correctly as PASS, BOUNDED_FAIL, BLOCKED, or INVALID?

This makes the Corpus Explorer a test fixture for the prompt itself.

---

## 14. Potential later extensions — not V1 requirements

If V1 works, several extensions become possible.

### 14.1 Comparison view

Display two documents side by side:

- old/new versions;
- analysis/response;
- parent/amendment.

### 14.2 Campaign dashboard

A campaign-specific projection:

- charter;
- milestones;
- children;
- current state;
- findings;
- changes;
- unresolved items.

### 14.3 Measurement Philosophy traversal

From a document, show explicit Charter-principle citations and their downstream operationalizations.

This could eventually make the Measurement Philosophy inheritance map directly navigable.

### 14.4 Saved local research trails

Allow the operator to save a list of documents visited during an inquiry.

This should remain a separate personal workspace artifact, not mutate the canonical corpus.

### 14.5 Local deterministic reports

Generate a non-LLM query report:

- query;
- filters;
- retrieval mode;
- returned ids;
- paths;
- relation trails.

This could make search itself a durable evidence artifact.

### 14.6 Optional model-assisted layer

Only after the deterministic human comprehension layer is established should an optional LLM interpretation layer be considered.

If added later, it should sit above the Explorer rather than replace it:

```text
Corpus
  │
  ▼
Deterministic retrieval + Explorer
  │
  ├──► Human
  │
  └──► Optional LLM interpretation
```

That preserves the ability to inspect what the model had access to.

---

## 15. Main risks

### Risk 1 — UI becomes a second authority

Mitigation:

- read-only;
- explicit non-authoritative notice;
- direct links to canonical files;
- no write paths;
- no generated correctness labels.

### Risk 2 — Retrieval logic gets duplicated for convenience

Mitigation:

- dedicated adapter;
- mandatory reuse of RHACO functions;
- no component-score reconstruction unless existing API exposes it.

### Risk 3 — Graph becomes speculative

Mitigation:

- only typed recorded edges;
- unresolved stays unresolved;
- relation direction explicit.

### Risk 4 — Search sophistication outruns empirical evidence

Mitigation:

- inherit current accepted flat-hybrid default;
- preserve negative reranker result;
- current ratified repository evidence can supersede prompt expectations.

### Risk 5 — autonomous critic rewards polish over truth

Mitigation:

- objective fidelity gates precede critic score;
- probe captures ids/relations as data, not screenshot only;
- fixture oracle cases.

### Risk 6 — verification shares hidden failure modes

Mitigation:

- `docs/LAYERS.md`;
- explicit shared-dependency register;
- known-good/bad qualification;
- corpus/gold target checks.

---

## 16. What a successful result would mean

A successful V1 would establish more than a convenient browser.

It would demonstrate an architecture in which RHACO has three distinct layers:

```text
                 ┌──────────────────────────┐
                 │ Canonical RHACO corpus   │
                 │ docs + governed cards    │
                 └────────────┬─────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │ Derived retrieval layer  │
                 │ FTS / hybrid / graph     │
                 └────────────┬─────────────┘
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
       ┌──────────────────┐      ┌──────────────────┐
       │ Human Explorer   │      │ Model / MCP path │
       │ browse/read/     │      │ retrieval for    │
       │ traverse         │      │ frontier models  │
       └──────────────────┘      └──────────────────┘
```

That architecture gives the operator direct access to the same epistemic infrastructure used by model-mediated research.

The model no longer has to be the sole interpreter of the database.

The operator can inspect:

- what exists;
- why a result was retrieved;
- where a document sits in the provenance graph;
- how a campaign evolved;
- which result superseded another;
- where negative results remain in the record;
- whether the retrieval layer is degraded or stale.

This is a natural extension of the RHACO Measurement Philosophy.

**Reasoning as Artifact** becomes **reasoning as navigable infrastructure**.

The Corpus Explorer becomes a **comprehension instrument for RHACO's epistemic infrastructure**.

---

## 17. Source basis

This proposal was drafted against the repository state inspected on 2026-09-03, particularly:

- `rhaco/RHACO_corpus_index.py` — derived SQLite corpus index, FTS/hybrid/graph retrieval, freshness and degradation architecture.
- `RHACO_mcp_observatory_server.py` — current model-facing retrieval surface.
- `docs/reports/RHACO-CMP-20260628-001_Corpus_RAG_Retrieval_Layer.md` — authority boundary, evaluation campaign, accepted/rejected retrieval path history.
- `docs/reports/RHACO-ANL-20260712-001_M3_Gate_Evaluation_And_Disposition.md` — reranker negative-result disposition and flat-hybrid standing.
- `docs/reference/RHACO_Card_YAML_Schema_Specification_v1_9.md` — current document-card schema and the `status` / `lifecycle_state` distinction.
- `RHACO_Measurement_Philosophy_v1_4_1` — principles used to shape the build harness.

The build prompt instructs the executing agent to reinspect current repository state before implementation. If the repository has superseded any of these dispositions, current ratified evidence takes precedence and the change must be recorded.
