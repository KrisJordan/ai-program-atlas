"""GSS actual department catalog content; no inferred GHS substitution."""
from collections import Counter
from copy import deepcopy
import hashlib
from pathlib import Path
from bs4 import BeautifulSoup
import pytest
from atlas.adapters import miami_gss_context_reviews as m
from atlas.adapters.business_society_minors import clean
PID='miami-data-science-ai-bs'

@pytest.fixture
def synthetic(monkeypatch):
    spec=deepcopy(m.SPEC);spec['courses']={c:spec['courses'][c] for c in ['GSS 347','GSS 360','GSS 469','GSS 471']};blocks=[]
    for code,e in spec['courses'].items():
        block=f'<div class="courseblock"><p class="courseblocktitle">{code}. {e["name"]}. 3 Credit Hours.</p><p>Distinct reviewed source content. Prerequisite: TEST 100. Components: LEC.</p></div>'
        e['block_hash']=hashlib.sha256(clean(BeautifulSoup(block,'html.parser').get_text(' ',strip=True)).encode()).hexdigest();blocks.append(block)
    monkeypatch.setattr(m,'SPEC',spec)
    return '<h1>Gender and Sexuality Studies</h1>'+''.join(blocks)


def test_actual_enrollment_alternatives_and_medical_social_scope(synthetic):
    result=m.parse(synthetic,pid=PID);courses={c['code']:c for c in result['courses']}
    assert courses['GSS 347']['category']=='human_context'
    assert courses['GSS 360']['category']=='other'
    assert courses['GSS 360']['prerequisites']=='Prerequisite: GSS 201 or GSS 202 .'
    assert courses['GSS 469']['prerequisites']=='Prerequisite: POL 201 or POL 202 Or GSS 202 or GSS 301 .'
    assert courses['GSS 471']['prerequisites']=='Prerequisite: POL 202 .'
    assert not any(c.startswith(('POL','GHS')) for c in courses)
    assert not {'requirements','curriculum_audit','last_verified','course_identity_groups','curriculum_status'}&result.keys()
    assert all('category_review' not in c for c in courses.values())


@pytest.mark.parametrize('change',['missing','duplicate','body','prerequisite','credits','heading','login','wrong_subject'])
def test_changed_source_or_global_health_cannot_supply_gss(synthetic,change):
    first=str(BeautifulSoup(synthetic,'html.parser').select_one('.courseblock'))
    changed={'missing':synthetic.replace(first,''),'duplicate':synthetic+first,
      'body':synthetic.replace('Distinct reviewed source content.','New subject.',1),
      'prerequisite':synthetic.replace('TEST 100','TEST 101',1),
      'credits':synthetic.replace('3 Credit Hours','4 Credit Hours',1),
      'heading':synthetic.replace('Gender and Sexuality Studies','Other chapter'),
      'login':'<h1>Sign in</h1><form>Login</form>',
      'wrong_subject':synthetic.replace('GSS ','GHS ')}[change]
    with pytest.raises(ValueError):m.parse(changed,pid=PID)


def test_manual_exact_scope_and_current_source_navigation():
    entries=m.SPEC['courses'];assert len(entries)==23
    assert Counter(e['category'] for e in entries.values())=={'human_context':19,'other':4}
    assert {c for c,e in entries.items() if e['review']['status']=='unclassified'}=={'GSS 350','GSS 360','GSS 370','GSS 450'}
    assert all(e['description'] and e['credits']==3 for e in entries.values())
    assert m.URL=='https://bulletin.miami.edu/undergraduate-academic-programs/arts-sciences/womens-gender-studies/'
    assert m.SPEC['sources']['gss']['catalog_year'] is None
    assert len(m.SPEC['navigation_evidence'])==4
    assert 'GSS 590' not in entries


def test_same_source_composition_preserves_old_requirements(synthetic):
    old={'id':PID,'courses':[],'requirements':[{'id':'prior'}]};before=deepcopy(old)
    sources=[];parsers={m.URL:lambda html:old};m.register(PID,sources,parsers);callback=parsers[m.URL]
    m.register(PID,sources,parsers);result=callback(synthetic)
    assert old==before and result['requirements']==old['requirements']
    assert callback is parsers[m.URL] and sources==[m.URL]


def test_actual_current_department_courses_all_scopes():
    path=Path('.cache/research/miami-degree-audit/gss.html')
    if not path.exists():pytest.skip('Raw source capture deliberately ignored')
    pids={p for e in m.SPEC['courses'].values() for p in e['program_ids']};assert len(pids)==4
    for pid in pids:
        result=m.parse(path.read_text(),pid=pid)
        assert len(result['courses'])==23
        assert all(c['description'] for c in result['courses'])
