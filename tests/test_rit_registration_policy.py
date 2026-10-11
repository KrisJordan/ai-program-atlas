import json
from pathlib import Path
import pytest
from atlas.adapters.rit_policies import parse_policy, SPECS
from atlas.curriculum_profile import requirement_profile

PID='rochester-institute-of-technology-artificial-intelligence-bs-degree'

def test_registration_observation_detects_changes_without_granting_waivers():
    title,headings=SPECS['d030']
    html=f'<h1>{title}</h1>'+''.join(f'<section><h2>{h}</h2><p>Synthetic lengthy section for source observation; approval remains conditional.</p></section>' for h in headings)
    result=parse_policy(html,pid=PID,code='d030')
    assert len(result['observed_policy_sections'])==4
    assert result['requirements']==[] and result['courses']==[]
    assert 'curriculum_audit' not in result
    changed=parse_policy(html.replace('approval','permission'),pid=PID,code='d030')
    assert changed['observed_policy_sections']!=result['observed_policy_sections']
    with pytest.raises(ValueError,match='section missing'):
        parse_policy(html.replace(headings[0],'Changed heading'),pid=PID,code='d030')

def test_conditional_registration_does_not_change_course_roles():
    p=json.loads(Path('data/programs',PID+'.json').read_text())
    profile=requirement_profile(p)
    assert [profile[k]['count'] for k in ['required','options','unresolved']]==[23,476,14]
    rules=[r for r in p['requirements'] if r['source_id']=='rit-policy-d030']
    assert len(rules)==3 and all(r['kind']=='note' and not r['course_ids'] for r in rules)
    assert 'both home and offering departments approve' in rules[0]['summary']
    assert 'not granted waivers' in rules[0]['summary']
    courses={c['code']:c for c in p['courses']}
    assert courses['EEEE-485']['prerequisites']=='EEEE-346 or equivalent.'
