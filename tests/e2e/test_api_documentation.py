# ruff: noqa: F811
"""Documentation works as a static accessible page with Pages base-path navigation."""
import pytest
from playwright.sync_api import expect

from tests.e2e.test_atlas import browser, page, site  # noqa: F401
from tests.test_site import site_data  # noqa: F401

pytestmark = pytest.mark.e2e


@pytest.mark.parametrize('width', [1440, 390])
def test_api_docs_downloads_status_history_and_mobile(page, site, width):
    page.set_viewport_size({'width': width, 'height': 900})
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(site)
    page.locator('footer').get_by_role('link', name='JSON API').click()
    expect(page).to_have_url(site + 'api/')
    expect(page.get_by_role('heading', name='Static JSON API', exact=True)).to_be_visible()
    expect(page.get_by_role('table')).to_have_count(1)
    expect(page.locator('main')).to_have_count(1)
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
    for path in ['index.json', 'dataset.json', 'programs.json', 'metadata.json',
                 'institutions.json', 'families.json', 'rankings.json', 'openapi.json',
                 'schema.json', 'programs/test-ai-0.json', 'courses/test-ai-0.json',
                 'requirements/test-ai-0.json', 'profiles/test-ai-0.json']:
        response = page.request.get(site + 'api/v1/' + path)
        assert response.ok, path
        assert 'application/json' in response.headers['content-type']
        response.json()
    missing = page.request.get(site + 'api/v1/programs/nonexistent.json')
    assert missing.status == 404
    assert 'text/html' in missing.headers['content-type']
    # Query strings cannot be mistaken for runtime filtering.
    assert page.request.get(site + 'api/v1/programs.json?q=missing').json() == page.request.get(
        site + 'api/v1/programs.json').json()
    page.reload()
    expect(page.get_by_role('heading', name='Static JSON API', exact=True)).to_be_visible()
    page.go_back()
    expect(page).to_have_url(site)
    page.go_forward()
    expect(page).to_have_url(site + 'api/')
    page.get_by_role('link', name='Skip to content').focus()
    page.keyboard.press('Enter')
    assert page.evaluate('document.activeElement.id') == 'main'
    assert not errors
