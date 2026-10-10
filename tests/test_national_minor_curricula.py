"""Requirements parsers must observe source structure and preserve alternatives."""
import importlib
import json
from pathlib import Path
import pytest
from atlas.db import validate_program
ROOT=Path(__file__).resolve().parents[1]
FIXTURES=ROOT/'tests/fixtures/national_minors'
IDS={'gatech':'georgia-institute-of-technology-computing-and-artificial-intelligence-minor-minor','cornell':'cornell-university-artificial-intelligence-minor-minor','northwestern':'northwestern-university-artificial-intelligence-minor-minor-minor','emory':'emory-university-artificial-intelligence-minor-minor'}
IDS.update({'tamu':'texas-am-ai-business-minor','scu':'santa-clara-responsible-ai-minor','gatech-apps':'georgia-institute-of-technology-applications-of-artificial-intelligence-and-machine-learning-minor-minor'})
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
    if key in ('northwestern','emory','tamu','scu'):assert d['curriculum_status']=='complete'
    else:assert d['curriculum_status']=='partial'


def test_santa_clara_whole_foundations_and_credit_electives():
    d=adapter('scu').parse(fixture('scu'))
    assert len(d['courses'])==46
    foundation=next(g for g in d['requirements'] if g['id']=='scu-foundation')
    assert foundation['kind']=='alternative'
    assert len([g for g in d['requirements'] if g['parent_id']==foundation['id']])==3
    math=next(g for g in d['requirements'] if g['course_ids']==['scu-amath-108','scu-math-122'])
    assert math['parent_id']=='scu-option-a' and math['count']==1
    electives=next(g for g in d['requirements'] if g['id']=='scu-electives')
    assert electives['kind']=='choose_credits' and electives['credits']==4 and len(electives['course_ids'])==28
    assert next(c for c in d['courses'] if c['code']=='CSCI 62')['credits'] is None
    with pytest.raises(ValueError):adapter('scu').parse(fixture('scu').replace('Option C:','Unknown option:'))


def test_tamu_observes_course_rows_and_policies():
    d=adapter('tamu').parse(fixture('tamu'))
    assert len(d['courses'])==5 and sum(c['credits'] for c in d['courses'])==15
    assert all(c['name'].startswith('Synthetic course') for c in d['courses'])
    with pytest.raises(ValueError):adapter('tamu').parse(fixture('tamu').replace('overall GPA of 3.00','overall GPA of 2.50'))


def test_applications_minor_requires_four_whole_tracks_and_named_topics():
    d=adapter('gatech-apps').parse(fixture('gatech-apps'))
    tracks=[g for g in d['requirements'] if g['parent_id']=='gt-apps-tracks']
    assert len(tracks)==4 and all(g['credits']==15 for g in tracks)
    assert len([g for g in d['requirements'] if g['id'].endswith('-electives')])==4
    assert len([c for c in d['courses'] if c['code']=='MGT 4803'])==3
    assert not any('XXXX' in c['code'] for c in d['courses'])
    assert all(g['count']==2 for g in d['requirements'] if g['id'].endswith('-electives'))


def test_tamu_rejects_changed_credit_eligibility_even_when_gpa_is_unchanged():
    with pytest.raises(ValueError):
        adapter('tamu').parse(fixture('tamu').replace('completed 24 credit hours','completed 30 credit hours'))
