"""Scope and change detection for the reviewed UT/Yeshiva policy additions."""
import hashlib
import importlib
import json
from pathlib import Path
import pytest
Y=importlib.import_module('atlas.adapters.yeshiva-cs-ai-concentration.adapter')
U=importlib.import_module('atlas.adapters.ut-austin-cs-ml-ai-concentration.adapter')
ROOT=Path(__file__).parents[1]

def test_yu_changed_grade_or_new_condition_is_not_replayed():
    html='<main id="main"><h1>Grade Requirement</h1><p>Yeshiva College: major GPA 2.000.</p></main>'
    p={'heading':'Grade Requirement','sha256':Y.policy_digest('Grade Requirement Yeshiva College: major GPA 2.000.'),'id':'test','title':'Major grades','summary':'At least 2.000.','source_id':'test-source'}
    assert Y.parse_policy(html,p)['requirements'][0]['summary']=='At least 2.000.'
    for changed in [html.replace('2.000','3.000'),html.replace('</main>','<p>Except AI majors.</p></main>'),html.replace('id="main"','id="elsewhere"'),'<nav>'+html+'</nav>']:
        with pytest.raises(ValueError):Y.parse_policy(changed,p)

def test_ut_exact_course_scope_changed_requisites_and_wrong_topic():
    body='Methods. Prerequisite: CS 429 with C-.'
    p={'heading':'342 Test course','code':'CS 342','name':'Test course','sha256':hashlib.sha256(body.encode()).hexdigest(),'description':'Reviewed methods.','prerequisites':'CS 429 with C-.'}
    html='<main><h1>Undergraduate Courses</h1><div class="accordion-item"><h4>342 Test course</h4><div class="accordion-body">'+body+'</div></div></main>'
    assert U.parse_course_metadata(html,[p])['courses'][0]['prerequisites']=='CS 429 with C-.'
    for changed in [html.replace('CS 429','CS 439'),html.replace('342 Test course','378 Different topic'),html.replace('</div></div>',' Additional approval.</div></div>'),'<nav>'+html+'</nav>']:
        with pytest.raises(ValueError):U.parse_course_metadata(changed,[p])

def test_policy_seed_boundaries_and_counts():
    from atlas.db import validate_program
    y=json.loads((ROOT/'data/programs/yeshiva-cs-ai-concentration.json').read_text())
    u=json.loads((ROOT/'data/programs/ut-austin-cs-ml-ai-concentration.json').read_text())
    validate_program(y);validate_program(u)
    assert y['curriculum_status']==u['curriculum_status']=='partial'
    assert len(y['courses'])==22 and len(y['requirements'])==13
    assert len(u['courses'])==9 and len(u['requirements'])==4
    assert sum(c['description'] is not None for c in u['courses'])==5
    assert sum(c['prerequisites'] is not None for c in u['courses'])==5
    assert all((c['credits'],c['credit_unit'])==(3,'semester') for c in u['courses'])
    residence=next(r for r in y['requirements'] if r['id'].endswith('-residency'))
    assert residence['kind']=='note' and residence['credits'] is None
    assert '60%' in residence['summary'] and 'adviser' in residence['summary']
    assert any('74' in n and '75' in n for n in y['notes'])
    assert any('CS 363D' in n for n in u['notes'])
    assert all('curriculum_audit' not in p for p in [y,u])

def test_optional_policy_and_metadata_replay():
    for url,p in Y.POLICY_PROFILES.items():
        path=ROOT/'.cache/research'/('yu-rule-'+p['id']+'.html')
        if not path.exists():pytest.skip('Ignored live review sources unavailable')
        assert Y.parse_policy(path.read_text(),p)['requirements'][0]['id'].endswith(p['id'])
    source=ROOT/'.cache/research/yu-department.html'
    assert len(Y.parse_department_policies(source.read_text())['requirements'])==3
    html=source.read_text().replace('No - students who complete','Yes - students who complete')
    with pytest.raises(ValueError):Y.parse_department_policies(html)
    courses=U.parse_course_metadata((ROOT/'.cache/research/ut-courses.html').read_text())['courses']
    assert len(courses)==5
    U.parse_credit_policy((ROOT/'.cache/research/ut-credit.html').read_text())

def test_optional_credit_rule_new_exception_requires_review():
    source=ROOT/'.cache/research/ut-credit.html'
    if not source.exists():pytest.skip('Ignored credit-policy review source unavailable')
    html=source.read_text()
    U.parse_credit_policy(html)
    with pytest.raises(ValueError):
        U.parse_credit_policy(html.replace('301 through 399, a value of three semester hours','301 through 399, a value of four semester hours'))
    with pytest.raises(ValueError):
        U.parse_credit_policy(html.replace('Course Numbers</h2>','Course Numbers</h2><p>Except CS concentration courses.</p>'))
