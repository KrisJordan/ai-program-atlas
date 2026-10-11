"""Synthetic observations for BS-only metadata; no copied catalog fixtures."""
import hashlib
import json
from pathlib import Path
import pytest
from atlas.adapters.cmu_bs import adapter
from atlas.adapters.cmu_bs import core_enrichment as e
from atlas import db


def directory(url, body):
    return '<title>Course catalog</title><h1>'+e.DIRECTORIES[url][0]+'</h1><p>2026-2027 Catalog</p>'+body


def block(code='21-266', units='10', prereq='(21-122 and 21-241 Min. grade B)', prose='Vector methods.'):
    return f'<dl class="courseblock"><dt>{code} Example Course</dt><dd>Fall: {units} units<br>{prose}<br>Prerequisites: {prereq}</dd></dl>'


def test_exact_units_and_boolean_grades_not_flattened():
    out=e.parse_directory(directory(e.MATH,block()),e.MATH)
    c=out['courses'][0]
    assert c['credits']==10 and c['credit_unit']=='units'
    assert c['prerequisites']=='(21-122 and 21-241 Min. grade B)'
    assert c['source_id']=='cmu-bs-ai-mathematics-directory'
    assert c['description'] is None
    assert out['curriculum_status']=='partial'
    assert 'curriculum_audit' not in out and 'last_verified' not in out


def test_variable_units_and_missing_prerequisites_remain_unknown():
    raw=directory(e.MATH,'<dl class="courseblock"><dt>21-241 Example</dt><dd>Fall: 9-12 units<br>21-127 is strongly recommended.</dd></dl>')
    out=e.parse_directory(raw,e.MATH)
    assert out['courses'][0]['credits'] is None
    assert out['courses'][0]['prerequisites'] is None
    assert out['observed_eligibility']['21-241']==['21-127 is strongly recommended.']


def test_inline_restrictions_and_changed_prose_observed():
    raw=directory(e.STATS,block('36-235',prose='This course is currently open only to statistics minors. This course is open to those with sophomore standing or higher.'))
    a=e.parse_directory(raw,e.STATS)
    b=e.parse_directory(raw.replace('sophomore','junior'),e.STATS)
    assert len(a['observed_eligibility']['36-235'])==2
    assert a['observed_description_digests']!=b['observed_description_digests']


@pytest.mark.parametrize('raw',[
    '<h1>Sign in</h1><input type="password">',
    '<h1>Unrelated directory</h1>2026-2027 Catalog'+block(),
    '<h1>Department of Mathematical Sciences Courses</h1>'+block(),
    directory(e.MATH,block()+block()),
    directory(e.MATH,block('99-999')),
])
def test_invalid_directory_is_rejected(raw):
    with pytest.raises(ValueError):e.parse_directory(raw,e.MATH)


def history(phrase):
    return '<main><h1>Artificial Intelligence Program</h1><p>BSAI: bachelor’s degree in Artificial Intelligence, '+phrase+'</p></main>'


def test_retrospective_start_is_observed_not_planned_date():
    out=e.parse_history(history('which started in Fall 2018.'))
    assert out['first_offered']['value']=='Fall 2018'
    assert out['first_offered']['evidence_url']==e.HISTORY
    with pytest.raises(ValueError):e.parse_history(history('which will start in Fall 2018.'))
    assert e.parse_history(history('which started in Spring 2020.'))['first_offered']['value']=='Spring 2020'


def test_syllabus_identity_term_and_actual_content_required():
    url='https://www.cs.cmu.edu/~15122/syllabus.shtml'
    good='<title>15-122 Fall 2026</title><h1>Course syllabus</h1><p>Grading Prerequisites Learning Objectives</p>'
    assert e.parse_resource(good,url)['courses'][0]['syllabus']==url
    for bad in [good.replace('Fall 2026','Fall 2025'),good.replace('Learning Objectives','Other'),good.replace('15-122','15-123')]:
        with pytest.raises(ValueError):e.parse_resource(bad,url)


def test_public_policy_not_promoted_as_private_syllabus():
    out=e.parse_resource('<title>15-210 F26</title><p>Fall 26 Course Policies</p>','https://www.cs.cmu.edu/~15210/policies.html')
    assert out['courses'][0]['syllabus'] is None
    assert out['courses'][0]['public_site'] is None


def test_undated_site_does_not_invent_offering_term():
    out=e.parse_resource('<h1>Great Ideas in Theoretical Computer Science</h1><p>Welcome to CS251 at CMU!</p>','https://www.cs251.com')
    assert 'Undated' in out['notes'][0]
    assert 'first_offered' not in out


def test_conditional_minor_policy_changes_require_review():
    html='<h1>Additional Majors, Dual Degrees and Minors</h1><p>Unless otherwise indicated, minors are generally open to all university undergraduate students.</p>'
    assert 'generally' in e.parse_minor_access(html,e.OPTIONS)['observed_minor_access']
    with pytest.raises(ValueError):e.parse_minor_access(html.replace('all university','Dietrich'),e.OPTIONS)
    html='<h1>Statistics and Data Science, Minor</h1><p>36-235 36-236 Double Counting three statistics courses not in the primary major. Sample Programs for the Minor</p>'
    assert 'three statistics' in e.parse_minor_access(html,e.MINOR)['observed_minor_access']
    with pytest.raises(ValueError):e.parse_minor_access(html.replace('three','two'),e.MINOR)


def test_seed_consistency_and_observations_do_not_certify():
    seed=json.loads(Path('data/programs/cmu-bs-ai.json').read_text())
    db.validate_program(seed)
    assert set(adapter.SOURCES)<={s['url'] for s in seed['sources']}
    courses={c['code']:c for c in seed['courses']}
    assert all(courses[c]['name'] for c in ['21-127','21-266','21-268','21-269'])
    assert courses['21-241']['prerequisites'] is None
    assert courses['15-210']['syllabus'] is None
    assert courses['15-122']['syllabus'].endswith('/syllabus.shtml')
    assert seed['first_offered']['evidence_url']==e.HISTORY
    rule=next(r for r in seed['requirements'] if r['id'].endswith('probability-route-eligibility'))
    assert rule['parent_id']=='cmu-bs-ai-math-probability-6'
    assert 'not unrestricted' in rule['summary']
    # These resources do not claim measured program attainment.
    assert not any(o.get('statement_type')=='assessed_outcome' for o in seed['outcomes'])


def test_live_cache_replay_when_available():
    urls=list(e.DIRECTORIES)+[e.HISTORY]+list(e.RESOURCES)+[e.MINOR,e.OPTIONS]
    for url in urls:
        path=Path('.cache/http')/(hashlib.sha256(url.encode()).hexdigest()+'.body')
        if not path.exists():pytest.skip('Optional local source cache is absent')
        observed=adapter.SOURCE_PARSERS[url](path.read_text())
        assert 'curriculum_audit' not in observed and 'last_verified' not in observed
        assert observed['curriculum_status']=='partial'


def test_additional_math_resources_preserve_historical_term():
    url='https://www.math.cmu.edu/~jmackey/151_128/syll.html'
    raw='<title>21-128 and 15-151, Fall 2023</title><h2>Syllabus for 15-151 and 21-128</h2><p>Course Outline: Topics. Tentative week by week schedule</p>'
    out=e.parse_resource(raw,url)
    assert out['courses'][0]['syllabus']==url
    assert out['courses'][0]['public_site'] is None
    assert 'Fall 2023' in out['notes'][0]
    with pytest.raises(ValueError):e.parse_resource(raw.replace('Fall 2023','Fall 2026'),url)
