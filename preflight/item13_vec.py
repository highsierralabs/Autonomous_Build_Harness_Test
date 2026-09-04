"""HND-20260903-001 section 0 item 13 -- vector channel state and the W7 mechanism.

Read-only against the live index through the module's own connect().
Usage:
    item13_vec.py part1    # parent-environment state: vec availability, search_hybrid
    item13_vec.py part2    # run in a child with RHACO_CORPUS_DISABLE_VEC=1: typed degradation
Never writes; never calls reindex_*; never opens the db outside ci.connect().
"""
import os
import sys
import time

sys.path.insert(0, r"C:\RHACO\rhaco")
sys.path.insert(1, r"C:\RHACO\tools")
import RHACO_corpus_index as ci  # noqa: E402

QUERY = "firmware transfer function"
part = sys.argv[1] if len(sys.argv) > 1 else "part1"
print("part:", part, "| env RHACO_CORPUS_DISABLE_VEC =", repr(os.environ.get(ci.VEC_DISABLE_ENV)))

conn = ci.connect()
print("sqlite-vec loaded on connect:", ci._load_sqlite_vec(conn))
try:
    ci._require_vec(conn)
    print("_require_vec: available")
except ci.VecUnavailable as e:
    print("_require_vec raised typed VecUnavailable:", e)

if part == "part1":
    for tag in ci.MODEL_TAGS:
        tbl = ci._vec_table(tag)
        n = conn.execute("SELECT count(1) FROM sqlite_master WHERE name=?", (tbl,)).fetchone()[0]
        if n:
            cnt = conn.execute("SELECT count(1) FROM %s" % tbl).fetchone()[0]
            print("vec table", tbl, "present, rows =", cnt)
        else:
            print("vec table", tbl, "absent")
    keys = ("index_schema_version", "librarian_version", "current_nc_version",
            "last_full_reindex_utc", "corpus_card_count", "corpus_cards_sha",
            "fts_docs_count", "edges_count", "id_aliases_count")
    print("index_meta:", {k: ci.get_meta(conn, k) for k in keys})
    for t in ("cards", "fts_docs", "edges", "id_aliases"):
        print("count", t, "=", conn.execute("SELECT count(1) FROM %s" % t).fetchone()[0])
    print("edges by relation:", conn.execute(
        "SELECT relation, resolved, count(1) FROM edges GROUP BY relation, resolved ORDER BY relation, resolved").fetchall())
conn.close()

t0 = time.perf_counter()
try:
    v = ci._vec_doc_ranking(QUERY, ci.CPU_FLOOR_TAG, ci.DEFAULT_DB)
    print("VEC CHANNEL: AVAILABLE (%.2fs); top-5 by best-chunk cosine:" % (time.perf_counter() - t0), v[:5])
except ci.VecUnavailable as e:
    print("VEC CHANNEL: VecUnavailable (%.2fs):" % (time.perf_counter() - t0), e)

t0 = time.perf_counter()
r = ci.search_hybrid(QUERY, top_k=5)
print("search_hybrid(%r, top_k=5) (%.2fs) ->" % (QUERY, time.perf_counter() - t0), r)
t0 = time.perf_counter()
f = ci._fts_doc_ranking(QUERY, ci.DEFAULT_DB)
print("FTS-only doc ranking (%.2fs) top-5 ->" % (time.perf_counter() - t0), f[:5])
print("search_hybrid result equals FTS-only top-5:", r == f[:5])
print("ITEM13_%s_DONE" % part.upper())
