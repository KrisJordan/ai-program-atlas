"""Named members of an open elective pool remain options after static export."""
import json
import subprocess
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import pytest
from playwright.sync_api import expect
from atlas import db
from atlas.site import build
from tests.e2e.test_atlas import browser  # noqa: F401

pytestmark = pytest.mark.e2e
PID = 'stevens-institute-of-technology-artificial-intelligence-bs-degree'


@pytest.fixture(scope='module')
def stevens_inventory(tmp_path_factory):
    root = Path(__file__).resolve().parents[2]
    folder = tmp_path_factory.mktemp('stevens-reviewed-roles')
    relative = 'data/programs/'+PID+'.json'
    raw = subprocess.run(['git','show','HEAD:'+relative],cwd=root,check=True,capture_output=True,text=True).stdout if (root/'.git').exists() else (root/relative).read_text()
    connection = db.connect(folder/'atlas.sqlite')
    db.migrate(connection)
    db.ingest_program(connection,json.loads(raw))
    build(db.export_data(connection),folder/'ai-program-atlas')
    connection.close()
    server = ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(folder)))
    thread = Thread(target=server.serve_forever,daemon=True)
    thread.start()
    yield f'http://127.0.0.1:{server.server_port}/ai-program-atlas/'
    server.shutdown()
    server.server_close()
    thread.join()


@pytest.mark.parametrize('width',[1440,390])
def test_stevens_fixed_options_and_context_survive_comparison_history(browser,stevens_inventory,width):
    context = browser.new_context(viewport={'width':width,'height':950})
    page = context.new_page()
    errors = []
    page.on('pageerror',lambda error:errors.append(str(error)))
    try:
        page.goto(stevens_inventory+'programs/'+PID+'/')
        required = page.locator('[data-profile=required]')
        expect(required.locator('.profile-total')).to_contain_text('24 distinct')
        expect(required.locator('[data-category=foundations] strong')).to_have_text('6')
        expect(page.locator('.profile-uncertainty')).to_contain_text('25 course records are outside the fixed/option count profiles')
        page.locator('label[for=profile-options]').click()
        options = page.locator('[data-profile=options]')
        expect(options.locator('.profile-total')).to_contain_text('30 distinct')
        expect(options.locator('[data-category=applications] strong')).to_have_text('12')
        expect(options.locator('.profile-taxonomy')).to_contain_text('24 reviewed')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.goto(stevens_inventory+'?compare='+PID)
        cell = page.locator('.compare-profile-cell')
        expect(cell.locator('.profile-total')).to_contain_text('24 distinct')
        page.locator('#compare-profile').select_option('options')
        expect(cell.locator('.profile-total')).to_contain_text('30 distinct')
        page.reload()
        expect(page.locator('#compare-profile')).to_have_value('options')
        expect(cell.locator('.profile-total')).to_contain_text('30 distinct')
        page.go_back()
        expect(page.locator('#compare-profile')).to_have_value('required')
        page.go_forward()
        expect(page.locator('#compare-profile')).to_have_value('options')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert not errors
    finally:
        context.close()
