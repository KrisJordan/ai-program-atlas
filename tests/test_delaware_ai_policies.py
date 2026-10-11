import json
from pathlib import Path
import pytest
from atlas.adapters.delaware_ai_policies import *
@pytest.mark.parametrize('key',PAGES)
def test_delaware_changed_rules_require_review(key):
 html='<h1>'+PAGES[key][1]+'</h1>'+''.join('<p>'+p+'</p>' for _,_,phrases,_ in RULES[key] for p in phrases)
 assert parse_policy(html,key)['curriculum_status']=='partial'
 for _,_,phrases,_ in RULES[key]:
  for phrase in phrases:
   with pytest.raises(ValueError):parse_policy(html.replace(phrase,'changed'),key)
def test_delaware_partial_and_unknown_amounts_are_preserved():
 d=json.loads(Path('data/programs/'+PID+'.json').read_text())
 assert d['curriculum_status']=='partial'
 assert all(c['credits'] is None and c['credit_unit']=='semester_hours' for c in d['courses'])
 assert len([r for r in d['requirements'] if '-policy-' in r['id']])==11
 assert any('returned403' in s for s in d['curriculum_audit']['unresolved_requirements'])
 assert not any('CISC 106' in r['summary'] and 'C-' in r['summary'] for r in d['requirements'])
