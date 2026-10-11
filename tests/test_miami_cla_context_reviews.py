"""Classics source identity, absent codes and content-specific dispositions."""
from collections import Counter
from copy import deepcopy
import hashlib
from pathlib import Path
from bs4 import BeautifulSoup
import pytest
from atlas.adapters import miami_cla_context_reviews as module
from atlas.adapters.business_society_minors import clean
PID='miami-data-science-ai-bs'

@pytest.fixture
def synthetic(monkeypatch):
    spec=deepcopy(module.SPEC)
    spec['courses']={c:spec['courses'][c] for c in ['CLA 101','CLA 102','CLA 224','CLA 326','CLA 401']}
    blocks=[]
    for code,e in spec['courses'].items():
        block=f'<div class="courseblock"><p class="courseblocktitle">{code}. {e["name"]}. 3 Credit Hours.</p><p>Distinct synthetic reviewed source. Requisite: TEST 100. Components: LEC.</p></div>'
        e['block_hash']=hashlib.sha256(clean(BeautifulSoup(block,'html.parser').get_text(' ',strip=True)).encode()).hexdigest()
        blocks.append(block)
    spec['sources']['cla']['course_code_inventory_hash']=hashlib.sha256('\n'.join(sorted(spec['courses'])).encode()).hexdigest()
    monkeypatch.setattr(module,'SPEC',spec)
    return '<h1>Classics (CLA)</h1>'+''.join(blocks)


def test_literal_mismatched_references_and_philosophical_ai_scope(synthetic):
    result=module.parse(synthetic,pid=PID);courses={c['code']:c for c in result['courses']}
    assert courses['CLA 326']['category']=='human_context'
    assert courses['CLA 401']['category']=='other'
    assert courses['CLA 101']['prerequisites']=='Requisite: Not Allow Enrollment in CLA 220 if already Enrolled/Took CLA 219.'
    assert courses['CLA 102']['prerequisites']=='Requisite: Not Allow Enrollment in CLA 219 if already Enrolled/Took CLA 220.'
    assert set(result['observed_missing_courses'])=={'CLA 201'}
    assert not {'CLA 201','CLA 219','CLA 220'}&courses.keys()
    assert not {'requirements','curriculum_audit','last_verified','course_identity_groups'}&result.keys()
    assert all('category_review' not in c for c in courses.values())


@pytest.mark.parametrize('change',['missing','duplicate','body','eligibility','credits','heading','login','formerly_missing','new_inventory'])
def test_changed_source_requires_review(synthetic,change):
    first=str(BeautifulSoup(synthetic,'html.parser').select_one('.courseblock'))
    changed={'missing':synthetic.replace(first,''),'duplicate':synthetic+first,
      'body':synthetic.replace('Distinct synthetic reviewed source.','Changed content.',1),
      'eligibility':synthetic.replace('TEST 100','TEST 101',1),
      'credits':synthetic.replace('3 Credit Hours','4 Credit Hours',1),
      'heading':synthetic.replace('Classics (CLA)','Other'),
      'login':'<h1>Sign in</h1><form>Login</form>',
      'formerly_missing':synthetic+first.replace('CLA 101','CLA 201'),
      'new_inventory':synthetic+first.replace('CLA 101','CLA 999')}[change]
    with pytest.raises(ValueError):module.parse(changed,pid=PID)


def test_manual_scope_and_unreviewed_absence():
    entries=module.SPEC['courses'];assert len(entries)==42
    assert Counter(e['category'] for e in entries.values())=={'human_context':38,'other':4}
    assert {c for c,e in entries.items() if e['review']['status']=='unclassified'}=={'CLA 401','CLA 402','CLA 403','CLA 505'}
    assert set(module.SPEC['missing_courses'])=={'CLA 201'}
    assert 'review' not in module.SPEC['missing_courses']['CLA 201']
    assert 'truncated' in entries['CLA 224']['review']['rationale']
    assert entries['CLA 211']['category']=='human_context'
    assert all(e['credits']==3 for e in entries.values())
    assert module.SPEC['sources']['cla']['catalog_year'] is None


def test_composition_keeps_old_scope_without_certification(synthetic):
    old={'id':PID,'courses':[],'requirements':[{'id':'prior'}]};snapshot=deepcopy(old)
    sources=[];parsers={module.URL:lambda html:old};module.register(PID,sources,parsers)
    callback=parsers[module.URL];module.register(PID,sources,parsers);result=callback(synthetic)
    assert callback is parsers[module.URL] and sources==[module.URL]
    assert old==snapshot and result['requirements']==old['requirements']
    assert set(result['observed_missing_courses'])=={'CLA 201'}


def test_optional_actual_chapter_four_scopes():
    path=Path('.cache/research/miami-degree-audit/cla.html')
    if not path.exists():pytest.skip('Official raw capture deliberately ignored')
    pids={p for e in module.SPEC['courses'].values() for p in e['program_ids']}
    assert len(pids)==4
    for pid in pids:
        result=module.parse(path.read_text(),pid=pid)
        assert len(result['courses'])==42 and set(result['observed_missing_courses'])=={'CLA 201'}
