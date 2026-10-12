"""Preview complete routes without promoting choices or losing source graph nodes."""
from copy import deepcopy

import pytest
from bs4 import BeautifulSoup

from atlas.site import requirement_tree


def node(rid, parent=None, kind='all', courses=(), source='source', **kwargs):
    return dict(id=rid, title=rid, parent_id=parent, kind=kind, course_ids=list(courses), source_id=source, **kwargs)


def program(route_children):
    return {'courses': [{'id': 'one', 'code': 'CS 101', 'name': 'Programming'}, {'id': 'two', 'code': 'DS 120', 'name': 'Scripting'}], 'requirements': [node('Choice', kind='alternative'), node('Route', parent='Choice'), *route_children]}


def test_course_routes_are_visible_without_concatenated_headers():
    p = program([node('All of the following:', parent='Route', courses=['one', 'two'])])
    p['sources'] = [{'id': 'source', 'url': 'https://example.edu/catalog'}]
    before = deepcopy(p)
    soup = BeautifulSoup(requirement_tree(p), 'html.parser')
    assert soup.select_one('#requirement-Choice > details > summary .requirement-rule').get_text() == 'Complete one route (OR)'
    assert soup.select_one('#requirement-Route > details > summary h3').get_text() == 'Route'
    assert soup.select_one('#requirement-Route > details > summary .requirement-rule').get_text() == 'All 2 courses required (AND)'
    alias = soup.find(id='requirement-All of the following:')
    assert 'requirement-flattened' in alias['class']
    assert len(alias.select('.requirement-course-row')) == 2
    assert not alias.select('h3')
    assert all(n.has_attr('open') for n in soup.select('.requirement-disclosure'))
    assert not any(n.has_attr('open') for n in soup.select('.requirement-course-details'))
    assert {n['id'] for n in soup.select('.requirement')} == {'requirement-' + n['id'] for n in p['requirements']}
    assert p == before


@pytest.mark.parametrize('children', [
    [node('Note', parent='Route', kind='note'), node('Leaf', parent='Note', courses=['one'])],
    [node('Nested choice', parent='Route', kind='choose_courses', courses=['one', 'two'], count=1)],
    [node('Unknown', parent='Route', courses=['one', 'missing'])],
    [node('Other source', parent='Route', courses=['one'], source='other')],
    [node('First', parent='Route', courses=['one']), node('Second', parent='Route', courses=['two'])],
])
def test_uncertain_branched_context_or_cross_source_routes_remain_structural(children):
    soup = BeautifulSoup(requirement_tree(program(children)), 'html.parser')
    assert not soup.select('.requirement-flattened')
    assert not soup.select('.requirement-preview')
    assert soup.select_one('#requirement-Route > details > summary h3').get_text() == 'Route'


@pytest.mark.parametrize('extra', [
    {'credits': 6, 'credit_unit': 'semester_hours'}, {'count': 2},
    {'summary': 'One course may be substituted with advisor approval.'},
    {'source_text': 'Earn a C or better in both courses.'},
    {'source_id': 'other'}, {'origin': 'replacement'}, {'component': 'ai_core'},
    {'course_ids': ['one', 'unknown']},
])
def test_wrapper_policies_thresholds_sources_and_unknowns_never_flatten(extra):
    child = node('All of the following:', parent='Route', courses=['one', 'two'])
    child.update(extra)
    p = program([child])
    p['sources'] = [{'id': 'source', 'url': 'https://example.edu/catalog'}, {'id': 'other', 'url': 'https://example.edu/exception'}]
    soup = BeautifulSoup(requirement_tree(p), 'html.parser')
    wrapper = soup.find(id='requirement-All of the following:')
    assert 'requirement-flattened' not in wrapper['class']
    assert wrapper.select_one(':scope > details.requirement-disclosure')
    if extra.get('summary'):
        assert extra['summary'] in wrapper.get_text()
    if extra.get('source_text'):
        assert extra['source_text'] in wrapper.get_text()


def test_real_cmu_computer_science_has_one_rule_five_rows_and_original_anchors():
    import json
    from pathlib import Path
    p = json.loads((Path(__file__).resolve().parents[1] / 'data/programs/cmu-bs-ai.json').read_text())
    before = deepcopy(p)
    soup = BeautifulSoup(requirement_tree(p), 'html.parser')
    group = soup.select_one('#requirement-cmu-bs-ai-computer-science')
    assert group.select_one(':scope > details > summary h3').get_text() == 'Computer Science'
    assert group.select_one(':scope > details > summary .requirement-rule').get_text() == 'All 5 courses required'
    assert len(group.select('.requirement-course-row')) == 5
    assert len(group.select('.requirement-rule')) == 1
    assert len(group.select('.requirement-evidence')) == 1
    assert len(group.select('h3')) == 1
    assert 'requirement-flattened' in group.select_one('#requirement-cmu-bs-ai-computer-science-table-1')['class']
    assert {n['id'] for n in soup.select('.requirement')} == {'requirement-' + n['id'] for n in p['requirements']}
    assert p == before
