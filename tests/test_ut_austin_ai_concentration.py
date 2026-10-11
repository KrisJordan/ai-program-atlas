import importlib,json
from pathlib import Path
import pytest
from atlas.db import validate_program
m=importlib.import_module('atlas.adapters.ut-austin-cs-ml-ai-concentration.adapter')
ROOT=Path(__file__).parents[1]

def pdf_text():
    return '''December 17, 2025
CONCENTRATIONS COURSE LISTINGS
Computer Systems Concentration
● CS 999 Unrelated
Machine Learning and Artificial Intelligence Concentration
Foundation Courses
To earn the Machine Learning and Artificial Intelligence Concentration, you will need to
complete one of the following courses:
These courses may change and additional courses may be added in the future.
● CS 343(H) Test AI foundation
● CS 363M (378H) Test ML foundation
If both CS 343(H) Test AI foundation and CS 363M (378H) Test ML foundation
are taken, one may count as an elective.
Electives
You will also need to take three of the following elective classes:
● CS 342 Test Neural Models
● CS 371N Test Language Methods
● CS 378 Test Applied Language Topic
Mobile Computing Concentration
● CS 371M Unrelated Mobile
'''

def html():
    return '<nav><h3>Machine Learning & Artificial Intelligence</h3></nav><main><h1>Concentrations</h1><h3>Machine Learning &amp; Artificial Intelligence</h3><p>Are you a current CS student interested in a concentration?</p><a href="/sites/default/files/2025-12/UTCS_Concentrations_Course_Listings_12172025.pdf">Explore Concentration Courses</a></main>'

def test_directory_identity_without_claiming_curriculum_freshness():
    r=m.parse(html())
    assert r['program_kind']=='concentration'
    assert not {'courses','requirements','last_verified','curriculum_audit'} & r.keys()

@pytest.mark.parametrize('before,after',[
    ('<h1>Concentrations</h1>','<h1>Graduate programs</h1>'),
    ('<h3>Machine Learning &amp; Artificial Intelligence</h3>','<h3>Other</h3>'),
    ('current CS student','prospective MBA student'),
    ('Explore Concentration Courses','Other file'),
])
def test_html_wrong_scope_and_nav_do_not_qualify(before,after):
    with pytest.raises(ValueError):m.parse(html().replace(before,after))

def test_pdf_rule_hierarchy_and_conditional_reuse():
    r=m.parse_pdf_text(pdf_text())
    assert len(r['courses'])==5 and all(c['credits'] is None for c in r['courses'])
    assert {c['code'] for c in r['courses']}=={'CS 343(H)','CS 363M (378H)','CS 342','CS 371N','CS 378'}
    groups=r['requirements'];assert [g['kind'] for g in groups]==['all','choose_courses','choose_courses','note']
    assert groups[1]['count']==1 and groups[2]['count']==3
    assert set(groups[1]['course_ids']) <= set(groups[2]['course_ids'])
    assert groups[3]['parent_id']==groups[2]['id']
    assert 'only if both foundation routes are taken' in groups[2]['summary']
    assert r['curriculum_status']=='partial' and 'curriculum_audit' not in r

def test_changed_pdf_pool_is_observed_not_seed_replay():
    r=m.parse_pdf_text(pdf_text().replace('CS 342 Test Neural Models','CS 399 Changed named option'))
    assert 'CS 399' in {c['code'] for c in r['courses']}
    assert 'CS 342' not in {c['code'] for c in r['courses']}

@pytest.mark.parametrize('before,after',[
    ('complete one of','complete two of'),
    ('take three of','take two of'),
    ('are taken, one may count as an elective.','may both count twice.'),
    ('Mobile Computing Concentration','Unrecognized End'),
    ('CONCENTRATIONS COURSE LISTINGS','Graduate Research Guide'),
    ('● CS 342 Test Neural Models','● CS 342 Test Neural Models\nOnly with approval.'),
    ('● CS 371N Test Language Methods','● CS 342 Test Neural Models'),
])
def test_unreviewed_pdf_rule_changes_fail(before,after):
    with pytest.raises(ValueError):m.parse_pdf_text(pdf_text().replace(before,after))

def test_seed_keeps_conflicts_and_scope_explicit():
    p=json.loads((ROOT/'data/programs/ut-austin-cs-ml-ai-concentration.json').read_text());validate_program(p)
    assert p['institution']['id']=='university-of-texas-austin'
    assert p['curriculum_status']=='partial' and p['first_offered'] is None
    assert len(p['courses'])==9 and len(p['requirements'])==4
    assert not any(c['name']=='Machine Learning & Artificial Intelligence Capstone' for c in p['courses'])
    assert 'CS 363D' not in {c['code'] for c in p['courses']}
    assert any('conflict' in n for n in p['notes'])
    assert all(o['statement_type']!='learning_outcome' for o in p['outcomes'])

def test_optional_actual_pdf_and_html_replay():
    cached=ROOT/'.cache/research/ut-concentrations-20251217.txt'
    if not cached.exists():pytest.skip('Ignored source extraction absent')
    p=json.loads((ROOT/'data/programs/ut-austin-cs-ml-ai-concentration.json').read_text())
    r=m.parse_pdf_text(cached.read_text())
    assert r['courses']==p['courses'] and r['requirements']==p['requirements']
    directory=Path('/tmp/atlas-ut-concentrations.html')
    if directory.exists():assert m.parse(directory.read_text())['id']==p['id']
