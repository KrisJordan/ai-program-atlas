import hashlib,json
from pathlib import Path
import pytest
from bs4 import BeautifulSoup
from atlas.adapters import ucsd_seventh_pools as p
from atlas.db import validate_program


def test_pool_preserves_inline_code_spans_bundles_and_prerequisites():
    s=BeautifulSoup('<h2>Test pool</h2><div><p>TEST<span>-00</span>1 - Synthetic course<br>TEST-002A+002B - Synthetic sequence<br>*EDS-139 - Synthetic practicum<br>TEST-003 - Synthetic option (no prerequisites)</p></div>','html.parser')
    courses,rows=p.parse_pool(s,'Test pool','test',2)
    assert {c['code']for c in courses.values()}=={'TEST 1','EDS 139','TEST 3'}
    assert rows[2]['course_ids']==[]
    assert next(c for c in courses.values()if c['code']=='EDS 139')['prerequisites'].startswith('EDS 139 requires')
    assert len(rows)==5


def test_transfer_stays_conditional_and_does_not_require_optional_syn150():
    html='<h1>Degree Requirements for Transfer Students</h1><p>All transfer students must complete SYN 100 and High-Impact; Missing no more than two IGETC requirements; letter grade of C- or better; Winter Quarter of their first year; cannot be taken after SYN 100; Synthesis 100 (4 units)</p>'
    r=p.parse_transfer(html)
    assert r['courses'][0]['credits']==4
    assert any('not an added mandatory course'in n['summary']for n in r['requirements'])
    assert any('does not independently establish CalGETC'in n['summary']for n in r['requirements'])
    assert 'curriculum_audit'not in r
    with pytest.raises(ValueError):p.parse_transfer(html.replace('cannot be taken after SYN 100','unrestricted'))


def test_curated_seventh_inventory_validates():
    d=json.loads(Path('data/programs/'+p.PID+'.json').read_text());validate_program(d)
    rows=[n for n in d['requirements']if n['id'].startswith(p.PID+'-seventh-')]
    assert len(rows)==595
    assert sum('-high-impact-pool-row-'in n['id']for n in rows)==149
    assert sum('-alternatives-'in n['id']and'-row-'in n['id']for n in rows)==432
    assert any('open approved routes'in n['summary']for n in rows)
    assert d['curriculum_status']=='partial'
