import json
from pathlib import Path
import pytest
from atlas.adapters import ucsd_warren_pools as p
from atlas.db import validate_program


def table(rows):
    return '<table>'+''.join('<tr>'+''.join('<td>'+x+'</td>'for x in row)+'</tr>'for row in rows)+'</table>'


def test_live_table_parser_preserves_split_blanks_and_annotated_codes():
    html=table([['Course Code','Course Title'],['Choose one of the following:','',''],['TEST','010','Introductory example'],['Choose two of the following:','',''],['TEST','120',''],['TEST','121***','Qualified example'],['TEST/OTHER','122','Cross-listed example']])
    r=p.parse_table(html,'law');assert {c['code']for c in r['courses']}=={'TEST 10','TEST 120'}
    assert next(c for c in r['courses']if c['code']=='TEST 120')['name']is None
    choices=[n['count']for n in r['requirements']if n['kind']=='choose_courses'];assert choices==[3,1,2]
    assert any('121***'in n['summary']and not n['course_ids']for n in r['requirements'])
    assert 'curriculum_audit'not in r and 'last_verified'not in r
    with pytest.raises(ValueError):p.parse_table(html.replace('Choose two','Select two'),'law')


def test_formal_merged_alternatives_are_not_misread_as_single_code():
    r=p.parse_table(table([['Course Code','Course Title'],['TEST-010 or TEST-011','Synthetic alternative'],['TEST','012','Single course']]),'formal')
    assert len(r['courses'])==1 and r['courses'][0]['code']=='TEST 12'
    assert r['requirements'][0]['count']==2
    assert r['requirements'][1]['course_ids']==[]


def test_warren_curated_applicability_and_table_inventory():
    d=json.loads(Path('data/programs/'+p.PID+'.json').read_text());validate_program(d)
    rows=[n for n in d['requirements']if n['id'].startswith(p.PID+'-warren-') and not n['id'].startswith(p.PID+'-warren-discipline-') and not n['id'].startswith(p.PID+'-warren-language-')]
    assert len(rows)==319
    assert next(n for n in rows if n['id'].endswith('ai-scope'))['summary'].startswith('The published B.S. Engineering list explicitly includes CSE Artificial Intelligence')
    counts={key:sum(n['id'].startswith(p.PID+'-warren-option-'+key+'-')for n in rows)for key in p.TABLES}
    assert counts=={'formal':36,'anti-racism-humanities':28,'anti-racism-social':79,'environment':52,'law':61}
    assert any('ETHN 153***'in n['summary']for n in rows)
    assert any('one four-unit upper-division course'in n['summary']for n in rows)
    assert d['curriculum_status']=='partial'
