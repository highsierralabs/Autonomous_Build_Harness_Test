"""L4 direction oracle: the rendered edge sentence vs the recorded direction
(integrator-owned; docs/LAYERS.md L4; RHACO-CCX-20260905-001 section 4 step 3).

PURPOSE
  Close objective gate 7 -- "typed relation direction preserved" -- at the only
  layer left that can.

  Critic round 1 recorded gate 7 FAIL against a build that had asserted PASS. The
  machine-readable direction was, and is, correct: `data-edge-from`,
  `data-edge-to`, `data-edge-direction`, the outgoing/incoming buckets and the SVG
  arrowheads. The SENTENCE shown to a human was not: `RELATION_LABELS` held one
  label per relation and `Edge.direction_label` returned it regardless of
  direction, so an incoming edge printed the converse of the recorded fact. The
  current head of a supersession family read "is superseded by <its own
  predecessor>"; a campaign parent read "has campaign child <its own parent>".

  Nothing in the harness could see it. The probe's W5 preset asserts each edge's
  `direction_label` against `RELATION_LABELS` -- it compares the product against
  the constant the product renders from, so it can only detect a divergence
  between two copies of one answer. That is the SA-4 class: a check narrower than
  its apparent guarantee. The probe cannot be repaired (exhausted at 4 of 4,
  Director ruling, not waived), so W5's failure on direction-aware sentences is a
  declared BOUNDED_FAIL (BF-1) and this oracle is its compensating control.

THE INDEPENDENCE THAT MAKES IT AN ORACLE
  EXPECTED_SENTENCES below is written HERE, by hand, from what each relation means
  read from each of its two ends. It is NOT imported from `explorer.models`, and
  that is the whole point: an oracle that read the product's own table could not
  disagree with the product, which is precisely how the defect survived. If the
  product's labels change, this file must be changed too -- deliberately, by a
  human who has decided the new sentence is true -- and that friction is the
  instrument, not an inconvenience.

  The expectations are derived from CONSTRAINTS.md O8's edge semantics:
  `from` is the citing card / the superseded document / the amendment stem /
  the campaign; `to` is the cited card / the superseding document / the amended
  parent / the campaign member.

WHAT IT CHECKS, per typed edge on a sampled card's lineage page
  1. DIRECTION SENTENCE -- the rendered sentence equals the expectation for
     (relation, direction). A mismatch is a DEFECT.
  2. CONVERSE GUARD -- the rendered sentence is not the expectation for the
     OPPOSITE direction. This is the specific failure the critic found, called out
     separately so the report names it rather than burying it in (1).
  3. SUPERSESSION HEAD -- on a chain head, no incoming edge may read as the head
     being superseded. The critic derived this case rather than observing it; the
     oracle observes it.

  A relation with no expectation on record is reported UNKNOWN_RELATION and fails:
  silence about a relation nobody wrote down is how this class starts.

USAGE
  python tools/l4_direction_oracle.py [--sample N] [--out PATH] [--db PATH]
                                      [--docs-root PATH]
  exit 0 = every sampled edge's sentence matches its recorded direction
  exit 1 = at least one direction defect
  exit 2 = operational error

OUTPUT
  ASCII only on stdout. JSON report at --out
  (default docs/probe-qualification/direction_oracle.json).

  Read-only throughout: the index is opened only through CorpusAdapter, the sole
  caller of RHACO_corpus_index.connect(); pages are rendered in-process through
  TestClient; no server is launched and nothing is written except the report.
  The live db sha256 is taken before and after and reported (criterion 6).

VERSION HISTORY
  v1.0  2026-09-05  First cut. Round 7 / CCX section 4 step (3); gate 7's
                    compensating control for BOUNDED_FAIL BF-1.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.append(REPO_ROOT)

# Written here by hand, deliberately NOT imported from explorer.models.
# CONSTRAINTS.md O8 gives the edge semantics; these are the sentences those
# semantics license when the edge is read from each end.
EXPECTED_SENTENCES = {
    # relation:      (read from the `from` end, read from the `to` end)
    "cites": ("cites", "cited by"),
    "supersedes": ("is superseded by", "supersedes"),
    "amends": ("amends", "amended by"),
    "campaign_child": ("has campaign child", "is campaign child of"),
}
DIRECTION_INDEX = {"outgoing": 0, "incoming": 1}


def db_sha(path: str) -> tuple[str, int]:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest(), os.path.getsize(path)


def expected_for(relation: str, direction: str):
    pair = EXPECTED_SENTENCES.get(relation)
    if pair is None:
        return None, None
    idx = DIRECTION_INDEX.get(direction)
    if idx is None:
        return None, None
    return pair[idx], pair[1 - idx]


def evaluate(client, card_refs: list[str]) -> dict:
    findings, checked, pages = [], 0, 0
    head_checks = []
    for ref in card_refs:
        resp = client.get("/api/lineage/" + ref)
        if resp.status_code != 200:
            findings.append({"card_ref": ref, "verdict": "PAGE_ERROR",
                             "detail": f"status {resp.status_code}"})
            continue
        pages += 1
        data = resp.json()
        centre = (data.get("center") or {}).get("doc_id")
        # The supersession chain is exposed as `chain`, a list of {card, is_head}.
        # An earlier draft of this oracle looked for a `chain_head` key that does
        # not exist, so check 3 silently never fired -- a second cannot-fail check
        # inside the instrument written to end cannot-fail checks. Derived from the
        # observed API shape now, and the empty-run guard below would catch it again.
        head_id = None
        for entry in data.get("chain") or []:
            if entry.get("is_head"):
                head_id = (entry.get("card") or {}).get("doc_id")
                break
        for direction in ("outgoing", "incoming"):
            for edge in data.get(direction) or []:
                checked += 1
                relation = edge.get("relation")
                sentence = edge.get("direction_label")
                want, converse = expected_for(relation, direction)
                if want is None:
                    findings.append({"card_ref": ref, "relation": relation,
                                     "direction": direction, "sentence": sentence,
                                     "verdict": "UNKNOWN_RELATION",
                                     "detail": "no expectation on record for this relation/direction"})
                    continue
                if sentence == want:
                    continue
                verdict = "CONVERSE" if sentence == converse else "MISMATCH"
                findings.append({
                    "card_ref": ref, "relation": relation, "direction": direction,
                    "from_id": edge.get("from_id"), "to_id": edge.get("to_id"),
                    "sentence": sentence, "expected": want, "verdict": verdict,
                    "detail": ("the sentence read from the other end -- the exact defect "
                               "critic round 1 recorded as gate 7 FAIL")
                    if verdict == "CONVERSE" else "sentence does not match either end",
                })
        # Check 3: a supersession head must never read as superseded.
        if head_id and centre and head_id == centre:
            bad = [e for e in (data.get("incoming") or [])
                   if e.get("relation") == "supersedes"
                   and e.get("direction_label") == EXPECTED_SENTENCES["supersedes"][0]]
            head_checks.append({"card_ref": ref, "is_chain_head": True,
                                "offending_incoming_edges": len(bad)})
            for e in bad:
                findings.append({
                    "card_ref": ref, "relation": "supersedes", "direction": "incoming",
                    "from_id": e.get("from_id"), "to_id": e.get("to_id"),
                    "sentence": e.get("direction_label"),
                    "expected": EXPECTED_SENTENCES["supersedes"][1],
                    "verdict": "HEAD_REPORTED_SUPERSEDED",
                    "detail": "the current head of the family is rendered as superseded by its own predecessor",
                })
    return {"pages_rendered": pages, "edges_checked": checked,
            "findings": findings, "head_checks": head_checks}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", default=r"C:\RHACO\index\corpus_index.db")
    ap.add_argument("--docs-root", default=r"C:\RHACO\docs")
    ap.add_argument("--sample", type=int, default=120)
    ap.add_argument("--out", default=os.path.join(REPO_ROOT, "docs", "probe-qualification",
                                                  "direction_oracle.json"))
    args = ap.parse_args(argv)

    try:
        from fastapi.testclient import TestClient

        from explorer.app import create_app
        from explorer.config import Settings
        from explorer.corpus_adapter.adapter import CorpusAdapter
    except Exception as exc:  # noqa: BLE001
        print(f"l4-direction-oracle: import error: {exc}")
        return 2

    before = db_sha(args.db)
    settings = Settings(db_path=args.db, docs_root=args.docs_root)
    adapter = CorpusAdapter(settings)

    # Sample cards that actually carry typed edges, newest first, through the
    # adapter's own documented queries -- never raw SQL from here.
    conn = adapter.connect()
    try:
        # Two strata, deliberately. The recency stratum alone returned ZERO
        # supersession chain heads, which would have left check 3 -- the critic's
        # decisive derived case -- never exercised. So the sample explicitly unions
        # in the superseding side of every `supersedes` edge, where the heads live.
        rows = conn.execute(
            "SELECT DISTINCT c.yaml_path FROM cards c "
            "JOIN edges e ON e.from_id = c.doc_id OR e.to_id = c.doc_id "
            "ORDER BY c.date DESC, c.yaml_path LIMIT ?",
            (args.sample,),
        ).fetchall()
        head_rows = conn.execute(
            "SELECT DISTINCT c.yaml_path FROM cards c "
            "JOIN edges e ON e.to_id = c.doc_id "
            "WHERE e.relation = 'supersedes' AND e.resolved = 1 "
            "ORDER BY c.date DESC, c.yaml_path LIMIT ?",
            (args.sample,),
        ).fetchall()
        rows = list(rows) + [r for r in head_rows if r not in rows]
    finally:
        conn.close()
    # `cards.yaml_path` is absolute on disk; the URL key is card_ref, the path
    # RELATIVE to the docs root (ARCHITECTURE.md section 3). Converting here rather
    # than assuming they are the same is what the first run of this oracle got wrong.
    docs_root_norm = os.path.normcase(os.path.abspath(args.docs_root))
    card_refs = []
    for (yaml_path,) in rows:
        absolute = os.path.abspath(yaml_path)
        if os.path.normcase(absolute).startswith(docs_root_norm):
            card_refs.append(os.path.relpath(absolute, args.docs_root).replace(os.sep, "/"))
        else:
            card_refs.append(yaml_path.replace("\\", "/"))

    client = TestClient(create_app(settings))
    result = evaluate(client, card_refs)
    after = db_sha(args.db)

    # Every finding is a defect, PAGE_ERROR included: a lineage page that will not
    # render is a failure, not an excuse to skip the card.
    defects = list(result["findings"])
    by_verdict = {}
    for f in result["findings"]:
        by_verdict[f["verdict"]] = by_verdict.get(f["verdict"], 0) + 1

    # An oracle that checked nothing must never report PASS. The first run of this
    # file did exactly that -- 120 cards, every page errored, zero edges compared,
    # verdict PASS -- which is the "check that cannot fail" pathology this oracle
    # exists to catch, reproduced inside the oracle. The floor is the fix.
    empty = []
    if result["pages_rendered"] == 0:
        empty.append("no lineage page rendered")
    if result["edges_checked"] == 0:
        empty.append("no edge compared")
    if not result["head_checks"]:
        empty.append("no supersession chain head exercised -- check 3 is the critic's "
                     "decisive derived case, and an oracle that never reaches it is not "
                     "evidence for gate 7")

    report = {
        "tool": "l4_direction_oracle v1.0",
        "empty_run_guard": empty or "not triggered",
        "db_path": args.db,
        "docs_root": args.docs_root,
        "sampled_cards": len(card_refs),
        "expectation_source": ("hand-written in this file from CONSTRAINTS.md O8; deliberately NOT "
                               "imported from explorer.models, so the oracle can disagree with the product"),
        "expected_sentences": {k: {"outgoing": v[0], "incoming": v[1]}
                               for k, v in EXPECTED_SENTENCES.items()},
        "pages_rendered": result["pages_rendered"],
        "edges_checked": result["edges_checked"],
        "chain_heads_checked": len(result["head_checks"]),
        "counts_by_verdict": by_verdict,
        "findings": result["findings"],
        "db_unchanged": before == after,
        "db_sha256_before": before[0],
        "db_sha256_after": after[0],
        "db_bytes": before[1],
        "verdict": "PASS" if not defects and before == after and not empty else "FAIL",
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=True)
        fh.write("\n")

    for f in result["findings"][:40]:
        line = (f"DEFECT: {f.get('card_ref')} [{f.get('relation')}/{f.get('direction')}] "
                f"rendered={f.get('sentence')!r} expected={f.get('expected')!r} "
                f"-- {f.get('verdict')}")
        print(line.encode("ascii", "replace").decode("ascii"))
    print(f"l4-direction-oracle: cards={len(card_refs)} pages={result['pages_rendered']} "
          f"edges={result['edges_checked']} heads={len(result['head_checks'])} "
          f"defects={len(defects)} db_unchanged={before == after} verdict={report['verdict']}")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
