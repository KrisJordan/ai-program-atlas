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


def test_crosslisted_course_is_one_slot_not_a_required_bundle():
    html='<table><tr><td class="codecol"><a class="code" href="/a">ONE 100</a> / <a class="code" href="/b">TWO 100</a></td><td>Synthetic cross-listed course</td><td class="hourscol">3</td></tr></table>'
    t=Tables('test','source','https://example.edu/')
    t.table(BeautifulSoup(html,'html.parser').table,'Core')
    slot=next(r for r in t.rules if r['course_ids'])
    assert slot['kind']=='choose_courses' and slot['count']==1 and len(slot['course_ids'])==2
    assert all(c['credits'] is None for c in t.courses.values())


EXTRA_IDS=['rice-university-artificial-intelligence-bs-degree','northwestern-university-artificial-intelligence-major-bs-in-engineering-bse-degree']

@pytest.mark.parametrize('pid',EXTRA_IDS)
def test_additional_degree_seeds_and_observations(pid):
    a=importlib.import_module('atlas.adapters.'+pid+'.adapter')
    p=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text());validate_program(p)
    assert set(a.SOURCES)<={s['url'] for s in p['sources']}
    assert p['curriculum_status']=='partial' and p['curriculum_audit']['unresolved_requirements']
    with pytest.raises(ValueError):a.parse('<main><h1>Unrelated degree</h1></main>')
    path=ROOT/'.cache/http'/(hashlib.sha256(a.SOURCES[0].encode()).hexdigest()+'.body')
    if not path.exists():pytest.skip('Optional local evidence cache unavailable')
    html=path.read_text();d=a.parse(html)
    assert not {'last_verified','curriculum_status','curriculum_audit'}&d.keys()
    with pytest.raises(ValueError):a.parse('<h1>Sign in</h1><input type="password">'+html)
    if pid.startswith('rice'):
        domains=next(r for r in d['requirements'] if r['title']=='Choose three of five elective areas')
        assert domains['count']==3
        children=[r for r in d['requirements'] if r['parent_id']==domains['id']]
        assert len(children)==5 and all(r['kind']=='alternative' for r in children)
        stats=[r for r in d['requirements'] if 'rice-ai-stat-314' in r['course_ids']]
        assert len(stats)==2 and all(r['kind']=='all' and len(r['course_ids'])==2 for r in stats)
        crosslist=next(r for r in d['requirements'] if 'rice-ai-comp-450' in r['course_ids'])
        assert crosslist['kind']=='choose_courses' and crosslist['count']==1 and len(crosslist['course_ids'])==3
        with pytest.raises(ValueError):a.parse(html.replace('3 of the following 5','4 of the following 5'))
    else:
        domains=next(r for r in d['requirements'] if r['title']=='Five of six breadth domains')
        assert domains['count']==5
        children=[r for r in d['requirements'] if r['parent_id']==domains['id']]
        assert len(children)==6 and all(r['kind']=='alternative' for r in children)
        topics=[c for c in d['courses'] if c['code']=='COMP_SCI 496-0']
        assert len(topics)>3 and len({c['id'] for c in topics})==len(topics)
        assert next(r for r in d['requirements'] if r['course_ids']==['nw-bse-physics-135-1'])['kind']=='note'
        with pytest.raises(ValueError):a.parse(html.replace('five of the six categories','four of the six categories'))


def test_reviewed_outcomes_require_current_matching_statements():
    from atlas.adapters.degree_table_observations import reviewed_outcomes
    root=BeautifulSoup('<main><h2>Learning Outcomes</h2><ul><li>Evaluate synthetic systems with explicit tests.</li></ul></main>','html.parser')
    summaries=[(['Evaluate','explicit tests'],'Assess systems through tests.')]
    result=reviewed_outcomes(root,'Learning Outcomes',summaries,'source')
    assert result[0]['kind']=='source_stated' and result[0]['source_id']=='source'
    with pytest.raises(ValueError):reviewed_outcomes(root,'Learning Outcomes',[(['invented evidence'],'Wrong.')],'source')
    with pytest.raises(ValueError):reviewed_outcomes(root,'Learning Outcomes',summaries*2,'source')
