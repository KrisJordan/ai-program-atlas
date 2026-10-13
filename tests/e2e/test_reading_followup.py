"""Visible route titles and page-sticky headers preserve the original graph and table."""
import json
from pathlib import Path

import pytest
from playwright.sync_api import expect

from atlas import db
from atlas.site import build
from tests.e2e import test_atlas as fixtures

browser = fixtures.browser
page = fixtures.page
site = fixtures.site
site_data = fixtures.site_data
pytestmark = pytest.mark.e2e


def real_build(tmp_path):
    conn = db.connect(tmp_path / 'reading.sqlite')
    db.migrate(conn)
    for pid in ['penn-state-ai-engineering-bs', 'unc-ai-minor']:
        seed = json.loads((Path(__file__).resolve().parents[2] / 'data/programs' / (pid + '.json')).read_text())
        db.ingest_program(conn, seed)
    build(db.export_data(conn), tmp_path / 'ai-program-atlas')
    conn.close()


@pytest.mark.parametrize('width', [1440, 390])
def test_course_routes_visible_at_branch_and_metadata_with_records(page, site, tmp_path, width):
    real_build(tmp_path)
    page.set_viewport_size({'width': width, 'height': 900})
    page.goto(site + 'programs/penn-state-ai-engineering-bs/')
    base = '#requirement-penn-state-ai-engineering-bs-major-'
    choice = page.locator(base + 'r29 > details')
    expect(choice).not_to_have_attribute('open', '')
    choice.locator(':scope > summary').focus()
    page.keyboard.press('Enter')
    expect(choice).to_have_attribute('open', '')
    expect(choice.locator(':scope > summary .requirement-rule')).to_contain_text('Complete one route (OR)')
    expect(choice.locator('.requirement-course-name')).to_have_text(['CMPSC 448 · Machine Learning and Algorithmic AI', 'CMPSC 445 · Applied Machine Learning in Data Science'])
    programming = page.locator(base + 'r23')
    expect(programming.locator('.requirement-course-name')).to_have_text(['CMPSC 131 · Programming and Computation I: Fundamentals', 'CMPSC 121 · Introduction to Programming Techniques', 'DS 120 · Scripting for Data Sciences'])
    expect(page.locator(base + 'r25 > details > summary .requirement-rule')).to_have_text('All 2 courses required (AND)')
    expect(page.locator('.brand-mark')).to_have_text('AI')
    expect(page.locator('.masthead nav a')).to_have_count(1)
    expect(page.locator('footer nav a').filter(has_text='Coverage')).to_have_attribute('href', '/ai-program-atlas/coverage/')
    expect(page.locator('footer nav a').filter(has_text='Methodology')).to_have_attribute('href', '/ai-program-atlas/methodology/')
    expect(page.locator('.detail-hero + .fact-grid')).to_have_count(0)
    expect(page.locator('#courses > .fact-grid')).to_contain_text('Calendar')
    expect(page.locator('#courses > .fact-grid')).to_contain_text('Requirement inventory')
    page.goto(site + 'programs/penn-state-ai-engineering-bs/#requirement-penn-state-ai-engineering-bs-major-r30')
    expect(page.locator(base + 'r30 .requirement-course-details')).to_have_attribute('open', '')
    expect(page.locator(base + 'r30 .requirement-course-name')).to_be_visible()
    expect(page.locator('.requirements').get_by_role('link', name='Requirement source').first).to_have_attribute('href', 'https://bulletins.psu.edu/undergraduate/colleges/engineering/artificial-intelligence-engineering-bs/')
    page.reload()
    expect(page.locator(base + 'r30 .requirement-course-details')).to_have_attribute('open', '')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')


@pytest.mark.parametrize('width', [1440, 390])
def test_sticky_two_row_headers_align_with_horizontal_scroll(page, site, tmp_path, site_data, width):
    # Long concrete rows make page scrolling meaningful without a nested vertical scroller.
    from copy import deepcopy
    original = site_data['programs'][0]
    for i in range(35):
        program = deepcopy(original)
        program.update(id=f'long-table-{i}', title=f'Long table program {i}')
        site_data['programs'].append(program)
    build(site_data, tmp_path / 'ai-program-atlas')
    page.set_viewport_size({'width': width, 'height': 900})
    page.goto(site)
    expect(page.locator('#directory-view, .directory-hero')).to_have_count(0)
    assert page.locator('#result-count').evaluate('(n) => getComputedStyle(n).position') == 'absolute'
    assert page.locator('.cohort-result-count').first.evaluate('(n) => getComputedStyle(n).position') == 'absolute'
    assert abs(page.locator('#open-filters').bounding_box()['y'] - page.locator('#sort-order').bounding_box()['y']) < 5
    wrap = page.locator('#cohort-nu-majors .directory-table-wrap')
    overlay = page.locator('#cohort-nu-majors .directory-sticky-viewport')
    wrap.evaluate('(n) => window.scrollTo(0, scrollY + n.getBoundingClientRect().top + 250)')
    expect(overlay).to_be_visible()
    assert abs(overlay.bounding_box()['y']) < 2
    expect(overlay.locator('thead tr')).to_have_count(2)
    expect(overlay).to_contain_text('Math + Statistics')
    assert overlay.locator('..').get_attribute('aria-hidden') == 'true'
    expect(overlay.locator('a, button, input')).to_have_count(0)
    if width == 1440:
        page.set_viewport_size({'width': 1100, 'height': 900})
    wrap.evaluate('(n) => {n.scrollLeft = 100}')
    page.wait_for_function("document.querySelector('#cohort-nu-majors .directory-sticky-table').style.transform === 'translateX(-100px)'")
    source = wrap.locator('thead th').all()
    copied = overlay.locator('thead th').all()
    for a, b in zip(source, copied):
        assert abs(a.bounding_box()['x'] - b.bounding_box()['x']) < 2
        assert abs(a.bounding_box()['width'] - b.bounding_box()['width']) < 2
    # Keyboard horizontal scrolling still targets the existing semantic table region.
    wrap.focus()
    expect(wrap).to_be_focused()
    before = wrap.evaluate('(n) => n.scrollLeft')
    page.keyboard.press('ArrowRight')
    page.wait_for_function(f"document.querySelector('#cohort-nu-majors .directory-table-wrap').scrollLeft > {before}")
    page.goto(site + '?view=cards')
    expect(overlay).not_to_be_visible()
    page.goto(site)
    page.locator('#open-filters').click()
    page.locator('#search').fill('absent-result-xyz')
    page.locator('#apply-filters').click()
    expect(overlay).not_to_be_visible()
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')


@pytest.mark.parametrize('width', [1440, 390])
def test_comparison_reuses_detail_tree_compact_rows_and_external_links(page, site, tmp_path, width):
    real_build(tmp_path)
    page.set_viewport_size({'width': width, 'height': 900})
    ids = 'penn-state-ai-engineering-bs,unc-ai-minor'
    page.goto(site + '?compare=' + ids + '#comparison')
    table = page.locator('.compare-table')
    for label in ['Documented selection rules', 'Last verified', 'Course metadata availability', 'Course records', 'Credit units']:
        expect(table.get_by_role('rowheader', name=label, exact=True)).to_have_count(0)
    labels = table.locator('tbody > tr > th').all_text_contents()
    assert labels[:3] == ['Official curriculum', 'Curriculum profile', 'Requirement structure']
    tree = page.locator('[data-comparison-requirements=penn-state-ai-engineering-bs]')
    expect(tree.locator('.requirements')).to_have_count(1)
    base = '#compare-requirement-penn-state-ai-engineering-bs-requirement-penn-state-ai-engineering-bs-major-'
    route = tree.locator(base + 'r29 > details')
    expect(route).not_to_have_attribute('open', '')
    route.locator(':scope > summary').focus()
    page.keyboard.press('Enter')
    expect(route).to_have_attribute('open', '')
    expect(route.locator('.requirement-course-name')).to_contain_text(['Machine Learning and Algorithmic AI', 'Applied Machine Learning in Data Science'])
    expect(tree.locator('.requirement-bundle-disclosure').first).not_to_have_attribute('open', '')
    leaf = tree.locator(base + 'r30')
    course = leaf.locator('.requirement-course-details')
    course.locator(':scope > summary').focus()
    page.keyboard.press('Enter')
    expect(course).to_have_attribute('open', '')
    expect(course.get_by_role('link', name='Full course record', exact=True)).to_have_attribute('href', '/ai-program-atlas/programs/penn-state-ai-engineering-bs/#course-psu-cmpsc-448')
    expect(tree.get_by_role('link', name='Requirement source').first).to_have_attribute('target', '_blank')
    expect(leaf.locator('.course-list-label, .requirement-courses')).to_have_count(0)
    page.locator('#compare-profile').select_option('options')
    expect(route).to_have_attribute('open', '')
    expect(course).to_have_attribute('open', '')
    assert not page.evaluate("(() => {const ids=[...document.querySelectorAll('[id]')].map(n=>n.id);return ids.length!==new Set(ids).size})()")
    assert page.locator('.comparison-outcomes .statement-text').first.evaluate('(n) => getComputedStyle(n).display') == 'inline'
    assert page.locator('a[href^="https://"], a[href^="http://"]').evaluate_all("nodes=>nodes.every(n=>n.target==='_blank' && n.rel.includes('noopener'))")
    page.goto(site + '?compare=' + ids + base + 'r30')
    expect(tree.locator(base + 'r30 .requirement-course-details')).to_have_attribute('open', '')
    page.reload()
    expect(tree.locator(base + 'r30 .requirement-course-details')).to_have_attribute('open', '')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')


def test_comparison_tree_fetch_failure_keeps_program_requirements_link(page, site, tmp_path):
    real_build(tmp_path)
    page.route('**/programs/penn-state-ai-engineering-bs/?*', lambda route: route.fulfill(status=503))
    page.goto(site + '?compare=penn-state-ai-engineering-bs#comparison')
    cell = page.locator('[data-comparison-requirements=penn-state-ai-engineering-bs]')
    expect(cell).to_contain_text('Requirement view could not be loaded')
    expect(cell.get_by_role('link')).to_have_attribute('href', '/ai-program-atlas/programs/penn-state-ai-engineering-bs/#requirements')
    expect(page.locator('.compare-table')).to_contain_text('required course obligations')


@pytest.mark.parametrize('width', [1440, 390])
def test_real_cmu_outline_flattens_only_redundant_wrappers_and_keeps_course_details(page, site, tmp_path, width):
    conn = db.connect(tmp_path / 'cmu.sqlite')
    db.migrate(conn)
    for pid in ['cmu-bs-ai', 'cmu-additional-ai', 'cmu-minor-ai']:
        seed = json.loads((Path(__file__).resolve().parents[2] / 'data/programs' / (pid + '.json')).read_text())
        db.ingest_program(conn, seed)
    build(db.export_data(conn), tmp_path / 'ai-program-atlas')
    conn.close()
    page.set_viewport_size({'width': width, 'height': 900})
    page.goto(site + 'programs/cmu-bs-ai/')
    group = page.locator('#requirement-cmu-bs-ai-computer-science')
    expect(group.locator(':scope > details > summary h3')).to_have_text('Computer Science')
    expect(group.locator('.requirement-rule')).to_have_text('All 5 courses required')
    expect(group.locator('h3')).to_have_count(1)
    expect(group.locator('.requirement-evidence')).to_have_count(1)
    expect(group.locator('.requirement-course-row')).to_have_count(5)
    for course in group.locator('.requirement-course-details').all():
        expect(course.locator(':scope > summary')).to_be_visible()
        expect(course).not_to_have_attribute('open', '')
    course = group.locator('[data-course-id=cmu-15-150]')
    course.locator(':scope > summary').focus()
    page.keyboard.press('Enter')
    expect(course).to_have_attribute('open', '')
    expect(course.locator('.prerequisite-text')).to_contain_text('15-112')
    expect(course.locator('.prerequisite-titles')).to_contain_text('Fundamentals of Programming and Computer Science')
    expect(course.locator('.prerequisite-titles')).to_contain_text('Mathematical Foundations for Computer Science')
    expect(course.locator('.prerequisite-titles a[href$="#course-cmu-15-112"]')).to_have_count(1)
    assert course.locator('.requirement-course-credits').bounding_box()['x'] > course.locator('.requirement-course-name').bounding_box()['x']
    assert group.evaluate('(n) => getComputedStyle(n).borderLeftWidth') == '0px'
    group.locator(':scope > details > summary').click()
    page.goto(site + 'programs/cmu-bs-ai/#requirement-cmu-bs-ai-computer-science-table-1')
    expect(group.locator('.requirement-course-name').first).to_be_visible()
    page.reload()
    expect(group.locator('.requirement-course-name').first).to_be_visible()
    page.goto(site + 'programs/cmu-additional-ai/')
    additional = page.locator('#requirement-cmu-additional-ai-computer-science-core')
    expect(additional.locator('h3')).to_have_count(1)
    expect(additional.locator('.requirement-rule')).to_have_text('All 5 courses required')
    expect(additional.locator('.requirement-course-row')).to_have_count(5)
    expect(page.locator('.requirements')).to_contain_text('All 2 courses required (AND) · 18 Units')
    expect(page.locator('.requirements')).to_contain_text('Complete one route (OR)')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')


@pytest.mark.parametrize('width', [1440, 390])
def test_two_visible_levels_ignore_flattened_wrappers_reset_on_navigation_and_reveal_fragments(page, site, tmp_path, site_data, width):
    p = site_data['programs'][0]
    cid = p['courses'][0]['id']
    p['sources'].append({'id': 'outline', 'url': 'https://example.edu/catalog'})
    def group(rid, title, parent=None, courses=()):
        return {'id': rid, 'title': title, 'parent_id': parent, 'kind': 'all', 'source_id': 'outline', 'summary': title, 'course_ids': list(courses)}
    p['requirements'] = [group('major', 'Major requirements'), group('wrapper', 'All of the following:', 'major'), group('direct', 'Direct child', 'wrapper'), group('deep', 'Deeper group', 'direct', [cid])]
    build(site_data, tmp_path / 'ai-program-atlas')
    page.set_viewport_size({'width': width, 'height': 900})
    url = site + 'programs/test-ai-0/'
    page.goto(url)
    expect(page.locator('#requirement-major > details')).to_have_attribute('open', '')
    expect(page.locator('#requirement-wrapper > details')).to_have_count(0)
    expect(page.locator('#requirement-direct > details')).to_have_attribute('open', '')
    deep = page.locator('#requirement-deep > details')
    expect(deep).not_to_have_attribute('open', '')
    deep.locator(':scope > summary').focus()
    page.keyboard.press('Enter')
    expect(deep).to_have_attribute('open', '')
    expect(deep.locator('.requirement-course-name')).to_be_visible()
    page.goto(site + 'programs/test-ai-1/')
    page.goto(url)
    expect(deep).not_to_have_attribute('open', '')
    page.goto(url + '#requirement-deep')
    expect(deep).to_have_attribute('open', '')
    page.reload()
    expect(deep.locator('.requirement-course-name')).to_be_visible()
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
