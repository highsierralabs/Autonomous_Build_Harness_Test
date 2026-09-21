# The Measurement Philosophy, in its frozen portable form

This folder holds one file: [`measurement-philosophy.md`](measurement-philosophy.md), RHACO's seven principles written as domain-neutral operating rules. It is about 800 words. If you want to know what the build prompt in this repository was standing on, this is the shortest accurate answer.

## What it is

RHACO's Measurement Philosophy is the methodological charter of a small physics observatory. The charter itself is written in the observatory's own terms: detectors, baselines, event classes. In August 2026 RHACO ran a separate campaign to translate the seven principles into a form that needs no knowledge of the observatory to read, while keeping the function each principle was distilled to serve. The test it set itself was whether the result still encoded the reasoning system the observatory had actually arrived at in practice, and not a generic list of good engineering advice.

The output of that campaign is this file. It was reviewed against a fidelity checklist and **frozen on August 16, 2026**. Frozen means its identity is fixed: filename, frontmatter, display name, body, and full-file hash. Any change is a new version, never an edit.

| | |
|---|---|
| File | `measurement-philosophy.md` |
| Size | 5,333 bytes |
| SHA-256 | `3f9b520ba986175a923ed01bb6822ccc8eccef3e1793519362f00d6e52016820` |
| Frozen | 2026-08-16, by RHACO's Measurement Philosophy transfer-artifact campaign |

The copy here is byte-identical to RHACO's. You can check it against the hash above.

## How to read it

The file is written as instructions to an engineering agent, because that is what it is for: the frontmatter at the top makes it loadable as a Claude Code output style. Read past that and it is simply seven principles and three operating rules.

Two things in it are easy to skim over and matter most:

- **The opening paragraph and rule R1.** Apply a principle only where it materially fits. Do not recite or label the principles to show compliance, and do not manufacture checks, distinctions or documentation to look rigorous. The philosophy is explicitly against ceremony.
- **Rule R2.** Agreement between checks counts as independent confirmation only when the checks can fail in different ways. Checks that share a failure mode are one observation, not several.

## Its relationship to the build prompt, stated carefully

This file is **not** what the build prompt was written from, and nothing in the build's record shows it playing any part in the build.

- The prompt was rewritten against the **charter** (Measurement Philosophy v1.4.1), which is an RHACO reference document and is not reproduced in this repository.
- This file is a **sibling**: a separate, earlier distillation of the same seven principles, made for a different purpose. That purpose is an RHACO experiment on whether the principles change an AI agent's behaviour when supplied as an operating style. That experiment is RHACO's own and is not part of this repository.

It is included because it is the compact, self-contained statement of the principles, and because the charter is much more to unpack. For how each principle became a section of the prompt, and where that transfer failed, read [`../MEASUREMENT_PHILOSOPHY.md`](../MEASUREMENT_PHILOSOPHY.md).

One observation a careful reader will make, recorded here so it is not left to be discovered. Rule R2 in this file, frozen on August 16, says exactly what the build test later had to learn the hard way. RHACO's first rewrite of the build prompt, written in early September, still described its verification layers as *independent*, and the post-pilot review had to remove the word. The dates are a fact. Why a lesson RHACO had already written down did not carry into the rewrite is not something the record answers.

## Licence

This file is RHACO's work and is shared under [CC BY 4.0](../../LICENSE), like the rest of this repository's documentation.
