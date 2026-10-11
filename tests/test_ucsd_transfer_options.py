import json
from pathlib import Path
import pytest
from atlas.adapters import ucsd_transfer_options as p
from atlas.db import validate_program


def test_external_course_table_does_not_invent_ucsd_courses():
    html='<h1>Humanities Transfer Course Policy</h1><p>All freshmen entering Revelle Fall 2017 and after; three approved quarter courses, two approved semester courses; All institutions are on the semester system except for De Anza and Foothill; Credit is allowed for only one of HUM 200 and HUM 204</p>'
    html+='<table><tr><th>Institution</th><th>Course</th><th>Course Title</th></tr><tr><td>Test College</td><td>TEST 1</td><td>Synthetic humanities</td></tr></table>'*2
    r=p.parse_humanities(html);assert len(r['requirements'])==5
    assert not r.get('courses')
    assert all(n['course_ids']==[]for n in r['requirements'])
    assert 'external-institution option'in r['requirements'][-1]['summary']
    with pytest.raises(ValueError):p.parse_humanities(html.replace('only one of HUM 200 and HUM 204','both'))


def test_seed_has_all_24_external_options_and_service_bundles():
    d=json.loads(Path('data/programs/'+p.PID+'.json').read_text());validate_program(d)
    rows=[n for n in d['requirements']if n['id'].startswith(p.PID+'-transfer-options-')]
    assert len(rows)==34
    assert sum('external-institution option'in n['summary']for n in rows)==24
    assert any('two-course wording differs'in n['summary']for n in rows)
    assert any('six-unit standalone'in n['summary']for n in rows)
    assert d['curriculum_status']=='partial'
