"""Source-verified Case role counts survive persistence, static pages and comparison."""
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
PIDS = [f'case-western-reserve-university-artificial-intelligence-{award}-degree' for award in ['ba','bs']]


@pytest.fixture(scope='module')
def case_inventory(tmp_path_factory):
    root = Path(__file__).resolve().parents[2]
    folder = tmp_path_factory.mktemp('case-independent-roles')
    connection = db.connect(folder/'atlas.sqlite')
    db.migrate(connection)
    for pid in PIDS:
        relative = 'data/programs/'+pid+'.json'
        raw = subprocess.run(['git','show','HEAD:'+relative],cwd=root,check=True,capture_output=True,text=True).stdout if (root/'.git').exists() else (root/relative).read_text()
        db.ingest_program(connection,json.loads(raw))
    data = db.export_data(connection)
    connection.close()
    build(data,folder/'ai-program-atlas')
    server = ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(folder)))
    thread = Thread(target=server.serve_forever,daemon=True)
    thread.start()
    yield f'http://127.0.0.1:{server.server_port}/ai-program-atlas/'
    server.shutdown()
    server.server_close()
    thread.join()


@pytest.mark.parametrize('width',[1440,390])
def test_case_role_identity_and_context_counts_in_real_views(browser,case_inventory,width):
    context = browser.new_context(viewport={'width':width,'height':950})
    page = context.new_page()
    errors = []
    page.on('pageerror',lambda error:errors.append(str(error)))
    try:
        for pid,fixed,options,records in zip(PIDS,[8,9],[585,595],[639,650]):
            page.goto(case_inventory+'programs/'+pid+'/')
            required = page.locator('[data-profile=required]')
            expect(required.locator('.profile-total')).to_contain_text(f'{fixed} distinct')
            expect(required.locator('[data-category=foundations] strong')).to_have_text('2')
            expect(page.locator('.profile-uncertainty')).to_contain_text('97 course identities are outside the fixed/option count profiles')
            expect(page.locator('.profile-uncertainty')).not_to_contain_text('unresolved requirement roles')
            page.locator('label[for=profile-options]').click()
            choice = page.locator('[data-profile=options]')
            expect(choice.locator('.profile-total')).to_contain_text(f'{options} distinct')
            expect(choice.locator('.profile-identity')).to_contain_text(f'{records} retained source-code records')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.goto(case_inventory+'?compare='+','.join(PIDS))
        for cell,count in zip(page.locator('.compare-profile-cell').all(),[8,9]):
            expect(cell.locator('.profile-total')).to_contain_text(f'{count} distinct')
            expect(cell.locator('.profile-uncertainty')).to_contain_text('97 course identities are outside the fixed/option count profiles')
        page.locator('#compare-profile').select_option('options')
        for cell,count in zip(page.locator('.compare-profile-cell').all(),[585,595]):
            expect(cell.locator('.profile-total')).to_contain_text(f'{count} distinct')
        page.reload()
        expect(page.locator('#compare-profile')).to_have_value('options')
        expect(page.locator('.compare-profile-cell').first.locator('.profile-total')).to_contain_text('585 distinct')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert not errors
    finally:
        context.close()
