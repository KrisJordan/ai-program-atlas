"""Independent Rice source expectations must survive database and chart rendering."""
import pytest
from playwright.sync_api import expect
from tests.e2e.test_atlas import browser  # noqa: F401
from tests.e2e.test_real_parent_context import parent_inventory  # noqa: F401

pytestmark = pytest.mark.e2e


@pytest.mark.parametrize('width', [1440,390])
def test_rice_required_foundations_and_systems_remain_visible(browser,parent_inventory,width):
    base,_ = parent_inventory
    pid = 'rice-university-artificial-intelligence-bs-degree'
    context = browser.new_context(viewport={'width':width,'height':950})
    page = context.new_page()
    errors = []
    page.on('pageerror',lambda error: errors.append(str(error)))
    try:
        page.goto(base+'programs/'+pid+'/')
        required = page.locator('[data-profile=required]')
        expect(required).to_be_visible()
        expect(required.locator('[data-category=foundations] strong')).to_have_text('3')
        expect(required.locator('[data-category=systems] strong')).to_have_text('2')
        expect(required.locator('.profile-total')).to_contain_text('13 distinct')
        expect(required.locator('.profile-taxonomy')).to_contain_text('13 reviewed')
        page.locator('label[for=profile-options]').click()
        options = page.locator('[data-profile=options]')
        expect(options).to_be_visible()
        expect(options.locator('.profile-total')).to_contain_text('26 distinct')
        expect(options.locator('.profile-identity')).to_contain_text('30 retained source-code records')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.goto(base+'?compare='+pid)
        cell = page.locator('.compare-profile-cell')
        expect(cell.locator('.profile-total')).to_contain_text('13 distinct')
        for label,count in [('Computing foundations','3'),('Systems','2')]:
            term = cell.locator('dt').filter(has_text=label)
            expect(term.locator('xpath=following-sibling::dd[1]')).to_have_text(count)
        page.reload()
        expect(cell.locator('.profile-total')).to_contain_text('13 distinct')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert not errors
    finally:
        context.close()
