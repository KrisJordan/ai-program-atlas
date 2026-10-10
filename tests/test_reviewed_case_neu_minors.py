"""Synthetic structural fragments test source-sensitive local minor extraction."""
import importlib
import json
from pathlib import Path

import pytest

from atlas.adapters.reviewed_minors_2026 import parse_case, parse_neu_ai, parse_neu_interdisciplinary, policy_observation
from atlas.requirements import validate_requirements, validate_curriculum_audit


def head(title):return f'<tr class="areaheader"><td colspan="2">{title}</td><td class="hourscol"></td></tr>'
def rule(text,hours=''):return f'<tr><td colspan="2">{text}</td><td class="hourscol">{hours}</td></tr>'
def course(code,name='Test name',hours='',orcode=False):
    return f'<tr class="{"orclass" if orcode else ""}"><td class="codecol"><a class="code" href="/course">{code}</a></td><td>{name}</td><td class="hourscol">{hours}</td></tr>'
def table(rows):return '<table class="sc_courselist">'+rows+'</table>'
def doc(body,scope='minorrequirementstextcontainer'):
    return '<h1>Artificial Intelligence, Minor</h1><p>2026-2027</p><p>prior coursework in computer science and mathematics</p><div id="'+scope+'">'+body+'</div>'


def case_fixture():
    return doc('<p>The minor consists of six courses. No more than four courses can be double counted.</p>'+table(head('Required Courses:')+course('CSDS 330',hours='3')+course('CSDS 340',hours='3')+head('Societal Impact Elective')+rule('Choose one of the following:')+course('PHIL 210')+head('Technical Electives')+rule('Choose three of the following:')+course('CSDS 335/435')+rule('Total Credit Hours 18')),'programrequirementstextcontainer')


def interdisciplinary_fixture():
    return doc(table(head('Technology and Ethics')+rule('Complete one of the following:',4)+course('PHIL 1145')+course('PHIL 1300')+course('DS 1300',orcode=True)+head('Experiential, Project-Based, and Applied Coursework')+rule('Complete one of the following:',4)+course('INMI 2710')+head('Electives')+rule('Complete two of the following not used to fulfill another requirement; prerequisite rules apply:',8)+course('PHIL 1300')+course('INMI 2710')+course('BUSN 3501'))+'<p>Minimum 2.000 GPA</p>')


def bundle(code1,code2):
    return f'<tr><td class="codecol"><a class="code">{code1}</a><br>and <a class="code">{code2}</a></td><td>Lecture<br>and Lab</td><td class="hourscol">5</td></tr>'


def ai_fixture():
    policy='<p>Only non–Khoury majors; at most one Khoury minor. A self-assessment allows 4-5 semester hours at 3000 level or higher, not otherwise required in the degree.</p>'
    return doc(policy+table(head('Fundamental Courses')+bundle('CS 2000','CS 2001')+bundle('CS 2100','CS 2101')+head('Artificial Intelligence Foundations')+course('DS 3000',hours='4')+course('DS 4400',hours='4'))+table(rule('Complete one of the following:',4)+course('CS 3200')+rule('DS 2010 to DS 4989')+rule('Meaningful Minor list'))+table(head('Arts, Media and Design')+course('ARTG 5100')))


def test_case_course_choices_overlap_and_changed_rules():
    p=parse_case(case_fixture(),'test','source','https://example.edu/')
    validate_requirements(p)
    assert p['requirements'][0]['credits']==18
    assert next(r for r in p['requirements'] if r['title']=='Technical Electives')['count']==3
    assert len(p['courses'])==4 and sum(c['credits'] is not None for c in p['courses'])==2
    changed=parse_case(case_fixture().replace('Choose three','Choose two').replace('than four','than three'),'test','source','https://example.edu/')
    assert next(r for r in changed['requirements'] if r['title']=='Technical Electives')['count']==2
    assert 'At most 3' in changed['requirements'][-1]['summary']
    assert changed['curriculum_status']=='partial' and 'curriculum_audit' not in changed


def test_interdisciplinary_crosslist_dedup_and_changed_count():
    p=parse_neu_interdisciplinary(interdisciplinary_fixture(),'test','source','https://example.edu/')
    validate_requirements(p)
    assert len(p['courses'])==4
    assert next(c for c in p['courses'] if c['code'].startswith('PHIL 1300'))['code']=='PHIL 1300 / DS 1300'
    assert all(c['credits'] is None for c in p['courses'])
    assert any('group' in r['title'].lower() for r in p['requirements'])
    changed=parse_neu_interdisciplinary(interdisciplinary_fixture().replace('Complete two','Complete three'),'test','source','https://example.edu/')
    assert next(r for r in changed['requirements'] if r['title']=='Electives')['count']==3


def test_khoury_bundles_range_and_open_placement_rule():
    p=parse_neu_ai(ai_fixture(),'test','source','https://example.edu/')
    validate_requirements(p)
    assert len(p['courses'])==8
    assert all(c['credits'] is None for c in p['courses'] if c['code'].startswith('CS '))
    assert next(r for r in p['requirements'] if r['id']=='neu-ai-first-programming')['credits']==5
    assert any('2010 through 4989' in r['summary'] for r in p['requirements'])
    assert any('4–5' in r['summary'] for r in p['requirements'])
    with pytest.raises(ValueError,match='count changed'):
        parse_neu_ai(ai_fixture().replace('Complete one','Complete two'),'test','source','https://example.edu/')


def test_university_overlap_policy_change_is_observed():
    policy='<div id="textcontainer">A minor consists of a minimum of four courses (16 semester hours). A maximum of 50% of the credits required for a minor may overlap. Declare by end of the junior year; finish concurrently; may not extend. Programs cannot be a subset of required courses.</div>'
    p=policy_observation(policy,'test','policy','neu');q=policy_observation(policy.replace('50%','40%'),'test','policy','neu')
    assert '50%' in p['requirements'][0]['summary'] and '40%' in q['requirements'][0]['summary']
    assert p['observed_policy_digest']!=q['observed_policy_digest']


@pytest.mark.parametrize('pid,course_count',[
    ('case-western-reserve-university-artificial-intelligence-minor-minor',26),
    ('northeastern-university-artificial-intelligence-minor-minor-minor',48),
    ('northeastern-university-interdisciplinary-artificial-intelligence-minor-minor',19),
])
def test_curated_complete_minors_have_source_scoped_audits(pid,course_count):
    p=json.loads((Path(__file__).resolve().parents[1]/'data/programs'/f'{pid}.json').read_text())
    validate_requirements(p);validate_curriculum_audit(p)
    assert p['curriculum_status']=='complete' and p['curriculum_audit']['scope']=='minor'
    assert len(p['courses'])==course_count
    assert len({c['id'] for c in p['courses']})==course_count
    assert len(p['sources'])>=2
    m=importlib.import_module('atlas.adapters.'+pid+'.adapter')
    assert set(m.SOURCE_PARSERS)==set(m.SOURCES[1:])
