"""Five chapter identity guards and bounded manual subject review."""
from collections import Counter
from copy import deepcopy
import hashlib
from pathlib import Path
from bs4 import BeautifulSoup
import pytest
from atlas.adapters import miami_area_studies_context_reviews as m
from atlas.adapters.business_society_minors import clean
PID='miami-data-science-ai-bs'

@pytest.fixture
def synthetic(monkeypatch):
    spec=deepcopy(m.SPEC);spec['courses']={c:e for c,e in spec['courses'].items() if c in ['AAS 350','AMS 301','AMS 331','ASG 150','CUB 201','GHS 312','GHS 440']};pages={}
    for key,source in spec['sources'].items():
        blocks=[];codes=[]
        for code,e in spec['courses'].items():
            if e['key']!=key:continue
            amount='0-3' if code=='AMS 301' else '3'
            block=f'<div class="courseblock"><p class="courseblocktitle">{code}. {e["name"]}. {amount} Credit Hours.</p><p>Synthetic distinct content. Prerequisite: TEST 100. Components: LEC.</p></div>'
            e['block_hash']=hashlib.sha256(clean(BeautifulSoup(block,'html.parser').get_text(' ',strip=True)).encode()).hexdigest();blocks.append(block);codes.append(code)
        source['course_code_inventory_hash']=hashlib.sha256('\n'.join(sorted(codes)).encode()).hexdigest()
        pages[key]='<h1>'+source['heading']+'</h1>'+''.join(blocks)
    monkeypatch.setattr(m,'SPEC',spec);return pages


def test_explicit_conditions_and_unknown_selected_topics(synthetic):
    aas=m.parse(synthetic['aas'],pid=PID,key='aas')['courses'][0]
    assert aas['prerequisites']=='Prerequisite: 3 Credits in AAS.'
    ghs=m.parse(synthetic['ghs'],pid=PID,key='ghs');courses={c['code']:c for c in ghs['courses']}
    assert courses['GHS 440']['prerequisites']=='Prerequisite: GHS 310 or GHS 312 .'
    assert courses['GHS 312']['category']=='other'
    assert set(ghs['observed_missing_courses'])=={'GHS 370'}
    assert 'GHS 370' not in courses
    ams=m.parse(synthetic['ams'],pid=PID,key='ams')
    assert ams['observed_credit_ranges']['AMS 301']=={'minimum':0,'maximum':3,'credit_unit':'semester_hours'}
    assert next(c for c in ams['courses'] if c['code']=='AMS 301')['credits'] is None
    for key in synthetic:
        result=m.parse(synthetic[key],pid=PID,key=key)
        assert not {'requirements','curriculum_audit','last_verified','course_identity_groups','curriculum_status'}&result.keys()
        assert all('category_review' not in c for c in result['courses'])


@pytest.mark.parametrize('key',['aas','ams','asg','cub','ghs'])
def test_each_chapter_rejects_wrong_identity_and_changed_content(synthetic,key):
    for html in [synthetic[key].replace('Synthetic distinct content.','Different topic.',1),synthetic[key].replace('TEST 100','TEST 101',1),synthetic[key].replace('Credit Hours','Credits',1),'<h1>Sign in</h1>',synthetic[key]+str(BeautifulSoup(synthetic[key],'html.parser').select_one('.courseblock'))]:
        with pytest.raises(ValueError):m.parse(html,pid=PID,key=key)


def test_newly_present_missing_code_requires_review(synthetic):
    block=str(BeautifulSoup(synthetic['ghs'],'html.parser').select_one('.courseblock')).replace('GHS 312','GHS 370')
    with pytest.raises(ValueError,match='Previously missing'):m.parse(synthetic['ghs']+block,pid=PID,key='ghs')


def test_manual_review_scope_and_no_missing_review():
    entries=m.SPEC['courses'];assert len(entries)==45
    assert Counter(e['category'] for e in entries.values())=={'human_context':36,'other':9}
    assert Counter(e['review']['status'] for e in entries.values())=={'reviewed':36,'mixed':4,'unclassified':5}
    assert entries['AMS 321']['category']=='human_context'
    assert entries['AMS 331']['review']['status']=='unclassified'
    assert entries['ASG 401']['review']['candidate_categories']==['applications','human_context']
    assert 'review' not in m.SPEC['missing_courses']['GHS 370']
    assert all(s['catalog_year'] is None for s in m.SPEC['sources'].values())


def test_registration_preserves_prior_result(synthetic):
    old={'id':PID,'courses':[],'requirements':[{'id':'prior'}]};snapshot=deepcopy(old)
    url=m.SPEC['sources']['ghs']['url'];sources=[];parsers={url:lambda html:old}
    m.register(PID,sources,parsers);callback=parsers[url];m.register(PID,sources,parsers)
    result=callback(synthetic['ghs']);assert old==snapshot and result['requirements']==old['requirements']
    assert callback is parsers[url] and len(sources)==5


@pytest.mark.parametrize('key',['aas','ams','asg','cub','ghs'])
def test_optional_actual_four_scope_replays(key):
    path=Path('.cache/research/miami-degree-audit',key+'.html')
    if not path.exists():pytest.skip('Raw official capture deliberately ignored')
    pids={p for e in m.SPEC['courses'].values() if e['key']==key for p in e['program_ids']}
    assert len(pids)==4
    for pid in pids:
        result=m.parse(path.read_text(),pid=pid,key=key)
        assert len(result['courses'])=={'aas':8,'ams':24,'asg':2,'cub':1,'ghs':10}[key]
