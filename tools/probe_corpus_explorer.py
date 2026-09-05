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
  outside its own --out directory). W1-W10, KG, and KB1-KB5 remain
  not_implemented_yet stubs this round (any run that selects one is
  INCOMPLETE, never a PASS of any kind) -- wave 2 fills them in.

USAGE
  <venv python> tools/probe_corpus_explorer.py --db <path> --docs-root <path>
      [--port 8765] [--preset NAME|all] [--out DIR] [--fault NAME]
      [--disable-vec] [--timeout 30] [--ledger PATH]

  --db and --docs-root are REQUIRED (no default) so this tool can never launch
  the explorer against the live corpus_index.db by omission -- every run names
  its database explicitly. --preset defaults to "all" (every registry entry).
  --out defaults to docs/probe-qualification/runs/<utc stamp>. --ledger
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
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

# --- make `explorer` importable regardless of how this file is invoked -----
_WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, _WORKSPACE_ROOT)

from explorer.faults import FAULTS, is_under_rhaco_tree  # noqa: E402

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


def _w(n: int, label: str, required_classes: tuple[str, ...] = ()) -> PresetSpec:
    return PresetSpec(name=f"W{n}", kind="not_implemented", label=label, required_classes=required_classes)


def _kb(n: int, fault: str) -> PresetSpec:
    return PresetSpec(
        name=f"KB{n}", kind="not_implemented",
        label=f"Known-bad qualification case KB{n}: RHACO_EXPLORER_FAULT={fault} "
              "(explorer/faults.py; the probe must flag it once the reader/lineage/search "
              "surfaces the fault touches are built)",
        fault=fault,
    )


# Registry order: the two presets this round implements for real, then the ten
# acceptance workflows (PROMPT.md section 8), then the qualification cases
# (ARCHITECTURE.md section 6 / explorer/faults.FAULTS) -- KG first (known-good
# baseline, no fault), then KB1-KB5 mapped 1:1 onto FAULTS in its declared
# order (wrong_doc_for_id, stale_card, reverse_edges, broken_jump,
# console_error). All of W1-W10/KG/KB1-KB5 are "not_implemented" stubs filled
# in by later waves once catalog/search/reader/lineage exist to drive.
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
             required_classes=("KB1", "KB5")),
    "W2": _w(2, "Lexical phrase -- search a known phrase, expect target + consistent excerpt/line",
             required_classes=("KB1", "KB2", "KB5")),
    "W3": _w(3, "Semantic inquiry -- frozen gold semantic query, accepted hybrid baseline preserved",
             required_classes=("KB1", "KB5")),
    "W4": _w(4, "Campaign lifecycle browse -- CMP filter, status + lifecycle_state both visible/filterable",
             required_classes=("KB2", "KB5")),
    "W5": _w(5, "Reasoning lineage -- edges match indexed relationships and direction",
             required_classes=("KB3", "KB5")),
    "W6": _w(6, "Supersession/amendment -- historical artifact visible, replacement relationship clear",
             required_classes=("KB3", "KB5")),
    "W7": _w(7, "Degraded semantic channel -- RHACO_CORPUS_DISABLE_VEC=1, lexical/direct still usable",
             required_classes=("KB5",)),
    "W8": _w(8, "Staleness -- freshness DRIFT surfaced, never silently treated as current",
             required_classes=("KB2", "KB5")),
    "W9": _w(9, "Reader provenance -- open a hit at a line/section, body vs card rendered distinctly",
             required_classes=("KB4", "KB5")),
    "W10": _w(10, "No-LLM operation -- full standard workflow, no frontier model access",
              required_classes=("KB1", "KB2", "KB4", "KB5")),
    "KG": PresetSpec(
        "KG", "not_implemented",
        "Known-good qualification baseline against the fixture index (no RHACO_EXPLORER_FAULT set)",
        required_classes=(),
    ),
    "KB1": _kb(1, FAULTS[0]),
    "KB2": _kb(2, FAULTS[1]),
    "KB3": _kb(3, FAULTS[2]),
    "KB4": _kb(4, FAULTS[3]),
    "KB5": _kb(5, FAULTS[4]),
}

# Fault-class attribution table (task C1 item 1), kept next to PRESET_REGISTRY: KBn ->
# the explorer.faults.FAULTS name it qualifies (same order as explorer/faults.py). Wave
# 2 adds the attribution *rule* for KB1-KB4 (how to recognize each from an observation);
# this round implements only KB5's rule (a console/page error whose text contains
# CONSOLE_ERROR_FAULT_TEXT, checked by _attribute_fault_class below). Extending
# FAULT_TEXT_MARKERS with a KB1-KB4 marker is enough to wire in the next rule --
# evaluate_page and PRESET_REGISTRY need no restructuring.
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


def run_presets(names: list[str], base_url: str, browser, out_dir: Path) -> dict[str, dict]:
    results: dict[str, dict] = {}
    for name in names:
        spec = PRESET_REGISTRY[name]
        if spec.kind == "json_endpoint":
            result = run_json_endpoint_preset(base_url, spec)
        elif spec.kind == "page":
            result = run_page_preset(browser, base_url, spec, out_dir)
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

# console_error (KB5) is the only fault whose runner (diagnostics) exists this round,
# and its instruction is explicit: it touches every page-kind preset run. Wave 2, once
# search/reader/lineage exist, extends this with which pages KB1-KB4 each touch.
_FAULTS_TOUCHING_ALL_PAGES = frozenset({"console_error"})


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
    incomplete = sorted(n for n, r in results.items() if r.get("status") == "not_implemented_yet")
    if incomplete:
        return _qual("INCOMPLETE", incomplete=incomplete,
                      reasons=[f"preset {n} still reports not_implemented_yet" for n in incomplete])

    all_ok = bool(results) and all(r.get("ok") for r in results.values())

    if run_kind == "qualification":
        target_class = FAULT_TO_CLASS.get(fault)
        if target_class is None:
            return _qual("FAIL", reasons=[f"unknown fault {fault!r}: no qualification class mapping"])
        touched = [n for n, r in results.items() if r.get("kind") == "page"] if fault in _FAULTS_TOUCHING_ALL_PAGES else []
        reasons: list[str] = []
        if not touched:
            reasons.append(f"no page-kind preset selected to exercise fault {fault!r}")
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
                     help=f"one of {{{', '.join(PRESET_REGISTRY)}}} or 'all' (default)")
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

    server_log_path = out_dir / "server.log"
    with open(server_log_path, "w", encoding="utf-8", errors="replace") as server_log:
        try:
            proc = launch_server(
                sys.executable, args.port, db_path, docs_root, cwd=_WORKSPACE_ROOT,
                log_file=server_log, fault=args.fault, disable_vec=args.disable_vec,
            )
            healthz_body = wait_for_healthz(base_url, args.timeout)

            needs_browser = any(PRESET_REGISTRY[n].kind == "page" for n in names)
            if needs_browser:
                from playwright.sync_api import sync_playwright
                with sync_playwright() as pw:
                    browser = pw.chromium.launch(headless=True)
                    try:
                        results = run_presets(names, base_url, browser, out_dir)
                    finally:
                        browser.close()
            else:
                results = run_presets(names, base_url, None, out_dir)
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
        "run_error": run_error,
        "server_log": str(server_log_path),
        "ledger_path": str(ledger_path),
        "run_kind": run_kind,
        "results": {
            n: {"ok": r.get("ok"), "kind": r.get("kind"), "http_status": r.get("http_status"),
                "route_absent": r.get("route_absent"), "status": r.get("status"),
                "verdict": r.get("verdict"), "reasons": r.get("reasons"),
                "fault_detected": r.get("fault_detected"), "fault_class": r.get("fault_class")}
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
