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

  This round lands two presets for real -- `healthz` (a plain JSON check, no
  browser) and `diagnostics` (a Playwright page preset; the route is expected
  to 404 until the diagnostics module merges -- recorded as "route absent",
  never a crash) -- plus the full REGISTRY for the ten acceptance workflows
  W1-W10 (PROMPT.md section 8) and the qualification cases KG (known-good
  baseline) / KB1-KB5 (one per RHACO_EXPLORER_FAULT value in
  explorer/faults.FAULTS, same order), each of which cleanly reports
  {"status": "not_implemented_yet"} until wave 2 fills them in.

USAGE
  <venv python> tools/probe_corpus_explorer.py --db <path> --docs-root <path>
      [--port 8765] [--preset NAME|all] [--out DIR] [--fault NAME]
      [--disable-vec] [--timeout 30]

  --db and --docs-root are REQUIRED (no default) so this tool can never launch
  the explorer against the live corpus_index.db by omission -- every run names
  its database explicitly. --preset defaults to "all" (every registry entry).
  --out defaults to docs/probe-qualification/runs/<utc stamp>.

OUTPUT
  <out>/<preset>.json (+ <out>/<preset>.png for page-kind presets),
  <out>/run_summary.json, <out>/server.log (the child's stdout/stderr).
  Exit 0 iff every selected preset collected its required observations and
  none failed (a page preset's 404 "route absent" is a recorded state, not a
  failure; a not_implemented preset always reports cleanly). ASCII-only
  stdout (PYTHONIOENCODING=utf-8 set for the child too, per O19).

VERSION HISTORY
  v1.0  2026-09-04  Initial build (RHACO-HND-20260903-001 strand B2, round 1).
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

from explorer.faults import FAULTS  # noqa: E402

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


def _w(n: int, label: str) -> PresetSpec:
    return PresetSpec(name=f"W{n}", kind="not_implemented", label=label)


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
    ),
    "diagnostics": PresetSpec(
        "diagnostics", "page",
        "Diagnostics page (GET /diagnostics; 404 \"route absent\" is expected and "
        "accepted until the diagnostics module merges)",
        path="/diagnostics",
    ),
    "W1": _w(1, "Exact known document -- search a canonical id, expect direct result -> correct card"),
    "W2": _w(2, "Lexical phrase -- search a known phrase, expect target + consistent excerpt/line"),
    "W3": _w(3, "Semantic inquiry -- frozen gold semantic query, accepted hybrid baseline preserved"),
    "W4": _w(4, "Campaign lifecycle browse -- CMP filter, status + lifecycle_state both visible/filterable"),
    "W5": _w(5, "Reasoning lineage -- edges match indexed relationships and direction"),
    "W6": _w(6, "Supersession/amendment -- historical artifact visible, replacement relationship clear"),
    "W7": _w(7, "Degraded semantic channel -- RHACO_CORPUS_DISABLE_VEC=1, lexical/direct still usable"),
    "W8": _w(8, "Staleness -- freshness DRIFT surfaced, never silently treated as current"),
    "W9": _w(9, "Reader provenance -- open a hit at a line/section, body vs card rendered distinctly"),
    "W10": _w(10, "No-LLM operation -- full standard workflow, no frontier model access"),
    "KG": PresetSpec(
        "KG", "not_implemented",
        "Known-good qualification baseline against the fixture index (no RHACO_EXPLORER_FAULT set)",
    ),
    "KB1": _kb(1, FAULTS[0]),
    "KB2": _kb(2, FAULTS[1]),
    "KB3": _kb(3, FAULTS[2]),
    "KB4": _kb(4, FAULTS[3]),
    "KB5": _kb(5, FAULTS[4]),
}


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
    selected = page.evaluate(
        "() => { const el = document.querySelector('[data-selected-doc-id]'); "
        "return el ? el.getAttribute('data-selected-doc-id') : null; }"
    )
    result_ids = page.evaluate(
        "() => Array.from(document.querySelectorAll('[data-doc-id]'))"
        ".map((el) => el.getAttribute('data-doc-id'))"
    )
    return {"mode": mode, "selected_doc_id": selected, "result_ids": result_ids}


def run_page_preset(browser, base_url: str, spec: PresetSpec, out_dir: Path) -> dict:
    url = base_url + (spec.path or "")
    console_errors: list = []
    failed_requests: list = []

    context = browser.new_context(viewport=VIEWPORT)
    page = context.new_page()
    page.on("console", _console_listener(console_errors))
    page.on("requestfailed", _request_failed_listener(failed_requests))
    page.on("response", _response_listener(failed_requests))

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
    dom_obs = {"mode": None, "selected_doc_id": None, "result_ids": []}
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

    route_absent = http_status == 404
    # A route that 404s (module not merged yet) is a recorded, accepted state
    # per this round's spec -- only an actual crash/navigation error fails the preset.
    ok = error is None

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
        "selected_doc_id": dom_obs["selected_doc_id"],
        "result_ids": dom_obs["result_ids"],
        "console_errors": console_errors,
        "failed_requests": failed_requests,
        "timings": {"nav_start_utc": nav_start, "nav_end_utc": nav_end, "elapsed_ms": round(elapsed_ms, 1)},
        "screenshot": screenshot_saved,
        "error": error,
        "ok": ok,
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
    all_ok = run_error is None and all(r.get("ok", False) for r in results.values()) and bool(results)

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
        "results": {
            n: {"ok": r.get("ok"), "kind": r.get("kind"), "http_status": r.get("http_status"),
                "route_absent": r.get("route_absent"), "status": r.get("status")}
            for n, r in results.items()
        },
        "verdict": "PASS" if all_ok else "FAIL",
    }
    _write_json(out_dir / "run_summary.json", summary)

    print(f"probe run: out={out_dir}")
    print(f"probe run: presets={','.join(names)}")
    print(f"probe run: verdict={summary['verdict']}")
    if run_error:
        print(_ascii(f"probe run: error={run_error}"))

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
