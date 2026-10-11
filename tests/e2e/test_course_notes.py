"""Native note disclosures remain usable without JavaScript and on narrow screens."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest
from playwright.sync_api import expect

from atlas.site import build
from tests.e2e.test_atlas import browser  # noqa: F401
from tests.test_site import site_data  # noqa: F401

pytestmark=pytest.mark.e2e


@pytest.fixture
def notes_site(tmp_path,site_data):
    site_data['programs'][0]['courses'][0]['notes']=[
        'Permission is required for this historical offering; it has not been granted by this record.',
        'Version-specific evidence: https://example.edu/'+('long-source-locator-'*20)+' <untrusted-markup>',
    ]
    for duplicate in site_data['programs'][0]['courses']:
        duplicate['notes']=list(site_data['programs'][0]['courses'][0]['notes'])
    site_data['programs'][0]['sources'][0]['locator'] = (
        'Selected public Eligibility tab; source SHA256 ' + '3c904a76fa15e9747' * 4
    )
    build(site_data,tmp_path/'ai-program-atlas')
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(tmp_path)))
    thread=Thread(target=server.serve_forever,daemon=True);thread.start()
    yield f'http://127.0.0.1:{server.server_port}/ai-program-atlas/'
    server.shutdown();server.server_close();thread.join()


@pytest.mark.parametrize('width',[1440,390])
def test_course_notes_keyboard_no_javascript_and_mobile_overflow(browser,notes_site,width):
    context=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=False)
    page=context.new_page()
    try:
        page.goto(notes_site+'programs/test-ai-0/#course-course-0')
        locator = page.locator('.sources > li > p').filter(has_text='source SHA256')
        expect(locator).to_contain_text('3c904a76fa15e9747' * 4)
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
        row=page.locator('#course-course-0')
        notes=row.locator('.course-notes');summary=notes.locator('summary')
        expect(summary).to_have_text('Course notes (2) for AI 001')
        assert notes.get_attribute('open') is None
        summary.focus();page.keyboard.press('Enter')
        expect(notes).to_have_attribute('open','')
        expect(notes.locator('li').first).to_contain_text('Permission is required')
        expect(notes.locator('li').last).to_contain_text('<untrusted-markup>')
        assert notes.locator('untrusted-markup').count()==0
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
        assert row.locator('.course-description').is_visible()
        page.keyboard.press('Enter')
        assert notes.get_attribute('open') is None
        page.reload()
        assert notes.get_attribute('open') is None
        expect(summary).to_be_visible()
    finally:
        context.close()
