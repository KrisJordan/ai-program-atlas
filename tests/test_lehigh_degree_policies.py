import json
from pathlib import Path
import pytest
from atlas.adapters.lehigh_degree_policies import PID, PAGES, RULES, parse_policy, parse_engineering, parse_writing

@pytest.mark.parametrize('key',PAGES)
def test_lehigh_changed_material_rule_requires_review(key):
 html='<h1>'+PAGES[key][1]+'</h1>'+''.join('<p>'+p+'</p>' for _,_,phrases,_ in RULES[key] for p in phrases)
 result=parse_policy(html,key)
 assert 'curriculum_audit' not in result and result['curriculum_status']=='partial'
 for _,_,phrases,_ in RULES[key]:
  for phrase in phrases:
   with pytest.raises(ValueError,match='condition changed'):parse_policy(html.replace(phrase,'changed rule'),key)


def test_lehigh_writing_credits_prerequisites_are_observed():
 html='<h1>Writing (WRT)</h1>'
 for code in ['WRT 001','WRT 002','WRT 003','WRT 005']:
  desc='Prerequisites: WRT 001' if code=='WRT 002' else ''
  if code=='WRT 003':desc='Enrollment is limited to multilingual English speakers; English placement testing and ICAPE director’s recommendation determines placement.'
  html+=f'<div class="courseblock"><p class="courseblocktitle"><span class="cdspacing">{code}</span><span class="cdspacing">Example writing title</span> 3 Credits</p><p>{desc}</p></div>'
 observed=parse_writing(html)
 assert observed['courses'][1]['prerequisites']=='WRT 001'
 assert observed['courses'][0]['prerequisites'] is None
 assert parse_writing(html.replace('3 Credits','4 Credits'))['courses'][0]['credits']==4
 with pytest.raises(ValueError):parse_writing(html.replace('Enrollment is limited','Enrollment is not limited'))


def test_lehigh_seed_reconciles_titles_but_preserves_total_conflict():
 d=json.loads(Path('data/programs/'+PID+'.json').read_text());c={c['code']:c for c in d['courses']};r=d['requirements']
 assert c['ECO 001']['name']=='Principles of Economics'
 assert c['WRT 002']['name']=='Research and Argument'
 assert c['WRT 005']['prerequisites']=='WRT 003'
 assert all(c['credit_unit']=='semester_hours' for c in c.values())
 assert c['PHY 011']['credits'] is None
 assert any(x['kind']=='alternative' and x['course_ids']==['lehigh-wrt-001','lehigh-wrt-003'] for x in r)
 assert '130–131' in d['curriculum_audit']['unresolved_requirements'][0]
 assert '11 credits' in d['curriculum_audit']['unresolved_requirements'][0]
 assert d['curriculum_status']=='partial'


def test_lehigh_basic_hss_alternatives_cannot_silently_become_required():
 html='<h1>'+PAGES['engineering'][1]+'</h1>'+''.join('<p>'+p+'</p>' for _,_,phrases,_ in RULES['engineering'] for p in phrases)
 html+='<p>minimum of ten credit hours</p><h3>Basic Requirement</h3><table>'
 for code,name,credits,alt in [('ECO 001','Principles of Economics','4',False),('WRT 001','Academic and Analytical Writing','3',False),('WRT 003','Multilingual I','',True),('WRT 002','Research and Argument','3',False),('WRT 005','Multilingual II','',True)]:
  html+=f'<tr class="{"orclass" if alt else ""}"><td class="codecol"><a class="code">{code}</a></td><td>{name}</td><td class="hourscol">{credits}</td></tr>'
 html+='</table>'
 result=parse_engineering(html)
 assert result['courses'][2]['credits'] is None
 assert result['requirements'][-1]['credits']==10
 with pytest.raises(ValueError,match='alternatives changed'):parse_engineering(html.replace('class="orclass"','class=""'))
