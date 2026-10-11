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
