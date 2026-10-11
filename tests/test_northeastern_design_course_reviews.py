import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from atlas.adapters import northeastern_design_course_reviews as m
from atlas.adapters.northeastern_courseleaf import clean
from atlas.curriculum_profile import requirement_profile
from atlas.families import resolve_program

PID=m.SPEC['degree_review']['program_id']


def source(subject):
    path=Path('.cache/http')/(hashlib.sha256(m.SOURCES[subject].encode()).hexdigest()+'.body')
    if not path.exists():pytest.skip('Ignored actual source cache unavailable')
    return path.read_text()


def test_manifest_individual_taxonomy_and_context():
    c=m.SPEC['courses']
    assert len(c)==29 and sum(len(e['targets']) for e in c.values())==29
    assert Counter(e['category'] for e in c.values())=={'applications':21,'other':3,'human_context':3,'foundations':2}
    assert c['ARTF 1000']['review']['status']=='unclassified'
    assert c['ARTG 1290']['review']['status']==c['ARTG 5150']['review']['status']=='mixed'
    assert c['ARTG 5330']['category']==c['ARTG 2401']['category']=='foundations'
    assert c['ARTG 5150']['credits']==3
    assert c['ARTG 1002']['credits']==2
    assert 'limited design-domain' in c['ARTG 3400']['review']['rationale']
    assert c['ARTG 5100']['conditions'][0]['kind']=='additional_prerequisite'


def test_actual_blocks_permissions_repeats_and_studio_identity():
    courses={}
    for subject in m.SOURCES:
        out=m.parse_subject(source(subject),program_id=PID,subject=subject)
        courses.update({c['code']:c for c in out['courses']})
        assert all('category_review' not in c for c in out['courses'])
        assert out['requirements']==[]
    assert len(courses)==29
    assert 'graduate standing or permission' in courses['ARTG 5100']['prerequisites']
    assert 'only be taken in conjunction' in courses['ARTG 5151']['prerequisites']
    assert 'may be taken concurrently' in courses['ARTG 4550']['prerequisites']
    assert courses['ARTG 1270']['id']!=courses['ARTG 1271']['id']
    assert courses['ARTG 1290']['id']!=courses['ARTG 1291']['id']
    html=source('ARTG')
    for bad in [html.replace('May be repeated twice.','May be repeated three times.'),html.replace('2026-2027','2025-2026')]:
        with pytest.raises(ValueError):m.parse_subject(bad,program_id=PID,subject='ARTG')
    soup=BeautifulSoup(html,'html.parser')
    for b in soup.select('.courseblock'):
        if clean(b.select_one('.courseblocktitle')).startswith('ARTG 1001.'):
            b.decompose()
    with pytest.raises(ValueError):m.parse_subject(str(soup),program_id=PID,subject='ARTG',codes=['ARTG 1002'])


def test_context_only_mapping_preserves_manual_roles():
    path=Path('.cache/research/degree-audit-northeastern')/(PID+'.html')
    if not path.exists():pytest.skip('Ignored actual degree cache unavailable')
    html=path.read_text()
    seed=json.loads(Path('data/programs',PID+'.json').read_text())
    family=json.loads(Path('data/families/northeastern-ai-combined-degrees.json').read_text())
    p=resolve_program(seed,family)
    if not any(c['code']=='ARTG 5100' for c in p['courses']):
        before=requirement_profile(p)
        p=m.attach_contextual_courses(p,html)
        after=requirement_profile(p)
        assert before['required']['count']==after['required']['count']
        assert before['options']['count']==after['options']['count']
        assert after['unresolved']['count']==before['unresolved']['count']+3
    for c in p['courses']:
        if c['code'] in m.SPEC['courses']:c['category']=m.SPEC['courses'][c['code']]['category']
    lookup={c['id']:c for c in p['courses']};result=requirement_profile(p)
    for role,ids in m.SPEC['degree_review']['expected_course_ids'].items():
        for cid in ids:assert requirement_profile({**p,'courses':[lookup[cid]]})[role]['count']==1
        expected=m.SPEC['degree_review']['expected_profile'][role]
        assert result[role]['count']==expected['count']
        assert {k:v for k,v in result[role]['categories'].items() if v}==expected['categories']
    assert result['required']['count']==23 and result['options']['count']==41
    assert result['unresolved']['count']==3
    with pytest.raises(ValueError):m.attach_contextual_courses(copy.deepcopy(p),html.replace('130 total semester hours','134 total semester hours'))
    assert any(r['kind']=='note' and PID+'-artg-5100' in r['course_ids'] for r in p['requirements'])
