"""Dated finite inventory, source grammar, and conditional applicability checks."""
import json
from pathlib import Path
import pytest
from atlas.adapters import miami_thematic_directory as td
from atlas.db import validate_program

ROOT=Path(__file__).resolve().parents[1]
PIDS=['miami-data-science-ai-bs','miami-ai-technologies-business-bsba',
 'university-of-miami-data-science-and-artificial-intelligence-ba-degree',
 'university-of-miami-artificial-intelligence-technologies-for-business-other-degree']


def row(code='AAA 101',inactive=False,extra=''):
    return f'<tr class="course"><td>{code}{" *" if inactive else ""}</td><td></td><td><a>Synthetic course</a>{extra}</td><td>1/3</td><td>Fall</td></tr>'


def fixture(rule='Complete at least 1 course from the following:',group_rule='Complete 1 of the following option groups:'):
    return f'''<h1>Synthetic cognate</h1><select id="term_selector" data-acadplan="AT_9999"><option selected>Fall 2026</option></select>
    <ul><li><span>Academic Plan</span>AT_9999</li><li><span>Cognate</span>Arts and Humanities</li>
    <li><span>Responsible Academic Unit</span><span>Synthetic unit</span></li><li><span>Recommended for</span>All students.</li>
    <li><span>Required Courses</span>Students must complete at least 3 courses for at least 9 credits.</li><li><span>Number of Groups:</span>1</li></ul>
    <div><h2>Description</h2><p>Synthetic context.</p></div><div><h2>Option Groups</h2><p>{group_rule}</p></div>
    <a href="#panel_1">Synthetic group</a><div id="panel_1"><p>{rule}</p><table class="group_table"><tr><th>Course</th></tr>
    {row()}{row('AAA 102',True)}{row('AAA 103',extra='<div>Requisite: Sophomore standing.</div>')}</table></div>
    <p>*Indicates an inactive course</p>'''


def parse(html,spec=None):
    spec=spec or td.extract_plan(fixture(),'AT_9999')
    return td.parse_thematic(html,pid='synthetic',plan='AT_9999',spec=spec)


def test_extracted_counts_caps_inactive_and_context():
    d=parse(fixture());assert len(d['courses'])==2
    assert d['requirements'][1]['count']==1
    assert 'at least 3 courses for at least 9 credits' in d['requirements'][0]['summary']
    assert 'AAA 102' in d['requirements'][-1]['summary']
    assert '1–3 published credit range' in d['requirements'][1]['summary']
    assert 'Requisite: Sophomore standing.' in d['requirements'][1]['summary']
    assert all(c['credits'] is None for c in d['courses'])
    assert not {'curriculum_audit','curriculum_status','last_verified'} & d.keys()
    d=parse(fixture('Complete at least 2 courses from the following:'))
    assert d['requirements'][1]['count']==2
    for text in ['Complete at most 2 courses from the following:',
                 'Complete 6 credits from the following:',
                 'Complete exactly 1 course from the following: except eligible majors take two.']:
        d=parse(fixture(text));assert d['requirements'][1]['kind']=='note'
        assert d['requirements'][1]['count'] is None and text in d['requirements'][1]['summary']
    assert parse(fixture(group_rule='Choose one route with approval.'))['requirements'][1]['kind']=='note'


@pytest.mark.parametrize('old,new',[
 ('Fall 2026','Spring 2027'),('Synthetic context.','A new placement prerequisite.'),
 ('All students.','Non-majors only.'),('Synthetic unit','Other unit'),
 ('<span>Number of Groups:</span>1','<span>Number of Groups:</span>2'),
 ('*Indicates an inactive course','*Another marker'),
 ('<td>1/3</td>','<td>3/1</td>'),
 ('</table>','<tr><td>Unclassified option</td></tr></table>'),
 ('<p>Complete at least 1','<p>Hidden extra rule.</p><p>Complete at least 1'),
])
def test_changed_context_or_unaccounted_rows_require_review(old,new):
    with pytest.raises(ValueError):parse(fixture().replace(old,new))


def test_missing_titles_and_null_unit_are_not_invented():
    html=fixture().replace('<span>Synthetic unit</span>','').replace('Synthetic course','Synthetic cou…')
    spec=td.extract_plan(html,'AT_9999');o=parse(html,spec)
    assert spec['unit'] is None and all(c['name'] is None for c in o['courses'])
    assert 'unit not stated' in o['requirements'][0]['summary']


def test_manifest_has_every_dated_active_entry_and_exact_row_accounting():
    m=json.loads(td.MANIFEST.read_text());ps=m['plans']
    assert len(ps)==len({p['id'] for p in ps})==215
    assert m['scope']['unreviewed_entries']==0
    assert sum(p['route_kind']=='thematic' for p in ps)==212
    assert {p['id'] for p in ps if p['route_kind']=='individualized'}==td.INDIVIDUALIZED
    assert {p['semester'] for p in ps}=={'Fall 2026'}
    assert {p['directory_state'] for p in ps}=={'active_filter_listing'}
    assert sum(len(p['groups']) for p in ps)==440
    assert sum(len(g['rows']) for p in ps for g in p['groups'])==2699
    for p in ps:
        assert p['accounting']['rows']==sum(len(g['rows']) for g in p['groups'])
        assert p['accounting']['inactive_rows']==sum(r['inactive'] for g in p['groups'] for r in g['rows'])
        assert p['source_publication_date'] is None
        for g in p['groups']:assert [r['row'] for r in g['rows']]==list(range(1,len(g['rows'])+1))


@pytest.mark.parametrize('pid',PIDS)
def test_curated_routes_conditional_rules_source_conflicts_and_business_exclusion(pid):
    d=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text());validate_program(d)
    rs={r['id']:r for r in d['requirements']};business='business' in pid
    specs=td.reviewed_specs()
    ids={p for p in specs if p.startswith(('AT_','PS_')) and p not in td.INDIVIDUALIZED and not(business and p=='PS_0051')}
    assert len(ids)==(172 if business else 173)
    for plan in ids:
        root=rs[pid+'-thematic-'+plan.lower()]
        assert root['parent_id']==pid+'-policy-cognate-rules' and root['kind']=='note'
    assert not any('-thematic-st_' in rid for rid in rs)
    if business:
        assert pid+'-thematic-ps_0051' not in rs
        assert 'unavailable for credit' in rs[pid+'-thematic-business-exclusion']['summary']
    assert 'NEU majors' in rs[pid+'-thematic-ps_0044']['summary']
    assert rs[pid+'-thematic-ps_0044-group-1']['kind']=='note'
    assert 'SPA 211 or higher' in rs[pid+'-thematic-at_0079']['summary']
    assert 'AP and IB credit cannot' in rs[pid+'-thematic-at_0055-group-1']['title']
    assert 'open approval route' in rs[pid+'-thematic-at_0045']['summary']
    assert rs[pid+'-thematic-at_0045-group-1']['course_ids']==[]
    assert 'audition' in rs[pid+'-thematic-at_0102']['summary']
    assert 'blank' in rs[pid+'-thematic-at_0094']['summary']
    assert 'clarification' in rs[pid+'-thematic-ps_0017']['summary']
    assert d['curriculum_status']=='partial'
    assert any('summer' in x for x in d['curriculum_audit']['unresolved_requirements'])
    assert any('zero unreviewed' in x for x in d['curriculum_audit']['unresolved_requirements'])
    assert len(d['courses'])==len({c['id'] for c in d['courses']})==len({c['code'] for c in d['courses']})


def test_optional_complete_source_replay():
    plans=td.reviewed_specs();cache=ROOT/'var/miami-cognates'
    if not all((cache/(p+'.html')).exists() for p in plans):pytest.skip('Optional ignored public HTML captures')
    for plan,spec in plans.items():
        html=(cache/(plan+'.html')).read_text();observed=td.extract_plan(html,plan)
        assert all(observed[k]==spec[k] for k in observed)
        if plan not in td.INDIVIDUALIZED:
            result=td.parse_thematic(html,pid='synthetic',plan=plan,spec=spec)
            assert len(result['courses'])==len({r['code'] for g in spec['groups'] for r in g['rows'] if not r['inactive']})
    b=td.parse_thematic((cache/'PS_0051.html').read_text(),pid=PIDS[1],plan='PS_0051')
    assert b['courses']==[] and len(b['requirements'])==1


def test_reviewed_conditional_rules_cannot_silently_keep_old_manual_summary():
    spec=td.extract_plan(fixture(),'AT_9999')
    spec['context_note']='Reviewed one-course branch.'
    spec['context_rule_sha256']=td.rule_context_digest(spec)
    with pytest.raises(ValueError,match='conditional/group context'):
        parse(fixture('Complete at least 2 courses from the following:'),spec)
