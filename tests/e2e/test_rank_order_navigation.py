"""Rank ordering stays scoped to both cohorts and every program-type panel."""
from copy import deepcopy

import pytest
from playwright.sync_api import expect

from atlas.site import build
from tests.e2e.test_atlas import open_filters, browser, page, site  # noqa: F401
from tests.test_site import site_data  # noqa: F401

pytestmark = pytest.mark.e2e
PATHS = ('majors','concentrations','minors')


def rank_fixture(data):
    template = deepcopy(data['programs'][0])
    data.update(programs=[],institutions=[],families=[])
    data['meta']['cohort'] = dict(edition='2027',complete=False)
    values = [('two','Zulu Two',2,'primary_verified'),
              ('beta','Beta Ten',10,'enumerated_secondary'),
              ('alpha','Alpha Ten',10,'primary_verified'),
              ('unverified','Aardvark Unverified',1,'unverified'),
              ('unknown','Able Unknown',None,'primary_membership_verified'),
              ('inferred','Acorn Inferred',3,'primary_edition_inferred')]
    for cohort,category in [('nu','National Universities'),('lac','National Liberal Arts Colleges')]:
        family_ids = []
        for key,name,rank,status in values:
            institution = dict(id=f'{cohort}-{key}',name=name,calendar='semester')
            data['institutions'].append({**institution,'coverage_status':'confirmed',
                'rankings':[dict(publisher='U.S. News',edition='2027',category=category,
                                 rank=rank,verification_status=status,
                                 source_url='https://example.edu/ranking')],
                'program_ids':[]})
            for path,kind,award in [('majors','degree','BS'),
                                    ('concentrations','concentration','concentration'),
                                    ('minors','minor','minor')]:
                p = deepcopy(template)
                p.update(id=f'{cohort}-{key}-{path}',institution=institution,
                         program_kind=kind,award_level=award,title='Artificial Intelligence B')
                if key == 'two':
                    p['family'] = dict(id=f'family-{cohort}',variant_label=p['title'],
                        disciplines=['Computing'],classification_kind='source_stated',
                        relationship='integrated',source_ids=['outcome-source'])
                    family_ids.append(p['id'])
                data['programs'].append(p)
                if key == 'two':
                    a = deepcopy(p)
                    a.update(id=p['id']+'-a',title='Artificial Intelligence A')
                    a['family']['variant_label'] = a['title']
                    data['programs'].append(a)
                    family_ids.append(a['id'])
        data['families'].append(dict(id=f'family-{cohort}',institution_id=f'{cohort}-two',
            name='AI family',classification_kind='source_stated',variant_ids=family_ids,
            sources=deepcopy(template['sources']),shared_requirements=[]))
    # Reverse input order to ensure sorting does not accidentally reflect fixtures.
    data['programs'].reverse()
    return data


def section(page, cohort):
    return page.locator(f'section[data-cohort-group="{cohort}"]')


def ids(page, cohort, path):
    return section(page,cohort).locator(
        f'[role="tabpanel"][data-path="{path}"] .program-grid > [data-sort-id]:visible'
    ).evaluate_all('(nodes)=>nodes.map(node=>node.dataset.sortId)')


def expected_ids(cohort,path):
    return [f'family-{cohort}']+[f'{cohort}-{key}-{path}' for key in
                               ('alpha','beta','unverified','unknown','inferred')]


@pytest.mark.parametrize('path',PATHS)
@pytest.mark.parametrize('width',[1440,390])
def test_numeric_ties_unknowns_families_and_filters_in_both_categories(
        page,site,tmp_path,site_data,path,width):
    build(rank_fixture(site_data),tmp_path/'ai-program-atlas')
    page.set_viewport_size({'width':width,'height':900})
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.goto(site+f'?path_nu={path}&path_lac={path}')
    expect(page.locator('#sort-order')).to_have_value('rank')
    for cohort in ('nu','lac'):
        assert ids(page,cohort,path)==expected_ids(cohort,path)
        root=section(page,cohort)
        expect(root.locator(f'[role="tab"][data-path="{path}"] .path-count')).to_have_text('7')
        family=root.locator(f'[role="tabpanel"][data-path="{path}"] .program-family')
        expect(family.locator(':scope > summary')).to_contain_text('#2')
        expect(family.locator(':scope > summary')).to_contain_text('2027')
        family.locator(':scope > summary').click()
        assert family.locator('.program-card').evaluate_all(
            '(nodes)=>nodes.map(node=>node.dataset.programId)')==[
                f'{cohort}-two-{path}-a',f'{cohort}-two-{path}']
        expect(root.locator(f'[data-program-id="{cohort}-beta-{path}"] .card-ranking')).to_contain_text('#10')
        expect(root.locator(f'[data-program-id="{cohort}-unverified-{path}"] .card-ranking')).to_contain_text('not used for sorting')
    open_filters(page)
    page.locator('#search').fill('Beta Ten')
    for cohort in ('nu','lac'):
        expect(section(page,cohort).locator('.program-card:visible')).to_have_count(1)
        assert ids(page,cohort,path)==[f'{cohort}-beta-{path}']
    page.reload()
    expect(page.locator('#search')).to_have_value('Beta Ten')
    expect(page.locator('#sort-order')).to_have_value('rank')
    page.go_back()
    expect(page.locator('#search')).to_have_value('')
    for cohort in ('nu','lac'):
        assert ids(page,cohort,path)==expected_ids(cohort,path)
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    assert not errors


def test_explicit_sort_preserves_award_path_comparison_and_history(page,site,tmp_path,site_data):
    build(rank_fixture(site_data),tmp_path/'ai-program-atlas')
    page.goto(site+'?path_lac=minors&award_nu=BS&compare=nu-two-majors')
    page.locator('#sort-order').select_option('name')
    assert ids(page,'nu','majors')==[f'nu-{key}-majors' for key in
        ('unverified','unknown','inferred','alpha','beta')]+['family-nu']
    assert 'sort=name' in page.url
    page.reload()
    expect(page.locator('#sort-order')).to_have_value('name')
    expect(section(page,'nu').locator('[data-major-award]')).to_have_value('BS')
    expect(section(page,'lac').locator('[role="tab"][data-path="minors"]')).to_have_attribute('aria-selected','true')
    expect(page.locator('.compare-table thead th')).to_have_count(2)
    page.locator('#sort-order').select_option('rank')
    assert ids(page,'nu','majors')==expected_ids('nu','majors')
    page.go_back()
    expect(page.locator('#sort-order')).to_have_value('name')
    page.go_forward()
    expect(page.locator('#sort-order')).to_have_value('rank')
    page.locator('#sort-order').select_option('name')
    open_filters(page)
    page.locator('#reset-filters').click()
    expect(page.locator('#sort-order')).to_have_value('rank')


def test_static_no_javascript_default_is_ranked_in_each_panel(browser,site,tmp_path,site_data):
    build(rank_fixture(site_data),tmp_path/'ai-program-atlas')
    context=browser.new_context(java_script_enabled=False)
    page=context.new_page()
    page.goto(site)
    for cohort in ('nu','lac'):
        for path in PATHS:
            assert ids(page,cohort,path)==expected_ids(cohort,path)
    context.close()
