"""Selected content, external credit, replacement statements and travel conditions."""
from collections import Counter
from copy import deepcopy
import hashlib
from pathlib import Path
from bs4 import BeautifulSoup
import pytest
from atlas.adapters import miami_judaic_latin_urban_context_reviews as m
from atlas.adapters.business_society_minors import clean
PID='miami-data-science-ai-bs'

@pytest.fixture
def synthetic(monkeypatch):
    spec=deepcopy(m.SPEC);spec['courses']={c:e for c,e in spec['courses'].items() if c in ['JUS 205','JUS 421','LAS 101','LAS 111','LAS 302','LAS 369','URB 201']};pages={}
    for key,source in spec['sources'].items():
        blocks=[];codes=[]
        for code,e in spec['courses'].items():
            if e['key']!=key:continue
            amount='1-3' if code in {'JUS 421','LAS 111'} else '3'
            block=f'<div class="courseblock"><p class="courseblocktitle">{code}. {e["name"]}. {amount} Credit Hours.</p><p>Synthetic distinct topic. Prerequisite: TEST 100. Components: LEC.</p></div>'
            e['block_hash']=hashlib.sha256(clean(BeautifulSoup(block,'html.parser').get_text(' ',strip=True)).encode()).hexdigest();blocks.append(block);codes.append(code)
        source['course_code_inventory_hash']=hashlib.sha256('\n'.join(sorted(codes)).encode()).hexdigest()
        pages[key]='<h1>'+source['heading']+'</h1>'+''.join(blocks)
    monkeypatch.setattr(m,'SPEC',spec);return pages


def test_conditions_and_replacement_statement_are_not_equivalence(synthetic):
    result=m.parse(synthetic['las'],pid=PID,key='las');courses={c['code']:c for c in result['courses']}
    assert 'replaces LAS 201' in courses['LAS 101']['description']
    assert 'LAS 201' not in courses
    assert courses['LAS 111']['credits'] is None
    assert result['observed_credit_ranges']['LAS 111']=={'minimum':1,'maximum':3,'credit_unit':'semester_hours'}
    assert courses['LAS 302']['prerequisites']=='Course involves travel during Spring Break and it has a program fee.'
    assert courses['LAS 369']['prerequisites']=='Prerequisite: LAS 101 .'
    for key in synthetic:
        result=m.parse(synthetic[key],pid=PID,key=key)
        assert not {'requirements','curriculum_audit','last_verified','course_identity_groups','curriculum_status'}&result.keys()
        assert all('category_review' not in c for c in result['courses'])


@pytest.mark.parametrize('key',['jus','las','urb'])
def test_changed_source_or_wrong_chapter_requires_review(synthetic,key):
    for html in [synthetic[key].replace('Synthetic distinct topic.','Changed subject.',1),synthetic[key].replace('TEST 100','TEST 101',1),synthetic[key].replace('Credit Hours','Credits',1),'<h1>Sign in</h1>',synthetic[key]+str(BeautifulSoup(synthetic[key],'html.parser').select_one('.courseblock'))]:
        with pytest.raises(ValueError):m.parse(html,pid=PID,key=key)
    other='las' if key!='las' else 'jus'
    with pytest.raises(ValueError):m.parse(synthetic[other],pid=PID,key=key)


def test_credit_range_changes_require_review(synthetic):
    with pytest.raises(ValueError):m.parse(synthetic['jus'].replace('1-3 Credit Hours','1-6 Credit Hours'),pid=PID,key='jus')


def test_manual_source_subjects_and_unspecified_content():
    entries=m.SPEC['courses'];assert len(entries)==47
    assert Counter(e['category'] for e in entries.values())=={'human_context':35,'applications':1,'other':11}
    assert Counter(e['review']['status'] for e in entries.values())=={'reviewed':36,'mixed':1,'unclassified':10}
    assert entries['JUS 205']['review']['candidate_categories']==['applications','human_context']
    assert entries['JUS 421']['review']['status']=='unclassified'
    assert entries['LAS 340']['category']=='applications'
    assert entries['LAS 580']['category']=='human_context'
    assert entries['LAS 491']['review']['status']=='unclassified'
    assert len([e for e in entries.values() if e['credit_range']])==7
    assert m.SPEC['missing_courses']=={}
    assert all(s['catalog_year'] is None for s in m.SPEC['sources'].values())


def test_composition_retains_old_scope(synthetic):
    old={'id':PID,'courses':[],'requirements':[{'id':'prior'}]};snapshot=deepcopy(old)
    url=m.SPEC['sources']['las']['url'];sources=[];parsers={url:lambda html:old}
    m.register(PID,sources,parsers);callback=parsers[url];m.register(PID,sources,parsers)
    result=callback(synthetic['las']);assert old==snapshot and result['requirements']==old['requirements']
    assert callback is parsers[url] and len(sources)==3


@pytest.mark.parametrize('key',['jus','las','urb'])
def test_optional_actual_four_scope_replays(key):
    path=Path('.cache/research/miami-degree-audit',key+'.html')
    if not path.exists():pytest.skip('Official raw capture deliberately ignored')
    pids={p for e in m.SPEC['courses'].values() if e['key']==key for p in e['program_ids']};assert len(pids)==4
    for pid in pids:
        result=m.parse(path.read_text(),pid=pid,key=key)
        assert len(result['courses'])=={'jus':17,'las':28,'urb':2}[key]
        assert not result['observed_missing_courses']
