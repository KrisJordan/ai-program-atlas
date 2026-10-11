"""Published parent evidence survives a clean build and every presentation surface."""
import io
import subprocess
import shutil
import tarfile
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import pytest
from playwright.sync_api import expect

from atlas import db
from atlas.cli import ingest_all
from atlas.site import build
from tests.e2e.test_atlas import browser, open_filters  # noqa: F401

pytestmark = pytest.mark.e2e


@pytest.fixture(scope='module')
def parent_inventory(tmp_path_factory):
    """Exclude concurrent uncommitted research from this release-data regression."""
    root = Path(__file__).resolve().parents[2]
    folder = tmp_path_factory.mktemp('committed-parent-evidence')
    if (root/'.git').exists():
        archive = subprocess.run(['git', 'archive', 'HEAD', 'data', 'research/degree-audit'], cwd=root, check=True, capture_output=True).stdout
        with tarfile.open(fileobj=io.BytesIO(archive)) as source:
            source.extractall(folder, filter='data')
    else:
        # Release source archives already contain a frozen snapshot and no .git.
        shutil.copytree(root/'data', folder/'data')
        shutil.copytree(root/'research/degree-audit', folder/'research/degree-audit')
    connection = db.connect(folder/'atlas.sqlite')
    db.migrate(connection)
    ingest_all(connection, folder/'data')
    data = db.export_data(connection)
    connection.close()
    build(data, folder/'ai-program-atlas')
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(folder)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f'http://127.0.0.1:{server.server_port}/ai-program-atlas/', data
    server.shutdown()
    server.server_close()
    thread.join()


@pytest.mark.parametrize('width', [1440, 390])
def test_committed_parent_evidence_cards_details_comparison(browser, parent_inventory, width):
    base, data = parent_inventory
    programs = {p['id']: p for p in data['programs']}
    concentration_ids = [p['id'] for p in data['programs'] if p['program_kind']=='concentration']
    ohio = 'ohio-state-ai-specialization'
    partials = ['boston-college-artificial-intelligence-concentration-concentration-concentration', 'ut-austin-cs-ml-ai-concentration']
    unknown = 'rit-ai-society-immersion'
    wpi = 'wpi-ai-advanced-methods-concentration'
    assert len(programs[ohio]['parent_programs']) == 2
    assert all(programs[pid]['parent_program_review']['status']=='partial' for pid in partials)
    assert programs[unknown]['parent_program_review']['status']=='unknown'
    assert programs[wpi]['parent_programs'][0]['award_label']=='Bachelor of Science'
    assert programs[wpi]['parent_programs'][0]['award_level'] is None
    context = browser.new_context(viewport={'width':width, 'height':1000})
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    try:
        page.goto(base+'?path_nu=concentrations&path_lac=concentrations')
        expect(page.locator('#filter-panel')).not_to_have_attribute('open', '')
        for pid in concentration_ids:
            card = page.locator(f'[data-program-id="{pid}"] .parent-programs')
            expect(card).to_be_visible()
            for parent in programs[pid].get('parent_programs', []):
                expect(card).to_contain_text(parent['title'])
                expect(card).to_contain_text(parent.get('award_label') or parent.get('award_level') or 'Award not yet verified')
        expect(page.locator(f'[data-program-id="{unknown}"] .parent-programs')).to_contain_text('Not yet verified')
        for pid in partials:
            expect(page.locator(f'[data-program-id="{pid}"] .parent-programs')).to_contain_text('Award not yet verified')
        page.reload()
        expect(page.locator('#tab-nu-concentrations')).to_have_attribute('aria-selected','true')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        for pid in [ohio, *partials, unknown, wpi]:
            response = page.goto(base+f'programs/{pid}/')
            assert response.status == 200
            detail = page.locator('.detail-hero .parent-programs')
            expect(detail).to_be_visible()
            for parent in programs[pid].get('parent_programs', []):
                expect(detail).to_contain_text(parent['title'])
                source_ids = set(parent['source_ids'])
                urls = {s['url'] for s in programs[pid]['sources'] if s['id'] in source_ids}
                for url in urls:
                    assert url in detail.locator('a').evaluate_all('(links)=>links.map(a=>a.href)')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        selected = [ohio, partials[0], unknown, wpi]
        page.goto(base+'?path_nu=concentrations&path_lac=concentrations&compare='+','.join(selected))
        row = page.locator('.compare-table tr').filter(has=page.get_by_role('rowheader', name='Parent program / award', exact=True))
        expect(row).to_contain_text('Award not yet verified')
        expect(row).to_contain_text('Not yet verified')
        for parent in programs[ohio]['parent_programs']:
            expect(row).to_contain_text(parent['title'])
        expect(row).to_contain_text('Bachelor of Science')
        page.reload()
        expect(page.locator('#tray-count')).to_contain_text('4 of 4')
        open_filters(page)
        page.locator('#search').fill('Ohio State')
        expect(page.locator('[data-program-id]:visible')).to_have_count(1)
        page.go_back()
        expect(page.locator('#search')).to_have_value('')
        page.go_forward()
        expect(page.locator('#search')).to_have_value('Ohio State')
        expect(page.locator('#tray-count')).to_contain_text('4 of 4')
        expect(page.locator('#tab-nu-concentrations')).to_be_visible()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert not errors
    finally:
        context.close()
