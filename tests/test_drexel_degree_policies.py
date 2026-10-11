from pathlib import Path
import json
import pytest
from atlas.adapters.drexel_degree_policies import PID, PAGES, RULES, parse_policy, parse_wi

@pytest.mark.parametrize('key',PAGES)
def test_drexel_policy_material_change_requires_review(key):
 html='<h1>'+PAGES[key][1]+'</h1>'+''.join('<p>'+p+'</p>' for _,_,phrases,_ in RULES[key] for p in phrases)
 result=parse_policy(html,key)
 assert result['curriculum_status']=='partial'
 assert 'curriculum_audit' not in result
 for _,_,phrases,_ in RULES[key]:
  for phrase in phrases:
   with pytest.raises(ValueError,match='condition changed'):parse_policy(html.replace(phrase,'changed material rule'),key)


def test_drexel_wi_inventory_is_dated_and_dynamic():
 html='<h1>Writing Intensive Course List</h1><h3>List updated as of July 1, 2026</h3><table id="wi-courses"><tr><td>CI 491</td><td>Senior Project I</td><td>Computing</td></tr></table>'
 result=parse_wi(html)
 assert result['courses'][0]['code']=='CI 491'
 assert result['courses'][0]['credits'] is None
 assert 'not all required' in result['requirements'][0]['summary']
 assert parse_wi(html.replace('CI 491','CI 492'))['courses'][0]['code']=='CI 492'
 with pytest.raises(ValueError):parse_wi(html.replace('July 1, 2026','July 1, 2027'))


def test_drexel_seed_preserves_ambiguities_and_credit_scope():
 d=json.loads(Path('data/programs/'+PID+'.json').read_text());r={r['id']:r for r in d['requirements']}
 assert len(r[PID+'-policy-wi-options']['course_ids'])==205
 assert 'not course credits' in r[PID+'-policy-coopcredit-credit']['summary']
 assert 'prospective' in r[PID+'-policy-coopgrad-lastterm']['summary']
 assert not any(c['code']=='ECEC 455' for c in d['courses'])
 assert len({c['id'] for c in d['courses']})==len(d['courses'])
 assert any('SharePoint' in n or 'sharepoint' in n for n in d['curriculum_audit']['unresolved_requirements'])
 assert d['curriculum_status']=='partial'
