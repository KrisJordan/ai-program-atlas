"""UNC source scopes and changed observations, without copied catalog fixtures."""
import hashlib
import importlib.util
import json
from pathlib import Path
import pytest
from atlas import db
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('unc_minor',ROOT/'atlas/adapters/unc-ai-minor/adapter.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)

def minor_fixture():
    rows=['<tr><td>Core Requirements</td></tr>']
    for i,code in enumerate(a.CODES):
        if i==3:rows.append('<tr><td>Select two courses from the following list:</td><td>6</td></tr>')
        rows.append(f'<tr><td class="codecol"><a class="code">{code}</a></td><td>Example topic {i}</td><td>{3 if i<3 else ""}</td></tr>')
    rows.append('<tr class="listsum"><td>Total Hours</td><td>15</td></tr>')
    return '<div id="content"><h1>Artificial Intelligence Minor</h1><div id="requirementstextcontainer"><p>at least nine hours; 2.000; Honors version available; Enrollment and GPA restrictions may apply</p><table class="sc_courselist"><tbody>'+''.join(rows)+'</tbody></table></div></div>'

def course_fixture():
    rows=[]
    for i,code in enumerate(a.CODES):
        rows.append(f'<div class="courseblock"><span class="detail-code">{code}.</span><span class="detail-title">Example topic {i}.</span><span class="detail-hours">3 Credits.</span><p class="courseblockextra">Synthetic description {i}.</p><span class="detail-requisites">Requisites: Example permission {i}.</span></div>')
    return '<div id="content"><h1>DATA SCIENCE AND SOCIETY (DATA)</h1>'+''.join(rows)+'</div>'

def test_extracts_required_and_alternative_scopes_and_changed_choice():
    observation=a.parse(minor_fixture())
    assert len(observation['courses'])==7
    core=next(r for r in observation['requirements'] if r['id'].endswith('-core'))
    electives=next(r for r in observation['requirements'] if r['id'].endswith('-electives'))
    assert len(core['course_ids'])==3 and len(electives['course_ids'])==4
    assert electives['count']==2 and electives['credits']==6
    assert all(c['credits'] is None for c in observation['courses'][3:])
    changed=a.parse(minor_fixture().replace('Select two','Select three'))
    assert next(r for r in changed['requirements'] if r['id'].endswith('-electives'))['count']==3
    assert not {'outcomes','curriculum_status','curriculum_audit','last_verified'} & observation.keys()

def test_names_prerequisites_and_credit_amounts_are_observed_not_seed_replayed():
    fixture=course_fixture().replace('Example topic 0','Different subject').replace('3 Credits.','4 Credits.',1)
    observation=a.parse_courses(fixture)
    assert observation['courses'][0]['name']=='Different subject'
    assert observation['courses'][0]['credits']==4
    assert observation['courses'][0]['prerequisites']=='Example permission 0.'
    assert all(c['description'] is None for c in observation['courses'])
    with pytest.raises(ValueError):a.parse_courses(fixture.replace('DATA 520.','DATA 999.'))

@pytest.mark.parametrize('prefix',['<h1>Access denied</h1>','<input type="password">'])
def test_rejects_gates(prefix):
    with pytest.raises(ValueError):a.parse(prefix+minor_fixture())
    with pytest.raises(ValueError):a.parse_courses(prefix+course_fixture())

def test_navigation_and_missing_curriculum_do_not_establish_identity():
    with pytest.raises(ValueError):a.parse('<nav><h1>Artificial Intelligence Minor</h1></nav><div id="content"><h1>Other Program</h1></div>')
    with pytest.raises(ValueError):a.parse('<div id="content"><h1>Artificial Intelligence Minor</h1></div>')
    with pytest.raises(ValueError):a.parse(minor_fixture().replace('2.000','3.000'))

def test_nested_policy_heading_preserves_section_scope():
    m=a.content('<div id="content"><h1>Example</h1><div><h3>Rule</h3></div><p>Relevant words.</p><h3>Next</h3><p>Unrelated words.</p></div>','Example')
    assert a.section(m,'Rule')=='Relevant words.'

@pytest.mark.parametrize('url',a.SOURCES)
def test_optional_current_cache_replay(url):
    path=ROOT/'.cache/http'/(hashlib.sha256(url.encode()).hexdigest()+'.body')
    if not path.exists():pytest.skip('Optional ignored official source cache absent')
    html=path.read_text();observed=a.SOURCE_PARSERS[url](html)
    assert observed['id']=='unc-ai-minor'
    assert not {'curriculum_status','curriculum_audit','last_verified'} & observed.keys()
    if url in a.POLICIES:
        guard=a.POLICIES[url][2][0][-1][0]
        assert guard in html
        with pytest.raises(ValueError):a.SOURCE_PARSERS[url](html.replace(guard,'Unreviewed changed condition'))
    if url==a.COURSES:
        assert sum(c['description'] is not None for c in observed['courses'])==7
        assert sum(c['prerequisites'] is not None for c in observed['courses'])==4
        changed=html.replace('This course is a broad, high-level survey','A different course description')
        assert a.parse_courses(changed)['courses'][0]['description'] is None
    if url==a.CATALOG:
        assert len(observed['outcomes'])==5


def test_manual_complete_local_audit_and_missingness():
    seed=json.loads((ROOT/'data/programs/unc-ai-minor.json').read_text());db.validate_program(seed)
    assert seed['curriculum_status']=='complete'
    assert seed['curriculum_audit']['scope']=='minor'
    assert seed['first_offered'] is None
    assert not seed['curriculum_audit']['unresolved_requirements']
    assert len(seed['courses'])==7 and len(seed['outcomes'])==5
    assert all(o['statement_type']=='learning_outcome' for o in seed['outcomes'])
    assert all(c['credits']==3 and c['credit_unit']=='semester_hours' for c in seed['courses'])
    assert set(a.SOURCES)<={s['url'] for s in seed['sources']}
    assert all(r['source_id'] in seed['curriculum_audit']['source_ids'] for r in seed['requirements'])


def test_bounded_survey_covers_exact_claims_without_absence_inference():
    rows=json.loads((ROOT/'data/surveys/national-depth-batch2-2026-10-11.json').read_text())
    assert len(rows)==10 and len({r['institution_id'] for r in rows})==10
    assert sum(r['status']=='confirmed' for r in rows)==1
    assert sum(r['status']=='inspected' for r in rows)==9
    assert all(r['sources'] and r['note'] and r['checked_at']=='2026-10-11' for r in rows)
