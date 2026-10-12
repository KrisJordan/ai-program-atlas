"""Display ordering and expansion do not change recorded academic rules."""
import json
from copy import deepcopy
from pathlib import Path

from bs4 import BeautifulSoup

from atlas.site import requirement_tree


def course(cid, name, prerequisites=None):
    return {'id': cid, 'code': 'CS ' + cid, 'name': name, 'prerequisites': prerequisites}


def rule(rid, title, courses=(), kind='all', parent=None):
    return {'id': rid, 'title': title, 'kind': kind, 'parent_id': parent, 'course_ids': list(courses), 'count': 1 if kind == 'choose_courses' else None}


def render(courses, requirements):
    program = {'id': 'test', 'courses': courses, 'requirements': requirements}
    before = deepcopy(program)
    result = BeautifulSoup(requirement_tree(program), 'html.parser')
    assert program == before
    assert {n['id'] for n in result.select('.requirement')} == {'requirement-' + r['id'] for r in requirements}
    return result


def test_core_before_electives_and_prerequisite_heavy_required_siblings():
    courses = [course('100', 'Fundamentals of programming'), course('200', 'Methods'), course('300', 'Methods', 'CS 100 and CS 200')]
    soup = render(courses, [rule('elective', 'Technical electives', ['100'], 'choose_courses'), rule('heavy', 'Required methods', ['300']), rule('early', 'Required fundamentals', ['100']), rule('other', 'Other required methods', ['200'])])
    assert [n['id'] for n in soup.select('.requirements > .requirement')] == ['requirement-early', 'requirement-other', 'requirement-heavy', 'requirement-elective']


def test_course_rows_keep_unknown_neutral_and_stable_ties():
    courses = [course('100', 'Methods'), course('200', 'Methods', 'No prerequisites.'), course('300', 'Methods', 'CS 100 and CS 200'), course('400', 'Methods', 'Instructor permission'), course('500', 'Introduction to computing')]
    soup = render(courses, [rule('list', 'Required courses', ['300', '400', '100', '200', '500'])])
    assert [n['data-course-id'] for n in soup.select('.requirement-course-details')] == ['500', '200', '400', '100', '300']


def test_named_route_order_survives_heuristics():
    courses = [course('100', 'Introduction'), course('300', 'Advanced methods', 'CS 100')]
    soup = render(courses, [rule('first', 'First course route', ['300']), rule('second', 'Second course route', ['100'])])
    assert [n['id'] for n in soup.select('.requirements > .requirement')] == ['requirement-first', 'requirement-second']


def test_large_pool_threshold_and_empty_open_scope():
    courses = [course(str(i), 'Methods') for i in range(6)]
    soup = render(courses, [rule('five', 'Five choices', [str(i) for i in range(5)], 'choose_courses'), rule('six', 'Six choices', [str(i) for i in range(6)], 'choose_courses'), rule('open', 'Approved elective categories', kind='choose_credits')])
    assert soup.select_one('#requirement-five > details').has_attr('open')
    assert not soup.select_one('#requirement-six > details').has_attr('open')
    assert soup.select_one('#requirement-six .requirement-rule').get_text() == 'Choose 1 course · 6 listed courses'
    assert '0 listed' not in soup.select_one('#requirement-open').get_text()


def test_routes_count_bundles_once():
    courses = [course(str(i), 'Methods') for i in range(12)]
    rules = [rule('pool', 'Options', kind='choose_courses')]
    rules += [rule('route-' + str(i), 'Course bundle', [str(2 * i), str(2 * i + 1)], parent='pool') for i in range(6)]
    soup = render(courses, rules)
    assert '6 listed routes' in soup.select_one('#requirement-pool > details > summary').get_text()
    assert not soup.select_one('#requirement-pool > details').has_attr('open')
    assert len(soup.select('.requirement-course-details')) == 12


def test_mixed_pool_course_inventory_is_not_hidden_by_few_policy_children():
    courses = [course(str(i), 'Methods') for i in range(6)]
    soup = render(courses, [rule('pool', 'Electives', [str(i) for i in range(6)], 'choose_courses'), rule('policy', 'Permission required', kind='note', parent='pool')])
    assert not soup.select_one('#requirement-pool > details').has_attr('open')
    assert '6 listed courses · 1 recorded branch' in soup.select_one('#requirement-pool > details > summary').get_text()


def test_real_penn_concentration_names_visible_one_level_and_pools_closed():
    program = json.loads((Path(__file__).resolve().parents[1] / 'data/programs/penn-bse-ai.json').read_text())
    before = deepcopy(program)
    soup = BeautifulSoup(requirement_tree(program), 'html.parser')
    assert program == before
    assert soup.select_one('#requirements-group-optional-top > details').has_attr('open')
    assert soup.select_one('#requirement-penn-bse-ai-optional-concentrations > details').has_attr('open')
    for rid in ['optional-robotics', 'optional-machine-learning', 'optional-vision-language', 'technical-electives', 'ai-electives-6-cus']:
        node = soup.select_one('#requirement-penn-bse-ai-' + rid)
        assert not node.select_one(':scope > details').has_attr('open')
        assert 'listed courses' in node.select_one(':scope > details > summary').get_text()
    assert 'not an additional degree requirement' in soup.get_text()


def test_optional_policy_and_fields_do_not_open_concentration_bundle():
    soup = render([course('100', 'Introduction')], [rule('field', 'Optional HASS field: Music', ['100']), rule('policy', 'Optional pass/fail policy', kind='note')])
    assert not soup.select_one('#requirements-group-optional-top > details').has_attr('open')
