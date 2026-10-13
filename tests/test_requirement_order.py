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


def test_course_rows_sort_codes_independently_of_titles_and_prerequisites():
    courses = [course('100', 'Methods'), course('200', 'Methods', 'No prerequisites.'), course('300', 'Methods', 'CS 100 and CS 200'), course('400', 'Methods', 'Instructor permission'), course('500', 'Introduction to computing')]
    soup = render(courses, [rule('list', 'Required courses', ['300', '400', '100', '200', '500'])])
    assert [n['data-course-id'] for n in soup.select('.requirement-course-details')] == ['100', '200', '300', '400', '500']


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


def test_literal_codes_prefixes_punctuation_crosslists_unknowns_and_stable_ties():
    codes = ['CS 2', None, 'CS 10', '16.C20[J]', '15-213', '15-122',
             'CS 10 / MATH 9', 'cs 10', '', ' CS 10 ', '6.100A']
    courses = [dict(id=str(i), code=code, name='Advanced' if i%2 else 'Introduction') for i,code in enumerate(codes)]
    soup = render(courses, [rule('list', 'Required courses', [str(i) for i in range(len(courses))])])
    assert [n['data-course-id'] for n in soup.select('.requirement-course-details')] == ['5','4','3','10','2','7','9','6','0','1','8']


def test_nested_options_sort_each_pool_without_changing_routes_or_bundles():
    courses = [course('20','Introductory'),course('10','Advanced'),course('2','Methods')]
    rules = [rule('outer','Major requirements'),rule('pool','Technical electives',['20','2','10'],'choose_courses','outer'),
             rule('routes','Alternatives',kind='alternative',parent='outer'),
             rule('first','First course route',['20','10'],parent='routes'),rule('second','Second course route',['2'],parent='routes'),
             rule('seq','Required academic sequence',parent='outer'),rule('seq-list','All of the following',['20','10'],parent='seq')]
    soup = render(courses,rules)
    assert [n['data-course-id'] for n in soup.select('#requirement-pool .requirement-course-details')] == ['10','2','20']
    assert [n['id'] for n in soup.select('#requirement-routes > details > .requirement-body > ul > li')] == ['requirement-first','requirement-second']
    assert [n['data-course-id'] for n in soup.select('#requirement-first .requirement-course-details')] == ['20','10']
    assert [n['data-course-id'] for n in soup.select('#requirement-seq .requirement-course-details')] == ['20','10']
    assert 'All 2 courses required (AND)' in soup.select_one('#requirement-first').get_text()
    assert 'Complete one route (OR)' in soup.select_one('#requirement-routes').get_text()


def test_real_cmu_additional_degree_cs_core_lexical_and_canonical_unchanged():
    program = json.loads((Path(__file__).resolve().parents[1]/'data/programs/cmu-additional-ai.json').read_text())
    before = deepcopy(program)
    soup = BeautifulSoup(requirement_tree(program),'html.parser')
    assert [n['data-course-id'] for n in soup.select('#requirement-cmu-additional-ai-computer-science-core .requirement-course-details')] == ['cmu-15-122','cmu-15-150','cmu-15-210','cmu-15-213','cmu-15-251']
    assert soup.select_one('.requirements > .requirement')['id'] == 'requirement-cmu-additional-ai-mathematics'
    assert program == before


def test_subject_groups_use_aggregate_order_without_splitting_mixed_or_unknown():
    courses = [dict(id=k,code=k,name=k,category=v) for k,v in [('m','mathematics'),('f','foundations'),('s','systems'),('a','ai_ml'),('h','human_context'),('d','applications'),('u','other')]]
    rules = [rule('unknown','Unresolved topics',['u']),rule('mixed','Mixed subjects',['m','a']),rule('apps','Domain core',['d']),rule('human','Human core',['h']),rule('ai','AI core',['a']),rule('compute','Computing core',['f','s']),rule('math','Math core',['m'])]
    soup = render(courses,rules)
    assert [n['id'] for n in soup.select('.requirements > .requirement')] == ['requirement-math','requirement-compute','requirement-ai','requirement-human','requirement-apps','requirement-unknown','requirement-mixed']
    assert len(soup.select('#requirement-mixed .requirement-course-details')) == 2
    assert 'All 2 courses required' in soup.select_one('#requirement-compute').get_text()


def test_nested_subject_choices_complete_descendants_labels_and_unknown_fallback():
    courses = [dict(id=k,code=k,name=k,category=v) for k,v in [('m','mathematics'),('f','foundations'),('s','systems'),('a','ai_ml'),('u','other')]]
    rules = [rule('root','Major requirements'),rule('ai','AI methods',['a'],'choose_courses','root'),rule('compute','Core',parent='root'),rule('system','Infrastructure',['s'],parent='compute'),rule('foundation','Methods',['f'],parent='compute'),rule('math','Mathematics',kind='choose_credits',parent='root'),rule('unavailable','Mathematics core',['missing'],'choose_courses','root'),rule('ambiguous','AI and ethics',kind='choose_credits',parent='root')]
    soup = render(courses,rules)
    children = soup.select('#requirement-root > details > .requirement-body > ul > .requirement')
    assert [n['id'] for n in children] == ['requirement-math','requirement-compute','requirement-ai','requirement-unavailable','requirement-ambiguous']
    assert 'Course records not available: missing' in soup.select_one('#requirement-unavailable').get_text()
    assert soup.select_one('#requirement-ai .requirement-rule').get_text() == 'Choose 1 course'


def test_explicit_sequence_and_named_routes_override_subject_group_sort():
    courses = [dict(id='a',code='AI 1',name='AI methods',category='ai_ml'),dict(id='m',code='MATH 1',name='Mathematics',category='mathematics')]
    rules = [rule('seq','Required academic sequence'),rule('first','AI stage',['a'],parent='seq'),rule('second','Math stage',['m'],parent='seq'),rule('routes','Alternatives',kind='alternative'),rule('route1','First course route',['a'],parent='routes'),rule('route2','Second course route',['m'],parent='routes')]
    soup = render(courses,rules)
    for parent,expected in [('seq',['first','second']),('routes',['route1','route2'])]:
        assert [n['id'] for n in soup.select('#requirement-'+parent+' > details > .requirement-body > ul > .requirement')] == ['requirement-'+i for i in expected]


def test_course_entry_nodes_are_lexical_rows_not_subject_groups():
    courses = [dict(id='a',code='15-213',name='Introduction',category='systems'),dict(id='b',code='15-122',name='Programming',category='foundations')]
    soup = render(courses,[rule('list','Computer Science Core'),rule('a','Introduction',['a'],parent='list'),rule('b','15-122',['b'],parent='list')])
    assert [n['data-course-id'] for n in soup.select('.requirement-course-details')] == ['b','a']
