"""Philosophy evidence keeps missing records and formal logic distinctions honest."""
from collections import Counter
from copy import deepcopy
import hashlib
from pathlib import Path

from bs4 import BeautifulSoup
import pytest
from atlas.adapters import miami_phi_context_reviews as module
from atlas.adapters.business_society_minors import clean

PID='miami-data-science-ai-bs'


@pytest.fixture
def synthetic(monkeypatch):
    spec=deepcopy(module.SPEC)
    spec['courses']={c:spec['courses'][c] for c in ['PHI 210','PHI 247','PHI 295','PHI 544']}
    blocks=[]
    for code,entry in spec['courses'].items():
        credits='1-4' if code=='PHI 295' else '3'
        block=(f'<div class="courseblock"><p class="courseblocktitle">{code}. '
               f'{entry["name"]}. {credits} Credit Hours.</p>'
               '<p>Synthetic reviewed philosophical topic. Prerequisite: TEST 100 or TEST 200. Components: LEC.</p></div>')
        entry['block_hash']=hashlib.sha256(clean(BeautifulSoup(block,'html.parser').get_text(' ',strip=True)).encode()).hexdigest()
        blocks.append(block)
    spec['sources']['phi']['course_code_inventory_hash']=hashlib.sha256('\n'.join(sorted(spec['courses'])).encode()).hexdigest()
    monkeypatch.setattr(module,'SPEC',spec)
    return '<h1>Philosophy (PHI)</h1>'+''.join(blocks)


def test_missing_codes_are_evidence_not_fabricated_course_records(synthetic):
    result=module.parse(synthetic,pid=PID)
    records={c['code']:c for c in result['courses']}
    assert set(result['observed_missing_courses'])=={'PHI 296','PHI 301'}
    assert not set(records)&{'PHI 296','PHI 301'}
    assert records['PHI 295']['credits'] is None
    assert result['observed_credit_ranges']['PHI 295']['maximum']==4
    assert records['PHI 544']['prerequisites']=='Prerequisite: PHI 357 (249) or at least one of PHI 341 - 346.'
    assert not {'requirements','curriculum_audit','last_verified','course_identity_groups'}&set(result)
    assert all('category_review' not in c for c in records.values())


@pytest.mark.parametrize('change',['missing','duplicate','content','prerequisite','credits','new_missing_code','inventory','heading','login'])
def test_source_changes_require_review(synthetic,change):
    first=str(BeautifulSoup(synthetic,'html.parser').select_one('.courseblock'))
    new='<div class="courseblock"><p class="courseblocktitle">PHI 296. New Topic. 3 Credit Hours.</p><p>New description.</p></div>'
    edited={
        'missing':synthetic.replace(first,''),'duplicate':synthetic+first,
        'content':synthetic.replace('Synthetic reviewed philosophical topic.','New content.',1),
        'prerequisite':synthetic.replace('TEST 100 or TEST 200','TEST 100 and TEST 200',1),
        'credits':synthetic.replace('1-4 Credit Hours','3 Credit Hours',1),
        'new_missing_code':synthetic+new,
        'inventory':synthetic+new.replace('PHI 296','PHI 999'),
        'heading':synthetic.replace('Philosophy (PHI)','Other subject'),
        'login':'<h1>Login required</h1><form>Account</form>',
    }[change]
    with pytest.raises(ValueError):module.parse(edited,pid=PID)


def test_manual_review_distinguishes_formal_methods_from_philosophical_topics():
    e=module.SPEC['courses']
    assert len(e)==84 and len(module.SPEC['missing_courses'])==2
    assert Counter(c['category'] for c in e.values())=={'human_context':74,'mathematics':3,'applications':1,'other':6}
    assert {c for c,x in e.items() if x['category']=='mathematics'}=={'PHI 210','PHI 506','PHI 510'}
    assert {c for c,x in e.items() if x['review']['status']=='mixed'}=={'PHI 135','PHI 246','PHI 339','PHI 546'}
    assert {c for c,x in e.items() if x['review']['status']=='unclassified'}=={'PHI 247','PHI 295'}
    assert e['PHI 348']['category']=='applications'
    assert all(e[c]['category']=='human_context' for c in ['PHI 110','PHI 215','PHI 346','PHI 543','PHI 560','PHI 359'])
    assert e['PHI 358']['review']['rationale'].startswith('Limited precise-title')
    assert all('review' not in x for x in module.SPEC['missing_courses'].values())
    assert module.SPEC['sources']['phi']['catalog_year'] is None


def test_composition_preserves_missing_evidence_and_prior_rules(synthetic):
    old={'id':PID,'courses':[],'requirements':[{'id':'old-rule'}],
         'observed_missing_courses':{'TEST 500':{'scope':'prior observation'}}}
    before=deepcopy(old);sources=[];parsers={module.URL:lambda html:old}
    module.register(PID,sources,parsers);callback=parsers[module.URL]
    module.register(PID,sources,parsers)
    result=callback(synthetic)
    assert old==before and result['requirements']==old['requirements']
    assert callback is parsers[module.URL] and sources==[module.URL]
    assert set(result['observed_missing_courses'])=={'TEST 500','PHI 296','PHI 301'}
    with pytest.raises(ValueError):module.parse(synthetic,pid='unreviewed')


def test_optional_actual_source_replay_all_scopes():
    path=Path('.cache/research/miami-degree-audit/phi.html')
    if not path.exists():pytest.skip('Raw official capture deliberately uncommitted')
    pids={p for e in module.SPEC['courses'].values() for p in e['program_ids']}
    assert len(pids)==4
    for pid in pids:
        result=module.parse(path.read_text(),pid=pid)
        assert len(result['courses'])==84
        assert set(result['observed_missing_courses'])=={'PHI 296','PHI 301'}
