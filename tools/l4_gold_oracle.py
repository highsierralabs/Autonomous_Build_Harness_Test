"""L4 corpus oracle: Gold v1.1 compatibility check (CONSTRAINTS.md O16; ARCHITECTURE.md section 6).

PURPOSE
  For every row of the frozen Gold v1.1 set, obtain the top-10 doc ids from
  (a) the adapter's hybrid path and (b) the module's direct search_hybrid on
  the same live index, assert the two lists are identical (the adapter did not
  degrade the module), and compute Recall@10 with the set's own hit rule:
  any-target-in-top-10, where a target written as a reference-document FAMILY
  under `resolve: supersession-head` (RHACO-ANL-20260711-001 rows 16, 27, 35:
  "family <name> [resolve: supersession-head]", "live-head semantics") is
  resolved to the family's LIVE HEAD -- the version card that no `supersedes`
  edge leaves, with the max-version fallback RHACO-ANL-20260712-002 describes
  when family edges are absent. Explicit versioned or canonical targets stay
  literal.

  Two verdicts are reported separately: adapter_matches_module (the compatibility
  claim the build owns) and threshold_met (the 0.700 aggregate of
  DISPATCH_PARAMETERS.md item E). A module-direct figure below 0.700 on today's
  corpus is a substrate observation for SCOPE.md, never silently accepted or
  hidden (PROMPT.md section 8 item 9). Gold v1.2 is profiled only when --gold
  points at it (never gated).

USAGE
  python tools/l4_gold_oracle.py [--gold PATH] [--top-k 10] [--out PATH] [--threshold 0.700]
  exit 0 = adapter matches module on every row AND threshold met;
  exit 3 = adapter matches module but the threshold is not met (SCOPE.md row required);
  exit 1 = adapter differs from the module on some row; exit 2 = operational error.

OUTPUT
  ASCII only. Per-row line: id, stratum, hit, adapter==module, mode, target resolution.
  JSON report at --out (default docs/probe-qualification/gold_v1_1_compat.json).
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

DEFAULT_GOLD = r"C:\RHACO\working\eval\gold_queries.yaml"
_VERSION_RE = re.compile(r"_v(\d+(?:_\d+)*)$")
_CANONICAL_RE = re.compile(r"^RHACO-[A-Z]+-\d{8}-\d+$")


def _load_rows(path: str) -> tuple[dict, list[dict]]:
    import yaml  # PyYAML (item-11 set)

    with open(path, encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    rows = doc.get("queries") or doc.get("rows") or []
    meta = {k: v for k, v in doc.items() if k not in ("queries", "rows")}
    return meta, rows


def _targets(row: dict) -> list[str]:
    t = row.get("targets") or row.get("target") or []
    if isinstance(t, str):
        t = [t]
    return [str(x).split(" ")[0].strip() for x in t]


def _version_key(doc_id: str) -> tuple:
    m = _VERSION_RE.search(doc_id)
    return tuple(int(p) for p in m.group(1).split("_")) if m else ()


def _is_family_name(target: str) -> bool:
    return not _CANONICAL_RE.match(target) and not _VERSION_RE.search(target)


def resolve_family_head(adapter, family: str) -> tuple[str | None, str]:
    """Live head of a reference-document family: the version card no `supersedes`
    edge leaves; max-version fallback when no edges exist. Returns (head, how)."""
    from explorer.models import CatalogFilters

    docs_root = adapter.docs_root
    candidates: dict[str, object] = {}
    for sub in ("reference", "reports", "handoffs", ""):
        prefix = os.path.join(docs_root, sub, family + "_v") if sub else os.path.join(docs_root, family + "_v")
        try:
            page = adapter.catalog(CatalogFilters(path_prefix=prefix), "doc_id", 1, 500)
        except Exception:  # noqa: BLE001 -- a failed lookup is reported as unresolved
            continue
        for c in page.rows:
            if c.doc_id.startswith(family + "_v"):
                candidates[c.doc_id] = c
    if not candidates:
        return None, "unresolved (no version cards found)"
    heads = []
    for doc_id, card in candidates.items():
        try:
            es = adapter.edges_for(card)
            if not any(e.relation == "supersedes" for e in es.outgoing):
                heads.append(doc_id)
        except Exception:  # noqa: BLE001
            heads.append(doc_id)
    if len(heads) == 1:
        return heads[0], "supersedes-edge terminal"
    best = max(candidates, key=_version_key)
    return best, f"max-version fallback (no unique edge terminal among {len(candidates)} versions)"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Gold v1.1 compatibility oracle (adapter vs module, Recall@10)")
    ap.add_argument("--gold", default=DEFAULT_GOLD)
    ap.add_argument("--top-k", type=int, default=10)
    ap.add_argument("--threshold", type=float, default=0.700)
    ap.add_argument("--out", default=os.path.join(WORKSPACE, "docs", "probe-qualification", "gold_v1_1_compat.json"))
    ap.add_argument("--gate", action="store_true", help="apply the threshold gate (default when --gold is the v1.1 default)")
    args = ap.parse_args(argv)
    gate = args.gate or os.path.normcase(os.path.abspath(args.gold)) == os.path.normcase(os.path.abspath(DEFAULT_GOLD))

    try:
        from explorer.config import Settings
        from explorer.corpus_adapter import CorpusAdapter
    except ModuleNotFoundError as exc:
        print(f"l4-gold-oracle: OPERATIONAL adapter not importable: {exc}")
        return 2
    try:
        adapter = CorpusAdapter(Settings.from_env())
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
        accepted: list[str] = []
        resolution: list[str] = []
        for t in targets:
            if resolve == "supersession-head" and _is_family_name(t):
                head, how = resolve_family_head(adapter, t)
                if head:
                    accepted.append(head)
                    resolution.append(f"{t} -> {head} ({how})")
                else:
                    accepted.append(t)
                    resolution.append(f"{t} -> {how}")
            else:
                accepted.append(t)
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
        acc = set(accepted)
        hit_a = any(x in acc for x in adapter_ids)
        hit_m = any(x in acc for x in module_ids)
        same = adapter_ids == module_ids
        hits_adapter += hit_a
        hits_module += hit_m
        equal += same
        per_stratum.setdefault(stratum, [0, 0])
        per_stratum[stratum][0] += hit_a
        per_stratum[stratum][1] += 1
        results.append({"id": rid, "stratum": stratum, "query": q, "targets": targets, "resolve": resolve,
                        "row_mode": row.get("mode"), "target_resolution": resolution, "accepted": accepted,
                        "adapter_ids": adapter_ids, "module_ids": module_ids,
                        "hit_adapter": hit_a, "hit_module": hit_m, "lists_equal": same, "mode_effective": mode})
        res_note = ("; ".join(resolution)) if resolution else ""
        print(f"row {rid!s:>3} {stratum:<3} hit={'Y' if hit_a else 'n'} equal={'Y' if same else 'N'} mode={mode} {res_note}".rstrip())
    n = len(rows) or 1
    recall_a = hits_adapter / n
    recall_m = hits_module / n
    adapter_matches = equal == len(rows)
    threshold_met = (recall_a >= args.threshold) if gate else True
    overall = "PASS" if (adapter_matches and threshold_met) else ("SCOPE" if adapter_matches else "FAIL")
    summary = {
        "gold_path": args.gold, "gold_meta": meta, "rows": len(rows), "top_k": args.top_k,
        "hit_rule": "any-target-in-top-10; family targets under resolve: supersession-head resolved to the live head (supersedes-edge terminal, max-version fallback)",
        "vector_availability": {"available": vec.available, "reason": vec.reason},
        "recall_at_10_adapter": round(recall_a, 4), "recall_at_10_module_direct": round(recall_m, 4),
        "hits_adapter": hits_adapter, "hits_module": hits_module, "lists_equal": equal,
        "threshold": args.threshold if gate else None,
        "per_stratum_adapter": {k: {"hits": v[0], "rows": v[1], "recall": round(v[0] / v[1], 4)} for k, v in sorted(per_stratum.items())},
        "started_utc": started.isoformat(timespec="seconds"), "finished_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "db_path": adapter.db_path, "index_meta_corpus_cards_sha": adapter.index_meta().meta.get("corpus_cards_sha"),
        "verdict": {"adapter_matches_module": adapter_matches, "threshold_met": threshold_met, "overall": overall},
        "results": results,
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=True)
    print(f"l4-gold-oracle: rows={len(rows)} adapter_recall@{args.top_k}={recall_a:.3f} ({hits_adapter}/{len(rows)}) "
          f"module_recall={recall_m:.3f} lists_equal={equal}/{len(rows)} vector={'available' if vec.available else 'unavailable:' + vec.reason} "
          f"gate={'on' if gate else 'off'} adapter_matches_module={adapter_matches} threshold_met={threshold_met} "
          f"verdict={overall} out={os.path.relpath(args.out, WORKSPACE)}")
    return 0 if overall == "PASS" else (3 if overall == "SCOPE" else 1)


if __name__ == "__main__":
    sys.exit(main())
