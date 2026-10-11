"""Eighth College's published breadth table and current entry-path rules."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import course, requirement, slug, text
from atlas.adapters.ucsd_degree_policies import PID, guarded
from atlas.adapters.ucsd_revelle_pools import section
BASE='https://eighth.ucsd.edu/academics/degree-requirements/'
FIRST_URL=BASE+'first-year.html'
TRANSFER_URL=BASE+'transfer.html'
TABLE_URL='https://docs.google.com/spreadsheets/u/0/d/e/2PACX-1vTjSFu7S3GggkhDIouNMzkt-2ikXeiCHwu2RVljn44ZIKuvUDCog6TBv0DFOZwvQIlF_zHDGefamoJD/pubhtml/sheet?headers=false&gid=336726230'
AREAS={'ART':'Arts','HUM':'Humanities','NAT SCI':'Natural sciences','QM/ENG':'Quantitative methods and engineering','SOC SCI':'Social sciences'}


def node(key,title,source='first',**kw):
    return requirement(PID,'eighth-'+key,title,PID+'-eighth-'+source,unit='quarter_hours',category='human_context',**kw)


def parse_table(html):
    s=BeautifulSoup(html,'html.parser');guarded(text(s),['Eighth College General Education Breadth Requirements','Breadth Req. Area','Course Title','JTCCER'])
    rows=[];courses={};counts={k:0 for k in AREAS}
    for key,label in AREAS.items():
        rows.append(node('breadth-'+slug(key),label+' breadth options','table',kind='choose_courses',count=2,summary='Conditional Eighth route: two courses in this area, subject to entry pathway and approved prior credit. Table rows preserve bundles, suffixes and open ranges. Major/minor/university overlap is allowed; this is not an extra requirement in addition to the college breadth component.'))
    for tr in s.find_all('tr'):
        cells=[text(c)for c in tr.find_all('td')]
        if not cells or cells[0]not in AREAS:continue
        if len(cells)!=9:raise ValueError('Eighth table column layout changed')
        area,department,prefix,number,suffix,title,dei,climate,ahi=cells
        raw=prefix+' '+number+suffix;ids=[]
        if re.fullmatch(r'[A-Z]+',prefix)and re.fullmatch(r'\d+',number)and re.fullmatch(r'[A-Z]*',suffix):
            code=prefix+' '+str(int(number))+suffix
            c=course(code,title or None,PID+'-eighth-table',TABLE_URL,institution='ucsd',unit='quarter_hours',category='human_context');courses[c['id']]=c;ids=[c['id']]
        detail='Published '+AREAS[area]+' option '+raw+' ('+department+'): '+(title or 'no separate title printed')+'.'
        flags=', '.join(x for x in [dei,climate,ahi]if x)
        if flags:detail+=' Table overlap annotations: '+flags+'; separate university approval rules and dates still apply.'
        if not ids:detail+=' Compound language/lecture-lab notation and 100–199 ranges remain literal; no independent-choice or course-credit inference.'
        rows.append(node('table-row-'+str(sum(counts.values())),raw,'table',parent=PID+'-eighth-breadth-'+slug(area),kind='note',course_ids=ids,summary=detail));counts[area]+=1
    if not all(counts.values()):raise ValueError('Eighth breadth area missing or empty')
    return dict(id=PID,curriculum_status='partial',courses=list(courses.values()),requirements=rows)


def parse_first(html):
    s=section(html,'Degree Requirements for First Year Students');v=text(s)
    guarded(v,['four-course sequence','A D grade or higher','Select two courses of interest','3rd-quarter level or higher','Courses numbered 1**','Starting Fall 2025','Petitions are not guaranteed','35 of the final 45'])
    return dict(id=PID,curriculum_status='partial',requirements=[
      node('first-cce','Eighth first-year CCE sequence',kind='note',summary='CCE 1, 2, 3 and 120 are the four-course first-year sequence, all at UCSD and letter grade D or better. CCE 120 begins Fall 2025. CCE 1/2/3 are offered fall/winter/spring, with respectively fall/spring/winter identified as off-cycle terms with fewer seats. The page describes CCE120 using skills from CCE1–3 or transfer CCE110; it does not publish a complete formal prerequisite catalog.'),
      node('breadth-policy','Eighth breadth grading and overlap',kind='note',summary='Two courses each in arts, humanities, natural sciences, quantitative methods/engineering and social sciences. D or better, or Pass; major/minor/university overlap permitted. Approved AP/IB/transfer credit applies. Humanities includes language at third-quarter level or higher, with listed 100–199 language ranges as open predicates. No IGETC waiver for first-year admits.'),
      node('transfer-credit-policy','Eighth prior credit and open petitions',kind='note',summary='California community-college courses taken before UCSD may satisfy equivalent breadth areas through their IGETC/CalGETC approvals. After starting UCSD, coursework must articulate to an approved UCSD course or receive a petition approval; petitions are not guaranteed. Off-list breadth courses are an open petition route, not a missing finite approved list.'),
      node('university-policy','Eighth current university rule summary',kind='note',summary='Current page: 180 total/60 upper-division units; UC GPA at least 2.0; no more than 25% of UCSD units P/NP; 35 of final 45 units at UCSD; distance-designated courses below 50% unless the major is approved as a distance program. This residence figure agrees with Senate but differs from separately retained older college catalog wording. Climate applies to lower-division entrants from Fall2024. Eighth says F-1/J-1 students receive an AHI waiver at the end of the final quarter; retain the separate university petition language rather than assuming identical processing.'),
      node('first-quarter-limit','Eighth first-year quarter limit',kind='note',summary='From Fall2019 first-year entrants have twelve quarters. Extra quarters require a completion plan approved by college and major. Summer, approved part-time quarters and quarters withdrawn from all courses do not count.')])


def parse_transfer(html):
    s=section(html,'Degree Requirements for Transfer Students');v=text(s)
    guarded(v,['CCE-110 (4 units)','CCE-120 (4 units)','Two Additional College Level Writing Courses','Starting in Fall 2026','six quarters','Official Letter of Reciprocity'])
    courses=[course(code,None,PID+'-eighth-transfer',TRANSFER_URL,institution='ucsd',unit='quarter_hours',credits=4,category='human_context')for code in ['CCE 110','CCE 120']]
    return dict(id=PID,curriculum_status='partial',courses=courses,requirements=[
      node('transfer-cce','Eighth transfer CCE sequence','transfer',kind='all',course_ids=[c['id']for c in courses],summary='Transfer sequence is CCE110 and120, four units each, both at UCSD for letter grade D or better. CCE110 begins Fall2026; both offered fall/winter/spring.'),
      node('transfer-certified','Eighth certified-transfer branch','transfer',kind='note',summary='Complete IGETC/CalGETC before transfer and send separate official certification, or complete lower-division GE at a UC/four-year institution and provide official reciprocity. Lower-division breadth is waived; CCE110/120 remain. These agreements apply only to students admitted as transfers.'),
      node('transfer-other','Eighth other-transfer branch','transfer',kind='note',summary='Individual course review determines remaining first-year breadth. Complete CCE110/120, two additional college-level writing courses (often already completed before transfer), and all remaining GE not satisfied by prior courses/test scores. Pre-UCSD California community-college IGETC/CalGETC area approvals can meet equivalent breadth; later courses need UCSD equivalence or approved petition. Review begins mid-August and continues through fall; students receive their pathway determination.'),
      node('transfer-limit','Eighth transfer quarter limit','transfer',kind='note',summary='From Fall2019 transfer entrants have six quarters, excluding summer, approved part-time terms and all-course withdrawals. Additional time requires a completion plan approved by major and college. Transfer students meet ELWR before enrollment; DEI remains required.')])
