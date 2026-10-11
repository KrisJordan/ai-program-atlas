"""Source-scoped, conditional college rules; no inferred home-college assignment."""
from bs4 import BeautifulSoup
from atlas.adapters.northeastern_policies import text, section, need

KHOURY_URL='https://www.khoury.northeastern.edu/current-undergraduate-students/undergraduate-advising-academic-support/academic-policies-and-procedures/'

# Each exact section/claim is independently reviewed. Changed policy statements
# fail for review rather than silently retaining an older eligibility threshold.
KHOURY_RULES=[
 ('course-load','Academic progression standards',[
  'full-time Khoury students enroll in four courses with appropriate labs and recitations',
  'at least 12 semester hours each academic semester','exceptions to the course load requirement must be approved',
  'Pass/fail courses are restricted to electives outside of the major, minor, and NUpath requirements'],
  'If subject to Khoury full-time rules, enroll in four courses with required labs/recitations and complete at least twelve hours each academic semester. The advisor must approve load exceptions before the semester. Pass/fail is restricted to electives outside major, minor and NUpath requirements.'),
 ('graduation-gpa','GPA requirements for graduation',[
  '2.000 in major (CS/CY/AI) courses','2.000 overall'],
  'For Khoury graduation, the current advising policy requires cumulative major (CS/CY/AI) GPA 2.000 and overall GPA 2.000. This may supplement the catalog; catalog omission does not waive it. Exact applicability to the student’s home college/cohort still requires confirmation.'),
 ('first-year-progression','First-year students',[
  'overall cumulative GPA of at least 1.800','at the end of each full-term semester',
  'GPA of at least 2.000 in the major at the end of the second academic full-term semester'],
  'For students subject to these Khoury first-year rules, probation applies below cumulative overall GPA 1.800 at each full academic term end or below major GPA 2.000 at the end of the second term.'),
 ('later-progression','Upperclass and transfer students',[
  'overall cumulative GPA of at least 2.000','GPA of at least 2.000 in the major',
  'second academic full-term semester of the curriculum completed on campus','each full-term academic semester thereafter'],
  'For Khoury upperclass/transfer students, the current advising policy requires overall and major GPA 2.000 by the end of the second full academic term completed on campus and each later full term. It is not an unconditional rule for every partner-college student.'),
 ('probation-plan','Criteria for academic probation',[
  'Not following a program of study approved by the student’s academic advisor',
  'Not earning at least 12 semester hours in each academic full-term semester'],
  'For full-time Khoury students, not following the advisor-approved program or not earning twelve hours in a full academic term triggers probation for the following academic semester, alongside the separately stated GPA criteria.'),
 ('major-dismissal','Academic dismissal from major',[
  'GPA of at least 2.000 in the major at the end of the third academic full-term semester',
  'for more than one semester may be dismissed','as a transitional major for one semester'],
  'For students subject to Khoury major rules, major GPA below 2.000 at the third full academic term end or later results in dismissal from Khoury. More than one semester off the advisor-approved plan may also result in dismissal. Otherwise university-eligible dismissed students may remain as a transitional major for one semester.'),
 ('transfer-entry','Admission requirements for students changing majors',[
  'Must be in good academic standing','overall GPA of 2.0 or higher in Khoury classes',
  'Successful completion of CS 2000/2001 or CS 2100/2101 or DS 2500/DS 2501 (whichever comes first)',
  'not eligible for a major change based on passing the CS 2000/2001 placement test alone',
  'remain in your current college as a transitional student'],
  'For a student changing into a Khoury major/home college, require good standing, GPA 2.0 or higher in Khoury classes and successful completion of CS 2000/2001, CS 2100/2101 or DS 2500/2501 as specified. Placement alone does not establish admission; after placing out, pass the applicable second-course pair. Applicants not yet meeting entry criteria remain transitional in their current college. These are conditional entry pathways, not extra fixed degree courses.'),
 ('business-transfer','Admission requirements for students changing majors',[
  'For admission into CS/Business, CY/Business, or AI/Business','GPA of 2.0 or higher average in any business courses'],
  'Only when applying to change into CS/Business, CY/Business or AI/Business, the stated admission condition additionally requires a 2.0 or higher average GPA in any business courses. This does not add a business-GPA requirement to unrelated degrees.'),
 ('home-change','Guided self-placement test for students changing majors',[
  'currently in a Khoury combined major, but not in Khoury College as their home college',
  'must meet with their assigned Khoury secondary academic advisor',
  'If the combined major you want is offered by your home college, you can choose to stay in your home college'],
  'An existing Khoury combined-major student requesting Khoury as home college must meet the assigned Khoury secondary advisor. A student may stay in their current home college if that college offers the intended combination, subject to advisor confirmation. This does not identify which home colleges are allowed for this exact degree/cohort.'),
 ('graduation-clearance','Preparing to graduate',[
  'Khoury advising office and the university registrar’s office','Review and approve your official Graduation Clearance Contract',
  'Apply to graduate on the Student Hub','Notify your academic advisor of any changes in registration or graduation plans'],
  'For Khoury graduation clearance, the college advising office and registrar review completion. Confirm the intended graduation year, follow advisor instructions, approve the Graduation Clearance Contract, apply through the Student Hub and notify the advisor of registration/graduation changes.'),
]


def parse_khoury_policy(html,*,program_id):
    soup=BeautifulSoup(html,'html.parser')
    for node in soup.find_all(['nav','aside','script','style','footer']):node.decompose()
    panel=soup.find('main',id='main')
    heading=panel.find('h1') if panel else None
    if heading is None or text(heading)!='Academic Policies and Procedures':
        raise ValueError('Expected Khoury academic-policy identity/panel missing')
    for node in panel.find_all(['nav','aside','script','style','footer']):node.decompose()
    sid=program_id+'-khoury-advising-policy';root=program_id+'-req-policy-khoury-conditional'
    def row(key,title,summary,parent):
        return dict(id=key,parent_id=parent,title=title,kind='note',count=None,credits=None,credit_unit='unknown',category='other',source_id=sid,source_text=None,summary=summary,course_ids=[])
    rows=[row(root,'Conditional Khoury advising policies','Apply only when the stated Khoury home-college, enrollment or change-of-major condition holds. These public rules do not resolve this combined degree’s exact allowed/designated home college or cohort.',None)]
    for key,title,guards,summary in KHOURY_RULES:
        need(section(panel,title),*guards)
        rows.append(row(program_id+'-req-policy-khoury-'+key,title,summary,root))
    return dict(id=program_id,courses=[],requirements=rows,curriculum_status='partial',notes=['Conditional Khoury policy observation; no home assignment, course enrollment, category review or complete audit is inferred.'])

CSSH_TRANSFER_URL='https://cssh.northeastern.edu/transfer-credit-guidelines/'


def parse_cssh_transfer(html,*,program_id):
    soup=BeautifulSoup(html,'html.parser')
    for node in soup.find_all(['nav','aside','script','style','footer']):node.decompose()
    panel=soup.find('main',id='content');heading=panel.find('h1') if panel else None
    if heading is None or text(heading)!='Transfer Credit Guidelines':raise ValueError('Expected CSSH transfer policy identity/panel missing')
    prose=text(panel)
    need(prose,'must petition to have the credit count','reviewed by the Office of the Provost',
         'Before registering for any courses at an institution outside of Northeastern',
         'approved petition on file','after a student has enrolled or completed the coursework potentially may not be approved',
         'from an approved and accredited','earn a C or higher','Pass/fail courses will not transfer',
         'number of credits as the other institution attributes to the course or less',
         'A maximum of 80 credits from a four-year institution and 60 credits from a two-year institution (combined total of 80)',
         'may not be Remedial/Developmental/ESL/Physical Education/Non-academic',
         'up to one semester after matriculation to finalize transfer credit',
         'course description and syllabus for evaluation','official, approved evaluation from a Northeastern University evaluator',
         'official transcript','original sealed envelope','Opened transcripts cannot be accepted',
         'emailed directly to your academic advisor')
    sid=program_id+'-cssh-transfer-policy';base=program_id+'-req-policy-cssh-transfer'
    claims=[
      ('','Conditional CSSH transfer-credit scope','Apply these published CSSH guidelines only when the student’s college/advising and transfer circumstances make them applicable. CSSH participation in a combined major does not itself assign a home college.'),
      ('petition','Post-matriculation transfer petition','Before outside registration, petition through the academic advisor for Provost review and keep the approved petition on file. Deficiency, unavailable relevant study or other permitted circumstances may support a request. A petition after enrollment/completion may not be approved; permission is not automatic.'),
      ('eligibility','Eligible transfer coursework','Use an approved accredited institution, academic-credit coursework and grade C or higher; pass/fail and remedial, developmental, ESL, physical-education or nonacademic courses do not qualify. Credit awarded is no more than the originating institution’s course credit and can be less.'),
      ('limits','Transfer limits and finalization','The page permits at most eighty credits from a four-year institution or sixty from a two-year institution, with a combined maximum of eighty. Finalize transfer credit within one semester after matriculation. Preserve these published scopes alongside any degree-specific residency rule; this is not permission for a particular transfer.'),
      ('evaluation','Evaluation and official records','Obtain an official approved Northeastern evaluation before petition consideration; for an unlisted course provide its description and syllabus to the advisor for departmental evaluation. After completion submit the official transcript promptly, in an unopened sealed envelope or sent electronically directly to the advisor. Opened transcripts are not accepted.')]
    rows=[dict(id=base+('-'+key if key else ''),parent_id=base if key else None,title=title,kind='note',count=None,credits=None,credit_unit='unknown',category='other',source_id=sid,source_text=None,summary=summary,course_ids=[]) for key,title,summary in claims]
    return dict(id=program_id,courses=[],requirements=rows,curriculum_status='partial',notes=['Conditional CSSH transfer-policy observation; no home-college assignment, course equivalence or approval inferred.'])

SCIENCE_URL='https://catalog.northeastern.edu/undergraduate/science/'
SCIENCE_RULES=[
 ('clearance','Graduation Clearance Process',['required to meet with an academic advisor in the College of Science','completed in the junior year'],
  'For College of Science students, meet a Science advisor in the junior year to identify remaining graduation requirements and allow time to finish them.'),
 ('load','Academic Progression Standards',['full-time science students enroll in four (3- or 4-credit) courses','appropriate labs and recitations','at least 12 semester hours each academic semester'],
  'When subject to full-time Science rules, enroll in four three- or four-credit courses with appropriate labs/recitations and complete at least twelve hours per academic semester, alongside the relevant GPA standards.'),
 ('reduced-load','Academic Progression Standards',['final semester with less than 12 semester hours needed','request this with their academic advisor before the start of their final semester','approved for reduced course load accommodation','Disability Access Services','not evaluated or approved by a students’ academic advisor'],
  'A reduced Science course load is allowed for a final semester needing fewer than twelve hours, requested from the advisor before that semester, or through a Disability Access Services-approved accommodation. The latter is evaluated by that service rather than the academic advisor; other exceptions are not invented.'),
 ('grades','Graduation Requirements',['2.000 in major courses','2.000 overall','minimum grade of C for First-Year Writing and Advanced Writing requirements'],
  'For Science graduation, require major and overall cumulative GPA 2.000, with university C-minimum first-year and advanced writing. The concrete degree may specify its own major-GPA code scope; do not silently replace that scope.'),
 ('first-year-standing','First-year Students:',['semester GPA of at least a 1.800','at the end of each full-term semester','at least 12 semester hours at the end of each fall and spring semester'],
  'For Science first-year students, probation follows a semester GPA below 1.800 or fewer than twelve earned hours at each fall/spring term end. This source says semester GPA, unlike the separate Khoury cumulative first-year wording.'),
 ('later-standing','Upperclass and Transfer Students:',['at least 12 semester hours in the academic full-term semester','overall cumulative GPA of at least 2.000','each full-term academic semester'],
  'For Science upperclass/transfer students, probation follows fewer than twelve earned hours in the full term or cumulative overall GPA below 2.000 at each full-term end.'),
 ('major-dismissal','Academic Dismissal from Major',['2.000 GPA in courses aligned with one\'s major','at the end of the second academic full-term semester','up to two semesters','placed on academic probation','does not find a new major after two transitional semesters'],
  'Science may dismiss a student from the major for major-aligned GPA below 2.000 from the second full academic term onward. Otherwise university-eligible students may remain transitional for up to two semesters on probation, potentially subject to university dismissal; without a new major after two transitional semesters they are dismissed from the college.'),
 ('university-dismissal','Academic Dismissal from University',['probation after two full-term academic semesters','below a 1.000 GPA or fewer than 4 earned semester hours','at the discretion of their college','appeal this decision to the Academic Standing Committee','International students must consult with an advisor'],
  'After two full terms of continuing probation, Science students may face university dismissal. GPA below 1.000 or fewer than four earned hours in a term or cumulatively may also trigger college-discretionary dismissal. Appeal is to the Academic Standing Committee; international students must consult Global Services about implications rather than relying on an inferred immigration outcome.')]


def parse_science_policy(html,*,program_id):
    soup=BeautifulSoup(html,'html.parser');title=soup.find(id='site-title');h1=title.find('h1') if title else None;panel=soup.find(id='textcontainer')
    if h1 is None or text(h1)!='College of Science' or panel is None:raise ValueError('Expected Science college-policy identity/panel missing')
    for node in panel.find_all(['nav','aside','script','style']):node.decompose()
    need(section(panel,'Academic Progression Standards'),'Satisfactory/unsatisfactory graded courses are restricted to electives outside of the major, minor, and NUpath requirements')
    sid=program_id+'-science-college-policy';base=program_id+'-req-policy-science-conditional'
    def row(rid,title,summary,parent):return dict(id=rid,parent_id=parent,title=title,kind='note',count=None,credits=None,credit_unit='unknown',category='other',source_id=sid,source_text=None,summary=summary,course_ids=[])
    rows=[row(base,'Conditional College of Science policies','Apply only where the student is subject to College of Science rules; participating-college evidence does not assign the home college. Satisfactory/unsatisfactory courses may count only as electives outside major, minor and NUpath. BA-only additional rules are not imposed on these BS degrees.',None)]
    for key,title,guards,summary in SCIENCE_RULES:
        need(section(panel,title),*guards);rows.append(row(program_id+'-req-policy-science-'+key,title,summary,base))
    return dict(id=program_id,courses=[],requirements=rows,curriculum_status='partial',notes=['Conditional Science college observation; no inferred home assignment, course pool or whole-degree completion.'])
