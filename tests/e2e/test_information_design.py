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
    header=listing.locator(':scope > summary')
    for i in range(6):expect(header.locator('h3')).to_contain_text(f'CS {100+i} · Course title {i}')
    expect(header.locator('.requirement-preview')).to_have_count(0)
    assert header.locator('.requirement-rule').evaluate('n=>getComputedStyle(n).display')=='block'
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


@pytest.mark.parametrize('width',[1440,390])
def test_real_mit_domain_context_order_and_compact_outcomes(page,site,tmp_path,width):
    import json
    from pathlib import Path
    from atlas import db
    seed=json.loads((Path(__file__).resolve().parents[2]/'data/programs/mit-ai-decision-making-bs.json').read_text())
    conn=db.connect(tmp_path/'mit.sqlite');db.migrate(conn);db.ingest_program(conn,seed)
    build(db.export_data(conn),tmp_path/'ai-program-atlas');conn.close()
    page.set_viewport_size({'width':width,'height':950});page.goto(site+'programs/mit-ai-decision-making-bs/')
    expect(page.locator('.requirements > .requirement').first).to_have_attribute('id','requirement-mit-ai-version-required')
    for focus in ['data-centric','model-centric','decision-centric','computation-centric','human-centric']:
        node=page.locator('#requirement-mit-ai-v2025-overlay-'+focus)
        expect(node.locator(':scope > details > summary')).to_be_visible()
        expect(node.locator(':scope > details')).to_have_attribute('open','')
    areas=page.locator('[data-related-pool=mit-ai-v2025-centers]')
    expect(areas.locator('.related-course-group')).to_have_count(5)
    expect(areas).to_contain_text('Data-centric')
    group=areas.locator('[data-related-requirement=mit-ai-v2025-overlay-data-centric]')
    group.locator(':scope > summary').focus();page.keyboard.press('Enter')
    expect(group.locator('ul > li')).to_have_count(4)
    expect(group).to_contain_text('Introduction to Machine Learning')
    expect(group.locator('ul > li').nth(2)).to_contain_text('6.C01')
    expect(group.locator('ul > li').nth(2)).to_contain_text('6.C011')
    pool=page.locator('#requirement-mit-ai-v2025-centers .requirement-option-pool')
    expect(pool).not_to_have_attribute('open','')
    page.goto(site+'programs/mit-ai-decision-making-bs/#requirement-mit-ai-v2025-centers-1')
    page.reload();expect(pool).to_have_attribute('open','')
    expect(page.locator('#requirement-mit-ai-v2025-centers-1 > details')).to_have_attribute('open','')
    general=page.locator('#requirements-group-general-top > details')
    expect(general).not_to_have_attribute('open','')
    general.locator(':scope > summary').focus();page.keyboard.press('Enter')
    expect(page.get_by_role('heading',name='Biology (GIR)',exact=True)).to_be_visible()
    page.goto(site+'programs/mit-ai-decision-making-bs/#requirement-mit-ai-gir-science-1')
    page.reload();expect(general).to_have_attribute('open','')
    expect(page.locator('#requirement-mit-ai-gir-science-1 > details')).to_have_attribute('open','')
    assert page.locator('.outcomes .statement-text').first.evaluate('n=>getComputedStyle(n).display')=='inline'
    assert page.locator('#requirement-mit-ai-version-required > details > summary .requirement-rule').evaluate('n=>getComputedStyle(n).display')=='inline'
    expect(page.locator('#requirement-mit-ai-version-required > details > .requirement-body > .requirement-tags')).to_have_count(0)
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')


@pytest.mark.parametrize('width',[1440,390])
def test_real_penn_state_single_course_headers(page,site,tmp_path,width):
    import json
    from pathlib import Path
    from atlas import db
    seed=json.loads((Path(__file__).resolve().parents[2]/'data/programs/penn-state-ai-engineering-bs.json').read_text())
    conn=db.connect(tmp_path/'penn-state.sqlite');db.migrate(conn);db.ingest_program(conn,seed)
    build(db.export_data(conn),tmp_path/'ai-program-atlas');conn.close()
    page.set_viewport_size({'width':width,'height':950})
    page.goto(site+'programs/penn-state-ai-engineering-bs/')
    card=page.locator('#requirement-penn-state-ai-engineering-bs-major-r3 > details')
    header=card.locator(':scope > summary')
    expect(header.locator('h3')).to_have_text('A-I 100 · Artificial Intelligence: Automated Thinking to Augment Human Intellect')
    expect(header.locator('.requirement-rule')).to_have_text('3 Semester hours')
    expect(header.locator('.requirement-preview')).to_have_count(0)
    expect(header).not_to_contain_text('Complete all')
    assert header.locator('.requirement-rule').evaluate('n=>getComputedStyle(n).display')=='inline'
    assert header.locator('.requirement-rule').evaluate('n=>parseFloat(getComputedStyle(n).fontSize)') < header.locator('h3').evaluate('n=>parseFloat(getComputedStyle(n).fontSize)')
    header.focus();page.keyboard.press('Enter')
    expect(card).to_have_attribute('open','')
    expect(card.locator(':scope > .requirement-body .requirement-courses a')).to_contain_text('Artificial Intelligence: Automated Thinking')
    page.goto(site+'programs/penn-state-ai-engineering-bs/#requirement-penn-state-ai-engineering-bs-major-r3')
    page.reload();expect(card).to_have_attribute('open','')
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')


@pytest.mark.parametrize('width', [1440, 390])
def test_buffalo_group_is_independent_and_preserves_state(page, site, tmp_path, site_data, width):  # noqa: F811
    data = joint_fixture(site_data)
    for i, award in enumerate(['BS', 'BA']):
        program = deepcopy(data['programs'][i])
        program.update(id=f'buffalo-test-{i}', title='AI+X ' + ['Geospatial', 'Econometrics'][i], award_level=award)
        program['institution']['id'] = 'university-at-buffalo-suny'
        program['institution']['name'] = 'University at Buffalo–SUNY'
        program['family']['id'] = 'buffalo-ai-plus-x-degrees'
        data['programs'].append(program)
    # A same-institution degree without verified family membership stays separate.
    separate = deepcopy(data['programs'][-1])
    separate.pop('family')
    separate.update(id='buffalo-separate', title='Separate AI degree')
    data['programs'].append(separate)
    build(data, tmp_path / 'ai-program-atlas')
    page.set_viewport_size({'width': width, 'height': 900})
    page.goto(site)
    expect(page.locator('#sort-order option:checked')).to_have_text('AI Ranking')
    group = page.locator('[data-table-group=buffalo-ai-plus-x]')
    members = page.locator('[data-joint-member=buffalo-ai-plus-x]:visible')
    northeastern = page.locator('[data-table-group=northeastern-joint-ai] .joint-toggle')
    expect(group).to_be_visible()
    expect(members).to_have_count(0)
    expect(page.locator('[data-row-id=buffalo-separate]')).to_be_visible()
    expect(group.locator('.joint-awards')).to_have_text('BA / BS')
    toggle = group.locator('.joint-toggle')
    toggle.focus()
    page.keyboard.press('Enter')
    expect(members).to_have_count(2)
    expect(northeastern).to_have_attribute('aria-expanded', 'false')
    page.locator('[data-row-compare=buffalo-test-0]').check()
    page.reload()
    expect(toggle).to_have_attribute('aria-expanded', 'true')
    expect(page.locator('[data-row-compare=buffalo-test-0]')).to_be_checked()
    assert 'buffalo=open' in page.url
    toggle.click()
    expect(members).to_have_count(0)
    assert 'buffalo=closed' in page.url
    page.reload()
    expect(toggle).to_have_attribute('aria-expanded', 'false')
    page.go_back()
    expect(toggle).to_have_attribute('aria-expanded', 'true')
    page.go_forward()
    expect(toggle).to_have_attribute('aria-expanded', 'false')
    open_filters(page)
    page.locator('#search').fill('Econometrics')
    page.locator('#apply-filters').click()
    expect(group.locator('.joint-summary')).to_contain_text('1 matching program')
    expect(group.locator('.joint-awards')).to_have_text('BA')
    expect(page.locator('[data-table-group=northeastern-joint-ai]')).not_to_be_visible()
    toggle.click()
    expect(members).to_have_count(1)
    expect(members.locator('.directory-program-link')).to_have_attribute('href', '/ai-program-atlas/programs/buffalo-test-1/')
    page.locator('#sort-order').select_option('name')
    page.reload()
    expect(members).to_have_count(1)
    expect(page.locator('#sort-order')).to_have_value('name')
    expect(page.locator('.compare-table')).to_contain_text('AI+X Geospatial')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')


@pytest.mark.parametrize('width', [1440, 390])
def test_detail_structure_before_profiles_and_unboxed_facts(page, site, width):  # noqa: F811
    page.set_viewport_size({'width': width, 'height': 900})
    page.goto(site + 'programs/test-ai-0/')
    order = page.locator('.detail-section').evaluate_all('(nodes) => nodes.map(n => n.id)')
    assert order.index('requirements') < order.index('curriculum') < order.index('courses')
    expect(page.locator('#outcomes .section-note, #requirements > .section-note')).to_have_count(0)
    expect(page.get_by_role('heading', name='Inferred taxonomy', exact=True)).to_be_visible()
    expect(page.locator('.fact-grid')).to_contain_text('Requirement inventory')
    assert page.locator('.fact-grid').evaluate('(n) => getComputedStyle(n).backgroundColor') == 'rgba(0, 0, 0, 0)'
    assert page.locator('.fact-grid').evaluate('(n) => getComputedStyle(n).borderTopWidth') == '0px'
    expect(page.locator('#curriculum .profile-panel:visible .profile-taxonomy')).to_contain_text('Taxonomy review')
    expect(page.locator('#evidence-context')).to_contain_text('Unknown values are not zero')
    page.locator('label[for=profile-options]').click()
    expect(page.locator('[data-profile=options]')).to_be_visible()
    page.locator('.section-nav a[href="#requirements"]').click()
    assert page.url.endswith('#requirements')
    page.reload()
    expect(page.locator('#requirements h2')).to_be_visible()
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
