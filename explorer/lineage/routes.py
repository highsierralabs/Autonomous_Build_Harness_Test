"""Lineage routes (builder-owned: lineage). ARCHITECTURE.md 4.5; task B8.

GET /lineage/{card_ref:path}      -- HTML: the relationship / reasoning-trail view.
GET /api/lineage/{card_ref:path}  -- JSON twin (dataclasses.asdict(view)).

The adapter is reached only through explorer.app.get_adapter(request) (the
diagnostics precedent, explorer/diagnostics/routes.py): when it raises
RuntimeError (corpus_adapter not built), the HTML page renders a visible 503
notice and the API returns 503 {"error": "corpus_adapter not built"}. An
unknown card_ref, a docs_archive card_ref (never indexed, so build_view
already returns None for it), or a `..` traversal is a 404 on both, with a
visible notice on the page -- never a crash, never a silent landing.
"""
from __future__ import annotations

import dataclasses

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from explorer.lineage.service import build_view, compute_layout

TEMPLATE = "lineage/lineage.html"
ADAPTER_ABSENT_MESSAGE = "corpus_adapter not built"


def _get_adapter(request: Request):
    from explorer.app import get_adapter

    return get_adapter(request)


def _parse_relation(request: Request) -> str | None:
    raw = request.query_params.get("relation")
    return raw.strip() if raw and raw.strip() else None


def _parse_hops(request: Request) -> int:
    raw = request.query_params.get("hops")
    if raw is None:
        return 1
    try:
        value = int(raw.strip())
    except (TypeError, ValueError):
        return 1
    return 2 if value == 2 else 1


def register(app: FastAPI) -> None:
    @app.get("/lineage/{card_ref:path}")
    def lineage_page(card_ref: str, request: Request):
        templates = request.app.state.templates
        try:
            adapter = _get_adapter(request)
        except RuntimeError as exc:
            return templates.TemplateResponse(
                request, TEMPLATE,
                {
                    "adapter_absent": True, "adapter_absent_message": str(exc),
                    "not_found": False, "card_ref": card_ref,
                },
                status_code=503,
            )
        relation = _parse_relation(request)
        hops = _parse_hops(request)
        view = build_view(adapter, request.app.state.settings, card_ref, relation, hops)
        if view is None:
            return templates.TemplateResponse(
                request, TEMPLATE,
                {"adapter_absent": False, "not_found": True, "card_ref": card_ref},
                status_code=404,
            )
        layout = compute_layout(view)
        return templates.TemplateResponse(
            request, TEMPLATE,
            {"adapter_absent": False, "not_found": False, "view": view, "layout": layout, "card_ref": card_ref},
        )

    @app.get("/api/lineage/{card_ref:path}")
    def lineage_api(card_ref: str, request: Request):
        try:
            adapter = _get_adapter(request)
        except RuntimeError:
            return JSONResponse({"error": ADAPTER_ABSENT_MESSAGE}, status_code=503)
        relation = _parse_relation(request)
        hops = _parse_hops(request)
        view = build_view(adapter, request.app.state.settings, card_ref, relation, hops)
        if view is None:
            return JSONResponse({"error": "card not found"}, status_code=404)
        return JSONResponse(dataclasses.asdict(view))
