import hashlib
import json
from pathlib import Path
import pytest
from bs4 import BeautifulSoup
from atlas.adapters import njit_rutgers_history_reviews as m
from atlas.adapters.national_curriculum_common import clean
from atlas import db


def fixture(monkeypatch, conflict=False):
    block='<p>21:510:201,202 Example historical inquiry (3,3) Invented description. Prerequisite: Permission.</p>'
    digest=hashlib.sha256(clean(BeautifulSoup(block,'html.parser').get_text(' ',strip=True)).encode()).hexdigest()
    monkeypatch.setattr(m,'SPEC',{'R510 '+n:dict(source_url=m.URLS['510'],title='Example historical inquiry',digest=digest,
       identity_conflict=conflict,rutgers_code='21:510:'+n,njit_title='Previous example',credits=3,
       description='Invented historical inquiry.',prerequisites='Prerequisite: Permission.') for n in ['201','202']})
    return '<div role="tab" aria-selected="true">Courses (History 510)</div><section role="tabpanel"><h3>Courses (History 510)</h3>'+block+'</section>'


def test_paired_codes_are_distinct_observations_and_no_review(monkeypatch):
    html=fixture(monkeypatch);result=m.parse(html,'510')
    assert [c['id'] for c in result['courses']]==['njit-r510-201','njit-r510-202']
    assert all(c['credits']==3 and c['prerequisites']=='Prerequisite: Permission.' for c in result['courses'])
    assert all('category_review' not in c for c in result['courses'])
    assert 'curriculum_audit' not in result and 'course_identity_groups' not in result
    for before,after in [('Invented description','Changed description'),('3,3','4,4')]:
        with pytest.raises(ValueError,match='changed'):m.parse(html.replace(before,after),'510')
    with pytest.raises(ValueError,match='Duplicate'):m.parse(html.replace('</section>','<p>21:510:201,202 Example historical inquiry (3,3) Invented description. Prerequisite: Permission.</p></section>'),'510')


def test_conflicts_not_silently_mapped_and_missing_capture_rejected(monkeypatch):
    html=fixture(monkeypatch,True);result=m.parse(html,'510')
    assert result['courses']==[] and len(result['observed_identity_conflicts'])==2
    for bad in ['<h1>History overview</h1>',html.replace('aria-selected="true"','aria-selected="false"'),html.replace('Courses (History 510)','Other course tab')]:
        with pytest.raises(ValueError):m.parse(bad,'510')
    with pytest.raises(ValueError,match='Previously missing'):
        m.parse(html.replace('</section>','<p>21:510:489 Newly added course (3) New content.</p></section>'),'510')


def test_actual_captures_when_available():
    path=Path('/tmp/atlas-rutgers-history-captures.json')
    if not path.exists():pytest.skip('Ignored rendered source captures unavailable')
    counts=[]
    for cap in json.loads(path.read_text()):
        result=m.parse(cap['html'],cap['section'][-3:]);counts.append((len(result['courses']),len(result['observed_identity_conflicts'])))
    assert counts==[(84,4),(52,1)]
    policy=Path('/tmp/atlas-rutgers-credit-policy.html')
    if policy.exists():assert m.parse_credit_policy(policy.read_text())['observed_credit_unit']=='semester_hours'


def test_history_seed_conflicts_and_absences_remain_unknown():
    p=json.loads(Path('data/programs',m.PID+'.json').read_text());db.validate_program(p)
    courses={c['code']:c for c in p['courses']}
    for code in ['R510 257','R510 325','R510 351','R510 404','R512 405','R510 489','R512 364']:
        assert courses[code]['category']=='other'
        assert courses[code]['category_review']['status']=='unclassified'
        assert courses[code]['description'] is None
    assert courses['R510 325']['name']=='The Ancient World'
    assert courses['R510 201']['credits']==3 and courses['R510 202']['credits']==3
    assert courses['R512 350']['category']=='human_context'  # Computer use supports historical inquiry.
    assert 'highly recommended' in courses['R512 350']['prerequisites']
    assert courses['R510 401']['description'] is None  # Precise title only, not manufactured topic prose.
    assert all(c['category_review']['status']=='reviewed' for c in p['courses'] if c['code'] in m.SPEC and not m.SPEC[c['code']]['identity_conflict'])
