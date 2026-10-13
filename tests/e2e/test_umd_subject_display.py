"""Canonical categories stay separate while all visible aggregate views sum them."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from pathlib import Path
import json

import pytest
from playwright.sync_api import expect

from atlas import db
from atlas.site import build
from tests.e2e.test_atlas import browser  # noqa: F401

BA='university-of-maryland-college-park-human-centered-ai-ba-degree'
BS='university-of-maryland-college-park-artificial-intelligence-computational-structures-for-ai-systems-bsai-degree'
pytestmark=pytest.mark.e2e


@pytest.mark.parametrize('width',[1440,390])
def test_umd_table_comparison_and_detail_share_display_groups(browser,tmp_path,width):
    conn=db.connect(tmp_path/'umd.sqlite');db.migrate(conn)
    for pid in [BA,BS]:db.ingest_program(conn,json.loads(Path('data/programs',pid+'.json').read_text()))
    data=db.export_data(conn);conn.close()
    build(data,tmp_path/'ai-program-atlas')
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(tmp_path)))
    worker=Thread(target=server.serve_forever,daemon=True);worker.start()
    context=browser.new_context(viewport={'width':width,'height':950});page=context.new_page();errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    base=f'http://127.0.0.1:{server.server_port}/ai-program-atlas/'
    try:
        page.goto(base+f'?compare={BA},{BS}')
        table=page.locator('.directory-table').last
        expect(table.locator('thead tr').nth(1).locator('th')).to_have_text(['Math + Statistics','Computing + Systems','AI + ML','Human Context','Applications','Other'])
        expect(table.locator('th.required-heading')).to_have_text('Required Curriculum (Electives Counted Separately)')
        expect(table.locator('th.required-heading')).to_have_attribute('colspan','6')
        for pid,amount in [(BA,'3'),(BS,'4')]:
            expect(page.locator(f'[data-row-id="{pid}"] [data-required-category=computing_systems]')).to_have_text(amount)
        cells=page.locator('.compare-profile-cell')
        expect(cells).to_have_count(2)
        expect(cells.nth(0).locator('.mini-counts dt').first).to_have_text('Math + Statistics')
        for i,amount in [(0,'3'),(1,'4')]:
            label=cells.nth(i).locator('dt',has_text='Computing + Systems')
            expect(label.locator('xpath=following-sibling::dd[1]')).to_have_text(amount)
        page.locator('#compare-profile').select_option('options')
        expect(cells.nth(1).locator('dt',has_text='Computing + Systems').locator('xpath=following-sibling::dd[1]')).to_have_text('10')
        page.reload();expect(page.locator('#compare-profile')).to_have_value('options')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.goto(base+f'programs/{BA}/')
        required=page.locator('[data-profile=required]')
        expect(required.locator('[data-category=computing_systems] strong')).to_have_text('3')
        expect(required.locator('[data-category=ai_ml] strong')).to_have_text('2')
        expect(required.locator('.category-row > span').nth(0)).to_have_text('Math + Statistics')
        expect(required.locator('.category-row > span').nth(1)).to_have_text('Computing + Systems')
        expect(required.locator('.category-row > span').nth(2)).to_have_text('AI + ML')
        page.locator('label[for=profile-options]').click()
        expect(page.locator('[data-profile=options] [data-category=computing_systems] strong')).to_have_text('0 mapped')
        api=page.request.get(base+f'api/v1/profiles/{BA}.json').json()
        assert api['required']['categories']['foundations']==3
        assert api['required']['categories']['systems']==0
        assert 'computing_systems' not in api['required']['categories']
        assert api['required']['count']==10 and api['options']['count']==59
        assert not errors
    finally:
        context.close();server.shutdown();server.server_close();worker.join()
