import json
from pathlib import Path
import pytest
from atlas.adapters import ucsd_warren_disciplines as p
from atlas.db import validate_program


def test_chinese_list_boundary_bundles_and_inline_spans():
    html='<p>TEST 90. Outside approved block</p><h2>Courses Applicable for the Chinese Studies Major and/or Minor Offered by Various Departments and Programs</h2><p>TEST 1. <span>Synthetic course</span><br>TEST 2A-B. Synthetic bundle</p>'
    r=p.parse(html,'chinese');assert {c['code']for c in r['courses']}=={'TEST 1'}
    assert len(r['requirements'])==3
    assert r['requirements'][-1]['course_ids']==[]
    with pytest.raises(ValueError):p.parse(html.replace('Courses Applicable','Different'),'chinese')


def test_japanese_uses_names_without_copying_descriptions_or_graduate_pool():
    html='<h1>Non Language Courses</h1><p>more than 33% of the course content concerns Japan</p><h2>History</h2><table><tr><th>Course Name</th><th>Description</th></tr><tr><td>TEST 101 Synthetic title</td><td>Long synthetic prose must not be copied.</td></tr><tr><td>*TEST 102 Restricted topic</td><td>Other prose.</td></tr></table><h2>Graduate School of International Relations and Pacific Studies</h2><table><tr><td>GRAD 400 Graduate title</td><td>Graduate course.</td></tr></table>'
    r=p.parse(html,'japanese');assert {c['code']for c in r['courses']}=={'TEST 101'}
    assert 'Long synthetic prose'not in json.dumps(r)
    assert 'GRAD 400'not in json.dumps(r)
    assert any('more than33%'in n['summary']for n in r['requirements'])
    assert 'curriculum_audit'not in r


def test_latin_pool_does_not_impose_methods_course_requirement():
    html='<h3>Courses that Satisfy Undergraduate Degree Elective Requirements in Latin American Studies</h3><p>TEST 101. Topic (when Latin American content)</p><h3>Methods Courses</h3><p>TEST 199. Other degree method</p>'
    r=p.parse(html,'latin-american');assert {c['code']for c in r['courses']}=={'TEST 101'}
    assert all(n['kind']=='note'for n in r['requirements'])


def test_curated_discipline_inventory_validates():
    d=json.loads(Path('data/programs/'+p.PID+'.json').read_text());validate_program(d)
    rows=[n for n in d['requirements']if n['id'].startswith(p.PID+'-warren-discipline-')]
    assert len(rows)==553
    assert d['curriculum_status']=='partial'
