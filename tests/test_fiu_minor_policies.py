import json
from pathlib import Path
import pytest
from atlas.adapters.fiu_minor_policies import *

def test_fiu_changed_minor_conditions_require_review():
 html='<h1>Minor and Certificate Programs</h1>'+''.join('<p>'+p+'</p>' for _,_,phrases,_ in RULES for p in phrases)
 assert len(parse_policy(html)['requirements'])==3
 for _,_,phrases,_ in RULES:
  for phrase in phrases:
   with pytest.raises(ValueError,match='condition changed'):parse_policy(html.replace(phrase,'changed'))

def test_fiu_course_credit_and_prerequisite_changes_require_review():
 html='<h1>CAI4105</h1><p>Introduction to Machine Learning classification, clustering, structured models and recommendation system STA 3033 or STA 2122 or STA 3145 or STA 3193 or STA 3163 or STA 3111 or STA 2023 or STA 4322 Minimum Credits 3 Maximum Credits 3 Repeat for Credit No</p>'
 c=parse_course(html)['courses'][0]
 assert c['credits']==3 and c['credit_unit']=='unknown'
 assert 'STA 4322' in c['prerequisites']
 for old,new in [('Minimum Credits 3','Minimum Credits 4'),('STA 4322','STA 4323')]:
  with pytest.raises(ValueError):parse_course(html.replace(old,new))

def test_fiu_conflicting_course_is_not_silently_approved():
 d=json.loads(Path('data/programs/'+PID+'.json').read_text())
 choice=next(r for r in d['requirements'] if r['id']==PID+'-ml-listed')
 assert PID+'-cai-4105' in choice['course_ids'] and PID+'-cap-4612' not in choice['course_ids']
 assert d['curriculum_status']=='partial'
 assert len([r for r in d['requirements'] if '-policy-' in r['id']])==3
