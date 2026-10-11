import json
from pathlib import Path
import pytest
from atlas.adapters.ncsu_ai_policies import *
@pytest.mark.parametrize('key',PAGES)
def test_ncsu_material_policy_changes_fail(key):
 html='<h1>'+PAGES[key][1]+'</h1>'+''.join('<p>'+p+'</p>' for _,_,phrases,_ in RULES[key] for p in phrases)
 assert parse_policy(html,key)['curriculum_status']=='partial'
 for _,_,phrases,_ in RULES[key]:
  for phrase in phrases:
   with pytest.raises(ValueError):parse_policy(html.replace(phrase,'changed'),key)
def test_ncsu_dsa_identity_and_credit_guard():
 html='<h1>Data Science (DSA)</h1>'+''.join(f'<div class="courseblock"><span class="detail-coursecode">DSA {n}</span><span class="detail-title">Example</span><span class="detail-hours_html">(1 credit hours)</span><p class="courseblockextra">Example description. Prerequisite skills and knowledge: Python.</p></div>' for n in ['405','406','412','435'])
 assert len(parse_dsa(html)['courses'])==4
 with pytest.raises(ValueError):parse_dsa(html.replace('DSA 405','DSC 405'))
 with pytest.raises(ValueError):parse_dsa(html.replace('(1 credit hours)','(3 credit hours)'))
def test_ncsu_seed_preserves_grade_and_special_topic_uncertainty():
 d=json.loads(Path('data/programs/'+PID+'.json').read_text())
 assert d['curriculum_status']=='partial'
 assert len(d['requirements'])==20
 assert any('C-minus' in s for s in d['curriculum_audit']['unresolved_requirements'])
 assert all(c['source_id']==PID+'-dsa-courses' for c in d['courses'] if c['code'].startswith('DSA '))
 assert not any(c['code']=='CSC 495' for c in d['courses'])
