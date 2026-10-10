"""Smoke test the actual maintained evidence after a clean SQLite reconstruction."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import pytest
from playwright.sync_api import expect

from atlas import db
from atlas.cli import ingest_all
from atlas.site import build
from tests.e2e.test_atlas import browser  # noqa: F401

pytestmark = pytest.mark.e2e


def test_real_database_pages_comparison_and_mobile(browser, tmp_path):
    root = Path(__file__).resolve().parents[2]
    conn = db.connect(tmp_path / "atlas.sqlite")
    db.migrate(conn)
    ingest_all(conn, root / "data")
    data = db.export_data(conn)
    conn.close()
    build(data, tmp_path / "ai-program-atlas")
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(tmp_path))
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    context = browser.new_context(viewport={"width": 1440, "height": 1000})
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    base = f"http://127.0.0.1:{server.server_port}/ai-program-atlas/"
    try:
        page.goto(base)
        expect(page.locator(".program-card:visible")).to_have_count(len(data["programs"]))
        page.locator('[data-compare="purdue-ai-bs"]').check()
        page.locator('[data-compare="penn-bse-ai"]').check()
        page.reload()
        expect(page.locator(".compare-table thead th")).to_have_count(3)
        expect(page.locator(".compare-table")).to_contain_text("Course units")
        expect(page.locator(".compare-table")).to_contain_text("Semester hours")
        for pid in [
            "cmu-bs-ai",
            "penn-bse-ai",
            "purdue-ai-ba",
            "penn-state-ai-engineering-minor",
            "denison-mlai-minor",
            "furman-ai-bs",
        ]:
            response = page.goto(base + f"programs/{pid}/")
            assert response.status == 200
            expect(page.locator("h1")).to_be_visible()
            expect(page.locator("body")).not_to_contain_text("NaN")
        for path in ["", "coverage/", "methodology/", "programs/penn-bse-ai/"]:
            page.set_viewport_size({"width": 390, "height": 844})
            page.goto(base + path)
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        assert not errors
    finally:
        context.close()
        server.shutdown()
        server.server_close()
        thread.join()
