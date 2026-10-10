"""Observe selected degree-wide policies on Penn's current academic-services host."""
import re
from atlas.adapters.national_curriculum_common import content,require_phrases,clean
from .common import req,penn_course
PID='penn-bse-ai'
URL='https://academics.engineering.upenn.edu/ugrad/student-handbook/'
SID=PID+'-canonical-handbook'
# Each note is a short review paraphrase guarded by the local, numbered handbook section.
POLICIES=[
(12,'catalog-cohort','Applicable curriculum and major changes',['entering year determines','current academic advisor','Undergraduate Chair'],'Use the curriculum associated with the Penn entering catalog year. Major changes require the field-of-study form and meetings with the current advisor and receiving program chair.'),
(21,'credit-away','Credit away and transfer residence',['up to 4 course units','only be taken during the summer term','minimum grade of "C"','at least one-half of the total courses required for graduation at Penn'],'Credit away is limited to four course units for students entering Fall 2020 or later, requires prior department approval, and is summer-only with at least C. Penn summer plus credit away cannot exceed four units per summer. Two-year-institution, high-school-era, leave-of-absence and academic-drop coursework is excluded. External transfer students must complete at least half their graduation courses at Penn; those transferring five or more courses cannot take further credit away. Failed Penn courses cannot be cleared elsewhere. Approved study abroad and the Quaker Consortium have separate policies.'),
(24,'handbook-dual-major','Engineering dual-major rules',['ARIN students are not eligible for dual majors with ASCS, CSCI, NETS, or SSE','minimum of 22 Engineering courses','No course may be triple counted'],'ARIN cannot dual major with ASCS, CSCI, NETS or SSE. An allowed Engineering dual major must satisfy both curricula and at least 22 Engineering courses, with at most one 1000-level course outside the two majors. One senior-design project suffices; use the larger unit requirement when they differ. Apply with an approved academic plan by the start of junior year or 20 relevant units. Generally a 3.0 cumulative GPA is required. No course may count toward more than two degrees/majors.'),
(26,'engineering-ethics-scope','Engineering ethics: source discrepancy',['EAS 2030 Engineering Ethics','CIS 4230/5230','ASCS, BE, CMPE, CSCI, DMD and NETS students only'],'The handbook permits EAS 2030 for Engineering ethics and permits overlap with SS/H/TBS, without extra degree units. It limits CIS 4230/5230 ethics eligibility to a named list that omits ARIN, although the AI program lists CIS 4230 in its own ethics pool. Preserve this unresolved program/college discrepancy rather than silently overriding either source. VIPER has separate VIPR 1200/1210 permission and those courses cannot be SS/H.'),
(29,'uncleared-grades','Uncleared grades and incomplete work',['may not graduate with an uncleared failure or unsatisfactory','may not graduate with an uncleared “I”','may not graduate with an uncleared “NR”','Beginning with the Summer 2026 term','Grade Mode Change Deadline'],'Graduation requires clearing F/U, I and NR entries. Failed courses require repetition or an approved substitution; failures remain in the cumulative GPA. Starting Summer 2026, incomplete work in undergraduate Engineering courses must be completed by the following enrolled semester’s grade-mode deadline; the instructor must submit the change by that deadline or the converted F becomes permanent. Earlier I/NR conversion deadlines and any exceptions remain governed by the handbook.'),
(37,'minimum-performance','Minimum academic performance',['minimum cumulative GPA of 2.0','minimum GPA of 2.0 in "the major."','all math, science, and engineering courses','eight successfully completed course units'],'Maintain cumulative GPA of at least 2.0 and at least 2.0 across all mathematics, science and Engineering courses. Academic progress means averaging at least eight successfully completed course units each academic year.'),
(42,'pass-fail','Pass/fail limits',['total of four course units','No more than one course per term','only for courses in the Social Sciences, Humanities, Technology Business & Society (TBS), and Free Elective categories','NINTH FULL WEEK'],'At most four degree course units may be pass/fail, normally one course per term, and only in SS/H/TBS/free-elective categories. Additional pass/fail is possible for courses beyond the degree minimum; overload exceptions need a petition. D or better earns P without GPA weight, while F counts. A failed pass/fail course cannot be repeated pass/fail. Grade-mode changes must meet the ninth-week or pre-registration deadline, whichever comes first; writing changes require the registrar procedure.'),
(47,'repeated-course','Repeated courses',['may not repeat a course already passed (D or better)','repeats a substantial part'],'Do not repeat a passed course (D or better), or take a course substantially repeating earlier material; related later courses should have higher-level content.'),
(54,'ssh-breadth','Humanities/social science breadth applicability',['breadth requirement has been discontinued for some majors','still in place for all curricula with 40 CUs'],'The handbook’s two-social-science/two-humanities breadth rule is explicitly retained for 40-unit curricula and waived for some others. The AI degree lists 37 units; its exact breadth applicability needs department confirmation. The department-based SS/H classifications and exceptions are not yet fully enumerated here.'),
(55,'ssh-depth','Humanities/social science depth scope',['only applies to SEAS Curricula with 40 CU requirements'],'The handbook’s specific SSH depth rule applies only to 40-unit Engineering curricula. Do not impose it as an additional requirement on the 37-unit AI curriculum.'),
(58,'sunset','Maximum elapsed degree time',['eight-year calendar period after matriculation','petition for action for an extension'],'Complete the BAS/BSE within eight calendar years after matriculation. An extension requires a petition and review that may impose additional or replacement coursework. This differs from the AI major-change limit measured in semesters.'),
(60,'internal-transfer','Internal Engineering transfer eligibility',['external transfer student) is ineligible','minimum of eight (8) Penn course units','minimum gpa for consideration is 3.0','May 15','December 15','prior to the end of the sophomore year'],'Internal applicants need a four-year plan naming the intended major, eight completed Penn units, at least 3.0 GPA and no uncleared F/I/GR/NR. Calculus preparation and normally physics are reviewed by major and semesters completed. Students who entered Penn as external transfers cannot use this internal-transfer route. Apply before sophomore year ends; the published fall/spring entry deadlines are May 15 and December 15. Application availability is separate from eligibility.'),
(65,'writing-policy','Writing policy and grade mode',['Any WRIT course','may not use A.P. credit','Dual degree students must take the writing requirement for a grade'],'Complete a critical writing seminar, preferably in year one and no later than year two. AP credit cannot satisfy writing. Writing may be pass/fail through the registrar process by the drop deadline, but dual-degree students must take it for a grade. WRIT classification determines its distribution slot; a free-elective classification does not automatically qualify within the AI program’s five-unit SS/H distribution.')]


def parse(html):
    root=content(html,'Student Handbook');groups=[]
    for number,key,title,markers,summary in POLICIES:
        section=root.find(id='faq_'+str(number))
        if section is None:raise ValueError('Handbook policy section missing: '+str(number))
        require_phrases(section,markers)
        groups.append(req(PID,key,title,SID,kind='note',summary=summary))
    courses,writing_groups=parse_writing(root)
    return dict(id=PID,courses=courses,requirements=groups+writing_groups)


def parse_writing(root):
    groups=[]
    section=root.find(id='faq_64')
    if section is None:raise ValueError('Writing course list missing')
    table=section.find('table')
    if table is None:raise ValueError('Writing course table missing')
    courses=[];classes={}
    for row in table.find_all('tr'):
        cells=row.find_all(['td','th'],recursive=False)
        if len(cells)!=3:continue
        code=clean(cells[0].get_text(' ',strip=True));match=re.fullmatch(r'WRIT\s*(\d{4})',code)
        if not match:continue
        name=clean(cells[1].get_text(' ',strip=True));classification=clean(cells[2].get_text(' ',strip=True))
        if classification not in {'SS','H','TBS','FE','-'}:raise ValueError('Writing classification changed')
        c=penn_course('WRIT '+match[1],name,SID,URL,category='human_context');courses.append(c);classes.setdefault(classification,[]).append(c['id'])
    if not courses:raise ValueError('Writing inventory empty')
    for classification,ids in classes.items():
        groups.append(req(PID,'writing-classification-'+classification.lower().replace('-','unknown'),'Writing course classification: '+classification,SID,kind='note',course_ids=ids,summary='Handbook worksheet classification '+classification+'. These are alternatives, not an extra mandatory course list. '+('No worksheet category is supplied; obtain advising review.' if classification=='-' else 'Free elective writing does not automatically fill SS/H.' if classification=='FE' else 'Apply the program-specific distribution rules.')))
    return courses,groups
