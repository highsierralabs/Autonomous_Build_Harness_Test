"""Search routes (builder-owned: search). ARCHITECTURE.md 4.3; task B5.

GET /search      -- HTML search surface (template search/search.html).
GET /api/search  -- JSON twin (dataclasses.asdict over the same SearchView the
                     page renders, including every result's evidence).

The adapter is reached only through explorer.app.get_adapter(request)
(ARCHITECTURE.md 4.3 access rule, matching the diagnostics precedent). When it
raises RuntimeError (corpus_adapter not built yet), the HTML page renders a
visible notice at HTTP 503 and the API returns 503 {"error": "corpus_adapter
not built"}.
"""
from __future__ import annotations

import dataclasses

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from explorer.search.service import run_search

TEMPLATE = "search/search.html"
ADAPTER_ABSENT_MESSAGE = "corpus_adapter not built"


def _get_adapter(request: Request):
    from explorer.app import get_adapter

    return get_adapter(request)


def register(app: FastAPI) -> None:
    @app.get("/search")
    def search_page(request: Request):
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
        view = run_search(adapter, request.app.state.settings, dict(request.query_params))
        return templates.TemplateResponse(request, TEMPLATE, {"adapter_absent": False, "view": view})

    @app.get("/api/search")
    def search_api(request: Request):
        try:
            adapter = _get_adapter(request)
        except RuntimeError:
            return JSONResponse({"error": ADAPTER_ABSENT_MESSAGE}, status_code=503)
        view = run_search(adapter, request.app.state.settings, dict(request.query_params))
        return JSONResponse(dataclasses.asdict(view))
