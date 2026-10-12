"""A reviewed AI literacy correction reaches profile, course evidence and comparison."""
import json
from pathlib import Path
import pytest
from playwright.sync_api import expect
from atlas import db
from atlas.site import build
from tests.e2e.test_atlas import browser,page,site  # noqa: F401
from tests.test_site import site_data  # noqa: F401

pytestmark=pytest.mark.e2e


@pytest.mark.parametrize('width',[1440,390])
def test_unc_literacy_review_and_counts(page,site,tmp_path,width):
    seed=json.loads((Path(__file__).resolve().parents[2]/'data/programs/unc-ai-minor.json').read_text())
    conn=db.connect(tmp_path/'unc.sqlite');db.migrate(conn);db.ingest_program(conn,seed)
    build(db.export_data(conn),tmp_path/'ai-program-atlas');conn.close()
    page.set_viewport_size({'width':width,'height':950})
    page.goto(site+'programs/unc-ai-minor/#course-unc-data-117')
    cell=page.locator('#course-unc-data-117').locator('+ td')
    expect(cell).to_contain_text('Domain studies & applications')
    expect(cell).to_contain_text('Reviewed classification')
    expect(cell).not_to_contain_text('Legacy / unreviewed')
    details=cell.locator('.category-review');details.locator('summary').focus();page.keyboard.press('Enter')
    expect(details).to_contain_text('interdisciplinary AI literacy')
    expect(details.get_by_role('link',name='Classification source')).to_have_attribute('href','https://catalog.unc.edu/courses/data/')
    expect(page.locator('[data-profile=required] [data-category=applications] strong')).to_have_text('2')
    expect(page.locator('[data-profile=required] [data-category=ai_ml] strong')).to_have_text('0 mapped')
    data110 = page.locator('#course-unc-data-110').locator('+ td')
    expect(data110).to_contain_text('Domain studies & applications')
    expect(data110).to_contain_text('Reviewed classification')
    expect(page.locator('[data-profile=required] [data-category=mathematics] span').first).to_have_text('Mathematics and Statistics')
    page.reload();expect(cell).to_contain_text('Reviewed classification')
    page.goto(site+'?compare=unc-ai-minor#comparison')
    cell=page.locator('.compare-profile-cell')
    expect(cell.locator('dt',has_text='Domain studies & applications').locator('+ dd')).to_have_text('2')
    expect(cell.locator('dt',has_text='AI & machine learning').locator('+ dd')).to_have_text('0 mapped')
    page.reload();expect(cell.locator('dt',has_text='Domain studies & applications').locator('+ dd')).to_have_text('2')
    page.goto(site+'methodology/#curriculum-method')
    expect(page.locator('#curriculum-method')).to_contain_text('AI in a title is insufficient')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
