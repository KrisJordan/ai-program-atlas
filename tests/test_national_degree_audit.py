"""Independent source-derived role and subject checks for the national degree batch."""
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path
import pytest
from atlas.curriculum_profile import requirement_profile
from atlas.adapters import lehigh_degree_courses as lehigh

LEHIGH=lehigh.PID
# Hand enumeration of the prescribed rows, excluding every printed OR/pool.
LEHIGH_REQUIRED={
 'CSE 012','CSE 027','CSE 127','CSE 140','CSE 160','CSE 211','CSE 252',
 'CSE 282','CSE 283','CSE 327','CSE 330','ENGR 005','ENGR 010','CHM 030',
 'MATH 021','MATH 022','MATH 231','PHY 011','PHY 012','ECO 001',
}
# Three linear alternatives, nine depth options, twelve named general options,
# and four writing alternatives. Open CSE/HSS/science/free predicates add no IDs.
LEHIGH_OPTIONS={
 'MATH 205','MATH 241','MATH 242','CSE 323','CSE 325','CSE 326','CSE 335',
 'CSE 337','CSE 347','CSE 348','CSE 349','MATH 312','ISE 230','ISE 240',
 'ISE 309','ECE 303','MATH 023','MATH 310','MATH 338','MATH 339','COMM 165',
 'COMM 351','JOUR 025','TLT 351','WRT 001','WRT 003','WRT 002','WRT 005',
}

def test_lehigh_manual_profile_and_subject_review():
 p=json.loads(Path('data/programs/'+LEHIGH+'.json').read_text())
 courses={c['code']:c for c in p['courses']}
 assert set(courses)==LEHIGH_REQUIRED|LEHIGH_OPTIONS
 assert len(LEHIGH_REQUIRED)==20 and len(LEHIGH_OPTIONS)==28
 profile=requirement_profile(p)
 for role,codes in [('required',LEHIGH_REQUIRED),('options',LEHIGH_OPTIONS)]:
  assert profile[role]['count']==len(codes)
  expected=Counter(courses[code]['category'] for code in codes)
  assert {k:v for k,v in profile[role]['categories'].items() if v}==expected
 assert profile['unresolved']['count']==0
 assert all(c['category_review']['taxonomy_version']=='1' for c in courses.values())
 assert courses['CSE 027']['category']=='foundations'
 assert courses['CSE 211']['category']=='systems'
 assert courses['CSE 252']['category']=='human_context'
 assert courses['COMM 351']['category']=='human_context'
 assert courses['ISE 230']['category']=='mathematics'
 assert courses['ECE 303']['category']=='other'
 assert courses['ECE 303']['category_review']['status']=='mixed'
 assert courses['CSE 282']['category_review']['status']=='mixed'
 assert p['curriculum_status']=='partial'  # Graph correction does not repair source conflict.


def test_lehigh_course_observation_never_reuses_review_after_change(monkeypatch):
 text='CSE 012 Programming 3 Credits A synthetic course description. Prerequisites: TEST 100'
 html='<div class="courseblock"><p class="courseblocktitle"><span class="cdspacing">CSE 012</span> <span class="cdspacing">Programming</span> 3 Credits</p><p>A synthetic course description.</p><p>Prerequisites: TEST 100</p></div>'
 monkeypatch.setattr(lehigh,'SPEC',{'CSE 012':{'digest':hashlib.sha256(text.encode()).hexdigest(),'description':'Programming practice.','category':'foundations'}})
 result=lehigh.parse_courses(html,'cse')
 assert result['courses'][0]['prerequisites']=='TEST 100'
 assert 'category_review' not in result['courses'][0]
 assert 'curriculum_audit' not in result
 with pytest.raises(ValueError,match='description changed'):
  lehigh.parse_courses(html.replace('synthetic','altered'),'cse')
 with pytest.raises(ValueError,match='identities missing'):
  lehigh.parse_courses('<h1>Unrelated</h1>','cse')
