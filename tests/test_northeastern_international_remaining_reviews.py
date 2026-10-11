import copy
import hashlib
import json
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from atlas.adapters import northeastern_international_remaining_reviews as m
from atlas.adapters.northeastern_courseleaf import clean

PID='northeastern-university-artificial-intelligence-and-international-affairs-bs-boston-bs-degree'


def test_scope_and_source_backed_identity_are_manual():
    entries=m.SPEC['courses']
    assert len(entries)==35
    assert sum(len(c['targets']) for c in entries.values())==35
    assert sum(c['category']=='human_context' for c in entries.values())==32
    assert {code for code,c in entries.items() if c['review']['status']=='mixed'}=={'AFCS 1270','PHTH 1270','AFCS 4939'}
    assert sum(c['prerequisites'] is None for c in entries.values())==28
    seed=json.loads(Path('data/programs',PID+'.json').read_text())
    group,=m.SPEC['manual_identity_groups']
    assert set(group['course_ids'])<={c['id'] for c in seed['courses']}
    assert set(group['source_ids'])<={s['id'] for s in seed['sources']}
    assert all('afcs-' not in cid for cid in group['course_ids'])
    assert len(m.SPEC['identity_evidence'])==1
    for code in ['AFCS 3900','PHTH 1270']:
        assert any(c['kind']=='identity_uncertainty' for c in entries[code]['conditions'])


def test_whole_block_and_version_guards_preserve_language_conditions(monkeypatch):
    block='<div class="courseblock"><p class="courseblocktitle">SPNS 3240. Synthetic film. (4 Hours)</p><p class="cb_desc">Critical analysis of films. Conducted in Spanish.</p><p class="courseblockextra">Prerequisite(s): Placement in SPNS 3101 with a score of 3101</p></div>'
    spec=copy.deepcopy(m.SPEC['courses']['SPNS 3240'])
    spec['block_digest']=hashlib.sha256(clean(BeautifulSoup(block,'html.parser')).encode()).hexdigest()
    spec['description_guard']='Critical analysis of films.'
    monkeypatch.setitem(m.SPEC['courses'],'SPNS 3240',spec)
    def page(b,year='2026-2027'):
        return '<p>'+year+' Edition</p><div id="site-title"><h1>'+m.SPEC['sources']['SPNS']['heading']+'</h1></div><div id="textcontainer">'+b+'</div>'
    out=m.parse_subject(page(block),program_id=PID,subject='SPNS',codes=['SPNS 3240'])
    assert len(out['courses'])==1 and out['courses'][0]['credits']==4
    assert out['courses'][0]['prerequisites'].endswith('score of 3101')
    assert any('Conducted in Spanish.' in n for n in out['notes'])
    assert 'category_review' not in out['courses'][0]
    assert out['requirements']==[] and 'course_identity_groups' not in out
    for bad in [block.replace('3101','3102'),block.replace('4 Hours','3 Hours'),block.replace('films.','paintings.'),block+block,'']:
        with pytest.raises(ValueError):m.parse_subject(page(bad),program_id=PID,subject='SPNS',codes=['SPNS 3240'])
    with pytest.raises(ValueError):m.parse_subject(page(block,'2025-2026'),program_id=PID,subject='SPNS',codes=['SPNS 3240'])
    with pytest.raises(ValueError):m.parse_subject(page(block),program_id=PID,subject='SPNS',codes=['SPNS 3240','SPNS 3240'])


def actual(url):
    path=Path('.cache/http')/(hashlib.sha256(url.encode()).hexdigest()+'.body')
    if not path.exists():pytest.skip('Ignored actual source cache unavailable')
    return path.read_text()


def test_actual_source_observations_and_exact_reciprocal_identity():
    courses={};notes=[]
    for subject,url in m.SOURCES.items():
        out=m.parse_subject(actual(url),program_id=PID,subject=subject)
        courses.update({c['code']:c for c in out['courses']});notes+=out['notes']
    assert len(courses)==35 and all(c['credits']==4 and c['credit_unit']=='semester_hours' for c in courses.values())
    assert 'score of 3101' in courses['SPNS 3240']['prerequisites']
    assert 'minimum grade of C-' in courses['SPNS 3240']['prerequisites']
    assert 'minimum grade of D-' in courses['SPNS 3715']['prerequisites']
    assert courses['PHIL 1285']['prerequisites'] is None
    assert any('No prior knowledge of Judaism' in n for n in notes)
    assert any('AFRS 1270 and PHTH 1270' in n for n in notes)
    assert courses['CRIM 5203']['category']=='human_context'
    assert courses['INNO 3308']['category']=='human_context'
    evidence,=m.SPEC['identity_evidence']
    for code,url,digest in zip(evidence['codes'],evidence['source_urls'],evidence['block_digests']):
        soup=BeautifulSoup(actual(url),'html.parser')
        block=next(b for b in soup.select('#textcontainer .courseblock') if clean(b.select_one('.courseblocktitle')).startswith(code+'.'))
        assert hashlib.sha256(clean(block).encode()).hexdigest()==digest
        assert 'ASNS 1150 and HIST 1150 are cross-listed.' in clean(block)
