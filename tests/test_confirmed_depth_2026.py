"""Synthetic requirement structures; examples are not copied catalog passages."""
import importlib.util
import json
from pathlib import Path
import pytest
from atlas import db
from atlas.adapters import northwestern_second_majors as nw, stanford_symsys_concentrations as sy
ROOT=Path(__file__).resolve().parents[1]
PIDS=[x[0] for x in nw.CONFIG.values()]+[x[0] for x in sy.CONFIG.values()]+['rice-ece-ai-systems-specialization']
def adapter(pid):
 spec=importlib.util.spec_from_file_location(pid.replace('-','_'),ROOT/'atlas/adapters'/pid/'adapter.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);return a
def document(route):
 title=('Human-Centered ' if route=='hai' else '')+'Artificial Intelligence Concentration'
 text='# '+title+'\n\nUpdated September 27, 2024\n3 units; 5 courses beyond the Core; Junior Year; Core Capstone; requires a Stanford login; urged to take CS 161\n'
 for i,h in enumerate(sy.HEADINGS[route],1):
  condition='Two courses chosen' if h=='Artificial Intelligence Depth' else 'One course aimed' if h in ['Human Impact','Augmenting Human Capabilities','Intelligence'] else 'One of the following' if h in ['Programming','Digital Technology Ethics and Policy'] else 'Must be completed no earlier than the Junior Year' if h=='Integrative Requirement' else ''
  text+=f'\n{i}. ***{h}***. '+condition+' '+('For example:' if h in ['Human Impact','Augmenting Human Capabilities'] else '')+'\n   * CS '+str(100+i)+': Synthetic Course '+str(i)+'\n'
 text+='   * The combination of SYMSYS 176S and OSPGEN 47 (both classes must be completed)\n'
 return text
@pytest.mark.parametrize('route',['ai','hai'])
def test_public_document_dynamic_courses_and_conditions(route):
 text=document(route);r=sy.parse_document(text,route)
 assert any(c['name']=='Synthetic Course 1' for c in r['courses'])
 assert all(c['credits'] is None for c in r['courses'])
 bundle=next(x for x in r['requirements'] if x['title'].startswith('Combined contingent'))
 assert len(bundle['course_ids'])==2 and bundle['kind']=='all'
 assert not {'curriculum_status','curriculum_audit','last_verified'} & r.keys()
 changed=sy.parse_document(text.replace('CS 101: Synthetic Course 1','CS 199: New Evidence'),route)
 assert any(c['code']=='CS 199' and c['name']=='New Evidence' for c in changed['courses'])
 assert not any(c['code']=='CS 101' for c in changed['courses'])
 if route=='hai':assert next(x for x in r['requirements'] if x['title']=='Human Impact')['kind']=='note'
@pytest.mark.parametrize('marker',['Updated September 27, 2024','requires a Stanford login','Core Capstone','5 courses beyond','Junior Year'])
def test_changed_document_policy_rejected(marker):
 with pytest.raises(ValueError):sy.parse_document(document('ai').replace(marker,'changed'),'ai')
@pytest.mark.parametrize('route',['ai','hai'])
def test_stanford_exact_heading_and_document_link(route):
 _,title,_,doc=sy.CONFIG[route]
 html=f'<main><h1>{title}</h1><p>G4 Fall of 2020 3 units</p><a href="{doc}">requirements</a></main>'
 assert sy.parse(html,route)['program_kind']=='concentration'
 with pytest.raises(ValueError):sy.parse(html.replace('<h1>','<h2>').replace('</h1>','</h2>'),route)
 with pytest.raises(ValueError):sy.parse('<h1>Sign in</h1>'+html,route)
 with pytest.raises(ValueError):sy.parse(html.replace(doc,'https://example.invalid/'),'ai')
def table(code='COMP_SCI 111-0'):
 return f'<table class="sc_courselist"><tbody><tr><td class="codecol"><a class="code" href="/course/">{code}</a></td><td>Observed course</td><td class="hourscol"></td></tr></tbody></table>'
def nw_fixture(route):
 title=nw.CONFIG[route][1]
 common='one course in five of the six categories; six technical electives; Any 300- or 400-level COMP_SCI course; Undergraduate Registration Requirement; degree requirements of their home school'
 special='AI Major Program (22 units); 6 required courses; 4 advanced elective courses; Any 300-level or higher class; Scores of 4 or 5 on the AP CS A; scores of 5, 6, or 7 on the IB CS HL; introductory courses that directly support computer science (MATH 101)' if route=='mccormick' else 'Program Courses (19 units); 7 required courses; Weinberg College prohibits double-counting; Weinberg College allows double-counting a related course; A single course does not satisfy more than one requirement; STAT 202-0 is not accepted'
 return '<main><h1>'+title+'</h1><p>'+common+'; '+special+'</p>'+''.join(table('COMP_SCI '+str(110+i)+'-0') for i in range(9 if route=='mccormick' else 11))+'</main>'
@pytest.mark.parametrize('route',['mccormick','non-mccormick'])
def test_northwestern_route_scoping_and_open_electives(route):
 html=nw_fixture(route);r=nw.parse(html,route)
 assert r['award_level']=='other' and r['program_kind']=='additional_major'
 assert next(x for x in r['requirements'] if x['title']=='Five distinct breadth domains')['count']==5
 assert next(x for x in r['requirements'] if x['title']=='Technical electives: displayed additional pool')['kind']=='note'
 assert next(x for x in r['requirements'] if x['title']=='Six technical electives with open eligibility')['count']==6
 with pytest.raises(ValueError):nw.parse(html.replace('one course in five of the six categories','changed selection'),route)
 with pytest.raises(ValueError):nw.parse(html.replace('<h1>','<h2>').replace('</h1>','</h2>'),route)
 assert any(c['code']=='COMP_SCI 999-0' for c in nw.parse(html.replace('COMP_SCI 110-0','COMP_SCI 999-0'),route)['courses'])
def test_rice_noncredential_policy_rejects_contrary_evidence():
 a=adapter(PIDS[-1]);html='<main><h1>Majors, Minors, and University Certificates</h1><p>area of specialization; not an official academic credential; will not appear on the transcript; during or before the spring semester of their second year; any academic year between their matriculation and graduation; may not declare a catalog year in the future; signature of the advisor and/or department chair; not required to drop or change</p></main>'
 r=a.parse_registrar(html);assert 'not an official academic credential' in r['requirements'][0]['summary']
 with pytest.raises(ValueError):a.parse_registrar(html.replace('will not appear on the transcript','will appear on the transcript'))
@pytest.mark.parametrize('pid',PIDS)
def test_reviewed_seed_and_registered_refresh_sources(pid):
 p=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text());db.validate_program(p)
 assert p['curriculum_status']==('complete' if pid=='rice-ece-ai-systems-specialization' else 'partial')
 assert bool(p['curriculum_audit']['unresolved_requirements']) == (p['curriculum_status']=='partial')
 assert p['first_offered'] is None
 a=adapter(pid);assert set(a.SOURCES)<={s['url'] for s in p['sources']}
 assert all(r['source_id'] in {s['id'] for s in p['sources']} for r in p['requirements'])
 assert not p['outcomes']
@pytest.mark.parametrize('pid',PIDS)
def test_cached_http_observations_never_confer_review(pid):
 import hashlib
 a=adapter(pid)
 for url,parse in a.SOURCE_PARSERS.items():
  path=ROOT/'.cache/http'/(hashlib.sha256(url.encode()).hexdigest()+'.body')
  if not path.exists():pytest.skip('Optional live public source cache unavailable')
  r=parse(path.read_text());assert r['id']==pid
  assert not {'curriculum_status','curriculum_audit','last_verified'} & r.keys()


def test_stanford_changed_depth_count_is_not_silently_replayed():
 with pytest.raises(ValueError):sy.parse_document(document('ai').replace('Two courses chosen','Three courses chosen'),'ai')

def test_rice_merged_pools_keep_crosslist_as_one_option():
 from bs4 import BeautifulSoup
 from atlas.adapters.degree_table_observations import Tables
 a=adapter(PIDS[-1])
 html='<table><tr><td class="codecol"><a class="code" href="/a">ELEC 440</a> / <a class="code" href="/b">COMP 440</a></td><td>Observed AI class</td></tr></table>'
 table1=BeautifulSoup(html,'html.parser').table
 merged=a.merged([table1,table1]);assert len(merged.select('tr'))==1
 t=Tables('synthetic','catalog','https://example.invalid/')
 t.table(merged,'Choose one',kind='choose_courses',count=1,interpret_choices=False)
 option=t.rules[1];assert option['kind']=='choose_courses' and option['count']==1 and len(option['course_ids'])==2


@pytest.mark.parametrize('key',['graduation','transfer','grades','registration'])
def test_rice_policy_changed_material_condition_rejected(key):
 a=adapter('rice-ece-ai-systems-specialization');_,heading,specs=a.POLICIES[key]
 html='<main><h1>'+heading+'</h1><p>'+'; '.join(marker for _,markers,_ in specs for marker in markers)+'</p></main>'
 r=a.parse_policy(html,key);assert len(r['requirements'])==len(specs)
 assert not {'curriculum_status','curriculum_audit','last_verified'} & r.keys()
 with pytest.raises(ValueError):a.parse_policy(html.replace(specs[0][1][0],'changed condition'),key)
