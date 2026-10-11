import json
from pathlib import Path
import pytest
from atlas.adapters import ucsd_muir_pools as p
from atlas.db import validate_program


def fixture():
    return '<h1>Approved Muir College General Education Courses</h1><p>two different areas; 3 courses in a single language; placement exam or proficiency exam; such exceptions are not guaranteed; duplicates credits; grade of D or higher</p><h2>Muir College Writing Program</h2><ol><li>MCWP-040 or MCWP-040R</li><li>MCWP-050</li></ol><h2>Math or Natural Sciences</h2><h3>Synthetic Theme</h3><p>TEST-010, TEST-011 and -011L, COGS-0-2, TEST-014 (only if taken for 4 units)</p><h2>Social Sciences</h2><h2>Fine Arts</h2><h2>Humanities</h2><h2>Language Other Than English</h2>'


def test_actual_paragraphs_drive_inventory_and_conditions():
    r=p.parse(fixture());assert {c['code']for c in r['courses']}=={'TEST 10','MCWP 40','MCWP 40R','MCWP 50'}
    assert any('TEST-011 and -011L'in n['summary']and n['course_ids']==[]for n in r['requirements'])
    assert any('COGS-0-2'in n['summary']and n['course_ids']==[]for n in r['requirements'])
    assert any('only if taken for 4 units'in n['summary']for n in r['requirements'])
    changed=p.parse(fixture().replace('TEST-010','TEST-090'));assert 'TEST 90'in {c['code']for c in changed['courses']}
    assert 'last_verified'not in r and 'curriculum_audit'not in r
    with pytest.raises(ValueError):p.parse(fixture().replace('Social Sciences','Changed Area'))


def test_current_muir_option_inventory_validates():
    d=json.loads(Path('data/programs/'+p.PID+'.json').read_text());validate_program(d)
    rows=[r for r in d['requirements']if r['id'].startswith(p.PID+'-muir-')]
    assert len(rows)==676
    assert sum(r['kind']=='choose_courses'and r['count']==3 for r in rows)==33
    assert any('COGS-0-2'in r['summary']for r in rows)
    assert any('MCWP 125 or 125R'in r['summary']for r in rows)
    assert d['curriculum_status']=='partial'
