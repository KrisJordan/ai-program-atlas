"""Actual sociology content, conditional preparation and changed-source guards."""
from collections import Counter
from copy import deepcopy
import hashlib
from pathlib import Path
from bs4 import BeautifulSoup
import pytest
from atlas.adapters import miami_soc_context_reviews as module
from atlas.adapters.business_society_minors import clean
PID='miami-data-science-ai-bs'

@pytest.fixture
def synthetic(monkeypatch):
    spec=deepcopy(module.SPEC)
    spec['courses']={c:spec['courses'][c] for c in ['SOC 210','SOC 211','SOC 372','SOC 470']}
    blocks=[]
    for code,e in spec['courses'].items():
        block=f'<div class="courseblock"><p class="courseblocktitle">{code}. {e["name"]}. 3 Credit Hours.</p><p>Synthetic reviewed context. Prerequisite: TEST 100. Corequisite: TEST 200. Components: LEC.</p></div>'
        e['block_hash']=hashlib.sha256(clean(BeautifulSoup(block,'html.parser').get_text(' ',strip=True)).encode()).hexdigest()
        blocks.append(block)
    monkeypatch.setattr(module,'SPEC',spec)
    return '<h1>Sociology and Criminology (SOC)</h1>'+''.join(blocks)


def test_actual_content_dispositions_and_conditional_prerequisites(synthetic):
    result=module.parse(synthetic,pid=PID)
    courses={c['code']:c for c in result['courses']}
    assert courses['SOC 210']['category']=='other'
    assert courses['SOC 211']['category']=='mathematics'
    assert courses['SOC 372']['category']=='human_context'
    assert courses['SOC 211']['prerequisites']=='Prerequisite: SOC 101 , 210 . Corequisite: 212.'
    assert courses['SOC 470']['prerequisites']=='Prerequisite: SOC 101 and SOC 371 .'
    assert 'SOC 212' not in courses
    assert not {'requirements','course_identity_groups','curriculum_audit','last_verified','curriculum_status'} & result.keys()
    assert all('category_review' not in c for c in courses.values())


@pytest.mark.parametrize('change',['missing','duplicate','body','prerequisite','corequisite','credits','heading','login'])
def test_changed_or_wrong_source_cannot_replay_reviews(synthetic,change):
    first=str(BeautifulSoup(synthetic,'html.parser').select_one('.courseblock'))
    changed={
        'missing':synthetic.replace(first,''),'duplicate':synthetic+first,
        'body':synthetic.replace('Synthetic reviewed context.','Different subject.',1),
        'prerequisite':synthetic.replace('TEST 100','TEST 101',1),
        'corequisite':synthetic.replace('TEST 200','TEST 201',1),
        'credits':synthetic.replace('3 Credit Hours','4 Credit Hours',1),
        'heading':synthetic.replace('Sociology and Criminology (SOC)','Different chapter'),
        'login':'<h1>Sign in</h1><form>Authentication required</form>'
    }[change]
    with pytest.raises(ValueError):module.parse(changed,pid=PID)


def test_manual_complete_assignment_and_unknown_boundaries():
    entries=module.SPEC['courses']
    assert len(entries)==49
    assert Counter(e['category'] for e in entries.values())=={'human_context':45,'mathematics':1,'other':3}
    assert {c for c,e in entries.items() if e['review']['status']=='unclassified'}=={'SOC 210','SOC 291','SOC 391'}
    assert all(e['credits']==3 and e['credit_range'] is None for e in entries.values())
    assert entries['SOC 345']['category']=='human_context'
    assert 'no specific mathematical' in entries['SOC 345']['review']['rationale']
    assert entries['SOC 303']['prerequisites'] is None
    assert module.SPEC['sources']['soc']['catalog_year'] is None


def test_registration_is_idempotent_and_preserves_existing_scope(synthetic):
    old={'id':PID,'courses':[],'requirements':[{'id':'prior-policy'}]}
    snapshot=deepcopy(old);sources=[];parsers={module.URL:lambda html:old}
    module.register(PID,sources,parsers);callback=parsers[module.URL]
    module.register(PID,sources,parsers)
    result=callback(synthetic)
    assert old==snapshot and result['requirements']==old['requirements']
    assert callback is parsers[module.URL] and sources==[module.URL]
    with pytest.raises(ValueError):module.parse(synthetic,pid='unknown-program')


def test_optional_actual_capture_all_assigned_program_scopes():
    path=Path('.cache/research/miami-degree-audit/soc.html')
    if not path.exists():pytest.skip('Raw official capture deliberately uncommitted')
    pids={p for e in module.SPEC['courses'].values() for p in e['program_ids']}
    assert len(pids)==4
    for pid in pids:
        result=module.parse(path.read_text(),pid=pid)
        assert len(result['courses'])==49
        for c in result['courses']:
            e=module.SPEC['courses'][c['code']]
            assert (c['name'],c['description'],c['credits'],c['prerequisites'])==(e['name'],e['description'],e['credits'],e['prerequisites'])
