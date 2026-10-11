import json
from pathlib import Path
import pytest
from atlas.adapters import ucsd_marshall_pools as p
from atlas.db import validate_program


def test_actual_department_lists_not_navigation_drive_options():
    html='<h2>General Education Requirements for First-Year Students</h2><p>Option A: Option B: Option C: two different academic disciplines; four 4-unit; no exceptions; before enrolling in DOC 2 and DOC 3</p><h3>DOC-001: Synthetic writing (4 units) Fall Quarter only</h3><div class="panel"><h3>Biology</h3><ul><li>TEST-001, 002, or 004</li><li>PHYS-001A & 001AL</li></ul></div><div class="panel"><h3>Mathematics, Advanced Statistics</h3><ul><li>MATH-180A</li></ul></div><nav>TEST-999</nav>'
    r=p.parse_first(html)
    assert {c['code']for c in r['courses']}=={'DOC 1','TEST 1','TEST 2','TEST 4','MATH 180A'}
    assert next(n for n in r['requirements']if n['title']=='Mathematics, Advanced Statistics approved pool')['count']is None
    assert any('001A & 001AL'in n['summary']and not n['course_ids']for n in r['requirements'])
    assert 'curriculum_audit'not in r


def test_selector_requires_actual_selected_ai_and_reads_observed_groups():
    groups={key:['Synthetic eligible subject']for key in ['Humanities/Fine Arts','Social Sciences','Interdepartmental / Interdisciplinary','Foreign Languages']}
    r=p.parse_breadth_observation('CS29 - Artificial Intelligence','Engineering or Science',groups)
    assert len(r['requirements'])==5 and 'Synthetic eligible subject'in r['requirements'][1]['summary']
    with pytest.raises(ValueError):p.parse_breadth_observation('Select your major','Engineering or Science',groups)
    with pytest.raises(ValueError):p.parse_breadth_observation('CS29 - Artificial Intelligence','Unknown',groups)


def test_curated_marshall_pools_and_current_transfer_rule():
    d=json.loads(Path('data/programs/'+p.PID+'.json').read_text());validate_program(d)
    rows=[r for r in d['requirements']if r['id'].startswith(p.PID+'-marshall-')]
    assert len(rows)==188
    assert any('Winter 2027'in r['summary']and r['course_ids']==['ucsd-doc-170']for r in rows)
    assert any('ALL UPPER-DIVISION COURSES EXCEPT'in r['summary']for r in rows)
    assert any('129A -129C & 139'in r['summary']for r in rows)
    assert d['curriculum_status']=='partial'
