import copy,hashlib
from collections import Counter
from pathlib import Path
import pytest
from bs4 import BeautifulSoup
from atlas.adapters import northeastern_public_health_course_reviews as m
from atlas.adapters.northeastern_courseleaf import clean
PID='northeastern-university-artificial-intelligence-and-public-health-bs-boston-bs-degree'

def synthetic(monkeypatch):
    block='<div class="courseblock"><p class="courseblocktitle">HLTH 5280. Synthetic disability inquiry. (3,4 Hours)</p><p class="cb_desc">Synthetic social rights inquiry.</p><p class="courseblockextra">Prerequisite(s): A or B with C-</p></div>'
    entry=copy.deepcopy(m.SPEC['courses']['HLTH 5280']);entry['block_digest']=hashlib.sha256(clean(BeautifulSoup(block,'html.parser')).encode()).hexdigest();entry['description_guard']='Synthetic social rights inquiry.';monkeypatch.setitem(m.SPEC['courses'],'HLTH 5280',entry)
    def page(b):return '<p>2026-2027 Edition</p><div id="site-title"><h1>'+m.SPEC['sources']['HLTH']['heading']+'</h1></div><div id="textcontainer">'+b+'</div>'
    return block,page

def test_variable_credits_and_changed_source_fail_closed(monkeypatch):
    block,page=synthetic(monkeypatch);r=m.parse_subject(page(block),program_id=PID,subject='HLTH',codes=['HLTH 5280']);c=r['courses'][0]
    assert c['credits'] is None and c['prerequisites']=='A or B with C-'
    assert r['requirements']==[] and 'category_review' not in c and 'curriculum_audit' not in r
    assert any('3 or 4' in n for n in r['notes'])
    for bad in [block.replace('3,4 Hours','4 Hours'),block.replace('C-','B-'),block+block,'']:
        with pytest.raises(ValueError):m.parse_subject(page(bad),program_id=PID,subject='HLTH',codes=['HLTH 5280'])
    with pytest.raises(ValueError):m.parse_subject(page(block).replace('2026-2027','2025-2026'),program_id=PID,subject='HLTH',codes=['HLTH 5280'])
    with pytest.raises(ValueError):m.parse_subject(page(block),program_id='unreviewed',subject='HLTH',codes=['HLTH 5280'])

def test_manual_subjects_and_eligibility_are_scoped():
    e=m.SPEC['courses'];assert len(e)==32 and sum(len(x['targets'])for x in e.values())==46
    assert e['AFCS 3424']['review']['candidate_categories']==['applications','human_context']
    assert e['PHTH 5232']['category']=='applications'
    assert e['PHTH 5234']['category']=='human_context'
    assert e['ORGB 3201']['category']=='applications'
    assert 'may be taken concurrently' in e['ORGB 3201']['prerequisites']
    assert 'instructor permission' in e['PHTH 5222']['conditions'][0]['summary']
    assert all(e[c]['conditions'][0]['kind']=='crosslist_observation' for c in ['INTL 5100','PPUA 5100'])

def test_composition_retains_unrelated_observations(monkeypatch):
    block,page=synthetic(monkeypatch);url=m.SOURCES['HLTH']
    previous=lambda html:{'id':PID,'courses':[{'id':'unrelated','name':'Preserved'}],'requirements':[{'id':'old-rule'}],'notes':['prior']}
    parsers=m.attach_reviewed_sources(PID,{url:previous});r=parsers[url](page(block))
    assert any(c['id']=='unrelated' for c in r['courses']) and r['requirements']==[{'id':'old-rule'}]
    assert 'prior' in r['notes']


def test_optional_complete_source_replay():
    cache=Path('.cache/research/degree-audit-northeastern')
    if not all((cache/(s.lower()+'.html')).exists() for s in m.SOURCES):pytest.skip('Optional ignored source captures absent')
    count=0
    for subject in m.SOURCES:
        for pid in {t['program_id'] for e in m.SPEC['courses'].values()if e['subject']==subject for t in e['targets']}:
            result=m.parse_subject((cache/(subject.lower()+'.html')).read_text(),program_id=pid,subject=subject)
            count+=len(result['courses']);assert all('category_review'not in c for c in result['courses'])
    assert count==46
