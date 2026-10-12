"""Real Penn defaults, keyboard navigation and shared comparison structure."""
import json
from pathlib import Path

import pytest
from playwright.sync_api import expect

from atlas import db
from atlas.site import build
from tests.e2e.test_atlas import browser, page, site  # noqa: F401
from tests.test_site import site_data  # noqa: F401

pytestmark = pytest.mark.e2e


@pytest.mark.parametrize('width', [1440, 390])
def test_penn_concentrations_large_pools_and_comparison(page, site, tmp_path, width):  # noqa: F811
    seed = json.loads((Path(__file__).resolve().parents[2] / 'data/programs/penn-bse-ai.json').read_text())
    conn = db.connect(tmp_path / 'penn.sqlite')
    db.migrate(conn)
    db.ingest_program(conn, seed)
    build(db.export_data(conn), tmp_path / 'ai-program-atlas')
    conn.close()
    page.set_viewport_size({'width': width, 'height': 950})
    page.goto(site + 'programs/penn-bse-ai/')
    for comparison in [False, True]:
        scope = page.locator('#requirements')
        if comparison:
            page.goto(site + '?compare=penn-bse-ai#comparison')
            scope = page.locator('[data-comparison-requirements=penn-bse-ai]')
        concentration = scope.locator('li[id$=requirement-penn-bse-ai-optional-concentrations] > details')
        expect(concentration).to_have_attribute('open', '')
        for rid in ['optional-robotics', 'optional-machine-learning', 'optional-vision-language']:
            node = scope.locator('li[id$=requirement-penn-bse-ai-' + rid + '] > details')
            expect(node.locator(':scope > summary')).to_be_visible()
            expect(node).not_to_have_attribute('open', '')
        technical = scope.locator('li[id$=requirement-penn-bse-ai-technical-electives] > details')
        expect(technical).not_to_have_attribute('open', '')
        expect(technical.locator(':scope > summary')).to_contain_text('listed courses')
        technical.locator(':scope > summary').focus()
        page.keyboard.press('Enter')
        expect(technical.locator('.requirement-course-name').first).to_be_visible()
        if comparison:
            page.locator('#compare-profile').select_option('options')
            expect(technical).to_have_attribute('open', '')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.goto(site + 'programs/penn-bse-ai/#requirement-penn-bse-ai-technical-electives')
    expect(page.locator('#requirement-penn-bse-ai-technical-electives > details')).to_have_attribute('open', '')
    page.reload()
    expect(page.locator('#requirement-penn-bse-ai-technical-electives > details')).to_have_attribute('open', '')
