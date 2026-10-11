"""International Studies actual-content and source-change boundaries."""
from collections import Counter
from copy import deepcopy
import hashlib
from pathlib import Path
from bs4 import BeautifulSoup
import pytest
from atlas.adapters import miami_ins_context_reviews as module
from atlas.adapters.business_society_minors import clean
PID='miami-data-science-ai-bs'

@pytest.fixture
def synthetic(monkeypatch):
    spec=deepcopy(module.SPEC);spec['courses']={c:spec['courses'][c] for c in ['INS 101','INS 320','INS 357','INS 421']};blocks=[]
    for code,e in spec['courses'].items():
        block=f'<div class="courseblock"><p class="courseblocktitle">{code}. {e["name"]}. 3 Credit Hours.</p><p>Synthetic reviewed context. Requisite: TEST 100. Components: LEC.</p></div>'
        e['block_hash']=hashlib.sha256(clean(BeautifulSoup(block,'html.parser').get_text(' ',strip=True)).encode()).hexdigest();blocks.append(block)
    monkeypatch.setattr(module,'SPEC',spec)
    return '<h1>International Studies (INS)</h1>'+''.join(blocks)


def test_exact_restrictions_no_identity_or_curriculum_promotion(synthetic):
    result=module.parse(synthetic,pid=PID);records={c['code']:c for c in result['courses']}
    assert records['INS 101']['prerequisites']=='Requisite: If took POL 203 , cannot take INS 101 .'
    assert records['INS 320']['prerequisites']=='Prerequisite: INS 102 or ECO 211 or ECO 212 .'
    assert records['INS 357']['category']=='applications'
    assert records['INS 421']['category']=='human_context'
    assert not {'course_identity_groups','requirements','curriculum_audit','last_verified'}&set(result)
    assert all('category_review' not in c for c in records.values())


@pytest.mark.parametrize('change',['missing','duplicate','body','eligibility','credits','heading','login'])
def test_invalid_or_changed_source_is_not_certified(synthetic,change):
    first=str(BeautifulSoup(synthetic,'html.parser').select_one('.courseblock'))
    edited={'missing':synthetic.replace(first,''),'duplicate':synthetic+first,
            'body':synthetic.replace('Synthetic reviewed context.','New topic.',1),
            'eligibility':synthetic.replace('TEST 100','TEST 200',1),
            'credits':synthetic.replace('3 Credit Hours','6 Credit Hours',1),
            'heading':synthetic.replace('International Studies (INS)','Other chapter'),
            'login':'<h1>Sign in</h1><form>Login</form>'}[change]
    with pytest.raises(ValueError):module.parse(edited,pid=PID)


def test_manual_dispositions_and_scope_limits():
    e=module.SPEC['courses'];assert len(e)==70
    assert Counter(x['category'] for x in e.values())=={'human_context':49,'applications':8,'other':13}
    assert {c for c,x in e.items() if x['category']=='applications'}=={f'INS {n}' for n in [102,320,322,357,420,520,521,551]}
    assert all(x['credits']==3 and x['credit_range'] is None for x in e.values())
    assert e['INS 202']['review']['status']=='unclassified'
    assert 'body emphasizes' in e['INS 509']['description']
    assert 'body emphasizes' in e['INS 518']['description']
    assert module.SPEC['sources']['ins']['catalog_year'] is None


def test_registration_preserves_original_response(synthetic):
    old={'id':PID,'courses':[],'requirements':[{'id':'preserve'}]};before=deepcopy(old)
    sources=[];parsers={module.URL:lambda html:old};module.register(PID,sources,parsers);callback=parsers[module.URL]
    module.register(PID,sources,parsers);result=callback(synthetic)
    assert old==before and result['requirements']==old['requirements']
    assert callback is parsers[module.URL] and sources==[module.URL]
    with pytest.raises(ValueError):module.parse(synthetic,pid='unreviewed')


def test_optional_actual_source_all_four_programs():
    path=Path('.cache/research/miami-degree-audit/ins.html')
    if not path.exists():pytest.skip('Official raw capture deliberately uncommitted')
    pids={p for e in module.SPEC['courses'].values() for p in e['program_ids']};assert len(pids)==4
    for pid in pids:
        result=module.parse(path.read_text(),pid=pid);assert len(result['courses'])==70
        for c in result['courses']:
            e=module.SPEC['courses'][c['code']]
            assert (c['name'],c['credits'],c['prerequisites'])==(e['name'],e['credits'],e['prerequisites'])
