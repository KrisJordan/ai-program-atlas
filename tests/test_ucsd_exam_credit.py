import json
from pathlib import Path
import pytest
from atlas.adapters import ucsd_exam_credit as p
from atlas.db import validate_program


def test_pdf_columns_preserve_college_mapping_and_do_not_infer_course_credits():
    rows=[dict(page=2,cells=['Synthetic exam—8','No exemption']+[c+' test rule'for c in p.COLLEGES])]
    r=p.parse_pdf_observation(rows,'ap')
    assert len(r['requirements'])==10
    assert all(n['credits']is None and not n['course_ids']for n in r['requirements'])
    assert 'Marshall test rule'in r['requirements'][3]['summary']
    assert 'Eighth test rule'in r['requirements'][8]['summary']
    assert 'curriculum_audit'not in r
    with pytest.raises(ValueError):p.parse_pdf_observation([dict(page=2,cells=rows[0]['cells'][:-1])],'ap')


def test_warren_multiple_headers_in_one_table_and_footnote():
    html='<h1>Advanced Placement and International Baccalaureate Credit</h1><p>2026-2027 Academic Year;4 units to each AS;IB credit limit at UC San Diego is 30 units;The IB Math AI HL is not UC transferable</p><h2>Advanced Placement Credit</h2><table><tr><th>First subject</th><th>Score</th><th>Units</th><th>Warren College GE Requirement</th></tr><tr><td></td><td>3</td><td>4</td><td>Synthetic rule</td></tr><tr><th>Second subject</th><th>Score</th><th>Units</th><th>Warren College GE Requirement</th></tr><tr><td>Test</td><td>5</td><td>8</td><td>Other synthetic rule</td></tr><tr><td colspan="4">Synthetic duplicate limit</td></tr></table>'
    r=p.parse_warren(html);assert len(r['requirements'])==4
    assert 'First subject'in r['requirements'][1]['title']
    assert 'Second subject'in r['requirements'][2]['title']
    assert 'Footnote'in r['requirements'][3]['title']


def test_curated_all_54_rows_eight_colleges_and_exact_conflicts():
    d=json.loads(Path('data/programs/'+p.PID+'.json').read_text());validate_program(d)
    rows=[n for n in d['requirements']if n['id'].startswith(p.PID+'-exam-')]
    assert len(rows)==584
    assert sum('Conditional 'in n['summary']for n in rows)==54*8
    assert any('Math' in n['summary']and 'discrepancy'in n['summary']for n in rows)
    assert d['curriculum_status']=='partial'
