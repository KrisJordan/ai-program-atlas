"""UNC's visible CourseLeaf minor, course inventory and linked policy sections.

Observations never confer reviewer completeness. Changed policy clauses fail
closed; description paraphrases are bound to hashes of the observed description.
"""
import hashlib
import re
from bs4 import BeautifulSoup, NavigableString

PROGRAM_ID = 'unc-ai-minor'
CATALOG = 'https://catalog.unc.edu/undergraduate/programs-study/artificial-intelligence-minor/'
COURSES = 'https://catalog.unc.edu/courses/data/'
DEGREE = 'https://catalog.unc.edu/undergraduate/degree-requirements/'
TRANSFER = 'https://catalog.unc.edu/policies-procedures/credit-evaluation/'
REGISTRATION = 'https://catalog.unc.edu/policies-procedures/registration-enrollment-withdrawal/'
GRADES = 'https://catalog.unc.edu/policies-procedures/attendance-grading-examination/'
SOURCES = (CATALOG, COURSES, DEGREE, TRANSFER, REGISTRATION, GRADES)
CODES = ('DATA 110','DATA 117','DATA 120','DATA 317','DATA 320','DATA 420I','DATA 520')
DATA117_TITLE = 'AI Unlocked for Curious Minds'
DATA117_APPLICATIONS_DESCRIPTION_HASH = '38077a91a33fe0a381dca19e91db40b11ad499a445e1b4d68b029cb4ac1237c2'
CATEGORIES = ('foundations','applications','human_context','applications','human_context','human_context','human_context')

def text(node):
    return re.sub(r'\s+', ' ', node.get_text(' ', strip=True)).strip() if node else ''

def content(html, heading):
    soup = BeautifulSoup(html, 'html.parser')
    if soup.select('input[type="password"]') or re.search(r'access denied|verify you are human|sign in to continue', text(soup), re.I):
        raise ValueError('Access or authentication page is not curriculum evidence')
    main = soup.select_one('#content')
    if not main or text(main.find('h1')) != heading:
        raise ValueError('Expected visible UNC catalog heading absent')
    return main

def section(main, heading):
    h = next((h for h in main.find_all(['h2','h3']) if text(h)==heading), None)
    if h is None: raise ValueError('Expected policy section absent: '+heading)
    out=[]
    for n in h.next_elements:
        if getattr(n,'name',None) in ['h2','h3']: break
        if isinstance(n, NavigableString) and h not in n.parents:
            out.append(str(n))
    return re.sub(r'\s+', ' ', ' '.join(out)).strip()

def rule(suffix,title,summary,source='catalog',kind='note',course_ids=None,parent=None,count=None,credits=None,category='other'):
    return dict(id=PROGRAM_ID+'-'+suffix,parent_id=parent,title=title,kind=kind,count=count,credits=credits,credit_unit='semester_hours' if credits is not None else 'unknown',category=category,source_id=PROGRAM_ID+'-'+source,source_text=None,summary=summary,course_ids=course_ids or [])

def cid(code): return 'unc-'+code.lower().replace(' ','-')

def parse(html):
    m=content(html,'Artificial Intelligence Minor')
    body=m.select_one('#requirementstextcontainer')
    if body is None: raise ValueError('Minor requirements tab absent')
    table=body.select_one('table.sc_courselist')
    if table is None: raise ValueError('Minor course table absent')
    core=[]; electives=[]; courses=[]; choice=None; total=None; pool=False
    for row in table.select('tbody tr'):
        rt=text(row);cells=row.find_all('td',recursive=False)
        if 'Select ' in rt:
            match=re.fullmatch(r'Select (\w+) courses from the following list: (\d+)',rt)
            if not match or match[1] not in {'one','two','three','four'}: raise ValueError('Unreviewed choice rule')
            choice=({'one':1,'two':2,'three':3,'four':4}[match[1]],float(match[2]));pool=True
        a=row.select_one('td.codecol a.code')
        if a:
            code=text(a); namecell=BeautifulSoup(str(cells[1]),'html.parser')
            for sup in namecell.select('sup'):sup.decompose()
            name=text(namecell);hours=text(cells[-1]); credit=float(hours) if re.fullmatch(r'\d+(?:\.\d+)?',hours) else None
            category=dict(zip(CODES,CATEGORIES)).get(code,'other')
            if code=='DATA 117' and name!=DATA117_TITLE:category='other'
            courses.append(dict(id=cid(code),code=code,name=name,description=None,prerequisites=None,credits=credit,credit_unit='semester_hours' if credit is not None else 'unknown',category=category,source_id=PROGRAM_ID+'-catalog',url=CATALOG,public_site=None,syllabus=None))
            (electives if pool else core).append(cid(code))
        if 'listsum' in row.get('class',[]):total=float(text(cells[-1]))
    if not core or not electives or not choice or total is None:raise ValueError('Incomplete minor inventory')
    bt=text(body)
    if not all(p in bt for p in ['at least nine hours','2.000','Honors version available','Enrollment and GPA restrictions may apply']):
        raise ValueError('Minor policy changed; review required')
    req=[rule('total','Minor total',f'Complete the published {total:g} semester-hour minor. The elective pool is not an additional requirement.',kind='all',credits=total),rule('core','Required core',f'Complete all {len(core)} core courses.',kind='all',course_ids=core,parent=PROGRAM_ID+'-total',category='other'),rule('electives','Minor electives',f'Choose {choice[0]} courses totaling {choice[1]:g} semester hours from the published pool.',kind='choose_courses',count=choice[0],credits=choice[1],course_ids=electives,parent=PROGRAM_ID+'-total',category='electives'),rule('residence','Minor residence','Complete at least nine core semester hours at UNC–Chapel Hill.'),rule('gpa','Minor GPA','Earn at least 2.000 cumulative GPA in minor core coursework.'),rule('honors','Honors alternatives','An honors version meets the same requirement; applicable honors enrollment and GPA restrictions still apply. DATA 110 and DATA 120 are marked as offering honors versions.')]
    result = dict(id=PROGRAM_ID,title='Artificial Intelligence Minor',program_kind='minor',award_level='minor',courses=courses,requirements=req)
    overview = m.select_one('#textcontainer')
    statements = [text(li) for li in overview.select('li')] if overview else []
    observed_hash = hashlib.sha256('\n'.join(statements).encode()).hexdigest()
    if observed_hash == '3d5bb8d1116c5c4c1e32bd06693d67e3ae51bee5b3279dd5a91049eeeb16d0c8':
        result['outcomes'] = [{'text': 'Explain the principles behind AI operation.', 'kind': 'source_stated', 'statement_type': 'learning_outcome', 'source_id': 'unc-ai-minor-catalog', 'locator': 'Overview: explicitly introduced learning outcomes'}, {'text': 'Choose suitable AI tools for different tasks.', 'kind': 'source_stated', 'statement_type': 'learning_outcome', 'source_id': 'unc-ai-minor-catalog', 'locator': 'Overview: explicitly introduced learning outcomes'}, {'text': 'Use current AI tools competently and adapt to new developments.', 'kind': 'source_stated', 'statement_type': 'learning_outcome', 'source_id': 'unc-ai-minor-catalog', 'locator': 'Overview: explicitly introduced learning outcomes'}, {'text': 'Evaluate AI-generated results critically.', 'kind': 'source_stated', 'statement_type': 'learning_outcome', 'source_id': 'unc-ai-minor-catalog', 'locator': 'Overview: explicitly introduced learning outcomes'}, {'text': 'Explain AI’s advantages and disadvantages for society.', 'kind': 'source_stated', 'statement_type': 'learning_outcome', 'source_id': 'unc-ai-minor-catalog', 'locator': 'Overview: explicitly introduced learning outcomes'}]
    return result

# Reviewed paraphrases only apply to the exact observed description; a changed
# description remains unknown in the candidate until separately reviewed.
DESCRIPTION_PARAPHRASES = {'79701badb351894e2d18f785020c0cdc1c27bac802443e356f379fadc1658bee': 'Introduces data-science reasoning, statistical and computational ideas, ethical practice and communicating results.', '38077a91a33fe0a381dca19e91db40b11ad499a445e1b4d68b029cb4ac1237c2': 'Introduces AI concepts, practical uses, limitations and social implications for students across disciplines.', 'a5d8afd921e7f978f948280ba8321d1a168351c3f075fdc15acb032ba210e807': 'Applies ethical reasoning to data-intensive systems, including fairness, transparency and accountability.', '711a55f046fbf0c7da72fc0d89afdfdaf1afd04b4d0420a3686cfb503cb9a3a0': 'Uses accessible AI tools for research, writing, analysis, media and coding, with practical prompt design.', '9d07e156757315bce1c8219ab496d08276337099ea73d4d61aa6d6082cc3a3d0': 'Examines reliable and accountable AI design that supports human needs and reduces harms.', 'c2a37cec3345d4d43f6d3abe9c58fb9665c23831adfddc44b51d6ce856d65b91': 'Uses interdisciplinary research to examine failures and social consequences of data-driven systems; no technical background is required.', '414e02eb0d4a0e406c212ded040972d74c567bad79bbf5f08e4b0d4294da416e': 'Team research examines socially responsible AI through a semester project with faculty and graduate teaching support.'}

def parse_courses(html):
    m=content(html,'DATA SCIENCE AND SOCIETY (DATA)');out=[]
    for block in m.select('.courseblock'):
        code=text(block.select_one('.detail-code')).rstrip('.')
        if code not in CODES:continue
        title=text(block.select_one('.detail-title')).rstrip('.')
        credit=re.fullmatch(r'(\d+(?:\.\d+)?) Credits?\.',text(block.select_one('.detail-hours')))
        if not title or not credit:raise ValueError('Unrecognized course identity or credit amount')
        description=text(block.select_one('.courseblockextra'))
        digest=hashlib.sha256(description.encode()).hexdigest()
        prereq=text(block.select_one('.detail-requisites'))
        category=dict(zip(CODES,CATEGORIES))[code]
        # This is a candidate proposal, bound to the actually reviewed evidence.
        if code=='DATA 117' and (title!=DATA117_TITLE or digest!=DATA117_APPLICATIONS_DESCRIPTION_HASH):category='other'
        out.append(dict(id=cid(code),code=code,name=title,description=DESCRIPTION_PARAPHRASES.get(digest),prerequisites=prereq.removeprefix('Requisites: ').strip() or None,credits=float(credit[1]),credit_unit='semester_hours',category=category,source_id=PROGRAM_ID+'-courses',url=COURSES,public_site=None,syllabus=None))
    if {c['code'] for c in out} != set(CODES):raise ValueError('Listed minor course block missing')
    return dict(id=PROGRAM_ID,courses=out)

# Each recipe is scoped to its visible policy heading. Missing or materially
# changed evidence is queued as a failed observation, never replayed from a seed.
POLICIES = {
 DEGREE: ('degree','Undergraduate Degree Requirements',[
 ('Requirements for Minors','minor-combinations','Minor combinations','At most two minors are allowed. Academic units may exclude particular major/minor combinations. A College of Arts and Sciences student needs the professional school’s permission for a minor there.',('no more than two minors','may exclude','permission')),
 ('Requirements for Minors','overlap','Exclusive minor work','More than half of both core courses and credit hours, including cross-listed work, must be exclusive to this minor versus other majors/minors. Units may further restrict general-education overlap.',('More than half (not merely half)','credit hours and courses','General Education')),
 ('Requirements for Minors','exam-credit','Exam credit limit','At most one course of 3–4 BE credit hours can count toward a minor.',('No more than one BE credit course','three to four')),
 ('Requirements for Minors','minor-pass','Pass/fail in a minor','Gateway, prerequisite and additional-requirement courses cannot be elected pass/fail. One PS course, but not LP, may meet minor core requirements.',('Gateway','not LP','one course')),
 ('Requirements for Minors','declaration','Declaration timing','Declaring by early junior year is encouraged, not presented as a mandatory admission deadline.',('encouraged','early in the junior year')),
 ('Combining Majors and Minors','permissions','Cross-school permissions','Professional-school students need their school and the relevant receiving school’s permission for an outside minor; a College of Arts and Sciences minor requires that college’s permission too.',('permission from their professional school and the College','permission from both professional schools')),
 ('Combining Majors and Minors','combinations','Concurrent subjects and overlap counting','College of Arts and Sciences students may study at most three subjects in the listed major/minor combinations. Same-unit combinations are subject to departmental restrictions and the 45-hour subject limit. A lecture/lab combination counts as one course for overlap.',('up to three subjects','45 credit hours','counted as one course')),
 ]),
 TRANSFER: ('transfer','Credit and Evaluation',[
 ('Hours of Credit','credit-unit','Credit unit','UNC values degree credit in semester hours; the catalog defines classroom, independent work and laboratory/studio expectations.',('semester hours','two hours','three hours')),
 ('Awarding Transfer Credit','transfer-approval','Transfer approval','Transfer credit requires an official final transcript; supporting course documentation may be required. Current students need term-specific advance course approval, and graduation clearance deadlines apply.',('official transcript','course pre-approval form','graduation clearance deadlines')),
 ('Awarding Transfer Credit','transfer-grade','External grades and credit','External courses require C or higher. External grades do not enter UNC cumulative GPA. UNC converts other credit scales into semester hours; zero-credit courses do not transfer.',('“C” or higher','not computed','converted into semester credit hours','no credit hours')),
 ('Awarding Transfer Credit','transfer-limit','Transfer ceiling','Once the 75-hour transfer maximum is reached, no additional credit or substitutions are posted; this university ceiling does not replace the minor’s nine-hour UNC residence rule.',('75 hours','No substitutions')),
 ('Overall Guidelines for Evaluations of Undergraduate Transfer of Credit','equivalence','Transfer equivalence and age','Equivalence normally uses 70% content alignment, subject to accreditation, sequence, rigor and discipline exceptions. Upper-division courses and courses at least ten years old require department review. Approved study abroad is handled by the designated global offices; international transcripts require a course-by-course WES evaluation.',('70%','upper division','10 years','World Education Services')),
 ('Credit by Departmental Examination','department-exam','Departmental examination credit','Department and school/college approval is required at least 30 days before an exam. The exam must precede the final semester or full summer session before graduation.',('30 days','before the beginning of the last semester')),
 ]),
 REGISTRATION: ('registration','Registration, Enrollment, and Withdrawal',[
 ('Repeating Course Enrollments','repeats','Repeated courses','A nonrepeatable course earns degree credit only once, using the highest passing grade (later attempt if tied); all attempt grades remain in cumulative GPA.',('highest passing grade','latter attempt','all attempts')),
 ]),
 GRADES: ('grades','Attendance, Grading, and Examination',[
 ('Pass/Fail Option','ps-definition','PS/LP grading','PS corresponds to A–C; LP corresponds to C−, D+ or D. PS/LP do not affect GPA; F does. One PS core course may count, and students cannot change a major/minor merely to elect pass/fail. Elections are final.',('A through C','C-, D+, or D','All PS/LP/F declarations are final','for the purpose')),
 ('Pass/Low Pass/Fail Declaration Procedure','ps-deadline','Pass/fail declaration window','Submit the ConnectCarolina form from the fifth class day through the end of week eight; consulting an advisor is recommended.',('fifth day','eighth week','ConnectCarolina')),
 ('Regulations Governing the Pass/Low Pass/Fail Option','ps-limits','Pass/fail university limits','At most one student-elected course per semester; 23 total pass/fail hours, with at most 16 elected and 13 established hours. Summer, honors and interinstitutional courses, general-education requirements, previously passed letter-graded courses and declared gateway/prerequisite/additional requirements cannot be elected pass/fail.',('one student-elected','23 total','16 hours','13 hours','Summer School courses','honors course','interinstitutional')),
 ('Other Grades and Notations','placement','Exam and placement distinctions','BE can award credit but does not meet minor GPA requirements; PL placement alone awards no credit hours.',('BE credit may not be used','PL does not confer credit hours')),
 ])
}

def parse_policy(html,url):
    source,heading,recipes=POLICIES[url];m=content(html,heading);req=[]
    for section_heading,suffix,title,summary,guards in recipes:
        observed=section(m,section_heading)
        if not all(g in observed for g in guards):raise ValueError('Policy evidence changed: '+suffix)
        req.append(rule(suffix,title,summary,source))
    return dict(id=PROGRAM_ID,requirements=req)

SOURCE_PARSERS = {CATALOG:parse,COURSES:parse_courses}
SOURCE_PARSERS.update({url:(lambda html,url=url:parse_policy(html,url)) for url in POLICIES})
