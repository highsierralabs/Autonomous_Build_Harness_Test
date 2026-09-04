"""L4 corpus oracle: Gold v1.1 compatibility check (CONSTRAINTS.md O16; ARCHITECTURE.md section 6).

PURPOSE
  For every row of the frozen Gold v1.1 set, obtain the top-10 doc ids from
  (a) the adapter's hybrid path and (b) the module's direct search_hybrid on
  the same live index, assert the two lists are identical (the adapter did not
  degrade the module), and compute Recall@10 with the set's own hit rule
  (any-target-in-top-10; a row with `resolve: supersession-head` also accepts
  the head of the target's supersession chain, obtained through the adapter).

  The 0.700 aggregate threshold (DISPATCH_PARAMETERS.md item E) applies to the
  ADAPTER figure. A module-direct figure below 0.700 on today's corpus is a
  substrate observation for SCOPE.md, never silently accepted or hidden. Gold
  v1.2 is profiled only when --gold points at it (never gated).

USAGE
  python tools/l4_gold_oracle.py [--gold PATH] [--top-k 10] [--out PATH] [--threshold 0.700]
  exit 0 = adapter recall >= threshold and all id lists equal; 1 = a gate failed;
  2 = operational error (missing db, adapter not built, vector channel required but unavailable is NOT an error -- it is recorded).

OUTPUT
  ASCII only. Per-row line: id, stratum, hit, adapter==module, mode. Summary block.
  JSON report at --out (default docs/probe-qualification/gold_v1_1_compat.json).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE not in sys.path:
    sys.path.insert(0, WORKSPACE)

DEFAULT_GOLD = r"C:\RHACO\working\eval\gold_queries.yaml"


def _load_rows(path: str) -> tuple[dict, list[dict]]:
    import yaml  # PyYAML (item-11 set)

    with open(path, encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    rows = doc.get("queries") or doc.get("rows") or []
    if not rows and isinstance(doc, list):
        rows = doc
    meta = {k: v for k, v in doc.items() if k not in ("queries", "rows")} if isinstance(doc, dict) else {}
    return meta, rows


def _targets(row: dict) -> list[str]:
    t = row.get("targets") or row.get("target") or []
    if isinstance(t, str):
        t = [t]
    out = []
    for x in t:
        # a target may be written "RHACO-SOP-... (head = v2)" -- keep the id token only
        out.append(str(x).split(" ")[0].strip())
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Gold v1.1 compatibility oracle (adapter vs module, Recall@10)")
    ap.add_argument("--gold", default=DEFAULT_GOLD)
    ap.add_argument("--top-k", type=int, default=10)
    ap.add_argument("--threshold", type=float, default=0.700)
    ap.add_argument("--out", default=os.path.join(WORKSPACE, "docs", "probe-qualification", "gold_v1_1_compat.json"))
    ap.add_argument("--gate", action="store_true", help="apply the threshold gate (default when the gold file is the v1.1 default)")
    args = ap.parse_args(argv)
    gate = args.gate or os.path.normcase(os.path.abspath(args.gold)) == os.path.normcase(os.path.abspath(DEFAULT_GOLD))

    try:
        from explorer.config import Settings
        from explorer.corpus_adapter import CorpusAdapter
    except ModuleNotFoundError as exc:
        print(f"l4-gold-oracle: OPERATIONAL adapter not importable: {exc}")
        return 2
    settings = Settings.from_env()
    try:
        adapter = CorpusAdapter(settings)
    except Exception as exc:  # noqa: BLE001 -- operational failure is reported, not raised
        print(f"l4-gold-oracle: OPERATIONAL adapter construction failed: {type(exc).__name__}: {exc}")
        return 2

    import RHACO_corpus_index as ci  # path entries appended by the adapter package

    meta, rows = _load_rows(args.gold)
    vec = adapter.vector_availability()
    started = dt.datetime.now(dt.UTC)
    results = []
    hits_adapter = hits_module = equal = 0
    per_stratum: dict[str, list[int]] = {}
    for row in rows:
        rid = row.get("id")
        stratum = str(row.get("stratum", "?"))
        q = str(row.get("query", ""))
        targets = _targets(row)
        resolve = row.get("resolve")
        accepted = set(targets)
        if resolve == "supersession-head":
            for t in targets:
                try:
                    chain = adapter.supersession_chain(t)
                    for c in chain:
                        accepted.add(c.doc_id)
                except Exception as exc:  # noqa: BLE001 -- recorded per row
                    row_note = f"chain lookup failed: {type(exc).__name__}"
                    results.append({"id": rid, "note": row_note})
        try:
            ad = adapter.search_hybrid(q, top_k=args.top_k)
            adapter_ids = [it.doc_id for it in ad.items]
            mode = ad.mode_effective
        except Exception as exc:  # noqa: BLE001 -- recorded per row
            adapter_ids, mode = [], f"error: {type(exc).__name__}"
        try:
            module_ids = list(ci.search_hybrid(q, top_k=args.top_k, db_path=adapter.db_path))
        except Exception as exc:  # noqa: BLE001 -- recorded per row
            module_ids = [f"error: {type(exc).__name__}"]
        hit_a = any(x in accepted for x in adapter_ids)
        hit_m = any(x in accepted for x in module_ids)
        same = adapter_ids == module_ids
        hits_adapter += hit_a
        hits_module += hit_m
        equal += same
        per_stratum.setdefault(stratum, [0, 0])
        per_stratum[stratum][0] += hit_a
        per_stratum[stratum][1] += 1
        results.append({"id": rid, "stratum": stratum, "query": q, "targets": targets, "resolve": resolve,
                        "row_mode": row.get("mode"),  # S4 rows marked `mode: graph` are still run through hybrid: the standing 0.700 is the hybrid config over all 40 rows
                        "accepted": sorted(accepted), "adapter_ids": adapter_ids, "module_ids": module_ids,
                        "hit_adapter": hit_a, "hit_module": hit_m, "lists_equal": same, "mode_effective": mode})
        print(f"row {rid!s:>3} {stratum:<3} hit={'Y' if hit_a else 'n'} equal={'Y' if same else 'N'} mode={mode}")
    n = len(rows) or 1
    recall_a = hits_adapter / n
    recall_m = hits_module / n
    summary = {
        "gold_path": args.gold, "gold_meta": meta, "rows": len(rows), "top_k": args.top_k,
        "vector_availability": {"available": vec.available, "reason": vec.reason},
        "recall_at_10_adapter": round(recall_a, 4), "recall_at_10_module_direct": round(recall_m, 4),
        "lists_equal": equal, "threshold": args.threshold if gate else None,
        "per_stratum_adapter": {k: {"hits": v[0], "rows": v[1], "recall": round(v[0] / v[1], 4)} for k, v in sorted(per_stratum.items())},
        "started_utc": started.isoformat(timespec="seconds"), "finished_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "db_path": adapter.db_path, "results": results,
    }
    verdict_lists = equal == len(rows)
    verdict_gate = (recall_a >= args.threshold) if gate else True
    summary["verdict"] = {"lists_equal_all": verdict_lists, "adapter_recall_gate": verdict_gate,
                          "overall": "PASS" if (verdict_lists and verdict_gate) else "FAIL"}
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=True)
    print(f"l4-gold-oracle: rows={len(rows)} adapter_recall@{args.top_k}={recall_a:.3f} module_recall={recall_m:.3f} "
          f"lists_equal={equal}/{len(rows)} vector={'available' if vec.available else 'unavailable:' + vec.reason} "
          f"gate={'on' if gate else 'off'} verdict={summary['verdict']['overall']} out={os.path.relpath(args.out, WORKSPACE)}")
    return 0 if summary["verdict"]["overall"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
