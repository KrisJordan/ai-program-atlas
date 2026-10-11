"""Additional-major evidence stays accessible without whole-degree claims."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest
from playwright.sync_api import expect

from atlas.site import build
from tests.test_site import site_data  # noqa: F401
from tests.test_additional_major_audit import record, review
from tests.e2e.test_atlas import browser  # noqa: F401

pytestmark = pytest.mark.e2e


@pytest.fixture
def reviewed_site(tmp_path, site_data):
    p = site_data['programs'][0]
    p.update(program_kind='additional_major', award_level='other',
             major_relationship=record()['major_relationship'])
    p['sources'].extend(record()['sources'])
    p['additional_major_audit'] = review(p)
    p['additional_major_audit']['dimensions']['choice_rules'].update(
        status='partial', summary='The named options were checked.',
        limitations=['The advisor-approved open pool has no finite published membership.'])
    build(site_data, tmp_path/'ai-program-atlas')
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(tmp_path)))
    thread = Thread(target=server.serve_forever, daemon=True); thread.start()
    yield f'http://127.0.0.1:{server.server_port}/ai-program-atlas/'
    server.shutdown(); server.server_close(); thread.join()


@pytest.mark.parametrize('width', [1440, 390])
def test_review_scope_keyboard_direct_reload_comparison(browser, reviewed_site, width):
    context = browser.new_context(viewport={'width': width, 'height': 1000})
    page = context.new_page(); errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    try:
        assert page.goto(reviewed_site+'programs/test-ai-0/').status == 200
        panel = page.locator('.additional-major-audit-program')
        expect(panel).to_contain_text('does not certify the complete host degree')
        expect(page.locator('.degree-audit-program')).to_have_count(0)
        expect(panel.locator('[data-review-dimension="eligibility"]')).to_contain_text('Verified within stated scope')
        choices = panel.locator('[data-review-dimension="choice_rules"]')
        expect(choices).to_contain_text('Partially reviewed')
        choices.locator('summary').focus(); page.keyboard.press('Enter')
        expect(choices.locator('details')).to_have_attribute('open', '')
        expect(choices).to_contain_text('no finite published membership')
        page.reload(); expect(panel).to_be_visible()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.goto(reviewed_site+'?compare=test-ai-0,test-ai-1')
        expect(page.locator('.compare-table thead th')).to_have_count(3)
        page.locator('#compare-profile').select_option('options'); page.reload()
        expect(page.locator('#compare-profile')).to_have_value('options')
        page.locator('#compare-profile').select_option('required'); page.go_back()
        expect(page.locator('#compare-profile')).to_have_value('options'); page.go_forward()
        expect(page.locator('#compare-profile')).to_have_value('required')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert not errors
    finally:
        context.close()
