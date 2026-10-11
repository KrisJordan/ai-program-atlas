"""Regressions for source-specific choices and independently reviewed core subjects."""
import json
from pathlib import Path
from bs4 import BeautifulSoup
import pytest
from atlas.adapters.degree_table_observations import Tables
from atlas.adapters.northwestern_degree_policies import parse_design_table, PID
from atlas.adapters.northwestern_degree_courses import parse_descriptions, classify_observed
from atlas.curriculum_profile import requirement_profile
from atlas.db import validate_program


def row(code,name):
 return f'<tr><td class="codecol"><a class="code" href="/synthetic">{code}</a></td><td>{name}</td></tr>'


def design_fixture():
 return BeautifulSoup('<table><tr><td>Writing and Design</td></tr>'+row('DSGN 106-1','Design Thinking and Communication')+'<tr><td>Innovation/Oral Communication</td></tr><tr><td>Select one of the following:</td></tr>'+row('COMM_ST 102-0','Public Speaking')+row('ENTREP 225-0','Principles of Entrepreneurship')+'</table>','html.parser').table


def test_explicit_unindented_choice_does_not_become_fixed():
 t=Tables('test','source','https://example.edu/')
 root=parse_design_table(t,design_fixture());groups={r['id']:r for r in t.rules}
 choice=next(r for r in t.rules if r['kind']=='alternative')
 assert choice['parent_id']==root['id']
 for r in t.rules:
  if r['course_ids']:
   assert r['parent_id']==(root['id'] if r['course_ids']==['test-dsgn-106-1'] else choice['id'])
 assert requirement_profile(dict(courses=list(t.courses.values()),requirements=t.rules))['required']['count']==1
 with pytest.raises(ValueError,match='operative policy'):
  parse_design_table(Tables('test','source','https://example.edu/'),BeautifulSoup(str(design_fixture()).replace('Select one','Select two'),'html.parser').table)


def test_english_half_units_are_observed_not_inferred():
 html='<h1>Academic Catalog</h1><h1>English (ENGLISH)</h1>'+''.join(f'<div class="courseblock"><p class="courseblocktitle">ENGLISH 106-{n} Writing in Special Contexts (0.5 Unit)</p><p class="courseblockdesc">Introduction to expository writing paired with another discipline.</p></div>'for n in [1,2])
 d=parse_descriptions(html,pid=PID,department='english')
 assert all(c['credits']==0.5 and c['category']=='human_context' for c in d['courses'])
 assert all('category_review' not in c for c in d['courses'])
 changed=parse_descriptions(html.replace('(0.5 Unit)','(1 Unit)'),pid=PID,department='english')
 assert all(c['credits']==1 for c in changed['courses'])
 with pytest.raises(ValueError,match='subject changed'):
  parse_descriptions(html.replace('expository writing','unspecified content'),pid=PID,department='english')
 with pytest.raises(ValueError,match='title changed'):
  classify_observed([dict(code='COMP_SCI 211-0',name='Unknown renamed subject',category='other')])


def test_current_seed_manual_fixed_set_and_mixed_design():
 p=json.loads(Path('data/programs',PID+'.json').read_text());validate_program(p)
 profile=requirement_profile(p)
 expected={'foundations':2,'mathematics':5,'ai_ml':2,'systems':0,'human_context':2,'applications':0,'electives':0,'other':2}
 assert profile['required']['count']==13 and profile['required']['categories']==expected
 # These seven are one source-defined choice, not mandatory cumulative courses.
 pool=['COMM_ST 102-0','ENTREP 225-0','ENTREP 325-0','PERF_ST 103-0','PERF_ST 203-0','PRDV 335-0','BMD_ENG 390-2']
 rules={r['id']:r for r in p['requirements']};byid={c['id']:c for c in p['courses']}
 for code in pool:
  cid=next(c['id']for c in p['courses']if c['code']==code)
  rule=next(r for r in p['requirements']if r['course_ids']==[cid]and r['source_id']==PID+'-college')
  assert rules[rule['parent_id']]['kind']=='alternative'
 for code in ['DSGN 106-1','DSGN 106-2']:
  c=next(c for c in p['courses']if c['code']==code)
  assert c['category']=='other' and c['category_review']['status']=='mixed'
  assert c['category_review']['candidate_categories']==['applications','human_context']
 assert next(c for c in p['courses']if c['code']=='COMP_SCI 211-0')['category']=='foundations'
 audit=json.loads(Path('research/degree-audit/northwestern.json').read_text())['programs'][0]
 assert audit['status']=='blocked' and len(audit['expected_course_ids']['required'])==13
 assert audit['blockers'] and not audit['remaining_work']


@pytest.mark.parametrize('dept',['comp_sci','gen_eng','dsgn','english'])
def test_optional_description_reread(dept):
 path=Path('/tmp/nw-audit-'+dept+'.html')
 if not path.exists():pytest.skip('Optional ignored source cache absent')
 d=parse_descriptions(path.read_text(),pid=PID,department=dept)
 assert d['courses'] and 'curriculum_audit' not in d
 assert all('category_review' not in c for c in d['courses'])
