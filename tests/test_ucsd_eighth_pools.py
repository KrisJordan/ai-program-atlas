import json
from pathlib import Path
import pytest
from atlas.adapters import ucsd_eighth_pools as p
from atlas.db import validate_program


def fixture():
    rows=[['ART','Arts','TEST','001','R','Synthetic remote option','DEI','',''],['HUM','Language','LANG','100-199','','','','',''],['NAT SCI','Physics','PHYS','001A+001AL','','Synthetic pair','','JTCCER',''],['QM/ENG','Math','MATH','020','A','Synthetic math','','',''],['SOC SCI','Society','TEST','200','','Synthetic social','','','AHI']]
    return '<h1>Eighth College General Education Breadth Requirements</h1><p>Breadth Req. Area; Course Title; JTCCER</p><table>'+''.join('<tr>'+''.join('<td>'+x+'</td>'for x in r)+'</tr>'for r in rows)+'</table>'


def test_breadth_preserves_pairs_ranges_suffixes_and_overlap_annotations():
    r=p.parse_table(fixture());assert {c['code']for c in r['courses']}=={'TEST 1R','MATH 20A','TEST 200'}
    assert len(r['requirements'])==10
    assert all(n['count']==2 for n in r['requirements'][:5])
    assert 'JTCCER'in r['requirements'][7]['summary']
    assert r['requirements'][7]['course_ids']==[]
    assert 'curriculum_audit'not in r
    with pytest.raises(ValueError):p.parse_table(fixture().replace('QM/ENG','UNKNOWN'))


def test_transfer_observation_requires_actual_branch_evidence():
    html='<h1>Degree Requirements for Transfer Students</h1><p>CCE-110 (4 units); CCE-120 (4 units); Two Additional College Level Writing Courses; Starting in Fall 2026; six quarters; Official Letter of Reciprocity</p>'
    r=p.parse_transfer(html);assert len(r['courses'])==2
    assert all(c['credits']==4 for c in r['courses'])
    assert any('two additional college-level writing' in n['summary']for n in r['requirements'])
    with pytest.raises(ValueError):p.parse_transfer(html.replace('Starting in Fall 2026','2025'))


def test_curated_eighth_scope_validates_and_retains_open_routes():
    d=json.loads(Path('data/programs/'+p.PID+'.json').read_text());validate_program(d)
    rows=[n for n in d['requirements']if n['id'].startswith(p.PID+'-eighth-')]
    assert len(rows)==660
    assert sum(n['id'].startswith(p.PID+'-eighth-table-row-')for n in rows)==646
    assert any('open petition route'in n['summary']for n in rows)
    assert d['curriculum_status']=='partial'
