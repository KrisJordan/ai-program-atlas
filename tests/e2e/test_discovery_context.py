"""Parent evidence, second-major navigation and collapsed search stay usable."""
import pytest
from playwright.sync_api import expect
from atlas.site import build
from tests.e2e.test_atlas import browser,page,site,open_filters  # noqa: F401
from tests.test_site import site_data  # noqa: F401
from tests.test_program_context_ui import context_fixture

pytestmark=pytest.mark.e2e


@pytest.mark.parametrize('width',[1440,390])
def test_second_major_navigation_and_parent_awards(page,site,tmp_path,site_data,width):
    context_fixture(site_data);build(site_data,tmp_path/'ai-program-atlas')
    page.set_viewport_size({'width':width,'height':950})
    errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
    page.goto(site + '?view=cards&award_nu=second_major&compare=test-ai-0')
    award=page.locator('#major-award-nu')
    expect(award).to_have_value('second_major')
    expect(page.locator('[data-program-id=test-ai-0]')).to_be_visible()
    expect(page.locator('[data-program-id=test-ai-1]')).not_to_be_visible()
    expect(page.locator('[data-program-id=test-ai-0] .major-relationship')).to_contain_text('Additional Major')
    open_filters(page)
    award.select_option('other')
    page.locator('#apply-filters').click()
    expect(page.locator('[data-program-id=test-ai-0]')).not_to_be_visible()
    expect(page.locator('[data-program-id=test-ai-1]')).to_be_visible()
    page.go_back();expect(award).to_have_value('second_major')
    page.reload();expect(award).to_have_value('second_major')
    expect(page.locator('#tray-count')).to_contain_text('1 of 4')
    expect(page.locator('.compare-table tr').filter(has=page.get_by_role('rowheader',name='Award / type',exact=True))).to_contain_text('No separate award')
    page.goto(site + '?view=cards&type=additional_major&award_nu=other')
    expect(page.locator('[data-program-id=test-ai-0]')).to_be_visible()
    page.goto(site + '?view=cards&path_lac=concentrations&path_nu=concentrations')
    expect(page.locator('[data-program-id=test-ai-2] .parent-programs')).to_contain_text('Bachelor of Arts (BA)')
    expect(page.locator('[data-program-id=test-ai-2] .parent-programs')).to_contain_text('Bachelor of Science (BS)')
    expect(page.locator('[data-program-id=test-ai-3] .parent-programs')).to_contain_text('Not yet verified')
    page.goto(site+'programs/test-ai-2/')
    expect(page.locator('.detail-hero .parent-programs')).to_contain_text('Bachelor of Science (BS)')
    page.goto(site + '?view=cards&compare=test-ai-2,test-ai-3')
    row=page.locator('.compare-table tr').filter(has=page.get_by_role('rowheader',name='Parent program / award',exact=True))
    expect(row).to_contain_text('Bachelor of Arts (BA)')
    expect(row).to_contain_text('Not yet verified')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    assert not errors


@pytest.mark.parametrize('width',[1440,390])
def test_filter_panel_keyboard_summary_preserves_state(page,site,width):
    page.set_viewport_size({'width':width,'height':950})
    page.goto(site + '?view=cards&compare=test-ai-0')
    panel=page.locator('#filter-panel');summary=page.locator('#active-filter-summary');launcher=page.locator('#open-filters')
    expect(panel).not_to_have_attribute('open','')
    expect(summary).to_contain_text('No search filters active')
    launcher.focus();page.keyboard.press('Enter')
    expect(panel).to_have_attribute('open','')
    page.locator('#search').fill('Artificial')
    expect(page).to_have_url(__import__('re').compile('q=Artificial'))
    page.locator('#filter-evidence').select_option('pending')
    expect(summary).to_contain_text('2 active filters')
    url=page.url
    page.keyboard.press('Escape')
    expect(panel).not_to_have_attribute('open','')
    expect(launcher).to_be_focused()
    assert page.url==url
    expect(page.locator('#tray-count')).to_contain_text('1 of 4')
    page.reload()
    expect(panel).not_to_have_attribute('open','')
    expect(summary).to_contain_text('2 active filters')
    expect(page.locator('#search')).to_have_value('Artificial')
    expect(page.locator('#filter-evidence')).to_have_value('pending')
    expect(page.locator('#tab-nu-majors')).to_be_visible()
    page.go_back()
    expect(summary).to_contain_text('1 active filter')
    page.go_forward()
    expect(summary).to_contain_text('2 active filters')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
