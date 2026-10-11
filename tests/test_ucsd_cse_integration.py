"""Reviewed CSE observations augment the existing source without changing roles."""
import importlib
import json
from pathlib import Path
import pytest
from atlas.curriculum_profile import requirement_profile

PID='university-of-california-san-diego-artificial-intelligence-bs-degree'
adapter=importlib.import_module('atlas.adapters.'+PID+'.adapter')


def test_composition_keeps_core_and_requirement_observations(monkeypatch):
    original={'id':PID,'courses':[{'id':'ucsd-cse-12','code':'CSE 12','name':'Core'}, {'id':'ucsd-cse-11','code':'CSE 11','category':'other'}], 'requirements':[{'id':'tag-rule'}]}
    monkeypatch.setattr(adapter,'_previous_cse_parser',lambda html:original)
    monkeypatch.setattr(adapter.remaining_cse,'parse_observations',lambda html:{'id':PID,'courses':[{'id':'ucsd-cse-11','code':'CSE 11','category':'foundations','description':'Reviewed programming'}]})
    result=adapter.parse_all_reviewed_cse('synthetic source')
    assert result['requirements']==original['requirements']
    assert result['courses'][0]==original['courses'][0]
    assert result['courses'][1]['category']=='foundations'
    assert original['courses'][1]['category']=='other'
    assert all('category_review'not in c for c in result['courses'])


def test_handoff_cannot_overwrite_previously_reviewed_core(monkeypatch):
    monkeypatch.setattr(adapter,'_previous_cse_parser',lambda html:{'courses':[],'requirements':[]})
    monkeypatch.setattr(adapter.remaining_cse,'parse_observations',lambda html:{'courses':[{'id':'ucsd-cse-12','code':'CSE 12'}]})
    with pytest.raises(ValueError,match='overlaps core'):adapter.parse_all_reviewed_cse('synthetic')


def test_seed_preserves_roles_missing_codes_and_conditional_restrictions():
    d=json.loads(Path('data/programs',PID+'.json').read_text());courses={c['code']:c for c in d['courses']}
    profile=requirement_profile(d)
    assert [profile[k]['count']for k in ['required','options','unresolved']]==[8,119,2240]
    assert courses['CSE 20']['category']=='mathematics'
    assert courses['CSE 105']['category']=='foundations'
    assert courses['CSE 193']['category_review']['status']=='unclassified'
    assert courses['CSE 154']['description'] is None
    assert 'Not for students who plan to study AI' in courses['CSE 5']['prerequisites']
    assert 'two units of credit' in courses['CSE 29']['prerequisites']
    assert courses['CSE 29']['credits']==4
    assert courses['CSE 90']['prerequisites'] is None
    assert courses['CSE 15L']['credits']==2 and courses['CSE 170']['credits']==5


def test_registered_source_replay_retains_tags_core_and_new_reviews():
    path=Path('.cache/http/02421735947aad7739f42482f2448cb91ce18e810264063f4b601113ac4d93d4.body')
    if not path.exists():pytest.skip('Optional private source cache')
    result=adapter.SOURCE_PARSERS[adapter.COURSE_URL](path.read_text())
    assert result==adapter.SOURCE_PARSERS[adapter.COURSE_URL](path.read_text())
    c={c['code']:c for c in result['courses']}
    assert result['requirements']
    assert c['CSE 12']['credits']==4
    assert c['CSE 20']['category']=='mathematics'
    assert c['CSE 127']['category']=='systems'
    assert c['CSE 151B']['category']=='ai_ml'
    assert all('category_review'not in c for c in result['courses'])


def test_core_prerequisite_suffixes_do_not_drop_permissions_or_credit_rules():
    d=json.loads(Path('data/programs',PID+'.json').read_text());c={x['code']:x for x in d['courses']}
    assert 'All other students will be allowed as space permits' in c['CSE 55']['prerequisites']
    assert 'Students may receive credit for one' in c['CSE 25']['prerequisites']
    assert 'not a prerequisite' in c['CSE 100']['prerequisites']
    assert 'COGS 188' in c['CSE 151A']['prerequisites']
    assert 'Graduate students will be allowed as space permits' in c['CSE 12']['prerequisites']
