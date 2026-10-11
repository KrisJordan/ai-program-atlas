import hashlib
import json
from pathlib import Path
import pytest
from bs4 import BeautifulSoup
from atlas import db
from atlas.adapters import njit_rutgers_other_reviews as m
from atlas.adapters.national_curriculum_common import clean
from atlas.curriculum_profile import requirement_profile


def fixture(monkeypatch):
    block='<p>21:120:101-102 Example life science (4,4) Invented biological inquiry.</p>'
    panel='<section role="tabpanel">'+block+'</section>'
    digest=lambda h:hashlib.sha256(clean(BeautifulSoup(h,'html.parser').get_text(' ',strip=True)).encode()).hexdigest()
    monkeypatch.setattr(m,'SPEC',dict(sources={'120':dict(url='https://example.edu/#courses',tab='Courses',heading='Biology',panel_digest=digest(panel))},courses={'R120 '+n:dict(subject='120',title='Example life science',digest=digest(block),credits=4,category='applications',description='Invented life-science study.',prerequisites=None,credit_conflict=False) for n in ['101','102']}))
    return '<h1>Biology</h1><div role="tab" aria-selected="true">Courses</div>'+panel


def test_guarded_sequence_observations_preserve_separate_identities(monkeypatch):
    html=fixture(monkeypatch);o=m.parse(html,'120')
    assert [c['id'] for c in o['courses']]==['njit-r120-101','njit-r120-102']
    assert all(c['credits']==4 and c['prerequisites'] is None for c in o['courses'])
    assert all('category_review' not in c for c in o['courses'])
    assert 'curriculum_audit' not in o and 'course_identity_groups' not in o
    for before,after in [('biological','mathematical'),('4,4','3,3')]:
        with pytest.raises(ValueError,match='changed'):m.parse(html.replace(before,after),'120')
    for bad in ['<h1>Sign in</h1>',html.replace('aria-selected="true"','aria-selected="false"')]:
        with pytest.raises(ValueError,match='tab required'):m.parse(bad,'120')


def test_actual_current_subject_captures_when_available():
    f=Path('/tmp/atlas-rutgers-other-captures.json')
    if not f.exists():pytest.skip('Ignored rendered source captures unavailable')
    counts={}
    for cap in json.loads(f.read_text()):
        o=m.parse(cap['html'],cap['subject']);counts[cap['subject']]=len(o['courses'])
        if cap['subject']=='216':
            assert o['observed_credit_conflicts']==[dict(code='R216 206',rutgers_credits=1,njit_credits=3)]
            assert o['requirements'][0]['kind']=='note'
    assert counts=={'120':2,'216':4,'460':4,'830':2,'920':1}


def test_integrated_subject_scope_and_credit_conflict():
    p=json.loads(Path('data/programs',m.PID+'.json').read_text());db.validate_program(p)
    cs={c['code']:c for c in p['courses']}
    assert all('category_review' in c for c in p['courses'])
    assert len(p['courses'])==381
    for code in m.SPEC['missing']:
        assert cs[code]['category_review']['status']=='unclassified'
        assert cs[code]['description'] is None
    assert cs['R216 206']['credits'] is None
    assert cs['R216 205']['credits']==3
    assert 'Corequisite: 21:216:205' in cs['R216 206']['prerequisites']
    assert 'either order' in cs['R830 101']['prerequisites']
    assert cs['R920 201']['category']=='human_context'
    profile=requirement_profile(p)
    assert (profile['required']['count'],profile['options']['count'])==(32,348)
    assert profile['required']['classification']['unreviewed']==0
    assert profile['options']['classification']['unreviewed']==0
