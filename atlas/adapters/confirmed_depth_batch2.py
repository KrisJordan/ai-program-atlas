"""Source-specific observations for four paths found in the second depth pass.

Parsers expose observed choices and reject missing policy context. They never
promote a curriculum to complete or include the full host bachelor's degree.
"""
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, content, course, rule, require_phrases


def _category(code, title):
    if code.startswith(('MA ', 'MTH ')): return 'mathematics'
    if any(x in (title or '').casefold() for x in ('artificial intelligence', 'machine learning', 'neural network', 'computer vision', 'ai agents')): return 'ai_ml'
    return 'other'


def _row(row, prefix, sid, url, unit='unknown'):
    cells = row.find_all('td', recursive=False)
    codecell = row.find('td', class_='codecol')
    if not codecell or len(cells) < 2: return None
    code = re.sub(r'^or\s+', '', clean(codecell.get_text(' ', strip=True)))
    if not re.fullmatch(r'[A-Z]+\s+\d+[A-Z]?(?:/(?:[A-Z]+\s*)?\d+[A-Z]?)?', code):
        raise ValueError('Unrecognized course code: '+code)
    title = clean(cells[1].get_text(' ', strip=True)) or None
    amount = row.find('td', class_='hourscol')
    amount = clean(amount.get_text()) if amount else ''
    value = float(amount) if re.fullmatch(r'\d+(?:\.\d+)?', amount) else None
    link = codecell.find('a', href=True)
    c = course(prefix, code, title, sid, urljoin(url, link['href']) if link else url,
               credits=value, unit=unit, category=_category(code,title))
    return c, amount


def parse_ncsu(html, pid, sid, url, discipline):
    root = content(html, discipline+' Engineering (BS): Artificial Intelligence and Machine Learning Concentration')
    plan = root.find(id='planrequirementstextcontainer')
    if plan is None: raise ValueError('NC State plan section missing')
    require_phrases(plan, ['3.5', 'graduate', 'A maximum of 3 credit hours of DSA courses', 'MA 405 is recommended', 'with permission of advisor'])
    tables = plan.find_all('table', class_='sc_courselist')
    if len(tables) != 5: raise ValueError('NC State concentration table layout changed')
    # Footnotes are checked above; their superscripts are not part of course names.
    for sup in plan.find_all('sup'): sup.decompose()
    local = []; active = False
    for row in tables[0].find_all('tr'):
        text = clean(row.get_text(' ', strip=True))
        if text == 'AI/ML Concentration': active=True; continue
        if active and 'areaheader' in row.get('class',[]): break
        if active: local.append(row)
    if not local: raise ValueError('Concentration scope boundary missing')
    courses={}; requirements=[]; ranges=[]
    def observe(rows):
        ids=[]
        for row in rows:
            result=_row(row,pid,sid,url)
            if not result: continue
            c,amount=result
            prior=courses.get(c['id'])
            if prior:
                if c['credits'] is None: c['credits']=prior['credits']
                if c['name'] is None: c['name']=prior['name']
            courses[c['id']]=c;ids.append(c['id'])
            if amount and c['credits'] is None: ranges.append(c['code']+': '+amount+' source hours')
        return list(dict.fromkeys(ids))
    core=observe(local)
    if len(core)!=3: raise ValueError('Expected linear algebra alternative and machine learning core')
    code_ids={c['code']:c['id'] for c in courses.values()}
    if set(code_ids) != {'MA 305','MA 405','ECE 411'}: raise ValueError('NC State core identity changed')
    requirements += [rule(pid+'-linear','Linear algebra alternative',sid,[code_ids['MA 305'],code_ids['MA 405']],kind='choose_courses',count=1,category='mathematics',summary='Choose MA 305 or MA 405. The table assigns 3 hours to this slot; the alternative row has no separate credit value.'), rule(pid+'-ml','Required machine learning course',sid,[code_ids['ECE 411']],category='ai_ml')]
    amounts={}
    for row in local:
        if row.find('td',class_='codecol'):continue
        text=clean(row.get_text(' ',strip=True));h=row.find('td',class_='hourscol')
        if 'Electives' in text and h:
            amounts['open' if 'Open Electives' in text else 'ai']=clean(h.get_text())
    if set(amounts)!={'ai','open'}:raise ValueError('Concentration elective amounts missing')
    ai=observe(tables[2].find_all('tr'))
    opened=observe(tables[3].find_all('tr'))+observe(tables[4].find_all('tr'))
    requirements += [rule(pid+'-ai-pool','AI/ML elective choices',sid,ai,kind='note',category='ai_ml',summary=f"Select {amounts['ai']} published hours from this pool. Alternatives separated by 'or' fill the same listed slot. No more than 3 DSA hours count. Credit-unit normalization is unverified; this is not an all-required list."),rule(pid+'-open-pool','Open elective choices',sid,list(dict.fromkeys(opened)),kind='note',summary=f"Select {amounts['open']} published hours from the ECE and other open-elective lists. Slash-labelled catalog entries remain verbatim combined labels, not separately counted courses; listed alternatives fill the same slot. Reuse with host-degree requirements needs review.")]
    for key,title,summary in [
        ('approval','Additional advisor-approved open electives','The open list also permits DSA courses at the 200 level or above, up to 3 credit hours, and College of Science or College of Engineering courses at the 400 level or above with advisor permission. These are open-ended eligibility rules, not a finite omitted course list.'),
        ('graduate','Graduate enrollment GPA','The catalog requires a minimum 3.5 GPA to enroll in graduate courses.'),
        ('recommended','Recommendations are not extra requirements','MA 405 is recommended for graduate study. The interest-based open-elective suggestions do not create additional required courses.'),
        ('scope','Concentration scope','This inventory covers the AI/ML concentration and its published elective lists. The rest of the host BS and its general education curriculum are outside this concentration record.')]: requirements.append(rule(pid+'-'+key,title,sid,kind='note',summary=summary))
    if ranges:requirements.append(rule(pid+'-ranges','Variable source credit amounts',sid,kind='note',summary='; '.join(dict.fromkeys(ranges))+'. Exact individual credits remain null.'))
    return dict(id=pid,program_kind='concentration',curriculum_status='partial',courses=list(courses.values()),requirements=requirements,outcomes=[],observed_hours=amounts)


def parse_msu(html,pid,sid,url):
    root=content(html,'Concentrations in Computer Science')
    require_phrases(root,['certification will appear on the student’s official transcript','no more than one concentration','3 credits of CSE 499 Undergraduate Research','with approval of the Department of Computer Science and Engineering'])
    heading=next((x for x in root.find_all('strong') if clean(x.get_text())=='Artificial Intelligence'),None)
    if heading is None:raise ValueError('MSU AI concentration heading missing')
    table=heading.find_parent('table'); active=False;pool=None;courses={};pools=[[],[]];counts=[];summaries=[]
    for row in table.find_all('tr'):
        strong=row.find('strong')
        if strong:
            if clean(strong.get_text())=='Artificial Intelligence':active=True;continue
            if active:break
        if not active:continue
        cells=[clean(x.get_text(' ',strip=True)) for x in row.find_all('td',recursive=False)]
        cells=[x for x in cells if x]
        text=' '.join(cells)
        m=re.match(r'(Two|Three) of the following courses( not taken above)? \((.*?) credits\):',text)
        if m:
            counts.append({'Two':2,'Three':3}[m[1]]);summaries.append(text);pool=len(counts)-1;continue
        if len(cells)==4 and re.fullmatch(r'[A-Z]+',cells[0]) and re.fullmatch(r'\d+',cells[1]):
            if pool is None or pool>1:raise ValueError('MSU choice context missing')
            c=course(pid,cells[0]+' '+cells[1],cells[2],sid,url,credits=float(cells[3]),category=_category(cells[0],cells[2]))
            # A title wording variant does not create a second course identity.
            courses.setdefault(c['id'],c);pools[pool].append(c['id'])
    if len(counts)!=2 or not all(pools) or 'not taken above' not in summaries[1]:raise ValueError('MSU two-stage disjoint course choices missing')
    requirements=[rule(pid+'-choice-'+str(i+1),'AI course selection '+str(i+1),sid,ids,kind='choose_courses',count=counts[i],summary=summaries[i]+' Courses in the second pool cannot reuse a course selected for the first pool.') for i,ids in enumerate(pools)]
    research=course(pid,'CSE 499','Undergraduate Research',sid,url,credits=None)
    courses[research['id']]=research
    requirements += [rule(pid+'-research','Conditional undergraduate research credit',sid,[research['id']],kind='note',summary='Up to the published 3-credit application of CSE 499 research related to the concentration is available with department approval. This is a conditional option, not an additional required course; the course’s own credit range is unverified.'),rule(pid+'-recognition','Eligibility and transcript recognition',sid,kind='note',summary='Optional for CS BS students only; at most one concentration may be selected. Completing the concentration produces official-transcript certification and may require more than 120 credits for the host degree.'),rule(pid+'-scope','Concentration scope',sid,kind='note',summary='The student must also complete the CS BS. This record covers the AI concentration, not the full host degree. Additional grade, transfer, residence and graduate-course enrollment policies remain unreviewed.')]
    return dict(id=pid,program_kind='concentration',curriculum_status='partial',courses=list(courses.values()),requirements=requirements,outcomes=[])


def parse_tamu_catalog(html,pid,sid,url):
    root=content(html,'Artificial Intelligence in the Arts - Minor')
    require_phrases(root,['Semester Credit Hours','Prescribed elective','Students seeking to declare the minor must email pvfaadvising@tamu.edu'])
    plan=root.find(id='programrequirementstextcontainer')
    if plan is None:raise ValueError('TAMU minor requirements missing')
    for sup in plan.find_all('sup'):sup.decompose()
    courses=[]
    for row in plan.find_all('tr'):
        x=_row(row,pid,sid,url,'semester_hours')
        if x:courses.append(x[0])
    if len(courses)!=3:raise ValueError('TAMU required course structure changed')
    text=clean(plan.get_text(' ',strip=True))
    total=re.search(r'Total Semester Credit Hours (\d+)',text);elective=re.search(r'Prescribed elective (\d+)',text)
    if not total or not elective:raise ValueError('TAMU total or elective amount missing')
    foot=plan.find('dl',class_='sc_footnotes')
    codes=[clean(a.get_text()) for a in foot.find_all('a',class_='code')] if foot else []
    if not codes:raise ValueError('TAMU prescribed elective pool missing')
    optional=[course(pid,c,None,sid,url,unit='semester_hours') for c in codes]
    requirements=[rule(pid+'-required','Required AI in the Arts courses',sid,[c['id'] for c in courses],unit='semester_hours'),rule(pid+'-electives','Prescribed electives',sid,[c['id'] for c in optional],kind='choose_credits',credits=int(elective[1]),unit='semester_hours',summary='Choose the published prescribed-elective hours from these options; the department specifies two courses.'),rule(pid+'-total','Minor total',sid,kind='note',summary=total[1]+' semester credit hours required.'),rule(pid+'-application','Minor declaration',sid,kind='note',summary='The catalog directs students declaring the minor to email PVFA advising. The department also links an application form; neither route was submitted.')]
    return dict(id=pid,program_kind='minor',curriculum_status='partial',courses=courses+optional,requirements=requirements,outcomes=[])


def parse_tamu_department(html,pid,sid,url):
    root=content(html,'AI In The Arts')
    require_phrases(root,['Undergraduate Minor','Three Required Courses, 9 Credit Hours','Select two from the following (6 hours)'])
    tables=root.find_all('table')
    if len(tables)!=2:raise ValueError('TAMU department curriculum tables changed')
    courses=[];groups=[]
    for table in tables:
        ids=[]
        for row in table.find_all('tr'):
            cells=[clean(x.get_text(' ',strip=True)) for x in row.find_all('td',recursive=False)]
            if len(cells)!=3 or not re.fullmatch(r'[A-Z]+ \d+',cells[0]):continue
            c=course(pid,cells[0],cells[1],sid,url,credits=float(cells[2]),unit='semester_hours',category='applications');courses.append(c);ids.append(c['id'])
        groups.append(ids)
    if [len(x) for x in groups]!=[3,4]:raise ValueError('TAMU department course counts changed')
    return dict(id=pid,program_kind='minor',curriculum_status='partial',courses=courses,requirements=[rule(pid+'-department-choice','Select two prescribed electives',sid,groups[1],kind='choose_courses',count=2,unit='semester_hours',summary='The department specifies two prescribed electives, totaling 6 semester credit hours.')],outcomes=[])
