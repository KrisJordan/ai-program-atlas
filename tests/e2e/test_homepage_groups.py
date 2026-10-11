"""Combined category/path navigation uses provenance and stable URL state."""
from copy import deepcopy

import pytest
from playwright.sync_api import expect

from atlas.site import build
from tests.e2e.test_atlas import open_filters, browser, page, site, family_fixture  # noqa: F401
from tests.test_site import site_data  # noqa: F401

pytestmark = pytest.mark.e2e


def grouped_fixture(data):
    family_fixture(data)
    data['programs'][1].update(program_kind='minor', award_level='minor')
    # Names deliberately contradict the recorded ranking category.
    data['institutions'][0]['name'] = 'Example Liberal Arts College'
    for program in data['programs'][:2]:
        program['institution']['name'] = 'Example Liberal Arts College'
    data['institutions'][2]['name'] = 'Example National University'
    data['programs'][2]['institution']['name'] = 'Example National University'
    unknown = deepcopy(data['programs'][0])
    unknown.update(id='unknown-ai', title='Unclassified AI degree')
    unknown.pop('family', None)
    unknown['institution'] = dict(id='unknown', name='Unranked University', calendar='semester')
    data['programs'].append(unknown)
    data['institutions'].append({**unknown['institution'], 'rankings': [],
                                 'coverage_status': 'confirmed_program',
                                 'program_ids': ['unknown-ai']})
    return data


def group(page, key):
    return page.locator(f'section[data-cohort-group="{key}"]')


def tab(section, path):
    return section.locator(f'[role="tab"][data-path="{path}"]')


@pytest.mark.parametrize('width', [1440, 390])
def test_cohort_paths_family_selection_history_and_profile(
        page, site, tmp_path, site_data, width):
    build(grouped_fixture(site_data), tmp_path / 'ai-program-atlas')
    page.set_viewport_size({'width': width, 'height': 900})
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(site)
    nu, lac = group(page, 'nu'), group(page, 'lac')
    expect(nu).to_contain_text('National Universities')
    expect(lac).to_contain_text('National Liberal Arts Colleges')
    for section in (nu, lac, group(page, 'unclassified')):
        expect(tab(section, 'majors')).to_have_attribute('aria-selected', 'true')
    expect(nu.locator('[data-program-id="test-ai-0"]')).to_have_count(1)
    expect(lac.locator('[data-program-id="test-ai-2"]')).to_be_visible()
    expect(lac.locator('[data-program-id="test-ai-2"] .card-badges')).to_contain_text('Additional major')
    expect(tab(nu, 'majors').locator('.path-count')).to_have_text('1')
    expect(tab(nu, 'minors').locator('.path-count')).to_have_text('1')
    expect(tab(nu, 'concentrations').locator('.path-count')).to_have_text('0')
    nu.locator('[role="tabpanel"][data-path="majors"] .program-family > summary').click()
    nu.locator('[data-compare="test-ai-0"]').check()
    tab(nu, 'minors').click()
    expect(nu.locator('[data-program-id="test-ai-0"]')).not_to_be_visible()
    expect(page.locator('.compare-table thead th')).to_have_count(2)
    expect(tab(lac, 'majors')).to_have_attribute('aria-selected', 'true')
    assert 'path_nu=minors' in page.url
    page.locator('#compare-profile').select_option('options')
    page.reload()
    expect(tab(nu, 'minors')).to_have_attribute('aria-selected', 'true')
    expect(page.locator('#compare-profile')).to_have_value('options')
    expect(page.locator('.compare-table thead th')).to_have_count(2)
    tab(lac, 'concentrations').click()
    expect(lac.locator('[data-program-id="test-ai-3"]')).to_be_visible()
    page.go_back()
    expect(tab(lac, 'majors')).to_have_attribute('aria-selected', 'true')
    page.go_forward()
    expect(tab(lac, 'concentrations')).to_have_attribute('aria-selected', 'true')
    tab(nu, 'minors').focus()
    page.keyboard.press('Home')
    expect(tab(nu, 'majors')).to_be_focused()
    expect(tab(nu, 'majors')).to_have_attribute('aria-selected', 'true')
    page.keyboard.press('ArrowRight')
    expect(tab(nu, 'concentrations')).to_be_focused()
    expect(nu.locator('.cohort-empty:visible')).to_have_count(1)
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    assert not errors


def test_legacy_type_category_search_and_explicit_empty_state(
        page, site, tmp_path, site_data):
    build(grouped_fixture(site_data), tmp_path / 'ai-program-atlas')
    page.goto(site + '?type=minor&cohort=National+Universities&compare=test-ai-2')
    nu = group(page, 'nu')
    expect(tab(nu, 'minors')).to_have_attribute('aria-selected', 'true')
    expect(group(page, 'lac')).not_to_be_visible()
    expect(group(page, 'unclassified')).not_to_be_visible()
    expect(page.locator('.compare-table thead th')).to_have_count(2)
    expect(tab(nu, 'minors').locator('.path-count')).to_have_text('1')
    open_filters(page)
    page.locator('#search').fill('no-such-program')
    expect(tab(nu, 'minors').locator('.path-count')).to_have_text('0')
    expect(nu.locator('.cohort-empty:visible')).to_have_count(1)
    expect(page.locator('#result-count')).to_contain_text('0')
    page.reload()
    expect(page.locator('#search')).to_have_value('no-such-program')
    expect(tab(nu, 'minors')).to_have_attribute('aria-selected', 'true')
    page.go_back()
    expect(page.locator('#search')).to_have_value('')
    expect(tab(nu, 'minors').locator('.path-count')).to_have_text('1')


def test_grouped_no_javascript_baseline(browser, site, tmp_path, site_data):
    build(grouped_fixture(site_data), tmp_path / 'ai-program-atlas')
    context = browser.new_context(java_script_enabled=False)
    page = context.new_page()
    page.goto(site)
    for key in ('nu', 'lac', 'unclassified'):
        expect(group(page, key)).to_be_visible()
    # Native family disclosure retains its members without JS.
    for summary in page.locator('.program-family > summary').all():
        summary.click()
    expect(page.locator('.program-card:visible')).to_have_count(6)
    context.close()


@pytest.mark.parametrize('width', [1440, 390])
def test_major_awards_multiple_options_and_combined_state(
        page, site, tmp_path, site_data, width):
    data = grouped_fixture(site_data)
    for key, award in [('ba','BA'), ('bse','BSE'), ('unmapped','BSAI'), ('multi','other')]:
        record = deepcopy(data['programs'][0])
        record.pop('family', None)
        record.update(id=f'award-{key}', title=f'Artificial Intelligence {key} degree',
                      award_level=award, hosting_unit='Engineering School')
        if key == 'multi':
            record['award_options'] = [
                dict(label='Bachelor of Arts', normalized='BA', source_id='outcome-source',
                     locator='Official award heading'),
                dict(label='Bachelor of Science', normalized='BS', source_id='outcome-source',
                     locator='Official award heading')]
        data['programs'].append(record)
    build(data, tmp_path / 'ai-program-atlas')
    page.set_viewport_size({'width': width, 'height': 900})
    page.goto(site + '?compare=test-ai-0')
    nu, lac = group(page, 'nu'), group(page, 'lac')
    award = nu.locator('select[data-major-award]')
    expect(tab(nu, 'majors').locator('.path-count')).to_have_text('5')
    award.select_option('BA')
    expect(nu.locator('.program-card:visible')).to_have_count(2)
    expect(nu.locator('[data-program-id="award-multi"]')).to_be_visible()
    expect(nu.locator('[data-program-id="award-ba"]')).to_be_visible()
    expect(nu.locator('[data-program-id="test-ai-0"]')).not_to_be_visible()
    expect(page.locator('.compare-table thead th')).to_have_count(2)
    assert 'award_nu=BA' in page.url
    page.reload()
    expect(award).to_have_value('BA')
    award.select_option('BSE')
    expect(nu.locator('.program-card:visible')).to_have_count(1)
    expect(nu.locator('[data-program-id="award-bse"]')).to_be_visible()
    page.go_back()
    expect(award).to_have_value('BA')
    page.go_forward()
    expect(award).to_have_value('BSE')
    award.select_option('other')
    expect(nu.locator('.program-card:visible')).to_have_count(1)
    expect(nu.locator('[data-program-id="award-unmapped"] .card-badges')).to_contain_text('BSAI')
    # A second major is discoverable without implying an independent BS award.
    lac.locator('select[data-major-award]').select_option('other')
    expect(lac.locator('[data-program-id="test-ai-2"]')).to_be_visible()
    expect(lac.locator('[data-program-id="test-ai-2"] .card-badges')).to_contain_text('Additional major')
    award.select_option('BA')
    open_filters(page)
    page.locator('#search').fill('multi degree')
    expect(nu.locator('.program-card:visible')).to_have_count(1)
    expect(page.locator('#result-count')).to_contain_text('1')
    open_filters(page)
    page.locator('#filter-cohort').select_option('National Universities')
    page.reload()
    expect(award).to_have_value('BA')
    expect(page.locator('#search')).to_have_value('multi degree')
    expect(group(page, 'lac')).not_to_be_visible()
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
