"""Drexel public school/co-op rules and dated writing-intensive inventory."""
import re
from functools import partial
from urllib.parse import urljoin
from atlas.adapters.national_curriculum_common import content, clean, course, rule, require_phrases
PID='drexel-ai-ml-bs'
BASE='https://drexel.edu/'
PAGES={
 'school':('https://catalog.drexel.edu/undergraduate/computer-information-sciences/','School of Computer and Information Sciences'),
 'coop':('https://catalog.drexel.edu/undergraduate/coop/','The Steinbright Career Development Center'),
 'freshman':(BASE+'cci/current-students/policies/freshman-design-sequence-process-and-exceptions/','Freshman Design Sequence Process and Exceptions'),
 'senior':(BASE+'cci/current-students/policies/senior-design-process-and-exceptions/','Senior Design Process and Exceptions'),
 'univfailure':(BASE+'cci/current-students/policies/Univ-101-failure-policy/','UNIV 101 Failure'),
 'cifailure':(BASE+'cci/current-students/policies/CI-101-103-failure-policy/','CI 101-103 Failure Policy'),
 'registration':(BASE+'cci/current-students/policies/registration-policies/','Registration Policies'),
 'coopcredit':(BASE+'scdc/co-op/policies/co-op-registration-and-credit','Co-op Registration and Credit'),
 'coopeligibility':(BASE+'scdc/co-op/policies/co-op-eligibility','Co-op Eligibility'),
 'coopfinal':(BASE+'scdc/co-op/policies/finalizing-co-op-credits','Finalizing Co-op Credits'),
 'coopgrad':(BASE+'scdc/co-op/policies/graduating-on-co-op','Graduating on Co-op'),
}
RULES={
 'school': [('admission','School transfer timing',['Transfer admission for traditional undergraduate programs occurs in the fall term only','Internal transfer students can be admitted at any term'],'Traditional undergraduate external transfers enter in fall because of required-course sequences; internal transfers may enter any term. The separately named Computing and Security Technology rolling-admission exception is not an AI/ML exception.')],
 'coop': [('completion','Co-op completion',['Successful completion of the cooperative education experience is a graduation requirement'],'Successful co-op completion is required for a co-op degree. AI/ML offers the one-co-op/four-year or three-co-op/five-year routes stated in its own degree catalog.')],
 'freshman': [('exceptions','First-year design exceptions',['complete a freshman design sequence in another Drexel college or at a prior institution','complete the first course','up to 6 credits of CCI electives replace CI101-103','Any exception not specifically listed','approval of the Associate Department Head'],'A complete design sequence from another Drexel college or prior institution can substitute for CI 101–103; a first design course can replace CI 101, leaving CI 102–103. Late major-changers unable to finish before junior/senior standing may replace up to six credits with CCI electives. Advising records listed exceptions in DegreeWorks; unlisted exceptions need written Associate Department Head approval. The AI/ML catalog’s explicit ENGR sequence alternative is retained independently.')],
 'senior': [('conditions','Senior design registration and exceptions',['option for students to complete a thesis in place of the team project','rare and requires permission from the instructors and faculty senior design coordinator','Any exception to this would need to be made by the appropriate Associate Department Head'],'The school describes a thesis option in place of the team project but does not provide a finite thesis-course mapping here. Project groups continue across the sequence; group changes need instructor and coordinator permission. Trailer exceptions need Associate Department Head approval. These school rules do not silently replace the AI/ML catalog’s CI/ECE sequence choices.')],
 'univfailure': [('replacement','UNIV 101 failure or withdrawal replacement',['Effective Date: Fall 2024','may not repeat the course for credit','2.75 GPA or above','1 credit added to the free electives','GPA below 2.75','GSTD 100 or 200-level course in the next active term'],'From fall 2024, freshmen with F/W in fall and/or spring UNIV 101 cannot repeat it for credit: GPA at least 2.75 adds one free-elective credit; below 2.75 requires a GSTD 100/200-level course in the next active term. Advising must reconcile this one-credit replacement policy with the AI/ML catalog’s two-credit total UNIV CI101 allocation.')],
 'cifailure': [('repetition','First-year design failures',['F in CI 101','Spring of the same academic year','F in CI 102 cannot be enrolled in CI 103','Fall and Winter terms (year 2)','F in CI 103 must retake the course'],'CI 101 failure requires a spring retake in the same academic year. CI 102 failure prevents the next CI 103 registration: repeat CI 102/103 in year-two fall/winter. CI 103 failure requires repeating it. Five-year fall/winter co-op students use the stated online sections.')],
 'registration': [
 ('substitutions','Course substitutions and prerequisite waivers',['no later than the first day of each academic term','approval by the end of drop/add (Week 1)','final approval by the Associate Department Head','does not exempt you from completing that course in the future'],'Submit written substitution and prerequisite-waiver requests to advising by the first day of term, with approval by the end of week one. Substitutions need case-specific advisor recommendation and ADH/program-director approval. A prerequisite waiver does not waive later completion of a required course; missing the deadline requires another way to meet the degree rule.'),
 ('independent','Independent-study limits',['may not take an independent study if there is a course that the University offers that covers the same topics','No more than 12 credits of Independent Study will count toward graduation credits'],'Use a formal independent-study agreement through advising and a full-time college faculty supervisor. Do not duplicate an offered course; undergraduate independent-study credit toward graduation is capped at 12.'),
 ('graduate','Graduate-course exceptions for non-BSMS undergraduates',['3.0 or better cumulative GPA','B or better grades in major related coursework','up to the Pre-Junior level','Max of 2 graduate courses','cannot request to take a graduate course that has an undergraduate course equivalency'],'For CCI undergraduates outside an approved BSMS, graduate-course permission requires cumulative GPA at least 3.0, B or better major grades, and completed major core through pre-junior level. The course must serve the degree, lack an undergraduate equivalent, receive faculty and both graduate/undergraduate ADH approvals, and have space after graduate registration. Limit two courses; additional elective acceptance review and advising-maintained equivalence/approved lists apply.'),
 ],
 'coopcredit': [('credit','Co-op registration, earned units and waivers',['end of the drop/add period','Employment Summary and Planner','co-op credit (16DCUs) for a given term','must be made-up','Academic Unit to determine if co-op graduation requirements should or can be reduced or waived'],'Register employment by drop/add of the assigned quarter-cycle. Earn credit through successful work and Employment Summary and Planner completion during assigned co-op terms. Steinbright determines 16 Drexel Co-op Units per term; missing units must be made up unless the academic unit approves a degree-requirement waiver. DCUs are not course credits and are not added to the 180-credit academic minimum. The page’s separately marked fall-2027 semester timetable is prospective, not applied to this quarter plan.')],
 'coopeligibility': [('eligibility','Co-op eligibility',['24 credits over the two terms','cumulative GPA of 2.0 or higher','COOP 101, COOP 001, or COOP 500','eligible to obtain work authorization','replacement co-op cycle will be added one year'],'Co-op eligibility requires a co-op concentration, completed preparation course, introduction/reflection meeting, active job search and advisor communication, progress toward graduation, cumulative GPA at least 2.0, and being on track for 24 credits over the prior two academic terms. Domestic work requires legal work authorization. For a preceding summer vacation use the prior winter/spring enrollment. Ineligibility receives case review/appeal and normally postpones co-op one year; repeated low-GPA/progress delays require a revised academic plan.')],
 'coopfinal': [('finalization','Co-op finalization',['last month of the co-op experience','post co-op meeting','after one year from the time a final grade is assigned'],'Complete the ES&P in the final month and attend the return meeting with the co-op advisor. Failure can yield no co-op units, missing graduation requirements or loss of later co-op eligibility. Grade/registration changes are not considered more than one year after the final grade.')],
 'coopgrad': [('lastterm','Graduating on co-op and future policy',['provide an approved plan of study','Effective Fall 2027: Students cannot graduate on co-op'],'Under the current quarter policy, graduating at the end of a final co-op requires academic-advisor discussion and an approved plan reviewed by the co-op advisor. A separately announced rule effective fall 2027 forbids a final co-op term; it is recorded as prospective, not retrospectively applied to this 2026 quarter curriculum.')],
}

def parse_policy(html,key):
 root=content(html,PAGES[key][1]);sid=PID+'-policy-'+key;reqs=[]
 for suffix,title,phrases,summary in RULES[key]:
  require_phrases(root,phrases);reqs.append(rule(PID+'-policy-'+key+'-'+suffix,title,sid,kind='note',summary=summary))
 return dict(id=PID,curriculum_status='partial',requirements=reqs)

WI_URL=BASE+'coas/academics/university-writing-program/faculty-programs/'
def parse_wi(html):
 root=content(html,'Writing Intensive Course List');table=root.find('table',id='wi-courses')
 if table is None:raise ValueError('Writing-intensive inventory missing')
 sid=PID+'-policy-wi';courses=[]
 for row in table.find_all('tr'):
  cells=row.find_all('td',recursive=False)
  if not cells:continue
  code=clean(cells[0].get_text(' ',strip=True))
  if not re.fullmatch(r'[A-Z]+ \d+',code):raise ValueError('Unexpected WI course code: '+code)
  courses.append(course('drexel',code,clean(cells[1].get_text(' ',strip=True)),sid,WI_URL))
 if not courses or len({c['id'] for c in courses})!=len(courses):raise ValueError('Empty or duplicate WI pool')
 r=rule(PID+'-policy-wi-options','Published writing-intensive options',sid,[c['id'] for c in courses],kind='note',summary='University Writing Program list updated July 1, 2026. These are certified options, not all required courses or guaranteed term offerings. The degree requires three post-freshman WI courses, two within the major; transfer adjustments require advising. Check the actual section/term WI attribute and major eligibility. This university-wide list does not certify every listed course as an AI/ML major WI course.')
 require_phrases(root,['List updated as of July 1, 2026'])
 return dict(id=PID,curriculum_status='partial',courses=courses,requirements=[r])

SOURCE_PARSERS={url:partial(parse_policy,key=key) for key,(url,_) in PAGES.items()}
SOURCE_PARSERS[WI_URL]=parse_wi
