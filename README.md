# Autonomous Build Harness Test

**An example of what you can do with the Cities: Skylines prompt.**

[`rawprogress/fable-cities`](https://github.com/rawprogress/fable-cities/blob/main/PROMPT.md) published a prompt that has an AI agent build a Cities: Skylines-style city builder on its own: plan the architecture, fan the work out to sub-agents, build a probe that looks at the running result, score it against a reference, and loop until it is good. This repository takes that prompt's structure somewhere else. It rebuilds it on a different foundation, points it at a different kind of job, runs it **once** under recorded conditions, and keeps everything: the prompt, the build, the evidence, the verdict, and what was changed afterwards.

- **The foundation** is the [Measurement Philosophy](docs/MEASUREMENT_PHILOSOPHY.md) of the Reno High-Altitude Cosmic Ray Observatory (RHACO), a small citizen-science physics observatory. It is a set of seven principles about how to make a measurement you can defend. The Skylines prompt is built on a game you can screenshot and compare against. This one is built on those principles, because its target had nothing to be compared against.
- **The job** was the **Corpus Explorer**: a local, read-only browser over RHACO's research records. It is the test fixture. It is also a real tool that RHACO needed and uses.
- **The thing under test** was the harness, not the app: the prompt, the way it governs its sub-agents, and whether the build would describe its own evidence honestly.

> **Result.** The build ended in the terminal state **`BOUNDED_FAIL`**: nine objective gates passed, 11 of 12 acceptance presets were satisfied, and the open issues were kept on the record instead of being waived. The separate evaluation of the harness concluded **partially supported**. This is one run (n = 1). It is shared as a worked example with its failures intact, not as a method shown to work.

![The Corpus Explorer's reader: a document and its metadata card shown as two distinct regions](docs/images/explorer-reader.png)

*What the harness built. The Corpus Explorer's reader, showing the test campaign's own charter beside its catalog card. Captured 2026-09-20 against the live RHACO corpus, after the build: an illustration of the running application, not part of the build's probe evidence.*

## The test

**Question.** Can a build harness derived from the Measurement Philosophy construct a trustworthy human interface over RHACO's existing corpus infrastructure, while preserving the boundary of what it may touch, keeping RHACO's already-measured retrieval decisions, holding to evidence discipline, and ending in the terminal state its own evidence actually supports?

**Setup.** One prompt, [`PROMPT.md`](PROMPT.md), frozen and hash-pinned before the build as the instrument under test, with its reasoning in [`RATIONALE.md`](RATIONALE.md). The prompt fixed the constraints, module ownership, verification requirements, evidence records, budgets and terminal states in advance. Builders worked in isolated modules; an integrator owned the shared contracts; a browser probe and critics tested the assembled result. Budgets were hard: four rounds per module, 28 in total, a two-round convergence window, and running out of budget was never allowed to lower the bar. The build ran in its own repository so it could commit freely without any authority over RHACO's records.

**Four possible endings, declared up front:** `PASS`, `BOUNDED_FAIL`, `BLOCKED`, `INVALID`. `PASS` could only be read from probe data. Exhausting the budget could only ever be `BOUNDED_FAIL`.

**What happened.** The run lasted September 3 to 5, 2026. Much of the application worked on its intended path. It did not meet its complete acceptance criteria, and the build said so. Along the way the record shows the things a reader would want to see in an honest run, and the things that went wrong: a production defect the hand-made test fixture could not see, a probe that reported success on a failed page, written claims that did not match what the code did, and corrections that came from later sessions and outside readers. [How it was built](docs/BUILD_CASE_STUDY.md) is the full account.

**What changed afterwards.** RHACO reviewed its own template against the run's record and found that much of what made the run honest had been added when the prompt was written for this job, and was missing from the template it came from. The template was revised three times. [How the prompt changed](docs/PROMPT_EVOLUTION.md) maps each change to the finding behind it. None of those later versions ran this build, and none has been validated by a run.

## From the Skylines prompt to this one

**Kept:** the shape. Architecture before code; fan-out to sub-agents with owned folders; a probe that observes the running artifact; a critic; a loop with a budget.

**Changed,** because the target changed. There is no *Cities: Skylines II* to hold a document browser up against, so an art-director's score could not be the bar. In its place: objective gates, a behavioural browser probe that must first prove it can detect known faults, corpus oracles with known answers, and a rule that an uncalibrated critic score can never by itself license `PASS`. Added around that: an authority boundary the build may not cross, verified from outside the build; explicit terminal states; a register of what the verification layers share, so their agreement is not mistaken for independent confirmation; and a written record of limits.

The side-by-side comparison is in [How it was built](docs/BUILD_CASE_STUDY.md), section 3.

## The Measurement Philosophy, briefly

The principles were written for a particle detector. Each became a section of the prompt.

| Principle | In one line | In the prompt |
|---|---|---|
| 1. Architectural Acceptance | The instrument's constraints are inputs to the design, not enemies of it. | Write the constraints down before the architecture. Never work around one by pretending it is absent. |
| 2. The Instrument Observes Itself | The science detector is also its own environmental sensor. | Build the probe before the product. It drives the real path, never a mock, and is itself qualified against known faults. |
| 3. Layered Self-Filtering | Several filtering layers, each able to fail without taking the others down. | Layered verification, with an honest register of what the layers share. |
| 4. Differential Measurement | A difference against a reference reveals what an absolute number buries. | The critic reports change against a reference, change since last round, and alone-versus-integrated, never a bare score. |
| 5. Measurement Defines Category | What was measured outranks what was expected. | Scoring anchors are calibrated on known artifacts, or `PASS` may not be read from them. |
| 6. Reasoning as Artifact | The reasoning behind a result is part of the result. | Rejected alternatives, ownership, provenance and round reports are kept as evidence. |
| 7. Honest Scope | What cannot be measured is named explicitly. | `SCOPE.md`, explicit terminal states, and "never inflate scores." |

One of these did not transfer cleanly, and the run is what showed it. [The Measurement Philosophy](docs/MEASUREMENT_PHILOSOPHY.md) explains each principle, where it came from, and where the transfer failed. The principles in RHACO's own compact, frozen wording are under [`docs/measurement-philosophy/`](docs/measurement-philosophy/).

## What it built: the Corpus Explorer

RHACO already had machine-facing retrieval over its document corpus. What was missing was a way for a human to inspect the same records directly, without a language model between the operator and the source. Building another chatbot would not have fixed that. The Explorer makes the material navigable instead.

- **Browse:** find documents through metadata such as type, date, program, tags, document status, and campaign lifecycle state.
- **Search:** use identifier, lexical, hybrid, or auxiliary graph retrieval through the pre-existing RHACO corpus index.
- **Read:** open a canonical document and its associated metadata card, with heading and line navigation where supported.
- **Trace:** follow explicit, directional citations, supersessions, amendments, and campaign relationships.
- **Inspect the instrument:** see index and retrieval state, availability and degradation notices, and on-demand freshness diagnostics.

The Explorer does **not** generate summaries or scientific conclusions, edit corpus material, rebuild an index, or infer relationships missing from source metadata. Search rank represents retrieval relevance, not correctness or authority.

```text
Canonical documents + sibling .card.yaml files   <- record of authority
                      |
                      v
         Existing, derived corpus index            <- retrieval aid
       (metadata, text, vectors, typed edges)
                      |
                      v
             Read-only corpus adapter
                      |
                      v
         Local FastAPI / Jinja2 application
                      |
          +-----------+-----------+
          |           |           |
     Search/read    Browse     Lineage/diagnostics
                      |
                      v
               Human inspection
```

The original documents and their metadata cards are the source of record. The SQLite index is derived and rebuildable, and the Explorer is a read-only consumer of both. It reuses RHACO's retrieval algorithms instead of duplicating them, and it does not offer a reranker that RHACO had already measured and rejected. [How it works](docs/HOW_IT_WORKS.md) covers the architecture, the search modes, more screenshots, and the limits.

This is a bespoke RHACO application, not a packaged or independently deployable product.

## Repository guide

| Start here | Purpose |
|---|---|
| [`PROMPT.md`](PROMPT.md) and [`RATIONALE.md`](RATIONALE.md) | The frozen build prompt and its design rationale: the instrument under test. Primary records, not user guides. |
| [`docs/BUILD_CASE_STUDY.md`](docs/BUILD_CASE_STUDY.md) | The test: prompt provenance, what was kept and changed from the Skylines prompt, governance, procedure, evidence, outcome, and lessons. |
| [`docs/MEASUREMENT_PHILOSOPHY.md`](docs/MEASUREMENT_PHILOSOPHY.md) | The seven principles the prompt was rebuilt on, how each became a section of it, and where the transfer did not hold. |
| [`docs/measurement-philosophy/`](docs/measurement-philosophy/) | The principles themselves, in RHACO's frozen domain-neutral form (about 800 words), with a short guide. |
| [`docs/HOW_IT_WORKS.md`](docs/HOW_IT_WORKS.md) | The thing that was built: architecture, data flow, search modes, interfaces, screenshots, and limitations. |
| [`CONSTRAINTS.md`](CONSTRAINTS.md), [`ARCHITECTURE.md`](ARCHITECTURE.md), [`SCOPE.md`](SCOPE.md) | Build-time architectural and honest-scope records. |
| [`docs/PROMPT_EVOLUTION.md`](docs/PROMPT_EVOLUTION.md) | The frozen build prompt, the template versions that followed it, and the finding behind each change. |
| [`docs/campaign/`](docs/campaign/) | Hash-pinned, unedited **snapshot copies** of the RHACO campaign records: charter, dispatch handoff and amendments, the builder's handback, both evaluations, the shepherding handoffs, every template version including the two unfiled originals (v0 and v1), and the release-readiness sweep. See its [`MANIFEST.md`](docs/campaign/MANIFEST.md). These are non-canonical copies; the RHACO repository remains the record of authority. |
| [`docs/release/`](docs/release/) | What was changed to make this public copy: the list of removed files with their hashes, and the commit map. |
| [`DISPATCH_PARAMETERS.md`](DISPATCH_PARAMETERS.md), [`preflight/`](preflight/) | Dispatch-time parameters and the pre-flight inspection outputs the build recorded before writing code. |
| [`docs/REFERENCE.md`](docs/REFERENCE.md), [`docs/LAYERS.md`](docs/LAYERS.md) | Retrieval dispositions and verification-layer/dependency records. |
| [`docs/rounds/`](docs/rounds/), [`docs/critique/`](docs/critique/), [`docs/probe-qualification/`](docs/probe-qualification/) | Implementation rounds, criticism, and recorded checks. |
| [`build_state.json`](build_state.json) | Machine-readable build state and closeout record. |
| [`explorer/`](explorer/) | Application implementation; [`tests/`](tests/) and [`tools/`](tools/) contain checks and instruments. |
| [`fixtures/`](fixtures/) | The synthetic fixture corpus and its index builder. Every fixture document declares itself synthetic; none is derived from a real RHACO record. |
| [`requirements.txt`](requirements.txt), [`ruff.toml`](ruff.toml), [`.gitignore`](.gitignore) | Historical environment and lint configuration. |
| [`LICENSE`](LICENSE), [`LICENSE-CODE`](LICENSE-CODE), [`CITATION.cff`](CITATION.cff) | Licensing and citation; see [Licence](#licence). |

## Running and reuse

This repository assumes access to a **separate RHACO installation**, its canonical corpus, its derived index, and the local retrieval dependencies used by that installation. Paths, module imports, and the available retrieval configuration are RHACO-specific. Simply cloning this repository is not sufficient to reproduce a working environment. This repository does not include RHACO's research corpus as a standalone distributable dataset.

The checked-in configuration defines environment overrides for the database, document root, host, port, and page size; it defaults to a loopback-only server. See [`explorer/config.py`](explorer/config.py) and [`requirements.txt`](requirements.txt) to inspect the historical environment. These files describe what was built; they are not a portability or security certification. Anyone attempting to run a derivative should supply their own corpus and index, inspect the path and import assumptions, and independently validate the resulting application.

The project is shared primarily for examination of its design, implementation, and development record. It makes no claim that its autonomous-build results generalize beyond the one recorded pilot.

## About this public copy

This repository is a **filtered copy** of the private repository the build ran in. The private original is unchanged and remains RHACO's record.

- **What was removed.** Forty-eight browser captures (PNG) from probe runs that were driven against the live RHACO corpus. Those images render complete RHACO documents, including unpublished research records, as bitmaps that no text scan can inspect. They were removed from every commit, not only from the latest one. Each removed file is listed with its path, size and SHA-256 in [`docs/release/REMOVED_FILES.md`](docs/release/REMOVED_FILES.md), so the absence is declared rather than silent. The structured JSON observations from those same runs are retained, as are all captures from fixture-backed runs.
- **What that does to the history.** Filtering rewrites commit identifiers. Where a build record cites a commit hash, it is the original repository's; [`docs/release/commit-map.txt`](docs/release/commit-map.txt) translates old identifiers to the ones in this copy.
- **What was left alone.** The build's records are otherwise unedited. They contain absolute Windows paths from the build host and RHACO document identifiers and titles that do not resolve here, because the corpus is not part of this repository. An identifier of the form `RHACO-TYPE-DATE-SEQ` with no matching file under [`docs/campaign/`](docs/campaign/) refers to a RHACO-internal record.
- **How it was checked.** The pre-publication measurement, including its own limits and the two instrument defects found while running it, is [`RHACO-ANL-20260920-001`](docs/campaign/RHACO-ANL-20260920-001_Corpus_Explorer_Public_Release_Readiness_Sweep.md).

## Evidence and status

The September 3–5, 2026 pilot ended with `BOUNDED_FAIL`: the closeout records nine objective gates passed, 11 of 12 acceptance presets satisfied, and outstanding issues retained rather than waived. The subsequent RHACO harness analysis classified the research hypothesis **partially supported** under its gating criteria. These are different findings: one describes the software build's terminal state; the other evaluates the build process as an experimental instrument.

The campaign charter and the full evaluation are RHACO records. Snapshot copies are included here:

- [Corpus Explorer build-harness campaign](docs/campaign/RHACO-CMP-20260903-001_Corpus_Explorer_Autonomous_Build_Harness.md)
- [Harness evaluation](docs/campaign/RHACO-ANL-20260905-001_Corpus_Explorer_Harness_Evaluation.md)

These are historical, dated findings. A later code change or new run requires new evidence; this README is not a claim of current deployment health.

## Provenance

The autonomous prompt's structural starting point was [`rawprogress/fable-cities`'s `PROMPT.md`](https://github.com/rawprogress/fable-cities/blob/main/PROMPT.md), accessed September 3, 2026. RHACO did not record the upstream commit at the time and did not keep the retrieved bytes; an earlier RHACO statement that a copy had been retained was wrong, and is corrected in template v2.2. Measured on September 20, 2026, the upstream's public history is a single commit (`aea8b103…`, committed about seventeen hours before the access), so its `PROMPT.md` (git blob `c2bc981d…`, 5,742 bytes) is the only version that history carries. A rewrite of the upstream history after the access would be undetectable, so this is a strong inference about what was read, not a captured fact. The upstream is MIT-licensed; a copy retrieved on September 20 is kept with its licence under [`docs/campaign/upstream/`](docs/campaign/upstream/).

RHACO generalised that structure (v0), rewrote it against its [Measurement Philosophy](docs/MEASUREMENT_PHILOSOPHY.md) (v1), and then instantiated it for the Corpus Explorer as the frozen [`PROMPT.md`](PROMPT.md). Both unfiled originals are included under [`docs/campaign/`](docs/campaign/). A generalized RHACO build-prompt template followed **after** the pilot, incorporating its findings: v2.0 and v2.1 are both dated **September 7**, and v2.2 (**September 20**) corrects the provenance statement only and changes no mechanism. **None of these was the prompt used to execute this build.** See [How it was built](docs/BUILD_CASE_STUDY.md) and [How the prompt changed](docs/PROMPT_EVOLUTION.md) for the sequence and source references.

## Licence

Documentation, build records, data and the campaign snapshot copies are licensed under [CC BY 4.0](LICENSE). Code — everything under `explorer/`, `tools/` and `tests/`, plus the two fixture-builder sources `fixtures/__init__.py` and `fixtures/build_fixture_index.py` — is licensed under the [MIT License](LICENSE-CODE). The upstream prompt copy under `docs/campaign/upstream/` is its author's work under its own MIT licence, included with that licence file. To cite this repository, see [`CITATION.cff`](CITATION.cff).

---

*RHACO Corpus Explorer — a navigable research record and a bounded autonomous-build case study.*
