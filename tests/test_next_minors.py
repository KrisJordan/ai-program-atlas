"""Guard verified choices, policy boundaries and source-specific observations."""
import importlib.util
import json
from pathlib import Path
import pytest
from atlas.db import validate_program
ROOT=Path(__file__).resolve().parents[1]
CASES=[('minnesota-ai-ml-minor','minnesota',49),('clemson-university-artificial-intelligence-minor-minor','clemson',0),('florida-international-university-artificial-intelligence-minor-minor','fiu',8),('stevens-institute-of-technology-artificial-intelligence-minor-minor','stevens',19)]
def adapter(pid):
 spec=importlib.util.spec_from_file_location('a',ROOT/'atlas/adapters'/pid/'adapter.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);return a

def seed(pid):return json.loads((ROOT/'data/programs'/(pid+'.json')).read_text())
def fixture(key):return (ROOT/'tests/fixtures/next_minors'/(key+'.html')).read_text()

@pytest.mark.parametrize('pid,key,count',CASES)
def test_seeds_have_scoped_audits_and_valid_sources(pid,key,count):
 d=seed(pid);validate_program(d);assert len(d['courses'])==count
 if key=='minnesota':assert d['curriculum_status']=='complete' and not d['curriculum_audit']['unresolved_requirements']
 else:assert d['curriculum_status']=='partial' and d['curriculum_audit']['unresolved_requirements']
 assert d['first_offered'] is None

@pytest.mark.parametrize('pid,key,count',CASES)
def test_adapters_never_certify_or_replay_reviewed_inventory(pid,key,count):
 a=adapter(pid);o=a.parse(fixture(key));assert o['curriculum_status']=='partial'
 assert 'curriculum_audit' not in o and 'last_verified' not in o
 with pytest.raises(ValueError):a.parse('<h1>Different program</h1>')

def test_minnesota_preserves_alternatives_and_open_elective():
 pid,key,_=CASES[0];a=adapter(pid);html=fixture(key);o=a.parse(html)
 assert [len(r['course_ids']) for r in o['requirements']]==[2,1,2,1,6,8,29]
 changed=a.parse(html.replace('Introduction to Computing and Programming Concepts','Revised Programming Title',1).replace('(2 credit)','(3 credit)',1))
 assert changed['courses'][0]['name']=='Revised Programming Title'
 assert changed['courses']!=o['courses']
 with pytest.raises(ValueError):a.parse(html.replace('Minor Electives','Electives changed'))
 d=seed(pid);assert all(c['credit_unit']=='semester_hours' for c in d['courses'])
 parent=next(r for r in d['requirements'] if r['id'].endswith('-elective-route'))
 children=[r for r in d['requirements'] if r['parent_id']==parent['id']]
 assert parent['kind']=='alternative' and {r['kind'] for r in children}=={'note','choose_courses'}
 assert d['status']=='announced'

def test_fiu_conflicting_course_is_not_added_to_catalog_choice():
 pid,key,_=CASES[2];o=adapter(pid).parse(fixture(key));assert len(o['courses'])==6
 d=seed(pid);code={c['id']:c['code'] for c in d['courses']}
 choice=next(r for r in d['requirements'] if r['id'].endswith('-ml-listed'))
 assert {code[c] for c in choice['course_ids']}=={'CNT 4153','CAI 4105'}
 conflict=next(r for r in d['requirements'] if r['id'].endswith('-ml-disagreement'))
 assert conflict['kind']=='note' and [code[c] for c in conflict['course_ids']]==['CAP 4612']
 assert any('GPA 3.0' in r['summary'] for r in d['requirements'])
 assert any(code.get(c)=='IDC 2002' for r in d['requirements'] for c in r['course_ids'])
 changed=adapter(pid).parse(fixture(key).replace('CAP 4612','CAP 4999'))
 assert 'CAP 4999' in [c['code'] for c in changed['courses']]

def test_stevens_branches_keep_counts_crosslisting_and_overlap_separate():
 pid,key,_=CASES[3];d=seed(pid);req={r['id']:r for r in d['requirements']}
 assert req[pid+'-cs-electives']['count']==2 and len(req[pid+'-cs-electives']['course_ids'])==10
 assert req[pid+'-other-electives']['count']==1 and len(req[pid+'-other-electives']['course_ids'])==12
 assert req[pid+'-other-discrete']['count']==1 and len(req[pid+'-other-discrete']['course_ids'])==2
 assert sum(c['code']=='CS 558 / CPE 558' for c in d['courses'])==1
 o=adapter(pid).parse(fixture(key).replace('four of the six','three of the six'))
 assert 'up to 3' in o['requirements'][0]['summary']
 assert 'courses' not in o # unresolved server IDs must never become course identities

def test_clemson_observes_minimum_without_inventing_catalog_courses():
 pid,key,_=CASES[1];o=adapter(pid).parse(fixture(key).replace('24 credits','27 credits'))
 assert o['requirements'][0]['credits']==27 and o['courses']==[]
 assert o['requirements'][0]['credit_unit']=='unknown'
