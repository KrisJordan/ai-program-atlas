import json
from pathlib import Path
import pytest
from atlas.adapters import ucsd_roosevelt_pools as p
from atlas.db import validate_program


def table(rows):
    return '<table>'+''.join('<tr>'+''.join('<td>'+x+'</td>'for x in row)+'</tr>'for row in rows)+'</table>'


def test_regions_preserve_markers_cohorts_and_blank_leading_cells():
    html='<h1>Regional Specialization</h1><h2>Multiculturalism in North America</h2><p>ALL courses from the SAME region; Only ONE course can be taken P/NP; MAY NOT OVERLAP WITH YOUR MAJOR; Last Updated: 8/2026; FOR STUDENTS WHO ENTERED FA21 AND AFTER</p>'+table([['','Course Number','Course Title'],['','!^TEST 11','Synthetic course'],['~TEST 120/120R','Synthetic variants']])
    r=p.parse_region(html,'north-america');assert {c['code']for c in r['courses']}=={'TEST 11'}
    assert '!^TEST 11'in r['requirements'][1]['summary']
    assert r['requirements'][2]['course_ids']==[]
    assert 'DEI approved list'in r['requirements'][0]['summary']
    assert 'curriculum_audit'not in r
    with pytest.raises(ValueError):p.parse_region(html.replace('FA21 AND AFTER','BEFORE FA21'),'north-america')


def test_writing_parser_retains_old_source_edition_and_qualification():
    html='<h1>Upper-Division Writing GE Requirement</h1><p>one upper-division course; Last Updated: 12/03/20; Open to transfer students only; MMW must be taken for a letter grade</p>'+table([['Course Number','Course Title'],['~ TEST 151','Synthetic seminar'],['MMW 122*','Transfer writing']])
    r=p.parse_writing(html)
    assert 'December 3, 2020'in r['requirements'][0]['summary']
    assert r['courses'][0]['code']=='TEST 151'
    assert r['requirements'][2]['course_ids']==[]


def test_curated_current_regions_and_conflicts_validate():
    d=json.loads(Path('data/programs/'+p.PID+'.json').read_text());validate_program(d)
    rows=[n for n in d['requirements']if n['id'].startswith(p.PID+'-roosevelt-')]
    assert len(rows)==1443
    assert sum(n['id'].startswith(p.PID+'-roosevelt-writing-option-')for n in rows)==215
    assert any('35 of final 45'in n['summary']and '36/44'in n['summary']for n in rows)
    assert any('MMW121 or122'in n['summary']for n in rows)
    assert not any('americas-multi-ethnic' in s['url']for s in d['sources'])
    assert d['curriculum_status']=='partial'
