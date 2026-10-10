"""W&M partial curricula preserve unknowns, source boundaries and policy changes."""
import importlib
import hashlib
import json
from pathlib import Path
import pytest
from atlas.adapters import william_mary_curricula as w
from atlas.db import validate_program
ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/'tests/fixtures/william_mary'


def fixture(name):return (FIX/(name+'.html')).read_text()


def test_ds_specialization_only_uses_ai_row_and_preserves_choose_rule():
    result=w.declaration(fixture('ds_declaration'),'william-mary-data-science-ai-specialization')
    assert [c['code'] for c in result['courses']]==['DATA 440','DATA 441','DATA 442','DATA 446','DATA 447','DATA 448']
    assert all(c['credits'] is None and c['description'] is None for c in result['courses'])
    assert result['requirements'][0]['count']==3
    assert result['requirements'][0]['kind']=='choose_courses'
    changed=fixture('ds_declaration').replace('DATA 448 (Reinforcement Learning)','DATA 499 (New course)')
    assert w.declaration(changed,'william-mary-data-science-ai-specialization')['courses'][-1]['code']=='DATA 499'


def test_ba_core_is_only_what_faq_states_and_is_not_full_degree():
    result=w.ba_overview(fixture('ba'))
    assert [c['code'] for c in result['courses']]==['DATA 201','DATA 202','DATA 305']
    assert result['requirements'][0]['credits']==30
    assert 'degree total' in result['requirements'][0]['summary']
    assert result['courses'][-1]['name']=='Designing AI Agents'


@pytest.mark.parametrize('name,parse',[('minor',w.ai_minor),('cs',w.cs_concentration),('ds',w.ds_overview),('ba',w.ba_overview),('ds_declaration',lambda h:w.declaration(h,'william-mary-data-science-ai-specialization')),('ba_declaration',lambda h:w.declaration(h,'william-mary-applied-ai-ba',True))])
def test_access_identity_and_no_review_state(name,parse):
    result=parse(fixture(name))
    assert not {'curriculum_status','curriculum_audit','last_verified'} & result.keys()
    for html in ('<main><h1>Unrelated</h1></main>','<title>Sign in</title>'+fixture(name),'<nav>'+fixture(name).replace('<main>','').replace('</main>','')+'</nav><main><h1>Unrelated</h1></main>'):
        with pytest.raises(ValueError):parse(html)


@pytest.mark.parametrize('old,new',[('three elective courses','four elective courses'),('maximum of 54','maximum of 60'),('Artificial Intelligence</td>','Other</td>')])
def test_ds_changed_material_rule_rejected(old,new):
    with pytest.raises(ValueError):w.declaration(fixture('ds_declaration').replace(old,new),'william-mary-data-science-ai-specialization')


def test_minor_credit_observation_is_extracted():
    assert w.ai_minor(fixture('minor').replace('19 credits','21 credits'))['requirements'][0]['credits']==21


def test_data_policy_change_is_not_silently_replayed():
    with pytest.raises(ValueError):w.ds_overview(fixture('ds').replace('must receive pre-approval','need not receive pre-approval'))


@pytest.mark.parametrize('pid',['william-mary-ai-minor','william-mary-cs-ai-ml-concentration','william-mary-data-science-ai-specialization','william-mary-applied-ai-ba'])
def test_curated_seed_and_optional_cached_live_evidence(pid):
    data=json.loads((ROOT/'data/programs'/(pid+'.json')).read_text());validate_program(data)
    assert data['curriculum_status']=='partial' and data['curriculum_audit']['unresolved_requirements']
    adapter=importlib.import_module('atlas.adapters.'+pid+'.adapter')
    for url in adapter.SOURCES:
        cached=ROOT/'.cache/http'/(hashlib.sha256(url.encode()).hexdigest()+'.body')
        if not cached.exists():continue
        result=getattr(adapter,'SOURCE_PARSERS',{}).get(url,adapter.parse)(cached.read_text())
        assert result['id']==pid
        assert not {'curriculum_status','curriculum_audit','last_verified'} & result.keys()
