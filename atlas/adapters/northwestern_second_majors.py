"""Distinct current AI second-major routes, observed from their own catalogs."""
import re
from atlas.adapters.national_curriculum_common import content,clean,require_phrases,course
from atlas.adapters.degree_table_observations import Tables
BASE='https://catalogs.northwestern.edu/undergraduate/engineering-applied-science/'
COLLEGE=BASE
CONFIG={
 'mccormick':('northwestern-ai-second-major-mccormick','Artificial Intelligence as a Second Major for McCormick Students',BASE+'artificial-intelligence/artificial-intelligence-second-major-mccormick/'),
 'non-mccormick':('northwestern-ai-second-major-non-mccormick','Artificial Intelligence as a Second Major for non-McCormick Students',BASE+'artificial-intelligence/artificial-intelligence-second-major-non-mccormick/')}
DOMAINS=['Advanced ML/NLP','Theoretical Foundations','Symbolic AI','Software and Systems Engineering for AI','Systems that Interact with Humans','Systems that Navigate the World']

def parse(html,route):
    pid,title,url=CONFIG[route];root=content(html,title)
    if not any(clean(h.get_text(' ',strip=True)) == title for h in root.find_all('h1')):raise ValueError('Exact second-major heading absent')
    for sup in root.find_all('sup'):sup.decompose()
    require_phrases(root,['one course in five of the six categories','six technical electives','Any 300- or 400-level COMP_SCI course','Undergraduate Registration Requirement','degree requirements of their home school'])
    tables=root.select('table.sc_courselist')
    if len(tables)!=(9 if route=='mccormick' else 11):raise ValueError('Second-major table structure changed')
    t=Tables(pid,pid+'-catalog',url,unit='units')
    t.table(tables[0],'Required program course slots')
    v=clean(root.get_text(' ',strip=True))
    match=re.search(r'(?:AI Major Program|Program Courses) \((\d+) units\)',v)
    if not match:raise ValueError('Program-unit amount absent')
    t.group('Published program units',kind='note',credits=float(match[1]),summary='Published program-unit total; the host degree remains independently required. Related courses, where listed, are additional to this program total.')
    if route=='mccormick':
        require_phrases(root,['6 required courses','4 advanced elective courses','Any 300-level or higher class','Scores of 4 or 5 on the AP CS A','scores of 5, 6, or 7 on the IB CS HL'])
        exceptions=re.search(r'introductory courses that directly support computer science \((.*?)\)',v)
        if not exceptions:raise ValueError('Advanced-elective exceptions absent')
        ids=[]
        for code in re.findall(r'\b[A-Z]+(?:_[A-Z]+)* \d+[A-Z]*(?:-\d+)?\b',exceptions[1]):
            c=course(pid,code,None,pid+'-catalog',url,unit='units',category='electives');t.courses.setdefault(c['id'],c);ids.append(c['id'])
        if not ids:raise ValueError('Empty introductory exception list')
        t.group('Four advanced electives',kind='note',count=4,ids=ids,summary='Four courses: any course at level 300 or above, or a listed introductory supporting exception. This is an open eligibility rule, not a finite pool. COMP_SCI 1CA denotes AP CS A 4/5 or IB CS HL 5/6/7 credit, not an invented scheduled course.')
    else:
        require_phrases(root,['7 required courses','Weinberg College prohibits double-counting','Weinberg College allows double-counting a related course','A single course does not satisfy more than one requirement','STAT 202-0','is not accepted'])
        t.group('Home-school and course-role overlap',kind='note',summary='Weinberg prohibits sharing program courses with another major/minor except explicit catalog permissions; related courses can overlap. Both may serve general degree requirements. Other home-school/program restrictions may supersede these rules. The separately linked non-WCAS policy still requires review.')
        t.table(tables[9],'Related mathematics: complete each slot with its listed course or whole sequence')
        t.table(tables[10],'Related probability and statistics: choose one',kind='alternative',interpret_choices=False)
        t.group('Related-course conditions',kind='note',summary='STAT 202-0 is excluded. Physics or biological science is recommended for Weinberg natural-science distribution, not an extra fixed AI course requirement. Related-course units vary with the mathematics sequence.')
        t.group('No internal double counting',kind='note',summary='When a course qualifies for multiple AI requirement areas, select one area; it cannot satisfy two requirements simultaneously.')
    breadth=t.group('Five distinct breadth domains',kind='choose_courses',count=5,summary='Complete one course in each of five of the six domains. OR rows represent alternatives, not additional compulsory courses.')
    for table,name in zip(tables[1:7],DOMAINS):t.table(table,name,parent=breadth['id'],kind='alternative',interpret_choices=False)
    t.table(tables[7],'Societal impact: choose one',kind='alternative',interpret_choices=False)
    t.table(tables[8],'Technical electives: displayed additional pool',kind='note',interpret_choices=False)
    t.group('Six technical electives with open eligibility',kind='note',count=6,summary='Choose six technical electives. Any 300- or 400-level COMP_SCI course is also eligible. The displayed additional list is not the complete universe of this open category.')
    t.group('Second-major relationship',kind='note',summary='This is an additional major for '+('McCormick' if route=='mccormick' else 'non-McCormick')+' students, not a standalone degree. The University Registration Requirement and the home school’s degree requirements remain applicable.')
    return dict(id=pid,title=title,award_level='other',program_kind='additional_major',courses=list(t.courses.values()),requirements=t.rules)

def parse_college(html,route):
    pid,_,_=CONFIG[route];root=content(html,'Robert R. McCormick School of Engineering and Applied Science');t=Tables(pid+'-policy',pid+'-college',COLLEGE,unit='units')
    require_phrases(root,['including McCormick and non-McCormick students','at least 11 units of credit','not applied to major requirements elsewhere','minor or certificate'])
    t.group('Eleven unique AI units',kind='note',credits=11,summary='The college explicitly applies an 11-unit uniqueness minimum to both McCormick and non-McCormick AI second majors: these units cannot also meet another major, minor or certificate.')
    if route=='mccormick':
        require_phrases(root,['no more than 4 units of transfer credit','approved by both the department and school','GPA in the 22 units','at least 2.0','no more than 3 of these units','grade of C or higher'])
        t.group('McCormick major transfer and grade rules',kind='note',summary='For the 22-unit McCormick major, at most four transferred units require department and school approval. External courses need C or better. Major GPA must be at least 2.0, with at most three D-grade units. Current AI-specific P/N applicability remains unreviewed here.')
    else:
        t.group('Home-school grade and transfer boundary',kind='note',summary='The college’s 11-unique-unit statement expressly covers non-McCormick second majors. Its separate 22-unit McCormick GPA/transfer wording is not silently assigned to this 19-unit program; applicable home-school rules require further review.')
    return dict(id=pid,requirements=t.rules)
