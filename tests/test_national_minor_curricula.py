"""Requirements parsers must observe source structure and preserve alternatives."""
import importlib
import json
from pathlib import Path
import pytest
from atlas.db import validate_program
ROOT=Path(__file__).resolve().parents[1]
FIXTURES=ROOT/'tests/fixtures/national_minors'
IDS={'gatech':'georgia-institute-of-technology-computing-and-artificial-intelligence-minor-minor','cornell':'cornell-university-artificial-intelligence-minor-minor','northwestern':'northwestern-university-artificial-intelligence-minor-minor-minor','emory':'emory-university-artificial-intelligence-minor-minor'}
def adapter(key):return importlib.import_module('atlas.adapters.'+IDS[key]+'.adapter')
def fixture(key):return (FIXTURES/(key+'.html')).read_text()

@pytest.mark.parametrize('key',IDS)
def test_parser_observations_have_no_review_or_audit_claims(key):
    d=adapter(key).parse(fixture(key))
    assert d['id']==IDS[key] and d['requirements']
    assert not {'last_verified','curriculum_audit','curriculum_status','verification_status'}&d.keys()
    with pytest.raises(ValueError):adapter(key).parse('<main><h1>Unrelated catalog</h1></main>')
    with pytest.raises(ValueError):adapter(key).parse('<h1>Sign in</h1><input type="password">'+fixture(key))


def test_northwestern_alternative_slots_and_topic_variants_are_distinct():
    d=adapter('northwestern').parse(fixture('northwestern'))
    assert len(d['courses'])==59
    calculus=next(r for r in d['requirements'] if 'nw-math-228-1' in r['course_ids'])
    assert calculus['count']==1 and set(calculus['course_ids'])=={'nw-math-228-1','nw-math-230-1'}
    elective=next(r for r in d['requirements'] if r['id']=='nw-electives')
    assert elective['count']==3 and elective['parent_id']=='nw-core'
    topics=[c for c in d['courses'] if c['code']=='COMP_SCI 396-0']
    assert len(topics)==3 and len({c['id'] for c in topics})==3
    assert any(c['name'].startswith('Synthetic course') for c in d['courses'])
    with pytest.raises(ValueError):adapter('northwestern').parse(fixture('northwestern').replace('3 upper level electives','three upper level electives'))


def test_emory_limits_to_ai_table_and_preserves_substitution():
    d=adapter('emory').parse(fixture('emory'))
    assert len(d['courses'])==10
    assert {r['count'] for r in d['requirements'] if r['kind']=='choose_courses'}=={1,2}
    g=next(r for r in d['requirements'] if r['id']=='emory-required-cs-110')
    assert set(g['course_ids'])=={'emory-cs-110','emory-cs-170'} and g['count']==1
    assert not any(c['code']=='CS 255' for c in d['courses'])
    with pytest.raises(ValueError):adapter('emory').parse_electives_text('AI Minor Electives\nchoose any two\nCS 441 incomplete')


def test_georgia_tech_prerequisite_not_counted_as_minor_core_and_no_guessed_credit():
    d=adapter('gatech').parse(fixture('gatech'))
    c=next(c for c in d['courses'] if c['code']=='CS 1331')
    assert c['credits'] is None
    choices=[g for g in d['requirements'] if g['kind']=='choose_courses']
    assert len(choices)==2 and all(g['count']==1 for g in choices)
    with pytest.raises(ValueError):adapter('gatech').parse(fixture('gatech').replace('Only CS courses','All departments'))


@pytest.mark.parametrize('key',IDS)
def test_curated_records_have_explicit_audits_and_registered_sources(key):
    d=json.loads((ROOT/'data/programs'/(IDS[key]+'.json')).read_text());validate_program(d)
    assert set(adapter(key).SOURCES)<={s['url'] for s in d['sources']}
    audit=d['curriculum_audit']
    assert audit['scope']=='minor' and audit['sections'] and audit['source_ids']
    assert bool(audit['unresolved_requirements'])==(d['curriculum_status']=='partial')
    if key in ('northwestern','emory'):assert d['curriculum_status']=='complete'
    else:assert d['curriculum_status']=='partial'
