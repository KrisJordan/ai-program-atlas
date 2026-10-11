import json
from pathlib import Path
import pytest
from atlas.adapters import ucsd_shared_requirements as p
from atlas.db import validate_program


def test_pdf_observations_retain_dates_composites_and_unknown_units():
    rows=[{'page':1,'cells':['Example','TEST 10','Synthetic climate course','','Fall 2030']},
          {'page':2,'cells':['','TEST 11/12','Synthetic paired option','Permission','Winter 2020 (through Fall 2021)']}]
    r=p.parse_approval_rows(rows,'climate')
    assert len(r['courses'])==1 and r['courses'][0]['credits']is None
    assert r['requirements'][0]['credits']is None
    assert 'Fall 2030' in r['requirements'][1]['summary']
    assert 'through Fall 2021' in r['requirements'][2]['summary']
    assert r['requirements'][2]['course_ids']==[]
    changed=p.parse_approval_rows([{'page':1,'cells':['','TEST 13','Changed title','None','Fall 2026']}],'dei')
    assert changed['courses'][0]['code']=='TEST 13'
    assert changed['requirements'][0]['credits']==4 and changed['courses'][0]['credits']is None
    assert 'curriculum_audit'not in r
    with pytest.raises(ValueError):p.parse_approval_rows([{'page':1,'cells':['','TEST 13','Title','','']}],'dei')


def test_ahi_named_ranges_and_open_department_rule():
    html='<h1>Undergraduate Degree Requirements</h1><p>Any of the following courses are suitable for fulfilling the requirement: HILD 2A-B-C, HILD 7A-B-C, or any course listed under HIUS (other than HIUS colloquia); POLI 110EA-EB; and USP 103. By presenting proof of prior study.</p>'
    r=p.parse_ahi(html)
    assert {c['code']for c in r['courses']}=={'HILD 2A','HILD 2B','HILD 2C','HILD 7A','HILD 7B','HILD 7C','POLI 110EA','POLI 110EB','USP 103'}
    assert all(c['name']is None for c in r['courses'])
    assert 'other than a colloquium' in r['requirements'][0]['summary']


def test_curated_rows_preserve_historical_future_and_malformed_evidence():
    d=json.loads(Path('data/programs/'+p.PID+'.json').read_text());validate_program(d)
    dei=[r for r in d['requirements']if '-shared-dei-option-'in r['id']]
    climate=[r for r in d['requirements']if '-shared-climate-option-'in r['id']]
    assert len(dei)==229 and len(climate)==58
    assert any('Fall 2027' in r['summary']for r in dei)
    assert any('through Spring 2023' in r['summary']for r in dei)
    assert any('USP/ANTH 128A, USP/ANTH 128' in r['summary']and not r['course_ids']for r in climate)
    assert d['curriculum_status']=='partial'
    assert next(c for c in d['courses']if c['code']=='MGT 18GS')['prerequisites'].endswith('Global Seminars Program.')
