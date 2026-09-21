# The Measurement Philosophy: what this prompt was built on

**Audience:** readers who know the Cities: Skylines prompt and want to understand the foundation RHACO rebuilt it on, and why that foundation changes what a build prompt asks for.

The fable-cities prompt is built on a game. Its quality bar, its critic and its final gate all point at *Cities: Skylines II*: a product you can look at, screenshot and compare against. That reference is what makes its loop work.

RHACO's version had no product to compare against. It needed a different foundation, and the one it used was not written for software at all. It is the methodological charter of a small physics observatory. This document summarizes that charter, shows how each principle became a section of the build prompt, and records where the transfer held and where the pilot pushed back on it.

This is a summary written for this repository. The charter itself, *RHACO Measurement Philosophy* v1.4.1 (June 26, 2026), is an RHACO reference document and is not reproduced here. What is included is RHACO's own frozen, domain-neutral statement of the same seven principles, about 800 words, under [`measurement-philosophy/`](measurement-philosophy/). Read that first if you want the principles without the observatory. Principle statements below are quoted from it; the descriptions of where each principle came from are paraphrased.

## 1. Where it comes from

The Reno High-Altitude Cosmic Ray Observatory is a single-operator, citizen-built instrument: one scintillation detector in a lead shield at 5,050 ft, running four science programs from the same data stream. Its stated purpose is to produce measurements that meet professional methodological standards within the limits of citizen-scale equipment. The charter puts the commitment this way: wherever a methodological choice exists between the easier path and the more rigorous path, the more rigorous path is taken, and where rigor is impossible, the limitation is named.

That sentence appears almost unchanged in the goal section of RHACO's build-prompt template. It is the single most direct inheritance.

Two features of the charter matter for reading it correctly:

- **It collects; it does not invent.** The charter says of itself that it gathers principles that were already operating in the observatory's work, scattered across analyses and deliberation records. Each principle carries a statement, a rationale, and citations to the documents where it was first demonstrated. A principle nobody would cite is not a principle.
- **It is a living document with a gate.** New principles require a recorded deliberation. Ideas that are not yet earned are held in a register of **parked candidates**, each with a stated promotion criterion. A parked candidate does not bind the observatory's method. This distinction turned out to matter for the prompt (section 4).

## 2. The seven principles

Each entry gives the charter's statement, where the idea came from in the observatory, and what it became in a build prompt. "In the prompt" describes RHACO's domain-agnostic template as it now stands ([v2.2](campaign/RHACO_Build_Prompt_Template_v2_2.md)); the frozen [`PROMPT.md`](../PROMPT.md) that this build ran carries the same principle labels on its own sections.

### 1. Architectural Acceptance

> The constraints of the instrument are accepted as inputs to the observable, not as enemies of it. Where the instrument's architecture suppresses one signal, the canonical observable is found in what remains uncorrupted.

**At the observatory.** The detector's firmware filters and averages its own output by design. Rather than fight that, the observatory characterized the filter and moved its measurement to the part of the signal the filter leaves intact. The same posture applies to dead-time gaps and to a shield whose geometry is known to be imperfect: measure what is there, do not pretend it is ideal.

**In the prompt.** *Constraints first, then architecture.* Before any feature code the build writes `CONSTRAINTS.md`: every known limit of the stack, the runtime, the data and the budget, each treated as a design input. A constraint is never worked around by pretending it is absent, and removing one later is an explicit, versioned event. In this repository: [`CONSTRAINTS.md`](../CONSTRAINTS.md).

### 2. The Instrument Observes Itself

> The science detector is also the environmental sensor. Background characterization, contamination flagging, and environmental monitoring are derived from the same data stream as the science observation, with no separate hardware path.

**At the observatory.** The same crystal that records cosmic-ray events also records the gamma signature of radon in its surroundings, so contamination is flagged from the science stream itself. The charter's argument is about epistemics, not economy: a separate sensor would be a second chain of evidence that could disagree with the first in ways that are hard to adjudicate. When the instrument is wrong about its environment it is also wrong about the science, and the charter calls that coupling honest.

**In the prompt.** *The artifact observes itself.* The verification probe is built before the product and must drive the real production path: a real server, a real browser, never a mock. No agent may make a production-behaviour claim from a probe it has not run and inspected. The template states the inheritance outright: if the probe is wrong about the artifact, it must be wrong for the same reasons the artifact is wrong, and that coupling is the point. The probe is itself an instrument, so it is qualified first against one known-good case and a set of known-bad ones. In this repository: [`docs/probe-qualification/`](probe-qualification/).

### 3. Layered Self-Filtering

> The observation pipeline is structured as four independent filtering layers — physical shielding, real-time classification, continuous contamination characterization, corrected analysis — each able to fail without compromising the others. Redundancy across layers is the design principle.

**At the observatory.** Lead shielding, a real-time classifier, a contamination monitor and analysis-time review fail in physically different ways. When the classifier misfires, the contamination monitor catches it downstream, and the shielding is unaffected by either. Single-point failures, the charter says, are how observatories produce confidently wrong results.

**In the prompt.** *Verification layers.* Static checks, a behavioural browser probe, a critic and corpus oracles. **This is the principle the pilot pushed back on**; see section 3.

### 4. Differential Measurement Reveals What Absolute Measurement Buries

> Common-mode cancellation is a first-class measurement technique. Where an absolute count rate is contaminated by confounders, the differential against an independent reference detector — or the differential between two channels of the same detector — reveals signals that absolute measurement cannot.

**At the observatory.** A space-weather signal that was buried in the detector's total count rate became clear when the observatory compared a better-chosen channel against an independent reference instrument. Same event, same detector, different observable design. The charter notes this was arrived at empirically and only afterwards recognized as a method.

**In the prompt.** *Differential critic* and *blind final gate.* The critic does not issue a bare score. It reports three numbers: quality against a reference set with recorded provenance, change since the previous round on the same presets, and the module scored alone versus integrated. The final gate is a paired comparison with the project's framing removed. An absolute "looks good" is exactly the kind of number this principle distrusts.

### 5. Measurement Defines Category

> Empirical baselines outrank theoretical expectations. Class identity is determined by the time-domain morphology the detector observes, not by assumed underlying physics. New event classes are created when the data demands them.

**At the observatory.** Baselines are what was measured, not what was calculated, and when the instrument's geometry changed the dependent quantities followed the measurement. Event classes are split when the data shows a population the existing taxonomy cannot hold without distortion. The catalog is a record of what was observed, not of what was expected.

**In the prompt.** Scoring anchors are calibrated empirically: the critic scores known calibration artifacts before judging the build, and if the anchors do not reproduce on known artifacts, the anchors are rewritten, not the scores. Where no calibration artifacts exist, the scale is declared ordinal and uncalibrated and `PASS` may never be read from it. The same principle sits under the rule that the identity of the executing model is something to measure at every round, not something to assume. And it decided a design question in the Explorer itself. RHACO had already evaluated a cross-encoder reranker for its search and measured it below its acceptance criterion, so the Explorer does not offer it. [`RATIONALE.md`](../RATIONALE.md) puts it this way: the browser should inherit the empirical result, not the prestige of the technique.

### 6. Reasoning as Artifact

> The reasoning chain that produces an observation is itself part of the observation. Methodological discipline is enforced by the document infrastructure: rejected alternatives must be named with specific reasoning; deliberation is captured contemporaneously; conclusions cite the documents whose reasoning they depend on.

**At the observatory.** Every analytical session leaves a deliberation record: hypotheses considered, alternatives rejected and why, and links forward to what it produced. The charter is blunt that this is costly and that the cost is what makes the method auditable. The campaign records under [`campaign/`](campaign/) are this principle applied to the build itself.

**In the prompt.** For every non-obvious design decision, the alternatives considered and why each was rejected. Explicit ownership of every module and every shared thing, with changes recorded with reasoning. Provenance for every reference. Round reports and critic reports kept as evidence, not discarded as scaffolding. In this repository: [`ARCHITECTURE.md`](../ARCHITECTURE.md), [`docs/rounds/`](rounds/), [`docs/critique/`](critique/), [`docs/REFERENCE.md`](REFERENCE.md).

### 7. Honest Scope

> What the observatory cannot measure is named explicitly. Limits are inputs to roadmap planning, not embarrassments to hide.

**At the observatory.** The charter carries a table of things the instrument does not measure, and the table is normative: a claim inside it requires acknowledging the limit. The principle guards against two failures at once. Overclaiming is the obvious one. The subtler one is under-developing, because a limit nobody wrote down never becomes a priority.

**In the prompt.** `SCOPE.md`, the register of what the build cannot do or could not verify. Explicit terminal states, so that running out of budget ends in `BOUNDED_FAIL` and never in a relabeled pass. The authority boundary: what the build may never touch, verified by someone outside the build. And the first rule of the prompt: never inflate scores; report real numbers, failed rounds and negative deltas. In this repository: [`SCOPE.md`](../SCOPE.md), and the terminal state recorded in [`build_state.json`](../build_state.json).

[`RATIONALE.md`](../RATIONALE.md) section 5 maps the same seven principles onto the Corpus Explorer's own design, written before the build ran.

## 3. Where the transfer did not hold

A philosophy written for a physical instrument does not move to a software build for free, and the pilot recorded one place where it did not.

Principle 3 rests on the word *independent*. At the observatory that word is earned: lead shielding and analysis code cannot fail for the same reason. The first RHACO rewrite of the prompt carried the word across and described "four independent verification layers."

In a build harness that claim is false. The probe, the critic and the corpus oracles share the same build, the same database, the same capture path, and in places the same model family. When two of them agree, that is not independent corroboration. The pilot's result on this point held only because the frozen Corpus Explorer prompt said the opposite of its own template, telling the build not to claim independence and to record what its layers share. The post-pilot review found this, and template v2.0 removed the word and replaced it with a **shared-dependency register** and a list of independence claims the build does not make. The details are in [`PROMPT_EVOLUTION.md`](PROMPT_EVOLUTION.md), revision R4, and the register the build actually wrote is [`docs/LAYERS.md`](LAYERS.md).

RHACO had in fact already written this lesson down. Its frozen portable form of the principles, frozen on August 16, more than two weeks before the rewrite, carries it as an operating rule: agreement between checks that share a failure mode is one observation, not several ([`measurement-philosophy/`](measurement-philosophy/), rule R2). The rewrite did not inherit it. The record shows the dates; it does not show why.

The principle survived; its naive transfer did not. What carries over is the goal, failure modes that do not coincide, together with the obligation to measure whether you have it. That obligation comes from Principle 5.

## 4. A label is a claim

Every section of the RHACO prompt names the principle it implements. The template says why: a label is a claim that the section's mechanism must support. The post-pilot review tested those labels like any other claim, and two did not pass as written.

- Some sections carried a principle label and no mechanism that implemented it. The review required each label to resolve to a mechanism in its own section or be dropped.
- One section had been justified by a *parked candidate*, the charter's not-yet-earned idea of grounding claims against external literature. A parked candidate does not bind the observatory, so it cannot warrant a section of a prompt. Template v2.0 removed it as a warrant.

Both corrections are the philosophy applied to itself: the principle labels on a prompt are prose claims about behaviour, and a prose claim needs a referent.

## 5. What this does not claim

- The Measurement Philosophy was written for a particle detector. Its use as the basis of a build prompt has been tried **once** (n = 1), and no later template version has been validated by any run.
- Nothing here shows that a prompt built on these principles produces better software than one that is not. The pilot ended in `BOUNDED_FAIL`, and its harness evaluation concluded *partially supported*.
- What the record does show is narrower: the properties of the run that an outside reader is most likely to value (an honest terminal state, a probe that was qualified before it was trusted, limits written down, negative results kept) trace to specific sections, and those sections trace to these principles. Whether that is cause or coincidence is not something one run can say.

## 6. Further reading

- [`measurement-philosophy/`](measurement-philosophy/): the seven principles in RHACO's frozen, domain-neutral form, with a short guide.
- [`BUILD_CASE_STUDY.md`](BUILD_CASE_STUDY.md) section 3: what was kept from the Skylines prompt and what was changed, side by side.
- [`PROMPT_EVOLUTION.md`](PROMPT_EVOLUTION.md): how the pilot's findings changed the template.
- [`../PROMPT.md`](../PROMPT.md): the frozen prompt the build ran, with its principle labels.
- [Template v2.2](campaign/RHACO_Build_Prompt_Template_v2_2.md): the current domain-agnostic template.
