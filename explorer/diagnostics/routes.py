"""Diagnostics routes (builder-owned: diagnostics). ARCHITECTURE.md 4.6; task B3 item 2.

GET /diagnostics        -- HTML instrument-state page.
POST /diagnostics/freshness -- the application's only POST; computes freshness via
                               adapter.freshness() and re-renders the page. Writes nothing.
GET /api/diagnostics     -- JSON twin (dataclasses.asdict); ?freshness=1 includes freshness.

The adapter is reached only through explorer.app.get_adapter(request) (task B3 access
rule). When it raises RuntimeError (corpus_adapter not built yet), every route degrades
visibly instead of crashing: the HTML page renders a notice, the API returns 503.
"""
from __future__ import annotations

import dataclasses

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from explorer.diagnostics.service import build_view

TEMPLATE = "diagnostics/diagnostics.html"
ADAPTER_ABSENT_MESSAGE = "corpus_adapter not built"


def _get_adapter(request: Request):
    from explorer.app import get_adapter

    return get_adapter(request)


def register(app: FastAPI) -> None:
    @app.get("/diagnostics")
    def diagnostics_page(request: Request):
        templates = request.app.state.templates
        try:
            adapter = _get_adapter(request)
        except RuntimeError as exc:
            return templates.TemplateResponse(
                request,
                TEMPLATE,
                {"adapter_absent": True, "adapter_absent_message": str(exc)},
                status_code=503,
            )
        view = build_view(adapter, request.app.state.settings)
        return templates.TemplateResponse(request, TEMPLATE, {"adapter_absent": False, "view": view})

    @app.post("/diagnostics/freshness")
    def diagnostics_freshness(request: Request):
        templates = request.app.state.templates
        try:
            adapter = _get_adapter(request)
        except RuntimeError as exc:
            return templates.TemplateResponse(
                request,
                TEMPLATE,
                {"adapter_absent": True, "adapter_absent_message": str(exc)},
                status_code=503,
            )
        fresh = adapter.freshness()
        view = build_view(adapter, request.app.state.settings, freshness=fresh)
        return templates.TemplateResponse(request, TEMPLATE, {"adapter_absent": False, "view": view})

    @app.get("/api/diagnostics")
    def diagnostics_api(request: Request):
        try:
            adapter = _get_adapter(request)
        except RuntimeError:
            return JSONResponse({"error": ADAPTER_ABSENT_MESSAGE}, status_code=503)
        include_freshness = request.query_params.get("freshness") == "1"
        fresh = adapter.freshness() if include_freshness else None
        view = build_view(adapter, request.app.state.settings, freshness=fresh)
        return JSONResponse(dataclasses.asdict(view))
