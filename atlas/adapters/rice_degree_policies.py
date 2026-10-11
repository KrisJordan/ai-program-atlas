"""Rice's shared graduation and transfer rules as guarded source observations."""
from atlas.adapters.national_curriculum_common import content, require_phrases, rule

PID = 'rice-university-artificial-intelligence-bs-degree'
GRADUATION = 'https://ga.rice.edu/undergraduate-students/academic-policies-procedures/graduation-requirements/'
TRANSFER = 'https://ga.rice.edu/undergraduate-students/academic-policies-procedures/transfer-credit/'
GRAD_RULES = [
 ('authority', 'Catalog authority and applicable year', ['GA shall prevail as the authoritative source', 'any academic year between their matriculation or graduation', 'more than seven years', 'time of their last readmission', 'no longer satisfies'], 'The General Announcements govern over other Rice publications. Choose a documented GA year between matriculation and graduation; after more than seven years use last readmission through graduation. Departments may decline old coursework for program requirements after review, while it remains on the transcript. A newly created program is available from its appearance in the GA, not an inferred first teaching date.'),
 ('residence', 'University residency and minimum degree hours', ['at least four semesters (fall and/or spring, and up to one summer semester)', 'at least 120 semester credit hours', 'at least 60 semester credit hours at Rice', 'at least 48 semester credit hours in upper-level', 'at least 25 of the 48', 'more than half of the upper-level coursework required by the declared major'], 'Complete the major and at least 120 semester hours, including 60 at Rice, 48 at level 300+, at least 25 of those upper-level hours at Rice and more than half of upper-level major work at Rice (or a stricter major rule). The graduation page permits one summer within four full-time residency semesters; the transfer page says four full fall/spring semesters. Preserve that conflict pending clarification.'),
 ('standing', 'Degree and major GPA, letter grades and standing', ['at least 1.67 or higher', 'at least 2.00 or higher', 'not on a Pass/Fail basis', 'not under investigation', 'Once the P is uncovered, it will not be restored'], 'Rice cumulative GPA must be at least 1.67, with at least 2.00 across Rice coursework satisfying each major/minor/certificate. Program courses need their earned letter grades: a needed P grade is uncovered on request or in the final audit and cannot be restored. Students must be in good academic/disciplinary standing and not under investigation. The major may impose higher standards.'),
 ('caps', 'LPAP and college-course credit caps', ['No more than 4 hours of credit for LPAP', 'No more than 3 hours of credit for student-taught College Courses'], 'No more than four LPAP hours or three student-taught COLL hours (including COLL 100–199 and COLL 200) count toward total graduation hours.'),
 ('fwis', 'First-year writing and placement', ['3-credit hour seminar', 'FWIS 100 cannot be used', 'during their first semester', 'during their first year', 'FWIS courses cannot be taken as Pass/Fail'], 'Complete and pass a three-credit FWIS in the first Rice year using letter grading. The prematriculation writing assessment determines placement; missing it defaults to FWIS 100. A student placed in FWIS 100 must pass that preparatory course in the first semester before the graduation FWIS; FWIS 100 itself does not meet the writing requirement.'),
 ('fwis-transfer', 'Writing transfer and enrollment restrictions', ['freshmen may not substitute pre-matriculation transfer credit', 'in their first semester at Rice', 'approval of the FWIS Program Director', 'at least 2.5 semester credit hours', 'after matriculating at Rice', 'After week two, FWIS courses cannot be dropped'], 'Freshman entrants cannot replace FWIS with prior transfer work. Transfer entrants must request a director-approved equivalent worth at least 2.5 semester hours in their first Rice semester. Neither group can take an external substitute after matriculation. During the first two weeks, a section change requires simultaneously adding another; later drops require an extraordinary committee exception.'),
 ('distribution', 'Distribution groups and designation timing', ['at least 3 courses', 'at least 3 credit hours each', 'at least two departments', 'at least 2.5 semester credit hours', 'at the time of course registration', 'at the time of matriculation'], 'Complete three designated courses of at least three credit hours in each of Groups I, II and III; each group must span at least two departments, with divisional/interdisciplinary designations counting as departments. An approved transfer equivalent must carry at least 2.5 semester hours. Designation is determined at registration/taking, or matriculation for prior work. These are term-dependent eligibility rules, not a fixed invented course pool. Eligible major work may also satisfy distribution.'),
 ('diversity', 'Analyzing Diversity and overlap', ['one course of three or more credit hours', 'All AD courses additionally carry Distribution Credit or fulfill', 'simultaneously more than one university graduation requirement category', 'AD-eligible Rice equivalent course'], 'Pass one AD-designated course of at least three credit hours. AD also carries distribution or FWIS eligibility and may overlap those requirements. An external equivalent needs approved AD designation when taken, or at matriculation for prior study. Completion in the first two years is encouraged, not a mandatory extra deadline.'),
 ('lpap', 'Lifetime physical activity requirement', ['one Lifetime Physical Activity Program (LPAP) course for one credit hour', 'Students with disabilities may make special arrangements'], 'Complete one one-credit LPAP course, with disability arrangements available. First-year completion is encouraged, including transfer students without an equivalent, not represented as an additional universal deadline.'),
 ('conferral', 'Degree application and faculty conferral', ['Application for Degree Form', 'late fee', 'degrees are approved by the faculty', 'December, May, and August'], 'Apply for the degree by the published semester deadline; late application carries a fee. Faculty approval and completion of all applicable requirements precede December, May or August conferral. Ceremony participation is distinct from earning the degree.'),
 ('dual', 'Conditional dual-degree requirements', ['different discipline', 'second degree must also be different', '30 additional semester hours at Rice University', 'Fulfill all requirements for the second degree'], 'Only if pursuing a second concurrent bachelor degree: choose a different degree type and discipline, obtain the additional declaration/advisor approval, complete both sets of requirements, and earn at least 30 additional Rice semester hours beyond the first degree. A second major alone is distinct and does not automatically constitute a second degree.'),
]
TRANSFER_RULES = [
 ('eligible', 'Transfer course and grade eligibility', ['grade of at least a C-', 'may not transfer courses taken pass/fail', 'previously completed at Rice with a passing grade', 'equivalency examinations', 'MOOCs'], 'Transfer work needs recognized institutional accreditation and at least C- equivalent, with official transcripts. Pass/fail, noncollegiate/life-experience, equivalency exams such as CLEP, remedial/life-skills, MOOCs and fields not offered at Rice do not transfer. Previously passed Rice courses do not earn duplicate transfer credit unless repeatable or exceptionally approved by the dean/vice provost.'),
 ('accounting', 'Transfer limits, GPA and converted hours', ['15 semester hours of summer school transfer credit', 'official summer study abroad', 'subject to Rice’s course load policy', 'grades lower than C-', 'no effect on a student', 'one-half (0.5) semester hour'], 'Postmatriculation summer transfer is capped at 15 semester hours except official summer study abroad. Concurrent external work remains subject to course-load rules and stricter program limits. Transfer normally has no Rice GPA effect; an explicitly approved curricular component can instead carry all grades, including below C-. Registrar-determined semester-hour/level conversion applies; ECTS has an explicit 0.5 semester-hour relation, not a generic conversion for other systems.'),
 ('approval', 'Equivalent credit versus general transfer electives', ['seek prior approval', 'granted TRAN', 'TRAN credit is reduced', 'official transcript'], 'Seek approval before external study. Without departmental equivalent-course approval, eligible work normally receives upper- or lower-level TRAN elective credit. Reclassification to a Rice equivalent reduces TRAN by the same hours, avoiding duplicate credit. The registrar evaluates only after receipt of an official transcript.'),
 ('international', 'International transfer evaluation and study-abroad exceptions', ['professional course-by-course evaluation', 'exempt from the requirement', 'School of Record transcript', 'unable to make a clear distinction'], 'Foreign work needs a professional course-by-course equivalency/grade/level evaluation. Official Rice study abroad is normally exempt unless the registrar cannot determine credit clearly. Third-party study abroad needs a School of Record transcript; direct-enrollment study may still need evaluation when credit is unclear.'),
]


def observe(html, heading, specs, suffix):
    root=content(html,heading)
    sid=PID+'-'+suffix
    rules=[]
    for key,title,markers,summary in specs:
        require_phrases(root,markers)
        rules.append(rule('rice-ai-'+suffix+'-'+key,title,sid,kind='note',summary=summary))
    return dict(id=PID,requirements=rules)


def parse_graduation(html):return observe(html,'Graduation Requirements',GRAD_RULES,'graduation')
def parse_transfer(html):return observe(html,'Transfer Credit',TRANSFER_RULES,'transfer')
SOURCE_PARSERS={GRADUATION:parse_graduation,TRANSFER:parse_transfer}

REGISTRATION='https://ga.rice.edu/undergraduate-students/academic-policies-procedures/registration/'
REGISTRATION_RULES=[
 ('load','Course load and outside-registration approvals',['more than 18 credit hours','including courses taken concurrently at another college or university','fewer than 12 credit hours','complete Rice graduation requirements elsewhere','without prior receipt of written permission'], 'For the AI degree, registration above 18 semester hours including concurrent external coursework needs prior written overload approval; below 12 hours in fall/spring needs reduced-load permission. Completing degree requirements elsewhere or concurrent enrollment also needs the specified advance written approval. An external course is not recorded without prior concurrent-enrollment authorization.'),
 ('levels','Full-time enrollment and graduate-course permission',['minimum of 12 semester credit hours','100-299 sequence classified as lower-level','300-499 sequence classified as upper-level','instructor permission required'], 'Undergraduate full-time status requires 12 semester hours, including summer. Courses 100–299 are lower-level and 300–499 upper-level. Enrolling outside the undergraduate level needs an instructor-permission override; an elective listing does not independently waive enrollment requirements.'),
 ('repeats','Repeat, prior-credit and cross-list accounting',['record of all attempts','credit is awarded only for the course with the highest grade','credit will be removed from the transfer or advanced placement credit','may not receive credit twice for cross-listed'], 'All attempts and grades remain on the transcript and in GPA. Repeating a passed nonrepeatable course earns credit only once, for the highest grade; repeating prior AP/transfer work removes that prior credit. Explicitly repeatable courses follow their designation. Cross-listed, equivalent and undergraduate/graduate equivalent courses cannot earn duplicate credit, concurrently or across terms unless repeatable.'),
]
def parse_registration(html):return observe(html,'Registration',REGISTRATION_RULES,'registration')
SOURCE_PARSERS[REGISTRATION]=parse_registration

COMMON_ERRORS = 'https://registrar.rice.edu/students/common-errors'
SPECIAL_REGISTRATION = 'https://registrar.rice.edu/students/special-registration'


def parse_common_errors(html):
    root = content(html, 'Common Registration Errors')
    rows = {}
    for row in root.find_all('tr'):
        cells = row.find_all(['td', 'th'])
        if len(cells) == 3:
            rows[' '.join(cells[0].stripped_strings)] = cells
    specs = [
        ('Mutually Exclusive', 'mutual-exclusion', 'Previously earned credit prohibits registration', 'Mutual-exclusion registration errors may be overridden only with instructor/department approval through an electronic Course Registration Override in ESTHER. The ordinary exclusion remains in force without approval. This is a conditional registration route, not guaranteed approval or an independent declaration of duplicate degree-credit entitlement.'),
        ('Prerequisite and Test Score', 'prerequisite', 'pre-requisite that you have not yet completed', 'A missing prerequisite must be completed or an instructor-permission Course Registration Override obtained through ESTHER. Thus the published alternative statistics routes can require approved exceptions for entry to later courses; no extra course, automatic waiver or guaranteed approval is inferred.'),
    ]
    result = []
    for label, key, condition, summary in specs:
        if label not in rows:
            raise ValueError('Registration error row missing: ' + label)
        cells = rows[label]
        require_phrases(cells[1], [condition])
        require_phrases(cells[2], ["instructor's permission", 'electronic Course Registration Override request via ESTHER'])
        if label == 'Mutually Exclusive':
            require_phrases(cells[2], ['If approved'])
        result.append(rule('rice-ai-registrar-' + key, label + ' conditional registration route', PID + '-registration-errors', kind='note', summary=summary))
    return dict(id=PID, requirements=result)


def parse_special_registration(html):
    root = content(html, 'Special Registration (and Course Registration Overrides)')
    require_phrases(root, ['Instructor-approved registration overrides', 'missing a required prerequisite', 'There is a level restriction on the course', 'If approved, return to ESTHER to complete your course registration'])
    return dict(id=PID, requirements=[rule('rice-ai-registrar-approval-procedure', 'Instructor-approved registration exceptions', PID + '-special-registration', kind='note', summary='Request the needed prerequisite or level exception electronically through ESTHER. Instructor approval and subsequent completion of registration are distinct steps; a submitted request is not permission. Individual decisions are not inferred from a published degree option.')])

SOURCE_PARSERS[COMMON_ERRORS] = parse_common_errors
SOURCE_PARSERS[SPECIAL_REGISTRATION] = parse_special_registration
