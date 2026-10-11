"""Run with uv run pytest tests/e2e (Playwright Chromium required)."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import os

import pytest

from atlas.site import build
from tests.test_site import site_data  # noqa: F401

pytestmark = pytest.mark.e2e


@pytest.fixture(scope="module")
def browser():
    required = os.environ.get("ATLAS_REQUIRE_BROWSER") == "1"
    try:
        from playwright import sync_api as playwright
    except ImportError:
        if required:
            pytest.fail("ATLAS_REQUIRE_BROWSER=1 requires the Playwright Python package")
        pytest.skip("Playwright is not installed")
    with playwright.sync_playwright() as p:
        try:
            instance = p.chromium.launch()
        except playwright.Error as error:
            if required:
                pytest.fail(f"ATLAS_REQUIRE_BROWSER=1: Chromium launch failed: {error}")
            pytest.skip(f"Chromium unavailable: {error}")
        yield instance
        instance.close()


@pytest.fixture
def site(tmp_path, site_data):
    build(site_data, tmp_path / "ai-program-atlas")
    handler = partial(SimpleHTTPRequestHandler, directory=str(tmp_path))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}/ai-program-atlas/"
    server.shutdown()
    server.server_close()
    thread.join()


@pytest.fixture
def page(browser):
    context = browser.new_context(viewport={"width": 1440, "height": 1000})
    page = context.new_page()
    yield page
    context.close()


def test_filters_empty_reset_detail_and_base_path(page, site):
    from playwright.sync_api import expect
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(site)
    expect(page.locator(".program-card:visible")).to_have_count(5)
    page.locator("#filter-award").select_option("BS")
    expect(page.locator(".program-card:visible")).to_have_count(1)
    page.locator("#filter-calendar").select_option("quarter")
    expect(page.locator("#empty-state")).to_be_visible()
    page.locator("#empty-reset").click()
    expect(page.locator(".program-card:visible")).to_have_count(5)
    page.locator("#filter-cohort").select_option("National Universities")
    expect(page.locator(".program-card:visible")).to_have_count(1)
    page.get_by_role("link", name="View program").first.click()
    expect(page).to_have_url(site + "programs/test-ai-0/")
    expect(page.locator("h1")).to_have_text("Artificial Intelligence 0")
    expect(page.get_by_text("1 unique documented course records.", exact=False)).to_be_visible()
    page.reload()
    expect(page.locator("h1")).to_have_text("Artificial Intelligence 0")
    assert not errors


def test_comparison_url_reload_history_and_limit(page, site):
    from playwright.sync_api import expect
    page.goto(site)
    page.locator('[data-compare="test-ai-0"]').check()
    page.locator('[data-compare="test-ai-1"]').check()
    expect(page.locator(".compare-table thead th")).to_have_count(3)
    assert "compare=test-ai-0%2Ctest-ai-1" in page.url
    page.reload()
    expect(page.locator('[data-compare="test-ai-1"]')).to_be_checked()
    page.locator('[data-compare="test-ai-2"]').check()
    page.go_back()
    expect(page.locator('[data-compare="test-ai-2"]')).not_to_be_checked()
    page.go_forward()
    expect(page.locator('[data-compare="test-ai-2"]')).to_be_checked()
    page.locator('[data-compare="test-ai-3"]').check()
    page.locator('[data-compare="test-ai-4"]').click()
    expect(page.locator('[data-compare="test-ai-4"]')).not_to_be_checked()
    expect(page.locator("#compare-status")).to_contain_text("Choose up to four")
    expect(page.locator(".compare-table thead th")).to_have_count(5)
    assert "/ai-program-atlas/?" in page.url


def test_search_history_mobile_and_no_document_overflow(page, site):
    from playwright.sync_api import expect
    requests = []
    page.on('request', lambda request: requests.append(request.url))
    page.route('**/data.json', lambda route: route.abort())
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(site)
    page.locator("#search").fill("Institution 4")
    expect(page.locator(".program-card:visible")).to_have_count(1)
    page.locator('[data-compare="test-ai-4"]').check()
    page.reload()
    expect(page.locator("#search")).to_have_value("Institution 4")
    expect(page.locator('[data-compare="test-ai-4"]')).to_be_checked()
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.locator("#reset-filters").click()
    expect(page.locator(".program-card:visible")).to_have_count(5)
    page.go_back()
    expect(page.locator("#search")).to_have_value("Institution 4")
    page.locator('#search').fill('AI 001')
    expect(page.locator('.program-card:visible')).to_have_count(1)
    expect(page.locator('.program-card:visible')).to_have_attribute('data-program-id', 'test-ai-0')
    page.locator('#search').fill('machine LEARNING')
    expect(page.locator('.program-card:visible')).to_have_count(3)
    page.locator('#filter-category').select_option('ai_ml')
    expect(page.locator('.program-card:visible')).to_have_count(3)
    page.locator('#filter-category').select_option('other')
    expect(page.locator('#empty-state')).to_be_visible()
    assert not any('/data.json' in url for url in requests)


def test_no_javascript_baseline(browser, site):
    from playwright.sync_api import expect
    context = browser.new_context(java_script_enabled=False)
    page = context.new_page()
    page.goto(site)
    expect(page.locator(".program-card:visible")).to_have_count(5)
    expect(page.locator("#filters")).not_to_be_visible()
    page.get_by_role("link", name="View program").first.click()
    expect(page.locator("h1")).to_have_text("Artificial Intelligence 0")
    context.close()


def test_program_type_and_evidence_filters_preserve_history(page, site):
    from playwright.sync_api import expect
    page.goto(site)
    page.locator('#filter-evidence').select_option('pending')
    expect(page.locator('.program-card:visible')).to_have_count(2)
    page.locator('#filter-type').select_option('additional_major')
    expect(page.locator('.program-card:visible')).to_have_count(1)
    expect(page.locator('.program-card:visible .card-badges')).to_contain_text('Additional major')
    assert 'type=additional_major' in page.url and 'evidence=pending' in page.url
    page.reload()
    expect(page.locator('#filter-type')).to_have_value('additional_major')
    expect(page.locator('#filter-evidence')).to_have_value('pending')
    page.locator('#filter-evidence').select_option('complete')
    expect(page.locator('#empty-state')).to_be_visible()
    page.go_back()
    expect(page.locator('.program-card:visible')).to_have_count(1)
    expect(page.locator('#filter-evidence')).to_have_value('pending')
    page.go_forward()
    expect(page.locator('#empty-state')).to_be_visible()


def test_cohort_context_theme_matrix_and_unknown_categories(page, site):
    from playwright.sync_api import expect
    page.goto(site + '?compare=test-ai-0,test-ai-1,test-ai-2')
    ranks = page.locator('.compare-table tr').filter(has=page.get_by_role('rowheader', name='U.S. News cohort context', exact=True))
    expect(ranks).to_contain_text('U.S. News 2027 · National Universities · #20')
    expect(ranks.locator('a').first).to_have_attribute('href', 'https://example.edu/ranking')
    themes = page.locator('.theme-table tbody tr')
    expect(themes).to_have_count(2)
    ai = themes.filter(has=page.get_by_role('rowheader', name='AI methods', exact=True))
    expect(ai.locator('td').nth(0)).to_contain_text('Documented inference')
    expect(ai.locator('td').nth(0).locator('a')).to_have_attribute('href', 'https://example.edu/outcome')
    expect(ai.locator('td').nth(1)).to_have_text('Not recorded')
    expect(ai.locator('td').nth(2)).to_have_text('Not recorded')
    category = page.locator('.compare-table tr').filter(has=page.get_by_role('rowheader', name='Course categories', exact=True))
    expect(category.locator('td').nth(2)).to_have_text('Not yet extracted')
    page.reload()
    expect(page.locator('.theme-table tbody tr')).to_have_count(2)


@pytest.mark.parametrize('width', [1440, 390])
def test_complete_concentration_scope_metadata_and_nested_choices(page, site, tmp_path, site_data, width):
    from playwright.sync_api import expect
    program = site_data['programs'][0]
    program.update(program_kind='concentration', curriculum_status='complete')
    program['notes'] = ['Public source URL remains readable: https://example.edu/evidence/' + 'a' * 100 + '/view.']
    course = dict(program['courses'][0], description='A sourced description.', prerequisites=None, credits=0)
    unsourced = dict(course, id='course-unsourced', code='AI 999', name='An elective option', description='Unverified text', credits=None, credit_unit='unknown', url=None, source_id=None)
    program['courses'] = [course, unsourced, dict(course)]
    def group(id, parent, title, kind, **extra):
        return dict(id=id, parent_id=parent, title=title, kind=kind, source_id='outcome-source', summary='Follow this recorded group rule.', course_ids=[], **extra)
    program['requirements'] = [
        group('root', None, 'Select one pathway', 'alternative', count=1),
        {**group('branch', 'root', 'Foundations pathway', 'all'), 'course_ids': [course['id']]},
        {**group('choice', 'root', 'Elective pathway', 'choose_courses', count=1), 'course_ids': [course['id'], unsourced['id']]},
        group('note', 'branch', 'Advisor approval', 'note', source_text='Approval is required for a substitution.'),
        group('credits', 'choice', 'Credit minimum', 'choose_credits', credits=3, credit_unit='semester_hours'),
    ]
    build(site_data, tmp_path / 'ai-program-atlas')
    page.set_viewport_size({'width': width, 'height': 950})
    page.goto(site + 'programs/test-ai-0/')
    expect(page.locator('.curriculum-scope')).to_contain_text('Complete means the requirement inventory')
    expect(page.locator('.curriculum-scope')).to_contain_text('concentration’s local requirements, not the whole parent degree')
    expect(page.locator('.metadata-counts > div').filter(has=page.locator('dt', has_text='Descriptions'))).to_contain_text('1 of 2 sourced')
    expect(page.locator('.metadata-counts > div').filter(has=page.locator('dt', has_text='Prerequisite statements'))).to_contain_text('0 of 2 sourced')
    expect(page.locator('.metadata-counts > div').filter(has=page.locator('dt', has_text='Credit amounts'))).to_contain_text('1 of 2 sourced')
    expect(page.locator('.metadata-counts > div').filter(has=page.locator('dt', has_text='Known credit units'))).to_contain_text('1 of 2 sourced')
    expect(page.locator('.requirements .requirement')).to_have_count(5)
    expect(page.get_by_role('heading', name='Advisor approval', exact=True)).to_be_visible()
    expect(page.get_by_role('heading', name='Credit minimum', exact=True)).to_be_visible()
    expect(page.locator('.requirements')).to_contain_text('Choose an alternative')
    expect(page.locator('.requirements')).to_contain_text('1 selection')
    expect(page.locator('.requirements')).to_contain_text('3 Semester hours')
    page.locator('.source-wording summary').click()
    expect(page.get_by_text('Approval is required for a substitution.', exact=True)).to_be_visible()
    expect(page.locator('.requirement-evidence a').first).to_have_attribute('href', 'https://example.edu/outcome')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.goto(site + '?compare=test-ai-0,test-ai-1')
    scope = page.locator('.compare-table tr').filter(has=page.get_by_role('rowheader', name='Requirement coverage', exact=True))
    expect(scope).to_contain_text('Concentration requirements only; not the whole parent degree')
    counts = page.locator('.compare-table tr').filter(has=page.get_by_role('rowheader', name='Course metadata availability', exact=True))
    expect(counts.locator('td').first).to_contain_text('Prerequisite statements0 of 2')
    for label in ['Descriptions', 'Credit amounts', 'Known credit units']:
        expect(counts.locator('td').first).to_contain_text(label + '1 of 2')
    records = page.locator('.compare-table tr').filter(has=page.get_by_role('rowheader', name='Course records', exact=True))
    expect(records.locator('td').first).to_contain_text('2 unique records')
    expect(records.locator('td').first).to_contain_text('1 with unknown credits')
    structure = page.locator('.compare-table tr').filter(has=page.get_by_role('rowheader', name='Requirement structure', exact=True))
    expect(structure).to_contain_text('1 alternative')
    expect(structure).not_to_contain_text('Foundations pathway')
    region = page.get_by_role('region', name='Program comparison', exact=True)
    region.focus()
    expect(region).to_be_focused()
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')


def family_fixture(data):
    """Synthetic evidence-backed family, never part of shipped inventory."""
    source={'id':'family-source','url':'https://example.edu/family','title':'Official family page'}
    shared={'id':'shared-core','parent_id':None,'title':'Shared AI core','kind':'all','source_id':'family-source','summary':'A documented common foundation.','course_ids':[]}
    data['families']=[{'id':'test-family','institution_id':'test-0','name':'AI combined programs','description':'Explicitly related test-only variants.','classification_kind':'source_stated','variant_ids':['test-ai-0','test-ai-1'],'disciplines':['Economics','Physics'],'sources':[source],'shared_requirements':[shared],'shared_course_codes':['AI 101']}]
    for i,discipline in enumerate(['Economics','Physics']):
        p=data['programs'][i]
        p['institution']=dict(data['programs'][0]['institution'])
        p['family']={'id':'test-family','variant_label':'AI and '+discipline,'disciplines':[discipline],'relationship':'ai_plus_x','classification_kind':'source_stated','source_ids':['family-source']}
        p['sources'].append(source)
        p['requirements']=[dict(shared,origin='family',component='ai_core',family_requirement_id='shared-core'),{'id':'variant-'+str(i),'parent_id':None,'title':discipline+' integration','kind':'note','origin':'variant','component':'integration','source_id':'family-source','summary':'A documented variant requirement.','course_ids':[]}]
    return data


@pytest.mark.parametrize('width',[1440,390])
def test_family_expand_discipline_compare_history_and_detail(page,site,tmp_path,site_data,width):
    from playwright.sync_api import expect
    family_fixture(site_data)
    site_data['programs'][0]['requirements'].append(dict(
        id='nested-local', parent_id='variant-0', title='Nested local exception',
        kind='note', origin='replacement', component='domain',
        source_id='family-source', summary='Preserve the nested evidence.', course_ids=[]))
    build(site_data,tmp_path/'ai-program-atlas')
    page.set_viewport_size({'width':width,'height':950})
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.goto(site)
    expect(page.locator('.program-family')).to_have_count(1)
    expect(page.locator('.program-card:visible')).to_have_count(3)
    family=page.locator('[data-family-id="test-family"]')
    family.locator(':scope > summary').click()
    expect(page.locator('.program-card:visible')).to_have_count(5)
    assert 'expand=test-family' in page.url
    page.reload()
    expect(family).to_have_attribute('open','')
    page.locator('#filter-discipline').select_option('Physics')
    expect(page.locator('.program-card:visible')).to_have_count(1)
    expect(family.locator('.family-match-count')).to_have_text('1 matching variant')
    page.locator('[data-compare="test-ai-1"]').check()
    page.locator('#filter-discipline').select_option('Economics')
    page.locator('[data-compare="test-ai-0"]').check()
    expect(page.locator('.compare-table thead th')).to_have_count(3)
    expect(page.locator('.compare-table')).to_contain_text('AI and Physics')
    expect(page.locator('.compare-table')).to_contain_text('Shared AI core')
    expect(page.locator('.compare-table')).to_contain_text('Physics integration')
    expect(page.locator('.compare-table')).to_contain_text('Economics integration')
    local_row = page.locator('.compare-table tr').filter(has=page.get_by_role('rowheader', name='Variant requirements / changes', exact=True))
    expect(local_row).to_contain_text('Nested local exception')
    expect(local_row).to_contain_text('Preserve the nested evidence.')
    local_row.locator('details').last.locator('summary').click()
    expect(local_row.locator('a[href="https://example.edu/family"]').last).to_be_visible()
    roots = page.locator('.compare-table tr').filter(has=page.get_by_role('rowheader', name='Requirement structure', exact=True))
    expect(roots).not_to_contain_text('Nested local exception')
    assert 'compare=test-ai-1%2Ctest-ai-0' in page.url
    page.reload()
    expect(page.locator('#filter-discipline')).to_have_value('Economics')
    expect(page.locator('.compare-table thead th')).to_have_count(3)
    page.locator('#filter-discipline').select_option('Physics')
    page.go_back()
    expect(page.locator('#filter-discipline')).to_have_value('Economics')
    page.go_forward()
    expect(page.locator('#filter-discipline')).to_have_value('Physics')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.goto(site+'programs/test-ai-1/')
    expect(page.locator('.family-context')).to_contain_text('AI and Physics')
    expect(page.locator('.requirements')).to_contain_text('Shared family requirement')
    expect(page.locator('.requirements')).to_contain_text('Local variant requirement')
    page.locator('.family-context summary').click()
    expect(page.locator('.family-context a[href$="/programs/test-ai-0/"]')).to_be_visible()
    page.reload()
    expect(page.locator('.family-context')).to_be_visible()
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    assert not errors


def test_family_native_disclosure_works_without_javascript(browser,site,tmp_path,site_data):
    from playwright.sync_api import expect
    build(family_fixture(site_data),tmp_path/'ai-program-atlas')
    context=browser.new_context(java_script_enabled=False)
    page=context.new_page()
    page.goto(site)
    page.locator('.program-family > summary').click()
    expect(page.locator('.family-variants .program-card:visible')).to_have_count(2)
    page.locator('.family-variants').get_by_role('link',name='View program').first.click()
    expect(page.locator('.family-context')).to_be_visible()
    context.close()


def test_explicit_family_exclusion_is_visible_in_compare_and_detail(page,site,tmp_path,site_data):
    from playwright.sync_api import expect
    data=family_fixture(site_data)
    p=data['programs'][1]
    p['requirements']=[r for r in p['requirements'] if r.get('origin')!='family']
    p['family']['requirement_overrides']=[{'shared_id':'shared-core','operation':'exclude','reason':'A documented exception for this variant.','source_id':'family-source'}]
    build(data,tmp_path/'ai-program-atlas')
    page.goto(site+'?compare=test-ai-0,test-ai-1')
    expect(page.locator('.compare-table')).to_contain_text('Excluded for this variant')
    expect(page.locator('.compare-table')).to_contain_text('A documented exception for this variant.')
    page.goto(site+'programs/test-ai-1/')
    expect(page.locator('.family-changes')).to_contain_text('Exclude: Shared AI core')
    expect(page.locator('.family-changes a')).to_have_attribute('href','https://example.edu/family')


@pytest.mark.parametrize('width', [1440, 390])
def test_statement_types_stay_separate_from_inferred_themes(page, site, width):
    from playwright.sync_api import expect
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.set_viewport_size({'width': width, 'height': 900})
    page.goto(site + '?compare=test-ai-0,test-ai-1')
    row = page.locator('.compare-table tr').filter(has=page.get_by_role('rowheader', name='Program aims & outcomes', exact=True))
    first = row.locator('td').nth(0)
    for text, label in [('Learn a documented skill.', 'Source statement'), ('Evaluate a model.', 'Learning outcome'), ('Connect computing and society.', 'Program aim'), ('Careers in research and industry.', 'Career pathway')]:
        item = first.locator('li').filter(has=page.get_by_text(text, exact=True))
        expect(item.locator('.statement-type')).to_have_text(label)
        expect(item.locator('a')).to_have_attribute('href', 'https://example.edu/outcome')
    expect(page.locator('.theme-table tbody tr')).to_have_count(2)
    expect(page.locator('.theme-table')).not_to_contain_text('Careers in research and industry.')
    page.reload()
    expect(first.locator('.statement-type')).to_have_count(4)
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.goto(site + 'programs/test-ai-0/')
    section = page.locator('#outcomes')
    expect(section.get_by_role('heading', name='Program aims & outcomes', exact=True)).to_be_visible()
    expect(section.locator('.outcomes').nth(0).locator('.statement-type')).to_have_text(['Source statement', 'Learning outcome', 'Program aim', 'Career pathway'])
    expect(section.locator('.outcomes').nth(1).locator('.statement-type')).to_have_text('Documented inference')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    assert not errors


@pytest.mark.parametrize('width', [1440, 390])
def test_clear_comparison_keeps_keyboard_focus(page, site, width):
    from playwright.sync_api import expect
    page.set_viewport_size({'width': width, 'height': 900})
    page.goto(site + '?compare=test-ai-0,test-ai-1')
    page.locator('#clear-comparison').focus()
    page.keyboard.press('Enter')
    expect(page.locator('#compare-title')).to_be_focused()
    expect(page.locator('#compare-title')).to_be_visible()
    expect(page.locator('#clear-comparison')).to_be_hidden()
    expect(page.locator('#comparison-content')).to_contain_text('Select “Compare”')
    expect(page.locator('#compare-status')).to_have_text('Comparison cleared.')
    assert 'compare=' not in page.url


@pytest.mark.parametrize('width', [1440, 390])
@pytest.mark.parametrize('query', ['compare=test-ai-0', 'discipline=Economics'])
def test_explicit_family_collapse_survives_reload_and_history(page, site, tmp_path, site_data, width, query):
    from playwright.sync_api import expect
    build(family_fixture(site_data), tmp_path / 'ai-program-atlas')
    page.set_viewport_size({'width': width, 'height': 900})
    page.goto(site + '?' + query)
    family = page.locator('[data-family-id="test-family"]')
    # An absent expansion parameter still reveals the selected/filtered variant.
    expect(family).to_have_attribute('open', '')
    family.locator(':scope > summary').click()
    expect(family).not_to_have_attribute('open', '')
    assert page.evaluate("new URLSearchParams(location.search).has('expand')")
    assert page.evaluate("new URLSearchParams(location.search).get('expand')") == ''
    page.reload()
    expect(family).not_to_have_attribute('open', '')
    family.locator(':scope > summary').click()
    expect(family).to_have_attribute('open', '')
    page.go_back()
    expect(family).not_to_have_attribute('open', '')
    page.go_forward()
    expect(family).to_have_attribute('open', '')
    assert '/ai-program-atlas/?' in page.url
