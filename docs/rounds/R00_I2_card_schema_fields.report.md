# R00_I2_card_schema_fields -- strand report (round 0 inspection)

strand_id: I2
agent_id: abc6a30e133d67c81
workflow_run: wf_c2507f3a-9da
model_id: You are powered by the model named Sonnet 5. The exact model ID is claude-sonnet-5.
t_start_utc: 2026-09-04T02:33:55.2969152Z
t_end_utc: 2026-09-04T02:35:47.9036689Z
transcript_last_write_utc: 2026-09-04T02:37:18+00:00
files_read:
  - C:\RHACO\docs\reference\RHACO_Card_YAML_Schema_Specification_v1_9.md (full, lines 1-633)
  - C:\RHACO\rhaco\RHACO_corpus_index.py (lines 420-534, 560-618, 690-1034, plus grep hits)
  - C:\RHACO\tools\RHACO_tool_catalog_librarian.py (lines 400-518, 634-693, plus grep hits)
commands_run:
  - (Get-Date).ToUniversalTime().ToString("o")  [x2, start and end]
  - Get-ChildItem -Path "C:\RHACO\docs\reference\" -Filter "*Card*" | Select-Object Name, Length
  - wc -l on the three target files (read-only line count)
  - Grep: pattern '_card_row|_card_id_aliases|emit_edges|CREATE TABLE|def _card_|card_programs|card_tags' in RHACO_corpus_index.py
  - Grep: pattern 'VALID_PROGRAMS|DENY_DIRS|DEFAULT_ROOT|lifecycle_state|VALID_STATUSES|NAMING.*REGEX|_regex|re\.compile' in RHACO_tool_catalog_librarian.py
  - Grep: pattern '^def _doc_id|_ALIAS_CANONICAL_RE|_EVENT_ID_RE\s=' in RHACO_corpus_index.py
  - Grep: pattern 'canonical_id|is_amendment_of|_build_id_index|_resolve_reference|class Card\b' in RHACO_tool_catalog_librarian.py
  - Grep: pattern '_CARDS_COLUMNS\s=|def _as_str|def _as_int|def _norm_date|def _mtime_utc|def _sha256_file' in RHACO_corpus_index.py
  - Grep: pattern '"notes"|\.get\(.notes.\)|amendment_seq' in RHACO_corpus_index.py (no matches)
deviations: One initial Bash `ls -la` invocation failed on quoting (POSIX sh syntax error) before any file was touched; it was immediately replaced with a PowerShell Get-ChildItem listing. No file content was read via the failed call, no state changed, and only the two required Get-Date PowerShell timestamp commands otherwise ran as PowerShell. All file reads stayed within the five allow-listed source paths for this strand; no Python was run, no module was imported, no database file was opened. The dispatch record's illustrative example ("RHACO-HND-20260903-001 currently has two cards: the hand and its Amendment A1") was not independently verified against a handoff card pair on disk — that specific document pair is outside this task's named Sources list (identity.reference, corpus_index.py, catalog_librarian.py) and doing so was not necessary to answer the assigned questions, which were answered from the verified mechanics of canonical_id derivation / the cards table PRIMARY KEY / is_amendment_of / the parent field.

---

## 1. Card schema v1.9 field inventory

Required top-level sections (`RHACO_Card_YAML_Schema_Specification_v1_9.md` §4, lines 63-76; table lines 65-75): `identity` (Yes), `abstract` (Yes), `tags` (Yes or `[]`), `depends_on` (Yes or `[]`), `see_also` (Yes or `[]`), `superseded_by` (Yes or `null`), `location` (Yes), `notes` (Yes or `[]`). Optional top-level: `parent` (§5.9, lines 284-302) — present only on amendment child cards, paired with optional `amendment_seq` (line 293, 298).

`identity.*` sub-fields (§5.1, lines 82-130; schema example lines 86-101):
- `document` (required) — exact filename incl. extension, must match disk (line 105, 122).
- `doc_type` (required) — one of the 24 formalized codes, or `REF` (§6.1/§8); must match filename TYPE (line 106, 123).
- `date` (required) — ISO `YYYY-MM-DD` matching filename YYYYMMDD (line 107).
- `seq` (required) — 3-digit string, quoted to preserve leading zeros (line 108).
- `title` (required) — human-readable (line 109).
- `status` (required) — enum `Active | Baseline | Superseded | Archived | Draft` (line 110; full enum text §6.2 lines 322-334).
- `lifecycle_state` (conditionally required) — required only when `doc_type: CMP`; enum `OPEN, ACTIVE, REVIEW, CLOSED, PAUSED, ACTIVE-STANDING` per CMP Spec §5 (line 111); for non-CMP types it is optional/ignored but triggers informational warning `lifecycle_state_on_non_cmp` if present (§6.4, lines 356-358).
- `programs` (required) — list, one or more of `CR/EAS | Helio | DetPhys | Radon | Cross | Infra` (line 112; enum detail §6.3 lines 336-352). Multi-program membership explicitly legitimate.
- `project_knowledge` (required) — `in` or `out` (line 113).
- `current_version` (optional) — present only for versioned living documents; omitted for one-shot docs (line 114); §8 states it is mandatory for Infra reference cards (line 461).
- `schema_version` (required) — integer, must equal spec version; held at `1` through v1.9 (line 115; §12 notes lines 606, 608).
- `naming_convention_version` (required) — quoted string, must resolve to a version in the Naming Convention's history table (line 116, 125-126); staleness (2+ minor versions behind) is a warning not an error (line 127).
- `last_human_review` (required) — ISO date; >90 days old triggers `stale_review` warning (line 117, 128).
- `reviewer` (required) — name of last reviewer (line 118).

`abstract` (§5.2, lines 144-161): free text, block scalar (`>` or `|`), target 40-80 words, Unicode-preserving.

`tags` (§5.3, lines 163-182): freeform list; lowercase-hyphenated by default with case-preserving exceptions from `TAG_CASING_EXCEPTIONS` allowlist (§6.5, lines 360-382: `path-A`, `path-B`, `path-X`, `K-value`, `D512`, plus composite `<allowlist-entry>-<lowercase-suffix>` forms).

`depends_on` / `see_also` (§5.4-5.5, lines 184-233): each entry `{id, note}`; `id` is canonical `RHACO-TYPE-YYYYMMDD-SEQ` (no filename/extension) or `external:<Name>` for whitelisted external refs (line 225-233).

`superseded_by` (§5.6, lines 235-254): single object `{id, note}` or `null`; required non-null only when `status: Superseded`; mutually exclusive with `parent` (line 254).

`location.local_path` (§5.7, lines 256-269): absolute Windows path, must exist at validation time.

`notes` (§5.8, lines 271-282): free-form list of strings; `[]` permitted.

`parent` (§5.9, lines 284-302): `{id, note}` object present only on amendment child cards; `amendment_seq` is an optional sibling string (`A1`, `A2`, …).

Vocabularies:
- **doc_type** (§6.1, lines 308-320): 24 formalized codes: `EVT FRB GLE ANL CAL FIX OBS HWR SPC NET RDM HND EXT DLB CCX CHG MTN CMP INC SOP CHR COR FND PUB`. Retired-but-grandfathered: `SCA` (retired 2026-04-22), `THR` (retired at NC v1.2) — both emit `retired_type_code` warning, escalating to error on files modified after retirement. `REF` is the special value for pre-type-code Infra docs (§8 line 461, §11.3 line 592) — not counted among the "24."
- **status** (§6.2, lines 322-334): `Active | Baseline | Superseded | Archived | Draft`, each with the descriptive text quoted at lines 325-331.
- **lifecycle_state** (§6.4, lines 356-358; enum first given §5.1 line 111): `OPEN, ACTIVE, REVIEW, CLOSED, PAUSED, ACTIVE-STANDING`; CMP-only rule quoted verbatim: *"If `identity.doc_type == 'CMP'`, `identity.lifecycle_state` is required and must be one of `[OPEN, ACTIVE, REVIEW, CLOSED, PAUSED, ACTIVE-STANDING]`. For all other doc types, the field is optional; if present, it is ignored by validation but emits informational warning class `lifecycle_state_on_non_cmp`"* (lines 356-358).
- **programs** (§6.3, lines 336-352): `CR/EAS, Helio, DetPhys, Radon, Cross, Infra`, each with descriptive text.
- **project_knowledge**: `in | out` (§5.1 line 113; no separate enum section — only stated inline).

## 2. Materialization (card key → table.column)

DDL is in `RHACO_corpus_index.py` lines 438-505 (`_METADATA_DDL`). Row-building function `_card_row` (lines 703-739); column-name tuple `_CARDS_COLUMNS` (lines 305-311).

`cards` table (yaml_path is `PRIMARY KEY`, line 440), columns and source, per `_card_row` lines 714-736:
- `yaml_path` ← `card.yaml_path` (line 715)
- `doc_id` ← `_doc_id(card)` = `card.canonical_id`, or the `.card.yaml` filename stem if non-canonical/REF (lines 694-700, 716)
- `doc_type` ← `identity.doc_type` (line 717)
- `date` ← `identity.date`, normalized to ISO via `_norm_date` (line 718, fn at 575-590)
- `seq` ← `identity.seq` (line 719)
- `title` ← `identity.title` (line 720)
- `status` ← `identity.status` (line 721)
- `project_knowledge` ← `identity.project_knowledge` (line 722)
- `current_version` ← `identity.current_version` (line 723)
- `schema_version` ← `identity.schema_version`, coerced int (line 724)
- `naming_convention_version` ← `identity.naming_convention_version` (line 725)
- `lifecycle_state` ← `identity.lifecycle_state` (line 726)
- `last_human_review` ← `identity.last_human_review` (line 727)
- `reviewer` ← `identity.reviewer` (line 728)
- `doc_filename` ← `card.doc_filename` (actual discovered basename, not literally re-read from `identity.document`) (line 729)
- `doc_path` ← `card.doc_path` (line 730)
- `local_path` ← `location.local_path` (line 731)
- `abstract` ← `data.abstract` (line 732)
- `card_sha256` ← sha256 of the `.card.yaml` file bytes (line 733, `_sha256_file` 593-600)
- `card_mtime_utc` ← filesystem mtime of the `.card.yaml` (line 734, `_mtime_utc` 603-608)
- `indexed_at_utc` ← run timestamp (line 735)

Multi-valued fields:
- `programs` → `card_programs(yaml_path, program)` junction table, one row per program (lines 467-472, 737, 848-849, 869).
- `tags` → `card_tags(yaml_path, tag)` junction table, one row per tag (lines 474-479, 738, 850-851, 872).

**Dropped (never written to any table by `_card_row`/`emit_edges`, confirmed by grep — no `"notes"` or `amendment_seq` references anywhere in `RHACO_corpus_index.py`):**
- `notes` — not materialized into any column; dropped entirely from the index (only lives in the card YAML itself).
- `amendment_seq` — not materialized; dropped.
- `identity.document` (the literal string) is not itself stored — `doc_filename` stores the Card object's discovered on-disk basename instead (line 729; these are validated equal by the librarian, but the index stores the filesystem-derived value, not a re-read of the YAML key).
- `depends_on`, `see_also`, `superseded_by`, `parent` are **not** stored as columns/fields verbatim — they are consumed only to derive `edges` rows (see §3) and are not otherwise retained (e.g., the free-text `note` on each ref is captured only inside the `edges.note` column, not as a card-level field).

## 3. Edges

Table DDL: `edges(from_id, to_id, relation, source_field, from_yaml_path, note, resolved)` (lines 481-492, `resolved INTEGER NOT NULL DEFAULT 0`). Built by `emit_edges()` (lines 934-1033), docstring "Relations (CHG-20260628-004 §3.A)" lines 937-959.

Relations materialized, `source_field`, direction, and resolution rule (quoting the docstring):
- **`cites`** — source_field `depends_on` or `see_also` (line 981, 1002). *"every depends_on/see_also ref (source_field preserved). resolved=0 IFF the ref would be an unresolved_reference finding (not external AND `_resolve_reference` is None). This is the ONLY relation that carries resolved=0"* (lines 938-943). Direction: `from_id` = the citing card's own id (`src_id`, line 978), `to_id` = the resolved target's canonical id, or the raw literal `rid` string if unresolved (lines 995-1001) — i.e., from → to means "from cites to."
- **`campaign_child`** — source_field `depends_on` (line 1007). *"directional campaign->child (from_id=CMP, to_id=child), the ref note preserved. see_also->CMP stays a cites edge, not membership. resolved=1"* (lines 956-959). Emitted alongside a `cites` edge whenever a resolved `depends_on` target's `doc_type == "CMP"` (lines 1004-1007): `from_id` = the CMP's id, `to_id` = the citing (child) card's id.
- **`supersedes`** — source_field `superseded_by` (line 1016). *"superseded_by mapping, emitted only when it resolves to a DISTINCT target (a self-edge from a shared-canonical-id version pair is skipped...)"* (lines 944-947). Direction: `from_id` = the superseding-relationship's source card, `to_id` = the resolved `superseded_by.id` target (lines 1009-1017) — from → to means "from is superseded by to" (i.e., the retired doc points to its replacement).
- **`amends`** — source_field `parent` (line 1025). *"amendment child (is_amendment_of) -> parent. from_id is the amendment's DISTINCT filename stem (an amendment shares its parent's canonical id by design); to_id the shared parent canonical id. resolved=1 by construction"* (lines 948-955). `from_id` = `_stem(card.doc_filename)` (the amendment's own filename stem, distinct from the shared doc_id), `to_id` = `parent_id` from `is_amendment_of()` (lines 1020-1025).

`resolved` flag meaning: 1 = target identity was found (via `_resolve_reference`) or is an external whitelisted ref or is resolved-by-construction (`supersedes`, `amends`, `campaign_child` all force `resolved=1` when emitted); 0 only ever occurs on `cites` edges where the reference id did not resolve and is not external (lines 992-1002) — designed so `count(edges WHERE resolved=0)` reconciles exactly with the librarian's `unresolved_reference` finding count (line 943).

Unresolved targets are retained, not dropped: for an unresolved `cites` edge, `to_id` is set to the raw literal `rid` string (the unresolved id text itself) rather than being nulled or omitted, and the edge row is still inserted with `resolved=0` (lines 998-999, 1002).

## 4. Identity

`doc_id` format: `_doc_id(card)` (lines 694-700) returns `card.canonical_id`, i.e. `f"RHACO-{doc_type}-{YYYYMMDD}-{SEQ:03d}"` (librarian `Card.canonical_id` property, `RHACO_tool_catalog_librarian.py` lines 646-664, format string line 662), or — if `canonical_id` is empty (non-canonical/REF) — the `.card.yaml`'s own filename stem (line 700).

Amendment children share the parent's doc_id **by design**: per Card Schema §5.9 (lines 300-302), *"An amendment child card's `identity.doc_type`/`date`/`seq` **remain the parent's**, so its parsed canonical id **is** the parent's canonical id. This is intentional, not a collision"*. Confirmed in code: `is_amendment_of()` (`RHACO_tool_catalog_librarian.py` lines 520-545) derives the parent id by parsing the amendment's *filename* through `CANONICAL_FILENAME_RE` (line 542, regex defined lines 610-613) — i.e. it does not read a distinct child identity block, matching the spec's statement that the amendment card's own `identity` block literally repeats the parent's `doc_type`/`date`/`seq`.

Disambiguating column: the `cards` table's `PRIMARY KEY` is **`yaml_path`**, not `doc_id` (line 440; `doc_id` only carries a non-unique index, `ix_cards_doc_id` line 462). So a parent card and its amendment child card(s) sharing one `doc_id` occupy **separate rows**, keyed uniquely by their distinct `.card.yaml` paths, both indexed under the same `doc_id` value.

Consequence for a UI asking "the document with id X": a query filtering `cards WHERE doc_id = X` is not guaranteed to return exactly one row — for a parent with N amendments it returns 1 (parent) + N (child) rows, all sharing `doc_id` but distinguished by `yaml_path`/`doc_filename`. A card-panel UI built assuming doc_id is a unique row key will either need to disambiguate (e.g., by `yaml_path`, or by filtering out amendment rows via `parent`/filename pattern) or will silently pick an arbitrary one of several matching rows. (The dispatch record's example of RHACO-HND-20260903-001 having a hand card + an Amendment A1 card sharing that doc_id illustrates exactly this shape; I did not independently re-derive that specific pair from disk, as it falls outside this strand's five allow-listed source files — see deviations.)

## 5. status vs. lifecycle_state

Spec text (§5.1.1, lines 132-142), quoted:

> "Two distinct lifecycles exist for CMP documents and must be tracked separately:
>
> **`status`** — the document-as-library-artifact lifecycle. Applies to all doc types. Values: `Active` (under active editorial maintenance), `Baseline` (settled reference, low edit cadence), `Draft` (not yet ratified), `Superseded` (replaced by a newer version), `Archived` (out of active library, historical record only). Answers: *what is the editorial state of this file?*
>
> **`lifecycle_state`** — the campaign-as-investigation lifecycle. Applies only to CMP documents. Values per CMP Specification §5: `OPEN`, `ACTIVE`, `REVIEW`, `CLOSED`, `PAUSED`, `ACTIVE-STANDING`. Answers: *what state is the underlying investigation in?*
>
> The two channels are independent. A CLOSED CMP whose charter is the historical record carries `status: Baseline, lifecycle_state: CLOSED`. A PAUSED investigation whose charter is still being maintained carries `status: Active, lifecycle_state: PAUSED`. An OPEN CMP not yet executing carries `status: Active, lifecycle_state: OPEN`... An ACTIVE-STANDING engagement-class CMP... carries `status: Active, lifecycle_state: ACTIVE-STANDING` indefinitely..." (lines 132-140)

Document types carrying `lifecycle_state`: only `doc_type: CMP` per the conditional rule (§5.1 line 111, §6.4 lines 356-358). All other doc types may carry the field but it is ignored by validation and triggers the informational `lifecycle_state_on_non_cmp` warning (line 358; code confirms this exact behavior at `RHACO_tool_catalog_librarian.py` lines 981-1000, including the literal warning code `lifecycle_state_on_non_cmp` at line 999).

## 6. Facet candidates in the data model

| Facet | Source | Evidence |
|---|---|---|
| document type (`doc_type`) | card (`identity.doc_type`) → index `cards.doc_type` column, indexed (`ix_cards_doc_type`) | Schema §5.1 line 106; index DDL line 442, 463; `_card_row` line 717 |
| date | card (`identity.date`) → index `cards.date`, normalized via `_norm_date`, indexed (`ix_cards_date`) | Schema §5.1 line 107; index DDL line 465; `_card_row` line 718 |
| status | card (`identity.status`) → index `cards.status`, indexed (`ix_cards_status`) | Schema §5.1 line 110, §6.2; index DDL line 464; `_card_row` line 721 |
| lifecycle_state | card (`identity.lifecycle_state`, CMP-only) → index `cards.lifecycle_state` column (present, but not separately indexed — no `ix_cards_lifecycle_state` in the DDL block read) | Schema §5.1 line 111, §6.4; index DDL line 451 (column only); `_card_row` line 726 |
| program | card (`identity.programs`, list) → index `card_programs(yaml_path, program)` junction table, indexed on `program` (`ix_cardprog_program`) | Schema §5.1 line 112, §6.3; index DDL lines 467-472; `_card_row` line 737 |
| tags | card (`tags`, list) → index `card_tags(yaml_path, tag)` junction table, indexed on `tag` (`ix_cardtag_tag`) | Schema §5.3; index DDL lines 474-479; `_card_row` line 738 |
| project_knowledge | card (`identity.project_knowledge`) → index `cards.project_knowledge` column (no dedicated index seen in the DDL block read) | Schema §5.1 line 113; index DDL line 447; `_card_row` line 722 |
| path/location | card (`location.local_path`) → index `cards.local_path` column, **plus** filesystem-derived `cards.doc_path`/`doc_filename` (from the librarian's walk, not re-read from `identity.document`) | Schema §5.7; index DDL lines 455-456; `_card_row` lines 729-731 |

All eight facet candidates originate in the card YAML (`identity.*` or top-level `tags`); none is invented independently by the index — the index's role is purely to mirror the card onto SQL-queryable columns/junction tables (per `_card_row`'s own docstring, "the index mirrors what is on disk; it does not validate," lines 706-708). The `doc_path`/`doc_filename` half of the "location" facet is filesystem-derived (the librarian's on-disk walk result) rather than a literal re-read of `identity.document`.

## 7. UNVERIFIED

- The dispatch record's specific claim that "RHACO-HND-20260903-001 currently has two cards: the hand and its Amendment A1" was not independently confirmed against the actual `.card.yaml` files on disk — that specific handoff/amendment pair lies outside this strand's five allow-listed source paths (only `RHACO_Card_YAML_Schema_Specification_v1_9.md`, `RHACO_corpus_index.py`, and the specified constants/functions in `RHACO_tool_catalog_librarian.py` were in scope), and it was not needed to answer Q4 from the verified general mechanism (`canonical_id`, PRIMARY KEY on `yaml_path`, `is_amendment_of`).
- Two divergences observed between the Card Schema v1.9 *text* and the *implementation* in `RHACO_tool_catalog_librarian.py`, noted here as they bear on Q1 (doc_type vocabulary) but were outside the literal ask (VALID_PROGRAMS / DENY_DIRS / DEFAULT_ROOT / status vocabulary / lifecycle_state rules / naming-convention regex only): (a) `FORMALIZED_DOC_TYPES` (lines 424-428) contains 25 codes including `GDE`, versus the spec's explicitly enumerated 24 codes (§6.1 lines 313-316) which do not list `GDE`; (b) `RETIRED_DOC_TYPES` (lines 431-438) includes a third retired code `BLD` (retired 2026-06-14 per NC v1.15) not mentioned anywhere in the v1.9 spec text, which names only `SCA` and `THR` (§6.1 line 320). I read both sources directly and confirm this is a genuine text/implementation gap, not a reading error, but did not investigate which is authoritative or whether a schema v1.10+ / NC v1.15+ text reconciles it — that lies outside the two files in scope.
- Whether `project_knowledge` and `lifecycle_state` have a dedicated SQL index (beyond the plain column) was checked only against the `_METADATA_DDL` block at lines 438-505; no `CREATE INDEX` statement targeting those two columns appears in that block, so I report their absence as observed in the read region, not as a claim about index behavior elsewhere in the 2377-line file outside the regions I was directed to and did read (DDL block, `_card_row`, `_card_id_aliases`, `emit_edges`, plus the targeted greps run above).
