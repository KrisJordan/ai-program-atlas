import json
from pathlib import Path
import pytest
from atlas.adapters.uva_ai_policies import *

def fixture(key):
 return '<h1>'+PAGES[key][1]+'</h1>'+''.join('<p>'+p+'</p>' for _,_,phrases,_ in RULES[key] for p in phrases)+'<p>College students must submit a form before they take it SEAS does not require anything in advance if the course is pre-approved SEAS has no restriction on allowing a course to count for two majors SEAS has no restriction on allowing a course to count for both a SEAS major and a minor</p>'
@pytest.mark.parametrize('key',PAGES)
def test_uva_changed_policy_is_not_silently_accepted(key):
 html=fixture(key);pid='uva-bacs-ai-concentration'
 assert parse_policy(html,pid,key)['curriculum_status']=='partial'
 for _,_,phrases,_ in RULES[key]:
  for phrase in phrases:
   with pytest.raises(ValueError):parse_policy(html.replace(phrase,'changed'),pid,key)
def test_uva_school_boundaries_are_explicit():
 ba=parse_policy(fixture('transfer'),'uva-bacs-ai-concentration','transfer')['requirements'][-1]
 bs=parse_policy(fixture('transfer'),'uva-bscs-ai-concentration','transfer')['requirements'][-1]
 assert 'before taking even' in ba['summary'] and 'does not require advance' in bs['summary']
 with pytest.raises(ValueError,match='not a BSCS'):parse_policy(fixture('college-minor'),'uva-bscs-ai-concentration','college-minor')
def test_uva_seed_keeps_new_overlap_ambiguity_and_partial_status():
 for stem in ['bacs','bscs']:
  d=json.loads(Path('data/programs/uva-'+stem+'-ai-concentration.json').read_text())
  assert d['curriculum_status']=='partial' and len(d['requirements'])==16
  conflict=any('exception has not been verified' in t for t in d['curriculum_audit']['unresolved_requirements'])
  assert conflict==(stem=='bacs')
