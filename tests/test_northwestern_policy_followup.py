import json
from pathlib import Path
import pytest
from atlas.adapters import northwestern_degree_policies as p
from atlas.db import validate_program


def test_intro_exceptions_are_reextracted_not_four_static_choices():
    html='''<h1>Artificial Intelligence Major, BS in Engineering</h1><p>introductory courses that directly support computer science (COG_SCI 207-0, COMP_SCI 1CA, MATH 228-2). Scores of 4 or 5 on the AP CS A; scores of 5, 6, or 7 on the IB CS HL; PHYSICS 125-1; PHYSICS 140-1; GEN_ENG 212-0.</p>'''
    r=p.parse_major_exceptions(html,'https://example.edu/major')
    assert len(r['requirements'][0]['course_ids'])==3
    assert r['requirements'][1]['kind']=='choose_courses' and r['requirements'][1]['count']==1
    changed=p.parse_major_exceptions(html.replace('MATH 228-2','MATH 229-2'),'https://example.edu/major')
    assert 'MATH 229-2' in {c['code']for c in changed['courses']}
    assert all(c['credits']is None for c in r['courses'])
    with pytest.raises(ValueError):p.parse_major_exceptions(html.replace('introductory courses that directly support computer science','revised'),'https://example.edu/major')


def test_theme_predicates_exclusions_and_changed_allowed_code():
    html='''<h1>Undergraduate Social Science and Humanities Theme Requirements</h1><p>maximum of five courses; minimum of three; up to four 100-level courses if three are foreign language; Half-unit (1/2) and one-third (1/3); By the end of your sophomore year</p><table><tr><th>Social &amp; Behavioral Sciences</th><th>Humanities</th></tr><tr><td><p>ECON - Synthetic economics</p></td><td><p>PHIL - Synthetic philosophy</p></td></tr></table><table><tr><th>Courses Allowed</th><th>Courses NOT Allowed</th></tr><tr><td><p>GEOG 1xx - Social Sciences</p></td><td><p>ECON 281</p></td></tr></table>'''
    r=p.parse_theme(html)
    assert 'courses' not in r
    assert 'GEOG 1xx' in next(n['summary']for n in r['requirements']if n['id'].endswith('exceptions-0'))
    changed=p.parse_theme(html.replace('ECON 281','ECON 282'))
    assert 'ECON 282' in next(n['summary']for n in changed['requirements']if n['id'].endswith('exceptions-1'))
    with pytest.raises(ValueError):p.parse_theme(html.replace('Courses NOT Allowed','Other'))


def test_duplicate_bundle_and_order_condition_preserved():
    html='''<h1>Course Duplicates</h1><p>Duplicates are not alternatives from which to choose; only one of them can be used; ONLY if COMP_SCI 111 is taken first; ONLY if COMP_SCI 211 is taken first</p><h2>Duplicate Courses List</h2><h2>Synthetic department</h2><ul><li>AAA 100 &amp; BBB 101 and BBB 102 (only before 2020)</li></ul>'''
    r=p.parse_duplicate_sets(html)
    assert 'BBB 101 and BBB 102' in r['requirements'][-1]['summary']
    assert 'only before 2020' in r['requirements'][-1]['summary']
    assert r['requirements'][-1]['course_ids']==[]


def test_seed_boundaries_and_no_legacy_ai_grade_inference():
    d=json.loads(Path('data/programs/'+p.PID+'.json').read_text());validate_program(d)
    assert d['curriculum_status']=='partial'
    pool=next(n for n in d['requirements']if n['id'].endswith('policy-advanced-intro'))
    assert len(pool['course_ids'])==14
    assert any('2018' in n['summary'] and 'distinct AI' in n['summary']for n in d['requirements'])
    assert any('major 21 units' in n['summary'] and 'major is 22' in n['summary'] for n in d['requirements'])
    assert any('eight units versus eight courses' in s for s in d['curriculum_audit']['unresolved_requirements'])
    science=next(n for n in d['requirements']if n['title']=='Approved basic-science pool')
    assert science['kind']=='choose_credits' and science['credits']==4
    assert any(len(n['course_ids'])==2 and n['kind']=='all' for n in d['requirements']if n['id'].startswith('nw-bse-college-'))
