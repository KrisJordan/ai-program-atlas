"""Default table, modal filters and shareable navigation on nested Pages paths."""
import pytest
from playwright.sync_api import expect
from tests.e2e.test_atlas import browser, page, site  # noqa: F401
from tests.test_site import site_data  # noqa: F401

pytestmark = pytest.mark.e2e


@pytest.mark.parametrize('width,height', [(1440,900), (390,844)])
def test_default_table_first_program_above_fold_and_modal(page, site, width, height):
    page.set_viewport_size({'width': width, 'height': height})
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(site)
    expect(page.locator('.directory-cards:visible')).to_have_count(0)
    expect(page.locator('#cohort-nu-majors .directory-table thead tr').first.locator('th')).to_have_text([
        'Compare', 'University', 'Program', 'AI Ranking', 'US News Ranking', 'Required Curriculum'])
    first = page.locator('#cohort-nu-majors [data-row-id]').first
    expect(first).to_be_visible()
    assert first.bounding_box()['y'] + first.bounding_box()['height'] <= height
    assert page.locator('.coverage-strip, .edition-note, .inventory-counts').count() == 0
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    launcher = page.locator('#open-filters')
    launcher.focus(); page.keyboard.press('Enter')
    expect(page.get_by_role('dialog', name='Search & filters')).to_be_visible()
    expect(page.locator('#search')).to_be_focused()
    page.locator('#search').fill('no-matching-program-here')
    page.locator('#apply-filters').click()
    expect(page.locator('#filter-panel')).not_to_be_visible()
    expect(launcher).to_be_focused()
    expect(page.locator('#empty-state')).to_be_visible()
    assert 'q=no-matching-program-here' in page.url
    page.reload()
    expect(page.locator('#empty-state')).to_be_visible()
    page.go_back()
    expect(first).to_be_visible()
    page.go_forward()
    expect(page.locator('#empty-state')).to_be_visible()
    page.locator('#empty-reset').click()
    expect(page.locator('#search')).to_have_value('')
    page.keyboard.press('Escape')
    expect(first).to_be_visible()
    assert not errors


@pytest.mark.parametrize('width', [1440,390])
def test_table_comparison_sort_and_view_history(page, site, width):
    page.set_viewport_size({'width':width,'height':950})
    page.goto(site)
    page.locator('[data-row-compare="test-ai-0"]').check()
    page.locator('[data-row-compare="test-ai-2"]').check()
    expect(page.locator('#result-count')).to_contain_text('2 programs')
    expect(page.locator('.compare-table thead th')).to_have_count(3)
    page.locator('#sort-order').select_option('rank')
    permalink = page.url
    page.reload()
    expect(page.locator('[data-row-compare="test-ai-0"]')).to_be_checked()
    expect(page.locator('#sort-order')).to_have_value('rank')
    page.locator('#directory-view').select_option('cards')
    expect(page.locator('.program-card:visible')).to_have_count(2)
    expect(page.locator('[data-compare="test-ai-0"]')).to_be_checked()
    page.go_back()
    expect(page.locator('#directory-view')).to_have_value('table')
    expect(page.locator('[data-row-compare="test-ai-2"]')).to_be_checked()
    assert page.url == permalink
    page.go_forward(); page.reload()
    expect(page.locator('#directory-view')).to_have_value('cards')
    page.locator('#directory-view').select_option('table')
    page.locator('#cohort-nu-majors .directory-program-link').click()
    expect(page).to_have_url(site + 'programs/test-ai-0/')
    page.reload(); expect(page.locator('h1')).to_have_text('Artificial Intelligence 0')


def test_static_table_without_javascript(browser,site):
    context = browser.new_context(java_script_enabled=False)
    try:
        page = context.new_page(); page.goto(site)
        expect(page.locator('#cohort-nu-majors .directory-table')).to_be_visible()
        expect(page.locator('.directory-cards:visible')).to_have_count(0)
        expect(page.locator('#filter-panel')).not_to_be_visible()
        page.locator('#cohort-nu-majors .directory-program-link').click()
        expect(page.locator('h1')).to_have_text('Artificial Intelligence 0')
    finally:
        context.close()


@pytest.mark.parametrize('width', [1440,390])
def test_table_rank_sort_includes_all_family_variants(page,site,tmp_path,site_data,width):
    from atlas.site import build
    from tests.e2e.test_rank_order_navigation import rank_fixture
    build(rank_fixture(site_data),tmp_path/'ai-program-atlas')
    page.set_viewport_size({'width':width,'height':900})
    page.goto(site)
    rows = page.locator('#cohort-nu-majors .directory-table tbody tr:visible')
    get_ids = lambda: rows.evaluate_all('(nodes)=>nodes.map(node=>node.dataset.rowId)')
    default = ['nu-two-majors-a','nu-two-majors','nu-alpha-majors','nu-beta-majors',
               'nu-unverified-majors','nu-unknown-majors','nu-inferred-majors']
    assert get_ids() == default
    page.locator('#sort-order').select_option('name')
    assert get_ids() == ['nu-unverified-majors','nu-unknown-majors','nu-inferred-majors',
                         'nu-alpha-majors','nu-beta-majors','nu-two-majors-a','nu-two-majors']
    page.locator('#sort-order').select_option('rank')
    assert get_ids() == default
    page.reload();assert get_ids() == default
    page.go_back();expect(page.locator('#sort-order')).to_have_value('name')
    page.go_forward();expect(page.locator('#sort-order')).to_have_value('rank')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
