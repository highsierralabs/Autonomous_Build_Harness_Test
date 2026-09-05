"""Reader routes (builder-owned: reader). ARCHITECTURE.md 4.4; PROMPT.md 5.4.

GET /doc/{card_ref:path}      -- HTML: the canonical document + card reader.
GET /api/doc/{card_ref:path}  -- JSON twin (dataclasses.asdict(view)).

The adapter is reached only through explorer.app.get_adapter(request) (the
diagnostics precedent, explorer/diagnostics/routes.py): when it raises
RuntimeError (corpus_adapter not built), the HTML page renders a visible 503
notice and the API returns 503 {"error": "corpus_adapter not built"}. An
unknown or out-of-root card_ref (build_view returns None) is a 404 on both,
with a visible notice on the page -- never a crash, never a silent landing.
"""
from __future__ import annotations

import dataclasses

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from explorer.reader.service import build_view

TEMPLATE = "reader/reader.html"
ADAPTER_ABSENT_MESSAGE = "corpus_adapter not built"


def _get_adapter(request: Request):
    from explorer.app import get_adapter

    return get_adapter(request)


def _parse_line(request: Request) -> int | None:
    raw = request.query_params.get("line")
    if raw is None or raw.strip() == "":
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def register(app: FastAPI) -> None:
    @app.get("/doc/{card_ref:path}")
    def reader_page(card_ref: str, request: Request):
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
        line = _parse_line(request)
        view = build_view(adapter, request.app.state.settings, card_ref, line)
        if view is None:
            return templates.TemplateResponse(
                request, TEMPLATE,
                {"adapter_absent": False, "not_found": True, "card_ref": card_ref},
                status_code=404,
            )
        return templates.TemplateResponse(
            request, TEMPLATE,
            {"adapter_absent": False, "not_found": False, "view": view, "card_ref": card_ref},
        )

    @app.get("/api/doc/{card_ref:path}")
    def reader_api(card_ref: str, request: Request):
        try:
            adapter = _get_adapter(request)
        except RuntimeError:
            return JSONResponse({"error": ADAPTER_ABSENT_MESSAGE}, status_code=503)
        line = _parse_line(request)
        view = build_view(adapter, request.app.state.settings, card_ref, line)
        if view is None:
            return JSONResponse({"error": "card not found"}, status_code=404)
        return JSONResponse(dataclasses.asdict(view))
