"""Catalog routes (builder-owned: catalog). ARCHITECTURE.md 4.2; task B4 item 2.

GET /             -- HTML browse/filter page (catalog/catalog.html extends base.html).
GET /api/catalog  -- JSON twin (dataclasses.asdict(view)).

The adapter is reached only through explorer.app.get_adapter(request)
(ARCHITECTURE.md 4.2 access rule, mirroring the diagnostics precedent). When
it raises RuntimeError (corpus_adapter not built yet), the HTML page renders
a visible notice at HTTP 503 and the API returns 503 {"error": "..."}.
"""
from __future__ import annotations

import dataclasses

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from explorer.catalog.service import build_view

TEMPLATE = "catalog/catalog.html"
ADAPTER_ABSENT_MESSAGE = "corpus_adapter not built"


def _get_adapter(request: Request):
    from explorer.app import get_adapter

    return get_adapter(request)


def register(app: FastAPI) -> None:
    @app.get("/")
    def catalog_page(request: Request):
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
        view = build_view(adapter, request.app.state.settings, dict(request.query_params))
        return templates.TemplateResponse(request, TEMPLATE, {"adapter_absent": False, "view": view})

    @app.get("/api/catalog")
    def catalog_api(request: Request):
        try:
            adapter = _get_adapter(request)
        except RuntimeError:
            return JSONResponse({"error": ADAPTER_ABSENT_MESSAGE}, status_code=503)
        view = build_view(adapter, request.app.state.settings, dict(request.query_params))
        return JSONResponse(dataclasses.asdict(view))
