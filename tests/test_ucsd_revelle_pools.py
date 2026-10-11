import json
from pathlib import Path
import pytest
from atlas.adapters import ucsd_revelle_pools as p
from atlas.db import validate_program


def table(rows):
    return '<table>'+''.join('<tr>'+''.join('<td>'+x+'</td>'for x in row)+'</tr>'for row in rows)+'</table>'


def test_science_parses_rows_and_keeps_bundle_uncertainty():
    html='<main><h1>Natural Science Requirement</h1><p>Five courses to include; Fall 2026 and after; Three courses to include; different disciplines; labs are not required; Course and lab must be taken concurrently</p>'
    html+=''.join(table([['Course No.','Course Title'],[code,name]])for code,name in [('BILD-099','Synthetic biology'),('CHEM-098','Synthetic chemistry'),('PHYS-001A PHYS-001AL','Synthetic paired lecture and lab'),('SIO-099','Synthetic oceanography'),('PHIL-098','Synthetic reasoning'),('ASTR-099','Synthetic astronomy')])+'</main>'
    r=p.parse_science(html)
    assert {c['code']for c in r['courses']}=={'BILD 99','CHEM 98','SIO 99','PHIL 98','ASTR 99'}
    bundle=next(n for n in r['requirements']if n['title']=='PHYS-001A PHYS-001AL option')
    assert bundle['course_ids']==[] and 'compound' in bundle['summary']
    assert all(c['credits']is None for c in r['courses'])
    assert 'curriculum_audit'not in r and 'last_verified'not in r
    with pytest.raises(ValueError):p.parse_science(html.replace('Three courses','Four courses'))


def test_math_excludes_legacy_alias_and_preserves_alternative_rows():
    html='<h1>Mathematics Requirements</h1><p>one course in calculus and two additional; Only one of MATH-011, PSYC-060, or AP Statistics; Effective Fall 2024; Letter Grade; AP Calculus (AB or BC) scores of 2 or higher; grade C- or better</p><p>Calculus course:</p><ul><li>MATH-010A or MATH-020A</li></ul><p>Approved list of mathematics courses:</p><ul><li>MATH-018 (formerly MATH-020F); or MATH-031AH</li><li>AP Statistics (Score 3 or higher)</li></ul>'
    r=p.parse_math(html)
    assert {c['code']for c in r['courses']}=={'MATH 10A','MATH 20A','MATH 18','MATH 31AH'}
    assert next(n for n in r['requirements']if n['title']=='Revelle additional mathematics')['count']==2


def test_language_endpoint_column_not_beginner_column():
    html='<h1>Language Requirement</h1><p>at least one year of high school abroad; Pass/Not Pass</p>'+table([['Language','Beginner','Course Needed for First Year Students','Course Needed for Transfer Students'],['Synthetic','LANG-001A','LANG-001D/001DX','LANG-001B/001BX']])
    r=p.parse_language(html);n=r['requirements'][1]
    assert 'LANG-001D/001DX'in n['summary'] and 'LANG-001B/001BX'in n['summary']
    assert 'LANG-001A'not in n['summary'] and r['courses']==[]


def test_social_open_predicates_and_finite_codes_are_distinct():
    html='<h1>Social Science Requirement</h1><p>Two courses (4 units each; Letter Grade; Special Studies courses will not be accepted; Upper division major courses may not overlap</p><h2>Approved Social Science Departments</h2><ul><li>Anthropology</li><li>Political Science [POLI-010 to POLI-179]</li><li>Communication [COMM-010, COMM-030 only]</li></ul><p>* COGS-009, 010, and 188</p>'
    r=p.parse_social(html)
    assert {c['code']for c in r['courses']}=={'COMM 10','COMM 30','COGS 9','COGS 10','COGS 188'}
    assert next(n for n in r['requirements']if n['title']=='Political Science eligibility')['course_ids']==[]


def test_curated_revelle_scope_and_conflicts_validate():
    d=json.loads(Path('data/programs/'+p.PID+'.json').read_text());validate_program(d)
    rows=[n for n in d['requirements']if n['id'].startswith(p.PID+'-revelle-')]
    assert len(rows)==133
    assert any('Fall 2024/2025' in n['summary']for n in rows)
    assert next(c for c in d['courses']if c['code']=='HUM 1')['credits']==6
    assert not any(c['code']=='BILD X13'for c in d['courses'])
    assert d['curriculum_status']=='partial'
