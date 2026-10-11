"""Official course titles with missing codes remain usable without invented labels."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest
from playwright.sync_api import expect

from atlas.site import build
from tests.test_site import site_data  # noqa: F401
from tests.e2e.test_atlas import browser  # noqa: F401

pytestmark = pytest.mark.e2e


@pytest.fixture
def uncoded_site(tmp_path, site_data):
    program = site_data['programs'][0]
    course = program['courses'][0]
    course.update(code=None, name='Introduction to Algorithmic Economics', category='other', credit_unit='unknown')
    program['courses'] = [course]
    program['requirements'] = [dict(id='uncoded-fixed', title='Required named course', kind='all', parent_id=None, course_ids=[course['id']], count=None, credits=None, credit_unit='unknown', category='other')]
    build(site_data, tmp_path/'ai-program-atlas')
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(tmp_path)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f'http://127.0.0.1:{server.server_port}/ai-program-atlas/'
    server.shutdown()
    server.server_close()
    thread.join()


@pytest.mark.parametrize('width', [1440, 390])
def test_uncoded_named_course_direct_compare_history_mobile(browser, uncoded_site, width):
    context = browser.new_context(viewport={'width': width, 'height': 1000})
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    try:
        assert page.goto(uncoded_site+'programs/test-ai-0/').status == 200
        row = page.locator('#course-course-0')
        expect(row).to_contain_text('Unknown')
        expect(row).to_contain_text('Introduction to Algorithmic Economics')
        expect(page.locator('a[href="#course-course-0"]').first).to_contain_text('Code unknown')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert page.goto(uncoded_site+'?compare=test-ai-0,test-ai-1').status == 200
        expect(page.locator('.compare-table thead th')).to_have_count(3)
        page.locator('#compare-profile').select_option('options')
        page.reload()
        expect(page.locator('#compare-profile')).to_have_value('options')
        page.locator('#compare-profile').select_option('required')
        page.go_back()
        expect(page.locator('#compare-profile')).to_have_value('options')
        page.go_forward()
        expect(page.locator('#compare-profile')).to_have_value('required')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert errors == []
    finally:
        context.close()
