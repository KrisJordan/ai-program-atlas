import copy
import hashlib
from collections import Counter
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from atlas.adapters import northeastern_business_marketing_reviews as m
from atlas.adapters.northeastern_courseleaf import clean

PID='northeastern-university-artificial-intelligence-and-business-administration-bs-boston-bs-degree'


def test_guarded_observation_keeps_review_separate(monkeypatch):
    block='<div class="courseblock"><p class="courseblocktitle">MKTG 2201. Synthetic marketing. (4 Hours)</p><p class="cb_desc">Synthetic marketing strategy.</p><p class="courseblockextra">Prerequisite(s): A or B (may be taken concurrently) with D-</p></div>'
    spec=copy.deepcopy(m.SPEC['courses']['MKTG 2201'])
    spec['block_digest']=hashlib.sha256(clean(BeautifulSoup(block,'html.parser')).encode()).hexdigest()
    spec['description_guard']='Synthetic marketing strategy.'
    monkeypatch.setitem(m.SPEC['courses'],'MKTG 2201',spec)
    def page(b):return '<p>2026-2027 Edition</p><div id="site-title"><h1>'+m.SPEC['sources']['MKTG']['heading']+'</h1></div><div id="textcontainer">'+b+'</div>'
    result=m.parse_subject(page(block),program_id=PID,subject='MKTG',codes=['MKTG 2201'])
    c=result['courses'][0]
    assert c['credits']==4 and c['credit_unit']=='semester_hours'
    assert 'may be taken concurrently' in c['prerequisites']
    assert 'category_review' not in c and 'curriculum_audit' not in result
    assert result['requirements']==[]
    for bad in [block.replace('4 Hours','3 Hours'),block.replace('D-','C-'),block.replace('strategy.','new material.'),block+block,'']:
        with pytest.raises(ValueError):m.parse_subject(page(bad),program_id=PID,subject='MKTG',codes=['MKTG 2201'])
    with pytest.raises(ValueError):m.parse_subject(page(block).replace('2026-2027','2025-2026'),program_id=PID,subject='MKTG',codes=['MKTG 2201'])
    with pytest.raises(ValueError):m.parse_subject(page(block),program_id='unreviewed',subject='MKTG',codes=['MKTG 2201'])


def test_manual_scope_and_substantive_distinctions():
    c=m.SPEC['courses']
    assert len(c)==51 and sum(len(e['targets']) for e in c.values())==52
    assert Counter(e['subject'] for e in c.values())=={'MKTG':25,'INNO':12,'ENTR':14}
    assert Counter(e['category'] for e in c.values())=={'applications':38,'other':7,'human_context':4,'foundations':1,'mathematics':1}
    assert c['MKTG 4604']['category']==c['INNO 3303']['category']=='applications'
    assert c['MKTG 2601']['category']=='foundations'
    assert c['MKTG 2602']['category']=='mathematics'
    assert c['ENTR 3304']['category']=='human_context'
    assert c['ENTR 2225']['category']=='human_context'
    assert {code for code,e in c.items() if e['review']['status']=='unclassified'}=={'MKTG 4120','MKTG 4983','INNO 4983','ENTR 4983'}
    assert c['ENTR 3217']['conditions'][0]['kind']=='required_field_component'
    assert c['MKTG 2601']['prerequisites'] is None
    assert c['MKTG 2601']['conditions'][0]['kind']=='preparation'


def test_optional_actual_all_blocks_and_composition():
    total=0
    for subject,url in m.SOURCES.items():
        path=Path('.cache/http')/(hashlib.sha256(url.encode()).hexdigest()+'.body')
        if not path.exists():pytest.skip('Ignored actual source cache unavailable')
        html=path.read_text()
        programs={t['program_id'] for e in m.SPEC['courses'].values() if e['subject']==subject for t in e['targets']}
        for pid in programs:
            result=m.parse_subject(html,program_id=pid,subject=subject)
            assert result==m.parse_subject(html,program_id=pid,subject=subject)
            assert all(c['credits']==4 for c in result['courses'])
            total+=len(result['courses'])
            sentry={'id':'independent-rule','kind':'note'}
            original=lambda _: {'id':pid,'courses':[{'id':'untouched-course'}],'requirements':[sentry],'notes':['Existing source note.']}
            composed=m.attach_reviewed_sources(pid,{url:original})[url](html)
            assert composed['requirements']==[sentry]
            assert {'id':'untouched-course'} in composed['courses']
            assert 'Existing source note.' in composed['notes']
            if subject=='ENTR':assert any('spring break international field project' in n for n in result['notes'])
            if subject=='MKTG':
                bycode={c['code']:c for c in result['courses']}
                assert 'CS 3250 (may be taken concurrently)' in bycode['MKTG 4605']['prerequisites']
                assert 'MKTG 3401 (may be taken concurrently)' in bycode['MKTG 4510']['prerequisites']
    assert total==52
