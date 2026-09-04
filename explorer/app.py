"""FastAPI application factory (integrator-owned). ARCHITECTURE.md sections 1-2, 4.

Wiring only: settings, templates (one Jinja2 environment over every module's
templates directory), static mounts, module route registration, /healthz.
Module packages register their own routes through `register(app)` in
`explorer/<module>/routes.py`; a module that is not built yet is skipped, so the
app boots at every wave. The adapter is created lazily and shared on app.state.
"""
from __future__ import annotations

import importlib
import os
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import ChoiceLoader, Environment, FileSystemLoader, select_autoescape

from explorer import __version__
from explorer.config import Settings
from explorer.models import AUTHORITY_NOTICE

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
# Registration order fixes template lookup precedence (ChoiceLoader) and nav order.
MODULES = ("web", "catalog", "search", "reader", "lineage", "diagnostics")


def _module_dir(mod: str, sub: str) -> str | None:
    p = os.path.join(PACKAGE_DIR, mod, sub)
    return p if os.path.isdir(p) else None


def build_templates() -> Jinja2Templates:
    dirs = [d for d in (_module_dir(m, "templates") for m in MODULES) if d]
    env = Environment(
        loader=ChoiceLoader([FileSystemLoader(d) for d in dirs]) if dirs else ChoiceLoader([]),
        autoescape=select_autoescape(["html", "xml"]),
        enable_async=False,
    )
    env.globals["app_version"] = __version__
    env.globals["authority_notice"] = AUTHORITY_NOTICE
    return Jinja2Templates(env=env)


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_templates(request: Request) -> Jinja2Templates:
    return request.app.state.templates


def get_adapter(request: Request) -> Any:
    """The shared CorpusAdapter (created on first use). Raises RuntimeError if the
    corpus_adapter module is not built yet -- routes that need it surface a 503."""
    app = request.app
    adapter = getattr(app.state, "adapter", None)
    if adapter is None:
        try:
            mod = importlib.import_module("explorer.corpus_adapter.adapter")
        except ModuleNotFoundError as exc:  # pragma: no cover - only before wave 1 lands
            raise RuntimeError("corpus_adapter is not built") from exc
        adapter = mod.CorpusAdapter(app.state.settings)
        app.state.adapter = adapter
    return adapter


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    app = FastAPI(
        title="RHACO Corpus Explorer",
        version=__version__,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.settings = settings
    app.state.templates = build_templates()
    app.state.adapter = None

    for mod in MODULES:
        static_dir = _module_dir(mod, "static")
        if static_dir:
            app.mount(f"/static/{mod}", StaticFiles(directory=static_dir), name=f"static-{mod}")

    for mod in MODULES:
        try:
            routes = importlib.import_module(f"explorer.{mod}.routes")
        except ModuleNotFoundError:
            continue
        register = getattr(routes, "register", None)
        if callable(register):
            register(app)

    @app.get("/healthz")
    def healthz(request: Request) -> JSONResponse:
        payload: dict[str, Any] = {
            "status": "ok",
            "version": __version__,
            "db": settings.db_path or "module default",
            "docs_root": settings.docs_root or "module default",
            "adapter": "absent",
            "vector": None,
        }
        try:
            adapter = get_adapter(request)
        except RuntimeError:
            return JSONResponse(payload)
        payload["adapter"] = "present"
        try:
            payload["db"] = adapter.db_path
            payload["docs_root"] = adapter.docs_root
            va = adapter.vector_availability()
            payload["vector"] = {"available": va.available, "reason": va.reason, "model_tag": va.model_tag}
        except Exception as exc:  # noqa: BLE001 -- the health endpoint never raises; it reports the failure class
            payload["status"] = "degraded"
            payload["error"] = f"{type(exc).__name__}: {exc}"
        return JSONResponse(payload)

    return app
