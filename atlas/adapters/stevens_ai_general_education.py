"""Additional publicly rendered degree-policy observations for Stevens AI."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, course, rule, require_phrases
from atlas.adapters.stevens_ai_requirements import PID
from atlas.adapters.stevens_public_policies import BASE

SCHOOL='https://stevens.catalog.prod.coursedog.com/schools/computing#undergraduate-programs'
GE=BASE+'#general-education1'
ENGLISH=BASE+'#english-language-requirement-for-international-students'
PREFIXES=('First-Year Experience','Frontiers of Technology','Foundations in Writing','Computing (','Innovation and Entrepreneurship','Science or Technological','Mathematics (','Humanities and Social Sciences')


def article(html,heading):
    soup=BeautifulSoup(html,'html.parser')
    matches=[a for a in soup.find_all('article') if any(clean(h.get_text(' ',strip=True))==heading for h in a.find_all(['h1','h2']))]
    if len(matches)!=1:raise ValueError('Expected rendered Stevens article: '+heading)
    return matches[0]


def parse_general(html):
    root=article(html,'General Education');sid=PID+'-general-education';rules=[];courses={};seen=set()
    require_phrases(root,['Total Credit Hours: 29-32','Clark Scholars can use CLK 183 to substitute for PRV 101','incoming international undergraduate students','HASS 101','HASS 103 and HASS 105'])
    for row in root.find_all('tr'):
        cells=row.find_all(['td','th'],recursive=False)
        if len(cells)!=4:continue
        label=clean(cells[0].get_text(' ',strip=True));prefix=next((p for p in PREFIXES if label.startswith(p)),None)
        if prefix is None:continue
        if prefix in seen:raise ValueError('Duplicate general education category')
        seen.add(prefix)
        codes=[a+' '+b for a,b in re.findall(r'\b([A-Z]+)\s*(\d+)\b',cells[1].get_text(' ',strip=True))]
        amounts=re.findall(r'\b\d+\b',cells[2].get_text(' ',strip=True))
        names=[clean(x) for x in cells[3].get_text('\n',strip=True).split('\n') if clean(x)]
        if not codes or len(codes)!=len(amounts) or len(codes)!=len(names):raise ValueError('General education course columns do not align')
        ids=[]
        for code,name,amount in zip(codes,names,amounts):
            c=course('stevens',code,name,sid,GE,credits=int(amount));courses[c['id']]=c;ids.append(c['id'])
        suffix=str(PREFIXES.index(prefix)+1)
        rules.append(rule(PID+'-ge-category-'+suffix,label,sid,ids,kind='note',summary='University general-education framework: '+label+'. The AI plan supplies its own specific courses and distribution rules; this category is not extra credits or blanket permission to substitute these options for required AI coursework. '+('The source explicitly labels these as common examples, not an exhaustive approved list.' if 'most common' in label else 'Preserve the published selection wording above.')))
    if seen!=set(PREFIXES):raise ValueError('Missing general education category')
    clk=course('stevens','CLK 183',None,sid,GE);courses[clk['id']]=clk
    rules.append(rule(PID+'-clark-substitution','Clark Scholars first-year substitution',sid,['stevens-clk-183','stevens-prv-101'],kind='note',summary='Clark Scholars may substitute CLK 183 for PRV 101. This is a conditional substitution, not an additional universally required course.'))
    return dict(id=PID,curriculum_status='partial',courses=list(courses.values()),requirements=rules)


def parse_english(html):
    root=article(html,'English Language Requirement for International Students');sid=PID+'-international-english'
    require_phrases(root,['international students will be placed in HASS 101 during their first semester','After successful completion of HASS 101','HASS 103, followed by HASS 105','diagnostic','first week','may transfer to HASS 103','general or free elective','remaining humanities courses required for their degree program'])
    c=course('stevens','HASS 101',None,sid,ENGLISH)
    return dict(id=PID,curriculum_status='partial',courses=[c],requirements=[rule(PID+'-international-english','International-student English placement',sid,['stevens-hass-101','stevens-hass-103','stevens-hass-105'],kind='note',summary='International undergraduates enter HASS 101 in semester one, then HASS 103 and HASS 105 after successful completion. A first-week diagnostic may permit moving directly to HASS 103. HASS 101 can satisfy a general/free elective; the remaining degree-specific humanities requirements still apply.')])


def parse_school(html):
    root=article(html,'Undergraduate Programs')
    require_phrases(root,['All undergraduate students must complete General Education credits','required Humanities courses and the SUCCESS Core','School of Computing offers'])
    if not root.find('a',href='/programs/qT6Ld1CzBAhQsVKYFNVv'):raise ValueError('AI degree not identified in Computing school scope')
    return dict(id=PID,curriculum_status='partial',courses=[],requirements=[rule(PID+'-computing-ge-scope','School of Computing general-education applicability',PID+'-computing-school',kind='note',summary='The School of Computing undergraduate section lists this AI degree and explicitly applies General Education, Humanities and SUCCESS Core requirements to all undergraduate degrees. This does not rewrite separate clauses expressly limited to SES/SSB.')])


SOURCE_PARSERS={GE:parse_general,ENGLISH:parse_english,SCHOOL:parse_school}

COURSE_OPTIONS=BASE+'#course-options'
OPTION_RULES=[
 ('university-graduate-courses','Undergraduate access to graduate courses',['500-level course','at least junior standing','pre-requisite requirements','A-U section','Pre-Requisite Eligibility Override Request','600-level or higher SES or SSB course','at least their fifth semester','3.25 GPA','student’s advisor','more than two 600-level courses'], 'For 500-level courses, undergraduates need junior standing and course prerequisites; use an A-U section or request an eligibility override with instructor and Graduate Academics approval. For 600+ courses offered by SES or SSB, request permission, attain fifth-semester standing and GPA 3.25, obtain Graduate Academics/advisor approval, and take at most two 600-level courses per semester. The clause scopes the course’s school, not the undergraduate student’s home school; offering units must be checked separately for selected courses.'),
 ('credit-by-exam','Credit by examination',['full-time status','add/drop deadline','GPA of 3.0','one exam per semester','grade of B or higher','previously been attempted','eight courses','three courses'], 'Full-time undergraduates may seek faculty-approved credit by exam by the fall/spring add-drop deadline. Current students need previous-semester or overall GPA 3.0. A B-or-higher result earns course credit without GPA weight; a failed exam requires regular enrollment. No previously attempted course qualifies. Limits are one exam per semester, eight undergraduate courses and three graduate courses, subject to the published request/approval route.'),
 ('course-by-application','Course by application',['not offered during a semester','approval of the instructor and the Office of Undergraduate Academics','Course by Application request','letter grade'], 'When a course is not offered, a student may request study by application with instructor and Undergraduate Academics approval after discussing syllabus and assessment arrangements. An approved request receives administrative enrollment and a letter grade; this is an approval route, not permission to replace a required course unilaterally.'),
 ('overload-policy','Optional overload approval',['First- Year undergraduate students are not allowed','GPA of 3.30','3.6 or higher GPA','18 credits per semester'], 'No extra courses beyond the first-year academic plan. After year one, Undergraduate Academics may approve one extra class with previous full-time-semester or cumulative GPA 3.30; after an overload semester, GPA 3.6 permits approval for two extra courses. The regular-load threshold is 18 credits. This optional permission does not add graduation credits.'),
]

def parse_options(html):
    root=article(html,'Course Options');rules=[]
    for suffix,title,phrases,summary in OPTION_RULES:
        require_phrases(root,phrases)
        rules.append(rule(PID+'-'+suffix,title,'stevens-policy-course-options',kind='note',summary=summary))
    return dict(id=PID,curriculum_status='partial',courses=[],requirements=rules)

SOURCE_PARSERS[COURSE_OPTIONS]=parse_options

GRADUATE_COURSES={
 'MA 661':('056460e313830166dcf5f1845234c2a3','Engineering and Science',['dynamic programming','statistical learning'],'Dynamic programming and stochastic control models, with approximate methods and applications to statistical learning.'),
 'BIA 665':('62f1e54e3e441000d12528653e9e0000','School of Business (School)',['Reinforcement Learning','decision-making policies'],'Reinforcement learning concepts and algorithms, emphasizing practical implementations of decision-making agents.'),
}

def parse_graduate_course(html,code):
    soup=BeautifulSoup(html,'html.parser');key,unit,phrases,summary=GRADUATE_COURSES[code]
    heading=soup.find(lambda n:n.name=='h1' and clean(n.get_text())==code)
    if heading is None:raise ValueError('Expected graduate elective code missing')
    require_phrases(soup,[unit,*phrases])
    title=next((n for n in heading.find_all_next('h2') if clean(n.get_text())!='Download as PDF'),None)
    credits=soup.find(lambda n:n.name=='h3' and clean(n.get_text())=='Credits')
    value=clean(credits.find_next_sibling().get_text()) if credits and credits.find_next_sibling() else ''
    if title is None or not value.isdigit():raise ValueError('Graduate elective metadata unresolved')
    sid=PID+'-'+code.lower().replace(' ','-');url='https://stevens.catalog.prod.coursedog.com/courses/'+key
    c=course('stevens',code,clean(title.get_text()),sid,url,credits=int(value),category='ai_ml');c['description']=summary
    return dict(id=PID,curriculum_status='partial',courses=[c],requirements=[rule(PID+'-offering-unit-'+code.lower().replace(' ','-'),code+' offering-school eligibility context',sid,[c['id']],kind='note',summary=code+' is identified in the current catalog under '+unit+'. Apply the published undergraduate permission rule for a 600-level SES/SSB course; program listing alone does not waive the GPA, standing or approval conditions.')])

from functools import partial
for code,(key,_,_,_) in GRADUATE_COURSES.items():
    SOURCE_PARSERS['https://stevens.catalog.prod.coursedog.com/courses/'+key]=partial(parse_graduate_course,code=code)

AP=BASE+'#advanced-placement'

def parse_ap(html):
    root=article(html,'Advanced Placement');sid=PID+'-advanced-placement'
    require_phrases(root,['maximum of 30 credits','International Baccalaureate','Cambridge A-Level','transfer credits','directly from high school','not previously enrolled as matriculated students'])
    rules=[rule(PID+'-ap-scope','Incoming examination and prior-credit limit',sid,kind='note',summary='For entrants directly from high school without prior matriculated higher-education enrollment, at most 30 pre-entry credits from AP, IB, Cambridge A-Level and transfer work may apply in combination. Listed score and major/school-specific equivalences remain conditional; this is not a universal waiver of the AI plan.')]
    seen=set()
    for row in root.find_all('tr'):
        cells=row.find_all(['td','th'],recursive=False)
        if len(cells)!=3:continue
        exam,equivalent,credit=[clean(c.get_text(' ',strip=True)) for c in cells]
        if not re.search(r'\([\d, ]+\)$',exam):continue
        if not credit.isdigit() or not equivalent:raise ValueError('AP equivalence row incomplete')
        if (exam,equivalent) in seen:raise ValueError('Duplicate AP equivalence row')
        seen.add((exam,equivalent))
        rules.append(rule(PID+'-ap-row-'+str(len(seen)),exam,sid,kind='note',credits=int(credit),summary='Published conditional AP equivalence: '+equivalent+'. The examination score and any named school/major restriction apply; this observation does not extend a restricted row to School of Computing.'))
    if not seen:raise ValueError('AP equivalence table missing')
    require_phrases(root,['QF majors receive transfer credit for ECON 242','both AP Macroeconomics and AP Microeconomics'])
    rules.append(rule(PID+'-ap-economics-footnote','AP economics footnote scope',sid,kind='note',summary='The combined macroeconomics/microeconomics ECON 242 substitution is explicitly for QF majors; it is not imported into the AI degree.'))
    return dict(id=PID,curriculum_status='partial',courses=[],requirements=rules)

SOURCE_PARSERS[AP]=parse_ap

PROGRESSION={
 'grade-point-averages':('Grade Point Averages','gpa-repetition',['best attempt','primary program of study','all graded courses attempted','no more than three attempts','Grades of W or F','select a program','withdraw from Stevens','previous grade','another school'], 'Cumulative and degree GPAs use the best course attempt; semester GPA includes all graded attempts that term. Each bachelor’s-program course must be passed within three attempts, with W/F counted as unsuccessful; otherwise change to a program not requiring it or withdraw. If a previously passed course is later repeated with F/W, its earlier passing grade remains usable in the graduating GPA. External grades do not enter Stevens GPA.'),
 'academic-standing':('Academic Standing','academic-standing',['at least 12 credits','2.000 or higher semester GPA','no more than two withdrawals or failures','cumulative GPA of 2.000','Academic Notice','Academic Warning','only be on Academic Notice one time'], 'Good standing each semester requires at least 12 earned credits, semester and cumulative GPAs at least 2.000, and at most two withdrawals/failures. The first shortfall leads to Academic Notice and an advised improvement plan; failure to regain good standing during Notice leads to Academic Warning. Notice is available only once; a later shortfall after prior Notice/Warning goes to Warning.'),
}

def parse_progression(html,tab):
    title,suffix,phrases,summary=PROGRESSION[tab];root=article(html,title);require_phrases(root,phrases)
    return dict(id=PID,curriculum_status='partial',courses=[],requirements=[rule(PID+'-'+suffix,title,PID+'-'+tab,kind='note',summary=summary)])

for tab in PROGRESSION:
    SOURCE_PARSERS[BASE+'#'+tab]=partial(parse_progression,tab=tab)
