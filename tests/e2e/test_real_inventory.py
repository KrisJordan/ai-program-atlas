"""Smoke test the actual maintained evidence after a clean SQLite reconstruction."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import pytest
from playwright.sync_api import expect

from atlas import db
from atlas.cli import ingest_all
from atlas.site import build
from tests.e2e.test_atlas import open_filters, browser  # noqa: F401

pytestmark = pytest.mark.e2e


def test_real_database_pages_comparison_and_mobile(browser, tmp_path):
    root = Path(__file__).resolve().parents[2]
    conn = db.connect(tmp_path / "atlas.sqlite")
    db.migrate(conn)
    ingest_all(conn, root / "data")
    data = db.export_data(conn)
    conn.close()
    build(data, tmp_path / "ai-program-atlas")
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(tmp_path))
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    context = browser.new_context(viewport={"width": 1440, "height": 1000})
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    base = f"http://127.0.0.1:{server.server_port}/ai-program-atlas/"
    try:
        page.goto(base + '?view=cards')
        expect(page.locator(".program-card")).to_have_count(len(data["programs"]))
        for summary in page.locator(".program-family:visible > summary").all():
            summary.click()
        expect(page.locator(".program-card:visible")).to_have_count(sum(p["program_kind"] in ("degree", "additional_major") for p in data["programs"]))
        page.locator('[data-compare="purdue-ai-bs"]').check()
        page.locator('[data-compare="penn-bse-ai"]').check()
        page.reload()
        expect(page.locator(".compare-table thead th")).to_have_count(3)
        expect(page.locator(".compare-table")).to_contain_text("Course units")
        expect(page.locator(".compare-table")).to_contain_text("Semester hours")
        for pid in [
            "cmu-bs-ai",
            "penn-bse-ai",
            "purdue-ai-ba",
            "penn-state-ai-engineering-minor",
            "denison-mlai-minor",
            "furman-ai-bs",
        ]:
            response = page.goto(base + f"programs/{pid}/")
            assert response.status == 200
            expect(page.locator("h1")).to_be_visible()
            expect(page.locator("body")).not_to_contain_text("NaN")
        for path in ["", "coverage/", "methodology/", "programs/penn-bse-ai/", "programs/stanford-ai-track/"]:
            page.set_viewport_size({"width": 390, "height": 844})
            page.goto(base + path)
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        assert not errors
    finally:
        context.close()
        server.shutdown()
        server.server_close()
        thread.join()


@pytest.mark.parametrize('width',[1440,390])
def test_real_family_variants_from_fresh_cli_database(browser,tmp_path,width):
    """The first reviewed family must survive CLI reconstruction and concrete URLs."""
    import json
    from atlas.cli import main
    root=Path(__file__).resolve().parents[2]
    database=tmp_path/'family.sqlite'
    assert main(['--db',str(database),'ingest','--data-dir',str(root/'data')]) in (0,None)
    assert main(['--db',str(database),'build','--output',str(tmp_path/'ai-program-atlas')]) in (0,None)
    data=json.loads((tmp_path/'ai-program-atlas/data.json').read_text())
    assert data.get('families'), 'The release must contain its reviewed program family.'
    family=next(f for f in data['families'] if f['id']=='northeastern-ai-combined-degrees')
    assert len(family['variant_ids'])>=3
    programs={p['id']:p for p in data['programs']}
    members=[programs[pid] for pid in family['variant_ids']]
    assert all(p.get('family',{}).get('id')==family['id'] for p in members)
    first,second=members[:2]
    discipline=next((d for d in first['family']['disciplines'] if d not in second['family']['disciplines']),first['family']['disciplines'][0])
    matching=[p for p in members if discipline in p['family']['disciplines']]
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(tmp_path)))
    thread=Thread(target=server.serve_forever,daemon=True);thread.start()
    context=browser.new_context(viewport={'width':width,'height':950});page=context.new_page();errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    base=f'http://127.0.0.1:{server.server_port}/ai-program-atlas/'
    try:
        page.goto(base + '?view=cards')
        panel=page.locator('[data-family-id="'+family['id']+'"]')
        expect(panel).to_be_visible()
        panel.locator(':scope > summary').focus()
        page.keyboard.press('Enter')
        expect(panel).to_have_attribute('open','')
        expect(panel.locator('.program-card:visible')).to_have_count(len(members))
        assert 'expand=' in page.url
        page.reload()
        expect(panel).to_have_attribute('open','')
        open_filters(page)
        page.locator('#filter-discipline').select_option(discipline)
        page.locator('#apply-filters').click()
        expect(panel.locator('.program-card:visible')).to_have_count(len(matching))
        page.locator('[data-compare="'+first['id']+'"]').check()
        open_filters(page)
        page.locator('#filter-discipline').select_option('')
        page.locator('#apply-filters').click()
        page.locator('[data-compare="'+second['id']+'"]').check()
        expect(page.locator('.compare-table thead th')).to_have_count(3)
        expect(page.locator('.compare-table')).to_contain_text(first['family']['variant_label'])
        expect(page.locator('.compare-table')).to_contain_text(second['family']['variant_label'])
        family_row=page.locator('.compare-table tr').filter(has=page.get_by_role('rowheader',name='Program family',exact=True))
        expect(family_row).to_contain_text(family['classification_kind'].replace('_',' ').capitalize())
        membership_row=page.locator('.compare-table tr').filter(has=page.get_by_role('rowheader',name='Concrete variant / disciplines',exact=True))
        expect(membership_row).to_contain_text('Membership evidence: Source stated')
        expect(membership_row).to_contain_text('Relationship: Integrated program')
        shared=page.locator('.compare-table tr').filter(has=page.get_by_role('rowheader',name='Shared family requirements',exact=True))
        expect(shared).to_contain_text(family['shared_requirements'][0]['title'])
        variants=page.locator('.compare-table tr').filter(has=page.get_by_role('rowheader',name='Variant requirements / changes',exact=True))
        for p in [first,second]:
            local=next(r for r in p['requirements'] if r.get('origin') in ['variant','replacement'])
            expect(variants).to_contain_text(local['title'])
        page.reload()
        expect(page.locator('.compare-table thead th')).to_have_count(3)
        open_filters(page)
        page.locator('#filter-discipline').select_option(discipline)
        page.locator('#apply-filters').click()
        page.go_back();expect(page.locator('#filter-discipline')).to_have_value('')
        page.go_forward();expect(page.locator('#filter-discipline')).to_have_value(discipline)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        response=page.goto(base+'programs/'+first['id']+'/')
        assert response.status==200
        expect(page.locator('.family-context')).to_contain_text(first['family']['variant_label'])
        expect(page.locator('.requirements')).to_contain_text('Shared family requirement')
        expect(page.locator('.requirements')).to_contain_text('Local variant requirement')
        expect(page.locator('.requirements')).to_contain_text('AI core')
        page.reload()
        expect(page.locator('h1')).to_have_text(first['title'])
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert not errors
    finally:
        context.close();server.shutdown();server.server_close();thread.join()
