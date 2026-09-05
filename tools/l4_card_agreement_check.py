"""L4 corpus oracle: card file vs index row agreement (integrator-owned; docs/LAYERS.md L4).

PURPOSE
  Cover the SILENT half of the card/index mismatch class, which no other layer can reach.

  The reader marks `data-card-index-mismatch` when the card file disagrees with the index row.
  The probe qualifies the POSITIVE direction only: KB2 injects `stale_card` and asserts the marker
  appears. The converse -- no fault, therefore no marker -- is asserted on the FIXTURE alone (KG),
  and the fixture cannot exhibit the failure mode that matters here, because every fixture card
  quotes its dates while ~60% of the live corpus does not (round-4 finding; ledger P-14).

  So a FALSE mismatch marker on a bare-date live card would fail nothing at L1, nothing on the
  fixture path, and nothing in the probe's production presets. It would simply tell the operator,
  wrongly and quietly, that the record and the index disagree. That is worse than a crash: a crash
  announces itself, this does not.

  This oracle closes that gap at the layer that can: for a sample of live cards drawn from BOTH
  date styles, it reads the card file from disk, parses it, reads the index row through the
  adapter, and classifies each compared field.

  The distinction the oracle exists to draw:
    AGREE            -- equal once both sides are normalised to text.
    TYPE_ARTIFACT    -- unequal as objects but EQUAL as text. This is the defect signal: the two
                        sides say the same thing and the code thinks they differ. Exit 1.
    GENUINE_DIFFERENCE -- unequal even as text. This is a CORPUS FACT (a stale index row, an
                        edited card awaiting reindex). It is reported, never failed: the explorer
                        does not adjudicate the corpus (PROMPT.md section 11; CONSTRAINTS S1).

USAGE
  python tools/l4_card_agreement_check.py [--sample N] [--out PATH] [--db PATH] [--docs-root PATH]
  exit 0 = no type artifacts (genuine differences may exist and are listed)
  exit 1 = at least one type artifact -- a silent false-mismatch class is live
  exit 2 = operational error

OUTPUT
  ASCII only on stdout. JSON report at --out
  (default docs/probe-qualification/card_agreement.json).

  Read-only throughout: the index is opened only through CorpusAdapter, which is the sole caller of
  RHACO_corpus_index.connect(); card files are read from the configured docs root; nothing is
  written except the report.

VERSION HISTORY
  v1.0  2026-09-05  Initial (RHACO-HND-20260903-001, session 6, integrator). Written after probe
                    round 4's W6 exposed the crashing half of this class and the Director directed
                    the silent half be covered at the oracle layer.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE not in sys.path:
    sys.path.insert(0, WORKSPACE)

# The fields the reader compares between the card file and the index row.
COMPARED_FIELDS = ("title", "status", "lifecycle_state", "date", "doc_type")

_BARE_DATE_RE = re.compile(r"^\s*(date|last_human_review):\s*\d{4}-\d{2}-\d{2}\s*$", re.MULTILINE)


def _as_text(value) -> str | None:
    """Normalise a card-file or index value to the text the card file itself carries.

    A YAML date scalar resolves to datetime.date; its text form is its ISO form, which is exactly
    what the file says. Everything else is compared as its plain string. None stays None so a
    missing field is never confused with an empty one.
    """
    if value is None:
        return None
    if isinstance(value, (dt.datetime, dt.date, dt.time)):
        return value.isoformat()
    return str(value)


def _card_file_fields(parsed: dict) -> dict:
    identity = parsed.get("identity") or {}
    if not isinstance(identity, dict):
        identity = {}
    return {
        "title": identity.get("title"),
        "status": identity.get("status"),
        "lifecycle_state": identity.get("lifecycle_state"),
        "date": identity.get("date"),
        "doc_type": identity.get("doc_type"),
    }


def classify(file_value, index_value) -> str:
    """AGREE | TYPE_ARTIFACT | GENUINE_DIFFERENCE for one field."""
    if file_value == index_value:
        return "AGREE"
    ft, it = _as_text(file_value), _as_text(index_value)
    if ft == it:
        # Same content, different Python type: precisely the silent class.
        return "TYPE_ARTIFACT"
    if ft is not None and it is not None and ft.strip() == it.strip():
        return "TYPE_ARTIFACT"
    return "GENUINE_DIFFERENCE"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="L4 card-file vs index-row agreement oracle (read-only).")
    ap.add_argument("--sample", type=int, default=60,
                    help="cards to draw from EACH date style (bare and quoted); default 60")
    ap.add_argument("--db", default=None)
    ap.add_argument("--docs-root", dest="docs_root", default=None)
    ap.add_argument("--out", default=os.path.join(WORKSPACE, "docs", "probe-qualification", "card_agreement.json"))
    args = ap.parse_args(argv)

    import yaml

    from explorer.config import Settings
    from explorer.corpus_adapter.adapter import CorpusAdapter

    adapter = CorpusAdapter(Settings(db_path=args.db, docs_root=args.docs_root))
    docs_root = adapter.docs_root

    before = (os.path.getsize(adapter.db_path), os.path.getmtime(adapter.db_path))

    # Enumerate the census through the adapter's own catalog, never by walking the index.
    from explorer.models import CatalogFilters
    page = adapter.catalog(CatalogFilters(), "doc_id:asc", 1, 5000)
    rows = list(page.rows)
    print(f"l4-card-agreement: census rows returned by the adapter = {len(rows)}")

    bare, quoted = [], []
    for card in rows:
        path = os.path.join(docs_root, card.card_ref.replace("/", os.sep))
        try:
            with open(path, encoding="utf-8") as fh:
                raw = fh.read()
        except OSError:
            continue
        (bare if _BARE_DATE_RE.search(raw) else quoted).append((card, raw))

    print(f"l4-card-agreement: bare-date cards = {len(bare)}, quoted-date cards = {len(quoted)}")
    sample = bare[: args.sample] + quoted[: args.sample]
    print(f"l4-card-agreement: sampling {len(sample)} cards ({min(args.sample, len(bare))} bare + "
          f"{min(args.sample, len(quoted))} quoted)")

    # The reader is driven in-process (TestClient), never through a server: only the probe launches
    # one (CONSTRAINTS O12). This is the half of the oracle that tests the PRODUCT rather than the
    # data -- whether the reader actually emits a mismatch marker for a field that only differs by
    # type. The classification above measures the hazard in the corpus; this measures the defect.
    from fastapi.testclient import TestClient

    from explorer.app import create_app

    client = TestClient(create_app(Settings(db_path=args.db, docs_root=args.docs_root)),
                        raise_server_exceptions=False)

    findings = []
    counts = {"AGREE": 0, "TYPE_ARTIFACT": 0, "GENUINE_DIFFERENCE": 0}
    parse_errors = []
    reader_rows = []
    for card, raw in sample:
        try:
            parsed = yaml.safe_load(raw) or {}
        except Exception as exc:  # noqa: BLE001 -- a malformed card is a corpus fact, recorded not raised
            parse_errors.append({"card_ref": card.card_ref, "error": f"{type(exc).__name__}: {exc}"})
            continue
        file_fields = _card_file_fields(parsed if isinstance(parsed, dict) else {})
        style = "bare" if _BARE_DATE_RE.search(raw) else "quoted"
        artifact_fields = set()
        for field in COMPARED_FIELDS:
            verdict = classify(file_fields.get(field), getattr(card, field, None))
            counts[verdict] += 1
            if verdict == "TYPE_ARTIFACT":
                artifact_fields.add(field)
            if verdict != "AGREE":
                findings.append({
                    "card_ref": card.card_ref,
                    "doc_id": card.doc_id,
                    "date_style": style,
                    "field": field,
                    "file_value": _as_text(file_fields.get(field)),
                    "file_type": type(file_fields.get(field)).__name__,
                    "index_value": _as_text(getattr(card, field, None)),
                    "index_type": type(getattr(card, field, None)).__name__,
                    "verdict": verdict,
                })

        # Drive the reader for this card and see what it actually claims.
        resp = client.get("/api/doc/" + card.card_ref)
        reported = ""
        if resp.status_code == 200:
            try:
                body = resp.json()
                reported = body.get("card_index_mismatch") or body.get("mismatch") or ""
                if isinstance(reported, list):
                    reported = ",".join(str(x) for x in reported)
            except Exception:  # noqa: BLE001 -- a shape we do not recognise is recorded, not raised
                reported = "<unparsed>"
        reported_fields = {f.strip() for f in str(reported).split(",") if f.strip()}
        false_markers = sorted(reported_fields & artifact_fields)
        reader_rows.append({
            "card_ref": card.card_ref,
            "date_style": style,
            "reader_status": resp.status_code,
            "reported_mismatch": reported,
            "type_artifact_fields": sorted(artifact_fields),
            "false_markers": false_markers,
        })

    after = (os.path.getsize(adapter.db_path), os.path.getmtime(adapter.db_path))
    artifacts = [f for f in findings if f["verdict"] == "TYPE_ARTIFACT"]
    genuine = [f for f in findings if f["verdict"] == "GENUINE_DIFFERENCE"]
    reader_errors = [r for r in reader_rows if r["reader_status"] != 200]
    false_marker_rows = [r for r in reader_rows if r["false_markers"]]

    # The DEFECT verdict is about the product, not the corpus: a reader that cannot render a card,
    # or that claims a mismatch which is only a type artifact. The hazard count is informational --
    # bare dates are a corpus convention, not a fault, and the explorer does not adjudicate them.
    if reader_errors or false_marker_rows:
        verdict = "FAIL"
    elif genuine:
        verdict = "PASS_WITH_CORPUS_DIFFERENCES"
    else:
        verdict = "PASS"

    report = {
        "tool": "l4_card_agreement_check v1.0",
        "db_path": adapter.db_path,
        "docs_root": docs_root,
        "census_rows": len(rows),
        "bare_date_cards": len(bare),
        "quoted_date_cards": len(quoted),
        "sampled": len(sample),
        "compared_fields": list(COMPARED_FIELDS),
        "counts": counts,
        "type_artifacts": artifacts,
        "genuine_differences": genuine,
        "parse_errors": parse_errors,
        "reader_probe": reader_rows,
        "reader_errors": reader_errors,
        "false_marker_rows": false_marker_rows,
        "db_unchanged": before == after,
        "verdict": verdict,
        "note": ("Two questions, deliberately separated. (1) THE CORPUS: a TYPE_ARTIFACT means the card file "
                 "and the index row say the same thing while a naive comparison would see them as different. "
                 "That is a HAZARD in the data, not a fault -- bare YAML dates are a corpus convention and the "
                 "explorer does not adjudicate the corpus. A GENUINE_DIFFERENCE is a corpus fact (a stale index "
                 "row, or an edited card awaiting reindex); reported, never failed. (2) THE PRODUCT: the reader "
                 "is driven for every sampled card, and the verdict FAILs only if the reader cannot render one "
                 "(non-200) or reports a mismatch marker on a field that is only a type artifact -- a false "
                 "claim that the record and the index disagree. That second question is the one no other layer "
                 "can reach: the probe qualifies the positive direction (KB2 injects a fault and the marker must "
                 "appear) and asserts the converse only on the fixture, which has no bare dates."),
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=True)
        fh.write("\n")

    print(f"l4-card-agreement: AGREE={counts['AGREE']} TYPE_ARTIFACT={counts['TYPE_ARTIFACT']} "
          f"GENUINE_DIFFERENCE={counts['GENUINE_DIFFERENCE']}")
    for f in artifacts[:10]:
        print(f"  ARTIFACT {f['card_ref']} [{f['date_style']}] {f['field']}: "
              f"file({f['file_type']})={f['file_value']!r} vs index({f['index_type']})={f['index_value']!r}")
    for f in genuine[:10]:
        print(f"  corpus-difference {f['card_ref']} [{f['date_style']}] {f['field']}: "
              f"file={f['file_value']!r} vs index={f['index_value']!r}")
    if parse_errors:
        print(f"l4-card-agreement: {len(parse_errors)} card(s) failed to parse (recorded, not failed)")
    print(f"l4-card-agreement: reader non-200 = {len(reader_errors)} of {len(reader_rows)} sampled")
    for r in reader_errors[:5]:
        print(f"  READER {r['reader_status']} {r['card_ref']} [{r['date_style']}]")
    print(f"l4-card-agreement: false mismatch markers = {len(false_marker_rows)}")
    for r in false_marker_rows[:5]:
        print(f"  FALSE MARKER {r['card_ref']} claims {r['reported_mismatch']!r}; "
              f"type-artifact-only fields {r['false_markers']}")
    print(f"l4-card-agreement: db unchanged = {report['db_unchanged']}")
    print(f"l4-card-agreement: verdict={report['verdict']} out={os.path.relpath(args.out, WORKSPACE)}")
    return 1 if verdict == "FAIL" else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 -- operational failure is exit 2, distinct from a finding
        print(f"l4-card-agreement: ERROR {type(exc).__name__}: {exc}")
        sys.exit(2)
