import json
from pathlib import Path
import pytest
from atlas.adapters import ucsd_warren_languages as p
from atlas.db import validate_program


def test_chinese_reads_credits_and_prereqs_but_excludes_graduate_only_entries():
    html='<h2>Chinese Language Acquisition Courses</h2><p>placement interview; N track; M and D tracks converge</p><p class="course-name">CHIN 10AN. Synthetic language (5)</p><p class="course-descriptions">Synthetic description. Prerequisites: Placement approval.</p><p class="course-name">CHIN 160/260. Synthetic cross-list (4)</p><p class="course-descriptions">Prerequisites: Permission.</p><p class="course-name">CHIN 260. Graduate-only (4)</p><p class="course-descriptions">Graduate description.</p>'
    r=p.parse_chinese(html);assert [c['code']for c in r['courses']]==['CHIN 10AN']
    assert r['courses'][0]['credits']==5
    assert r['courses'][0]['prerequisites']=='Placement approval.'
    assert r['requirements'][1]['course_ids']==[]
    assert len(r['requirements'])==3
    assert 'curriculum_audit'not in r


def test_current_chicanx_schedule_does_not_merge_historical_terms_or_waive_petitions():
    html='<h1>Course Offerings</h1><p>schedule is tentative and subject to change; Courses with * need a petition form</p>'
    for t in ['Fall 2026','Winter 2027','Spring 2027']:
        html+='<h2>'+t+' Elective Courses</h2><div><p>*TEST-001. Synthetic option</p></div>'
    html+='<h1>Past Course Offerings</h1><p>TEST-999. Old course</p>'
    r=p.parse_chicanx(html);assert [c['code']for c in r['courses']]==['TEST 1']
    assert len(r['requirements'])==4
    assert all('not automatically approved'in n['summary']for n in r['requirements'][:3])
    with pytest.raises(ValueError):p.parse_chicanx(html.replace('Spring 2027','Spring 2026'))


def test_curated_languages_and_current_terms_validate():
    d=json.loads(Path('data/programs/'+p.PID+'.json').read_text());validate_program(d)
    rows=[n for n in d['requirements']if n['id'].startswith(p.PID+'-warren-language-')]
    assert len(rows)==116
    assert sum('-chicanx-'in n['id']and not n['id'].endswith('policy')for n in rows)==65
    assert not any(c['source_id']==p.PID+'-warren-language-chinese'and c['code']in ['CHIN 260','CHIN 296','CHIN 299','CHIN 500']for c in d['courses'])
    assert d['curriculum_status']=='partial'
