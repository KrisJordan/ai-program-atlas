"""Independent degree-parser checks use invented course titles and minimal fact tables."""
import hashlib
import importlib
import json
from pathlib import Path
from bs4 import BeautifulSoup
import pytest
from atlas.adapters.degree_table_observations import Tables
from atlas.db import validate_program

ROOT=Path(__file__).resolve().parents[1]
IDS=[f'case-western-reserve-university-artificial-intelligence-{award}-degree' for award in ['ba','bs']]


def row(code,title='Synthetic course',classes='',indent=False):
    link=f'<a class="code" href="/course/{code}">{code}</a>'
    if indent:link='<div class="blockindent">'+link+'</div>'
    return f'<tr class="{classes}"><td class="codecol">{link}</td><td>{title}</td></tr>'


def test_bundled_alternative_preserves_both_courses_and_unknown_credits():
    html='<table><tr><td>Choose one of the following:</td></tr>'+row('TEST 100',indent=True)+'''<tr><td class="codecol"><div class="blockindent"><a class="code" href="/a">TEST 101</a> &amp; <a class="code" href="/b">TEST 102</a></div></td><td>Synthetic first<br/>and Synthetic second</td><td class="hourscol">4</td></tr>'''+row('TEST 200')+'</table>'
    t=Tables('test','source','https://example.edu/catalog/')
    root=t.table(BeautifulSoup(html,'html.parser').table,'Core')
    alt=next(r for r in t.rules if r['kind']=='alternative')
    options=[r for r in t.rules if r['parent_id']==alt['id']]
    assert [len(r['course_ids']) for r in options]==[1,2]
    assert options[1]['kind']=='all'
    assert next(r for r in t.rules if r['course_ids']==['test-test-200'])['parent_id']==root['id']
    assert all(c['credits'] is None for c in t.courses.values())


def test_or_rows_are_alternatives_and_choose_six_keeps_count():
    html='<table>'+row('TEST 1')+row('TEST 2',classes='orclass')+'<tr><td>Choose six from the following:</td></tr>'+''.join(row('TEST '+str(i),indent=True) for i in range(10,18))+'</table>'
    t=Tables('test','source','https://example.edu/')
    t.table(BeautifulSoup(html,'html.parser').table,'Core')
    alt=next(r for r in t.rules if r['kind']=='alternative')
    assert len([r for r in t.rules if r['parent_id']==alt['id']])==2
    choose=next(r for r in t.rules if r['kind']=='choose_courses')
    assert choose['count']==6 and len([r for r in t.rules if r['parent_id']==choose['id']])==8


@pytest.mark.parametrize('pid',IDS)
def test_records_validate_and_sources_are_registered(pid):
    p=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text());validate_program(p)
    a=importlib.import_module('atlas.adapters.'+pid+'.adapter')
    assert set(a.SOURCES)<={s['url'] for s in p['sources']}
    assert p['curriculum_status']=='partial' and p['curriculum_audit']['unresolved_requirements']
    for html in ['<main>Unrelated program</main>','<h1>Sign in</h1><input type="password">Artificial Intelligence, BA']:
        with pytest.raises(ValueError):a.parse(html)


@pytest.mark.parametrize('pid',IDS)
def test_cached_live_structure_and_material_changes(pid):
    a=importlib.import_module('atlas.adapters.'+pid+'.adapter')
    path=ROOT/'.cache/http'/(hashlib.sha256(a.SOURCES[0].encode()).hexdigest()+'.body')
    if not path.exists():pytest.skip('Optional local evidence cache unavailable')
    html=path.read_text();d=a.parse(html)
    assert not {'curriculum_audit','curriculum_status','last_verified'}&d.keys()
    bundle=next(r for r in d['requirements'] if len(r['course_ids'])==2 and any(c.endswith('csds-132') for c in r['course_ids']))
    assert bundle['kind']=='all' and any(c.endswith('csds-237') for c in bundle['course_ids'])
    if '-bs-' in pid:
        assert any(r['count']==6 for r in d['requirements'])
        assert any(r['count']==4 for r in d['requirements'])
        assert any('at most two' in r['summary'].lower() or 'no more than two' in r['summary'].lower() for r in d['requirements'])
        with pytest.raises(ValueError):a.parse(html.replace('at most two courses','at most three courses'))
    else:
        assert any('two listed courses carrying 1.5' in r['summary'] for r in d['requirements'])
        with pytest.raises(ValueError):a.parse(html.replace('Choose three of the following','Choose four of the following'))
