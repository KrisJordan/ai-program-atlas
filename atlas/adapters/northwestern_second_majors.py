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
        t.group('Home-school and course-role overlap',kind='note',summary='Weinberg prohibits sharing program courses with another major/minor except explicit catalog permissions; related courses can overlap. Both may serve general degree requirements. Other home-school/program restrictions may supersede these rules. The linked 2025–2026 non-WCAS guide applies to WCAS programs, not directly to this AI major.')
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
        t.group('Home-school grade and transfer boundary',kind='note',summary='The college’s 11-unique-unit statement expressly covers non-McCormick second majors. Its separate 22-unit McCormick GPA/transfer wording is not silently assigned to this 19-unit program; home-school rules are mapped conditionally, with unresolved applicability conflicts recorded separately.')
    return dict(id=pid,requirements=t.rules)

POLICY_BASE='https://catalogs.northwestern.edu/undergraduate/'
POLICIES={
 'credit':(POLICY_BASE+'requirements-policies/courses-credit/','Courses and Credit',[
  ('Quarter units and repeated credit',['quarter system','awarded 1.0 unit of credit','credit is awarded only once','highest grade'],'Traditional Evanston undergraduate work uses quarters and published course units. Exceptions carry different unit amounts; no individual credit is inferred from a program total. All repeated attempts stay in the GPA, but a nonrepeatable course earns credit only once, for the highest-grade attempt.'),
  ('Advanced course entry',['400–499','advanced undergraduate students with permission'],'400-level electives may require permission for advanced undergraduates. Inclusion in the eligible technical category does not waive course prerequisites or registration permission.')]),
 'grades':(POLICY_BASE+'requirements-policies/grades/','Grades',[
  ('University P/N boundary',['Student Option','particular school’s P/N policy'],'Only CAESAR Student Option courses permit elected P/N. The student’s school policy controls application to requirements; general availability is not AI-major permission.'),
  ('Incomplete coursework',['end of the following like term','before graduating','Grade changes are not permitted after a degree'],'An incomplete must be resolved by the following like term or an earlier agreed deadline, and before graduation; unresolved work converts to F. Grades cannot be changed after conferral.')]),
 'urr':(POLICY_BASE+'requirements-policies/undergraduate-registration-requirement/','Undergraduate Registration Requirement',[
  ('Resident registration, distinct from an extra degree',['at least 9 quarters','at least 32 units','at least 6 quarters','at least 21 units','at least 11 quarters','at least 42 units'],'A single-degree first-year entrant needs nine Northwestern quarters and 32 Northwestern units; a transfer entrant needs six and 21. An additional major is not itself a dual degree. Approved cross-school dual-degree programs have different eleven/42 and transfer nine/32 thresholds.'),
  ('Registration versus earned credits',['at least 2 full units','Courses in which the student receives an NR are not included','Only credits earned','-SA','exceptions would only be considered','University error'],'A counted quarter needs at least two Northwestern units under Northwestern faculty; earned-credit and registered-quarter tests differ, and NR is excluded. Qualifying Northwestern-faculty -SA study-abroad work may count; ordinary external transfer does not. Rare waiver petitions require advising and documented grounds, with quarter reductions limited to University error.')]),
 'pn-public':('https://www.mccormick.northwestern.edu/students/undergraduate/advising-registration/pass-no-credit-option.html','Pass / No Credit Option',[
  ('McCormick P/N application and unresolved AI permission',['McCormick courses are not offered with the Student Option','Only select McCormick degree programs allow P grades','Friday of the eighth week','eight courses with P grades'],'For McCormick students, Student Option availability and the program’s approval are both needed. The public page limits eight P courses and uses the Friday-of-week-eight deadline; years one/two permit one P/N course per quarter. The catalog separately says eight units. The linked dated table has no AI row, so neither universal AI permission nor a CS-major prohibition is inferred.'),
  ('External graded-credit P/N exception',['Non-Northwestern University courses that were taken for a grade','curriculum petition'],'An external course taken for a letter grade but posted without one may be exempted from McCormick P/N restrictions through an approved curriculum petition.')]),
 'transfer-public':('https://www.mccormick.northwestern.edu/students/undergraduate/advising-registration/transfer-credits.html','Transfer Credits',[
  ('McCormick equivalence approval and version discrepancy',['without a direct equivalent course','curriculum petition','no more than 4 units','(21 units)','departmental approval'],'McCormick transfer credit lacking a direct equivalent needs a curriculum petition outside unrestricted electives. At most four major transfer units need departmental approval and possibly tighter department limits. This operational page still describes a 21-unit major; the current AI catalog specifies 22, so the older amount is not substituted.')]),
 'weinberg':(POLICY_BASE+'arts-sciences/','Judd A. and Marjorie Weinberg College of Arts and Sciences',[
  ('Weinberg-student grade and overlap conditions',['at least a C– in all major courses','including all related courses','Courses completed with a P (pass) cannot be counted toward a major or minor','total number of majors plus minors may not typically exceed three'],'For Weinberg students, major and related courses need C− or better and cannot remain P. A prior P requires adviser consultation. Majors/minors normally total at most three, with advising permission for exceptions. The AI catalog’s more specific program-versus-related-course overlap rules and eleven unique AI units also apply.'),
  ('Weinberg transfer-student major residence',['at least four 300-level courses at Northwestern in their major','all required 300-level courses must be completed at Northwestern'],'Weinberg transfer students must complete four 300-level major courses at Northwestern, or all such required courses if the major has fewer than four. Further study away must be planned with advising; this is not a rule for students in other home schools.')]),
 'communication':(POLICY_BASE+'communication/','School of Communication',[
  ('SoC grade and overlap conditions',['Grades of P or D may apply only to elective requirements','SoC does not restrict the double counting','other schools typically restrict'],'For SoC students, P or D cannot satisfy major, minor or distribution requirements; they may serve electives. SoC allows overlap with non-SoC programs subject to the other program’s restrictions, including eleven unique AI units.'),
  ('SoC eligibility statement conflicts with AI route',['cannot be an SoC student and do a second major in any of those schools','SESP, Medill and Engineering'],'The SoC catalog says its students cannot take an Engineering second major, while the current AI and McCormick catalogs expressly describe a non-McCormick AI route. Whether the new AI route is an exception for SoC students requires reconciliation; this record does not promise eligibility.')]),
 'music':(POLICY_BASE+'music/','Henry and Leigh Bienen School of Music',[
  ('Music-student overlap and P/N context',['Music major courses may be double counted','as allowed by the non-music program','maximum of six courses in non-music subjects'],'Music courses may overlap non-music programs only as permitted by that program. Bienen permits at most six non-music P/N courses toward its degree; this does not itself establish AI-major P/N eligibility.'),
  ('Bienen eligibility statement conflicts with AI route',['Majors in the other four undergraduate schools','may only be completed by students in that school'],'Bienen’s general double-major wording requires enrollment in the other home school for its majors, whereas the specific AI catalog advertises a non-McCormick route. The AI exception’s applicability to music students remains unresolved.')]),
 'medill':(POLICY_BASE+'journalism-media-integrated-marketing-communications/','Medill School of Journalism, Media, Integrated Marketing Communications',[
  ('Medill-student grade and P/N context',['minimum GPA of 2.0 (C) in all nonjournalism courses','No more than 3 courses taken P/N','Only 1 course per quarter','WCAS concentration courses'],'Medill students need a 2.0 GPA in nonjournalism letter-graded work. Its general P/N limit is three courses and one per quarter; specified categories, including WCAS concentration courses, require letters. That WCAS wording is not treated as an explicit AI-program P/N permission or prohibition.')]),
 'sesp':(POLICY_BASE+'education-social-policy/','School of Education and Social Policy',[
  ('SESP-student overlap, grades and transfer',['may be used only toward elective requirements','up to 3 course units from their concentration toward a second major','must be approved in advance','grade of B or higher'],'SESP permits P/N only for electives, one unit per quarter. Up to three concentration units may overlap a second or adjunct major, while required Weinberg related courses are exempt from that limit. AI’s eleven unique units still apply. External coursework needs advance approval, and SESP requires B or better for community-college credit.')])}
def parse_policy(html,route,key):
 pid,_,_=CONFIG[route];url,heading,specs=POLICIES[key];root=content(html,heading)
 t=Tables(pid+'-'+key,pid+'-'+key,url,unit='units')
 for title,markers,summary in specs:
  require_phrases(root,markers);t.group(title,kind='note',summary=summary)
 return dict(id=pid,requirements=t.rules)

def parse_existing_policy(html,route,key):
 """Reuse observed exclusion/approval extraction, remapped to this route's sources."""
 from atlas.adapters import northwestern_degree_policies as original
 pid=CONFIG[route][0]
 result=(original.parse_duplicate_sets(html) if key=='duplicates' else original.parse_registrar_transfer(html))
 rows=[]
 for r in result['requirements']:
  r=dict(r);r['id']=r['id'].replace(original.PID,pid);r['source_id']=pid+'-'+key
  r['summary']=r['summary'].replace('Other published duplicate pairs and bundles still require mapping; do not treat this bounded observation as the full list.','The observed duplicate-set groups below retain the published pairs, bundles and conditions.')
  rows.append(r)
 return dict(id=pid,requirements=rows)
DUPLICATES='https://www.mccormick.northwestern.edu/students/undergraduate/advising-registration/course-duplicates.html'
TRANSFER_AFTER='https://www.registrar.northwestern.edu/registration-graduation/transfer-and-test-credit/transfer-credit-after-matriculating-at-nu.html'
PN_PDF='https://www.mccormick.northwestern.edu/documents/students/undergraduate/advising/pass-no-credit-policies.pdf'
OVERLAP_PDF='https://www.registrar.northwestern.edu/registration-graduation/graduation-preparation/double_counting_non_wcas-2025_2026.pdf'
def parse_pdf_text(text,route,key):
 pid=CONFIG[route][0];normalized=clean(text)
 if key=='pn-table':
  if not all(x in normalized for x in ['1/22/2018','Departmental Programs','Computer Science','Integrated Engineering Studies']):raise ValueError('Dated P/N table changed')
  if 'Artificial Intelligence' in normalized:raise ValueError('New AI entry requires substantive policy review')
  summary='The linked McCormick P/N table is dated January 22, 2018 and has no AI departmental row. Its Computer Science rule is not silently applied to the separately cataloged AI major.';url=PN_PDF
 else:
  if not all(x in normalized for x in ['2025-2026','non-WCAS students','second major and/or minor in WCAS','Other rules may apply for other years']):raise ValueError('Overlap publication scope changed')
  summary='The linked 2025–2026 table addresses non-WCAS students completing WCAS majors/minors. It is not direct authority for overlap with a McCormick AI second major; current source applicability remains distinct.';url=OVERLAP_PDF
 t=Tables(pid+'-'+key,pid+'-'+key,url,unit='units');t.group('Reviewed PDF scope',kind='note',summary=summary)
 return dict(id=pid,requirements=t.rules)
