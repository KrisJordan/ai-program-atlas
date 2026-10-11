import json
from pathlib import Path
import pytest
from atlas.adapters import ucsd_sixth_pools as p
from atlas.db import validate_program


def table(rows):
    return '<table>'+''.join('<tr>'+''.join('<td>'+x+'</td>'for x in row)+'</tr>'for row in rows)+'</table>'


def test_pdf_category_units_and_ranges_not_invented_courses():
    value='2026-2027 Academic Year\nUpdated August 12, 2026\ntwo different academic departments\nR versions of courses\n'
    for title,_,count,units in p.SECTIONS:value+=title+' ('+str(units)+' units)\nSynthetic Department: TEST-001, 002—005\n'
    value+='Upper Division Requirements'
    r=p.parse_pdf_text(value);assert {c['code']for c in r['courses']}=={'TEST 1'}
    art=next(n for n in r['requirements']if n['title']=='Art Making')
    assert art['kind']=='choose_credits'and art['credits']==8 and art['count']is None
    assert all(c['credits']is None for c in r['courses'])
    assert 'curriculum_audit'not in r
    with pytest.raises(ValueError):p.parse_pdf_text(value.replace('Updated August 12, 2026','Undated'))


def test_elr_table_retains_open_families_pairs_and_prerequisites():
    html='<p>Experiential Learning Requirement Approved Course List; at least four units; beginning in Fall 2026; Enrollment Requirements</p>'+table([['Research and Design','ALL DEPARTMENTS','All 198 courses','Special studies','Application','Summer 2026'],['Community Engagement','Example','TEST-010 & TEST-011','Paired option','Permission',''],['Research and Design','Example','TEST-120','Synthetic practicum','Upper division','Fall 2026']])
    r=p.parse_elr_table(html);assert len(r['courses'])==1
    c=r['courses'][0];assert c['code']=='TEST 120'and c['prerequisites']=='Upper division'and c['credits']is None
    assert r['requirements'][1]['course_ids']==[]and 'Fall 2026'in r['requirements'][0]['summary']
    assert r['requirements'][2]['course_ids']==[]


def test_cat90_is_explicit_exception_not_four_unit_inference():
    html='<h1>CAT-090</h1><p>one-unit reflection seminar; eighty hours; at least five weeks; no earlier than July 1 and no later than October 1; end of Week 1; must not receive academic credit; regardless of whether you have lower- or upper-division standing; pass/no pass</p>'
    r=p.parse_cat90(html);assert r['courses'][0]['credits']==1
    assert '80 hours'in r['requirements'][0]['summary']and 'P/NP only'in r['requirements'][0]['summary']


def test_curated_sixth_scope_remains_honestly_partial():
    d=json.loads(Path('data/programs/'+p.PID+'.json').read_text());validate_program(d)
    rows=[n for n in d['requirements']if n['id'].startswith(p.PID+'-sixth-')]
    assert len(rows)==190
    assert sum('-sixth-elr-option-'in n['id']for n in rows)==97
    assert next(c for c in d['courses']if c['code']=='CAT 90')['credits']==1
    assert any('CAT 125GS'in n['summary']for n in rows)
    assert any('Friday of week eight in the quarter after return'in n['summary']for n in rows)
    assert d['curriculum_status']=='partial'
