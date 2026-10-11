"""Current ERC component/region lists; older linked writing list stays versioned."""
import re
from atlas.adapters.cmu_bs.common import course, slug, text
from atlas.adapters.ucsd_college_context import requirement
from atlas.adapters.ucsd_degree_policies import PID, guarded
from atlas.adapters.ucsd_revelle_pools import section
BASE='https://roosevelt.ucsd.edu/academics/gen-ed/'
GE_URL=BASE+'index.html'
GRAD_URL='https://roosevelt.ucsd.edu/academics/graduation-requirements.html'
WRITING_URL=BASE+'udw/UDW_GE.html'
REGIONS={'africa':('africa.html','Africa'),'north-america':('multiculturalism in north america -- FA21 and after.html','Multiculturalism in North America'),'latin-america':('latin-america---fa21-and-after.html','Latin America'),'asia-pacific':('asia-pacific.html','Asia/Pacific'),'europe':('europe.html','Europe'),'middle-east':('middle-east.html','Middle East')}
REGION_URLS={k:BASE+'all-regions/'+v[0]for k,v in REGIONS.items()}


def node(key,title,source='ge',**kw):
    return requirement(PID,'roosevelt-'+key,title,PID+'-roosevelt-'+source,unit='quarter_hours',category='human_context',**kw)


def option(raw,detail,key,source,url,parent,prereq=None):
    bare=re.sub(r'^[\s^!#*~]+','',raw)
    m=re.fullmatch(r'([A-Z]+)\s+(\d+[A-Z]*)',bare);c=None
    if m:
        c=course(m[1]+' '+m[2],detail or None,PID+'-roosevelt-'+source,url,institution='ucsd',unit='quarter_hours',category='human_context');c['prerequisites']=prereq
    summary='Printed approved option '+raw+': '+detail+'.'
    if prereq:summary+=' Listed prerequisite/credit condition: '+prereq+'.'
    summary+=' Markers, dates, cross-listings, ranges and course bundles retain their published qualifications; no unmarked independent-choice inference.'
    return c,node(key,raw,source,parent=parent,kind='note',course_ids=[c['id']]if c else[],summary=summary)


def parse_region(html,key):
    s=section(html,'Regional Specialization');v=text(s);label=REGIONS[key][1]
    guarded(v,[label,'ALL courses from the SAME region','Only ONE course can be taken P/NP','MAY NOT OVERLAP WITH YOUR MAJOR','Last Updated: 8/2026'])
    if key in ['north-america','latin-america']:guarded(v,['FOR STUDENTS WHO ENTERED FA21 AND AFTER'])
    summary='Select one region. First-year entrants take three courses including two upper division; transfers take two upper division. At most one course may be P/NP; AP counts as the lower-division slot, not the P/NP slot. Upper-division major overlap is prohibited; language and fine-arts requirements cannot reuse these courses. Approved upper-division writing overlap is allowed. '
    if key in ['north-america','latin-america']:summary+='This region is for Fall-2021-onward entrants; the earlier combined Americas region is not substituted. '
    if key=='north-america':summary+='The page also permits the open predicate of courses on the DEI approved list, under regional distribution rules. '
    summary+='Source updated August 2026. ^ marks the upper-division distribution reminder, # native-language instruction, * regional-or-fine-arts but not both, and ! possible DEI overlap subject to separate current approval evidence.'
    root=node('region-'+key,label+' regional choices','region-'+key,kind='note',summary=summary);rows=[root];courses={};i=0
    for table in s.find_all('table'):
        for tr in table.find_all('tr'):
            cells=[text(c)for c in tr.find_all(['th','td'])]
            while cells and not cells[0]:cells.pop(0)
            if len(cells)<2 or cells[0]=='Course Number'or not any(cells):continue
            raw=cells[0];detail='; '.join(dict.fromkeys(cells[1:]))
            if not re.match(r'[\s^!#*~]*[A-Z]+\s*\d',raw):raise ValueError('Regional option notation changed: '+raw)
            c,n=option(raw,detail,'region-'+key+'-'+str(i),'region-'+key,REGION_URLS[key],root['id']);rows.append(n);i+=1
            if c:courses[c['id']]=c
    if not i:raise ValueError('Empty regional pool')
    return dict(id=PID,curriculum_status='partial',courses=list(courses.values()),requirements=rows)


def parse_writing(html):
    s=section(html,'Upper-Division Writing GE Requirement');v=text(s)
    guarded(v,['one upper-division course','Last Updated: 12/03/20','Open to transfer students only','MMW must be taken for a letter grade'])
    root=node('writing-pool','ERC approved upper-division writing options','writing',kind='choose_courses',count=1,summary='Current-linked page is explicitly dated December 3, 2020. One approved English writing course at upper-division 100–199 level; R variants permitted. May overlap other requirements; MMW 121/122 are transfer-only and letter graded. * marks regional-or-fine-art eligibility, not both; ~ indicates possible regional overlap within the selected region. Other eligible work may be petitioned using the current GE-page criteria.');rows=[root];courses={};i=0
    for table in s.find_all('table'):
        for tr in table.find_all('tr'):
            cells=[text(c)for c in tr.find_all(['th','td'])]
            while cells and not cells[0]:cells.pop(0)
            if len(cells)<2 or cells[0]=='Course Number'or not any(cells):continue
            raw,detail=cells[:2];c,n=option(raw,detail,'writing-option-'+str(i),'writing',WRITING_URL,root['id']);rows.append(n);i+=1
            if c:courses[c['id']]=c
    if not i:raise ValueError('Empty writing pool')
    return dict(id=PID,curriculum_status='partial',courses=list(courses.values()),requirements=rows)


def parse_ge(html):
    s=section(html,'General Education');v=text(s)
    guarded(v,['Choose any two courses from the lists below','Upper-Division Writing Requirement','2500-word minimum','minimum total word count of 3000','including optional Language Other Than English (LOTE) certification','no more than three (3) upper-division courses'])
    tables=s.find_all('table')
    if len(tables)!=14:raise ValueError('ERC component table layout changed')
    rows=[node('current-policy','ERC first-year component rules',kind='note',summary='First-year route: MMW 11–15, two quantitative/formal-skills courses, two natural sciences, fourth-quarter/third-semester language proficiency, one fine-art course of at least four units, three same-region courses including two upper division, and upper-division writing. MMW is letter graded at UCSD with no AP/IB/transfer substitution; ELWR precedes MMW 12/13 but does not waive 11. Approved R variants count. Quantitative, science and fine-arts P/NP options remain subject to major grading rules.'),node('overlap','ERC overlap restrictions',kind='note',summary='Lower-division major and all minor courses may overlap GE. Upper-division major courses cannot overlap ERC GE except writing; noncontiguous double majors may overlap at most three upper-division courses with GE. No GE-to-GE overlap except upper-division writing. Fine arts and regional specialization cannot overlap; language, including prerequisites to the endpoint, cannot overlap regional specialization. Up to two upper-division major/minor courses need department approval; no upper-division course may count in two minors.'),node('writing-petition','ERC off-list upper-division writing petition',kind='note',summary='Provide a syllabus and original English graded writing: either one paper of at least 2,500 words, or a portfolio totaling at least 3,000 words including one paper of at least 1,500. Work must earn C− or better and develop an evidence-supported original argument. Poetry, fiction, in-class exams, group work and lab reports do not qualify. This open petition route is not a missing finite list.')];courses={}
    for index,table in enumerate(tables[:8]):
        area='quantitative'if index<6 else'science'
        for j,tr in enumerate(table.find_all('tr')):
            cells=[text(c)for c in tr.find_all(['th','td'])]
            while cells and not cells[0]:cells.pop(0)
            if len(cells)<2 or cells[0]=='Course Number':continue
            c,n=option(cells[0],cells[1],'component-'+str(index)+'-'+str(j),'ge',GE_URL,None,cells[2]if len(cells)>2 else None);n['title']=area+' — '+n['title'];rows.append(n)
            if c:courses[c['id']]=c
    for index,label in [(8,'language'),(10,'fine-arts')]:
        for j,tr in enumerate(tables[index].find_all('tr')):
            cells=[text(c)for c in tr.find_all(['th','td'])]
            if not any(cells)or cells[0]=='Department'or len(cells)<2:continue
            rows.append(node(label+'-row-'+str(j),label+' option '+str(j),kind='note',summary='Published endpoint/eligible course row: '+' | '.join(dict.fromkeys(cells))+'. Rowspan department labels carry through their published table. Language endpoints are proficiency targets, not a requirement to start at beginner level.'))
    rows.extend([
      node('language-policy','ERC language qualification',kind='note',summary='Proficiency is fourth-quarter/third-semester level, placement into the fifth quarter at UCSD, or an approved UCSD proficiency exam. P/NP and approved R variants count. Self-directed LIGN 19 is excluded. SAT II Language at least 700 or eligible high school abroad may qualify after official scores/transcripts and advising review. The listed heritage LIHL route requires prior exposure, upper-division standing and Linguistics approval. A LIxx 1D/DX endpoint meets proficiency but later continuation/study abroad still requires LTxx 2A. AP/IB routes follow the separate credit chart.'),
      node('transfer-certified','ERC certified-transfer writing route',kind='note',summary='Current page: complete certified IGETC, UC reciprocity or CalGETC before transfer, document it, and take MMW 122 at letter grade D or better. CalGETC without optional LOTE certification additionally needs one college LOTE course or approved proficiency. Transfer agreements are unavailable to first-year admits. This current single-course route differs from the separately retained catalog transfer sequence; applicability is not silently reconciled.'),
      node('transfer-partial','ERC partial and other transfer branches',kind='note',summary='Partial IGETC or reciprocity leaves at most two certified missing areas, reviewed by advising. Use MMW 122 (4 units) after both IGETC 1A/1B or two semesters of writing, otherwise MMW 12 (6 units) after one; letter grade D or better. Prior complete/partial GE at another four-year institution needs a letter and the same writing-dependent MMW route. Without qualifying documentation use the general-transfer branch. General transfers complete remaining GE individually, including two upper-division same-region courses if needed; MMW 122 also satisfies writing. Current transfer table elsewhere says MMW121 or122, another visible inconsistency.'),
      node('component-notes','ERC component annotations and grading limits',kind='note',summary='CSE 8A has a fall CSE-major restriction; math # entries are calculus preparation; ‡ statistics options are discouraged in the first quarter, not prohibited. ASTR 1–4 apply from Fall 2024 and their listed PHYS predecessors ended Spring 2024. PHYS 1 lecture/lab pairs require both; CENG/NANO 15/R variants allow credit only once. Fine arts permits four-unit MUS/TD/VIS courses numbered 1–199 plus listed exceptions, not one-to-three-unit classes. COMM 80 is for Speech and Debate Team members.')])
    return dict(id=PID,curriculum_status='partial',courses=list(courses.values()),requirements=rows)


def parse_graduation(html):
    s=section(html,'University Requirements and Regulations');v=text(s)
    guarded(v,['35 of the last 45','36 units in an academic year','MMW 15 must be taken for a letter grade','last day of finals week','Students cannot petition other courses'])
    return dict(id=PID,curriculum_status='partial',requirements=[node('graduation','Current ERC degree/progress/residence policy','graduation',kind='note',summary='Current public college page agrees with the Senate: 180 total/60 upper-division units, cumulative and major GPA at least 2.0, and 35 of final 45 units at UCSD. Its catalog still prints 36/44; this is retained as a source discrepancy. Minimum progress is 36 degree-applicable units per academic year. MMW 15 supplies first-year climate credit and must be letter graded. Students cannot individually petition an off-list DEI course; departments seek Senate approval. File the DDA from registration opening through final-exam week for the graduating quarter; ordinary first-year/transfer quarter limits and approved extensions apply.')])
