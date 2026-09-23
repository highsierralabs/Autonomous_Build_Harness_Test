# Using the build prompt template (v2.2)

**Audience:** anyone who wants to take the structure this repository tested and point it at their own build.

> **Status: untested.** No run has executed any v2.x version of this template. v2.0 was derived from one run of a *different* text, the frozen [`PROMPT.md`](../PROMPT.md) (n = 1). v2.1 applied an external review that included no run. v2.2 corrects the provenance paragraph only. What follows is a design with its reasons recorded. It is not a method shown to work.

## 1. What it is

This repository's test produced two artifacts. The first is the **Corpus Explorer**, the application the harness built. The second is this **build prompt template**, which RHACO wrote from the harness's record once the run was over. The template is a domain-agnostic, self-verifying autonomous-build prompt with `{{SLOT}}` placeholders, together with a companion guide for filling them in:

- [Template v2.2](campaign/RHACO_Build_Prompt_Template_v2_2.md)
- [Guide v2.2](campaign/RHACO_Build_Prompt_Template_Guide_v2_2.md)

Both are unedited snapshot copies of RHACO's filed versions. Their hashes are in the [manifest](campaign/MANIFEST.md).

The upstream [Cities: Skylines prompt](campaign/upstream/fable-cities_PROMPT.md) invites readers to copy it and swap in their own domain, and presents the game as only an example. This template is RHACO's attempt to make that swap for targets where no game can be screenshotted and compared against.

## 2. How it came from the test

The lineage is **upstream → v0 → v1 → `PROMPT.md` → v2.0 → v2.1 → v2.2**. v0 generalised the upstream structure. v1 rewrote it on the [Measurement Philosophy](MEASUREMENT_PHILOSOPHY.md). `PROMPT.md` filled v1 in for the Corpus Explorer and was frozen as the instrument under test.

The run tested `PROMPT.md`, not v1. That distinction is the reason v2.x exists. The review that produced v2.0 ([RHACO-ANL-20260907-001](campaign/RHACO-ANL-20260907-001_Build_Prompt_Template_Review.md)) was the last item on the test campaign's closing queue. It found that seven sections the run's positive results depended on had been added when `PROMPT.md` was written, and that v1 did not contain them. A second instantiation of v1 would not have inherited them. v1 also claimed its verification layers were independent, the opposite of what `PROMPT.md` said.

v2.0 therefore does two things. It moves those seven sections back into the template, and it adds a response to each prompt-design failure recorded during the run. [How the prompt changed](PROMPT_EVOLUTION.md) maps every change to the finding behind it.

## 3. What "untested" means, section by section

"Ran" below means that text serving the same function was in the frozen `PROMPT.md`, in different wording, and operated during the September 3–5 run. It does not mean the mechanism is shown to work in general: that was one run, on one host, with one client.

| Template section | In the run? | Notes |
|---|---|---|
| Goal; rigorous-path rule | Ran | Carried from v1. |
| 1. Constraints first, then architecture | Ran | `CONSTRAINTS.md` and `ARCHITECTURE.md` in this repository are the outputs. **New:** shared things owned by rule, each with a contract test (R8). |
| 2. The probe on the production path; showcase modes | Ran | Credited to the template itself, and it caught a real defect. |
| 2. Probe qualification (known-good, known-bad) | Ran | Instantiation addition, restored in v2.0. **New:** the fault predicate, progressive qualification, asserting on the rendered observable, and a separate probe budget (R2). Each was written after a recorded failure. |
| 2. Fixtures derived from production data, with a census | **New** (R9) | Written after a hand-authored fixture hid a crash through four green rounds. |
| 3. Verification layers and shared-dependency register | Ran | Instantiation addition, restored in v2.0. **New:** the fifth layer (claim audit) and the disagreement protocol. |
| 4. Fan-out under ownership, waves, integrator | Ran | **New:** dispatch records written before a strand returns (R6). |
| 5. Critic, objective gates, calibration | Ran, in a different form | The run had objective gates and a critic, with a fallback to an ordinal scale when no calibrated exemplars exist. **Did not run:** the three-number differential score against an external reference corpus. No such reference existed, which is why the prompt was rebuilt. **New:** repeatability from calibration artifacts each scored twice, and gate-over-score (v2.1). |
| 5a. Claim audit; `UNVERIFIED` as a first-class value | **New** (R3) | Written after true code with false prose about it recurred three times inside the run's own controls. |
| 6. Blind final gate | Did not run | `PROMPT.md` has no blind gate. The template says to drop it and record that in `SCOPE.md` when no external artifact of the same medium exists. |
| 7. Honest scope (`SCOPE.md`) | Ran | Credited to the template itself. |
| 8. Reasoning as artifact; round reports; state file | Ran, partly | Round reports and reasoning records ran. **New:** the state-file schema with `UNVERIFIED`, dispatch records and identity history. |
| 9. Terminal states | Ran | Instantiation addition, restored in v2.0 (R1). This is the section credited with the honest `BOUNDED_FAIL`. |
| Authority boundary, verified by a hand outside the build | Ran | Instantiation addition, restored in v2.0 (R5). **New:** a closeout invariant per substrate (v2.1). |
| Rules: executing-client identity as a measurement variable | **New** (R7) | Written after the executing model changed mid-run and no single surface reported it reliably. |

Parts of `PROMPT.md` did not generalise into the template: hard budgets as a separate block, invariants, and the acceptance workflow set. Their functions appear inside template sections 2, 5 and 9 and the authority boundary. The mapping is in [RHACO-ANL-20260907-001](campaign/RHACO-ANL-20260907-001_Build_Prompt_Template_Review.md).

## 4. Why it works the way it does

The upstream prompt's quality bar is a comparison. The build is screenshotted, held up against the game, and scored by an art director. Many targets have nothing to hold up against. The template replaces that comparison with measurement discipline: every claim about the product must trace to an observation made by an instrument that has itself been shown to fail on known-bad cases.

Seven principles set the shape. [The Measurement Philosophy](MEASUREMENT_PHILOSOPHY.md) explains each one, what it became in the prompt, and where the transfer failed. The section labels P1–P7 in the template refer to principles 1–7 of RHACO's [frozen domain-neutral text](measurement-philosophy/measurement-philosophy.md). Two names differ in wording:

- "The Instrument Observes Itself" is called "The System Observes Itself" there.
- "Layered Self-Filtering" is called "Layered Independence" there. Its rule R2, that checks sharing a failure mode count as one observation, is exactly what the template's shared-dependency register enforces.

If you adopt only three parts, the guide's section 1 names them:

1. **A qualified probe.** The builder runs it before saying "done", the critic can inspect its output, and it has been shown to fail on known-bad cases.
2. **A critic that writes no code** and scores against something outside the project.
3. **A claim audit** that reads every prose claim against the thing it describes.

The state file is not optional overhead. It is the record that keeps those findings intact across rounds.

## 5. Should you use it?

The guide's [section 2](campaign/RHACO_Build_Prompt_Template_Guide_v2_2.md#2-when-to-use-it--and-when-not) gives the conditions:

- several independently ownable modules;
- a script that can produce an inspectable artifact from the current build;
- a concrete external reference to score against;
- a budget you can afford.

Neither recorded harness met its own bar. The upstream project reports about 20M output tokens across six runs without clearing its bar. The RHACO run used 20 of 28 builder rounds and ended `BOUNDED_FAIL`. v2.0 is roughly twice the length of v1.

The template is not suited to single-module tasks, or to outputs judged only by taste with no comparable artifact.

## 6. How to adapt it

1. **Copy the raw template** from the link in section 1.
2. **Remove the RHACO-specific material.** This means the provenance paragraph, the "Companion to" line, the Version History table, and the footer. Keep a one-line credit (section 8). You may keep the P1–P7 labels (section 4) or drop them. Each label is a claim that its section's mechanism implements the principle, so if you remove a mechanism, remove its label too.
3. **Fill every `{{SLOT}}`** using the guide's [section 3](campaign/RHACO_Build_Prompt_Template_Guide_v2_2.md#3-filling-the-slots). Its per-domain table covers web or 3D apps, data pipelines, HTTP services and document generators, and [section 9](campaign/RHACO_Build_Prompt_Template_Guide_v2_2.md#9-minimal-worked-instance-non-visual) is a worked non-visual instance. The verification block decides whether the harness functions at all. Your probe output must be directly comparable to your reference, and a second agent must be able to inspect it without running the build.
4. **If you have no external reference or calibration artifacts,** follow what the template itself says. Drop the blind gate, and declare the critic's scale ordinal and uncalibrated in `SCOPE.md`. PASS then cannot be reached from critic scores. That is deliberate: the best honest outcome available is `BOUNDED_FAIL`, which is the outcome the pilot recorded.
5. **Name your orchestration mechanism** for what your tool actually provides. Sequential waves in one session keep the builder/critic separation, and that separation is the part that matters.
6. **Choose one human-gate policy** (guide [section 6](campaign/RHACO_Build_Prompt_Template_Guide_v2_2.md#6-human-gate-policy)) and delete the others.
7. **Delete the `<!-- -->` guidance comments,** confirm that a search for `{{` returns nothing, and work through the guide's [pre-launch checklist](campaign/RHACO_Build_Prompt_Template_Guide_v2_2.md#10-pre-launch-checklist).

**Change these only on purpose.** Some rules carry the meaning of the terminal state:

- `PASS` only from probe data with every gate green;
- budget exhaustion is always `BOUNDED_FAIL`;
- never probe through a mock;
- `UNVERIFIED` survives integration;
- the critic writes no code;
- the build never certifies its own authority boundary.

Relaxing any of them changes what a declared `PASS` means. That is a design argument drawn from the pilot's record, not a measured result.

## 7. What a run would tell us

One run of this template would be the first evidence about v2.x itself. A run that ends `BOUNDED_FAIL` or `INVALID` with its record intact is as informative as a `PASS`.

## 8. Licence and credit

Template v2.2 and Guide v2.2 are available under the [MIT License](../LICENSE-CODE). The structure derives from [`rawprogress/fable-cities`](https://github.com/rawprogress/fable-cities/blob/main/PROMPT.md), which is also MIT-licensed. A suggested credit line for an adapted copy:

> Adapted from the RHACO Build Prompt Template v2.2 (Kris E. Granholm, MIT), itself derived from the structure of rawprogress/fable-cities `PROMPT.md` (MIT).
