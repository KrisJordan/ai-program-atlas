"""Publication context stays usable on direct, mobile and history navigation."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
import pytest
from playwright.sync_api import expect
from atlas.site import build
from tests.test_site import site_data  # noqa: F401
from tests.test_csrankings_context_ui import research_site_data  # noqa: F401
from tests.e2e.test_atlas import browser  # noqa: F401

pytestmark=pytest.mark.e2e


@pytest.fixture
def research_site(tmp_path,research_site_data):
    build(research_site_data,tmp_path/'nested'/'atlas','/nested/atlas/')
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(tmp_path)))
    thread=Thread(target=server.serve_forever,daemon=True);thread.start()
    yield f'http://127.0.0.1:{server.server_port}/nested/atlas/'
    server.shutdown();server.server_close();thread.join()


@pytest.mark.parametrize('width',[1440,390])
def test_research_context_direct_keyboard_comparison_history(browser,research_site,width):
    context=browser.new_context(viewport={'width':width,'height':1000})
    page=context.new_page();errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
    try:
        assert page.goto(research_site+'programs/test-ai-0/').status==200
        panel=page.locator('#research-context')
        assert panel.evaluate("node => node.previousElementSibling.classList.contains('cohort-context')")
        assert panel.evaluate("node => node.nextElementSibling.id") == 'sources'
        expect(panel.locator('tbody tr')).to_have_count(6)
        expect(panel).to_contain_text('#175 of 197')
        expect(panel).to_contain_text('do not measure undergraduate teaching')
        panel.get_by_role('region',name='CSRankings research fields').focus()
        expect(panel.get_by_role('region',name='CSRankings research fields')).to_be_focused()
        page.reload();expect(panel).to_contain_text('3.2')
        panel.get_by_role('link').click()
        expect(page).to_have_url(research_site+'methodology/#research')
        provenance=page.locator('.research-provenance')
        provenance.locator('summary').focus();page.keyboard.press('Enter')
        expect(provenance).to_have_attribute('open','')
        expect(provenance).to_contain_text('No broader permission is inferred')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.goto(research_site+'?compare=test-ai-0,test-ai-1')
        expect(page.locator('.compare-table')).to_have_count(1)
        matrix=page.locator('.research-comparison')
        expect(matrix.locator('tbody tr')).to_have_count(6)
        expect(matrix).to_contain_text('#175 of 197')
        expect(matrix).to_contain_text('No selected publication output')
        expect(matrix.locator('[data-research-field="aggregate"] td').first).to_contain_text('3.2')
        page.locator('#compare-profile').select_option('options');page.reload()
        expect(page.locator('#compare-profile')).to_have_value('options')
        expect(matrix).to_contain_text('#175 of 197')
        page.locator('#compare-profile').select_option('required');page.go_back()
        expect(page.locator('#compare-profile')).to_have_value('options')
        page.go_forward();expect(page.locator('#compare-profile')).to_have_value('required')
        matrix.get_by_role('region',name='Institution research comparison').focus()
        expect(matrix.get_by_role('region',name='Institution research comparison')).to_be_focused()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert not errors
    finally:context.close()
