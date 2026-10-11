from atlas.adapters.northwestern_degree_courses import classify_observed
"""Actual public McCormick tables and policies; no advising-system access."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import course, requirement, text, slug
from atlas.adapters.degree_table_observations import Tables
PID='northwestern-university-artificial-intelligence-major-bs-in-engineering-bse-degree'
COLLEGE_URL='https://catalogs.northwestern.edu/undergraduate/engineering-applied-science/'
URR_URL='https://catalogs.northwestern.edu/undergraduate/requirements-policies/undergraduate-registration-requirement/'
THEME_URL='https://www.mccormick.northwestern.edu/students/undergraduate/social-science-humanities-theme/index.html'
FAQ_URL='https://www.mccormick.northwestern.edu/students/undergraduate/social-science-humanities-theme/frequently-asked-questions.html'
REGISTRATION_URL='https://www.mccormick.northwestern.edu/students/undergraduate/advising-registration/registration.html'
TRANSFER_URL='https://www.mccormick.northwestern.edu/students/undergraduate/advising-registration/transfer-credits.html'
PN_URL='https://www.mccormick.northwestern.edu/students/undergraduate/advising-registration/pass-no-credit-option.html'
DUPLICATES_URL='https://www.mccormick.northwestern.edu/students/undergraduate/advising-registration/course-duplicates.html'


def document(html,heading):
    s=BeautifulSoup(html,'html.parser')
    if not any(text(h)==heading or text(h).endswith(' '+heading) for h in s.find_all(['h1','h2'])):raise ValueError('Northwestern heading missing: '+heading)
    return s,text(s.find(id='content')or s.find('main')or s)


def guard(value,phrases):
    if any(x not in value for x in phrases):raise ValueError('Northwestern operative policy changed')


def rule(key,title,source,summary,**kw):
    return requirement(PID,'policy-'+key,title,PID+'-'+source,unit='units',kind='note',summary=summary,**kw)


def parse_major_exceptions(html,url):
    s,v=document(html,'Artificial Intelligence Major, BS in Engineering')
    match=re.search(r'introductory courses that directly support computer science \((.*?)\)',v)
    if not match:raise ValueError('Advanced introductory exception list missing')
    codes=re.findall(r'\b[A-Z]+(?:_[A-Z]+)* \d+[A-Z]*(?:-\d+)?\b',match[1]);cs=[]
    for code in codes:
        cs.append(course(code,None,PID+'-catalog',url,institution='nw-bse',unit='units',category='electives'))
    if not cs:raise ValueError('Introductory exception list empty')
    guard(v,['Scores of 4 or 5 on the AP CS A','scores of 5, 6, or 7 on the IB CS HL','PHYSICS 125-1','PHYSICS 140-1','GEN_ENG 212-0'])
    for code,name in [('PHYSICS 125-1','General Physics for ISP'),('PHYSICS 140-1','Fundamentals of Physics'),('GEN_ENG 212-0','Engineering Physics - Dynamics')]:
        cs.append(course(code,name,PID+'-catalog',url,institution='nw-bse',unit='units',category='other'))
    rows=[rule('advanced-intro','Introductory advanced-elective exceptions','catalog','These explicitly listed introductory courses may fill the four advanced-elective slots; courses at level 300 or higher are also eligible. COMP_SCI 1CA is transfer credit awarded for AP CS A scores 4/5 or IB CS HL scores 5/6/7, not an invented scheduled course.',course_ids=[c['id']for c in cs[:-3]]),
          requirement(PID,'policy-physics-alternatives','Required physics alternative',PID+'-catalog',unit='units',kind='choose_courses',count=1,course_ids=['nw-bse-physics-135-1']+[c['id']for c in cs[-3:]],summary='Complete PHYSICS 135-1 or one of the three explicitly permitted substitutes. Remaining basic science rules still apply.')]
    return {'id':PID,'curriculum_status':'partial','courses':cs,'requirements':rows}


def parse_design_table(t, table):
    """The seven unindented oral-communication rows form one explicit choice."""
    guard(text(table), ['Writing and Design', 'Innovation/Oral Communication', 'Select one of the following:'])
    root = t.table(table, 'Three design, communications and innovation units')
    choices = [r for r in t.rules if r['parent_id'] == root['id'] and r['kind'] == 'alternative']
    if len(choices) != 1: raise ValueError('McCormick innovation choice changed')
    choice = choices[0]
    pool = []; selecting = False
    for row in table.find_all('tr'):
        value = text(row)
        if value == 'Select one of the following:':
            selecting = True
            continue
        if selecting:
            observed = t.row(row)
            if observed is None: raise ValueError('Unexpected row inside innovation choice')
            pool.extend(observed['ids'])
    if not pool: raise ValueError('Innovation choice pool missing')
    for r in t.rules:
        if r['parent_id'] == root['id'] and set(r['course_ids']) & set(pool):
            r['parent_id'] = choice['id']
    choice['summary'] = 'Select one innovation/oral-communication option. Writing/design bundles remain required; these unindented source rows are alternatives, not seven fixed courses.'
    return root


def parse_college(html):
    s,v=document(html,'Robert R. McCormick School of Engineering and Applied Science')
    guard(v,['Lab courses may count','at least 11 units of credit','no more than 4 units of transfer credit','winter quarter of their junior year','not less than 2.0','no more than 3 of these units','No more than 8 units taken P/N'])
    root=s.find(id='requirementstextcontainer');tables=root.find_all('table',class_='sc_courselist')if root else []
    if len(tables)!=4:raise ValueError('McCormick core table structure changed')
    for sup in root.find_all('sup'):sup.decompose()
    t=Tables('nw-bse-college',PID+'-college',COLLEGE_URL,unit='units')
    sci=t.table(tables[1],'Approved basic-science pool',kind='choose_credits',interpret_choices=False);sci['credits']=4;sci['summary']='Four science units total, including the AI major’s required physics alternative and three additional units. Count an already-used physics unit only once. Laboratories count only with their corresponding lectures; bundled options remain bundled.'
    t.table(tables[2],'Three engineering-foundations units')
    parse_design_table(t, tables[3])
    # Stable shared course IDs allow overlap with the major record, not duplicate instances.
    mapping={i:i.replace('nw-bse-college-','nw-bse-',1)for i in t.courses}
    for c in t.courses.values():c['id']=mapping[c['id']]
    for r in t.rules:r['course_ids']=[mapping[i]for i in r['course_ids']]
    specs=[
      ('mathematics','AI mathematics override','AI uses COMP_SCI 212-0 instead of the generic MATH 228-2 core requirement. ES_APPM 252-1/252-2 can substitute for the corresponding MATH 228-1/228-2 sequence; this does not erase the AI discrete-mathematics requirement.'),
      ('science-labs','Science lab and duplicate restrictions','Science labs count only together with their corresponding lectures. EARTH 210/203, EARTH 214/201 and EARTH 215/202 carry explicit duplicate-credit restrictions. The separate duplicate-course rules also apply.'),
      ('theme','Seven-unit humanities/social science theme','Seven courses, with at most five in either category, at least three thematically related, and ordinarily no more than three at 100 level. AP/IB/transfer credit may qualify. The catalog says submit by winter of junior year; public theme guidance instead says end of sophomore year. Full public subject rules are mapped separately.'),
      ('unrestricted','Five unrestricted electives','Any credit-bearing university course may fill the five unrestricted electives, subject to duplicate-credit and other degree policies.'),
      ('unique','BSE relationship and unique major credit','The BSE AI major may be pursued in McCormick or as a second major from another undergraduate school. At least 11 of its 22 major units must be unique, unused in other majors, minors or certificates. Adding AI to a discipline-specific McCormick BS is a second major, not the multiple-BS arrangement. This record maps the McCormick degree; another home school retains its own degree rules.'),
      ('transfer','Transfer-credit cap and approval','At most four externally completed units may count in the 22-unit major, with both department and school approval. Other degree categories are not subject to this four-unit cap; the University Registration Requirement still applies.'),
      ('grades','Degree and major grades','At least 2.0 GPA in all degree units and separately in the 22-unit major. At most three major units may have D grades. External courses used for McCormick requirements need C or better.'),
      ('application','Degree application and curriculum changes','Apply for the degree through MAS a year before graduation. Students encountering changes while enrolled may choose an entire curriculum used during their enrollment; extended interruptions normally trigger new requirements.'),
      ('pn','Catalog P/N limits','No more than eight P/N units toward the 48-unit degree, and at most one per quarter in years one/two. No P/N in mathematics, engineering foundations, sciences or design/communication/innovation. Theme permits any 300-level course but at most four at 100/200 level. Major P/N eligibility is delegated to the department; do not assume permission.'),
      ('exemptions','Approved placement and exemptions','Approved tests or individually reviewed prior coursework may grant credit or an exemption reducing required units. Such approval never removes the separate registration requirement; no particular waiver is presumed.')]
    t.rules.extend(rule(k,title,'college',summary)for k,title,summary in specs)
    return {'id':PID,'curriculum_status':'partial','courses':classify_observed(list(t.courses.values())),'requirements':t.rules}


def parse_urr(html):
    s,v=document(html,'Undergraduate Registration Requirement')
    guard(v,['at least 9 quarters','at least 32 units','at least 6 quarters','at least 21 units','at least 11 quarters','at least 42 units','at least 2 full units','within two quarters of graduating','cases of University error'])
    specs=[('urr-standard','Registration and Northwestern-credit minimums','First-year single-degree entrants need nine registered quarters and 32 earned Northwestern units; transfers need six quarters and 21 units. These are separate from the 48-unit degree total.'),('urr-dual','Approved dual-school registration minimums','For approved dual bachelor’s degrees across schools, first-year entrants need eleven quarters/42 Northwestern units; transfers need nine quarters/32 units. Adding a second major does not itself create a dual degree.'),('urr-counting','Qualifying quarters versus earned credits','A registered quarter needs at least two full units of Northwestern coursework under Northwestern faculty. Passing and listed nonpassing/W grades can count toward quarter registration; NR cannot. Only earned A–D or P credit counts toward the unit minimum. Co-op and ordinary transferred study-abroad credit do not qualify; at least two units of Northwestern-faculty -SA study-abroad courses do.'),('urr-waiver','Rare registration-waiver petition','Consult school advising; petition only within two quarters of graduation. Exceptions normally address credit amounts; reducing required quarters is considered only for University error. Eligibility is not an approved waiver.')]
    return {'id':PID,'curriculum_status':'partial','requirements':[rule(k,t,'urr',s)for k,t,s in specs]}


def parse_theme(html):
    s,v=document(html,'Social Science and Humanities Theme Requirements')
    guard(v,['maximum of five courses','minimum of three','up to four 100-level courses if three are foreign language','Half-unit (1/2) and one-third (1/3)','By the end of your sophomore year'])
    tables=s.find_all('table');first=next((t for t in tables if [text(x)for x in t.find_all('th')]==['Social & Behavioral Sciences','Humanities']),None);second=next((t for t in tables if [text(x)for x in t.find_all('th')]==['Courses Allowed','Courses NOT Allowed']),None)
    if first is None or second is None:raise ValueError('Theme policy tables missing')
    rows=[]
    for i,label in enumerate(['Social & Behavioral Sciences','Humanities']):
        entries=[text(p)for p in first.find_all('td')[i].find_all('p')if text(p)]
        prefixes=[]
        for e in entries:
            m=re.match(r'([A-Z_]+)\s*[–-]',e)
            if not m:raise ValueError('Theme department row changed')
            prefixes.append(m[1])
        rows.append(rule('theme-'+slug(label),label+' eligible departments','theme','Courses from these departments/programs are generally eligible, subject to the explicit exclusions and thematic approval: '+', '.join(prefixes)+'.'))
    for i,label in enumerate(['additional eligible categories','excluded courses/categories']):
        entries=[text(p)for p in second.find_all('td')[i].find_all('p')if text(p)]
        if not entries:raise ValueError('Theme exception table empty')
        rows.append(rule('theme-exceptions-'+str(i),'Theme '+label,'theme','Public table '+label+': '+'; '.join(entries)+'. Codes and open predicates are retained as printed; no nonexistent course is generated from GEOG 1xx or the PRDV level rule.'))
    rows.append(rule('theme-process','Theme structure and approval','theme','Use seven courses, at most five in one category, with at least three related and a title/narrative. Three 100-level courses maximum, or four if three are foreign language. Fractional-unit courses combine; petition Weinberg first-year seminars. AP/IB may qualify. No course may also fill another of the 48 McCormick requirements. Public deadline is end of sophomore year, differing from the catalog’s junior-winter deadline.'))
    return {'id':PID,'curriculum_status':'partial','requirements':rows}


def parse_public(html, key):
    specs={
      'theme-faq':('Social Science and Humanities Theme Requirement - Frequently Asked Questions',['cannot be waived or excused','syllabus from the host institution in English','committee\'s decisions are final'],'Theme approvals and restrictions','Theme cannot be waived, including for co-op or a second major. Study-abroad theme credit needs MAS petition with an English syllabus. Denied plans may go to the Curriculum Committee, whose decision is final. Planned courses may receive conditional approval and revisions. Research methods/statistics/accounting/econometrics and Engineering coursework are excluded; non-engineering second-major courses can count if otherwise eligible.'),
      'registration':('Registration',['4.99 units','5.5 units','advisor approval','e-signature of the instructors of both courses'],'Public registration approval rules','Each quarter requires an adviser meeting and approved MAS study plan before the hold is released. Regular registration caps at 4.99 units; up to 5.5 may be added in drop/add, and higher loads need associate-dean permission. Conflicting times need both instructors’ signed permission. McCormick does not ordinarily participate in preregistration. Study-abroad return-quarter plans need approval before departure sign-off.'),
      'transfer-public':('Transfer Credits',['no more than 4 units','Major Program degree requirements (21 units)','without a direct equivalent'],'Public transfer review and source discrepancy','Transfer without a direct Northwestern equivalent requires curriculum petition for any category except unrestricted electives. Review proposed US coursework before beginning it. Departmental approval is needed for at most four major transfer units and departments may impose tighter limits. This page calls the major 21 units; the current AI/catalog major is 22. The discrepancy is retained; no 21-unit AI requirement is inferred.'),
      'pn-public':('Pass / No Credit Option',['eight courses with P grades','Friday of the eighth week','McCormick courses are not offered with the Student Option'],'Operational P/N approvals','Only courses offering Student Option can use P/N; McCormick cannot override another school and says its own courses do not offer that option. Confirm permitted requirement use before changing grading. Deadline is Friday of week eight. Years one/two: one course per quarter; later additional courses need the P/N form. Public page says eight P courses, catalog says eight units; no equivalence is assumed. AI-specific major P/N permission remains unverified.'),
      'duplicates':('Course Duplicates',['Duplicates are not alternatives from which to choose','only one of them can be used','ONLY if COMP_SCI 111 is taken first','ONLY if COMP_SCI 211 is taken first'],'Duplicate courses are not substitutions','Only one of duplicate courses may satisfy a McCormick degree/certificate requirement; taking a duplicate does not replace a specifically required course and cannot supply an unrestricted elective. CS110/111 duplication is conditional on taking111 first; CS230/211 on taking211 first. Other published duplicate pairs and bundles still require mapping; do not treat this bounded observation as the full list.')}
    heading,guards,title,summary=specs[key];s,v=document(html,heading);guard(v,guards)
    return {'id':PID,'curriculum_status':'partial','requirements':[rule(key,title,key,summary)]}

REGISTRAR_TRANSFER_URL='https://www.registrar.northwestern.edu/registration-graduation/transfer-and-test-credit/transfer-credit-after-matriculating-at-nu.html'
PN_PDF_URL='https://www.mccormick.northwestern.edu/documents/students/undergraduate/advising/pass-no-credit-policies.pdf'


def parse_duplicate_sets(html):
    result=parse_public(html,'duplicates');s,_=document(html,'Course Duplicates')
    start=next((h for h in s.find_all('h2')if text(h)=='Duplicate Courses List'),None)
    if start is None:raise ValueError('Duplicate set heading missing')
    found=0
    for h in start.find_all_next('h2'):
        entries=[]
        for n in h.next_siblings:
            if getattr(n,'name',None)=='h2':break
            if getattr(n,'name',None)=='ul':entries.extend(text(li)for li in n.find_all('li',recursive=False))
        if not entries:continue
        if any('&' not in e for e in entries):raise ValueError('Duplicate relationship notation changed')
        found+=1
        result['requirements'].append(rule('duplicate-set-'+slug(text(h)),text(h)+' duplicate sets','duplicates','Published duplicate sets: '+'; '.join(entries)+'. Here & denotes duplication, while “and” joins a combined course bundle. These are exclusions, not substitution permissions. Legacy codes and conditional dates/order are preserved as printed.'))
    if not found:raise ValueError('No duplicate sets observed')
    return result


def parse_registrar_transfer(html):
    s,v=document(html,'Transfer Credit after Matriculation')
    guard(v,['does not guarantee an articulation','fully accredited 4-year college or university','does not accept post-matriculation credit for online courses','McCormick - Credit accepted with approval'])
    return {'id':PID,'curriculum_status':'partial','requirements':[
      rule('transfer-procedure','Post-matriculation transfer approval','registrar-transfer','Consult school/major advisers and submit a proposal with course description or syllabus before outside coursework; a month of lead time is recommended. Review proceeds through home school, relevant department and applicable credential adviser, then student and final school approval. Final official transcript is required; advance approval does not guarantee final articulation. McCormick may accept two-year/community-college credit with approval.'),
      rule('transfer-math','Mathematics transfer format restriction','registrar-transfer','Mathematics post-matriculation transfer courses must be in person at a fully accredited four-year institution; online coursework is not accepted by the department.'),
      rule('transfer-abroad','Study-abroad credit approval','registrar-transfer','Follow the approved study-abroad process before foreign coursework, including the published home-country exceptions. After program evaluation and official transcript review, eligible credit is initially general elective credit; school petition is needed to designate a Northwestern course or apply it to major/minor requirements. Program-specific conversion ratios apply; no universal conversion is inferred.') ]}
