"""Joint-program ranges and drillable requirements preserve concrete comparisons."""
from copy import deepcopy
import pytest
from playwright.sync_api import expect
from atlas.site import build
from tests.e2e.test_atlas import browser,page,site,family_fixture,open_filters  # noqa: F401
from tests.test_site import site_data  # noqa: F401

pytestmark=pytest.mark.e2e


def joint_fixture(data):
    family_fixture(data)
    data['families'][0]['id']='northeastern-ai-combined-degrees'
    for p in data['programs'][:2]:
        p['family']['id']='northeastern-ai-combined-degrees'
    chemical=deepcopy(data['programs'][0]);chemical.pop('family')
    chemical.update(id='northeastern-chemical-engineering-ai-bsche',title='Chemical Engineering and Artificial Intelligence, BSChE (Boston)',award_level='other',award_options=[dict(label='BSChE',normalized='BS',source_id='family-source',locator='Test heading')])
    data['programs'].append(chemical)
    math=deepcopy(data['programs'][1]['courses'][0]);math.update(id='test-math',code='MATH 101',category='mathematics')
    data['programs'][1]['courses'].append(math)
    data['programs'][1]['requirements'].append(dict(id='fixed-math',parent_id=None,title='Mathematics',kind='all',course_ids=['test-math']))
    return data


@pytest.mark.parametrize('width',[1440,390])
def test_joint_collapse_ranges_filter_compare_history(page,site,tmp_path,site_data,width):
    build(joint_fixture(site_data),tmp_path/'ai-program-atlas')
    page.set_viewport_size({'width':width,'height':900})
    page.goto(site)
    group=page.locator('[data-table-group]')
    expect(group).to_be_visible();expect(page.locator('[data-joint-member]:visible')).to_have_count(0)
    expect(group.locator('[data-joint-count=mathematics]')).to_have_text('0–1')
    toggle=group.locator('.joint-toggle');toggle.focus();page.keyboard.press('Enter')
    expect(page.locator('[data-joint-member]:visible')).to_have_count(3)
    page.locator('[data-row-compare=northeastern-chemical-engineering-ai-bsche]').check()
    expect(page.locator('.compare-table thead th')).to_have_count(2)
    page.reload();expect(toggle).to_have_attribute('aria-expanded','true')
    expect(page.locator('[data-row-compare=northeastern-chemical-engineering-ai-bsche]')).to_be_checked()
    toggle.click();expect(page.locator('[data-joint-member]:visible')).to_have_count(0)
    page.go_back();expect(toggle).to_have_attribute('aria-expanded','true')
    page.go_forward();expect(toggle).to_have_attribute('aria-expanded','false')
    open_filters(page);page.locator('#search').fill('Chemical');page.locator('#apply-filters').click()
    expect(group.locator('.joint-summary')).to_contain_text('1 matching program')
    expect(group.locator('[data-joint-count=mathematics]')).to_have_text('0')
    expect(group.locator('.joint-awards')).to_have_text('BSChE')
    toggle.click();expect(page.locator('[data-joint-member]:visible')).to_have_count(1)
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')


@pytest.mark.parametrize('width',[1440,390])
def test_detail_drilldown_and_fragment_reveal(page,site,tmp_path,site_data,width):
    program=site_data['programs'][0]
    program['requirements']=[dict(id=f'r-{n}',parent_id=f'r-{n-1}' if n else None,title=f'Group {n}',kind='all',course_ids=[program['courses'][0]['id']] if n==3 else [],summary=f'Detail {n}') for n in range(4)]
    build(site_data,tmp_path/'ai-program-atlas')
    page.set_viewport_size({'width':width,'height':900})
    page.goto(site+'programs/test-ai-0/')
    deep=page.locator('#requirement-r-2 > details')
    expect(deep).not_to_have_attribute('open','')
    expect(deep.locator(':scope > summary > .requirement-preview')).to_contain_text('Group 3')
    deep.locator(':scope > summary').focus();page.keyboard.press('Enter')
    expect(deep).to_have_attribute('open','')
    expect(page.locator('#requirement-r-3 > details')).not_to_have_attribute('open','')
    page.goto(site+'programs/test-ai-0/#requirement-r-3')
    expect(deep).to_have_attribute('open','')
    expect(page.locator('#requirement-r-3 > details')).to_have_attribute('open','')
    page.reload();expect(deep).to_have_attribute('open','')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')


@pytest.mark.parametrize('width',[1440,390])
def test_readable_lists_grouped_notes_optional_fields_and_prerequisites(page,site,tmp_path,site_data,width):
    from tests.test_requirement_readability import rule
    program=site_data['programs'][0]
    program['courses']=[dict(id=f'c{i}',code=f'CS {100+i}',name=f'Course title {i}',prerequisites='CS100 or instructor permission' if i==5 else None) for i in range(6)]
    program['requirements']=[rule('policy',kind='note'),rule('root',title='Core'),rule('mid',parent='root'),rule('list',parent='mid',courses=[f'c{i}' for i in range(6)]),rule('nested-note',kind='note',parent='mid'),rule('optional',kind='note',title='Optional HASS field'),rule('optional-course',parent='optional',courses=['c0'])]
    build(site_data,tmp_path/'ai-program-atlas')
    page.set_viewport_size({'width':width,'height':900})
    page.goto(site+'programs/test-ai-0/')
    listing=page.locator('#requirement-list > details')
    expect(listing).not_to_have_attribute('open','')
    preview=listing.locator(':scope > summary > .requirement-preview')
    for i in range(6):expect(preview).to_contain_text(f'Course title {i}')
    expect(preview.locator('[role=listitem]')).to_have_count(6)
    for key in ['notes-mid','other-top','optional-top']:
        expect(page.locator(f'#requirements-group-{key} > details')).not_to_have_attribute('open','')
    expect(page.locator('#course-c5').locator('..').locator('.prerequisite-titles')).to_contain_text('Course title 0')
    page.goto(site+'programs/test-ai-0/#requirement-nested-note')
    expect(page.locator('#requirements-group-notes-mid > details')).to_have_attribute('open','')
    expect(page.locator('#requirement-nested-note > details')).to_have_attribute('open','')
    page.reload();expect(page.locator('#requirement-nested-note > details')).to_have_attribute('open','')
    page.goto(site+'programs/test-ai-0/')
    optional=page.locator('#requirements-group-optional-top > details')
    optional.locator(':scope > summary').focus();page.keyboard.press('Enter')
    expect(optional).to_have_attribute('open','')
    expect(page.get_by_role('heading',name='Optional HASS field',exact=True)).to_be_visible()
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
