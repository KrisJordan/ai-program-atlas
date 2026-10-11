import json
from pathlib import Path
import pytest
from atlas.adapters.njit_degree_policies import PID, POOLS, GER_RULES, POLICY_RULES, parse_pool, parse_rules


def test_njit_pool_extracts_changed_options_and_preserves_blank_credits():
 html='<h1>History and Humanities GER 200 level</h1><table class="sc_courselist"><tr><td class="codecol">HIST 2**</td><td>History elective</td><td></td></tr><tr><td class="codecol">COM 200</td><td>Communicating in Organizations</td><td></td></tr></table>'
 result=parse_pool(html,'njit-ger-200')
 assert [c['code'] for c in result['courses']]==['COM 200']
 assert result['courses'][0]['credits'] is None
 assert 'HIST 2**' in result['requirements'][0]['summary']
 assert result['requirements'][0]['kind']=='choose_credits'
 assert result['requirements'][0]['credit_unit']=='semester_hours'
 changed=parse_pool(html.replace('COM 200','COM 201'),'njit-ger-200')
 assert changed['courses'][0]['code']=='COM 201'
 assert 'curriculum_audit' not in result and 'last_verified' not in result


@pytest.mark.parametrize('kind,rows',[('ger',GER_RULES),('policies',POLICY_RULES)])
def test_njit_changed_material_policy_fails_review(kind,rows):
 heading='General Education Requirements' if kind=='ger' else 'Academic Policies and Procedures'
 html='<h1>'+heading+'</h1>'+''.join('<p>'+phrase+'</p>' for _,_,phrases,_ in rows for phrase in phrases)
 assert len(parse_rules(html,kind)['requirements'])==len(rows)
 for _,_,phrases,_ in rows:
  with pytest.raises(ValueError,match='condition changed'):
   parse_rules(html.replace(phrases[0],'changed rule'),kind)


def test_njit_seed_explicit_pools_no_duplicate_required_course():
 d=json.loads(Path('data/programs/'+PID+'.json').read_text());courses={c['id']:c for c in d['courses']};rules={r['id']:r for r in d['requirements']}
 assert len(courses)==len(d['courses'])
 assert len(rules[PID+'-njit-ger-300']['course_ids'])==248
 assert len(rules[PID+'-njit-natural']['course_ids'])==36
 assert courses['njit-r216-206']['credits']==3
 assert courses['njit-com-200']['credits'] is None
 assert courses['njit-phil-310']['source_id']==PID+'-courses-humanities'
 # Description enrichment preserves the same required identity and its plan provenance.
 assert any('njit-phil-310' in r['course_ids'] and r['source_id']==PID+'-official' for r in d['requirements'])
 assert 'njit-phil-310' in rules[PID+'-njit-ger-300']['course_ids']
 assert not any('*' in c['code'] for c in courses.values())
 assert d['curriculum_status']=='partial' and d['curriculum_audit']['unresolved_requirements']


def test_degree_pool_profile_preserves_fixed_overlap_and_open_predicates():
 from atlas.curriculum_profile import requirement_profile
 d=json.loads(Path('data/programs/'+PID+'.json').read_text())
 profile=requirement_profile(d)
 assert [profile[k]['count'] for k in ('required','options','unresolved')]==[32,349,0]
 # Four published code pools contain 350 records, with prescribed PHIL310
 # already fixed. This does not authorize using PHIL310 for two credit slots.
 assert sum(len(r['course_ids']) for r in d['requirements'] if r['id'] in {PID+'-'+k for k in POOLS})==350
 assert all(c['credit_unit']=='semester_hours' for c in d['courses'])
 assert any(s['id']==PID+'-credit-definition' and s['source_date'] is None for s in d['sources'])
 assert any('PHIL 310' in q for q in d['curriculum_audit']['unresolved_requirements'])
