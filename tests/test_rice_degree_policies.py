from pathlib import Path
import hashlib
import json
import pytest
from atlas.adapters import rice_degree_policies as m
from atlas.db import validate_program

ROOT=Path(__file__).resolve().parents[1]


def test_distribution_designation_criteria_do_not_fabricate_course_pool():
    spec=next(s for s in m.GRAD_RULES if s[0]=='distribution')
    html='<main><h1>Graduation Requirements</h1><p>Synthetic policy: at least 3 courses of at least 3 credit hours each, from at least two departments. External equivalent at least 2.5 semester credit hours. Designation at the time of course registration or at the time of matriculation.</p></main>'
    d=m.observe(html,'Graduation Requirements',[spec],'graduation')
    r=d['requirements'][0]
    assert r['kind']=='note' and r['course_ids']==[]
    assert 'each of Groups I, II and III' in r['summary']
    with pytest.raises(ValueError):m.observe(html.replace('two departments','one department'),'Graduation Requirements',[spec],'graduation')


def test_repeat_credit_does_not_erase_earlier_grades():
    spec=next(s for s in m.REGISTRATION_RULES if s[0]=='repeats')
    html='<main><h1>Registration</h1><p>Synthetic record of all attempts; credit is awarded only for the course with the highest grade; credit will be removed from the transfer or advanced placement credit. Students may not receive credit twice for cross-listed subjects.</p></main>'
    d=m.observe(html,'Registration',[spec],'registration')
    assert 'All attempts and grades remain' in d['requirements'][0]['summary']
    assert 'unless repeatable' in d['requirements'][0]['summary']
    assert not {'curriculum_audit','curriculum_status','last_verified'} & d.keys()


def test_residency_conflict_remains_explicit_in_manual_audit():
    d=json.loads((ROOT/'data/programs'/f'{m.PID}.json').read_text())
    validate_program(d)
    assert d['curriculum_status']=='partial'
    assert any('summer' in x and 'fall/spring' in x for x in d['curriculum_audit']['unresolved_requirements'])


@pytest.mark.parametrize('url,parse',list(m.SOURCE_PARSERS.items()))
def test_optional_real_policy_replay(url,parse):
    p=ROOT/'.cache/http'/(hashlib.sha256(url.encode()).hexdigest()+'.body')
    if not p.exists():pytest.skip('Raw official source cache is optional')
    d=parse(p.read_text());assert d['requirements']
    assert not {'curriculum_audit','curriculum_status','last_verified'} & d.keys()
