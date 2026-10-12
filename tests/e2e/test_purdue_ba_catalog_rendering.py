"""The real corrected BA must retain choices and the established profile placement."""
import json
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


@pytest.mark.parametrize('width',[1440,390])
def test_purdue_catalog_page_api_and_requirement_disclosures(browser,tmp_path,width):
    p=json.loads(Path('data/programs/purdue-ai-ba.json').read_text())
    conn=db.connect(tmp_path/'ba.sqlite');db.migrate(conn);db.ingest_program(conn,p)
    data=db.export_data(conn);conn.close()
    build(data,tmp_path/'ai-program-atlas')
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(tmp_path)))
    worker=Thread(target=server.serve_forever,daemon=True);worker.start()
    context=browser.new_context(viewport={'width':width,'height':950})
    page=context.new_page();errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    base=f'http://127.0.0.1:{server.server_port}/ai-program-atlas/'
    try:
        response=page.goto(base+'programs/purdue-ai-ba/')
        assert response.status==200
        expect(page.locator('h1')).to_have_text('Artificial Intelligence')
        expect(page.locator('body')).to_contain_text('Department of Philosophy')
        expect(page.locator('#requirement-purdue-ai-ba-major > details')).to_have_attribute('open','')
        expect(page.locator('#requirement-purdue-ai-ba-area-a > details')).to_have_attribute('open','')
        expect(page.locator('#requirement-purdue-ai-ba-area-b > details')).to_have_attribute('open','')
        expect(page.locator('#requirement-purdue-ai-ba-area-d > details')).not_to_have_attribute('open','')
        expect(page.locator('#requirement-purdue-ai-ba-calculus > details')).not_to_have_attribute('open','')
        page.locator('#requirement-purdue-ai-ba-calculus > details > summary').focus()
        page.keyboard.press('Enter')
        expect(page.locator('#requirement-purdue-ai-ba-calculus')).to_contain_text('MA 16010 AND MA 16020, OR MA 16100, OR MA 16500')
        assert page.evaluate("document.querySelector('#requirements').compareDocumentPosition(document.querySelector('#curriculum')) & Node.DOCUMENT_POSITION_FOLLOWING")
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(tmp_path/f'purdue-ba-{width}.png'),full_page=True)
        api=page.request.get(base+'api/v1/programs/purdue-ai-ba.json')
        assert api.status==200
        payload=api.json()
        record=payload.get('program',payload)
        assert len(record['courses'])==46
        assert record['catalog_year']=='2026–2027'
        assert record['award_level']=='BA'
        assert not any(c['code']=='CS 10100' for c in record['courses'])
        page.goto(base+'?view=cards&award=BA')
        page.reload()
        page.goto(base+'programs/purdue-ai-ba/')
        page.go_back();assert 'award=BA' in page.url
        page.go_forward();expect(page.locator('h1')).to_have_text('Artificial Intelligence')
        assert not errors
    finally:
        context.close();server.shutdown();server.server_close();worker.join()
