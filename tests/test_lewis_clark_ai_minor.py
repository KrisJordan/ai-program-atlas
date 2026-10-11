import importlib.util
import json
from pathlib import Path
import pytest
from atlas.db import validate_program
ROOT=Path(__file__).parents[1]
spec=importlib.util.spec_from_file_location('lc',ROOT/'atlas/adapters/lewis-clark-ai-minor/adapter.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def fixture():
    body='<h3>Minor Requirements: Artificial Intelligence</h3><p>A minimum of 24 credits distributed as follows:</p><ul>'
    for code in ['CS 171','CS 172','CS 369']:body+=f'<li><a class="code">{code}</a> Test core</li>'
    for label,codes in [('One mathematical course chosen from',['CS 230','ECON 303','MATH 225','MATH 255','MATH 351','MATH 352','MATH 451','PSY 311']),('One advanced or applied AI course chosen from',['CS 469']),('One social context course chosen from',['PHIL 241','RHMS 241','RHMS 360'])]:
        body+=f'<li>{label}:<table>'+''.join(f'<tr><td><a class="code">{c}</a></td><td>Test choice</td></tr>' for c in codes)+'</table></li>'
    return '<h3>Other Major</h3><p>CS999</p>'+body+'</ul><p>A minimum of 12 discrete credits are required for the minor.</p><h3>Minor Requirements: Cybersecurity</h3><li><a class="code">CS 111</a> Not AI</li>'

def test_bounded_pools_and_no_review_claim():
    p=m.parse(fixture())
    assert len(p['courses'])==15
    assert [len(r['course_ids']) for r in p['requirements'][:4]]==[3,8,1,3]
    assert [r['count'] for r in p['requirements'][:4]]==[None,1,1,1]
    assert not any(c['code']=='CS 111' for c in p['courses'])
    assert 'curriculum_audit' not in p and 'last_verified' not in p

@pytest.mark.parametrize('old,new',[('24 credits','20 credits'),('12 discrete credits','8 discrete credits'),('One mathematical course','Two mathematical courses'),('MATH 451','NOT A CODE')])
def test_changed_rule_requires_review(old,new):
    with pytest.raises(ValueError):m.parse(fixture().replace(old,new))

def test_course_metadata_observes_prerequisite_changes():
    html=''.join(f'<div class="courseblock"><p class="courseblocktitle">{code} Test</p><p>{guard} Prerequisites: TEST 101. Usually offered: Fall. Semester credits: 4.</p></div>' for code,(guard,summary) in m.SUMMARIES.items())
    a=m.parse_course_metadata(html);b=m.parse_course_metadata(html.replace('TEST 101','TEST 202'))
    assert all(c['credits']==4 and c['credit_unit']=='semester_hours' for c in a)
    assert all(c['prerequisites']=='TEST 202.' for c in b)
    with pytest.raises(ValueError):m.parse_course_metadata('<div>AI course</div>')

def test_wrong_policy_scope_rejected():
    for fn in [m.parse_minor_policy,m.parse_grading_policy,m.parse_transfer_policy]:
        with pytest.raises(ValueError):fn('<h1>Unrelated rules</h1>')

def test_reviewed_seed_integrity():
    p=json.loads((ROOT/'data/programs/lewis-clark-ai-minor.json').read_text());validate_program(p)
    assert p['curriculum_status']=='complete' and p['curriculum_audit']['scope']=='minor'
    assert p['curriculum_audit']['unresolved_requirements']==[] and p['first_offered'] is None
    assert len(p['courses'])==15 and sum(c['credits'] is not None for c in p['courses'])==5
    assert all(c['public_site'] is None and c['syllabus'] is None for c in p['courses'])
