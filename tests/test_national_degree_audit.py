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
 canonical_options=options-({'CMPSC410','CMPSC442','STAT318','STAT414'} if 'methods' in pid else set())
 assert profile['options']['count']==len(canonical_options)
 assert profile['options']['source_record_count']==len(options)
 assert {k:v for k,v in profile['options']['categories'].items() if v}==Counter(courses[code]['category'] for code in canonical_options)
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
 </div><div id="suggestedacademicplantextcontainer">All incoming Schreyer Honors College first-year students at University Park; ENGL 137H; ENGL 138T; Each course is 3 credits</div>'''
 result=parse_degree(html,pid)
 alt=next(r for r in result['requirements'] if r['kind']=='alternative')
 branches=[r for r in result['requirements'] if r['parent_id']==alt['id']]
 assert sorted(len(r['course_ids']) for r in branches)==[1,2]
 assert all(r['kind']=='all' for r in branches)
 assert all(c['credits'] is None for c in result['courses'] if c['code']!='A-I 100')
 assert 'curriculum_audit' not in result
 with pytest.raises(ValueError,match='course table missing'):
  parse_degree(html.replace('sc_courselist','other'),pid)
 with pytest.raises(ValueError,match='academic plan policy section missing'):
  parse_degree(html.replace('suggestedacademicplantextcontainer','missing-policy-panel'),pid)


def test_psu_real_identity_export_preserves_unproved_slash_pairs(tmp_path):
 from atlas import db
 p=json.loads(Path('data/programs/penn-state-ai-methods-applications-ist-bs.json').read_text())
 conn=db.connect(tmp_path/'psu.sqlite');db.migrate(conn)
 db.ingest_program(conn,p)
 exported=db.export_data(conn)['programs'][0]
 assert exported['course_identity_groups']==p['course_identity_groups']
 assert len(exported['courses'])==169
 profile=requirement_profile(exported)
 assert profile['identity']==dict(source_records=169,mapped_identities=165,crosslisted_aliases=4,reviewed_groups=4)
 assert profile['options']['count']==156
 assert profile['options']['source_record_count']==160
 grouped={cid for g in p['course_identity_groups'] for cid in g['course_ids']}
 bycode={c['code'].replace(' ',''):c['id'] for c in p['courses']}
 assert not {bycode[c] for c in ('IST301','ETI301','IST302','ETI302','PLSC418','PLSC418W')}&grouped
 assert not conn.execute('PRAGMA foreign_key_check').fetchall()
 conn.close()


@pytest.mark.parametrize('pid,fixed,options',[
 ('university-of-miami-artificial-intelligence-technologies-for-business-other-degree',22,21),
 ('miami-ai-technologies-business-bsba',21,33),
 ('university-of-miami-data-science-and-artificial-intelligence-ba-degree',7,39),
 ('miami-data-science-ai-bs',13,44),
])
def test_miami_primary_table_role_counts_keep_cognates_contextual(pid,fixed,options):
 p=json.loads(Path('data/programs/'+pid+'.json').read_text())
 profile=requirement_profile(p)
 assert (profile['required']['count'],profile['options']['count'])==(fixed,options)
 assert profile['unresolved']['count']>1800  # University cognate inventory, not all degree obligations.
 pools=[r for r in p['requirements'] if '-table-' in r['id'] and r['kind']=='choose_credits']
 assert pools and all(r['credit_unit']=='semester_hours' for r in pools)
 assert p['curriculum_status']=='partial'


def test_miami_synthetic_credit_pool_and_writing_overlay_roles():
 from atlas.adapters.miami_degree_curricula import observe
 html="""<h1>Example AI degree</h1><div id="curriculumtextcontainer"><table>
 <tr class="areaheader"><td>Core Computer Science Courses</td></tr>
 <tr><td><a class="code" href="/a">CSC 120</a></td><td>Example programming</td><td>4</td></tr>
 <tr><td>Electives</td><td>6</td></tr><tr><td>Techniques</td><td></td></tr>
 <tr><td><a class="code" href="/b">CSC 345</a></td><td>Example option</td><td></td></tr>
 <tr><td>Advanced Writing and Communication Requirement: Four W courses, including one of the following:</td><td></td></tr>
 <tr><td><a class="code" href="/c">CSC 405</a></td><td>Example writing</td><td>1</td></tr>
 <tr class="orclass"><td><a class="code" href="/d">CSC 431</a></td><td>Example alternative writing</td><td></td></tr>
 </table></div>"""
 result=observe(html,'test-degree','Example AI degree','BA','Example AI degree','catalog','https://example.edu/catalog')
 profile=requirement_profile(result)
 assert [profile[k]['count'] for k in ('required','options','unresolved')]==[1,3,0]
 pool=next(r for r in result['requirements'] if r['kind']=='choose_credits')
 assert pool['credits']==6 and pool['credit_unit']=='semester_hours'
 assert len(pool['course_ids'])==1  # One observed option does not become required.
 assert 'curriculum_audit' not in result


def test_maryland_capstone_requires_explicit_replacement_permission():
 from atlas.adapters.maryland_ai_curricula import parse
 html="""<h1>Human-Centered Artificial Intelligence Major</h1><div id="requirementstextcontainer">
 <p>College requirements include MATH115; at least 2 courses must be from LING.</p>
 <p>All students complete a capstone seminar. Students may replace this course with an internship.</p>
 <table class="sc_courselist"><tr><td class="codecol">HCAI100</td><td>Example core</td><td class="hourscol">3</td></tr>
 <tr><td class="codecol">HCAI490</td><td>Example capstone</td><td class="hourscol">3</td></tr></table></div>"""
 args=dict(pid='test-ba',title='Human-Centered Artificial Intelligence',award='BA',url='https://example.edu/catalog')
 result=parse(html,**args)
 profile=requirement_profile(result)
 assert [profile[k]['count'] for k in ('required','options','unresolved')]==[1,1,1]
 assert next(r for r in result['requirements'] if 'umd-hcai490' in r['course_ids'])['kind']=='alternative'
 assert len(result['courses'])==3  # No invented internship code.
 assert 'curriculum_audit' not in result
 with pytest.raises(ValueError):
  parse(html.replace('Students may replace this course with an internship.','An internship may be interesting.'),**args)
 p=json.loads(Path('data/programs/university-of-maryland-college-park-human-centered-ai-ba-degree.json').read_text())
 assert [requirement_profile(p)[k]['count'] for k in ('required','options')]==[9,59]


def test_miami_bte_description_guard_never_emits_manual_review(monkeypatch):
 from atlas.adapters import miami_bte_degree_courses as bte
 html='<div class="courseblock"><p class="courseblocktitle">BTE 320. Example programming. 3 Credit Hours.</p><p class="courseblockdesc">Example software construction. Requisite: Business School. Components: LEC.</p></div>'
 text='BTE 320. Example programming. 3 Credit Hours. Example software construction. Requisite: Business School. Components: LEC.'
 monkeypatch.setattr(bte,'SPEC',{'BTE 320':dict(digest=hashlib.sha256(text.encode()).hexdigest(),category='foundations',description='Example programming focus.')})
 result=bte.parse(html,'example')
 assert result['courses'][0]['prerequisites']=='Requisite: Business School.'
 assert result['courses'][0]['credits']==3
 assert 'category_review' not in result['courses'][0]
 with pytest.raises(ValueError,match='description changed'):
  bte.parse(html.replace('software construction','different content'),'example')
 with pytest.raises(ValueError,match='identities missing'):
  bte.parse('<h1>Login</h1>','example')
 for pid in ['miami-ai-technologies-business-bsba','university-of-miami-artificial-intelligence-technologies-for-business-other-degree']:
  p=json.loads(Path('data/programs/'+pid+'.json').read_text());courses={c['code']:c for c in p['courses']}
  assert courses['BTE 403']['category']=='systems'
  assert courses['BTE 320']['category']=='foundations'
  assert courses['BTE 440']['category']=='foundations'
  assert courses['BTE 401']['category']=='human_context'
  assert courses['BTE 210']['category_review']['status']=='mixed'
  assert courses['BTE 497']['credits'] is None


def test_stevens_review_scopes_identity_and_field_changes(monkeypatch):
 from atlas.adapters import stevens_degree_course_review as review
 html='<h1>Navigation</h1><article class="flex-1"><h1>CS 368</h1><div><h3 class="field-label">Course Description</h3><section class="field-value">Example database infrastructure.</section></div><div><h3 class="field-label">Credits</h3><section class="field-value">3</section></div></article>'
 monkeypatch.setattr(review,'SPEC',{'CS 368':dict(id='stevens-cs-368',name='Example data management',source_id='catalog',url='https://example.edu/course',description_digest=hashlib.sha256(b'Example database infrastructure.').hexdigest(),category='systems',description='Example database infrastructure.')})
 result=review.parse(html,'CS 368')
 assert result['courses'][0]['category']=='systems'
 assert result['courses'][0]['credit_unit']=='unknown'
 assert 'category_review' not in result['courses'][0]
 with pytest.raises(ValueError,match='field changed'):
  review.parse(html.replace('database infrastructure.','changed content.'),'CS 368')
 with pytest.raises(ValueError,match='identity changed'):
  review.parse(html.replace('<h1>CS 368</h1>','<h1>Login</h1>'),'CS 368')
 p=json.loads(Path('data/programs/stevens-institute-of-technology-artificial-intelligence-bs-degree.json').read_text())
 courses={c['code']:c for c in p['courses']}
 assert courses['CS 368']['category']=='systems'
 assert courses['CS 135']['category_review']['status']=='mixed'
 assert courses['CS 456']['category_review']['status']=='mixed'
 assert courses['CS 508']['category_review']['status']=='mixed'
 assert courses['CS 558 / CPE 558']['credits']==3
 assert 'Graduate Student or At Least Junior' in courses['CS 558 / CPE 558']['prerequisites']


def test_maryland_reviewed_subjects_and_change_guard(monkeypatch):
 from atlas.adapters import maryland_course_metadata as meta
 html='<h1>CMSC - Computer Science</h1><div class="courseblock"><p class="courseblocktitle">CMSC131 Example programming (4 Credits)</p><p class="courseblockdesc">Programming done in Java. Invented fixture.</p></div>'
 text='CMSC131 Example programming (4 Credits) Programming done in Java. Invented fixture.'
 monkeypatch.setattr(meta,'SUBJECTS',{'CMSC131':dict(digest=hashlib.sha256(text.encode()).hexdigest(),category='foundations',description='Example programming foundations.')})
 result=meta.parse(html,pid='example',prefix='cmsc',codes=['CMSC131'])
 assert result['courses'][0]['category']=='foundations'
 assert 'category_review' not in result['courses'][0]
 with pytest.raises(ValueError,match='block changed'):
  meta.parse(html.replace('Invented fixture.','Changed content.'),pid='example',prefix='cmsc',codes=['CMSC131'])
 pid='university-of-maryland-college-park-artificial-intelligence-computational-structures-for-ai-systems-bsai-degree'
 p=json.loads(Path('data/programs/'+pid+'.json').read_text());courses={c['code']:c for c in p['courses']}
 assert courses['CMSC351']['category']=='foundations'
 assert courses['CMSC250']['category']=='mathematics'
 assert courses['INST204']['category']=='human_context'
 assert courses['CMSC320']['category_review']['status']=='mixed'
 assert courses['MATH243']['category_review']['status']=='reviewed'
 assert 'MATH240' in courses['MATH243']['prerequisites']


def test_william_mary_partial_core_has_limited_subject_evidence():
 p=json.loads(Path('data/programs/william-mary-applied-ai-ba.json').read_text())
 assert {c['code']:c['category'] for c in p['courses']}=={'DATA 201':'other','DATA 202':'human_context','DATA 305':'other'}
 assert all(c['credits'] is None for c in p['courses'])
 assert requirement_profile(p)['required']['count']==3
 assert p['curriculum_status']=='partial'


def test_psu_unread_descriptions_are_unreviewed_not_inspected_unknown():
 p=json.loads(Path('data/programs/penn-state-ai-methods-applications-ist-bs.json').read_text())
 courses={c['code']:c for c in p['courses']}
 assert 'category_review' not in courses['PHIL 433']
 assert courses['PHIL 433']['category']=='other'
 assert courses['PSYCH 260']['category']=='applications'
 assert courses['PSYCH 260']['category_review']['status']=='reviewed'
 assert courses['A-I 494']['category_review']['status']=='unclassified'
 assert sum('category_review' not in c for c in p['courses'])==11
 assert requirement_profile(p)['options']['classification']['unreviewed']==11


def test_usf_review_does_not_recertify_brochure_or_infer_units():
 pid='university-of-south-florida-artificial-intelligence-bs-degree'
 p=json.loads(Path('data/programs/'+pid+'.json').read_text())
 courses={c['code']:c for c in p['courses']}
 assert courses['CAI 4624']['category']=='systems'
 assert courses['CAI 4024']['category']=='human_context'
 assert sum('category_review' in c for c in p['courses'])==8
 assert all(c['credit_unit']=='unknown' for c in p['courses'])
 assert all(r['credit_unit']=='unknown' for r in p['requirements'])
 assert p['curriculum_status']=='partial'
 ledger=json.loads(Path('research/degree-audit/national-degree-batch.json').read_text())
 entry=next(e for e in ledger['programs'] if e['program_id']==pid)
 assert entry['status']=='blocked' and entry['expected_profile'] is None
 assert any(s['access_status']=='robots_disallowed' for s in entry['sources'])


def test_drexel_prescribed_subjects_and_source_result_guard(monkeypatch):
 from atlas.adapters import drexel_required_course_review as review
 html='<article class="search-courseresult"><h3>CS 260 Example data structures 4.0 Credits</h3><div class="courseblock">Example structures and algorithms. Prerequisites: CS 265 [Min Grade: C]</div></article>'
 text='CS 260 Example data structures 4.0 Credits Example structures and algorithms. Prerequisites: CS 265 [Min Grade: C]'
 monkeypatch.setattr(review,'SPEC',{'CS 260':dict(id='drexel-cs-260',source_id='catalog',url='https://example.edu/course',digest=hashlib.sha256(text.encode()).hexdigest(),category='foundations',description='Example data structures.')})
 r=review.parse(html,'CS 260')
 assert r['courses'][0]['credits']==4
 assert r['courses'][0]['prerequisites']=='Prerequisites: CS 265 [Min Grade: C]'
 assert 'category_review' not in r['courses'][0]
 with pytest.raises(ValueError,match='changed'):
  review.parse(html.replace('Min Grade: C','Min Grade: B'),'CS 260')
 with pytest.raises(ValueError,match='missing'):
  review.parse(html.replace('search-courseresult','unrelated'),'CS 260')
 p=json.loads(Path('data/programs/drexel-ai-ml-bs.json').read_text())
 courses={c['code']:c for c in p['courses']}
 expected={'CS 180','CS 260','CS 265','CS 380','INFO 212','INFO 215','SE 201','SE 310','PHIL 311','CIVC 101','COOP 101'}
 assert {c['code'] for c in p['courses'] if c.get('category_review')}==expected
 assert requirement_profile(p)['required']['count']==len(expected)==11
 assert courses['INFO 215']['category']=='human_context'
 assert courses['INFO 212']['category']=='foundations'
 assert courses['COOP 101']['category']=='applications'


def test_psu_supporting_subjects_are_description_specific():
 p=json.loads(Path('data/programs/penn-state-ai-methods-applications-ist-bs.json').read_text())
 c={x['code']:x for x in p['courses']}
 assert c['MATH 452']['category']=='ai_ml'
 assert c['EE 483']['category']=='applications'
 assert c['DS 220']['category']=='systems'
 assert c['IST 242']['category']=='foundations'
 assert c['ETI 301']['category']=='human_context'
 assert c['ETI 302']['category']=='applications'
 assert c['PSYCH 452']['category']=='applications'  # Human/animal memory, not machine learning.
 assert c['SRA 111']['category_review']['status']=='mixed'
 assert c['DS 402']['category_review']['status']=='unclassified'
 assert c['A-I 495']['credits'] is None
 assert c['A-I 285']['credits']==3 and c['DS 402']['credits']==3
 assert 'Recommended Preparations: DS 310' in c['DS 320']['prerequisites']
 assert 'PSYCH 260A' in c['PSYCH 455']['prerequisites']  # Preserve published code; no correction by assumption.
 assert 'category_review' not in c['IST 301']
 assert 'category_review' not in c['SRA 221']


def test_psu_supporting_repeatability_and_changed_source_guard(monkeypatch):
 from bs4 import BeautifulSoup
 from atlas.adapters import psu_degree_courses as module
 pid='penn-state-ai-methods-applications-ist-bs'
 html='''<div class="courseblock"><div class="courseblocktitle"><div class="course_codetitle">DS 402: Example Topics</div><div class="course_credits">3 Credits/Maximum of 9</div></div><div class="courseblockdesc">A changing topic.</div><div class="courseblockextra"><p>Enforced Prerequisite at Enrollment: EX 100 or EX 200</p></div></div>'''
 text=' '.join(BeautifulSoup(html,'html.parser').get_text(' ',strip=True).split())
 monkeypatch.setattr(module,'SCOPES',{pid:['DS 402']})
 monkeypatch.setattr(module,'SPEC',{'DS 402':dict(digest=hashlib.sha256(text.encode()).hexdigest(),description='Variable topic.',category='other')})
 result=module.parse_courses(html,pid,'ds')
 course=result['courses'][0]
 assert course['credits']==3  # Per enrollment, not repeatability ceiling.
 assert course['prerequisites'].endswith('EX 100 or EX 200')
 assert 'category_review' not in course and 'curriculum_audit' not in result
 with pytest.raises(ValueError,match='block changed'):
  module.parse_courses(html.replace('EX 200','EX 201'),pid,'ds')
 with pytest.raises(ValueError,match='identities missing'):
  module.parse_courses('<h1>Login</h1>',pid,'ds')


def test_psu_policy_change_requires_review_and_does_not_certify(monkeypatch):
 from atlas.adapters import psu_degree_policy_details as module
 key='transfer-completion-procedure'
 html='<main><h1>Example policy</h1><p>Documents are due thirty days before the last class.</p></main>'
 spec=dict(title='Example deadline',summary='A reviewed deadline.',digest=hashlib.sha256(module.policy_text(html).encode()).hexdigest())
 monkeypatch.setattr(module,'SPEC',{key:spec})
 result=module.parse_policy(html,'example-program',key)
 assert result['requirements'][0]['kind']=='note'
 assert 'curriculum_audit' not in result and 'curriculum_status' not in result
 with pytest.raises(ValueError,match='policy changed'):
  module.parse_policy(html.replace('thirty','twenty'),'example-program',key)
 with pytest.raises(ValueError,match='main content missing'):
  module.parse_policy('<h1>Log in</h1>','example-program',key)


@pytest.mark.parametrize('pid',['penn-state-ai-engineering-bs','penn-state-ai-methods-applications-ist-bs'])
def test_psu_public_degree_procedures_preserve_conditions(pid):
 p=json.loads(Path('data/programs/'+pid+'.json').read_text())
 notes={r['id']:r['summary'] for r in p['requirements']}
 assert '30 days' in notes[pid+'-transfer-completion-procedure']
 assert 'up to 24' in notes[pid+'-residence-procedure']
 assert 'cross-listed' in notes[pid+'-general-education-policy']
 assert 'integrative studies is exempt' in notes[pid+'-general-education-policy'].lower()
 assert p['curriculum_status']=='partial'


def test_psu_domain_reviews_preserve_restrictions_and_missing_catalog_entries():
 p=json.loads(Path('data/programs/penn-state-ai-methods-applications-ist-bs.json').read_text())
 c={x['code']:x for x in p['courses']}
 assert c['HDFS 200']['category']=='mathematics'
 assert c['NUTR 360']['category']=='human_context'
 assert c['VBSC 418']['category']=='applications' and c['VBSC 418']['credits']==2
 assert c['NUTR 291N']['category_review']['status']=='mixed'
 assert c['HPA 470']['category_review']['status']=='mixed'
 assert c['HDFS 216']['category_review']['status']=='unclassified'
 assert c['AGBM 445']['credits']==3
 assert 'FIN 100' in c['BA 301']['prerequisites']
 assert 'Smeal' in c['BLAW 243']['prerequisites']
 assert 'non-nutrition' in c['NUTR 119']['prerequisites']
 assert 'SOC 30' in c['HDFS 129']['prerequisites']
 missing={'IST 301','IST 302','IST 311','IST 331','IST 411','IST 413','IST 451','IST 454','IST 456','SRA 221','PHIL 433'}
 assert {x['code'] for x in c.values() if 'category_review' not in x}==missing
 assert len(c)==169 and requirement_profile(p)['options']['count']==156


def test_psu_college_policy_observations_do_not_leak_between_degrees():
 from atlas.adapters import psu_degree_policy_details as module
 ist='penn-state-ai-methods-applications-ist-bs';eng='penn-state-ai-engineering-bs'
 assert module.SPEC['ist-faq-exemption']['url'] in module.source_parsers(ist)
 assert module.SPEC['ist-faq-exemption']['url'] not in module.source_parsers(eng)
 assert module.SPEC['engineering-department-guidance']['url'] not in module.source_parsers(ist)
 p=json.loads(Path('data/programs/'+ist+'.json').read_text())
 summary=next(r['summary'] for r in p['requirements'] if r['id']==ist+'-ist-faq-exemption')
 assert 'exempt' in summary and 'distinct' in summary
 assert 'IST 495' not in {c['code'] for c in p['courses']}

NJIT_REQUIRED=set('ACCT115 DS100 ENGL101 MATH135 MGMT190 FYSSEM DS110 ECON266 ENGL102 MGMT116 MGMT290 MIS245 MGMT216 MGMT232 FIN315 IS392 MRKT330 OM375 HRM301 MGMT399 MIS385 PHIL310 FIN320 IS465 MGMT316 MGMT322 PHIL335 FIN410 MGMT422 MGMT435 MGMT416 MGMT432'.split())


def test_njit_required_subjects_and_enrollment_roles():
 from atlas.adapters import njit_required_course_reviews as m
 p=json.loads(Path('data/programs/'+m.PID+'.json').read_text());courses={c['code'].replace(' ',''):c for c in p['courses']}
 assert len(NJIT_REQUIRED)==32
 profile=requirement_profile(p)
 assert profile['required']['count']==32 and profile['options']['count']==349
 assert profile['required']['classification']=={'reviewed':24,'mixed':7,'unclassified':0,'unreviewed':1}
 assert courses['MGMT116']['category']=='mathematics'
 assert courses['MGMT216']['category']=='mathematics'
 assert courses['OM375']['category']=='mathematics'
 assert courses['MIS385']['category']=='systems'
 assert courses['MGMT422']['category']=='human_context'
 assert courses['MGMT416']['category']=='applications'
 assert courses['FIN410']['category']=='ai_ml'
 assert courses['PHIL310']['category_review']['status']=='mixed'
 assert courses['FYSSEM']['credits']==0 and courses['FYSSEM']['category']=='other'
 assert 'category_review' not in courses['FYSSEM']
 assert 'No prerequisites' in courses['DS100']['prerequisites']
 assert courses['DS110']['prerequisites'] is None
 assert 'FIN 218' in courses['FIN320']['prerequisites']
 assert 'FIN 310' in courses['FIN410']['prerequisites']
 assert 'FIN218' not in NJIT_REQUIRED and 'FIN310' not in NJIT_REQUIRED
 assert 'concurrently' in courses['PHIL335']['prerequisites']


def test_njit_required_course_guard_and_exact_conditions(monkeypatch):
 from bs4 import BeautifulSoup
 from atlas.adapters import njit_required_course_reviews as m
 html='<div class="courseblock"><p class="courseblocktitle">MGMT 116. Example Quantitative Course. 4 credits, 5 contact hours (3;2;0).</p><p>Prerequisites: EX 100 or EX 200. Restrictions: Junior standing. Quantitative methods.</p></div>'
 text=' '.join(BeautifulSoup(html,'html.parser').get_text(' ',strip=True).split())
 monkeypatch.setattr(m,'SPEC',{'MGMT 116':dict(key='example',url='https://example.edu/course',digest=hashlib.sha256(text.encode()).hexdigest(),description='Quantitative methods.',category='mathematics')})
 result=m.parse_courses(html,'example');c=result['courses'][0]
 assert c['credits']==4  # Credits, not contact hours.
 assert c['prerequisites']=='Prerequisites: EX 100 or EX 200. Restrictions: Junior standing.'
 assert 'category_review' not in c and 'curriculum_status' not in result
 with pytest.raises(ValueError,match='course changed'):
  m.parse_courses(html.replace('EX 200','EX 201'),'example')
 with pytest.raises(ValueError,match='missing or duplicate'):
  m.parse_courses('<h1>Access denied</h1>','example')
