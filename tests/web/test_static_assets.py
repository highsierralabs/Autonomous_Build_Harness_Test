"""Static asset serving tests for explorer/web (dispatch task B9 item 4,
second bullet): /static/web/app.css and /static/web/app.js each 200 with a
non-empty body."""
from __future__ import annotations


def test_app_css_served(fixture_client):
    resp = fixture_client.get("/static/web/app.css")
    assert resp.status_code == 200
    assert len(resp.content) > 0
    assert "text/css" in resp.headers.get("content-type", "")


def test_app_js_served(fixture_client):
    resp = fixture_client.get("/static/web/app.js")
    assert resp.status_code == 200
    assert len(resp.content) > 0
    ctype = resp.headers.get("content-type", "")
    assert "javascript" in ctype or "ecmascript" in ctype
