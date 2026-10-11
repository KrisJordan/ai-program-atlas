import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from atlas.adapters import northeastern_civil_course_reviews as m
from atlas.adapters.northeastern_courseleaf import clean
from atlas.curriculum_profile import requirement_profile
from atlas.families import resolve_program

PID=m.SPEC['degree_review']['program_id']


def page(content):
    return '<p>2026-2027 Edition</p><div id="site-title"><h1>'+m.SPEC['sources']['CIVE']['heading']+'</h1></div><div id="textcontainer">'+content+'</div>'


def test_source_guards_and_range(monkeypatch):
    block='<div class="courseblock"><p class="courseblocktitle">CIVE 5699. Synthetic topics. (1-4 Hours)</p><p class="cb_desc">Synthetic domain topics.</p><p class="courseblockextra">Prerequisite(s): A or B with D-</p></div>'
    spec=copy.deepcopy(m.SPEC['courses']['CIVE 5699'])
    spec['block_digest']=hashlib.sha256(clean(BeautifulSoup(block,'html.parser')).encode()).hexdigest()
    spec['description_guard']='Synthetic domain topics.'
    monkeypatch.setitem(m.SPEC['courses'],'CIVE 5699',spec)
    r=m.parse_subject(page(block),program_id=PID,subject='CIVE',codes=['CIVE 5699'])
    assert r['courses'][0]['credits'] is None
    assert r['courses'][0]['prerequisites']=='A or B with D-'
    assert any('1-4 semester hours' in n for n in r['notes'])
    assert 'category_review' not in r['courses'][0]
    for bad in [block.replace('1-4','1-3'),block.replace('D-','C-'),block+block,'']:
        with pytest.raises(ValueError):m.parse_subject(page(bad),program_id=PID,subject='CIVE',codes=['CIVE 5699'])
    with pytest.raises(ValueError):m.parse_subject(page(block).replace('2026-2027','2025-2026'),program_id=PID,subject='CIVE',codes=['CIVE 5699'])


def test_manual_content_decisions_and_conditions():
    c=m.SPEC['courses']
    assert len(c)==33
    assert Counter(x['category'] for x in c.values())=={'applications':27,'other':4,'human_context':1,'mathematics':1}
    assert c['CIVE 2222']['credits']==0 and c['CIVE 5699']['credits'] is None
    assert c['CIVE 5100']['category']=='human_context'
    assert c['CIVE 5261']['category']=='mathematics'
    assert c['CIVE 5275']['category']=='applications'
    assert c['CIVE 5699']['review']['status']=='unclassified'
    assert 'graduate program admission' in c['CIVE 5150']['prerequisites']
    assert c['CIVE 5280']['conditions'][0]['kind']=='recommended_preparation'
    assert c['CIVE 5363']['conditions'][0]['kind']=='graduate_assignment'


def source(subject):
    path=Path('.cache/http')/(hashlib.sha256(m.SOURCES[subject].encode()).hexdigest()+'.body')
    if not path.exists():pytest.skip('Ignored actual course cache not available')
    return path.read_text()


def test_actual_all_blocks_and_conditional_preparation():
    r=m.parse_subject(source('CIVE'),program_id=PID,subject='CIVE')
    c={x['code']:x for x in r['courses']}
    assert len(c)==31 and c['CIVE 2222']['credits']==0
    assert 'one semester of fluid mechanics' in c['CIVE 5281']['prerequisites']
    assert 'one semester of undergraduate chemistry' in c['CIVE 5368']['prerequisites']
    assert c['CIVE 5280']['prerequisites'] is None
    assert any('preferred' in n for n in r['notes'])
    assert any('Graduate students' in n for n in r['notes'])
    html=source('CIVE')
    soup=BeautifulSoup(html,'html.parser')
    for b in soup.select('.courseblock'):
        if clean(b.select_one('.courseblocktitle')).startswith('CIVE 2221.'):
            b.decompose()
    with pytest.raises(ValueError,match='missing'):
        m.parse_subject(str(soup),program_id=PID,subject='CIVE',codes=['CIVE 2222'])
    assert len(m.parse_subject(source('GE'),program_id=PID,subject='GE')['courses'])==2


def test_source_bundle_correction_and_manual_roles():
    path=Path('.cache/research/degree-audit-northeastern')/(PID+'.html')
    if not path.exists():pytest.skip('Ignored actual degree cache not available')
    html=path.read_text()
    seed=json.loads(Path('data/programs',PID+'.json').read_text())
    family=json.loads(Path('data/families/northeastern-ai-combined-degrees.json').read_text())
    p=resolve_program(seed,family)
    if not any(r['id']==PID+'-req-introductory-engineering-bundle' for r in p['requirements']):
        before=requirement_profile(p)
        p=m.apply_degree_correction(p,html)
        after=requirement_profile(p)
        assert before['required']['count']-after['required']['count']==2
        assert after['options']['count']-before['options']['count']==4
    for c in p['courses']:
        if c['code'] in m.SPEC['courses']:c['category']=m.SPEC['courses'][c['code']]['category']
    spec=m.SPEC['degree_review'];profile=requirement_profile(p)
    lookup={c['id']:c for c in p['courses']}
    for role,ids in spec['expected_course_ids'].items():
        for cid in ids:assert requirement_profile({**p,'courses':[lookup[cid]]})[role]['count']==1
        assert profile[role]['count']==spec['expected_profile'][role]['count']
        assert {k:v for k,v in profile[role]['categories'].items() if v}==spec['expected_profile'][role]['categories']
    choice=PID+'-req-introductory-engineering-bundle'
    children=[r for r in p['requirements'] if r.get('parent_id')==choice]
    assert len(children)==2 and all(r['kind']=='all' and len(r['course_ids'])==2 for r in children)
    with pytest.raises(ValueError):m.apply_degree_correction(copy.deepcopy(p),html.replace('135 total semester hours','136 total semester hours'))
