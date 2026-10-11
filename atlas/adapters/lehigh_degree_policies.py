"""Lehigh's current college HSS distribution and university completion policies."""
import re
from functools import partial
from atlas.adapters.national_curriculum_common import content, clean, course, rule, require_phrases
PID='lehigh-university-artificial-intelligence-machine-learning-and-data-science-bs-degree'
BASE='https://catalog.lehigh.edu/'
RULEBASE=BASE+'undergraduatestudies/guidetoacademicrulesandregulations/'
PAGES={
 'engineering':(BASE+'coursesprogramsandcurricula/engineeringandappliedscience/','P.C. Rossin College of Engineering and Applied Science'),
 'undergrad':(BASE+'undergraduatestudies/','Undergraduate Studies'),
 'graduation':(BASE+'undergraduatestudies/graduationrequirements/','Graduation Requirements'),
 'residency':(BASE+'undergraduatestudies/graduationrequirements/undergraduateresidencyrequirement/','Undergraduate Residency Requirement'),
 'eligibility':(RULEBASE+'eligibilityfordegree/','Eligibility for Degree'),
 'application':(RULEBASE+'applicationfordegree/','Application for Degree'),
 'repeat':(RULEBASE+'repeatingofcourses/','Repeating of Courses'),
 'passfail':(RULEBASE+'passfailsystemsforundergraduates/','Pass-Fail Systems for Undergraduates'),
 'transfer':(RULEBASE+'transfercredit/','Transfer Credit'),
 'csetransfer':('https://engineering.lehigh.edu/cse/academics/undergraduate/transfer-credit','Eligibility at a Glance'),
}
RULES={
 'engineering':[
 ('advanced','Advanced HSS distribution',['minimum of three courses and a minimum of 12 credits','Human Experience (HE)','Social World (SW)','Arts & Languages (AL)','Community and Global Health (CGH) and Population Health (POPH)','one course of three credits or greater','each of two different categories','At least one course must have an HE or AL designation','None of the courses can be taken Pass/Fail','All courses must be two credits or greater'],'Complete at least three courses and 12 semester hours across eligible HE, SW, AL, or College of Health CGH/POPH categories. At least one course worth 3+ credits must be in each of two categories; at least one must carry HE or AL. Every course must be 2+ credits and letter graded. This is a designation-based eligibility rule, not a finite list. The AI/ML/DS-specific CSE 252 HSS exclusion still applies.'),
 ('free','Free electives and work experience',['regular course offerings or up to six credit hours of advanced ROTC','up to a maximum of six free elective credits','ENGR 200 or ENGR 160','P/F (Pass/Fail)'],'Free electives may use regular courses or up to six advanced ROTC credits. Successful professional work assignments may earn up to six free-elective credits through ENGR 200/160 with prescribed P/F grading; coordinate with the advisor. These permissions do not repair the AI/ML/DS page’s 11-credit versus sample-plan 10-credit discrepancy.'),
 ],
 'undergrad':[
 ('units','Semester credit hours and course eligibility',['in terms of semester hours','100-199','Not open to freshmen except by petition','400-499','Graduate-level courses, open to undergraduates only by petition'],'Lehigh defines course credits as semester hours. Intermediate 100–199 courses are normally closed to freshmen without petition; 400-level graduate courses require an undergraduate petition. Course numbering/department restrictions still apply to the AI/ML/DS open CSE 100+ elective rule.'),
 ('prerequisites','Prerequisite and corequisite compliance',['responsible to make sure they meet and maintain all conditions of prerequisite','drop the student from a course with unmet prerequisites','co-requisite course is taken in the same semester'],'Maintain prerequisites before classes begin; obtain authorized online permission or demonstrate equivalent outside preparation for exceptions. The dean, registrar or instructor may drop unmet-prerequisite registrations. Corequisites are taken in the same semester. Missing individual prerequisite metadata in this atlas is not permission to enroll.'),
 ],
 'graduation':[
 ('time','Degree time limit and military credit',['limit of 8 calendar years','up to a one-year leave of absence','maximum of six credit hours of advanced military science'],'Complete both degree and university requirements within eight calendar years; petition SOS for up to one year’s exceptional leave. Basic military-science credits are additional to curriculum credits; at most six advanced military-science credits can apply.'),
 ],
 'residency':[
 ('options','Undergraduate residence alternatives',['minimum of 90 credit hours at Lehigh','60 of the last 75 credit hours','Lehigh Abroad approved programs','approved LVAIC cross-registration'],'Satisfy either 90 credits at Lehigh or 60 of the final 75 degree credits at Lehigh/in residency programs. Approved Lehigh Abroad and LVAIC cross-registration count; ordinary outside transfer credit does not establish residency.'),
 ],
 'eligibility':[
 ('gpa','Degree GPA and completion deadline',['minimum cumulative average of 2.00','no later than noon, the Friday preceding the degree award date'],'Earn cumulative GPA at least 2.00 and complete all curriculum requirements and university financial obligations by noon on the Friday before conferral. Students remain responsible for checking the degree audit with their advisor.'),
 ],
 'application':[
 ('deadlines','Graduation application',['on or before December 1','August must apply on or before July 1','January must apply on or before October 1','No applications will be accepted within three weeks'],'Undergraduates apply through Banner by December 1 for May, July 1 for August, or October 1 for January graduation. Late applications incur a fee; no application is accepted within three weeks of conferral. Missing application requires the next conferral date.'),
 ],
 'repeat':[
 ('limit','Course repeat and grade replacement',['a total of three attempts','Withdrawal from a course counts as an attempt','Only the most recent grade','identical course with a final grade at Lehigh','may not be changed by repeating the course under the pass-fail option'],'At most three attempts, including withdrawals. Only the latest grade and associated credits count; replace GPA only by repeating the identical course for a final Lehigh grade. P/F repetition cannot replace the original grade, and overloads are not approved for repetition.'),
 ],
 'passfail':[
 ('limits','Optional pass/fail limits',['no more than one course pass-fail','maximum of six courses pass-fail','may not be used for major or minor subject credit toward graduation or for distribution requirements','written acknowledgment of the academic adviser','fifteenth day of instruction','Courses 400 and above are not available'],'Optional P/F is limited to one eligible 100–399-level course per semester and six courses in a four-year career (eight in a five-year/two-degree program). Below-100 courses need a college petition; 400+ courses are excluded. It cannot satisfy major/minor or distribution requirements. Obtain advisor acknowledgment and choose by day 15 (prorated summer/winter); no retroactive change. Returning to letter grading still uses a lifetime P/F slot. Required P/F work-experience courses are a separate prescribed grading system.'),
 ('restrictions','Optional pass/fail course exclusions',['No Sociology or Anthropology courses numbered 100 or above','Anth 140','Engl 387','Psyc 176'],'No Sociology or Anthropology course at level 100+ may be optional P/F. The catalog also excludes ANTH 140/COGS 140/MLL 140; ENGL 122,123,124,125,126,155,157,163,175,177,187,189,191,387; and PSYC 107,109/SSP 109,117,153/SSP 153,176. Course-specific college restrictions apply in addition to the major/distribution prohibition.'),
 ],
 'transfer':[
 ('conditions','Transfer grades, equivalence and session limits',['C-','Pass/Fail credit/non-credit courses are not acceptable','No student may receive more credit at Lehigh than was granted','maximum of 16 credits','winter session is limited to 4 credits','six regional associations'],'Transfer requires accredited-institution coursework, department/college equivalency and rigor review, and at least C (not C−); P/F credit does not transfer. Credit cannot exceed original or equivalent Lehigh amounts or duplicate an existing equivalent. Summer transfer maximum is 16 credits and winter maximum 4. The registrar makes the final award; non-equivalent courses may receive approved general/elective credit and appropriate distribution attributes.'),
 ('procedures','Transfer procedures and credit conversion',['3-2 ratio','2-1 ratio','less than 3 weeks and/or 14 contact hours per credit','advanced approval of the Committee on Standing of Students','Transfer grades are NOT calculated'],'Outside grades do not enter the Lehigh GPA or replace an existing grade; LVAIC has its stated exception. Quarter credits convert at 3:2 without partial credit; ECTS at 2:1, subject to registrar/equivalent-course caps. Full-time concurrent enrollment elsewhere requires advance SOS approval except LVAIC. Continuing education, correspondence, independent study, or courses shorter than three weeks/14 contact hours per credit need advance SOS petition approval. Pre-/post-matriculation college/department rules may differ.'),
 ],
 'csetransfer':[
 ('caps','Continuing-student CSE transfer eligibility',['up to 2 required CSE courses and 2 elective CSE courses','including AP or exam credit','grades of C- or lower','within the last 4 years','withdrew from the Lehigh course or earned below a C-'],'For continuing students, transfer at most two required plus two elective CSE courses including AP/exam credit. Obtain term-specific advance approval. Letter grade must exceed C−; completed coursework must be within four years. A repeat elsewhere is eligible only after withdrawal or a Lehigh grade below C−. University/college requirements also apply.'),
 ('assessment','CSE transfer institution, assessment and approval',['ABET-accredited programs or CSE-approved study abroad','at least 7 weeks','at least 60% of the grade','within 10 days of the start of the following semester','complete syllabus'],'Required CSE transfers normally need an ABET-accredited program or CSE-approved abroad program; the department may approve equivalent rigor. Four-credit courses need at least seven weeks. Required-course replacements need 60% controlled proctored/in-person assessment without internet, phone, messaging or AI (limited instructor-approved aids allowed), or a preapproved CSE in-person validation exam within ten days of the next semester. Submit complete syllabus/assessment protocol, instructor details, code/title and intended term for faculty review and Associate Chair recommendation; the chair decides appeals.'),
 ],
}

def parse_policy(html,key):
 root=content(html,PAGES[key][1]);sid=PID+'-policy-'+key;reqs=[]
 for suffix,title,phrases,summary in RULES[key]:
  require_phrases(root,phrases)
  reqs.append(rule(PID+'-policy-'+key+'-'+suffix,title,sid,kind='note',summary=summary))
 return dict(id=PID,curriculum_status='partial',requirements=reqs)


def parse_engineering(html):
 result=parse_policy(html,'engineering');root=content(html,'Basic Requirement');sid=PID+'-policy-engineering'
 heading=root.find(lambda n:n.name in ['h2','h3'] and clean(n.get_text(' ',strip=True))=='Basic Requirement')
 table=heading.find_next('table') if heading else None
 if table is None:raise ValueError('Basic HSS table missing')
 courses=[]; alternatives=[]
 for row in table.find_all('tr'):
  cell=row.find('td',class_='codecol')
  if cell is None:continue
  a=cell.find('a',class_='code');cells=row.find_all('td',recursive=False)
  if a is None:raise ValueError('Expected HSS code link')
  code=clean(a.get_text(' ',strip=True));name=clean(cells[1].get_text(' ',strip=True));raw=clean(row.find('td',class_='hourscol').get_text(' ',strip=True)) if row.find('td',class_='hourscol') else ''
  if raw and not raw.isdigit():raise ValueError('Unexpected HSS credits')
  alternatives.append((code,'orclass' in row.get('class',[])))
  courses.append(course('lehigh',code,name,sid,PAGES['engineering'][0],credits=int(raw) if raw else None,unit='semester_hours',category='human_context'))
 if {c['code'] for c in courses}!={'ECO 001','WRT 001','WRT 002','WRT 003','WRT 005'}:raise ValueError('Basic HSS option set changed; review')
 if alternatives != [('ECO 001',False),('WRT 001',False),('WRT 003',True),('WRT 002',False),('WRT 005',True)]:raise ValueError('Basic HSS alternatives changed')
 require_phrases(root,['minimum of ten credit hours'])
 result['courses']=courses
 result['requirements'].append(rule(PID+'-policy-basic-hss','College basic HSS structure',sid,kind='note',credits=10,unit='semester_hours',summary='ECO 001 plus WRT 001 or WRT 003, plus WRT 002 or WRT 005: three courses and at least ten semester hours. The source’s course titles resolve the degree page’s copied engineering/chemistry labels. Multilingual alternatives retain their course placement/prerequisite conditions. These are the same basic HSS slots, not ten additional credits.'))
 return result

WRT_URL=BASE+'courselisting/wrt/'
def parse_writing(html):
 root=content(html,'Writing (WRT)');sid=PID+'-policy-wrt';courses=[]
 for b in root.select('.courseblock'):
  title=b.find(class_='courseblocktitle');spans=title.select('.cdspacing') if title else []
  if len(spans)<2:continue
  code=clean(spans[0].get_text(' ',strip=True))
  if code not in {'WRT 001','WRT 002','WRT 003','WRT 005'}:continue
  m=re.search(r'\s(\d+) Credits$',clean(title.get_text(' ',strip=True)))
  if not m:raise ValueError('Writing-course credits changed')
  c=course('lehigh',code,clean(spans[1].get_text(' ',strip=True)),sid,WRT_URL,credits=int(m[1]),unit='semester_hours',category='human_context')
  desc=clean(b.get_text(' ',strip=True))
  if 'Prerequisites:' in desc:c['prerequisites']=desc.split('Prerequisites:',1)[1].split('Attribute/Distribution:',1)[0].strip()
  if code=='WRT 003':
   require_phrases(b,['Enrollment is limited to multilingual English speakers','English placement testing','ICAPE director’s recommendation determines placement'])
   c['prerequisites']='Enrollment limited to multilingual English speakers; prior academic writing history, placement testing and/or ICAPE director recommendation determines placement.'
  courses.append(c)
 if len(courses)!=4:raise ValueError('Required writing identities missing')
 return dict(id=PID,curriculum_status='partial',courses=courses)

SOURCE_PARSERS={url:partial(parse_policy,key=k) for k,(url,_) in PAGES.items()}
SOURCE_PARSERS[PAGES['engineering'][0]]=parse_engineering
SOURCE_PARSERS[WRT_URL]=parse_writing
