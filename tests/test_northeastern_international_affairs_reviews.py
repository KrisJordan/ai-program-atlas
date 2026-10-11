import copy
import hashlib
from collections import Counter
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from atlas.adapters import northeastern_international_affairs_reviews as m
from atlas.adapters.northeastern_courseleaf import clean

PID='northeastern-university-artificial-intelligence-and-international-affairs-bs-boston-bs-degree'


def test_manual_scope_and_non_keyword_categories():
    c=m.SPEC['courses']
    assert len(c)==24 and sum(len(e['targets']) for e in c.values())==24
    assert Counter(e['subject'] for e in c.values())=={'INTL':23,'PPUA':1}
    assert Counter(e['category'] for e in c.values())=={'human_context':23,'other':1}
    assert c['INTL 1000']['review']['status']=='unclassified'
    assert c['INTL 2600']['category']=='human_context'
    assert c['INTL 3450']['category']=='human_context'
    assert c['INTL 2718']['category']=='human_context'
    assert c['INTL 1000']['credits']==1
    assert sum(bool(e['conditions']) for e in c.values())==3
    assert 'INTL 1101' not in c


def test_changed_prerequisite_or_description_requires_review(monkeypatch):
    block='<div class="courseblock"><p class="courseblocktitle">INTL 2600. Synthetic policy. (4 Hours)</p><p class="cb_desc">Synthetic international policy.</p><p class="courseblockextra">Prerequisite(s): A and B (may be taken concurrently) with C</p></div>'
    spec=copy.deepcopy(m.SPEC['courses']['INTL 2600'])
    spec['block_digest']=hashlib.sha256(clean(BeautifulSoup(block,'html.parser')).encode()).hexdigest()
    spec['description_guard']='Synthetic international policy.'
    monkeypatch.setitem(m.SPEC['courses'],'INTL 2600',spec)
    def page(b):return '<p>2026-2027 Edition</p><div id="site-title"><h1>'+m.SPEC['sources']['INTL']['heading']+'</h1></div><div id="textcontainer">'+b+'</div>'
    out=m.parse_subject(page(block),program_id=PID,subject='INTL',codes=['INTL 2600'])
    assert 'may be taken concurrently' in out['courses'][0]['prerequisites']
    assert 'category_review' not in out['courses'][0]
    assert 'course_identity_groups' not in out
    assert out['requirements']==[]
    for bad in [block.replace('with C','with B'),block.replace('international policy.','new instruction.'),block.replace('4 Hours','3 Hours'),block+block,'']:
        with pytest.raises(ValueError):m.parse_subject(page(bad),program_id=PID,subject='INTL',codes=['INTL 2600'])
    with pytest.raises(ValueError):m.parse_subject(page(block).replace('2026-2027','2025-2026'),program_id=PID,subject='INTL',codes=['INTL 2600'])


def test_optional_actual_blocks_and_crosslist_observations():
    courses={};notes=[]
    for subject,url in m.SOURCES.items():
        path=Path('.cache/http')/(hashlib.sha256(url.encode()).hexdigest()+'.body')
        if not path.exists():pytest.skip('Ignored actual source cache unavailable')
        html=path.read_text();out=m.parse_subject(html,program_id=PID,subject=subject)
        assert out==m.parse_subject(html,program_id=PID,subject=subject)
        courses.update({c['code']:c for c in out['courses']});notes+=out['notes']
    assert len(courses)==24
    assert len(notes)==3 and all('crosslist_observation' in n for n in notes)
    assert 'WMNS 2480' in next(n for n in notes if n.startswith('INTL 2480'))
    assert 'JRNL 3300' in next(n for n in notes if n.startswith('INTL 3300'))
    assert 'ANTH 4500' in next(n for n in notes if n.startswith('INTL 4500'))
    assert 'may be taken concurrently' in courses['INTL 3470']['prerequisites']
    assert courses['INTL 3450']['prerequisites'].count(';')==2
    assert courses['PPUA 5267']['prerequisites'] is None
