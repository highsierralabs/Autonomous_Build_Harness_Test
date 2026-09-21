# PROMPT_TEMPLATE.md — Self-Verifying Multi-Agent Build Prompt

Boilerplate derived from the harness structure in `rawprogress/fable-cities/PROMPT.md`.
Fill every `{{SLOT}}`. Delete this header block and the `<!-- guidance -->` comments before use.
See `HOW_TO_USE.md` for slot-by-slot instructions.

---

# Goal

Build a {{TARGET_CLASS}} in {{STACK}}, from this empty folder.
The bar is {{QUALITY_BAR}}. Never {{ANTI_PATTERN}}.

<!-- TARGET_CLASS: name a real, external thing the output is measured against ("a Cities: Skylines II–class city builder", "a pandas-class dataframe library", "a Stripe-docs-class API reference site").
     STACK: language, framework, build tool, module system. Pin versions or say "latest release".
     QUALITY_BAR: 3–6 concrete, observable properties, not adjectives.
     ANTI_PATTERN: the one named failure mode that fails the whole project on sight. -->

# How to work

1. **Architecture first.** Before any feature code, write `ARCHITECTURE.md`:
   - one folder per subsystem: {{MODULE_LIST}}
   - a shared {{CORE_DATA_MODEL}} that every module reads from and writes to
   - the public API each module must expose, and the events it emits
   - conventions: {{UNITS_AND_CONVENTIONS}}
   - determinism: {{DETERMINISM_POLICY}}
   - a performance budget: {{PERF_BUDGET}}
   - an asset/data policy: {{ASSET_DATA_POLICY}}
   Isolate module failures so one broken module never takes the whole {{ARTIFACT_NOUN}} down.

<!-- MODULE_LIST: 8–15 nouns. Each becomes a folder, an agent, and a critic target. Too few = agents collide; too many = integration cost dominates.
     CORE_DATA_MODEL: the single shared state object/schema/DB. Only the integrator may change it.
     UNITS_AND_CONVENTIONS: units, coordinate frames, naming, timestamp format, error-handling style, whatever removes cross-module ambiguity.
     DETERMINISM_POLICY: "seeded RNG only", "fixed clock in tests", "no network in unit paths", etc. Needed so the critic can reproduce what it saw.
     PERF_BUDGET: numeric, machine-checkable. "≥50 fps at 1080p, ≤1500 draw calls" / "p95 latency ≤120 ms at 200 rps" / "full test suite ≤90 s".
     ASSET_DATA_POLICY: what may be pulled in and from where (licences, sources, synthetic-only, no PII, etc.).
     ARTIFACT_NOUN: "game", "service", "site", "pipeline", "document set". -->

2. **Build the verification loop before the {{ARTIFACT_NOUN}}.** Write `{{PROBE_TOOL}}`: a headless tool that {{PROBE_ACTION}}, waits until ready, applies a named {{PRESET_KIND}}, and writes {{PROBE_OUTPUT}} plus a JSON log containing {{PROBE_LOG_FIELDS}}.
   Every module also ships a **showcase mode** that stages a representative, minimal instance of just that module so it can be probed in isolation.
   **No agent may claim anything it has not run the probe on and inspected.**

<!-- This is the slot that decides whether the harness works. If you cannot name PROBE_TOOL and PROBE_OUTPUT concretely, stop and design them before anything else.
     PROBE_TOOL: a script path, e.g. tools/screenshot.mjs, tools/probe.py, tools/render-and-diff.sh.
     PROBE_ACTION: "loads the app in headless Chrome", "runs the pipeline on fixture set F", "renders the doc to PDF", "boots the service and hits /health then the golden request set".
     PRESET_KIND: the axis the critic varies — "camera preset and time of day", "input fixture and config profile", "page and viewport", "seed and dataset size".
     PROBE_OUTPUT: the thing a critic can look at — PNG, rendered PDF, golden-output diff, benchmark table, trace file.
     PROBE_LOG_FIELDS: e.g. "console errors, fps, draw calls" / "exit code, stderr, wall time, peak RSS, schema-validation result" / "test pass/fail counts, coverage, lint errors". -->

3. **Fan out.** Use {{ORCHESTRATION_MECHANISM}}. One builder agent per module, each owning only its folder. Run in waves ordered by dependency:
   - Wave 1: {{WAVE_1_MODULES}}
   - Wave 2: {{WAVE_2_MODULES}}
   - Wave 3: {{WAVE_3_MODULES}}
   Between waves, exactly one **integrator agent** — the only agent allowed to touch `{{CORE_PATH}}` — applies builders' core-change requests and fixes the seams.

<!-- ORCHESTRATION_MECHANISM: name what actually exists in your environment — a subagent/task tool, a worktree-per-agent script, a CI matrix, or "sequential waves in a single session if no parallelism is available". The original used a private command; do not copy its name.
     WAVE_n_MODULES: wave 1 = things with no upstream deps; wave 2 = things that consume wave-1 APIs; wave 3 = integration/demo/end-to-end.
     CORE_PATH: the folder holding the shared data model and cross-cutting infra. -->

4. **Gauntlet every module.** After each builder round, a separate **critic agent** — {{CRITIC_PERSONA}}, who writes no code — runs its own probes across several {{PRESET_KIND}} values, checks the API contract, the {{PROBE_LOG_FIELDS}}, and scores 0–10 against {{REFERENCE_CORPUS}}:
   - 10 = {{ANCHOR_10}}
   - 8.5 = {{ANCHOR_8_5}}
   - 7 = {{ANCHOR_7}}
   - 5 = {{ANCHOR_5}}
   Pass = ≥ {{PASS_THRESHOLD}} with {{ZERO_TOLERANCE_CONDITION}}. Below that, the builder receives the ranked issue list and goes again, up to {{MAX_ROUNDS}} rounds.

<!-- CRITIC_PERSONA: a domain expert with a reputation to protect and nothing to defend in the code — "a brutal AAA art director", "a principal SRE doing a production-readiness review", "a journal referee for a methods paper", "a technical editor at a top documentation team".
     REFERENCE_CORPUS: real, external, concrete artefacts the output is compared to — shipped-product screenshots, a competitor's public API responses, published benchmark numbers, a style guide plus exemplar pages, a conformance suite. If this is vague, the score is vague.
     ANCHOR_*: written definitions. Each anchor should be recognisable from the probe output alone.
     PASS_THRESHOLD: 8.5 in the original. Set deliberately; the original never cleared it.
     ZERO_TOLERANCE_CONDITION: "zero console errors" / "zero failing tests and zero schema violations" / "zero lint errors and no TODOs".
     MAX_ROUNDS: 3–5. Beyond that the builder is thrashing; escalate instead. -->

5. **Final gate.** A whole-{{ARTIFACT_NOUN}} critic scores {{END_TO_END_TARGET}}. Then **blind judges** receive pairs of probe outputs labelled only A and B (ours vs. {{REFERENCE_CORPUS}}, order shuffled) and state which is better and why.

<!-- END_TO_END_TARGET: the integrated deliverable — the demo scene, the full pipeline on the holdout fixture, the complete rendered document set.
     Blind pairing only works if the reference and the output are the same kind of artefact. Design PROBE_OUTPUT so that they are. -->

6. **Loop until every critic passes.** Persist scores, round counts, and open issues to `{{STATE_FILE}}` so each iteration resumes from the weakest module, not from scratch.

<!-- STATE_FILE: docs/STATUS.json or equivalent. Schema suggestion in HOW_TO_USE.md. -->

# Rules

- Never inflate scores. Report real numbers, failed rounds, and what is still missing.
- Never edit another module's folder. Core changes go through the integrator.
- Keep {{LIVE_CONDITION}} at all times; other agents are probing it.
- {{HUMAN_GATE_POLICY}}

<!-- LIVE_CONDITION: "the dev server running and the app loadable" / "the test fixtures and probe script runnable from a clean checkout" / "main branch green".
     HUMAN_GATE_POLICY — pick one:
       (a) Autonomous: "Do not ask me questions. Make routine decisions yourself, state assumptions in STATE_FILE, keep going."
       (b) Gated:      "Make routine decisions yourself and log assumptions to STATE_FILE. Stop and ask before: changing the core data model, changing any public API contract, or lowering a threshold. Otherwise keep going."
       (c) Reviewed:   "Do not begin a new wave until I have ratified the previous wave's STATE_FILE." -->

Start now.
