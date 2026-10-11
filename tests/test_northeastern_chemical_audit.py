"""BSChE independent course/profile and local policy source regression checks."""
import json
from importlib import import_module
from pathlib import Path
import pytest
from atlas.adapters.northeastern_course_metadata import parse_subject
from atlas.curriculum_profile import requirement_profile

ROOT=Path(__file__).resolve().parents[1]
PID='northeastern-chemical-engineering-ai-bsche'
URL='https://catalog.northeastern.edu/course-descriptions/chme/'


def test_chemical_recitation_metadata_observed_with_zero_hours_and_changed_conditions():
    html='''<header id="site-title"><h1>Chemical Engineering (CHME)</h1></header>
    <div id="textcontainer"><div class="courseblock"><p class="courseblocktitle">CHME 3306. Recitation for CHME 3305. (0 Hours)</p>
    <p class="cb_desc">Accompanies CHME 3305. Discusses laboratory safety, experiments and reporting.</p>
    <p class="courseblockextra">Corequisite(s): CHME 3305</p></div></div>'''
    def parse(h):return parse_subject(h,program_id=PID,subject='CHME',heading='Chemical Engineering (CHME)',codes=['CHME 3306'],url=URL)
    result=parse(html); observed=result['courses'][0]
    assert observed['credits']==0 and observed['credit_unit']=='semester_hours'
    assert observed['category']=='applications' and observed['description']
    assert observed['prerequisites'] is None
    assert any('corequisite(s): CHME 3305' in note for note in result['notes'])
    assert 'category_review' not in observed
    changed=parse(html.replace('(0 Hours)','(1 Hour)').replace('Corequisite(s): CHME 3305','Corequisite(s): CHME 4703'))
    assert changed['courses'][0]['credits']==1 and changed['courses'][0]['prerequisites'] is None
    assert any('corequisite(s): CHME 4703' in note for note in changed['notes'])
    changed=parse(html.replace('Accompanies CHME 3305','An entirely new independent topic'))
    assert changed['courses'][0]['description'] is None and changed['courses'][0]['category']=='other'
    renamed=parse(html.replace('Recitation for CHME 3305. (0 Hours)','Different Chemical Topic. (0 Hours)'))
    assert renamed['courses'][0]['description'] is None and renamed['courses'][0]['category']=='other'
    with pytest.raises(ValueError):parse(html.replace('<h1>Chemical Engineering (CHME)</h1>','<h1>Unrelated catalog</h1>'))


def test_bsche_policy_award_label_and_numeric_criteria_are_local_observations():
    m=import_module('atlas.adapters.'+PID+'.adapter')
    html='''<header id="site-title"><h1>Degrees, Majors, and Minors</h1></header><div id="textcontainer">
    <h2>Combined Majors</h2><p>A combined major is one major with at least nine courses from each discipline.
    No more than two courses may count for both disciplines and there must be at least 16 courses in the combined major.
    There are multiple points of curricular integration. Most combined majors allow the student to choose the home college.
    Completion earns one degree, and one diploma.</p><h2>Other</h2></div>'''
    result=m._chemical_policy(html,'combined')
    award=next(r for r in result['requirements'] if r['id'].endswith('combined-one-award'))
    assert 'BSChE' in award['summary'] and 'BSEnvE' not in award['summary']
    assert result['courses']==[] and result['curriculum_status']=='partial'
    assert 'curriculum_audit' not in result and 'family' not in result
    changed=m._chemical_policy(html.replace('at least nine','at least ten'),'combined')
    assert any('at least 10 courses' in r['summary'] for r in changed['requirements'])
    with pytest.raises(ValueError):m._chemical_policy(html.replace('Combined Majors','Other Majors'),'combined')


def test_chemical_manual_profile_and_all_six_source_policies_preserve_role_sets():
    p=json.loads((ROOT/'data/programs'/f'{PID}.json').read_text())
    e=next(e for e in json.loads((ROOT/'research/degree-audit/northeastern.json').read_text())['programs'] if e['program_id']==PID)
    assert len(p['courses'])==46 and all(c.get('category_review') for c in p['courses'])
    assert 'family' not in p and p['award_level']=='other'
    actual=requirement_profile(p)
    for role in ['required','options','unresolved']:
        assert actual[role]['count']==e['expected_profile'][role]['count']
        assert actual[role]['categories']==e['expected_profile'][role]['categories']
        assert actual[role]['classification']['unreviewed']==0
    assert actual['required']['count']==39 and actual['options']['count']==7
    for code in ['CHME 3306','CHME 4705']:
        c=next(c for c in p['courses'] if c['code']==code)
        assert c['credits']==0 and c['id'] in e['expected_course_ids']['required']
    assert next(c for c in p['courses'] if c['code']=='ENCP 3000')['category']=='human_context'
    assert next(c for c in p['courses'] if c['code']=='CHME 4512')['category']=='applications'
    for profile in ['universitywide','nupath','experiential','graduation','combined','progression']:
        sid=PID+'-'+profile+'-policy'
        assert any(s['id']==sid for s in p['sources'])
        rows=[r for r in p['requirements'] if r['source_id']==sid]
        assert rows and all(not r['course_ids'] for r in rows)


def test_optional_actual_chemical_sources_replay_without_manual_review_metadata():
    cache=ROOT/'.cache/research/degree-audit-northeastern'
    if not all((cache/(s+'.html')).exists() for s in ['chme','encp']):pytest.skip('Optional ignored official source cache')
    m=import_module('atlas.adapters.'+PID+'.adapter');p=json.loads((ROOT/'data/programs'/f'{PID}.json').read_text())
    courses={c['id']:c for c in p['courses']}
    for subject in ['chme','encp']:
        observed=m.SOURCE_PARSERS[f'https://catalog.northeastern.edu/course-descriptions/{subject}/']((cache/(subject+'.html')).read_text())
        for c in observed['courses']:
            assert 'category_review' not in c
            assert c=={k:v for k,v in courses[c['id']].items() if k!='category_review'}
    for profile in ['universitywide','nupath','experiential','graduation','combined','progression']:
        f=cache/f'policy-{profile}.html'
        if not f.exists():continue
        rows=m._chemical_policy(f.read_text(),profile)['requirements']
        assert rows==[r for r in p['requirements'] if r['source_id']==PID+'-'+profile+'-policy']
