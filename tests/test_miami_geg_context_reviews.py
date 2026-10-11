"""Geography mixed-content, missing identities and variable-credit observations."""
from collections import Counter
from copy import deepcopy
import hashlib
from pathlib import Path
from bs4 import BeautifulSoup
import pytest
from atlas.adapters import miami_geg_context_reviews as module
from atlas.adapters.business_society_minors import clean
PID='miami-data-science-ai-bs'

@pytest.fixture
def synthetic(monkeypatch):
    spec=deepcopy(module.SPEC)
    spec['courses']={c:spec['courses'][c] for c in ['GEG 101','GEG 315','GEG 338','GEG 580','GEG 590']}
    blocks=[]
    for code,e in spec['courses'].items():
        amount='1-6' if code=='GEG 590' else '3'
        block=f'<div class="courseblock"><p class="courseblocktitle">{code}. {e["name"]}. {amount} Credit Hours.</p><p>Distinct synthetic source content. Requisite: TEST 100. Components: LEC.</p></div>'
        e['block_hash']=hashlib.sha256(clean(BeautifulSoup(block,'html.parser').get_text(' ',strip=True)).encode()).hexdigest()
        blocks.append(block)
    spec['sources']['geg']['course_code_inventory_hash']=hashlib.sha256('\n'.join(sorted(spec['courses'])).encode()).hexdigest()
    monkeypatch.setattr(module,'SPEC',spec)
    return '<h1>Geography and Sustainable Development (GEG)</h1>'+''.join(blocks)


def test_source_conditions_range_and_missing_scope(synthetic):
    result=module.parse(synthetic,pid=PID);courses={c['code']:c for c in result['courses']}
    assert courses['GEG 101']['category']=='other'
    assert courses['GEG 315']['category']=='applications'
    assert courses['GEG 580']['category']=='other'
    assert courses['GEG 338']['prerequisites']=='Requisite: One introductory course from GEG or GSC or ECS.'
    assert courses['GEG 590']['credits'] is None
    assert result['observed_credit_ranges']['GEG 590']=={'minimum':1,'maximum':6,'credit_unit':'semester_hours'}
    assert courses['GEG 590']['prerequisites']=='Content and prerequisites vary by semester; no specific prerequisite is stated.'
    assert set(result['observed_missing_courses'])=={'GEG 261'}
    assert 'GEG 261' not in courses
    assert not {'requirements','curriculum_audit','curriculum_status','last_verified','course_identity_groups'}&result.keys()
    assert all('category_review' not in c for c in courses.values())


@pytest.mark.parametrize('change',['missing','duplicate','body','eligibility','credits','range','heading','login','formerly_missing','new_inventory'])
def test_source_changes_require_review(synthetic,change):
    first=str(BeautifulSoup(synthetic,'html.parser').select_one('.courseblock'))
    changed={'missing':synthetic.replace(first,''),'duplicate':synthetic+first,
      'body':synthetic.replace('Distinct synthetic source content.','New topic.',1),
      'eligibility':synthetic.replace('TEST 100','TEST 101',1),
      'credits':synthetic.replace('3 Credit Hours','4 Credit Hours',1),
      'range':synthetic.replace('1-6 Credit Hours','1-9 Credit Hours'),
      'heading':synthetic.replace('Geography and Sustainable Development (GEG)','Other'),
      'login':'<h1>Sign in</h1><form>Login</form>',
      'formerly_missing':synthetic+first.replace('GEG 101','GEG 261'),
      'new_inventory':synthetic+first.replace('GEG 101','GEG 999')}[change]
    with pytest.raises(ValueError):module.parse(changed,pid=PID)


def test_manual_dispositions_and_qualified_unknowns():
    entries=module.SPEC['courses'];assert len(entries)==47
    assert Counter(e['category'] for e in entries.values())=={'human_context':22,'applications':9,'other':16}
    assert Counter(e['review']['status'] for e in entries.values())=={'reviewed':31,'mixed':12,'unclassified':4}
    assert {c for c,e in entries.items() if e['review']['status']=='unclassified'}=={'GEG 105','GEG 562','GEG 580','GEG 590'}
    assert entries['GEG 306']['review']['candidate_categories']==['mathematics','human_context']
    assert entries['GEG 406']['review']['candidate_categories']==['applications','mathematics']
    assert all(entries[c]['category']=='applications' for c in ['GEG 315','GEG 321','GEG 414'])
    assert entries['GEG 359']['category']=='applications'
    assert 'review' not in module.SPEC['missing_courses']['GEG 261']
    assert module.SPEC['sources']['geg']['catalog_year'] is None


def test_registration_preserves_prior_scoped_facts(synthetic):
    old={'id':PID,'courses':[],'requirements':[{'id':'prior'}]};snapshot=deepcopy(old)
    sources=[];parsers={module.URL:lambda html:old};module.register(PID,sources,parsers)
    callback=parsers[module.URL];module.register(PID,sources,parsers);result=callback(synthetic)
    assert callback is parsers[module.URL] and sources==[module.URL]
    assert old==snapshot and result['requirements']==old['requirements']
    assert set(result['observed_missing_courses'])=={'GEG 261'}


def test_optional_actual_chapter_all_scopes():
    path=Path('.cache/research/miami-degree-audit/geg.html')
    if not path.exists():pytest.skip('Raw official capture deliberately ignored')
    pids={p for e in module.SPEC['courses'].values() for p in e['program_ids']}
    assert len(pids)==4
    for pid in pids:
        result=module.parse(path.read_text(),pid=pid)
        assert len(result['courses'])==47 and set(result['observed_missing_courses'])=={'GEG 261'}
        assert set(result['observed_credit_ranges'])=={'GEG 590'}
