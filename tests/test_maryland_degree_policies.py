from pathlib import Path
from bs4 import BeautifulSoup
import hashlib
import json
import pytest
from atlas.adapters import maryland_degree_policies as pol, maryland_course_metadata as meta
from atlas.adapters.maryland_ai_curricula import learning_outcomes
from atlas.db import validate_program

ROOT=Path(__file__).resolve().parents[1]
IDS=list(meta.TARGETS)


def test_metadata_restrictions_do_not_become_permission_waivers():
    html='<main><h1>CMSC - Computer Science</h1><div class="courseblock"><p class="courseblocktitle">CMSC999 Synthetic subject (3 Credits)</p><p class="courseblockextra"><strong>Prerequisite:</strong> Minimum C- in CMSC998.</p><p class="courseblockextra"><strong>Restriction:</strong> Department permission required.</p><p class="courseblockextra"><strong>Credit Only Granted for:</strong> CMSC999 or CMSC997.</p></div></main>'
    d=meta.parse(html,pid='synthetic',prefix='cmsc',codes=['CMSC999','CMSC996'])
    assert len(d['courses'])==1
    c=d['courses'][0]
    assert c['credits']==3 and c['description'] is None
    assert 'permission required' in c['prerequisites'] and 'Credit Only Granted for' in c['prerequisites']
    assert not {'curriculum_audit','curriculum_status','last_verified'} & d.keys()
    with pytest.raises(ValueError):meta.parse(html.replace('CMSC - Computer Science','Other listing'),pid='synthetic',prefix='cmsc',codes=['CMSC999'])


def test_variable_credits_and_generic_topic_are_not_promoted():
    html='<main><h1>CMSC - Computer Science</h1><div class="courseblock"><p class="courseblocktitle">CMSC498 Synthetic generic topics (1-6 Credits)</p></div></main>'
    d=meta.parse(html,pid='synthetic',prefix='cmsc',codes=['CMSC498'])
    assert d['courses'][0]['credits'] is None
    assert all('CMSC498' not in codes for groups in meta.TARGETS.values() for codes in groups.values())


def test_source_learning_outcomes_are_not_career_claims():
    rows=['human-facing disciplines','ethical, social, and cultural','biases, transparency, and accountability','technical reports','technical foundations']
    soup=BeautifulSoup('<h2>Program Learning Outcomes</h2><ol>'+''.join('<li>Synthetic '+x+'</li>' for x in rows)+'</ol>','html.parser')
    observed=learning_outcomes(soup,True,'source')
    assert len(observed)==5 and all(o['statement_type']=='learning_outcome' for o in observed)
    soup.find('li').decompose()
    with pytest.raises(ValueError):learning_outcomes(soup,True,'source')


@pytest.mark.parametrize('pid',IDS)
def test_curated_degree_scope_and_unknowns_remain_explicit(pid):
    d=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text())
    validate_program(d);assert d['curriculum_status']=='partial'
    assert len(d['outcomes'])==(5 if d['award_level']=='BA' else 6)
    rules={r['id']:r for r in d['requirements']}
    assert '40' in rules[pid+'-policy-gened-resources']['summary']
    if d['award_level']=='BA':
        assert rules[pid+'-policy-arhu-global-routes']['kind']=='alternative'
        assert rules[pid+'-policy-arhu-language']['parent_id']==pid+'-policy-arhu-global-routes'
        assert any('robots-disallowed' in g for g in d['curriculum_audit']['unresolved_requirements'])
        assert {c['code'] for c in d['courses']} >= {'MATH115','ARHU158'}
    else:
        assert any('12-credit' in g and '18-credit' in g for g in d['curriculum_audit']['unresolved_requirements'])
        assert 'does not list either AI degree' in rules[pid+'-closure-lep-scope']['summary']
        assert 'Computer Science gateway' in rules[pid+'-closure-lep-scope']['summary']


CASES=[]
for pid in IDS:
    cases=pol.parsers(pid,arhu='human-centered' in pid);cases.update(meta.parsers(pid))
    CASES.extend((pid,url,parse) for url,parse in cases.items())

@pytest.mark.parametrize('pid,url,parse',CASES)
def test_optional_actual_source_replay(pid,url,parse):
    p=ROOT/'.cache/http'/(hashlib.sha256(url.encode()).hexdigest()+'.body')
    if not p.exists():pytest.skip('Optional raw source cache')
    d=parse(p.read_text());assert d['id']==pid
    assert d.get('requirements') or d.get('courses')
    assert not {'curriculum_audit','curriculum_status','last_verified'} & d.keys()
