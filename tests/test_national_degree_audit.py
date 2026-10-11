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

PSU_ENGINEERING_REQUIRED=set('A-I100 A-I341W A-I375 A-I410 AIE489W A-I305 A-I370 AIE355 CMPSC360 EE456 ENGL202C MATH140 MATH141 MATH225 PHYS211 PHYS212 STAT401'.split())
PSU_ENGINEERING_OPTIONS=set('CMPSC131 CMPSC121 DS120 CMPSC132 CMPSC122 CMPSC448 CMPSC445 CAS100A CAS100B CAS138T ENGL15 ENGL30H ENGL137H'.split())
PSU_IST_REQUIRED=set('A-I100 A-I341W A-I370 A-I375 CMPSC131 CMPSC132 MATH140 MATH225 STAT401'.split())
PSU_IST_CORE_OPTIONS=set('CMPSC360 MATH311W DS200 STAT200 CMPSC462 CMPSC465 DS305 CMPSC445 CMPSC448 DS310 AIMA430 AIMA440 A-I494'.split())
# Independently transcribed from the supporting lists beneath the 2026–27 plan.
PSU_IST_TECH=set('''A-I285 A-I494 A-I495 CMPSC432 CMPSC442 DS442 CMPSC441 CMPSC446
CYBER100 CYBER262 IST220 IST451 IST454 IST456 SRA111 SRA221
DS220 DS300 DS320 DS330 DS402 DS410 CMPSC410 DS420 DS441 EE483 EE454 EE456
IST140 IST240 IST242 IST250 IST256 IST311 IST331 IST411 IST413
MATH318 STAT318 MATH414 STAT414 MATH425 MATH429 MATH430 MATH448 MATH452 MATH455 MATH486
STAT380 STAT462 STAT463 STAT464'''.split())
PSU_IST_APPLICATION=set('''AEE216 AGBM101 AGBM200 AGBM445 CED102N CED160 VBSC340 VBSC418 VBSC433 VBSC435 VBSC444 VBSC455 VBSC485
PLSC14 PLSC290N PLSC408 PLSC410 PLSC418 PLSC418W PLSC420 PLSC437 PLSC438 PLSC439 PLSC440 PLSC449 PLSC467 PLSC478 PLSC479 PLSC483 PLSC491
ACCTG211 BA301 BA302 BA303 BA304 BLAW243 IB303 ECON102
ETI300W ETI435 ETI461 IST256 IST301 ETI301 IST302 ETI302
HPA101 HPA200 HPA210 HPA211 HPA301 HPA311 HPA332 HPA410 HPA445 HPA450 HPA470
HDFS129 HDFS200 HDFS210 HDFS215N HDFS216 HDFS249N HDFS434 HDFS447 HDFS492
NUTR100 NUTR119 NUTR251 NUTR291N NUTR358 NUTR360 NUTR407 NUTR487
PHIL103 PHIL107 PHIL110 PHIL125 PHIL127 PHIL131N PHIL404 PHIL416 PHIL418 PHIL427 PHIL433
PSYCH100 PSYCH212 PSYCH221 PSYCH253 PSYCH260 PSYCH413 PSYCH425 PSYCH426 PSYCH451 PSYCH452 PSYCH455 PSYCH458'''.split())

@pytest.mark.parametrize('pid,required,options',[
 ('penn-state-ai-engineering-bs',PSU_ENGINEERING_REQUIRED,PSU_ENGINEERING_OPTIONS),
 ('penn-state-ai-methods-applications-ist-bs',PSU_IST_REQUIRED,PSU_IST_CORE_OPTIONS|PSU_IST_TECH|PSU_IST_APPLICATION),
])
def test_psu_manual_course_sets_do_not_import_prerequisites_or_other_campus(pid,required,options):
 p=json.loads(Path('data/programs/'+pid+'.json').read_text())
 courses={c['code'].replace(' ',''):c for c in p['courses']}
 assert set(courses)==required|options
 assert not required&options
 profile=requirement_profile(p)
 assert profile['required']['count']==len(required)
 assert profile['options']['count']==len(options)
 assert profile['unresolved']['count']==0
 assert 'CMPSC330' not in courses  # Prerequisite of a listed option, not a major row.
 assert 'MGMT301' not in courses  # Commonwealth-campus-only business focus.
 assert all(c['credit_unit']=='semester_hours' for c in courses.values())
 assert 'curriculum_audit' in p and p['curriculum_status']=='partial'
 assert courses['A-I370']['category']=='ai_ml'
 assert 'STAT 200 or DS 200' in courses['A-I370']['prerequisites']
 if 'methods' in pid:
  assert courses['A-I494']['credits'] is None  # Variable 1–12, not six per identity.
  assert courses['A-I494']['category_review']['status']=='unclassified'
 else:
  assert courses['A-I305']['category']=='foundations'
  assert courses['A-I410']['category']=='systems'
  assert courses['AIE355']['category']=='mathematics'


def test_psu_sequence_alternative_parser_synthetic():
 from atlas.adapters.psu_university_park_degrees import parse_degree
 pid='penn-state-ai-engineering-bs'
 # This fixture contains only invented titles, minimal structural source guards,
 # and the observed shape of one OR-with-AND route, not a copied catalog.
 html='''<h1>Artificial Intelligence Engineering, B.S.</h1><p>Plan Code: AIE_BS University Park</p>
 <div id="howtogetintextcontainer">minimum grade point average of 2.6; grade of C or better</div>
 <div id="programrequirementstextcontainer">For the Bachelor of Science degree in Artificial Intelligence Engineering, a minimum of 126 credits is required
 <table class="sc_courselist"><tbody>
 <tr class="areaheader"><td>Prescribed Courses</td></tr>
 <tr><td><a class="code">A-I 100</a></td><td>Example required course</td><td class="hourscol">3</td></tr>
 <tr class="areaheader"><td>Additional Courses</td></tr>
 <tr><td><a class="code">CMPSC 131</a></td><td>Example first route</td><td class="hourscol">3-4</td></tr>
 <tr class="orclass"><td><a class="code">CMPSC 121</a> &amp; <a class="code">DS 120</a></td><td>Example sequence I<br>and Example sequence II</td></tr>
 </tbody></table>
 2.00 grade-point average; 6 credits are required and may satisfy other requirements; 3 credits required from the college of graduation; up to 24 credits of course work in the major; Foundations (grade of C or better is required; Inter-Domain Courses (Inter-Domain): 6 credits; 102-103; 21 of the 45 credits; remaining 24 General Education credits must be distinct
 </div>'''
 result=parse_degree(html,pid)
 alt=next(r for r in result['requirements'] if r['kind']=='alternative')
 branches=[r for r in result['requirements'] if r['parent_id']==alt['id']]
 assert sorted(len(r['course_ids']) for r in branches)==[1,2]
 assert all(r['kind']=='all' for r in branches)
 assert all(c['credits'] is None for c in result['courses'] if c['code']!='A-I 100')
 assert 'curriculum_audit' not in result
 with pytest.raises(ValueError,match='course table missing'):
  parse_degree(html.replace('sc_courselist','other'),pid)
