"""Reviewed degree-policy observations from current public NJIT sources."""
from functools import partial
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, content, require_phrases, rule
from atlas.adapters.njit_degree_policies import PID, BASE

ADVISOR_URL='https://management.njit.edu/advising'
PETITION_URL='https://management.njit.edu/petition'
CATALOG_RULES=[
 ('curriculum-version','Curriculum version election', ['option of pursuing the revised curriculum or the curriculum in place at the time of admission','no later than the end of the academic year'], 'When a curriculum changes after admission, students may follow the admission curriculum or elect the revision by the end of the academic year when it becomes operative. No source-version election is inferred for an individual student.'),
 ('standing','Class standing and academic good standing', ['first year standing, 0--28 credits','sophomore standing, 29--56 credits','junior standing, 57--90 credits','senior standing, 91+ credits','TERM and CUM GPA of at least 2.0'], 'Class standing uses earned credits: first year 0–28, sophomore 29–56, junior 57–90, senior 91+. Good academic standing requires both term and cumulative GPA of at least 2.0. These definitions apply to course restrictions without adding prerequisite courses to the fixed degree set.'),
 ('credit-examination','Conditional credit by examination', ['perform at a level equivalent to a grade of "C"','failed or attempted a course at NJIT may not take an examination for credit'], 'Where the offering department makes an examination available, credit requires performance equivalent to C. A course already attempted or failed at NJIT cannot later receive examination credit; availability and approval are individual conditions, not a universal exemption.'),
 ('placement','Conditional placement and proficiency examinations', ['Transfer students who do not receive transfer credit for required first year courses','required to take placement tests','students selected to participate in such examinations are required to take them'], 'Required first-year preparation is determined by departmental placement. Transfer students without relevant first-year transfer credit take placement tests. Students selected for university proficiency examinations must participate even when the exam is zero-credit and not printed in the curriculum. The separate BEST rule applies to ABET engineering programs and is not assigned to this business degree.'),
 ('graduate-credit','Graduate credit outside an accelerated dual program', ['final two semesters','cumulative GPA is at least 2.8','maximum of nine graduate credits (3 courses)','will not count towards their undergraduate degree requirements','not permitted to take 700-level courses, except in rare cases'], 'Outside an admitted accelerated dual program, eligible undergraduates in their final two semesters may take at most three graduate courses/nine credits with cumulative GPA at least 2.8 and required approvals; these do not satisfy undergraduate degree requirements. 500/600-level registration requires the graduate and undergraduate advisors. 700-level study requires the stated rare explicit exception, not automatic free-elective eligibility.'),
 ('accelerated-credit','Conditional accelerated dual-degree credit', ['Admission into an accelerated dual degree program is required','passes it with a grade of B or better','grade lower than B','minimum cumulative GPA of either 3.0','3.5','at least five (5) major courses','Vice Provost for Graduate Studies'], 'Only formally admitted accelerated dual-program students may use the accepted graduate courses toward both degrees, with grade B or better; below B counts only toward the undergraduate degree and a required graduate course must be repeated later. Maintain the stated cumulative GPA (3.0 for master’s, 3.5 for PhD routes). Before admission students need the published junior-standing/two-full-semester condition and five completed major courses. BS/MS permits three graduate courses at GPA 3.0 to below 3.2 and four at 3.2 or higher; BS/MBA permits four at GPA 3.0; BS/PhD permits four at GPA 3.5. Required graduate, undergraduate and Vice Provost approvals and separate graduate admission remain conditions. This optional route does not create new universal business-degree requirements.'),
 ('expired-transfer','Expired transfer-credit completion plans', ['Expired Credits – for students with a conferred Associate Degree','four (4) full-time semesters','at least 45 credits','five (5) full-time semesters','required to take bridge courses','unprocessed credits'], 'For admitted associate-degree transfer students with expired credits, approved applicable credits determine an advisor completion plan: all approved credits permit at most four full-time-equivalent semesters; at least 45 approved credits permit at most five. Conditional admission with bridge courses instead uses a work-appropriate plan without the five-semester expectation. Students without an associate degree may request departmental review of previously unprocessed outside credits after admission; a request does not grant credit. These conditional paths do not shorten the ordinary degree for all students.'),
 ('online-campus','Online-course campus eligibility', ['Enrollment in Virtual Campus courses is restricted to Virtual Campus students','Newark Campus students are not eligible to register for Virtual Campus courses','Obtain special permission from the home department'], 'Online sections retain campus eligibility: Virtual Campus enrollment is for students admitted to a fully online program; Newark Campus students cannot register for Virtual Campus sections. A Virtual Campus student seeking another campus needs the published campus-change or home-department permission process. Taking courses online alone does not change the admitted campus.'),
 ('major-change','Course exclusion on change of major', ['Courses that only apply to the previous program may be excluded','including GER courses, may not have their grades excluded','will have its previous exclusion reversed'], 'On an approved major change, the new advisor determines whether previous-program-only courses may be excluded from cumulative GPA. Courses applying to the new program, including GER, cannot be excluded. A later applicable major change or permitted retake reverses exclusion. Exclusion does not erase the transcript or waive current degree requirements.'),
]
ADVISOR_RULES=[
 ('outside-mtsm','MTSM outside-course approval', ['NJIT students are expected to complete all MTSM courses at NJIT','only be considered during the summer','only in exceptional cases','not offered by NJIT during that summer term','at least eight (8) weeks in duration','signed approval form prior'], 'MTSM courses are expected at NJIT. An equivalent elsewhere is exceptional, considered only during summer when unavailable at NJIT, and requires prior MTSM approval and a signed outside-course form. The student must demonstrate inability to take it in fall/spring; the outside course must last at least eight weeks. Without prior signed approval no transfer is granted. The separately mentioned extenuating-circumstance Rutgers request is a permission route, not a waiver already granted.'),
 ('nonbusiness-transfer','Nonbusiness outside courses', ['non business courses at another school','appropriate department that offers the equivalent NJIT course','submit your transcript to the NJIT Registrar'], 'For nonbusiness courses elsewhere, obtain the outside-course form and approval from the NJIT department offering the equivalent, then send the completed-course transcript to the Registrar. Central transfer, residence and summer rules continue to apply.'),
 ('registration-permits','Advising and conditional registration permits', ['Credit overloads will need to be approved by your Academic Advisor','more than 19 credits','Prerequisites','Major','Honors Cohort','Repeat Limit','two or more times','Year (Class)'], 'Advisor approval is required for credit overload above 19 credits. Registration restrictions for prerequisites, major, honors cohort, repeat attempts and class standing use a permit request; a request is not approval. The two-attempt registration message is a permit trigger, not a replacement for the catalog’s four-attempt maximum.'),
]
PETITION_RULES=[
 ('substitution-petition','MTSM substitution, waiver and independent-study petitions', ['Substitution of unapproved course(s) for MTSM Program Requirements','Waiver of course','attach a mini syllabus','approved by the instructor prior to the start of the semester','petition decisions are final','does not constitute a guarantee of approval'], 'Unapproved substitutions or course waivers require an MTSM academic petition and decision; filing does not guarantee approval. Independent-study requests need a mini-syllabus approved by the instructor before the semester. Committee decisions are final and recorded through the advisor/DegreeWorks process. No specific substitution, duplicate allocation or waiver is inferred from this procedure.'),
]


def parse(html,kind):
    if kind=='catalog':root=content(html,'Academic Policies and Procedures');rows=CATALOG_RULES
    elif kind=='advising':
        soup=BeautifulSoup(html,'html.parser')
        headings=[h for h in soup.select('h4') if clean(h.get_text(' ',strip=True))=='Undergraduate Advising']
        if len(headings)!=1:raise ValueError('NJIT undergraduate advising scope missing')
        root=headings[0].parent;rows=ADVISOR_RULES
    else:root=content(html,'Petition');rows=PETITION_RULES
    sid=PID+'-closure-'+kind
    result=[]
    for key,title,phrases,summary in rows:
        require_phrases(root,phrases)
        result.append(rule(PID+'-closure-'+key,title,sid,kind='note',summary=summary))
    return {'id':PID,'requirements':result,'courses':[]}


def compose(previous,html):
    old=previous(html);new=parse(html,'catalog')
    if {r['id'] for r in old.get('requirements',[])} & {r['id'] for r in new['requirements']}:raise ValueError('Duplicate NJIT policy closure')
    return {**old,'requirements':old.get('requirements',[])+new['requirements']}


def register(parsers):
    parsers[BASE]=partial(compose,parsers[BASE])
    parsers[ADVISOR_URL]=partial(parse,kind='advising')
    parsers[PETITION_URL]=partial(parse,kind='petition')
