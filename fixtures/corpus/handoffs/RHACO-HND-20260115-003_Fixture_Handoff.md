# RHACO-HND-20260115-003 -- Fixture Handoff

## 1. Purpose

This is a synthetic fixture handoff document used to qualify the RHACO
Corpus Explorer probe framework. It is not a real RHACO handoff and carries
no operational content.

## 2. Dependencies

This document's card declares two `depends_on` entries:

- The fixture campaign (RHACO-CMP-20260115-001) -- resolves, and (because the
  target is a CMP) produces a `campaign_child` edge alongside the `cites`
  edge.
- A deliberately non-existent id (RHACO-ANL-20260101-099) -- does not
  resolve, so the fixture index carries one `cites` edge with `resolved = 0`.

## 3. Amendment

This document has one amendment child card,
`RHACO-HND-20260115-003_Fixture_Handoff_Amendment_A1.md`, which shares this
document's canonical id by design (Card Schema v1.9 section 5.9).
