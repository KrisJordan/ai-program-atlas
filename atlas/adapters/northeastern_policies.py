"""Observe shared Northeastern policy criteria; never enumerate invented courses.

Every profile is scoped to an official policy panel/section. Numeric criteria are
observed, semantic guard changes fail for review, and no audit is emitted.
"""
from __future__ import annotations
import re
from bs4 import BeautifulSoup

BASE='https://catalog.northeastern.edu/undergraduate/'
PROFILES={
    'universitywide':(BASE+'university-academics/university-wide-requirements/','Universitywide Requirements','textcontainer'),
    'nupath':(BASE+'university-academics/general-education-requirements/','General Education Requirements','nupathtextcontainer'),
    'experiential':(BASE+'academic-policies-procedures/experiential-learning-graduation-requirement/','Experiential Learning Graduation Requirement','textcontainer'),
    'graduation':(BASE+'academic-policies-procedures/graduation-requirements/','Graduation Requirements','textcontainer'),
    'combined':(BASE+'academic-policies-procedures/degrees-majors-minors/','Degrees, Majors, and Minors','textcontainer'),
    'progression':(BASE+'academic-policies-procedures/progression-standards/','Academic Progression Standards','textcontainer'),
}


def text(node):
    # CourseLeaf track-change spans sometimes split a single word into spans.
    return re.sub(r'\s+',' ',node.get_text('',strip=False)).strip()


def need(prose,*phrases):
    if any(phrase not in prose for phrase in phrases):
        raise ValueError('Reviewed policy semantics changed or missing')


def match(pattern,prose):
    found=re.search(pattern,prose,re.I)
    if not found:raise ValueError('Expected policy criterion missing')
    return found


def number(value):
    values=dict(one=1,two=2,three=3,four=4,five=5,six=6,seven=7,eight=8,nine=9,ten=10)
    if value.lower() in values:return values[value.lower()]
    if re.fullmatch(r'\d+(?:\.\d+)?',value):return float(value)
    raise ValueError('Unsupported policy number')


def section(panel,title):
    heading=next((h for h in panel.find_all(['h2','h3','h4']) if text(h)==title),None)
    if heading is None:raise ValueError('Expected policy section missing')
    parts=[]
    for n in heading.next_siblings:
        if getattr(n,'name',None) in ('h2','h3','h4') and int(n.name[1])<=int(heading.name[1]):break
        if getattr(n,'name',None):parts.append(text(n))
    return ' '.join(parts)


def parse_policy(html,*,program_id,profile):
    if profile not in PROFILES:raise ValueError('Unknown Northeastern policy profile')
    url,heading,panel_id=PROFILES[profile];soup=BeautifulSoup(html,'html.parser')
    title=soup.find(id='site-title');h1=title.find('h1') if title else None
    panel=soup.find(id=panel_id)
    if h1 is None or text(h1)!=heading or panel is None:raise ValueError('Expected official policy identity/panel missing')
    for n in panel.find_all(['nav','aside','script','style']):n.decompose()
    prose=text(panel);sid=program_id+'-'+profile+'-policy';rows=[]
    root_id=program_id+'-req-policy-'+profile
    def add(key,title,summary,*,kind='note',credits=None,parent=None):
        rid=program_id+'-req-policy-'+key
        rows.append(dict(id=rid,parent_id=parent or root_id,title=title,kind=kind,count=None,credits=credits,
            credit_unit='semester_hours' if credits is not None else 'unknown',category='other',source_id=sid,source_text=None,summary=summary,course_ids=[]))
        return rid
    add(profile,heading,'Published university policy criteria; apply alongside the concrete program requirements.',kind='all')
    rows[0]['parent_id']=None
    if profile=='universitywide':
        need(prose,'Individual program requirements may exceed','experiential learning graduation requirement')
        credits=number(match(r'Minimum (\d+) total semester hours required',prose)[1])
        gpa=match(r'Minimum (\d+\.\d+) GPA required',prose)[1]
        residency=number(match(r'minimum of (\d+) Northeastern University semester hours',prose)[1])
        add('university-credit-minimum','University minimum degree credits',f'At least {credits:g} total semester hours; a higher published program minimum controls.',credits=credits)
        add('university-gpa','University graduation GPA',f'Minimum overall GPA {gpa} for graduation.')
        add('university-residency','Northeastern-earned credit minimum',f'Earn at least {residency:g} Northeastern University semester hours for the bachelor’s degree.',credits=residency)
        add('university-all-requirements','Applicable program and experiential rules','Complete university and program requirements, including the separate experiential graduation requirement. These minima do not replace higher program-specific requirements.')
    elif profile=='nupath':
        need(prose,'competency based rather than course based','NUpath courses may not be taken pass/fail','There are no level restrictions or semester-hour restrictions','No course completed on a satisfactory/unsatisfactory grading basis','Transfer credits cannot be used to fulfill the capstone or experiential requirements','only the first-year writing requirement can be met by transferred or placement test credits')
        h=next((h for h in panel.find_all('h2') if text(h)=='NUpath Requirements'),None)
        ul=h.find_next_sibling('ul') if h else None
        names=[text(li) for li in ul.find_all('li',recursive=False)] if ul else []
        expected=int(match(r'set of (\d+) competencies',prose)[1])
        if len(names)!=expected:raise ValueError('NUpath competency list/count mismatch')
        for index,name in enumerate(names):add(f'nupath-competency-{index+1}',name,'Satisfy this published NUpath competency through an approved course or eligible university-recognized fulfillment; requirements may overlap only within the published limits.')
        capstone=section(panel,'Demonstrating Thought and Action in a Capstone')
        need(capstone,'Each student must take at least one course designated as a capstone experience','Students must complete a capstone in their major','the units may specify in which major to take the capstone or may leave the choice to the student')
        target=next((r for r in rows if r['title']=='Demonstrating Thought and Action in a Capstone'),None)
        if target is None:raise ValueError('NUpath capstone competency identity changed')
        target['summary']='Complete at least one designated capstone course in the major. For combined or double majors, the academic units may specify the major for the capstone or allow the student to choose; this policy does not require an extra capstone in every discipline.'
        entry=match(r'freshmen who entered in fall (\d{4}) and later',prose)[1]
        add('nupath-applicability','NUpath applicability',f'Applies to first-year entrants from fall {entry}; previously admitted students with another core and transfer students with earlier entry years follow their applicable rules.')
        add('nupath-eligibility','Competency-based course eligibility','Use approved NUpath attributes in course/section listings. Major, minor, concentration or elective coursework can qualify without additional course-level or semester-hour restrictions. Pass/fail and satisfactory/unsatisfactory coursework cannot qualify. This is an eligibility criterion, not an invented extra course pool.')
        maximum=number(match(r'single course can count for up to (\w+) of the following requirements',prose)[1])
        transfer=number(match(r'Up to (\w+) of the following eight requirements',prose)[1])
        add('nupath-overlap','NUpath overlap limits',f'One course may fulfill at most {maximum:g} of the first eight competencies; writing-intensive-in-major, capstone and experiential attributes can additionally overlap without that cap.')
        add('nupath-transfer','NUpath transfer and examination limits',f'Transfer/placement credit may fulfill at most {transfer:g} of the first eight competencies using Northeastern course equivalents. Transfer cannot fulfill capstone or experiential requirements; among writing requirements, only first-year writing permits transfer/placement credit.')
        first=section(panel,'First-Year Writing Requirement');need(first,'grade of C or better','qualifying advanced placement scores','appropriate transfer credit','guided self-placement','requires students bring an essay')
        add('nupath-first-year-writing','First-year writing standard','Complete an approved first-year writing option with C or higher, or qualifying advanced placement/transfer credit. The writing program uses guided self-placement and requires an essay at the first class meeting.')
        advanced=section(panel,'Advanced Writing Requirement');need(advanced,'satisfy the first-year requirement','at least junior or senior standing','Transfer credit cannot be used','C or better')
        hours=number(match(r'minimum of (\d+) semester hours',advanced)[1])
        add('nupath-advanced-writing','Advanced writing standard',f'Complete advanced writing with C or higher. Enrollment requires first-year writing, at least {hours:g} academic semester hours including the enrollment semester, and junior/senior standing. Transfer credit cannot satisfy advanced writing; choose the appropriate program-approved section with advising.')
        wi=section(panel,'Writing-Intensive Courses in the Major');count=number(match(r'at least (\w+) additional writing-intensive courses',wi)[1])
        add('nupath-major-writing','Writing-intensive work in the major',f'Complete at least {count:g} additional writing-intensive major courses, beyond first-year and advanced writing. Approved major courses may also fulfill other NUpath attributes within the overlap rules.')
    elif profile=='experiential':
        need(prose,'program on a campus in the U.S.','one qualifying Experiential Learning Engagement','Co-op','Internship','Clinical placement','Approved Courses with required industry partnership project','Online or primarily online programs','Mills College and Marymount Manhattan College continuing students','London dual-degree students')
        choice=add('experiential-choice','Qualifying experiential engagement','Complete one qualifying university experiential engagement; the concrete program may impose additional or more specific experience requirements.',kind='alternative')
        for key,label,summary in [('co-op','Co-op','Complete a qualifying co-op.'),('internship','Internship','Complete a qualifying internship.'),('clinical','Clinical placement','Complete a qualifying clinical placement.'),('industry-project','Approved industry-partnership course','Complete an approved course requiring an industry-partnership project.')]:add('experiential-'+key,label,summary,parent=choice)
        add('experiential-scope','Experiential requirement scope','The standard U.S.-campus matriculated degree rule applies to these Boston degree programs. Published exceptions cover nondegree, CPS undergraduate, online/primarily online, PhD and certificate programs, continuing Mills/Marymount Manhattan students, and London dual-degree students; assess any individual exception against that policy.')
    elif profile=='graduation':
        need(prose,'be in good standing','clear all financial, experiential education, and disciplinary deficiencies','student may petition their college for permission','academic advising office','All qualified students must submit a graduation application')
        add('graduation-clearance','Graduation and diploma clearance','Meet academic, program, experiential and residency requirements and remain in good standing. Clear financial, experiential-education and disciplinary deficiencies before diploma receipt; the college advising office reviews the degree audit.')
        add('graduation-coursework','Coursework after matriculation','Complete degree coursework at Northeastern, an entity with a formal contractual/consortial/partnership relationship, or approved Northeastern study abroad. Taking another accredited institution’s course requires a college petition under the published exceptions.')
        add('graduation-application','Graduation application','Submit the graduation application by the published deadlines to receive the diploma, including when not attending the optional ceremony.')
    elif profile=='combined':
        combined=section(panel,'Combined Majors');need(combined,'one major','Most combined majors allow the student to choose the home college','one degree, and one diploma','multiple points of curricular integration')
        each=number(match(r'at least (\w+) courses from each',combined)[1]);overlap=number(match(r'No more than (\w+) courses may count for both disciplines',combined)[1]);total=number(match(r'at least (\d+) courses in the combined major',combined)[1])
        add('combined-design','Combined-major discipline and integration criteria',f'The combined major includes at least {each:g} courses from each participating discipline, at most {overlap:g} courses counting in both, and at least {total:g} courses overall, with multiple curricular integration points. These are program-design/fulfillment criteria, not additional courses to add to the published degree plan.')
        add('combined-home-college','Designated home college','A designated home college registers and graduates the student; most combined majors allow a home-college choice. Catalog hosting context does not establish an individual student’s choice. Apply that college’s published rules and approved program of study.')
        add('combined-one-award','Combined-major award identity','Completion earns one major, one degree and one diploma; the combined major and home college appear on transcript and diploma. Preserve the concrete program’s BS or BSEnvE designation.')
    elif profile=='progression':
        need(prose,'minimum cumulative GPA of 2.000','Individual colleges may have additional requirements','at the end of each semester of their freshman year','Academic Standing Committee')
        gpa=match(r'overall GPA of (\d+\.\d+)',prose)[1];later=match(r'minimum cumulative GPA of (\d+\.\d+)',prose)[1];hours=number(match(r'Earn at least (\d+) semester hours in the semester just completed',prose)[1])
        add('progression-standing','University academic standing',f'Maintain overall GPA {gpa} at each first-year semester end and cumulative GPA {later} thereafter; earn at least {hours:g} semester hours in the completed semester. Individual colleges/programs may add progression criteria.')
        add('progression-incomplete','Incomplete grades and probation','When pending incomplete credits leave a student below full-time status, GPA determines temporary probation until the incomplete is resolved. Full-time students missing good-standing criteria are placed on academic probation for the following semester.')
        need(prose,'after two full-term academic semesters','below a 1.000 GPA or fewer than 4 earned semester hours','at the discretion of their college')
        appeal=number(match(r'no more than (\w+) additional full-term academic semester',prose)[1])
        add('progression-dismissal','Dismissal and appeal policy',f'Two full-term semesters of continuing probation may lead to dismissal. A GPA below 1.000 or fewer than four earned hours in a semester or cumulatively may also trigger college-discretionary dismissal; pending incompletes are excluded. Students may appeal to their college Academic Standing Committee. A probation appeal generally allows no more than {appeal:g} additional full-term academic semester to regain good standing.')
    return dict(id=program_id,courses=[],requirements=rows,curriculum_status='partial',notes=['Policy-only source observation; review applicability and merge with program/family requirements. No review audit or completeness claim is emitted.'])


def register_policy_sources(program_id):
    """Each program adapter keeps separately rerunnable observations and evidence."""
    return {url:(lambda html, profile=profile:parse_policy(html,program_id=program_id,profile=profile)) for profile,(url,_,_) in PROFILES.items()}
