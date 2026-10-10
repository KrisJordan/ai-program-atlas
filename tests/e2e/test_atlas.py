"""Run with uv run pytest tests/e2e (Playwright Chromium required)."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import os

import pytest

from atlas.site import build
from tests.test_site import site_data  # noqa: F401

pytestmark = pytest.mark.e2e


@pytest.fixture(scope="module")
def browser():
    required = os.environ.get("ATLAS_REQUIRE_BROWSER") == "1"
    try:
        from playwright import sync_api as playwright
    except ImportError:
        if required:
            pytest.fail("ATLAS_REQUIRE_BROWSER=1 requires the Playwright Python package")
        pytest.skip("Playwright is not installed")
    with playwright.sync_playwright() as p:
        try:
            instance = p.chromium.launch()
        except playwright.Error as error:
            if required:
                pytest.fail(f"ATLAS_REQUIRE_BROWSER=1: Chromium launch failed: {error}")
            pytest.skip(f"Chromium unavailable: {error}")
        yield instance
        instance.close()


@pytest.fixture
def site(tmp_path, site_data):
    build(site_data, tmp_path / "ai-program-atlas")
    handler = partial(SimpleHTTPRequestHandler, directory=str(tmp_path))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}/ai-program-atlas/"
    server.shutdown()
    server.server_close()
    thread.join()


@pytest.fixture
def page(browser):
    context = browser.new_context(viewport={"width": 1440, "height": 1000})
    page = context.new_page()
    yield page
    context.close()


def test_filters_empty_reset_detail_and_base_path(page, site):
    from playwright.sync_api import expect
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(site)
    expect(page.locator(".program-card:visible")).to_have_count(5)
    page.locator("#filter-award").select_option("BS")
    expect(page.locator(".program-card:visible")).to_have_count(1)
    page.locator("#filter-calendar").select_option("quarter")
    expect(page.locator("#empty-state")).to_be_visible()
    page.locator("#empty-reset").click()
    expect(page.locator(".program-card:visible")).to_have_count(5)
    page.locator("#filter-cohort").select_option("National Universities")
    expect(page.locator(".program-card:visible")).to_have_count(1)
    page.get_by_role("link", name="View program").first.click()
    expect(page).to_have_url(site + "programs/test-ai-0/")
    expect(page.locator("h1")).to_have_text("Artificial Intelligence 0")
    expect(page.get_by_text("1 unique documented course records.", exact=False)).to_be_visible()
    page.reload()
    expect(page.locator("h1")).to_have_text("Artificial Intelligence 0")
    assert not errors


def test_comparison_url_reload_history_and_limit(page, site):
    from playwright.sync_api import expect
    page.goto(site)
    page.locator('[data-compare="test-ai-0"]').check()
    page.locator('[data-compare="test-ai-1"]').check()
    expect(page.locator(".compare-table thead th")).to_have_count(3)
    assert "compare=test-ai-0%2Ctest-ai-1" in page.url
    page.reload()
    expect(page.locator('[data-compare="test-ai-1"]')).to_be_checked()
    page.locator('[data-compare="test-ai-2"]').check()
    page.go_back()
    expect(page.locator('[data-compare="test-ai-2"]')).not_to_be_checked()
    page.go_forward()
    expect(page.locator('[data-compare="test-ai-2"]')).to_be_checked()
    page.locator('[data-compare="test-ai-3"]').check()
    page.locator('[data-compare="test-ai-4"]').click()
    expect(page.locator('[data-compare="test-ai-4"]')).not_to_be_checked()
    expect(page.locator("#compare-status")).to_contain_text("Choose up to four")
    expect(page.locator(".compare-table thead th")).to_have_count(5)
    assert "/ai-program-atlas/?" in page.url


def test_search_history_mobile_and_no_document_overflow(page, site):
    from playwright.sync_api import expect
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(site)
    page.locator("#search").fill("Institution 4")
    expect(page.locator(".program-card:visible")).to_have_count(1)
    page.locator('[data-compare="test-ai-4"]').check()
    page.reload()
    expect(page.locator("#search")).to_have_value("Institution 4")
    expect(page.locator('[data-compare="test-ai-4"]')).to_be_checked()
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.locator("#reset-filters").click()
    expect(page.locator(".program-card:visible")).to_have_count(5)
    page.go_back()
    expect(page.locator("#search")).to_have_value("Institution 4")


def test_no_javascript_baseline(browser, site):
    from playwright.sync_api import expect
    context = browser.new_context(java_script_enabled=False)
    page = context.new_page()
    page.goto(site)
    expect(page.locator(".program-card:visible")).to_have_count(5)
    expect(page.locator("#filters")).not_to_be_visible()
    page.get_by_role("link", name="View program").first.click()
    expect(page.locator("h1")).to_have_text("Artificial Intelligence 0")
    context.close()


def test_program_type_and_evidence_filters_preserve_history(page, site):
    from playwright.sync_api import expect
    page.goto(site)
    page.locator('#filter-evidence').select_option('pending')
    expect(page.locator('.program-card:visible')).to_have_count(2)
    page.locator('#filter-type').select_option('additional_major')
    expect(page.locator('.program-card:visible')).to_have_count(1)
    expect(page.locator('.program-card:visible .card-badges')).to_contain_text('Additional major')
    assert 'type=additional_major' in page.url and 'evidence=pending' in page.url
    page.reload()
    expect(page.locator('#filter-type')).to_have_value('additional_major')
    expect(page.locator('#filter-evidence')).to_have_value('pending')
    page.locator('#filter-evidence').select_option('complete')
    expect(page.locator('#empty-state')).to_be_visible()
    page.go_back()
    expect(page.locator('.program-card:visible')).to_have_count(1)
    expect(page.locator('#filter-evidence')).to_have_value('pending')
    page.go_forward()
    expect(page.locator('#empty-state')).to_be_visible()


def test_cohort_context_theme_matrix_and_unknown_categories(page, site):
    from playwright.sync_api import expect
    page.goto(site + '?compare=test-ai-0,test-ai-1,test-ai-2')
    ranks = page.locator('.compare-table tr').filter(has=page.get_by_role('rowheader', name='U.S. News cohort context', exact=True))
    expect(ranks).to_contain_text('U.S. News 2027 · National Universities · #20')
    expect(ranks.locator('a').first).to_have_attribute('href', 'https://example.edu/ranking')
    themes = page.locator('.theme-table tbody tr')
    expect(themes).to_have_count(2)
    ai = themes.filter(has=page.get_by_role('rowheader', name='AI methods', exact=True))
    expect(ai.locator('td').nth(0)).to_contain_text('Documented inference')
    expect(ai.locator('td').nth(0).locator('a')).to_have_attribute('href', 'https://example.edu/outcome')
    expect(ai.locator('td').nth(1)).to_have_text('Not recorded')
    expect(ai.locator('td').nth(2)).to_have_text('Not recorded')
    category = page.locator('.compare-table tr').filter(has=page.get_by_role('rowheader', name='Course categories', exact=True))
    expect(category.locator('td').nth(2)).to_have_text('Not yet extracted')
    page.reload()
    expect(page.locator('.theme-table tbody tr')).to_have_count(2)
