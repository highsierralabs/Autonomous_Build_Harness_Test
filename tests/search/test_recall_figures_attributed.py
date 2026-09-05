"""No bare retrieval figure on the rendered search page (R08 dispatch item 1;
critic round 1 ranked issue 2; CONSTRAINTS.md S8: no hidden epistemic uplift).

The critic found one bare figure (`Recall@10 0.700 aggregate on Gold v1.1`,
service.py:93 at review time) and the dispatch names three more of the same
shape (lexical 0.200, graph 0.575, and the 0.575-vs-0.700 pair inside
HYBRID_RERANK_NOTE) that a plain grep for `Recall@10` on
`explorer/search/service.py` turns up alongside it -- see this round's report,
Evidence, for that grep's output. Every one of the four is a RHACO-ANL-20260712-001
figure presented with no date and no source, as though it were the mode's
present standing.

`test_no_bare_recall_figure_on_search_page` is written to catch a NEW bare
figure added later, not just the four that existed at dispatch: it scans the
whole rendered page for the `Recall@10 <number>` shape and requires an
explicit ISO date within a short window of each occurrence -- an ANL id alone
does not satisfy it, because the critic's own finding already had the ANL id
named without a date attached in one place (HYBRID_RERANK_NOTE). This is the
one test in this file that would have caught the critic's finding directly:
it FAILS against the code as of the critic's review (and as of this round's
dispatch) and PASSES after this round's fix.
"""
from __future__ import annotations

import re

# A "Recall@10" figure: the literal marker plus a decimal number nearby ("Recall@10
# 0.700" and "Recall@10 at 0.675" both match).
_RECALL_FIGURE_RE = re.compile(r"Recall@10\b[^0-9]{0,20}\d\.\d+")
# The "dated" half of S8's attribution requirement. Deliberately an explicit
# ISO date, not just the RHACO-ANL-YYYYMMDD-NNN id pattern -- the pre-fix page
# already named the ANL id next to one of the four figures with no date
# attached, and that was still a bare figure under this round's task.
_ISO_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
_WINDOW = 140


def _bare_recall_figures(body: str) -> list[str]:
    bad = []
    for m in _RECALL_FIGURE_RE.finditer(body):
        lo = max(0, m.start() - _WINDOW)
        hi = min(len(body), m.end() + _WINDOW)
        window = body[lo:hi]
        if not _ISO_DATE_RE.search(window):
            bad.append(body[m.start() : m.start() + 80])
    return bad


def test_no_bare_recall_figure_on_search_page(fixture_client):
    # Mode standing renders even for an empty query (task B5 deliverable 1) --
    # every Recall@10 figure this page can show is reachable with no query at all.
    body = fixture_client.get("/search").text
    bad = _bare_recall_figures(body)
    assert not bad, f"Recall@10 figure(s) with no dated attribution nearby: {bad}"


def test_recall_figures_are_attributed_to_the_source_anl_and_date(fixture_client):
    """Belt-and-suspenders on the specific fix (not just the generic scan above):
    every Gold v1.1 figure on the page names the RHACO ANL of record and its
    evaluation date, and the hybrid figure additionally carries this build's
    own current measurement rather than standing alone."""
    body = fixture_client.get("/search").text
    assert body.count("RHACO-ANL-20260712-001") >= 4
    assert body.count("evaluated 2026-07-12") >= 4
    assert "This build ran its own oracle" in body
    assert "0.675" in body
    assert "SCOPE.md" in body


def test_the_pages_own_measurement_date_matches_the_artifact_it_describes(fixture_client):
    """The date the page gives for THIS BUILD's own oracle run must be the UTC date
    of the run it describes -- critic round 2, ranked issue 2, and a P-13(a) control.

    The page first said "on 2026-09-04": a local-Pacific rendering of a UTC instant,
    matching no oracle run's UTC date. SCOPE.md row 16 was corrected off exactly that
    ambiguity in the same round, and the product page was left carrying it, so the
    surface and the scope register disagreed about when this build measured its own
    retrieval figure -- in a tool whose whole subject is provenance.

    A date on a provenance surface is a claim about an artifact. This test is the
    control that makes it one: it reads gold_v1_1_compat.json and fails if the page
    and the artifact ever disagree again, including after a future oracle re-run that
    moves the date and leaves the page behind.
    """
    import datetime
    import json
    import os

    from explorer.search import service

    repo = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    artifact = os.path.join(repo, "docs", "probe-qualification", "gold_v1_1_compat.json")
    with open(artifact, encoding="utf-8") as fh:
        report = json.load(fh)

    started = report.get("started_utc")
    assert started, "gold_v1_1_compat.json carries no started_utc to derive a date from"
    observed = datetime.datetime.fromisoformat(started).astimezone(datetime.UTC)
    artifact_date = observed.date().isoformat()

    assert service.GOLD_V1_1_CURRENT_RUN_UTC_DATE == artifact_date, (
        f"the search page dates this build's own oracle measurement "
        f"{service.GOLD_V1_1_CURRENT_RUN_UTC_DATE}, but gold_v1_1_compat.json's "
        f"started_utc is {started} -> {artifact_date} UTC. The page and the artifact "
        "it describes disagree; update GOLD_V1_1_CURRENT_RUN_UTC_DATE from the artifact."
    )

    body = fixture_client.get("/search").text
    assert f"on {artifact_date} UTC" in body, (
        "the rendered page does not carry the artifact-derived UTC date; the constant "
        "and the rendering have drifted apart"
    )
