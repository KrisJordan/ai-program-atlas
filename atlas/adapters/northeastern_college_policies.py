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

BOUVE_URL='https://catalog.northeastern.edu/undergraduate/health-sciences/academic-policies-procedures/'
BOUVE_RULES=[
 ('curriculum','Academic Requirements',['pattern of attendance, and graduation year','Any exceptions to a student\'s curriculum plan','after consultation with the student\'s academic advisor',"university's minimum passing grade for the course will be accepted"],
  'Where Bouvé rules apply, follow the major, attendance pattern and graduation-year curriculum, prerequisites and degree audit. Curriculum exceptions follow the program’s protocols after advisor consultation. Use the program’s published course minimum; where none is established, the university passing grade applies, alongside separately specified university writing minima. Do not invent a universal Bouvé C threshold.'),
 ('petitions','Undergraduate Student Academic Petitions',['Taking one course while on co-op does not require this form','Taking any course(s) while on co-op requires “I Am Here” participation','Preapproval for a course to be taken for transfer credit','requires petition process with academic advisor'],
  'Use the specified petition process for leave, policy waiver, major change, minor declaration, late registration, directed study or an academic-standing appeal. Two courses during co-op require the registration petition; one does not require that form, but any co-op coursework requires I Am Here participation. Seek outside-course transfer preapproval through the academic advisor; approval is not automatic.'),
 ('probation','Collegewide Academic Probation Procedure',['before the end of week 2','no later than the end of week 3','weeks 4, 10, and 12','required to submit a second Academic Probation Contract','may be dismissed from Bouvé with an option to appeal'],
  'For Bouvé probation, meet the advisor by week two, sign the contract and submit it to the program and Student Services designee by week three. Late submission may cause dismissal. Advisor checks occur in weeks four, ten and twelve, followed by term-end review. Restored standing ends probation; compliant students still below standing submit a second contract, while noncompliance may lead to dismissal with appeal.'),
 ('major-dismissal','Academic Dismissal from Major',['failure to earn the minimum required grade in the same required course twice','effective the following academic semester','up to two semesters as a provisional Bouvé student','blocked from further registration'],
  'Failure twice to earn the stipulated minimum in the same required course leads to Bouvé major/program dismissal effective the next semester; additional program grounds may apply. A student otherwise in university good standing may remain provisional for up to two semesters to enter another major; failure to move by then blocks registration.'),
 ('university-dismissal','Academic Dismissal from the University',['not permitted to remain registered for courses in the immediate next academic term','If the university dismissal is successfully appealed'],
  'A university dismissal under the applicable progression standard prevents immediate next-term registration. A successful appeal permits registration in the following academic term; no automatic reinstatement is inferred.'),
 ('grade-appeal','Grade Appeals',['students should discuss their concerns with the course instructor','department chair- or school dean-level of the college that offers the course'],
  'Start a grade concern with the course instructor under university appeals procedures. If unresolved, appeal through the college offering the course, which is not necessarily the student’s home college.'),
 ('unit-appeal','Step 1: BCHS Unit-Level Appeal',['within 28 calendar days','academic determination is made available to the student','within 10 business days'],
  'For a Bouvé unit-level academic determination, submit the appeal request and statement within twenty-eight calendar days after the determination becomes available. The unit Academic Standing Committee supplies its written decision within ten business days under its procedures.'),
 ('higher-appeal','Step 2: Department Chair- or School Dean-Level Appeal',['within 28 calendar days of the posting of the grade','within 10 business days of receiving the report from the previous step','within 10 business days of receiving the appeal request'],
  'A course-grade appeal request is due within twenty-eight calendar days after posting. A secondary unit-decision appeal goes to the specified department chair, school dean or Bouvé academic-affairs office within ten business days of the prior report; the receiving office supplies a written result within ten business days. The office depends on the actual program/school.'),
 ('college-appeal','Step 3. College-Level Appeal',['within 10 business days of receiving the report from the previous step','The college dean will have the final decision','no later than 10 business days after receiving the appeal request'],
  'An unresolved lower-level matter may proceed to the Bouvé Academic Affairs Committee; request the college hearing in writing within ten business days of the prior report. The dean makes the college decision and notifies the parties within ten business days of the request. Further university appeal exists only where permitted by the linked university process.'),
 ('conduct','Bouvé College of Health Sciences Code of Professional Conduct',['Department of Applied Psychology (all programs)','Department of Communication Sciences and Disorders (all programs)','Department of Medical Sciences (all programs)','Department of Physical Therapy, Movement, and Rehabilitation Sciences (all programs)','School of Pharmacy and Pharmaceutical Sciences (all programs)','students in the above-mentioned Bouvé schools or departments'],
  'The university conduct code applies generally. Bouvé’s additional professional code expressly covers its listed Applied Psychology, Communication Sciences and Disorders, Medical Sciences, Physical Therapy/Movement/Rehabilitation and Pharmacy programs; do not impose it universally from a health-related title. Within that scope, professional behavior includes accountability, respectful communication, confidentiality, integrity, appropriate appearance, teamwork and constructive improvement in academic, experiential and extracurricular settings.'),
 ('experiential','Requirements for Clinical, Internships, and Practicum Courses',['Some Bouvé programs require courses with clinical, internship, or fieldwork components','cooperative education requirements that are distinct from clinical requirements','Students are responsible for any costs associated with transportation and/or housing','International students must consult','before enrolling in clinical, internship, practicum, off-campus directed study, co-op, or capstone courses'],
  'Only when the actual program/course includes clinical, internship or fieldwork, follow its supplied evaluation/site policies; required travel and housing costs fall to the student. Co-op is distinct and also follows employer rules. International students must consult Global Services before the specified experiential enrollments. Site/program safety training is conditional; graduate nursing licensure is not added to this undergraduate degree.'),
 ('screening','Background Checks',['If applicable','provide instructions and a deadline for completion','Failure to complete the check in a timely manner could jeopardize progression','Students are responsible for any fees'],
  'If an assigned clinical site requires background or drug screening, follow the program’s instructions and deadline and pay applicable fees. A missed deadline can jeopardize progression; a site may deny placement under its requirements. No screening is asserted mandatory merely because the degree involves health.'),
 ('health-clearance','Health Clearance Requirements',['Students must comply with any universitywide health requirements','any site-specific requirements prior to entering the clinical setting','prohibited from attending a clinical course or rotation until satisfactory evidence is provided','students are responsible for software account fees'],
  'Follow applicable university health requirements. Before an actual clinical placement, satisfy program/site clearance and documentation; missing certification prevents attendance and can affect course completion. Where the program uses clearance software, the student pays its account fee. No particular immunization or clinical placement is inferred here.'),
 ('clinical-conduct','Student Conduct',['Students assigned to a clinical site for instruction','failure to adhere to these rules may result in dismissal from that institution or site and clinical course failure','Bouvé College of Health Sciences Code of Professional Conduct','if applicable'],
  'At an assigned clinical site, follow its rules and applicable university/program conduct standards; violations can cause site dismissal, clinical course failure and university discipline. Preserve patient/student record confidentiality under the published policies. The additional Bouvé professional code applies only where its stated scope holds.')]


def parse_bouve_policy(html,*,program_id):
    soup=BeautifulSoup(html,'html.parser')
    for node in soup.find_all(['nav','aside','script','style','footer']):node.decompose()
    title=soup.find(id='site-title');h1=title.find('h1') if title else None;panel=soup.find(id='textcontainer')
    if h1 is None or text(h1)!='Academic Policies and Procedures' or panel is None:raise ValueError('Expected Bouvé college-policy identity/panel missing')
    # This catalog page closes a formatting wrapper midway through Step 2.
    # Traverse only this panel's descendants, bounded by heading rank, so that
    # a wrapper boundary neither drops published text nor imports another rule.
    from bs4 import NavigableString
    import re
    def scoped_section(title):
        elements=list(panel.descendants)
        heading=next((n for n in elements if getattr(n,'name',None) in ('h2','h3','h4') and text(n)==title),None)
        if heading is None:raise ValueError('Expected Bouvé policy section missing')
        parts=[]
        for node in elements[elements.index(heading)+1:]:
            if getattr(node,'name',None) in ('h2','h3','h4') and int(node.name[1])<=int(heading.name[1]):break
            if isinstance(node,NavigableString):parts.append(str(node))
        return re.sub(r'\s+',' ',''.join(parts)).strip()
    need(scoped_section('Bouvé College of Health Sciences Code of Professional Conduct'),'Bouvé College of Health Sciences Code of Professional Conduct')
    base=program_id+'-req-policy-bouve-conditional';sid=program_id+'-bouve-college-policy'
    def row(rid,title,summary,parent):return dict(id=rid,parent_id=parent,title=title,kind='note',count=None,credits=None,credit_unit='unknown',category='other',source_id=sid,source_text=None,summary=summary,course_ids=[])
    rows=[row(base,'Conditional Bouvé college policies','Apply only when the student’s actual college/program, course or clinical circumstances satisfy each published condition. Evidence that Bouvé participates in this combination does not assign its home college, guarantee clinical enrollment or impose graduate/professional-only requirements.',None)]
    for key,title,guards,summary in BOUVE_RULES:
        need(scoped_section(title),*guards);rows.append(row(program_id+'-req-policy-bouve-'+key,title,summary,base))
    return dict(id=program_id,courses=[],requirements=rows,curriculum_status='partial',notes=['Conditional Bouvé policy observation; home/cohort applicability and actual clinical/professional scope remain student/program specific.'])

ENGINEERING_URL='https://catalog.northeastern.edu/undergraduate/engineering/'
ENGINEERING_RULES=[
 ('load','Academic Progression Standards',['four (4 credit) courses','corresponding labs and recitations','at least 12 semester hours each academic semester (fall, spring)'],
  'Where Engineering undergraduate rules apply, enroll in four four-credit courses with corresponding labs/recitations and successfully complete at least twelve hours each fall/spring academic semester, in addition to university progression standards.'),
 ('probation','Criteria for Academic Probation',['First-Year Students:','semester GPA of at least a 1.800','Upper-Level and Transfer Students:','cumulative GPA of at least 2.000','Not earning at least 12 semester hours','internal record but not on the permanent transcript'],
  'For Engineering first-year students, probation follows semester GPA below 1.800 or fewer than twelve earned hours in fall/spring. Upper-level/transfer students need cumulative GPA 2.000 and twelve earned hours. The action applies the next academic semester and appears on the internal record rather than permanent transcript. Preserve semester versus cumulative scope.'),
 ('dismissal','Criteria for Academic Dismissal',['below a 1.000 GPA or earn fewer than 4 semester hours','may be dismissed, regardless of their prior academic status','After two semesters (fall, spring) on academic probation','may be academically dismissed if they fail to meet academic progression standards','permanent transcript'],
  'Engineering may dismiss students below GPA 1.000 or four earned hours in a fall/spring semester regardless of prior standing, or after two probation semesters without meeting progression standards. This is discretionary rather than guaranteed dismissal; the action is recorded on the permanent transcript.'),
 ('satisfactory-grading','Satisfactory/Unsatisfactory Graded Coursework',['maximum of 9 semester hours','maximum of 4 semester hours','per semester','Only general electives taken outside the College of Engineering'],
  'Engineering permits at most nine satisfactory/unsatisfactory hours toward degree requirements, at most four per semester, and only general electives outside Engineering, under university policy. Do not apply this permission to major courses or infer that it overrides other university restrictions.'),
 ('graduation-gpa','Graduation Requirements',['2.000 in major coursework','2.000 overall'],
  'For Engineering graduation, the published cumulative minima are major GPA 2.000 and overall GPA 2.000. This conditional rule does not silently assign an Engineering home college or replace a more specific source-stated degree scope.'),
 ('catalog-cohort','Graduation Requirements',['year of graduation, determined by the date of entry or reentry into the College of Engineering','fails to make normal academic progress will be subject to review and possible change','reserves the right to amend programs'],
  'Engineering ties degree requirements to graduation year determined by entry/reentry into the college. Lack of normal progress can prompt review and change of requirements/year, and the college reserves curricular amendment. The public rule does not determine an individual student’s actual controlling cohort.'),
 ('study-plan','Progression Toward Fulfillment of Degree Requirements',['develop and follow a program of study','after completion of the third year','revised plans should be submitted to an academic advisor for review and approval','declare their minor no later than the third year'],
  'Follow a planned sequence toward Engineering degree requirements. For graduation-year changes after the third curriculum year, submit a revised plan for advisor review/approval. A student electing a minor should declare it by the third year; this does not require a minor.')]


def parse_engineering_policy(html,*,program_id):
    soup=BeautifulSoup(html,'html.parser')
    for node in soup.find_all(['nav','aside','script','style','footer']):node.decompose()
    title=soup.find(id='site-title');h1=title.find('h1') if title else None;panel=soup.find(id='textcontainer')
    if h1 is None or text(h1)!='College of Engineering' or panel is None:raise ValueError('Expected Engineering college-policy identity/panel missing')
    need(section(panel,'Undergraduate Academic Standards'),'Effective September 6, 2023')
    sid=program_id+'-engineering-college-policy';base=program_id+'-req-policy-engineering-conditional'
    def row(rid,title,summary,parent):return dict(id=rid,parent_id=parent,title=title,kind='note',count=None,credits=None,credit_unit='unknown',category='other',source_id=sid,source_text=None,summary=summary,course_ids=[])
    rows=[row(base,'Conditional College of Engineering policies','Current 2026–2027 catalog publishes these undergraduate standards as effective September 6, 2023. Apply only when the student’s actual college/enrollment/cohort makes them applicable. Verified COE participation does not independently assign home college or a personal controlling catalog.',None)]
    for key,title,guards,summary in ENGINEERING_RULES:
        need(section(panel,title),*guards);rows.append(row(program_id+'-req-policy-engineering-'+key,title,summary,base))
    return dict(id=program_id,courses=[],requirements=rows,curriculum_status='partial',notes=['Conditional Engineering policy observation retains its explicit effective date and cohort review boundaries; no course graph or award equivalence is inferred.'])
