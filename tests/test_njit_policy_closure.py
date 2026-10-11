"""Policy observations and independent source-inventory reconciliation."""
import hashlib
import importlib.util
import json
from html import escape
from pathlib import Path

import pytest
from atlas import db
from atlas.adapters import njit_policy_closure as m
from atlas.curriculum_profile import requirement_profile


def fixture(kind, rows):
    body=''.join('<p>'+escape(phrase)+'</p>' for _,_,phrases,_ in rows for phrase in phrases)
    if kind=='advising':
        return '<main><section><h4>Undergraduate Advising</h4>'+body+'</section><section><h4>Graduate Advising</h4><p>Graduate GPA 3.0</p></section></main>'
    return '<main><h1>'+('Academic Policies and Procedures' if kind=='catalog' else 'Petition')+'</h1>'+body+'</main>'


@pytest.mark.parametrize('kind,rows',[('catalog',m.CATALOG_RULES),('advising',m.ADVISOR_RULES),('petition',m.PETITION_RULES)])
def test_material_policy_changes_require_review(kind,rows):
    html=fixture(kind,rows)
    result=m.parse(html,kind)
    assert len(result['requirements'])==len(rows)
    assert result['courses']==[]
    assert not {'curriculum_audit','curriculum_status','last_verified'} & result.keys()
    assert all(r['kind']=='note' and not r['course_ids'] for r in result['requirements'])
    for _,_,phrases,_ in rows:
        with pytest.raises(ValueError,match='condition changed'):
            m.parse(html.replace(escape(phrases[0]),'changed source rule'),kind)


def test_graduate_scope_cannot_supply_undergraduate_condition():
    html=fixture('advising',m.ADVISOR_RULES)
    phrase='at least eight (8) weeks in duration'
    html=html.replace(phrase,'changed duration').replace('Graduate GPA 3.0',phrase)
    with pytest.raises(ValueError,match='condition changed'):
        m.parse(html,'advising')
    with pytest.raises(ValueError,match='scope missing'):
        m.parse('<h4>Graduate Advising</h4>','advising')


@pytest.mark.parametrize('kind,url',[('catalog',m.BASE),('advising',m.ADVISOR_URL),('petition',m.PETITION_URL)])
def test_actual_permitted_policy_cache_and_adapter_registration(kind,url):
    path=Path('.cache/http',hashlib.sha256(url.encode()).hexdigest()+'.body')
    if not path.exists():
        pytest.skip('Ignored public source cache unavailable')
    spec=importlib.util.spec_from_file_location('njit_closure_adapter',Path('atlas/adapters',m.PID,'adapter.py'))
    adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
    observed=adapter.SOURCE_PARSERS[url](path.read_text())
    assert len(observed['requirements'])==({'catalog':16,'advising':3,'petition':1}[kind])
    assert len({r['id'] for r in observed['requirements']})==len(observed['requirements'])
    assert not {'curriculum_audit','last_verified'} & observed.keys()
    program=json.loads(Path('data/programs',m.PID+'.json').read_text())
    assert url in {s['url'] for s in program['sources']}


def test_manual_source_sets_and_subject_counts_match_exported_profile():
    program=json.loads(Path('data/programs',m.PID+'.json').read_text())
    db.validate_program(program)
    ledger=json.loads(Path('research/degree-audit/national-degree-batch.json').read_text())
    entry=next(r for r in ledger['programs'] if r['program_id']==m.PID)
    assert entry['status']=='blocked' and len(entry['blockers'])==4
    assert program['curriculum_status']=='partial'
    assert len(program['courses'])==381
    assert all(c.get('category_review') for c in program['courses'])
    profile=requirement_profile(program)
    for kind in ['required','options','unresolved']:
        assert profile[kind]['count']==entry['expected_profile'][kind]['count']
        assert profile[kind]['categories']==entry['expected_profile'][kind]['categories']
    terms=[r for r in program['requirements'] if r['id'].startswith(m.PID+'-term-')]
    assert len(terms)==8 and all(r['kind']=='all' for r in terms)
    fixed={i for r in terms for i in r['course_ids']}
    pools=[r for r in program['requirements'] if r['id'] in {m.PID+'-'+k for k in ['njit-ger-200','njit-ger-300','njit-natural','njit-capstone']}]
    options={i for r in pools for i in r['course_ids']}-fixed
    assert len(options)==349
    options.remove('njit-lit-378')  # Explicit reciprocal identity, not title inference.
    assert fixed==set(entry['expected_course_ids']['required'])
    assert options==set(entry['expected_course_ids']['options'])
    assert entry['expected_course_ids']['unresolved']==[]
    assert profile['required']['count']==32
    assert profile['options']['count']==348
    assert profile['options']['source_record_count']==349
    assert 'njit-phil-310' in entry['expected_course_ids']['required']
    assert 'njit-phil-310' not in entry['expected_course_ids']['options']
    assert 'njit-sts-378' in entry['expected_course_ids']['options']
    assert 'njit-lit-378' not in entry['expected_course_ids']['options']
    courses={c['id']:c for c in program['courses']}
    assert courses['njit-r216-206']['credits'] is None
    assert courses['njit-fys-sem']['credits']==0
    rules={r['id']:r for r in program['requirements']}
    assert 'at least eight weeks' in rules[m.PID+'-closure-outside-mtsm']['summary']
    assert 'does not guarantee' in rules[m.PID+'-closure-substitution-petition']['summary']
