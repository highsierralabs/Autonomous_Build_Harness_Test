"""RHACO Corpus Explorer -- production-path probe (ARCHITECTURE.md section 4.8;
CONSTRAINTS.md O12; task RHACO-HND-20260903-001 strand B2).

PURPOSE
  The ONLY sanctioned launcher of the explorer server (CONSTRAINTS.md O12).
  Spawns `<venv python> -m uvicorn explorer.app:create_app --factory` as a
  foreground child of this process, waits on GET /healthz, drives it with
  Playwright (sync API, Chromium headless, 1280x900) through a registry of
  named presets, records DOM + /api observations, console errors, failed
  requests, screenshots, and timings per preset, then tears the child down in
  a finally block. Never backgrounds, never detaches, never sleep-polls
  outside the bounded readiness wait.

  This round (C1, correction round) repairs the round-1 verdict predicate --
  round 1 set `ok = error is None`, so a page preset passed even with a 404,
  console errors, and failed requests all recorded (docs/probe-qualification/
  runs/20260904T033047Z/diagnostics.json). `evaluate_page()` is now the one
  observed-fault predicate for every page-kind preset: navigation/extraction
  errors, an unexpected HTTP status, any console error (including a mirrored
  `pageerror`), any failed request, or a failed declarative data-* assertion
  all FAIL the preset; a FAIL whose console/page error text matches a known
  fault marker also sets `fault_detected` and `fault_class` (this round: KB5
  / console_error only -- see FAULT_CLASS_TABLE). `diagnostics` is upgraded
  from a 404-tolerant stub to a real assertion (HTTP 200, data-mode/
  data-vector/title present) now that the diagnostics module is merged.
  Every run also derives an AC-3 `qualification_state` (FRAMEWORK_SMOKE_PASS /
  QUALIFICATION_PASS / PRODUCT_EVIDENCE_PASS / FAIL / INCOMPLETE) recorded in
  run_summary.json, and a QUALIFICATION_PASS run appends its fault class to
  the committed `qualification_ledger.json` (the only file this tool writes
  outside its own --out directory).

  This round (B7, wave-2 round 3 of 4) replaces the W1-W10 / KG / KB1-KB5
  `not_implemented_yet` stubs with real "workflow"-kind runners (a Playwright
  `Session` -- one browser context reused across several logical navigation
  steps, tagging every console error / page error / failed request / request
  with the step active when it was captured) driving the merged catalog,
  search, reader, and diagnostics surfaces. KG and KB1/KB2/KB4/KB5 run against
  the fixture only; W1/W2/W3/W4/W7/W9/W10 run against the live index (never
  opened directly -- only through the server this file launches). W5, W6, and
  KB3 stay `not_implemented_yet` (lineage lands in wave 3 / Q3), so a run
  selecting one of those three is still INCOMPLETE.

USAGE
  <venv python> tools/probe_corpus_explorer.py --db <path> --docs-root <path>
      [--port 8765] [--preset NAME|NAME1,NAME2,...|all] [--out DIR] [--fault NAME]
      [--disable-vec] [--timeout 30] [--ledger PATH]

  --db and --docs-root are REQUIRED (no default) so this tool can never launch
  the explorer against the live corpus_index.db by omission -- every run names
  its database explicitly. --preset defaults to "all" (every registry entry);
  a comma-separated list (task B10, round 4) selects exactly those presets in
  one run, e.g. "KG,KB1,KB2,KB3,KB4,KB5" for the fixture FINAL suite -- an
  unknown name in the list is a hard error (exit 2), same as a single unknown
  name. --out defaults to docs/probe-qualification/runs/<utc stamp>. --ledger
  defaults to <workspace root>/docs/probe-qualification/qualification_ledger.json,
  resolved from this file's own location (so a worktree run writes the
  worktree's ledger, never another checkout's).

OUTPUT
  <out>/<preset>.json (+ <out>/<preset>.png for page-kind presets),
  <out>/run_summary.json, <out>/server.log (the child's stdout/stderr), and
  (only on a QUALIFICATION_PASS) an idempotent append to the ledger at
  --ledger. Exit 0 iff qualification_state is FRAMEWORK_SMOKE_PASS,
  QUALIFICATION_PASS, or PRODUCT_EVIDENCE_PASS; 1 for FAIL; 3 for INCOMPLETE.
  ASCII-only stdout (PYTHONIOENCODING=utf-8 set for the child too, per O19);
  qualification_state is also printed on stdout.

VERSION HISTORY
  v1.0  2026-09-04  Initial build (RHACO-HND-20260903-001 strand B2, round 1).
  v1.1  2026-09-04  Correction round (strand C1, round 2): observed-fault
                     predicate (evaluate_page/Verdict) replacing the round-1
                     `ok = error is None` bug; page-error (pageerror) capture,
                     mirrored into console_errors; the AC-3 qualification-state
                     vocabulary and the qualification ledger; diagnostics
                     preset upgraded from a 404-tolerant stub to a real
                     HTTP-200 + data-mode/data-vector/title assertion.
  v1.2  2026-09-04/05  Wave-2 runners (strand B7, round 3 of 4): the `Session`
                     multi-step Playwright driver; pure fault-attribution
                     predicates `_kb1_verdict`/`_kb2_verdict`/`_kb4_verdict`/
                     `_w10_localhost_check` (unit-tested without a server or
                     browser); real `"workflow"`-kind runners for KG, KB1,
                     KB2, KB4, KB5 (fixture) and W1, W2, W3, W4, W7, W8, W9,
                     W10 (production, except W8 which drives its own
                     dedicated temp-fixture server); `_touched_presets`
                     generalizes qualification-run fault attribution beyond
                     the C1 "every page-kind preset" rule to also match a
                     selected preset's own `PresetSpec.fault`; Q1 (search)
                     and Q2 (reader) qualification evidence against the
                     fixture, and PRODUCT_EVIDENCE_PASS / FRAMEWORK_SMOKE_PASS
                     evidence against the live index. W5, W6, KB3 remain
                     `not_implemented_yet` (lineage, wave 3 / Q3).
  v1.3  2026-09-05  Q3 + FINAL suite (strand S6-B10, round 4 of 4 -- the
                     LAST probe round). Real `kind="workflow"` runners for
                     `KB3` (`_kb3_verdict`, fed by the runner's own DOM +
                     `/api/lineage` observations, cross-checking the
                     `.edge-list` row against the graph `<line>` against the
                     API, against the frozen fixture fact), `W5` (reasoning
                     lineage: typed directional edges, `direction_label` vs
                     `explorer.models.RELATION_LABELS`, a chronological
                     reasoning trail, page/API edge-set parity, and an
                     independent read of two production `.card.yaml` files
                     confirming the rendered relation is actually declared
                     on disk), and `W6` (supersession chain + banner, the
                     historical artifact still readable through the reader,
                     an amendment's outgoing `amends` edge, and the parent's
                     incoming `amends` edge recorded against SCOPE.md row 17
                     -- present/typed/directional/resolved, never failed on
                     the disclosed missing click-through). `KG` gains the
                     Q3 typed-edge-direction case (CMP campaign_child x2,
                     amendment's outgoing `amends`, reference `supersedes` +
                     chain + banner, HND's unresolved `cites`). No preset in
                     `PRESET_REGISTRY` is `not_implemented_yet` after this
                     round. `--preset` accepts a comma-separated list (the
                     fixture FINAL run selects `KG,KB1,KB2,KB3,KB4,KB5` in
                     one invocation). `Session` gains `attr_dicts` (several
                     attributes -- or `"$text"` for `textContent` -- off the
                     same matched elements at once, in DOM order), used by
                     every Q3 runner in place of repeated single-attribute
                     `attr_all` calls.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

# --- make `explorer` importable regardless of how this file is invoked -----
_WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, _WORKSPACE_ROOT)

from explorer.faults import FAULTS, is_under_rhaco_tree  # noqa: E402
from explorer.models import COMPONENT_RANK_NOT_EXPOSED, RELATION_LABELS  # noqa: E402

VIEWPORT = {"width": 1280, "height": 900}
DEFAULT_TIMEOUT_S = 30.0
DEFAULT_PORT = 8765
READY_POLL_S = 0.5
NAV_TIMEOUT_MS = 15000


@dataclass(frozen=True)
class PresetSpec:
    name: str
    kind: str            # "json_endpoint" | "page" | "not_implemented"
    label: str
    path: str | None = None
    fault: str | None = None
    expected_status: int | None = None       # task C1 item 1 rule (b); no preset declares one this round
    data_mode_in: set[str] | None = None     # task C1 item 1 rule (e)
    data_vector_in: set[str] | None = None   # task C1 item 1 rule (e)
    require_title: bool = False              # task C1 item 1 rule (e)
    required_classes: tuple[str, ...] = ()   # AC-3 (task C1 item 2): KB classes this preset's
                                              # PRODUCT_EVIDENCE_PASS requires the ledger to cover


def _w(n: int, label: str, required_classes: tuple[str, ...] = (), kind: str = "not_implemented") -> PresetSpec:
    return PresetSpec(name=f"W{n}", kind=kind, label=label, required_classes=required_classes)


def _kb(n: int, fault: str, kind: str = "not_implemented", label: str | None = None) -> PresetSpec:
    return PresetSpec(
        name=f"KB{n}", kind=kind,
        label=label or (
            f"Known-bad qualification case KB{n}: RHACO_EXPLORER_FAULT={fault} "
            "(explorer/faults.py; the probe must flag it once the reader/lineage/search "
            "surfaces the fault touches are built)"
        ),
        fault=fault,
    )


# Registry order: healthz and diagnostics (rounds 1/C1), then the ten
# acceptance workflows (PROMPT.md section 8), then the qualification cases
# (ARCHITECTURE.md section 6 / explorer/faults.FAULTS) -- KG first (known-good
# baseline, no fault), then KB1-KB5 mapped 1:1 onto FAULTS in its declared
# order (wrong_doc_for_id, stale_card, reverse_edges, broken_jump,
# console_error). Round 2 (task B7) gave real `kind="workflow"` runners
# (WORKFLOW_RUNNERS, defined further down) to W1-W4, W7-W10, KG, KB1, KB2,
# KB4, KB5. Round 4 (task B10, Q3 + FINAL) gives the same to the remaining
# three -- W5, W6 (lineage, production) and KB3 (reverse_edges, fixture) --
# so every preset in this registry is now real; none is `not_implemented`.
PRESET_REGISTRY: dict[str, PresetSpec] = {
    "healthz": PresetSpec(
        "healthz", "json_endpoint",
        "Server health/readiness JSON (GET /healthz, status must equal \"ok\")",
        path="/healthz",
        required_classes=(),
    ),
    "diagnostics": PresetSpec(
        "diagnostics", "page",
        "Diagnostics page (GET /diagnostics; must return HTTP 200 with data-mode in "
        "{hybrid, hybrid-degraded-lexical}, data-vector in {available, unavailable}, "
        "and a non-empty title -- task C1 item 3, now that the diagnostics module is merged)",
        path="/diagnostics",
        data_mode_in={"hybrid", "hybrid-degraded-lexical"},
        data_vector_in={"available", "unavailable"},
        require_title=True,
        required_classes=("KB5",),
    ),
    "W1": _w(1, "Exact known document -- search a canonical id, expect direct result -> correct card",
             required_classes=("KB1", "KB5"), kind="workflow"),
    "W2": _w(2, "Lexical phrase -- search a known phrase, expect target + consistent excerpt/line",
             required_classes=("KB1", "KB2", "KB5"), kind="workflow"),
    "W3": _w(3, "Semantic inquiry -- frozen gold semantic query, accepted hybrid baseline preserved",
             required_classes=("KB1", "KB5"), kind="workflow"),
    "W4": _w(4, "Campaign lifecycle browse -- CMP filter, status + lifecycle_state both visible/filterable",
             required_classes=("KB2", "KB5"), kind="workflow"),
    "W5": _w(5, "Reasoning lineage -- edges match indexed relationships and direction",
             required_classes=("KB3", "KB5"), kind="workflow"),
    "W6": _w(6, "Supersession/amendment -- historical artifact visible, replacement relationship clear",
             required_classes=("KB3", "KB5"), kind="workflow"),
    "W7": _w(7, "Degraded semantic channel -- RHACO_CORPUS_DISABLE_VEC=1, lexical/direct still usable",
             required_classes=("KB5",), kind="workflow"),
    "W8": _w(8, "Staleness -- freshness DRIFT surfaced, never silently treated as current",
             required_classes=("KB2", "KB5"), kind="workflow"),
    "W9": _w(9, "Reader provenance -- open a hit at a line/section, body vs card rendered distinctly",
             required_classes=("KB4", "KB5"), kind="workflow"),
    "W10": _w(10, "No-LLM operation -- full standard workflow, no frontier model access",
              required_classes=("KB1", "KB2", "KB4", "KB5"), kind="workflow"),
    "KG": PresetSpec(
        "KG", "workflow",
        "Known-good qualification baseline against the fixture index (no RHACO_EXPLORER_FAULT set): "
        "identifier search (E000777), lexical search (quartz lattice lantern), reader body/card identity",
        required_classes=(),
    ),
    "KB1": _kb(1, FAULTS[0], kind="workflow",
               label="Known-bad KB1 (wrong_doc_for_id): identifier search for a multi-card id -- "
                     "the first listed card_ref must be the id's own card, not a sibling amendment"),
    "KB2": _kb(2, FAULTS[1], kind="workflow",
               label="Known-bad KB2 (stale_card): reader index row vs card file comparison"),
    "KB3": _kb(3, FAULTS[2], kind="workflow",
               label="Known-bad KB3 (reverse_edges): the CMP center's campaign_child edge to the ANL "
                     "fixture card -- from/to swapped and direction flipped under the fault"),
    "KB4": _kb(4, FAULTS[3], kind="workflow",
               label="Known-bad KB4 (broken_jump): reader heading line-anchor re-verification"),
    "KB5": _kb(5, FAULTS[4], kind="workflow",
               label="Known-bad KB5 (console_error): diagnostics page-error detection, extended to "
                     "catalog/search/reader as clean control navigations on the same wave-2 surfaces"),
}

# Fault-class attribution table (task C1 item 1), kept next to PRESET_REGISTRY: KBn ->
# the explorer.faults.FAULTS name it qualifies (same order as explorer/faults.py). KB5's
# rule (a console/page error whose text contains CONSOLE_ERROR_FAULT_TEXT) is a
# substring match, checked by _attribute_fault_class below via FAULT_TEXT_MARKERS.
# KB1/KB2/KB4 (task B7) have no console/page error to match at all -- each fault's
# observable signature is a DOM/API comparison instead, so each gets its own pure
# _kbN_verdict predicate immediately below (unit-tested in
# tests/probe/test_workflow_verdicts.py without a server or browser); evaluate_page
# and PRESET_REGISTRY need no restructuring for either kind of rule.
FAULT_CLASS_TABLE: dict[str, str] = {
    "KB1": "wrong_doc_for_id",
    "KB2": "stale_card",
    "KB3": "reverse_edges",
    "KB4": "broken_jump",
    "KB5": "console_error",
}
FAULT_TO_CLASS: dict[str, str] = {fault: cls for cls, fault in FAULT_CLASS_TABLE.items()}

# The exact string explorer/diagnostics/templates/diagnostics/diagnostics.html throws
# when RHACO_EXPLORER_FAULT=console_error is active (explorer/faults.py FAULTS[4]).
CONSOLE_ERROR_FAULT_TEXT = "RHACO_EXPLORER_FAULT console_error"
FAULT_TEXT_MARKERS: dict[str, str] = {
    CONSOLE_ERROR_FAULT_TEXT: "KB5",
}


def _attribute_fault_class(text: str) -> str | None:
    """A FAIL reason's text -> the KB class it is attributable to, or None. Substring
    match against FAULT_TEXT_MARKERS (task C1 item 1)."""
    for marker, cls in FAULT_TEXT_MARKERS.items():
        if marker in text:
            return cls
    return None


# task B6/O23's ATX re-check, independently re-implemented here (never imported from
# explorer.reader.service -- the probe verifies the observable contract, not the other
# builder's implementation) so KB4's independent comparison does not merely re-run the
# app's own check.
_ATX_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")


def _verify_heading_independently(lines: list[str], line_no: int, text: str) -> bool:
    idx = line_no - 1
    if idx < 0 or idx >= len(lines):
        return False
    m = _ATX_RE.match(lines[idx])
    if not m:
        return False
    return m.group(2).rstrip("#").strip() == text


def _kb1_verdict(observed_first_card_ref: str | None, expected_correct_ref: str, expected_fault_ref: str
                  ) -> tuple[list[str], bool, str | None]:
    """KB1 / wrong_doc_for_id: an identifier search for a multi-card-row id must
    list that id's OWN card first; the fault rotates the row order by one.
    Symmetric: a clean match to `expected_correct_ref` is a quiet PASS (this
    same rule also works as the id-resolution sanity check when no fault is
    active), a match to `expected_fault_ref` is the known-bad detection, and
    anything else is an unattributed FAIL."""
    if observed_first_card_ref == expected_correct_ref:
        return [], False, None
    if observed_first_card_ref == expected_fault_ref:
        return (
            ["KB1: identifier search's first card_ref rotated to the amendment's card_ref "
             f"({observed_first_card_ref!r}) instead of the id's own ({expected_correct_ref!r}) "
             "-- fault wrong_doc_for_id"],
            True, "KB1",
        )
    return (
        [f"KB1: identifier search's first card_ref={observed_first_card_ref!r} matches neither "
         "the expected correct ref nor the known fault rotation"],
        False, None,
    )


def _kb2_verdict(mismatch_attr: str | None, file_title: Any, file_status: Any,
                  indexed_title: Any, indexed_status: Any) -> tuple[list[str], bool, str | None]:
    """KB2 / stale_card: FAIL with KB2 when EITHER the reader's own
    data-card-index-mismatch marker is set OR the probe's independent
    title/status comparison (parsed card file vs. the index row the API
    reports) disagrees -- either observable alone is sufficient (task B7)."""
    page_marks_mismatch = bool(mismatch_attr)
    file_disagrees = (indexed_title != file_title) or (indexed_status != file_status)
    if not page_marks_mismatch and not file_disagrees:
        return [], False, None
    return (
        [f"KB2: stale index row detected -- page data-card-index-mismatch={mismatch_attr!r}, "
         f"independent file comparison: indexed title/status={indexed_title!r}/{indexed_status!r} "
         f"vs file title/status={file_title!r}/{file_status!r}"],
        True, "KB2",
    )


def _kb3_verdict(
    observed: tuple[str | None, str | None, str | None],
    expected_correct: tuple[str, str, str],
    expected_fault: tuple[str, str, str],
) -> tuple[list[str], bool, str | None]:
    """KB3 / reverse_edges (task B10): an edge's `(from_id, to_id, direction)`
    triple must equal the frozen known-correct fixture fact (docs/rounds/
    R03_lineage.report.md Evidence #6/#11; tests/lineage/test_faults.py). The
    fault swaps `from_id`/`to_id` inside `CorpusAdapter.edges_for`
    (explorer/corpus_adapter/adapter.py lines 506-507), and the lineage module
    never re-derives direction from the ids (explorer/lineage/service.py
    module docstring) -- it renders whichever `EdgeSet` bucket the adapter
    placed the (already swapped) edge into, faithfully. So a faulted edge is
    observed with from/to swapped AND its direction bucket flipped (outgoing
    <-> incoming) all at once, never one without the other.

    Symmetric, like `_kb1_verdict`: a match to `expected_correct` is a quiet
    PASS (also the no-fault sanity check, so this predicate is safe to run
    unconditionally), a match to `expected_fault` is the known-bad detection,
    and anything else -- including a missing edge, observed as a tuple of
    `None`s -- is an unattributed FAIL."""
    if observed == expected_correct:
        return [], False, None
    if observed == expected_fault:
        return (
            [f"KB3: observed edge (from_id, to_id, direction)={observed!r} is the SWAPPED "
             f"known-fault triple, not the known-correct {expected_correct!r} -- fault reverse_edges"],
            True, "KB3",
        )
    return (
        [f"KB3: observed edge triple {observed!r} matches neither the known-correct "
         f"{expected_correct!r} nor the known fault swap {expected_fault!r}"],
        False, None,
    )


def _kb4_verdict(page_any_unverified: bool, independent_mismatch_count: int) -> tuple[list[str], bool, str | None]:
    """KB4 / broken_jump: FAIL with KB4 when EITHER the reader's own TOC shows a
    data-line-verified="false" heading OR the probe's independent re-check
    (lines[line_no-1] must begin an ATX heading matching the heading's text)
    finds a mismatch."""
    if not page_any_unverified and not independent_mismatch_count:
        return [], False, None
    return (
        [f"KB4: broken heading line-anchor(s) detected -- page shows a data-line-verified=\"false\" "
         f"heading: {page_any_unverified}; independent re-check found {independent_mismatch_count} "
         "mismatched heading(s)"],
        True, "KB4",
    )


def _w10_localhost_check(requests: list[dict]) -> tuple[list[str], list[dict]]:
    """W10: every recorded request's host must be 127.0.0.1 (or localhost) --
    the only sanctioned dependency is the server-side local embedder, which
    the browser itself never contacts."""
    offenders = [
        r for r in requests
        if urllib.parse.urlparse(r.get("url", "")).hostname not in ("127.0.0.1", "localhost")
    ]
    if not offenders:
        return [], []
    return [f"W10: {len(offenders)} request(s) left 127.0.0.1: {offenders[:5]}"], offenders


def _utc_stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True), encoding="ascii")


def _ascii(text: str) -> str:
    return text.encode("ascii", "replace").decode("ascii")


# ─── Server lifecycle (the only sanctioned launcher, O12) ───────────────────

def launch_server(python_exe: str, port: int, db_path: str, docs_root: str,
                   cwd: str, log_file, fault: str | None = None,
                   disable_vec: bool = False) -> subprocess.Popen:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["RHACO_EXPLORER_DB"] = db_path
    env["RHACO_EXPLORER_DOCS_ROOT"] = docs_root
    env["RHACO_EXPLORER_HOST"] = "127.0.0.1"
    env["RHACO_EXPLORER_PORT"] = str(port)
    if fault:
        env["RHACO_EXPLORER_FAULT"] = fault
    if disable_vec:
        env["RHACO_CORPUS_DISABLE_VEC"] = "1"
    cmd = [
        python_exe, "-m", "uvicorn", "explorer.app:create_app", "--factory",
        "--host", "127.0.0.1", "--port", str(port),
    ]
    return subprocess.Popen(
        cmd, cwd=cwd, env=env, stdout=log_file, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="replace",
    )


def terminate_server(proc: subprocess.Popen, wait_s: float = 5.0) -> None:
    if proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=wait_s)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=wait_s)


def wait_for_healthz(base_url: str, timeout_s: float) -> dict:
    """Poll GET /healthz every READY_POLL_S up to timeout_s. The ONLY sleep-poll
    loop in this file, and it is bounded (O12 / D-3)."""
    deadline = time.monotonic() + timeout_s
    last_err = "no attempt made"
    while time.monotonic() < deadline:
        try:
            req = urllib.request.Request(f"{base_url}/healthz", headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=2) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                if body.get("status") == "ok":
                    return body
                last_err = f"status={body.get('status')!r}"
        except (urllib.error.URLError, OSError, json.JSONDecodeError, ValueError) as exc:
            last_err = f"{type(exc).__name__}: {exc}"
        time.sleep(READY_POLL_S)
    raise TimeoutError(f"server did not become ready within {timeout_s}s (last: {last_err})")


# ─── Preset runners ──────────────────────────────────────────────────────────

def run_json_endpoint_preset(base_url: str, spec: PresetSpec, timeout_s: float = 10.0) -> dict:
    url = base_url + (spec.path or "")
    t0 = time.monotonic()
    nav_start = _now_iso()
    http_status = None
    body = None
    error = None
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            http_status = resp.status
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        http_status = exc.code
        try:
            body = json.loads(exc.read().decode("utf-8"))
        except (ValueError, OSError):
            body = None
        error = f"HTTPError {exc.code}"
    except Exception as exc:  # noqa: BLE001 -- recorded as an observation, never crashes the probe
        error = f"{type(exc).__name__}: {exc}"
    nav_end = _now_iso()
    elapsed_ms = (time.monotonic() - t0) * 1000.0

    required_ok = error is None and isinstance(body, dict) and body.get("status") == "ok"
    return {
        "preset": spec.name,
        "kind": spec.kind,
        "label": spec.label,
        "url": url,
        "viewport": None,
        "http_status": http_status,
        "route_absent": False,
        "title": None,
        "mode": None,
        "selected_doc_id": None,
        "result_ids": [],
        "console_errors": [],
        "failed_requests": [],
        "timings": {"nav_start_utc": nav_start, "nav_end_utc": nav_end, "elapsed_ms": round(elapsed_ms, 1)},
        "screenshot": None,
        "body": body,
        "error": error,
        "ok": required_ok,
    }


def _console_listener(collected: list) -> callable:
    def _on_console(msg) -> None:
        if msg.type == "error":
            collected.append({"type": msg.type, "text": msg.text})
    return _on_console


def _page_error_listener(collected: list) -> callable:
    """Playwright's `pageerror` event -- an uncaught `throw` inside a page script
    (task C1 item 1). Verified empirically against explorer/diagnostics/templates/
    diagnostics/diagnostics.html's `<script>throw new Error(...)</script>`: it does
    NOT arrive on `console` (that event fires only for explicit console.* calls,
    i.e. Runtime.consoleAPICalled); it arrives here, on `pageerror`
    (Runtime.exceptionThrown). See the report's Evidence section for the run that
    established this."""
    def _on_page_error(exc) -> None:
        message = getattr(exc, "message", None) or str(exc)
        collected.append({"message": message})
    return _on_page_error


def _request_failed_listener(collected: list) -> callable:
    def _on_request_failed(request) -> None:
        failure = request.failure
        text = failure.get("errorText") if isinstance(failure, dict) else failure
        collected.append({"source": "requestfailed", "url": request.url, "method": request.method, "detail": text})
    return _on_request_failed


def _response_listener(collected: list) -> callable:
    def _on_response(response) -> None:
        if response.status >= 400:
            collected.append({"source": "response", "url": response.url, "status": response.status})
    return _on_response


def _extract_dom_observations(page) -> dict:
    mode = page.evaluate("() => document.documentElement.getAttribute('data-mode')")
    vector = page.evaluate("() => document.documentElement.getAttribute('data-vector')")
    selected = page.evaluate(
        "() => { const el = document.querySelector('[data-selected-doc-id]'); "
        "return el ? el.getAttribute('data-selected-doc-id') : null; }"
    )
    result_ids = page.evaluate(
        "() => Array.from(document.querySelectorAll('[data-doc-id]'))"
        ".map((el) => el.getAttribute('data-doc-id'))"
    )
    return {"mode": mode, "vector": vector, "selected_doc_id": selected, "result_ids": result_ids}


@dataclass(frozen=True)
class Verdict:
    ok: bool
    reasons: list[str]
    fault_detected: bool
    fault_class: str | None


def evaluate_page(observation: dict, spec: PresetSpec) -> Verdict:
    """The observed-fault predicate for page presets (task C1 item 1; repairs the
    round-1 `ok = error is None` bug -- docs/probe-qualification/runs/
    20260904T033047Z/diagnostics.json is the recorded defect). Pure: reads only
    `observation` (a page preset's collected navigation/DOM/console/network/
    page-error data) and `spec` (its PresetSpec); mutates neither; returns a
    Verdict. `observation` keys used: error, http_status, console_errors
    (already carrying any mirrored pageerror entries -- see run_page_preset),
    failed_requests, mode, vector, title.

    Rules, applied in this order (all contribute independently to `reasons`;
    the verdict is FAIL iff `reasons` is non-empty):
      (a) a navigation or extraction error -> FAIL (unchanged from round 1).
      (b) http_status >= 400 -> FAIL unless spec.expected_status equals it.
      (c) any console error (including a mirrored pageerror) -> FAIL; one
          whose text matches a known fault marker (FAULT_TEXT_MARKERS) also
          sets fault_detected / fault_class.
      (d) any failed request (a requestfailed event, or a response >= 400) ->
          FAIL.
      (e) the spec's declarative data-* assertions (data_mode_in,
          data_vector_in, require_title) -> FAIL with the assertion's name in
          the reason.
    """
    reasons: list[str] = []
    fault_detected = False
    fault_class: str | None = None

    def _note_fault(cls: str) -> None:
        nonlocal fault_detected, fault_class
        fault_detected = True
        fault_class = cls

    # (a) navigation or extraction error.
    error = observation.get("error")
    if error:
        reasons.append(f"navigation_or_extraction_error: {error}")

    # (b) unexpected HTTP status.
    http_status = observation.get("http_status")
    if isinstance(http_status, int) and http_status >= 400 and spec.expected_status != http_status:
        reasons.append(f"unexpected_http_status: {http_status}")

    # (c) console errors (pageerror entries are pre-mirrored in here by
    # run_page_preset with type "pageerror", so this one rule covers both).
    for entry in observation.get("console_errors") or []:
        text = entry.get("text", "")
        cls = _attribute_fault_class(text)
        if cls:
            _note_fault(cls)
            reasons.append(f"console_error[{entry.get('type')}] (fault {cls}): {text}")
        else:
            reasons.append(f"console_error[{entry.get('type')}]: {text}")

    # (d) failed requests.
    for entry in observation.get("failed_requests") or []:
        detail = entry.get("status", entry.get("detail"))
        reasons.append(f"failed_request[{entry.get('source')}]: {entry.get('url')} ({detail})")

    # (e) declarative data-* assertions.
    if spec.data_mode_in is not None:
        mode = observation.get("mode")
        if mode not in spec.data_mode_in:
            reasons.append(f"data_mode_in: mode={mode!r} not in {sorted(spec.data_mode_in)}")
    if spec.data_vector_in is not None:
        vector = observation.get("vector")
        if vector not in spec.data_vector_in:
            reasons.append(f"data_vector_in: vector={vector!r} not in {sorted(spec.data_vector_in)}")
    if spec.require_title:
        title = observation.get("title")
        if not title:
            reasons.append(f"require_title: title={title!r} is empty")

    return Verdict(ok=not reasons, reasons=reasons, fault_detected=fault_detected, fault_class=fault_class)


def run_page_preset(browser, base_url: str, spec: PresetSpec, out_dir: Path) -> dict:
    url = base_url + (spec.path or "")
    console_errors: list = []
    failed_requests: list = []
    page_errors: list = []

    context = browser.new_context(viewport=VIEWPORT)
    page = context.new_page()
    page.on("console", _console_listener(console_errors))
    page.on("requestfailed", _request_failed_listener(failed_requests))
    page.on("response", _response_listener(failed_requests))
    page.on("pageerror", _page_error_listener(page_errors))

    t0 = time.monotonic()
    nav_start = _now_iso()
    http_status = None
    error = None
    try:
        response = page.goto(url, timeout=NAV_TIMEOUT_MS, wait_until="load")
        http_status = response.status if response is not None else None
    except Exception as exc:  # noqa: BLE001 -- recorded as an observation, never crashes the probe
        error = f"{type(exc).__name__}: {exc}"
    nav_end = _now_iso()
    elapsed_ms = (time.monotonic() - t0) * 1000.0

    title = None
    dom_obs = {"mode": None, "vector": None, "selected_doc_id": None, "result_ids": []}
    if error is None:
        try:
            title = page.title()
            dom_obs = _extract_dom_observations(page)
        except Exception as exc:  # noqa: BLE001
            error = f"post-navigation extraction failed: {type(exc).__name__}: {exc}"

    screenshot_path = out_dir / f"{spec.name}.png"
    screenshot_saved = None
    try:
        page.screenshot(path=str(screenshot_path), full_page=True)
        screenshot_saved = str(screenshot_path)
    except Exception:  # noqa: BLE001 -- a missing screenshot is recorded, not fatal
        screenshot_saved = None

    context.close()

    # Mirror page-level uncaught exceptions into console_errors (type "pageerror")
    # so evaluate_page's single console-error rule (c) covers both sources -- see
    # _page_error_listener's docstring for the empirical finding on which event
    # actually carries the diagnostics fault's throw.
    for pe in page_errors:
        console_errors.append({"type": "pageerror", "text": pe["message"]})

    route_absent = http_status == 404  # descriptive only; no longer an accepted state (task C1)

    observation = {
        "error": error,
        "http_status": http_status,
        "console_errors": console_errors,
        "failed_requests": failed_requests,
        "mode": dom_obs["mode"],
        "vector": dom_obs["vector"],
        "title": title,
    }
    verdict = evaluate_page(observation, spec)

    return {
        "preset": spec.name,
        "kind": spec.kind,
        "label": spec.label,
        "url": url,
        "viewport": VIEWPORT,
        "http_status": http_status,
        "route_absent": route_absent,
        "title": title,
        "mode": dom_obs["mode"],
        "vector": dom_obs["vector"],
        "selected_doc_id": dom_obs["selected_doc_id"],
        "result_ids": dom_obs["result_ids"],
        "console_errors": console_errors,
        "failed_requests": failed_requests,
        "page_errors": page_errors,
        "timings": {"nav_start_utc": nav_start, "nav_end_utc": nav_end, "elapsed_ms": round(elapsed_ms, 1)},
        "screenshot": screenshot_saved,
        "error": error,
        "verdict": "PASS" if verdict.ok else "FAIL",
        "reasons": verdict.reasons,
        "fault_detected": verdict.fault_detected,
        "fault_class": verdict.fault_class,
        "ok": verdict.ok,
    }


def run_not_implemented_preset(spec: PresetSpec) -> dict:
    return {
        "preset": spec.name,
        "kind": spec.kind,
        "label": spec.label,
        "status": "not_implemented_yet",
        "fault": spec.fault,
        "ok": True,
    }


# ─── Wave-2 workflow runners (task B7) ───────────────────────────────────────
#
# W1-W10 / KG / KB1-KB5 (except W5, W6, KB3 -- lineage, wave 3) are implemented
# below as `kind="workflow"` presets: a `Session` (one Playwright browser
# context + page, reused across a short sequence of navigation "steps" per the
# dispatch's "a short sequence of page navigations recorded as one preset with
# sub-steps") drives the merged catalog/search/reader/diagnostics surfaces;
# each runner also cross-checks the /api twin and, where specified, reads the
# fixture or production docs root directly from disk (never through the
# index -- the index is reached only through the server this file launches).
#
# Each fault-specific runner (KB1/KB2/KB4) delegates its pass/fail decision to
# a pure, dependency-free `_kbN_verdict` function taking only the already-
# observed values -- these are what tests/probe/test_workflow_verdicts.py unit
# -tests without a server or browser (task B7 deliverable 4). `evaluate_page`
# and the `"page"` / `"json_endpoint"` kinds (healthz, diagnostics) from
# rounds 1/C1 are unchanged.


@dataclass
class ProbeContext:
    """Shared, read-only run configuration passed to every workflow runner
    (task B7). `docs_root` and `db_path` are the CLI's own (realpath'd)
    values -- workflow runners read `docs_root` directly from disk for
    independent verification (sha256, line content, YAML parsing) but never
    open `db_path`; only the server this file launches ever does."""

    docs_root: str
    db_path: str
    port: int
    fault: str | None
    disable_vec: bool
    timeout_s: float


def _free_port() -> int:
    """An OS-assigned free TCP port on 127.0.0.1 (W8: its own dedicated,
    isolated server needs a port distinct from the run's main --port)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _http_get(url: str, timeout_s: float = 10.0) -> tuple[int | None, str | None, str | None]:
    """GET url -> (status, body_text, error). Never raises -- a probe
    observation, same discipline as run_json_endpoint_preset."""
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace"), None
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode("utf-8", errors="replace")
        except OSError:
            body = None
        return exc.code, body, f"HTTPError {exc.code}"
    except Exception as exc:  # noqa: BLE001
        return None, None, f"{type(exc).__name__}: {exc}"


def _http_get_json(base_url: str, path: str, timeout_s: float = 10.0) -> tuple[int | None, dict | None, str | None]:
    status, body, error = _http_get(base_url + path, timeout_s)
    if body is None:
        return status, None, error
    try:
        return status, json.loads(body), error
    except ValueError as exc:
        return status, None, f"json_decode_error: {exc}"


def _api_doc_path(open_link: str) -> str:
    """The /api/doc twin of a /doc/... open link, preserving any ?line=... suffix."""
    if open_link.startswith("/doc/"):
        return "/api/doc/" + open_link[len("/doc/"):]
    return open_link


def _sha256_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _read_lines(path: str) -> list[str]:
    with open(path, "rb") as fh:
        raw = fh.read()
    return raw.decode("utf-8", errors="replace").splitlines()


def _parse_card_yaml_file(path: str) -> dict:
    with open(path, encoding="utf-8", errors="replace") as fh:
        data = yaml.safe_load(fh.read())
    return data if isinstance(data, dict) else {}


# ─── Fixture and production-path constants (task B7) ─────────────────────────

FIXTURE_CORPUS_ROOT = os.path.join(_WORKSPACE_ROOT, "fixtures", "corpus")

FIXTURE_EVT_IDENTIFIER_QUERY = "E000777"
FIXTURE_EVT_DOC_ID = "RHACO-EVT-20260115-004"
FIXTURE_EVT_CARD_REF = "reports/RHACO-EVT-20260115-004_Fixture_Event_E000777.card.yaml"

FIXTURE_ANL_LEXICAL_QUERY = "quartz lattice lantern"
FIXTURE_ANL_DOC_ID = "RHACO-ANL-20260115-002"
FIXTURE_ANL_CARD_REF = "reports/RHACO-ANL-20260115-002_Fixture_Analysis.card.yaml"
FIXTURE_ANL_DOC_PATH = os.path.join(FIXTURE_CORPUS_ROOT, "reports", "RHACO-ANL-20260115-002_Fixture_Analysis.md")
FIXTURE_ANL_CARD_PATH = os.path.join(
    FIXTURE_CORPUS_ROOT, "reports", "RHACO-ANL-20260115-002_Fixture_Analysis.card.yaml"
)
FIXTURE_ANL_LINE_NO = 15

FIXTURE_HND_IDENTIFIER_QUERY = "RHACO-HND-20260115-003"
FIXTURE_HND_CARD_REF = "handoffs/RHACO-HND-20260115-003_Fixture_Handoff.card.yaml"
FIXTURE_HND_AMENDMENT_CARD_REF = "handoffs/RHACO-HND-20260115-003_Fixture_Handoff_Amendment_A1.card.yaml"

# W8's synthetic drift card/document, written only into a *temp copy* of
# fixtures/corpus (never into the committed fixture tree).
W8_DRIFT_CARD_NAME = "RHACO-OBS-20260115-999_Fixture_Drift"
W8_DRIFT_CARD_YAML = """identity:
  document: RHACO-OBS-20260115-999_Fixture_Drift.md
  doc_type: OBS
  date: "2026-01-15"
  seq: "999"
  title: Fixture Drift Probe
  status: Active
  programs: [Infra]
  project_knowledge: in
  schema_version: 1
  naming_convention_version: "1.17"
  last_human_review: "2026-01-15"
  reviewer: Fixture Builder

abstract: >
  Synthetic OBS card added to a copy of the fixture corpus AFTER its index
  was built, so diagnostics freshness reports DRIFT (probe task B7, W8).

tags:
  - fixture
  - drift

depends_on: []
see_also: []
superseded_by: null

location:
  local_path: (probe-generated; not a real RHACO location)

notes:
  - "Synthetic fixture card; added post-index-build to exercise W8 staleness. Never committed."
"""
W8_DRIFT_CARD_MD = (
    "# RHACO-OBS-20260115-999 -- Fixture Drift Probe\n\n"
    "Added after the fixture index was built, to exercise W8 (staleness). Never committed.\n"
)

# W1 (production): this build's own campaign card -- guaranteed present in the
# live corpus once the wave-2 merge lands (the dispatch names it explicitly).
PRODUCT_W1_QUERY = "RHACO-CMP-20260903-001"

# W2 (production): Gold v1.1 S2 row 10 (docs/probe-qualification/gold_v1_1_compat.json)
# -- a title-fragment lexical query whose target is a frozen document; verified against
# the live corpus by reading C:\\RHACO\\docs directly (see the round report's Evidence).
PRODUCT_W2_QUERY = "tungsten putty seal"
PRODUCT_W2_TARGET_DOC_ID = "RHACO-MTN-20260520-001"

# W3 (production): Gold v1.1 S3 row 21 -- gold_v1_1_compat.json records it as a hit
# today (hit_adapter=true, lists_equal=true); PRODUCT_W3_ORACLE_ORDER is that row's
# recorded adapter_ids (the L4 oracle's top-10 hybrid order) for the reproducibility
# comparison the dispatch asks for.
PRODUCT_W3_QUERY = "moving the shielded enclosure to a new spot"
PRODUCT_W3_TARGET_DOC_ID = "RHACO-MTN-20260426-001"
PRODUCT_W3_TOP_K = 10
PRODUCT_W3_ORACLE_ORDER: tuple[str, ...] = (
    "RHACO-ANL-20260710-001", "RHACO-ANL-20260711-001", "RHACO-MTN-20260426-001",
    "RHACO-CHG-20260617-002", "RHACO-HND-20260609-001", "RHACO-CCX-20260617-002",
    "RHACO-CHG-20260502-001", "RHACO-CHG-20260423-004", "RHACO-HND-20260524-004",
    "RHACO-CHG-20260531-004",
)

PRODUCT_W4_DOC_TYPE = "CMP"

# CONSTRAINTS.md O4 -- exact wording, reused verbatim (matches explorer/corpus_adapter/
# adapter.py HYBRID_DEGRADED_NOTICE and explorer/diagnostics/service.py DEGRADATION_TEXT;
# defined independently here rather than imported, so the probe verifies the observable
# text contract rather than merely re-reading the same module constant both builders share).
HYBRID_DEGRADED_NOTICE_TEXT = "Hybrid unavailable: using lexical retrieval. Result ordering is lexical-only."

# ─── Lineage fixture/production constants (task B10, Q3, round 4) ───────────
#
# Fixture facts reproduced verbatim from tests/lineage/conftest.py and
# docs/rounds/R03_lineage.report.md Evidence #6/#8/#9/#10/#11 (not imported --
# the probe verifies the observable contract, never the other module's own
# test fixtures, matching this file's existing HYBRID_DEGRADED_NOTICE_TEXT
# convention above).
FIXTURE_CMP_CARD_REF = "reports/RHACO-CMP-20260115-001_Fixture_Campaign.card.yaml"
FIXTURE_CMP_DOC_ID = "RHACO-CMP-20260115-001"
FIXTURE_HND_DOC_ID = "RHACO-HND-20260115-003"
FIXTURE_AMENDMENT_STEM = "RHACO-HND-20260115-003_Fixture_Handoff_Amendment_A1"
FIXTURE_UNRESOLVED_TARGET = "RHACO-ANL-20260101-099"
FIXTURE_REF_V1_0_CARD_REF = "reference/RHACO_Fixture_Reference_v1_0.card.yaml"
FIXTURE_REF_V1_1_DOC_ID = "RHACO_Fixture_Reference_v1_1"

# W5/W6 (production): this build's own campaign, and two of its members whose
# card.yaml `depends_on` entry names the campaign directly (the "independent
# check" task 3 requires) -- verified by reading C:\RHACO\docs\** directly,
# never through the index (PROMPT.md 5.5 invariant; task 3's own instruction).
PRODUCT_W5_CMP_CARD_REF = "reports/RHACO-CMP-20260903-001_Corpus_Explorer_Autonomous_Build_Harness.card.yaml"
PRODUCT_W5_INDEPENDENT_CHECKS: tuple[tuple[str, str, str], ...] = (
    # (child_doc_id, child_card_ref relative to docs_root, the depends_on id expected on disk)
    ("RHACO-HND-20260903-001",
     "handoffs/RHACO-HND-20260903-001_Corpus_Explorer_Autonomous_Build_Dispatch.card.yaml",
     "RHACO-CMP-20260903-001"),
    ("RHACO-CHG-20260903-001",
     "reports/RHACO-CHG-20260903-001_Subagent_Guide_v1_3_Model_Tier_Declaration.card.yaml",
     "RHACO-CMP-20260903-001"),
)

# W6 (production): (a) supersession -- Card Schema v1.8 (Superseded) -> v1.9 (head).
PRODUCT_W6_SUPERSEDED_CARD_REF = "reference/RHACO_Card_YAML_Schema_Specification_v1_8.card.yaml"
PRODUCT_W6_SUPERSEDED_DOC_ID = "RHACO_Card_YAML_Schema_Specification_v1_8"
PRODUCT_W6_HEAD_DOC_ID = "RHACO_Card_YAML_Schema_Specification_v1_9"
# (b) amendment -- this build's own A1 amendment of its own dispatch hand.
PRODUCT_W6_AMENDMENT_CARD_REF = (
    "handoffs/RHACO-HND-20260903-001_Corpus_Explorer_Autonomous_Build_Dispatch_"
    "Amendment_A1_Cap_Rehome_And_Session_2_Findings.card.yaml"
)
PRODUCT_W6_AMENDMENT_STEM = (
    "RHACO-HND-20260903-001_Corpus_Explorer_Autonomous_Build_Dispatch_"
    "Amendment_A1_Cap_Rehome_And_Session_2_Findings"
)
PRODUCT_W6_PARENT_CARD_REF = "handoffs/RHACO-HND-20260903-001_Corpus_Explorer_Autonomous_Build_Dispatch.card.yaml"
PRODUCT_W6_PARENT_DOC_ID = "RHACO-HND-20260903-001"
# SCOPE.md row 17: the known, dispositioned limitation task 4(b) says to
# record and NOT fail on -- the parent's own incoming `amends` edge renders
# as typed, directional, resolved (never `unresolved`) text with no link,
# because CorpusAdapter.edges_for resolves source_cards/target_cards through
# cards_for_doc_id (doc_id only), while an `amends` edge's from_id is the
# amendment's filename STEM (CONSTRAINTS.md O8), which matches no card's
# doc_id.
W6_KNOWN_LIMITATION = (
    "SCOPE.md row 17 (\"Click-through from an amends edge to the amendment, on the "
    "lineage graph and trail\", status LIMITED): on the PARENT card's own lineage page "
    "the incoming amends edge from the amendment renders as typed, directional text "
    "with no link (source_cards is empty -- cards_for_doc_id cannot resolve a "
    "filename stem) but is NOT marked unresolved, since resolved=true for this edge."
)


# ─── Session: one browser context reused across a workflow's steps ──────────


class Session:
    """One Playwright browser context + page, reused across several logical
    navigation "steps" within a single workflow preset. Console/page-error/
    failed-request/request listeners are attached once and accumulate across
    every `.goto()` / `.click_submit()`, each entry tagged with the step name
    active at capture time -- this is what lets a composite preset (KB5, W10)
    attribute an observation to the specific step that produced it."""

    def __init__(self, browser) -> None:
        self.context = browser.new_context(viewport=VIEWPORT)
        self.page = self.context.new_page()
        self.console_errors: list[dict] = []
        self.page_errors: list[dict] = []
        self.failed_requests: list[dict] = []
        self.requests: list[dict] = []
        self.steps: list[dict] = []
        self._step: str | None = None
        self.page.on("console", self._on_console)
        self.page.on("pageerror", self._on_pageerror)
        self.page.on("requestfailed", self._on_request_failed)
        self.page.on("response", self._on_response)
        self.page.on("request", self._on_request)

    def _on_console(self, msg) -> None:
        if msg.type == "error":
            self.console_errors.append({"type": "error", "text": msg.text, "step": self._step})

    def _on_pageerror(self, exc) -> None:
        message = getattr(exc, "message", None) or str(exc)
        self.page_errors.append({"message": message, "step": self._step})
        self.console_errors.append({"type": "pageerror", "text": message, "step": self._step})

    def _on_request_failed(self, request) -> None:
        failure = request.failure
        text = failure.get("errorText") if isinstance(failure, dict) else failure
        self.failed_requests.append({
            "source": "requestfailed", "url": request.url, "method": request.method,
            "detail": text, "step": self._step,
        })

    def _on_response(self, response) -> None:
        if response.status >= 400:
            self.failed_requests.append({
                "source": "response", "url": response.url, "status": response.status, "step": self._step,
            })

    def _on_request(self, request) -> None:
        self.requests.append({"url": request.url, "method": request.method, "step": self._step})

    def goto(self, step: str, url: str, timeout_ms: int = NAV_TIMEOUT_MS) -> dict:
        self._step = step
        t0 = time.monotonic()
        nav_start = _now_iso()
        http_status = None
        error = None
        title = None
        try:
            response = self.page.goto(url, timeout=timeout_ms, wait_until="load")
            http_status = response.status if response is not None else None
        except Exception as exc:  # noqa: BLE001
            error = f"{type(exc).__name__}: {exc}"
        if error is None:
            try:
                title = self.page.title()
            except Exception as exc:  # noqa: BLE001
                error = f"post-navigation extraction failed: {type(exc).__name__}: {exc}"
        rec = {
            "step": step, "action": "goto", "url": url, "http_status": http_status, "error": error,
            "title": title,
            "timings": {"nav_start_utc": nav_start, "nav_end_utc": _now_iso(),
                        "elapsed_ms": round((time.monotonic() - t0) * 1000.0, 1)},
        }
        self.steps.append(rec)
        return rec

    def click_submit(self, step: str, selector: str, timeout_ms: int = NAV_TIMEOUT_MS) -> dict:
        """Click `selector` and wait for the resulting navigation -- a form POST
        (task B7 W8: "Playwright click; the only POST")."""
        self._step = step
        t0 = time.monotonic()
        nav_start = _now_iso()
        error = None
        title = None
        try:
            with self.page.expect_navigation(timeout=timeout_ms):
                self.page.click(selector, timeout=timeout_ms)
            title = self.page.title()
        except Exception as exc:  # noqa: BLE001
            error = f"{type(exc).__name__}: {exc}"
        rec = {
            "step": step, "action": "click", "selector": selector, "url": self.page.url,
            "http_status": None, "error": error, "title": title,
            "timings": {"nav_start_utc": nav_start, "nav_end_utc": _now_iso(),
                        "elapsed_ms": round((time.monotonic() - t0) * 1000.0, 1)},
        }
        self.steps.append(rec)
        return rec

    def attr(self, selector: str, name: str) -> str | None:
        try:
            return self.page.eval_on_selector(selector, "(el, n) => el.getAttribute(n)", name)
        except Exception:  # noqa: BLE001
            return None

    def attr_all(self, selector: str, name: str) -> list:
        try:
            return self.page.eval_on_selector_all(selector, "(els, n) => els.map((e) => e.getAttribute(n))", name)
        except Exception:  # noqa: BLE001
            return []

    def attr_dicts(self, selector: str, names: list[str]) -> list[dict]:
        """Every element matching `selector`, as one dict of {name: value} per
        element in DOM order (task B10) -- unlike `attr_all` (one attribute
        across every match), the Q3 lineage runners need several attributes
        off the SAME element at once (e.g. an edge row's data-relation,
        data-edge-from, data-edge-to, data-edge-direction together, so they
        can be compared against each other and against /api/lineage without
        an ordering assumption across separate calls). Pass the literal name
        `"$text"` to also capture an element's `textContent` alongside its
        attributes (e.g. the visible direction_label text, or "current head")."""
        try:
            return self.page.eval_on_selector_all(
                selector,
                "(els, ns) => els.map((el) => { const o = {}; "
                "ns.forEach((n) => { o[n] = (n === '$text') ? el.textContent : el.getAttribute(n); }); "
                "return o; })",
                names,
            )
        except Exception:  # noqa: BLE001
            return []

    def text(self, selector: str) -> str | None:
        try:
            return self.page.eval_on_selector(selector, "(el) => el.textContent")
        except Exception:  # noqa: BLE001
            return None

    def count(self, selector: str) -> int:
        try:
            return self.page.eval_on_selector_all(selector, "(els) => els.length")
        except Exception:  # noqa: BLE001
            return 0

    def html_attr(self, name: str) -> str | None:
        try:
            return self.page.evaluate("(n) => document.documentElement.getAttribute(n)", name)
        except Exception:  # noqa: BLE001
            return None

    def screenshot(self, path: Path) -> str | None:
        try:
            self.page.screenshot(path=str(path), full_page=True)
            return str(path)
        except Exception:  # noqa: BLE001
            return None

    def close(self) -> None:
        try:
            self.context.close()
        except Exception:  # noqa: BLE001
            pass


def _collect_basic_reasons(session: Session, expected_status_by_step: dict[str, int] | None = None
                            ) -> tuple[list[str], bool, str | None]:
    """Round 2's generalization of `evaluate_page`'s rules (a)-(d) to a
    multi-step `Session`: a navigation/extraction error, an unexpected HTTP
    status, any console error (fault-attributed via the same
    `FAULT_TEXT_MARKERS` substring match `evaluate_page` uses), or any failed
    request, on ANY step, contributes a reason (the preset FAILs iff `reasons`
    is non-empty, exactly as `Verdict` does for a single-page preset)."""
    expected_status_by_step = expected_status_by_step or {}
    reasons: list[str] = []
    fault_detected = False
    fault_class: str | None = None
    for step in session.steps:
        if step.get("error"):
            reasons.append(f"navigation_or_extraction_error[{step['step']}]: {step['error']}")
        hs = step.get("http_status")
        if isinstance(hs, int) and hs >= 400 and expected_status_by_step.get(step["step"]) != hs:
            reasons.append(f"unexpected_http_status[{step['step']}]: {hs}")
    for entry in session.console_errors:
        cls = _attribute_fault_class(entry["text"])
        if cls:
            fault_detected, fault_class = True, cls
            reasons.append(f"console_error[{entry['type']}@{entry['step']}] (fault {cls}): {entry['text']}")
        else:
            reasons.append(f"console_error[{entry['type']}@{entry['step']}]: {entry['text']}")
    for entry in session.failed_requests:
        detail = entry.get("status", entry.get("detail"))
        reasons.append(f"failed_request[{entry['source']}@{entry['step']}]: {entry['url']} ({detail})")
    return reasons, fault_detected, fault_class


def _finish_workflow(spec: PresetSpec, session: Session, out_dir: Path, *,
                      custom_reasons: list[str] | None = None,
                      fault_detected: bool = False, fault_class: str | None = None,
                      observations: dict | None = None,
                      screenshot_name: str | None = None,
                      expected_status_by_step: dict[str, int] | None = None,
                      incomplete: bool = False) -> dict:
    basic_reasons, basic_fd, basic_fc = _collect_basic_reasons(session, expected_status_by_step)
    reasons = list(custom_reasons or []) + basic_reasons
    fault_detected = fault_detected or basic_fd
    fault_class = fault_class or basic_fc
    screenshot = session.screenshot(out_dir / f"{screenshot_name}.png") if screenshot_name else None
    result = {
        "preset": spec.name,
        "kind": spec.kind,
        "label": spec.label,
        "steps": session.steps,
        "requests_total": len(session.requests),
        "console_errors": session.console_errors,
        "failed_requests": session.failed_requests,
        "page_errors": session.page_errors,
        "observations": observations or {},
        "screenshot": screenshot,
        "verdict": "PASS" if not reasons else "FAIL",
        "reasons": reasons,
        "fault_detected": fault_detected,
        "fault_class": fault_class,
        "ok": not reasons,
    }
    if incomplete and not reasons:
        # An environmental condition the dispatch says is INCOMPLETE, not FAIL
        # (currently: W3 when the vector channel is unavailable at run time) --
        # `derive_qualification` folds this preset into the run-level INCOMPLETE
        # state the same way it already does for a not_implemented_yet stub.
        result["incomplete"] = True
    return result


def _catalog_narrow_check(base_url: str, doc_type: str, param_name: str, facet_values: list, base_total: int
                           ) -> tuple[dict | None, str | None]:
    """W4/W10: try each candidate (value, count) under `param_name`, looking for
    one whose count is below `base_total` (task B7 W4: "each filter narrows
    independently"). Returns (detail, None) on the first value that narrows,
    or (None, reason) if none does or a request failed."""
    for value, count in facet_values:
        if not value or count is None or count >= base_total:
            continue
        qs = urllib.parse.urlencode({"doc_type": doc_type, param_name: value})
        status, body, err = _http_get_json(base_url, f"/api/catalog?{qs}")
        if err or not body:
            return None, f"/api/catalog?{qs} returned no usable body (status={status}, error={err})"
        new_total = body.get("total")
        if new_total is None or new_total >= base_total:
            return None, f"filtering {param_name}={value!r} did not narrow ({new_total} vs {base_total})"
        return {"param": param_name, "value": value, "facet_count": count, "new_total": new_total}, None
    return None, f"no facet value under {param_name!r} narrows below the base total {base_total}"


# ─── KG / KB1 / KB2 / KB4 / KB5 (fixture) ────────────────────────────────────


def _run_kg(browser, base_url: str, ctx: ProbeContext, out_dir: Path) -> dict:
    del ctx
    spec = PRESET_REGISTRY["KG"]
    session = Session(browser)
    try:
        reasons: list[str] = []
        obs: dict = {}

        # (a) identifier search E000777 -> the EVT card row first.
        session.goto("identifier_evt", f"{base_url}/search?q={urllib.parse.quote(FIXTURE_EVT_IDENTIFIER_QUERY)}&mode=identifier")
        first_row_doc_id = session.attr(".identifier-results > li", "data-doc-id")
        first_card_ref = session.attr(".identifier-results > li .result-card", "data-card-ref")
        obs["identifier_first_doc_id"] = first_row_doc_id
        obs["identifier_first_card_ref"] = first_card_ref
        if first_row_doc_id != FIXTURE_EVT_DOC_ID:
            reasons.append(f"KG(a): identifier search first row doc_id={first_row_doc_id!r}, expected {FIXTURE_EVT_DOC_ID!r}")
        if first_card_ref != FIXTURE_EVT_CARD_REF:
            reasons.append(f"KG(a): identifier search first card_ref={first_card_ref!r}, expected {FIXTURE_EVT_CARD_REF!r}")

        # (b) lexical search "quartz lattice lantern" -> ANL first, line_no 15, excerpt phrase;
        #     page and /api/search agree.
        session.goto("lexical_anl", f"{base_url}/search?q={urllib.parse.quote(FIXTURE_ANL_LEXICAL_QUERY)}&mode=lexical")
        page_first_doc_id = session.attr(".search-results > li", "data-doc-id")
        page_first_rank = session.attr(".search-results > li", "data-rank")
        obs["lexical_page_first_doc_id"] = page_first_doc_id
        obs["lexical_page_first_rank"] = page_first_rank
        if page_first_doc_id != FIXTURE_ANL_DOC_ID or page_first_rank != "1":
            reasons.append(f"KG(b): lexical search page first result doc_id={page_first_doc_id!r} "
                            f"rank={page_first_rank!r}, expected doc_id={FIXTURE_ANL_DOC_ID!r} rank='1'")

        api_status, api_body, api_err = _http_get_json(
            base_url, f"/api/search?q={urllib.parse.quote(FIXTURE_ANL_LEXICAL_QUERY)}&mode=lexical"
        )
        if api_err or not api_body or not api_body.get("results"):
            reasons.append(f"KG(b): /api/search returned no usable results (status={api_status}, error={api_err})")
        else:
            api_first = api_body["results"][0]
            api_evidence = api_first.get("evidence") or {}
            obs["lexical_api_first_doc_id"] = api_first.get("doc_id")
            obs["lexical_api_line_no"] = api_evidence.get("line_no")
            obs["lexical_api_line"] = api_evidence.get("line")
            if api_first.get("doc_id") != FIXTURE_ANL_DOC_ID:
                reasons.append(f"KG(b): /api/search first doc_id={api_first.get('doc_id')!r}, expected {FIXTURE_ANL_DOC_ID!r}")
            if api_evidence.get("line_no") != FIXTURE_ANL_LINE_NO:
                reasons.append(f"KG(b): /api/search line_no={api_evidence.get('line_no')!r}, expected {FIXTURE_ANL_LINE_NO}")
            if FIXTURE_ANL_LEXICAL_QUERY not in (api_evidence.get("line") or ""):
                reasons.append(f"KG(b): /api/search excerpt does not contain the query phrase: {api_evidence.get('line')!r}")

        # (c) reader for the ANL card -> body sha256, no index mismatch, /api/doc lines ==
        #     the file's lines, card panel identity == the fixture card file parsed from disk.
        session.goto("reader_anl", f"{base_url}/doc/{FIXTURE_ANL_CARD_REF}")
        body_sha = session.attr("#document", "data-body-sha256")
        mismatch_attr = session.attr("#card-panel", "data-card-index-mismatch")
        expected_sha = _sha256_file(FIXTURE_ANL_DOC_PATH)
        obs["reader_body_sha256"] = body_sha
        obs["disk_body_sha256"] = expected_sha
        obs["reader_card_index_mismatch"] = mismatch_attr
        if body_sha != expected_sha:
            reasons.append(f"KG(c): data-body-sha256={body_sha!r} != disk sha256 {expected_sha!r}")
        if mismatch_attr != "":
            reasons.append(f"KG(c): data-card-index-mismatch={mismatch_attr!r}, expected '' (no mismatch)")

        api_status2, api_body2, api_err2 = _http_get_json(base_url, f"/api/doc/{FIXTURE_ANL_CARD_REF}")
        if api_err2 or not api_body2:
            reasons.append(f"KG(c): /api/doc returned no usable body (status={api_status2}, error={api_err2})")
        else:
            api_line_texts = [ln.get("text") for ln in (api_body2.get("document") or {}).get("lines", [])]
            disk_lines = _read_lines(FIXTURE_ANL_DOC_PATH)
            if api_line_texts != disk_lines:
                reasons.append("KG(c): /api/doc document.lines does not match the file's lines verbatim")
            parsed_file = _parse_card_yaml_file(FIXTURE_ANL_CARD_PATH)
            identity = parsed_file.get("identity") if isinstance(parsed_file.get("identity"), dict) else {}
            card_panel = api_body2.get("card_panel") or {}
            obs["card_panel_doc_id"] = card_panel.get("doc_id")
            obs["card_panel_title"] = card_panel.get("title")
            obs["card_panel_status"] = card_panel.get("status")
            if card_panel.get("doc_id") != FIXTURE_ANL_DOC_ID:
                reasons.append(f"KG(c): card_panel.doc_id={card_panel.get('doc_id')!r} != {FIXTURE_ANL_DOC_ID!r}")
            if card_panel.get("title") != identity.get("title"):
                reasons.append(f"KG(c): card_panel.title={card_panel.get('title')!r} != "
                                f"file identity.title={identity.get('title')!r}")
            if card_panel.get("status") != identity.get("status"):
                reasons.append(f"KG(c): card_panel.status={card_panel.get('status')!r} != "
                                f"file identity.status={identity.get('status')!r}")

        # (d) Q3 typed-edge-direction (task B10): CMP page -- both campaign_child
        # edges outgoing (to ANL, to HND); page and /api/lineage agree.
        edge_attrs = ["data-relation", "data-edge-from", "data-edge-to", "data-edge-direction"]
        session.goto("lineage_cmp", f"{base_url}/lineage/{FIXTURE_CMP_CARD_REF}")
        cmp_rows = session.attr_dicts(".edge-list li", edge_attrs)
        cmp_campaign_child = [r for r in cmp_rows if r.get("data-relation") == "campaign_child"]
        obs["cmp_campaign_child_rows"] = cmp_campaign_child
        cmp_targets = {r.get("data-edge-to") for r in cmp_campaign_child}
        if cmp_targets != {FIXTURE_ANL_DOC_ID, FIXTURE_HND_DOC_ID}:
            reasons.append(f"KG(d): CMP campaign_child targets={sorted(cmp_targets)!r}, expected "
                            f"{sorted([FIXTURE_ANL_DOC_ID, FIXTURE_HND_DOC_ID])!r}")
        if not all(r.get("data-edge-from") == FIXTURE_CMP_DOC_ID and r.get("data-edge-direction") == "outgoing"
                   for r in cmp_campaign_child):
            reasons.append(f"KG(d): not every CMP campaign_child row is outgoing from the CMP: {cmp_campaign_child!r}")

        cmp_api_status, cmp_api_body, cmp_api_err = _http_get_json(base_url, f"/api/lineage/{FIXTURE_CMP_CARD_REF}")
        if cmp_api_err or not cmp_api_body:
            reasons.append(f"KG(d): /api/lineage(CMP) returned no usable body (status={cmp_api_status}, error={cmp_api_err})")
        else:
            api_targets = {e.get("to_id") for e in cmp_api_body.get("outgoing") or [] if e.get("relation") == "campaign_child"}
            obs["cmp_api_campaign_child_targets"] = sorted(api_targets)
            if api_targets != cmp_targets:
                reasons.append(f"KG(d): page campaign_child targets {sorted(cmp_targets)!r} != /api/lineage {sorted(api_targets)!r}")

        # (e) amendment page: outgoing amends edge, from=amendment's own filename
        # stem, to=RHACO-HND-20260115-003.
        session.goto("lineage_amendment", f"{base_url}/lineage/{FIXTURE_HND_AMENDMENT_CARD_REF}")
        amend_rows = session.attr_dicts(".edge-list li", edge_attrs)
        amends_row = next((r for r in amend_rows
                            if r.get("data-relation") == "amends" and r.get("data-edge-direction") == "outgoing"), None)
        obs["amendment_outgoing_amends_row"] = amends_row
        if amends_row is None or amends_row.get("data-edge-from") != FIXTURE_AMENDMENT_STEM \
                or amends_row.get("data-edge-to") != FIXTURE_HND_DOC_ID:
            reasons.append(f"KG(e): amendment page's outgoing amends row={amends_row!r}, expected "
                            f"from={FIXTURE_AMENDMENT_STEM!r} to={FIXTURE_HND_DOC_ID!r}")

        amend_api_status, amend_api_body, amend_api_err = _http_get_json(base_url, f"/api/lineage/{FIXTURE_HND_AMENDMENT_CARD_REF}")
        if amend_api_err or not amend_api_body:
            reasons.append(f"KG(e): /api/lineage(amendment) returned no usable body (status={amend_api_status}, error={amend_api_err})")
        else:
            api_amends = next((e for e in amend_api_body.get("outgoing") or [] if e.get("relation") == "amends"), None)
            obs["amendment_api_outgoing_amends"] = api_amends
            if api_amends is None or api_amends.get("from_id") != FIXTURE_AMENDMENT_STEM or api_amends.get("to_id") != FIXTURE_HND_DOC_ID:
                reasons.append(f"KG(e): /api/lineage(amendment) outgoing amends={api_amends!r} disagrees with the page")

        # (f) reference v1_0 page: outgoing supersedes to v1_1; chain marks v1_1
        # head; superseded banner present.
        session.goto("lineage_ref_v1_0", f"{base_url}/lineage/{FIXTURE_REF_V1_0_CARD_REF}")
        ref_rows = session.attr_dicts(".edge-list li", edge_attrs)
        supersedes_row = next((r for r in ref_rows if r.get("data-relation") == "supersedes"), None)
        obs["ref_v1_0_supersedes_row"] = supersedes_row
        if supersedes_row is None or supersedes_row.get("data-edge-to") != FIXTURE_REF_V1_1_DOC_ID \
                or supersedes_row.get("data-edge-direction") != "outgoing":
            reasons.append(f"KG(f): reference v1_0 supersedes row={supersedes_row!r}, expected "
                            f"to={FIXTURE_REF_V1_1_DOC_ID!r} direction=outgoing")

        chain_rows = session.attr_dicts(".supersession-chain li", ["data-doc-id", "data-chain-head"])
        obs["ref_v1_0_chain"] = chain_rows
        head_row = next((r for r in chain_rows if r.get("data-chain-head") == "true"), None)
        if head_row is None or head_row.get("data-doc-id") != FIXTURE_REF_V1_1_DOC_ID:
            reasons.append(f"KG(f): supersession chain head={head_row!r}, expected doc-id={FIXTURE_REF_V1_1_DOC_ID!r}")

        banner_present = session.count("[data-superseded-banner]") > 0
        obs["ref_v1_0_banner_present"] = banner_present
        if not banner_present:
            reasons.append("KG(f): reference v1_0's own page does not carry the superseded banner")

        ref_api_status, ref_api_body, ref_api_err = _http_get_json(base_url, f"/api/lineage/{FIXTURE_REF_V1_0_CARD_REF}")
        if ref_api_err or not ref_api_body:
            reasons.append(f"KG(f): /api/lineage(reference v1_0) returned no usable body (status={ref_api_status}, error={ref_api_err})")
        else:
            api_supersedes = next((e for e in ref_api_body.get("outgoing") or [] if e.get("relation") == "supersedes"), None)
            if api_supersedes is None or api_supersedes.get("to_id") != FIXTURE_REF_V1_1_DOC_ID:
                reasons.append(f"KG(f): /api/lineage(reference v1_0) outgoing supersedes={api_supersedes!r} disagrees with the page")
            chain_ids = [(c.get("card") or {}).get("doc_id") for c in ref_api_body.get("chain") or []]
            if FIXTURE_REF_V1_1_DOC_ID not in chain_ids:
                reasons.append(f"KG(f): /api/lineage(reference v1_0) chain doc_ids={chain_ids!r} does not include the head")
            if not ref_api_body.get("superseded_banner"):
                reasons.append("KG(f): /api/lineage(reference v1_0) superseded_banner is falsy")

        # (g) HND page: unresolved cites to the deliberately-absent id.
        session.goto("lineage_hnd", f"{base_url}/lineage/{FIXTURE_HND_CARD_REF}")
        hnd_rows = session.attr_dicts(".edge-list li", edge_attrs)
        unresolved_row = next((r for r in hnd_rows
                                if r.get("data-relation") == "cites" and r.get("data-edge-direction") == "unresolved"), None)
        obs["hnd_unresolved_cites_row"] = unresolved_row
        unresolved_marker_present = session.count(".edge-list li .degradation[role='note']") > 0
        obs["hnd_unresolved_marker_present"] = unresolved_marker_present
        if unresolved_row is None or unresolved_row.get("data-edge-to") != FIXTURE_UNRESOLVED_TARGET:
            reasons.append(f"KG(g): HND unresolved cites row={unresolved_row!r}, expected to={FIXTURE_UNRESOLVED_TARGET!r}")
        if not unresolved_marker_present:
            reasons.append("KG(g): HND page does not render the unresolved marker")

        hnd_api_status, hnd_api_body, hnd_api_err = _http_get_json(base_url, f"/api/lineage/{FIXTURE_HND_CARD_REF}")
        if hnd_api_err or not hnd_api_body:
            reasons.append(f"KG(g): /api/lineage(HND) returned no usable body (status={hnd_api_status}, error={hnd_api_err})")
        else:
            api_unresolved = next((e for e in hnd_api_body.get("unresolved") or [] if e.get("relation") == "cites"), None)
            if api_unresolved is None or api_unresolved.get("to_id") != FIXTURE_UNRESOLVED_TARGET:
                reasons.append(f"KG(g): /api/lineage(HND) unresolved cites={api_unresolved!r} disagrees with the page")

        return _finish_workflow(spec, session, out_dir, custom_reasons=reasons, observations=obs, screenshot_name="KG")
    finally:
        session.close()


def _run_kb1(browser, base_url: str, ctx: ProbeContext, out_dir: Path) -> dict:
    del ctx
    spec = PRESET_REGISTRY["KB1"]
    session = Session(browser)
    try:
        obs: dict = {
            "detection_observable": "search identifier result's first .result-card data-card-ref attribute",
            "expected_correct_first_card_ref": FIXTURE_HND_CARD_REF,
            "expected_fault_first_card_ref": FIXTURE_HND_AMENDMENT_CARD_REF,
        }
        session.goto("identifier_hnd", f"{base_url}/search?q={urllib.parse.quote(FIXTURE_HND_IDENTIFIER_QUERY)}&mode=identifier")
        observed_first_ref = session.attr(".identifier-results > li .result-card", "data-card-ref")
        obs["observed_first_card_ref"] = observed_first_ref

        # informational, per the dispatch: "also the reader for the hand's card_ref:
        # its depends_on links / lineage may resolve to the rotated row."
        session.goto("reader_hnd", f"{base_url}/doc/{FIXTURE_HND_CARD_REF}")
        obs["reader_selected_doc_id"] = session.attr("#document", "data-selected-doc-id")

        custom_reasons, fault_detected, fault_class = _kb1_verdict(
            observed_first_ref, FIXTURE_HND_CARD_REF, FIXTURE_HND_AMENDMENT_CARD_REF
        )
        return _finish_workflow(spec, session, out_dir, custom_reasons=custom_reasons,
                                 fault_detected=fault_detected, fault_class=fault_class,
                                 observations=obs, screenshot_name="KB1")
    finally:
        session.close()


def _run_kb2(browser, base_url: str, ctx: ProbeContext, out_dir: Path) -> dict:
    del ctx
    spec = PRESET_REGISTRY["KB2"]
    session = Session(browser)
    try:
        obs: dict = {
            "observable_page": "#card-panel data-card-index-mismatch attribute",
            "observable_independent": "probe's own file read (identity.title/status) vs /api/doc card_row.title/status",
        }
        session.goto("reader_anl", f"{base_url}/doc/{FIXTURE_ANL_CARD_REF}")
        mismatch_attr = session.attr("#card-panel", "data-card-index-mismatch")
        obs["page_card_index_mismatch"] = mismatch_attr

        parsed_file = _parse_card_yaml_file(FIXTURE_ANL_CARD_PATH)
        identity = parsed_file.get("identity") if isinstance(parsed_file.get("identity"), dict) else {}
        file_title, file_status = identity.get("title"), identity.get("status")
        obs["file_title"], obs["file_status"] = file_title, file_status

        api_status, api_body, api_err = _http_get_json(base_url, f"/api/doc/{FIXTURE_ANL_CARD_REF}")
        custom_reasons: list[str]
        fault_detected = False
        fault_class: str | None = None
        if api_err or not api_body:
            custom_reasons = [f"KB2: /api/doc returned no usable body (status={api_status}, error={api_err})"]
        else:
            card_row = api_body.get("card_row") or {}
            indexed_title, indexed_status = card_row.get("title"), card_row.get("status")
            obs["indexed_title"], obs["indexed_status"] = indexed_title, indexed_status
            custom_reasons, fault_detected, fault_class = _kb2_verdict(
                mismatch_attr, file_title, file_status, indexed_title, indexed_status
            )
        return _finish_workflow(spec, session, out_dir, custom_reasons=custom_reasons,
                                 fault_detected=fault_detected, fault_class=fault_class,
                                 observations=obs, screenshot_name="KB2")
    finally:
        session.close()


def _run_kb3(browser, base_url: str, ctx: ProbeContext, out_dir: Path) -> dict:
    """KB3 / reverse_edges (task B10, Q3). Drives the CMP fixture center's
    lineage page under the fault, locates the campaign_child edge to the ANL
    fixture card in BOTH the `.edge-list` row and the graph `<line>`, cross-
    checks the two against each other and against `/api/lineage`, then hands
    the observed `(from_id, to_id, direction)` triple to `_kb3_verdict`
    against the frozen known-correct fixture fact (outgoing, CMP -> ANL) and
    its known-fault swap (incoming, ANL -> CMP)."""
    del ctx
    spec = PRESET_REGISTRY["KB3"]
    session = Session(browser)
    try:
        expected_correct = (FIXTURE_CMP_DOC_ID, FIXTURE_ANL_DOC_ID, "outgoing")
        expected_fault = (FIXTURE_ANL_DOC_ID, FIXTURE_CMP_DOC_ID, "incoming")
        obs: dict = {
            "detection_observable": "the CMP center's campaign_child edge to the ANL fixture card: the "
                                     ".edge-list <li> and the graph <line>'s data-edge-from/data-edge-to/"
                                     "data-edge-direction, cross-checked against each other and against "
                                     "/api/lineage, against the frozen known-correct fixture fact",
            "expected_correct_triple": list(expected_correct),
            "expected_fault_triple": list(expected_fault),
        }
        custom_reasons: list[str] = []
        fault_detected = False
        fault_class: str | None = None

        session.goto("lineage_cmp", f"{base_url}/lineage/{FIXTURE_CMP_CARD_REF}")

        def _find_campaign_child_to_anl(rows: list[dict], from_key: str, to_key: str) -> dict | None:
            return next(
                (r for r in rows
                 if r.get("data-relation") == "campaign_child"
                 and FIXTURE_ANL_DOC_ID in (r.get(from_key), r.get(to_key))),
                None,
            )

        list_rows = session.attr_dicts(
            ".edge-list li", ["data-relation", "data-edge-from", "data-edge-to", "data-edge-direction"]
        )
        list_row = _find_campaign_child_to_anl(list_rows, "data-edge-from", "data-edge-to")
        obs["edge_list_row"] = list_row

        graph_lines = session.attr_dicts(
            ".lineage-graph line", ["data-relation", "data-edge-from", "data-edge-to", "data-edge-direction"]
        )
        graph_line = _find_campaign_child_to_anl(graph_lines, "data-edge-from", "data-edge-to")
        obs["graph_line"] = graph_line

        api_status, api_body, api_err = _http_get_json(base_url, f"/api/lineage/{FIXTURE_CMP_CARD_REF}")
        api_edge = None
        if api_err or not api_body:
            custom_reasons.append(f"KB3: /api/lineage returned no usable body (status={api_status}, error={api_err})")
        else:
            for bucket in ("outgoing", "incoming", "unresolved"):
                api_edge = next(
                    (e for e in api_body.get(bucket) or []
                     if e.get("relation") == "campaign_child" and FIXTURE_ANL_DOC_ID in (e.get("from_id"), e.get("to_id"))),
                    None,
                )
                if api_edge:
                    break
        obs["api_edge"] = api_edge

        if list_row is None or graph_line is None:
            custom_reasons.append(
                "KB3: could not locate the CMP<->ANL campaign_child edge in both the .edge-list rows "
                f"and the graph <line> elements (list_row={list_row!r}, graph_line={graph_line!r})"
            )
            observed = (None, None, None)
        else:
            list_triple = (list_row.get("data-edge-from"), list_row.get("data-edge-to"), list_row.get("data-edge-direction"))
            graph_triple = (graph_line.get("data-edge-from"), graph_line.get("data-edge-to"), graph_line.get("data-edge-direction"))
            if list_triple != graph_triple:
                custom_reasons.append(f"KB3: edge-list row and graph <line> disagree: list={list_triple} line={graph_triple}")
            if api_edge is not None:
                api_triple = (api_edge.get("from_id"), api_edge.get("to_id"), api_edge.get("direction"))
                if api_triple != list_triple:
                    custom_reasons.append(f"KB3: page edge-list and /api/lineage disagree: page={list_triple} api={api_triple}")
            observed = list_triple
        obs["observed_triple"] = list(observed)

        verdict_reasons, fault_detected, fault_class = _kb3_verdict(observed, expected_correct, expected_fault)
        custom_reasons.extend(verdict_reasons)

        return _finish_workflow(spec, session, out_dir, custom_reasons=custom_reasons,
                                 fault_detected=fault_detected, fault_class=fault_class,
                                 observations=obs, screenshot_name="KB3")
    finally:
        session.close()


def _run_kb4(browser, base_url: str, ctx: ProbeContext, out_dir: Path) -> dict:
    del ctx
    spec = PRESET_REGISTRY["KB4"]
    session = Session(browser)
    try:
        obs: dict = {
            "observable_page": ".toc li[data-line-verified] -- any value 'false'",
            "observable_independent": "for each /api/doc heading, lines[line_no-1] must begin a "
                                       "matching ATX heading marker (re-derived independently, never "
                                       "trusting the app's own line_verified claim)",
        }
        session.goto("reader_anl", f"{base_url}/doc/{FIXTURE_ANL_CARD_REF}")
        page_any_unverified = session.count('.toc li[data-line-verified="false"]') > 0
        obs["page_any_heading_unverified"] = page_any_unverified

        api_status, api_body, api_err = _http_get_json(base_url, f"/api/doc/{FIXTURE_ANL_CARD_REF}")
        custom_reasons: list[str]
        fault_detected = False
        fault_class: str | None = None
        if api_err or not api_body:
            custom_reasons = [f"KB4: /api/doc returned no usable body (status={api_status}, error={api_err})"]
        else:
            document = api_body.get("document") or {}
            headings = document.get("headings") or []
            line_texts = [ln.get("text", "") for ln in document.get("lines") or []]
            mismatches = [
                h for h in headings
                if not _verify_heading_independently(line_texts, h.get("line_no", -1), h.get("text", ""))
            ]
            obs["independent_mismatch_count"] = len(mismatches)
            obs["independent_mismatches"] = mismatches
            custom_reasons, fault_detected, fault_class = _kb4_verdict(page_any_unverified, len(mismatches))
        return _finish_workflow(spec, session, out_dir, custom_reasons=custom_reasons,
                                 fault_detected=fault_detected, fault_class=fault_class,
                                 observations=obs, screenshot_name="KB4")
    finally:
        session.close()


def _run_kb5(browser, base_url: str, ctx: ProbeContext, out_dir: Path) -> dict:
    del ctx
    spec = PRESET_REGISTRY["KB5"]
    session = Session(browser)
    try:
        session.goto("diagnostics", f"{base_url}/diagnostics")
        session.goto("catalog_home", f"{base_url}/")
        session.goto("search_lexical", f"{base_url}/search?q={urllib.parse.quote(FIXTURE_ANL_LEXICAL_QUERY)}&mode=lexical")
        session.goto("reader_anl", f"{base_url}/doc/{FIXTURE_ANL_CARD_REF}")

        obs = {
            "steps_visited": ["diagnostics", "catalog_home", "search_lexical", "reader_anl"],
            "observable": "diagnostics step's own console/pageerror text (fault-attributed via "
                           "FAULT_TEXT_MARKERS); catalog/search/reader are clean control navigations "
                           "on the same wave-2 surfaces, expected to show no console error of their own",
            "diagnostics_console_error_count": len([e for e in session.console_errors if e["step"] == "diagnostics"]),
            "other_steps_console_error_count": len([e for e in session.console_errors if e["step"] != "diagnostics"]),
        }
        # No custom reasons of its own: KB5's whole point is that the SAME generic
        # console-error rule in `_collect_basic_reasons`, applied across a composite
        # multi-page run, flags the diagnostics step and leaves the others alone.
        return _finish_workflow(spec, session, out_dir, observations=obs, screenshot_name="KB5")
    finally:
        session.close()


# ─── W1-W4, W7, W9, W10 (production), W8 (fixture, its own server) ──────────


def _run_w1(browser, base_url: str, ctx: ProbeContext, out_dir: Path) -> dict:
    del ctx
    spec = PRESET_REGISTRY["W1"]
    session = Session(browser)
    try:
        obs: dict = {}
        custom_reasons: list[str] = []
        q = PRODUCT_W1_QUERY

        session.goto("identifier_search", f"{base_url}/search?q={urllib.parse.quote(q)}&mode=identifier")
        matching_count = session.count(f'.identifier-results > li[data-doc-id="{q}"]')
        obs["identifier_row_count_for_query_id"] = matching_count
        if matching_count != 1:
            custom_reasons.append(f"W1: expected exactly one identifier result row with data-doc-id={q!r}, found {matching_count}")

        open_link = session.attr(f'.identifier-results > li[data-doc-id="{q}"] .result-card a', "href")
        obs["open_link"] = open_link
        if not open_link:
            custom_reasons.append("W1: could not find an open link for the identifier result")
        else:
            session.goto("reader", base_url + open_link)
            selected = session.attr("#document", "data-selected-doc-id")
            obs["reader_selected_doc_id"] = selected
            if selected != q:
                custom_reasons.append(f"W1: reader data-selected-doc-id={selected!r}, expected {q!r}")

            api_status, api_body, api_err = _http_get_json(base_url, _api_doc_path(open_link))
            if api_err or not api_body:
                custom_reasons.append(f"W1: /api/doc returned no usable body (status={api_status}, error={api_err})")
            else:
                card_panel = api_body.get("card_panel") or {}
                obs["api_doc_id"] = api_body.get("doc_id")
                obs["api_doc_type"] = card_panel.get("doc_type")
                obs["api_lifecycle_value"] = card_panel.get("lifecycle_value")
                if api_body.get("doc_id") != q:
                    custom_reasons.append(f"W1: /api/doc doc_id={api_body.get('doc_id')!r} != {q!r}")
                if selected != api_body.get("doc_id"):
                    custom_reasons.append("W1: page data-selected-doc-id and /api/doc doc_id disagree")
                if (card_panel.get("doc_type") or "").upper() != "CMP":
                    custom_reasons.append(f"W1: card_panel.doc_type={card_panel.get('doc_type')!r}, expected CMP")
                if not card_panel.get("lifecycle_value"):
                    custom_reasons.append("W1: card_panel.lifecycle_value is empty; expected a CMP lifecycle state present")
        return _finish_workflow(spec, session, out_dir, custom_reasons=custom_reasons, observations=obs, screenshot_name="W1")
    finally:
        session.close()


def _run_w2(browser, base_url: str, ctx: ProbeContext, out_dir: Path) -> dict:
    del ctx
    spec = PRESET_REGISTRY["W2"]
    session = Session(browser)
    try:
        obs: dict = {}
        custom_reasons: list[str] = []
        q = PRODUCT_W2_QUERY

        session.goto("lexical_search", f"{base_url}/search?q={urllib.parse.quote(q)}&mode=lexical")
        page_doc_ids = session.attr_all(".search-results > li", "data-doc-id")
        obs["page_result_doc_ids"] = page_doc_ids

        api_status, api_body, api_err = _http_get_json(base_url, f"/api/search?q={urllib.parse.quote(q)}&mode=lexical")
        if api_err or not api_body:
            custom_reasons.append(f"W2: /api/search returned no usable body (status={api_status}, error={api_err})")
            return _finish_workflow(spec, session, out_dir, custom_reasons=custom_reasons, observations=obs, screenshot_name="W2")

        target_item = next((it for it in api_body.get("results", []) if it.get("doc_id") == PRODUCT_W2_TARGET_DOC_ID), None)
        obs["target_found_in_results"] = target_item is not None
        if target_item is None:
            custom_reasons.append(f"W2: target {PRODUCT_W2_TARGET_DOC_ID!r} not among /api/search results for {q!r}")
            return _finish_workflow(spec, session, out_dir, custom_reasons=custom_reasons, observations=obs, screenshot_name="W2")

        if PRODUCT_W2_TARGET_DOC_ID not in page_doc_ids:
            custom_reasons.append("W2: target present via /api/search but not in the page's own search-results DOM")

        evidence = target_item.get("evidence") or {}
        line_no = evidence.get("line_no")
        excerpt = evidence.get("line")
        target_path = target_item.get("path")
        obs["target_line_no"], obs["target_excerpt"], obs["target_path"] = line_no, excerpt, target_path

        if not target_path or not os.path.isfile(target_path):
            custom_reasons.append(f"W2: result path {target_path!r} does not exist on disk")
        elif line_no is None:
            custom_reasons.append("W2: result evidence carries no line_no")
        else:
            disk_lines = _read_lines(target_path)
            obs["disk_line_count"] = len(disk_lines)
            if not (1 <= line_no <= len(disk_lines)):
                custom_reasons.append(f"W2: line_no {line_no} out of range for {target_path!r} ({len(disk_lines)} lines)")
            else:
                disk_line_text = disk_lines[line_no - 1]
                obs["disk_line_text"] = disk_line_text
                if disk_line_text != excerpt:
                    custom_reasons.append(
                        f"W2: excerpt does not match the file's line {line_no} verbatim: "
                        f"excerpt={excerpt!r} disk={disk_line_text!r}"
                    )
        return _finish_workflow(spec, session, out_dir, custom_reasons=custom_reasons, observations=obs, screenshot_name="W2")
    finally:
        session.close()


def _run_w3(browser, base_url: str, ctx: ProbeContext, out_dir: Path) -> dict:
    del ctx
    spec = PRESET_REGISTRY["W3"]
    session = Session(browser)
    try:
        obs: dict = {}
        custom_reasons: list[str] = []
        incomplete = False
        q = PRODUCT_W3_QUERY

        session.goto("hybrid_search", f"{base_url}/search?q={urllib.parse.quote(q)}&mode=hybrid&top_k={PRODUCT_W3_TOP_K}")
        html_mode = session.html_attr("data-mode")
        html_vector = session.html_attr("data-vector")
        obs["html_data_mode"], obs["html_data_vector"] = html_mode, html_vector

        if html_vector != "available":
            incomplete = True
            obs["incomplete_reason"] = (
                f"vector channel unavailable on this host at run time (data-vector={html_vector!r}); "
                "W3 recorded as INCOMPLETE per the dispatch, not FAIL"
            )
        else:
            if html_mode != "hybrid":
                custom_reasons.append(f"W3: data-mode={html_mode!r}, expected 'hybrid'")
            api_status, api_body, api_err = _http_get_json(
                base_url, f"/api/search?q={urllib.parse.quote(q)}&mode=hybrid&top_k={PRODUCT_W3_TOP_K}"
            )
            if api_err or not api_body:
                custom_reasons.append(f"W3: /api/search returned no usable body (status={api_status}, error={api_err})")
            else:
                results = api_body.get("results", [])
                returned_ids = [item.get("doc_id") for item in results]
                obs["returned_ids"] = returned_ids
                obs["oracle_order"] = list(PRODUCT_W3_ORACLE_ORDER)
                if PRODUCT_W3_TARGET_DOC_ID not in returned_ids:
                    custom_reasons.append(f"W3: target {PRODUCT_W3_TARGET_DOC_ID!r} not among returned ids {returned_ids}")
                if returned_ids != list(PRODUCT_W3_ORACLE_ORDER):
                    custom_reasons.append(
                        "W3: returned id order does not match the L4 oracle's recorded order "
                        f"(gold_v1_1_compat.json row 21): observed={returned_ids} oracle={list(PRODUCT_W3_ORACLE_ORDER)}"
                    )
                for item in results:
                    comp_rank = (item.get("evidence") or {}).get("component_rank")
                    if comp_rank != COMPONENT_RANK_NOT_EXPOSED:
                        custom_reasons.append(
                            f"W3: result {item.get('doc_id')!r} evidence.component_rank={comp_rank!r}, "
                            f"expected {COMPONENT_RANK_NOT_EXPOSED!r}"
                        )
        return _finish_workflow(spec, session, out_dir, custom_reasons=custom_reasons, observations=obs,
                                 screenshot_name="W3", incomplete=incomplete)
    finally:
        session.close()


def _run_w4(browser, base_url: str, ctx: ProbeContext, out_dir: Path) -> dict:
    del ctx
    spec = PRESET_REGISTRY["W4"]
    session = Session(browser)
    try:
        obs: dict = {}
        custom_reasons: list[str] = []

        session.goto("catalog_cmp", f"{base_url}/?doc_type={PRODUCT_W4_DOC_TYPE}")
        row_count = session.count("tr[data-doc-id]")
        status_attrs = session.attr_all("tr[data-doc-id]", "data-status")
        lifecycle_attrs = session.attr_all("tr[data-doc-id]", "data-lifecycle-state")
        lifecycle_control_present = session.count('[data-lifecycle-control="shown"]') > 0
        obs.update(row_count=row_count, lifecycle_control_present=lifecycle_control_present)

        if row_count == 0:
            custom_reasons.append(f"W4: no rows for doc_type={PRODUCT_W4_DOC_TYPE!r}")
        if len(status_attrs) != row_count or any(v is None for v in status_attrs):
            custom_reasons.append("W4: not every row carries a data-status attribute")
        if len(lifecycle_attrs) != row_count or any(v is None for v in lifecycle_attrs):
            custom_reasons.append("W4: not every row carries a data-lifecycle-state attribute")
        if not lifecycle_control_present:
            custom_reasons.append("W4: the lifecycle_state filter control is not rendered for CMP")
        for s_val, l_val in zip(status_attrs, lifecycle_attrs, strict=False):
            if l_val and s_val and l_val in s_val:
                custom_reasons.append(f"W4: lifecycle_state value {l_val!r} appears inside the status attribute {s_val!r}")

        api_status, api_body, api_err = _http_get_json(base_url, f"/api/catalog?doc_type={PRODUCT_W4_DOC_TYPE}")
        if api_err or not api_body:
            custom_reasons.append(f"W4: /api/catalog returned no usable body (status={api_status}, error={api_err})")
        else:
            base_total = api_body.get("total")
            obs["base_total"] = base_total
            facets = api_body.get("facets") or {}
            lc_detail, lc_err = _catalog_narrow_check(base_url, PRODUCT_W4_DOC_TYPE, "lifecycle_state",
                                                       facets.get("lifecycle_states") or [], base_total)
            obs["lifecycle_state_narrow"] = lc_detail
            if lc_err:
                custom_reasons.append(f"W4: {lc_err}")
            st_detail, st_err = _catalog_narrow_check(base_url, PRODUCT_W4_DOC_TYPE, "status",
                                                        facets.get("statuses") or [], base_total)
            obs["status_narrow"] = st_detail
            if st_err:
                custom_reasons.append(f"W4: {st_err}")
        return _finish_workflow(spec, session, out_dir, custom_reasons=custom_reasons, observations=obs, screenshot_name="W4")
    finally:
        session.close()


def _run_w5(browser, base_url: str, ctx: ProbeContext, out_dir: Path) -> dict:
    """W5 -- reasoning lineage (production, task B10). Centers on this build's
    own campaign, RHACO-CMP-20260903-001: typed directional edges, every
    edge's direction_label checked against explorer.models.RELATION_LABELS,
    the reasoning trail's chronological order, page/API edge-set parity, and
    an independent read of two production .card.yaml files off disk
    confirming the rendered campaign_child relation is actually declared
    there (never through the index)."""
    spec = PRESET_REGISTRY["W5"]
    session = Session(browser)
    try:
        obs: dict = {}
        custom_reasons: list[str] = []
        edge_attrs = ["data-relation", "data-edge-from", "data-edge-to", "data-edge-direction"]

        session.goto("lineage_cmp", f"{base_url}/lineage/{PRODUCT_W5_CMP_CARD_REF}")
        page_rows = session.attr_dicts(".edge-list li", edge_attrs)
        page_edges = {
            (r.get("data-relation"), r.get("data-edge-from"), r.get("data-edge-to"), r.get("data-edge-direction"))
            for r in page_rows
        }
        obs["page_edge_count"] = len(page_edges)

        page_campaign_child_targets = {
            r.get("data-edge-to") for r in page_rows
            if r.get("data-relation") == "campaign_child" and r.get("data-edge-direction") == "outgoing"
        }
        obs["page_campaign_child_outgoing_targets"] = sorted(page_campaign_child_targets)
        if not page_campaign_child_targets:
            custom_reasons.append("W5: no outgoing campaign_child edge rendered on the CMP's own lineage page")
        for child_doc_id, _card_ref, _dep in PRODUCT_W5_INDEPENDENT_CHECKS:
            if child_doc_id not in page_campaign_child_targets:
                custom_reasons.append(
                    f"W5: expected an outgoing campaign_child edge to {child_doc_id!r} on the page, "
                    f"observed targets={sorted(page_campaign_child_targets)!r}"
                )

        api_status, api_body, api_err = _http_get_json(base_url, f"/api/lineage/{PRODUCT_W5_CMP_CARD_REF}")
        if api_err or not api_body:
            custom_reasons.append(f"W5: /api/lineage returned no usable body (status={api_status}, error={api_err})")
        else:
            all_api_edges = [
                (e.get("relation"), e.get("from_id"), e.get("to_id"), e.get("direction"), e.get("direction_label"))
                for bucket in ("outgoing", "incoming", "unresolved")
                for e in api_body.get(bucket) or []
            ]
            obs["api_edge_count"] = len(all_api_edges)

            api_edge_triples = {(rel, frm, to, direc) for rel, frm, to, direc, _label in all_api_edges}
            if api_edge_triples != page_edges:
                custom_reasons.append(
                    f"W5: page edge-list set != /api/lineage edge set (page-only={sorted(page_edges - api_edge_triples)!r}, "
                    f"api-only={sorted(api_edge_triples - page_edges)!r})"
                )

            mismatched_labels = sorted({
                (rel, direc, label) for rel, _frm, _to, direc, label in all_api_edges
                if label != RELATION_LABELS.get(rel, rel)
            })
            obs["mismatched_direction_labels"] = mismatched_labels
            if mismatched_labels:
                custom_reasons.append(f"W5: direction_label does not match RELATION_LABELS for {mismatched_labels!r}")

            api_campaign_child_targets = {
                e.get("to_id") for e in api_body.get("outgoing") or [] if e.get("relation") == "campaign_child"
            }
            if api_campaign_child_targets != page_campaign_child_targets:
                custom_reasons.append(
                    f"W5: page campaign_child outgoing targets {sorted(page_campaign_child_targets)!r} != "
                    f"/api/lineage {sorted(api_campaign_child_targets)!r}"
                )

            trail = api_body.get("reasoning_trail") or []
            trail_dates = [(e.get("card") or {}).get("date") for e in trail]
            obs["reasoning_trail_dates"] = trail_dates
            sortable = [(d is None, d or "") for d in trail_dates]
            if sortable != sorted(sortable):
                custom_reasons.append(f"W5: reasoning_trail is not chronological (dates observed: {trail_dates!r})")

        # Independent check (task 3): for at least two resolved edges, read the
        # relevant .card.yaml from C:\RHACO\docs directly and confirm the
        # rendered campaign_child relation is actually declared there. Never
        # opens the index; a missing correspondence is UNVERIFIED, never a
        # FAIL (task instruction: "not inventing a correspondence").
        independent_checks = []
        for child_doc_id, child_card_ref, expected_dep_id in PRODUCT_W5_INDEPENDENT_CHECKS:
            abs_path = os.path.join(ctx.docs_root, child_card_ref.replace("/", os.sep))
            if not os.path.isfile(abs_path):
                independent_checks.append({
                    "child_doc_id": child_doc_id, "status": "UNVERIFIED",
                    "reason": f"card file not found on disk: {abs_path!r}",
                })
                continue
            parsed = _parse_card_yaml_file(abs_path)
            dep_ids = [d.get("id") for d in (parsed.get("depends_on") or []) if isinstance(d, dict)]
            if expected_dep_id in dep_ids:
                independent_checks.append({
                    "child_doc_id": child_doc_id, "status": "VERIFIED",
                    "detail": f"card.yaml depends_on declares {expected_dep_id!r} on disk, backing the "
                              "rendered campaign_child edge",
                })
            else:
                independent_checks.append({
                    "child_doc_id": child_doc_id, "status": "UNVERIFIED",
                    "reason": f"card.yaml depends_on={dep_ids!r} does not name {expected_dep_id!r}",
                })
        obs["independent_checks"] = independent_checks

        return _finish_workflow(spec, session, out_dir, custom_reasons=custom_reasons, observations=obs, screenshot_name="W5")
    finally:
        session.close()


def _run_w6(browser, base_url: str, ctx: ProbeContext, out_dir: Path) -> dict:
    """W6 -- supersession and amendment (production, task B10). (a) Card Schema
    v1.8 (Superseded) -> v1.9 (current head): banner, chain, the historical
    v1.8 document still openable through the reader, the replacement edge.
    (b) this build's own A1 amendment: its outgoing amends edge, resolved and
    linked. The parent's own incoming amends edge is recorded against
    SCOPE.md row 17 (`W6_KNOWN_LIMITATION`) -- present/typed/directional/
    resolved is asserted; the missing click-through is NEVER a FAIL, only
    disclosed."""
    del ctx
    spec = PRESET_REGISTRY["W6"]
    session = Session(browser)
    try:
        obs: dict = {}
        custom_reasons: list[str] = []
        edge_attrs = ["data-relation", "data-edge-from", "data-edge-to", "data-edge-direction"]

        # (a) Supersession.
        session.goto("lineage_v1_8", f"{base_url}/lineage/{PRODUCT_W6_SUPERSEDED_CARD_REF}")
        banner_present = session.count("[data-superseded-banner]") > 0
        obs["v1_8_banner_present"] = banner_present
        if not banner_present:
            custom_reasons.append("W6(a): v1_8's own lineage page does not carry the superseded banner")

        chain_rows = session.attr_dicts(".supersession-chain li", ["data-doc-id", "data-chain-head", "$text"])
        obs["v1_8_chain"] = chain_rows
        head_row = next((r for r in chain_rows if r.get("data-chain-head") == "true"), None)
        if head_row is None or head_row.get("data-doc-id") != PRODUCT_W6_HEAD_DOC_ID:
            custom_reasons.append(f"W6(a): supersession chain head={head_row!r}, expected doc-id={PRODUCT_W6_HEAD_DOC_ID!r}")
        elif "current head" not in (head_row.get("$text") or ""):
            custom_reasons.append(f"W6(a): chain head row text {head_row.get('$text')!r} does not contain 'current head'")

        v8_edges = session.attr_dicts(".edge-list li", edge_attrs)
        supersedes_edge = next((r for r in v8_edges if r.get("data-relation") == "supersedes"), None)
        obs["v1_8_supersedes_edge"] = supersedes_edge
        if supersedes_edge is None or supersedes_edge.get("data-edge-to") != PRODUCT_W6_HEAD_DOC_ID \
                or supersedes_edge.get("data-edge-direction") != "outgoing":
            custom_reasons.append(f"W6(a): v1_8 outgoing supersedes edge={supersedes_edge!r}, expected to={PRODUCT_W6_HEAD_DOC_ID!r}")

        # The historical v1_8 document itself remains openable and readable
        # through the reader (PROMPT.md W6: the historical artifact remains visible).
        session.goto("reader_v1_8", f"{base_url}/doc/{PRODUCT_W6_SUPERSEDED_CARD_REF}")
        v8_selected = session.attr("#document", "data-selected-doc-id")
        obs["v1_8_reader_selected_doc_id"] = v8_selected
        if v8_selected != PRODUCT_W6_SUPERSEDED_DOC_ID:
            custom_reasons.append(f"W6(a): reader for v1_8 data-selected-doc-id={v8_selected!r}, "
                                    f"expected {PRODUCT_W6_SUPERSEDED_DOC_ID!r}")

        v8_api_status, v8_api_body, v8_api_err = _http_get_json(base_url, f"/api/lineage/{PRODUCT_W6_SUPERSEDED_CARD_REF}")
        if v8_api_err or not v8_api_body:
            custom_reasons.append(f"W6(a): /api/lineage(v1_8) returned no usable body (status={v8_api_status}, error={v8_api_err})")
        else:
            api_chain_ids = [(c.get("card") or {}).get("doc_id") for c in v8_api_body.get("chain") or []]
            if PRODUCT_W6_HEAD_DOC_ID not in api_chain_ids:
                custom_reasons.append(f"W6(a): /api/lineage(v1_8) chain doc_ids={api_chain_ids!r} missing the head")
            if not v8_api_body.get("superseded_banner"):
                custom_reasons.append("W6(a): /api/lineage(v1_8) superseded_banner is falsy")

        # (b) Amendment -- outgoing amends edge, resolved and linked.
        session.goto("lineage_amendment", f"{base_url}/lineage/{PRODUCT_W6_AMENDMENT_CARD_REF}")
        amend_edges = session.attr_dicts(".edge-list li", edge_attrs)
        amends_row = next((r for r in amend_edges
                            if r.get("data-relation") == "amends" and r.get("data-edge-direction") == "outgoing"), None)
        obs["amendment_outgoing_amends_row"] = amends_row
        if amends_row is None or amends_row.get("data-edge-to") != PRODUCT_W6_PARENT_DOC_ID:
            custom_reasons.append(f"W6(b): amendment's outgoing amends row={amends_row!r}, "
                                    f"expected to={PRODUCT_W6_PARENT_DOC_ID!r}")

        amend_link = session.attr(
            '.edge-list li[data-relation="amends"][data-edge-direction="outgoing"] a', "href"
        )
        obs["amendment_outgoing_amends_link"] = amend_link
        if not amend_link:
            custom_reasons.append("W6(b): amendment's outgoing amends edge is not rendered as a resolved link")

        amend_api_status, amend_api_body, amend_api_err = _http_get_json(base_url, f"/api/lineage/{PRODUCT_W6_AMENDMENT_CARD_REF}")
        if amend_api_err or not amend_api_body:
            custom_reasons.append(f"W6(b): /api/lineage(amendment) returned no usable body (status={amend_api_status}, error={amend_api_err})")
        else:
            api_amends = next((e for e in amend_api_body.get("outgoing") or [] if e.get("relation") == "amends"), None)
            obs["amendment_api_outgoing_amends"] = api_amends
            if api_amends is None or not api_amends.get("resolved") or api_amends.get("to_id") != PRODUCT_W6_PARENT_DOC_ID:
                custom_reasons.append(f"W6(b): /api/lineage(amendment) outgoing amends={api_amends!r} not "
                                        "resolved/to-parent as expected")

        # Known, dispositioned limitation (SCOPE.md row 17, task 4(b)): visit
        # the PARENT's own page too and record -- never FAIL on -- the incoming
        # amends edge rendering as typed/directional/resolved text with no link.
        session.goto("lineage_parent", f"{base_url}/lineage/{PRODUCT_W6_PARENT_CARD_REF}")
        parent_edges = session.attr_dicts(".edge-list li", edge_attrs)
        parent_incoming_amends = next(
            (r for r in parent_edges if r.get("data-relation") == "amends" and r.get("data-edge-direction") == "incoming"),
            None,
        )
        obs["parent_incoming_amends_row"] = parent_incoming_amends
        parent_link = session.attr('.edge-list li[data-relation="amends"][data-edge-direction="incoming"] a', "href")
        obs["parent_incoming_amends_link"] = parent_link
        obs["known_limitation"] = W6_KNOWN_LIMITATION

        if parent_incoming_amends is None or parent_incoming_amends.get("data-edge-from") != PRODUCT_W6_AMENDMENT_STEM:
            custom_reasons.append(f"W6(b): parent's incoming amends row={parent_incoming_amends!r}, "
                                    f"expected from={PRODUCT_W6_AMENDMENT_STEM!r}")

        parent_api_status, parent_api_body, parent_api_err = _http_get_json(base_url, f"/api/lineage/{PRODUCT_W6_PARENT_CARD_REF}")
        if parent_api_err or not parent_api_body:
            custom_reasons.append(f"W6(b): /api/lineage(parent) returned no usable body (status={parent_api_status}, error={parent_api_err})")
        else:
            api_incoming_amends = next(
                (e for e in parent_api_body.get("incoming") or [] if e.get("relation") == "amends"), None
            )
            obs["parent_api_incoming_amends"] = api_incoming_amends
            if api_incoming_amends is None:
                custom_reasons.append("W6(b): /api/lineage(parent) has no incoming amends edge at all")
            elif not api_incoming_amends.get("resolved"):
                # This WOULD contradict SCOPE.md row 17, which says this edge is
                # resolved (only its click-through is missing) -- a real FAIL.
                custom_reasons.append(
                    f"W6(b): parent's incoming amends edge is marked unresolved (resolved="
                    f"{api_incoming_amends.get('resolved')!r}) -- contradicts SCOPE.md row 17"
                )
        obs["known_limitation_reproduced"] = not bool(parent_link)
        if parent_link:
            obs["known_limitation_note"] = (
                "the amends click-through now resolves to a link -- SCOPE.md row 17 may be stale; "
                "not treated as a FAIL here, filed as a change request instead"
            )

        return _finish_workflow(spec, session, out_dir, custom_reasons=custom_reasons, observations=obs, screenshot_name="W6")
    finally:
        session.close()


def _run_w7(browser, base_url: str, ctx: ProbeContext, out_dir: Path) -> dict:
    del ctx
    spec = PRESET_REGISTRY["W7"]
    session = Session(browser)
    try:
        obs: dict = {}
        custom_reasons: list[str] = []

        session.goto("hybrid_search", f"{base_url}/search?q={urllib.parse.quote(PRODUCT_W2_QUERY)}&mode=hybrid")
        html_mode = session.html_attr("data-mode")
        badge_mode = session.attr(".mode-badge", "data-mode-effective")
        notice_text = (session.text(".degradation[role='status']") or "").strip()
        obs.update(hybrid_html_mode=html_mode, hybrid_badge_mode_effective=badge_mode, degradation_notice_text=notice_text)
        if html_mode != "hybrid-degraded-lexical":
            custom_reasons.append(f"W7: search data-mode={html_mode!r}, expected 'hybrid-degraded-lexical'")
        if badge_mode != "hybrid-degraded-lexical":
            custom_reasons.append(f"W7: mode badge data-mode-effective={badge_mode!r}, expected 'hybrid-degraded-lexical'")
        if badge_mode and "Hybrid (default)" in badge_mode:
            custom_reasons.append("W7: active-mode badge shows the 'Hybrid (default)' label, expected the raw degraded mode")
        if notice_text != HYBRID_DEGRADED_NOTICE_TEXT:
            custom_reasons.append(f"W7: degradation notice text={notice_text!r}, expected {HYBRID_DEGRADED_NOTICE_TEXT!r}")

        session.goto("diagnostics", f"{base_url}/diagnostics")
        diag_mode = session.html_attr("data-mode")
        diag_vector = session.html_attr("data-vector")
        obs.update(diagnostics_mode=diag_mode, diagnostics_vector=diag_vector)
        if diag_mode != "hybrid-degraded-lexical":
            custom_reasons.append(f"W7: diagnostics data-mode={diag_mode!r}, expected 'hybrid-degraded-lexical'")
        if diag_vector != "unavailable":
            custom_reasons.append(f"W7: diagnostics data-vector={diag_vector!r}, expected 'unavailable'")

        _, id_body, id_err = _http_get_json(base_url, f"/api/search?q={urllib.parse.quote(PRODUCT_W1_QUERY)}&mode=identifier")
        obs["identifier_returned"] = bool(id_body and id_body.get("identifier_rows"))
        if id_err or not id_body or not id_body.get("identifier_rows"):
            custom_reasons.append("W7: identifier search returned no results under --disable-vec")

        _, lex_body, lex_err = _http_get_json(base_url, f"/api/search?q={urllib.parse.quote(PRODUCT_W2_QUERY)}&mode=lexical")
        obs["lexical_returned"] = bool(lex_body and lex_body.get("results"))
        if lex_err or not lex_body or not lex_body.get("results"):
            custom_reasons.append("W7: lexical search returned no results under --disable-vec")

        return _finish_workflow(spec, session, out_dir, custom_reasons=custom_reasons, observations=obs, screenshot_name="W7")
    finally:
        session.close()


def _run_w8(browser, base_url: str, ctx: ProbeContext, out_dir: Path) -> dict:
    """W8 drives its OWN dedicated server against a temp copy of fixtures/corpus
    (the run's main --db/--docs-root, i.e. `base_url`, is not used by this
    preset) -- built fresh, then mutated by adding one more card+document
    WITHOUT rebuilding, so freshness must report DRIFT (task B7). Reuses the
    `browser` this run already launched Playwright with; only ONE additional
    uvicorn child is spawned (still via `launch_server`/`terminate_server`,
    the same sanctioned lifecycle `main()` uses, foreground + bounded
    /healthz wait + `finally` teardown)."""
    del base_url
    spec = PRESET_REGISTRY["W8"]
    obs: dict = {}
    custom_reasons: list[str] = []
    tmp_root = Path(tempfile.mkdtemp(prefix="probe_w8_"))
    proc: subprocess.Popen | None = None
    session: Session | None = None
    try:
        docs_copy = tmp_root / "corpus"
        shutil.copytree(FIXTURE_CORPUS_ROOT, docs_copy)
        db_copy = tmp_root / "fixture_index.db"

        from fixtures.build_fixture_index import build as build_fixture_index

        build_summary = build_fixture_index(str(docs_copy), str(db_copy))
        obs["fixture_build_summary"] = build_summary

        drift_card = docs_copy / "reports" / f"{W8_DRIFT_CARD_NAME}.card.yaml"
        drift_doc = docs_copy / "reports" / f"{W8_DRIFT_CARD_NAME}.md"
        drift_card.write_text(W8_DRIFT_CARD_YAML, encoding="utf-8")
        drift_doc.write_text(W8_DRIFT_CARD_MD, encoding="utf-8")
        obs["drift_card_added"] = str(drift_card)

        port = _free_port()
        w8_base = f"http://127.0.0.1:{port}"
        server_log_path = out_dir / "W8_server.log"
        with open(server_log_path, "w", encoding="utf-8", errors="replace") as log_fh:
            proc = launch_server(sys.executable, port, str(db_copy), str(docs_copy), cwd=_WORKSPACE_ROOT, log_file=log_fh)
            wait_for_healthz(w8_base, ctx.timeout_s)

            session = Session(browser)
            session.goto("diagnostics_before", w8_base + "/diagnostics")
            session.click_submit("freshness_submit", "form[action='/diagnostics/freshness'] button[type=submit]")
            status_attr = session.attr("[data-freshness-status]", "data-freshness-status")
            obs["page_freshness_status"] = status_attr
            if status_attr != "DRIFT":
                custom_reasons.append(f"W8: data-freshness-status={status_attr!r}, expected 'DRIFT'")

            api_status, api_body, api_err = _http_get_json(w8_base, "/api/diagnostics?freshness=1")
            if api_err or not api_body:
                custom_reasons.append(f"W8: /api/diagnostics?freshness=1 returned no usable body (status={api_status}, error={api_err})")
            else:
                fresh = api_body.get("freshness") or {}
                added = fresh.get("added") or []
                obs["api_freshness_status"] = fresh.get("status")
                obs["api_freshness_added"] = added
                if fresh.get("status") != "DRIFT":
                    custom_reasons.append(f"W8: api freshness.status={fresh.get('status')!r}, expected 'DRIFT'")
                if not any(str(drift_card) == a or drift_card.name in a for a in added):
                    custom_reasons.append(f"W8: added card {drift_card} not listed in freshness.added={added}")
                if fresh.get("corpus_card_count_index") == fresh.get("corpus_card_count_live"):
                    custom_reasons.append("W8: live/indexed card counts agree -- drift not reflected (and not repaired: unchanged index count)")
                obs["corpus_card_count_index"] = fresh.get("corpus_card_count_index")
                obs["corpus_card_count_live"] = fresh.get("corpus_card_count_live")

            return _finish_workflow(spec, session, out_dir, custom_reasons=custom_reasons, observations=obs, screenshot_name="W8")
    finally:
        if session is not None:
            session.close()
        if proc is not None:
            terminate_server(proc)
        shutil.rmtree(tmp_root, ignore_errors=True)


def _run_w9(browser, base_url: str, ctx: ProbeContext, out_dir: Path) -> dict:
    del ctx
    spec = PRESET_REGISTRY["W9"]
    session = Session(browser)
    try:
        obs: dict = {}
        custom_reasons: list[str] = []
        q = PRODUCT_W2_QUERY

        api_status, api_body, api_err = _http_get_json(base_url, f"/api/search?q={urllib.parse.quote(q)}&mode=lexical")
        if api_err or not api_body:
            custom_reasons.append(f"W9: /api/search returned no usable body (status={api_status}, error={api_err})")
            return _finish_workflow(spec, session, out_dir, custom_reasons=custom_reasons, observations=obs, screenshot_name="W9")

        # The target doc_id can appear at more than one rank (several lexical hits
        # inside the same document); W9 needs one with a resolvable card row to
        # "follow its open link" -- an occurrence with no_card_row renders no link
        # at all on the real search page, so it is skipped in favour of the first
        # rank that does have one (falling back to the bare first match otherwise,
        # so the failure below still names the right doc_id).
        target_items = [it for it in api_body.get("results", []) if it.get("doc_id") == PRODUCT_W2_TARGET_DOC_ID]
        target_item = next((it for it in target_items if it.get("cards")), None) or (target_items[0] if target_items else None)
        if target_item is None:
            custom_reasons.append(f"W9: target {PRODUCT_W2_TARGET_DOC_ID!r} not found via lexical search for {q!r}")
            return _finish_workflow(spec, session, out_dir, custom_reasons=custom_reasons, observations=obs, screenshot_name="W9")

        line_no = (target_item.get("evidence") or {}).get("line_no")
        card_ref = ((target_item.get("cards") or [{}])[0].get("card") or {}).get("card_ref")
        obs["line_no"], obs["card_ref"] = line_no, card_ref
        if not card_ref or line_no is None:
            custom_reasons.append("W9: target result has no card row / line_no to open a jump link with")
            return _finish_workflow(spec, session, out_dir, custom_reasons=custom_reasons, observations=obs, screenshot_name="W9")

        open_link = f"/doc/{card_ref}?line={line_no}"
        session.goto("reader_jump", base_url + open_link)
        jump_line = session.attr("#document", "data-jump-line")
        selected = session.attr("#document", "data-selected-doc-id")
        hit_text = session.text(f"#L{line_no}.hit .line-text")
        doc_section_exists = session.count("#document") > 0
        card_section_exists = session.count("#card-panel") > 0
        obs.update(jump_line=jump_line, selected_doc_id=selected, hit_line_text=hit_text,
                   doc_section_exists=doc_section_exists, card_section_exists=card_section_exists)

        if jump_line != str(line_no):
            custom_reasons.append(f"W9: data-jump-line={jump_line!r}, expected {str(line_no)!r}")
        if q.lower() not in (hit_text or "").lower():
            custom_reasons.append(f"W9: source line marked 'hit' does not contain the phrase {q!r}: {hit_text!r}")
        if not doc_section_exists or not card_section_exists:
            custom_reasons.append("W9: the Document and Card (catalog metadata) regions are not both present")
        if selected != PRODUCT_W2_TARGET_DOC_ID:
            custom_reasons.append(f"W9: data-selected-doc-id={selected!r}, expected {PRODUCT_W2_TARGET_DOC_ID!r}")

        return _finish_workflow(spec, session, out_dir, custom_reasons=custom_reasons, observations=obs, screenshot_name="W9")
    finally:
        session.close()


def _run_w10(browser, base_url: str, ctx: ProbeContext, out_dir: Path) -> dict:
    del ctx
    spec = PRESET_REGISTRY["W10"]
    session = Session(browser)
    try:
        obs: dict = {}
        custom_reasons: list[str] = []

        session.goto("catalog_home", f"{base_url}/")

        q1 = PRODUCT_W1_QUERY
        session.goto("w1_identifier_search", f"{base_url}/search?q={urllib.parse.quote(q1)}&mode=identifier")
        w1_count = session.count(f'.identifier-results > li[data-doc-id="{q1}"]')
        if w1_count != 1:
            custom_reasons.append(f"W10/W1: expected exactly one identifier row for {q1!r}, found {w1_count}")
        w1_link = session.attr(f'.identifier-results > li[data-doc-id="{q1}"] .result-card a', "href")
        if w1_link:
            session.goto("w1_reader", base_url + w1_link)
            if session.attr("#document", "data-selected-doc-id") != q1:
                custom_reasons.append("W10/W1: reader data-selected-doc-id did not match the searched id")
        else:
            custom_reasons.append("W10/W1: no open link found for the identifier result")

        q2 = PRODUCT_W2_QUERY
        session.goto("w2_lexical_search", f"{base_url}/search?q={urllib.parse.quote(q2)}&mode=lexical")
        _, lex_body, lex_err = _http_get_json(base_url, f"/api/search?q={urllib.parse.quote(q2)}&mode=lexical")
        if lex_err or not lex_body or not lex_body.get("results"):
            custom_reasons.append("W10/W2: lexical search returned no usable results")
        else:
            # See _run_w9's comment: prefer a rank with a resolvable card row.
            w10_targets = [it for it in lex_body["results"] if it.get("doc_id") == PRODUCT_W2_TARGET_DOC_ID]
            target_item = next((it for it in w10_targets if it.get("cards")), None) or (w10_targets[0] if w10_targets else None)
            if target_item is None:
                custom_reasons.append(f"W10/W2: target {PRODUCT_W2_TARGET_DOC_ID!r} not found")
            else:
                line_no = (target_item.get("evidence") or {}).get("line_no")
                card_ref = ((target_item.get("cards") or [{}])[0].get("card") or {}).get("card_ref")
                if card_ref and line_no is not None:
                    session.goto("w9_reader_jump", f"{base_url}/doc/{card_ref}?line={line_no}")
                    if session.attr("#document", "data-jump-line") != str(line_no):
                        custom_reasons.append("W10/W9: reader jump line did not match")
                else:
                    custom_reasons.append("W10/W2: target result has no card_ref / line_no")

        session.goto("w4_catalog_cmp", f"{base_url}/?doc_type={PRODUCT_W4_DOC_TYPE}")
        row_count = session.count("tr[data-doc-id]")
        if row_count == 0:
            custom_reasons.append("W10/W4: no CMP rows in the catalog")
        else:
            if any(v is None for v in session.attr_all("tr[data-doc-id]", "data-status")):
                custom_reasons.append("W10/W4: not every CMP row carries data-status")
            if any(v is None for v in session.attr_all("tr[data-doc-id]", "data-lifecycle-state")):
                custom_reasons.append("W10/W4: not every CMP row carries data-lifecycle-state")

        session.goto("diagnostics", f"{base_url}/diagnostics")

        localhost_reasons, offenders = _w10_localhost_check(session.requests)
        obs["requests_total"] = len(session.requests)
        obs["non_localhost_requests"] = offenders
        custom_reasons.extend(localhost_reasons)

        return _finish_workflow(spec, session, out_dir, custom_reasons=custom_reasons, observations=obs, screenshot_name="W10")
    finally:
        session.close()


WORKFLOW_RUNNERS: dict[str, Callable[[Any, str, ProbeContext, Path], dict]] = {
    "KG": _run_kg,
    "KB1": _run_kb1,
    "KB2": _run_kb2,
    "KB3": _run_kb3,
    "KB4": _run_kb4,
    "KB5": _run_kb5,
    "W1": _run_w1,
    "W2": _run_w2,
    "W3": _run_w3,
    "W4": _run_w4,
    "W5": _run_w5,
    "W6": _run_w6,
    "W7": _run_w7,
    "W8": _run_w8,
    "W9": _run_w9,
    "W10": _run_w10,
}


def run_presets(names: list[str], base_url: str, browser, out_dir: Path,
                 ctx: ProbeContext | None = None) -> dict[str, dict]:
    results: dict[str, dict] = {}
    for name in names:
        spec = PRESET_REGISTRY[name]
        if spec.kind == "json_endpoint":
            result = run_json_endpoint_preset(base_url, spec)
        elif spec.kind == "page":
            result = run_page_preset(browser, base_url, spec, out_dir)
        elif spec.kind == "workflow":
            runner = WORKFLOW_RUNNERS[name]
            try:
                result = runner(browser, base_url, ctx, out_dir)
            except Exception as exc:  # noqa: BLE001 -- a workflow bug is a FAIL, never a crash
                result = {
                    "preset": spec.name, "kind": spec.kind, "label": spec.label,
                    "verdict": "FAIL", "ok": False, "fault_detected": False, "fault_class": None,
                    "reasons": [f"workflow_runner_exception: {type(exc).__name__}: {exc}"],
                }
        else:
            result = run_not_implemented_preset(spec)
        results[name] = result
        _write_json(out_dir / f"{name}.json", result)
    return results


# ─── Qualification-state vocabulary (AC-3; task C1 item 2) ──────────────────

QUALIFICATION_STATES = (
    "FRAMEWORK_SMOKE_PASS", "QUALIFICATION_PASS", "PRODUCT_EVIDENCE_PASS", "FAIL", "INCOMPLETE",
)
DEFAULT_LEDGER_PATH = Path(_WORKSPACE_ROOT) / "docs" / "probe-qualification" / "qualification_ledger.json"

# console_error (KB5) was, in round 1/C1 (only "diagnostics" existed as a page-kind
# preset), defined as touching every page-kind preset run -- kept verbatim for backward
# compatibility with the C1 tests and the `--preset diagnostics --fault console_error`
# invocation (item 2). Round 2's real KB5 runner (a single "workflow"-kind preset that
# visits diagnostics *and* catalog/search/reader as clean control steps, see
# `_run_kb5`) is matched instead by `_touched_presets`' second rule below (a selected
# preset whose own `PresetSpec.fault` equals the requested fault) -- both rules are
# applied together so neither invocation shape regresses the other.
_FAULTS_TOUCHING_ALL_PAGES = frozenset({"console_error"})


def _touched_presets(results: dict[str, dict], fault: str | None) -> list[str]:
    """Round 2: the presets a qualification run's `--fault` is expected to show up
    in. Two rules, unioned (a selected preset can match either):
      (a) legacy (task C1): if `fault` is in `_FAULTS_TOUCHING_ALL_PAGES`, every
          selected preset of kind "page" (kept for `--preset diagnostics --fault
          console_error`, still exercised by tests/probe/test_probe_qualification_
          subprocess.py and tests/probe/test_qualification_state.py).
      (b) round 2: any selected preset whose own `PRESET_REGISTRY[name].fault`
          equals the requested fault -- this is how KB1/KB2/KB4/KB5 (kind
          "workflow", each pairing 1:1 with one `explorer.faults.FAULTS` entry via
          `PresetSpec.fault`) are matched, regardless of their `kind`.
    """
    touched: set[str] = set()
    if fault in _FAULTS_TOUCHING_ALL_PAGES:
        touched.update(n for n, r in results.items() if r.get("kind") == "page")
    for name in results:
        spec = PRESET_REGISTRY.get(name)
        if spec is not None and spec.fault == fault:
            touched.add(name)
    return sorted(touched)


def determine_run_kind(fault: str | None, db_path: str) -> str:
    """run_kind derivation (task C1 item 2): "qualification" when a fault was
    requested; else "product" against a RHACO tree; else "smoke"."""
    if fault:
        return "qualification"
    if is_under_rhaco_tree(db_path):
        return "product"
    return "smoke"


def _qual(state: str, *, eligible: bool = False, classes: list[str] | None = None,
          incomplete: list[str] | None = None, reasons: list[str] | None = None,
          blocked: list[str] | None = None) -> dict:
    return {
        "qualification_state": state,
        "product_evidence_eligible": eligible,
        "qualified_failure_classes": classes or [],
        "incomplete_presets": incomplete or [],
        "product_evidence_blocked_by": blocked or [],
        "reasons": reasons or [],
    }


def derive_qualification(results: dict[str, dict], run_kind: str, fault: str | None, ledger: dict) -> dict:
    """AC-3 qualification-state derivation (task C1 item 2; Director ruling AC-3).
    Pure over already-computed preset `results` (the dict run_presets() returns,
    keyed by preset name) plus `run_kind` ("qualification" | "product" | "smoke"),
    the requested `--fault` (None for product/smoke), and the loaded ledger
    ({"classes": {...}, "runs": [...]}). Returns the fields recorded into
    run_summary.json; never writes the ledger itself (main() does that, and only
    on QUALIFICATION_PASS).
    """
    # Round 2: a "workflow"-kind preset can also self-report `incomplete=True` (currently
    # only W3, when the vector channel is unavailable at run time -- the dispatch's own
    # "recorded as INCOMPLETE for W3, not FAIL" rule) -- folded into the same run-level
    # INCOMPLETE state as a not_implemented_yet stub, not a sixth vocabulary state.
    incomplete = sorted(n for n, r in results.items()
                         if r.get("status") == "not_implemented_yet" or r.get("incomplete") is True)
    if incomplete:
        reasons = []
        for n in incomplete:
            r = results[n]
            if r.get("status") == "not_implemented_yet":
                reasons.append(f"preset {n} still reports not_implemented_yet")
            else:
                reasons.append(f"preset {n} is incomplete: "
                                f"{(r.get('observations') or {}).get('incomplete_reason') or 'see preset JSON'}")
        return _qual("INCOMPLETE", incomplete=incomplete, reasons=reasons)

    all_ok = bool(results) and all(r.get("ok") for r in results.values())

    if run_kind == "qualification":
        target_class = FAULT_TO_CLASS.get(fault)
        if target_class is None:
            return _qual("FAIL", reasons=[f"unknown fault {fault!r}: no qualification class mapping"])
        touched = _touched_presets(results, fault)
        reasons: list[str] = []
        if not touched:
            reasons.append(f"no preset selected to exercise fault {fault!r} "
                            f"(no page-kind preset and no preset whose own .fault matches)")
        detection_ok = True
        for name in touched:
            r = results[name]
            if not (r.get("verdict") == "FAIL" and r.get("fault_detected") and r.get("fault_class") == target_class):
                detection_ok = False
                reasons.append(f"preset {name} did not report FAIL/fault_detected/fault_class={target_class!r} "
                                f"(got verdict={r.get('verdict')!r}, fault_detected={r.get('fault_detected')!r}, "
                                f"fault_class={r.get('fault_class')!r})")
        others_ok = True
        for name, r in results.items():
            if name in touched:
                continue
            if not r.get("ok"):
                others_ok = False
                reasons.append(f"preset {name} did not pass (must stay clean during a qualification run)")
        if touched and detection_ok and others_ok:
            return _qual("QUALIFICATION_PASS", classes=[target_class])
        return _qual("FAIL", reasons=reasons)

    if run_kind == "smoke":
        if all_ok:
            return _qual("FRAMEWORK_SMOKE_PASS")
        return _qual("FAIL", reasons=[f"preset {n} failed" for n, r in results.items() if not r.get("ok")])

    # run_kind == "product"
    if not all_ok:
        return _qual("FAIL", reasons=[f"preset {n} failed" for n, r in results.items() if not r.get("ok")])
    ledger_classes = set((ledger or {}).get("classes", {}).keys())
    blocked = sorted(
        name for name in results
        if any(cls not in ledger_classes for cls in PRESET_REGISTRY[name].required_classes)
    )
    if not blocked:
        return _qual("PRODUCT_EVIDENCE_PASS", eligible=True, classes=sorted(ledger_classes))
    return _qual("FRAMEWORK_SMOKE_PASS", blocked=blocked,
                 reasons=[f"preset {n} missing ledger coverage for {list(PRESET_REGISTRY[n].required_classes)}"
                          for n in blocked])


def _load_ledger(path: Path) -> dict:
    if not path.is_file():
        return {"classes": {}, "runs": []}
    try:
        data = json.loads(path.read_text(encoding="ascii"))
    except (OSError, ValueError):
        return {"classes": {}, "runs": []}
    data.setdefault("classes", {})
    data.setdefault("runs", [])
    return data


def _update_ledger(path: Path, run_rel: str, qualification_state: str, classes: list[str]) -> None:
    """Idempotent, ASCII append (task C1 item 2): re-running the same --out (hence
    the same `run_rel`) never duplicates a `runs` entry; each class's ledger row is
    (re)set to this run, the latest evidence for it."""
    ledger = _load_ledger(path)
    recorded_utc = _now_iso()
    for cls in classes:
        ledger["classes"][cls] = {"run": run_rel, "recorded_utc": recorded_utc}
    if not any(r.get("run") == run_rel for r in ledger["runs"]):
        ledger["runs"].append({"run": run_rel, "qualification_state": qualification_state, "classes": list(classes)})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ledger, ensure_ascii=True, indent=2, sort_keys=True), encoding="ascii")


# ─── CLI ─────────────────────────────────────────────────────────────────────

def _build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="RHACO Corpus Explorer production-path probe.")
    ap.add_argument("--db", required=True, help="corpus_index.db path (fixture or live; read-only)")
    ap.add_argument("--docs-root", required=True, dest="docs_root",
                     help="docs root matching --db (display + confinement only)")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--preset", default="all",
                     help=f"one of {{{', '.join(PRESET_REGISTRY)}}}, a comma-separated list of them, "
                          "or 'all' (default)")
    ap.add_argument("--out", default=None,
                     help="output dir (default: docs/probe-qualification/runs/<utc stamp>)")
    ap.add_argument("--fault", default=None, choices=sorted(FAULTS),
                     help="fixture-only fault to inject (explorer/faults.FAULTS); ignored against a live db")
    ap.add_argument("--disable-vec", action="store_true",
                     help="set RHACO_CORPUS_DISABLE_VEC=1 in the child (W7 degradation)")
    ap.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_S,
                     help="readiness wait bound in seconds (default 30)")
    ap.add_argument("--ledger", default=None,
                     help="qualification ledger path (default: "
                          f"{DEFAULT_LEDGER_PATH}, resolved from this file's own location)")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)

    if args.preset == "all":
        names = list(PRESET_REGISTRY.keys())
    elif "," in args.preset:
        # Task B10, round 4: a comma-separated list selects exactly those
        # presets in one run (e.g. the fixture FINAL suite,
        # "KG,KB1,KB2,KB3,KB4,KB5") -- an unknown name is a hard error, same
        # as a single unknown name.
        requested = [p.strip() for p in args.preset.split(",") if p.strip()]
        unknown = [p for p in requested if p not in PRESET_REGISTRY]
        if unknown:
            print(f"ERROR: unknown preset(s) {unknown!r}. Known presets: {', '.join(PRESET_REGISTRY)}")
            return 2
        names = requested
    elif args.preset in PRESET_REGISTRY:
        names = [args.preset]
    else:
        print(f"ERROR: unknown preset {args.preset!r}. Known presets: {', '.join(PRESET_REGISTRY)}")
        return 2

    db_path = os.path.realpath(args.db)
    docs_root = os.path.realpath(args.docs_root)
    if not os.path.isfile(db_path):
        print(f"ERROR: --db does not exist: {db_path}")
        return 2
    if not os.path.isdir(docs_root):
        print(f"ERROR: --docs-root does not exist: {docs_root}")
        return 2

    out_dir = Path(args.out) if args.out else Path(_WORKSPACE_ROOT) / "docs" / "probe-qualification" / "runs" / _utc_stamp()
    out_dir.mkdir(parents=True, exist_ok=True)

    base_url = f"http://127.0.0.1:{args.port}"
    run_started = _now_iso()
    proc: subprocess.Popen | None = None
    results: dict[str, dict] = {}
    healthz_body: dict | None = None
    run_error: str | None = None
    db_meta_before: dict | None = None
    db_meta_after: dict | None = None

    def _db_meta() -> dict | None:
        """The diagnostics page's own "Database modified"/size observation, read
        ONLY through the server (never by opening --db) -- task B7 deliverable 3:
        record the db's mtime before and after a production run, expecting no
        change (the live index is read-only from this tool's perspective)."""
        _status, body, _err = _http_get_json(base_url, "/api/diagnostics")
        if not body or "index_meta" not in body:
            return None
        meta = body["index_meta"]
        return {"db_path": meta.get("db_path"), "db_bytes": meta.get("db_bytes"), "db_mtime_utc": meta.get("db_mtime_utc")}

    server_log_path = out_dir / "server.log"
    with open(server_log_path, "w", encoding="utf-8", errors="replace") as server_log:
        try:
            proc = launch_server(
                sys.executable, args.port, db_path, docs_root, cwd=_WORKSPACE_ROOT,
                log_file=server_log, fault=args.fault, disable_vec=args.disable_vec,
            )
            healthz_body = wait_for_healthz(base_url, args.timeout)
            db_meta_before = _db_meta()

            ctx = ProbeContext(
                docs_root=docs_root, db_path=db_path, port=args.port,
                fault=args.fault, disable_vec=bool(args.disable_vec), timeout_s=args.timeout,
            )
            needs_browser = any(PRESET_REGISTRY[n].kind in ("page", "workflow") for n in names)
            if needs_browser:
                from playwright.sync_api import sync_playwright
                with sync_playwright() as pw:
                    browser = pw.chromium.launch(headless=True)
                    try:
                        results = run_presets(names, base_url, browser, out_dir, ctx)
                    finally:
                        browser.close()
            else:
                results = run_presets(names, base_url, None, out_dir, ctx)
            db_meta_after = _db_meta()
        except TimeoutError as exc:
            run_error = str(exc)
        except Exception as exc:  # noqa: BLE001 -- never exit without writing run_summary.json
            run_error = f"{type(exc).__name__}: {exc}"
        finally:
            if proc is not None:
                terminate_server(proc)

    run_finished = _now_iso()

    ledger_path = Path(args.ledger) if args.ledger else DEFAULT_LEDGER_PATH
    if not ledger_path.is_absolute():
        ledger_path = Path(_WORKSPACE_ROOT) / ledger_path
    ledger = _load_ledger(ledger_path)

    run_kind = determine_run_kind(args.fault, db_path)
    if run_error is not None:
        qual = _qual("FAIL", reasons=[f"run_error: {run_error}"])
    else:
        qual = derive_qualification(results, run_kind, args.fault, ledger)

    if qual["qualification_state"] == "QUALIFICATION_PASS":
        run_rel = os.path.relpath(out_dir, _WORKSPACE_ROOT).replace(os.sep, "/")
        _update_ledger(ledger_path, run_rel, qual["qualification_state"], qual["qualified_failure_classes"])

    verdict = "PASS" if qual["qualification_state"] in (
        "FRAMEWORK_SMOKE_PASS", "QUALIFICATION_PASS", "PRODUCT_EVIDENCE_PASS",
    ) else qual["qualification_state"]  # "FAIL" or "INCOMPLETE" pass through unchanged

    summary = {
        "run_started_utc": run_started,
        "run_finished_utc": run_finished,
        "db_path": db_path,
        "docs_root": docs_root,
        "port": args.port,
        "fault": args.fault,
        "disable_vec": bool(args.disable_vec),
        "timeout_s": args.timeout,
        "presets_run": names,
        "healthz": healthz_body,
        "db_meta_before": db_meta_before,
        "db_meta_after": db_meta_after,
        "run_error": run_error,
        "server_log": str(server_log_path),
        "ledger_path": str(ledger_path),
        "run_kind": run_kind,
        "results": {
            n: {"ok": r.get("ok"), "kind": r.get("kind"), "http_status": r.get("http_status"),
                "route_absent": r.get("route_absent"), "status": r.get("status"),
                "verdict": r.get("verdict"), "reasons": r.get("reasons"),
                "fault_detected": r.get("fault_detected"), "fault_class": r.get("fault_class"),
                "incomplete": r.get("incomplete", False)}
            for n, r in results.items()
        },
        "qualification_state": qual["qualification_state"],
        "product_evidence_eligible": qual["product_evidence_eligible"],
        "qualified_failure_classes": qual["qualified_failure_classes"],
        "incomplete_presets": qual["incomplete_presets"],
        "product_evidence_blocked_by": qual["product_evidence_blocked_by"],
        "reasons": qual["reasons"],
        "verdict": verdict,
    }
    _write_json(out_dir / "run_summary.json", summary)

    print(f"probe run: out={out_dir}")
    print(f"probe run: presets={','.join(names)}")
    print(f"probe run: run_kind={run_kind}")
    print(f"probe run: qualification_state={qual['qualification_state']}")
    print(f"probe run: verdict={summary['verdict']}")
    if run_error:
        print(_ascii(f"probe run: error={run_error}"))

    exit_codes = {
        "FRAMEWORK_SMOKE_PASS": 0, "QUALIFICATION_PASS": 0, "PRODUCT_EVIDENCE_PASS": 0,
        "FAIL": 1, "INCOMPLETE": 3,
    }
    return exit_codes[qual["qualification_state"]]


if __name__ == "__main__":
    sys.exit(main())
