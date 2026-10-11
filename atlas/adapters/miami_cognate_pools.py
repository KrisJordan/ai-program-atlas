"""Miami public cognate observations: bounded exported rows and thematic HTML.

The public Tableau PDF is obtained through Download > PDF > Specific sheets >
Select All, not an undocumented endpoint. parse_individualized_text accepts
pypdf page text separated by formfeeds, limited to explicitly selected pages.
It does not fetch, infer pool completeness, or promote a curriculum audit.
"""
import re
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, course, rule

DIRECTORY = 'https://cognates.miami.edu/courses/individualized'
SID = 'miami-cognate-directory-20261002'
AREAS = {'Arts & Humanities': 'ah', 'People & Society': 'ps', 'STEM': 'st'}
PLANS = {
    'PS_0031': ('A Cross-Cultural and Historic Examination of Sexuality', 'People and Society', 'Gender and Sexuality Studies'),
    'AT_0027': ('Introduction to Philosophy (Arts and Humanities)', 'Arts and Humanities', 'Philosophy'),
}


def parse_individualized_text(text):
    """Parse complete selected Master List pages, deduplicating overlapping rows.

    A course's additional area can occupy the next row without repeating its
    code/title. Six-digit Course ID is an identity, never a credit amount.
    Truncated source titles remain unknown instead of being completed by guess.
    """
    records = {}
    for page_no, page in enumerate(text.strip().split('\f'), 1):
        lines = [clean(line) for line in page.splitlines() if line.strip()]
        expected = ['Subject', 'Course No.', 'Course Title', 'Area of Knowledge',
                    'Typically Oﬀered', 'Course ID']
        if lines[:6] != expected or lines[-2:] != ['Courses Eligible to be Used in Individualized Cognates', '(Updated 10/2/2026)']:
            raise ValueError('Master List export identity, columns or update date changed')
        lines = lines[6:-2]
        i = 0
        subject = code = title = None
        while i < len(lines):
            value = lines[i]
            if re.fullmatch('[A-Z]{2,5}', value) and value not in AREAS:
                subject = value
                i += 1
                if i >= len(lines): raise ValueError('Incomplete subject row')
                value = lines[i]
            if re.fullmatch(r'\d{3}[A-Z]?', value):
                if subject is None: raise ValueError('Course without a subject')
                code = subject + ' ' + value
                i += 1
                names = []
                while i < len(lines) and lines[i] not in AREAS:
                    if re.fullmatch(r'\d{6}', lines[i]): raise ValueError('Unknown area or malformed title row')
                    names.append(lines[i]); i += 1
                title = clean(' '.join(names))
                if not title: raise ValueError('Missing displayed title')
            if i >= len(lines) or lines[i] not in AREAS or code is None:
                raise ValueError('Unreviewed course-number or area layout')
            area = lines[i]; i += 1
            offered = []
            while i < len(lines) and not re.fullmatch(r'\d{6}', lines[i]):
                offered.append(lines[i]); i += 1
            if i >= len(lines) or not offered:
                raise ValueError('Incomplete course identity/area row')
            identity = lines[i]; i += 1
            key = (code, identity)
            r = records.setdefault(key, dict(code=code, source_course_id=identity,
                name=None if '..' in title or '…' in title else title,
                display_title=title, areas=[], pages=[]))
            if r['display_title'] != title:
                raise ValueError('Conflicting titles for repeated course identity')
            if area not in r['areas']: r['areas'].append(area)
            if page_no not in r['pages']: r['pages'].append(page_no)
    if not records: raise ValueError('Empty exported course evidence')
    by_code = {}
    for r in records.values():
        if r['code'] in by_code and by_code[r['code']] != r['source_course_id']:
            raise ValueError('Multiple source identities for one course code need review')
        by_code[r['code']] = r['source_course_id']
    return list(records.values())


def individualized_observation(text, *, pid):
    if len(text.strip().split('\f')) != 2:
        raise ValueError('This bounded observation requires the first two complete Master List pages')
    rows = parse_individualized_text(text)
    courses = []
    root = pid + '-cognate-directory-sample'
    requirements = [rule(root, 'Individualized cognates: bounded directory evidence', SID,
        parent=pid+'-supplement-individualized-overlap', kind='note',
        summary='Observed Master List pages 1–2 of the public PDF export, updated October 2, 2026. This is a partial candidate pool, not the complete approved list. Arts & Humanities and People & Society rows are attached; this AI major already supplies STEM. A selected individualized cognate needs at least three courses/nine credits in one area, with the current CaneLink attribute. None may satisfy another degree requirement, including quantitative proficiency. The same course cannot satisfy two area cognates. Credits and prerequisites are unknown in this directory.')]
    for area, key in list(AREAS.items())[:2]:
        selected = [r for r in rows if area in r['areas']]
        for r in selected:
            c = course(pid, r['code'], r['name'], SID, DIRECTORY, unit='unknown', category='human_context')
            if c['id'] not in {c['id'] for c in courses}: courses.append(c)
        ids = [course(pid,r['code'],r['name'],SID,DIRECTORY)['id'] for r in selected]
        requirements.append(rule(root+'-'+key, area+' — captured subset', SID, ids,
            parent=root, kind='note', category='human_context',
            summary=f'{len(selected)} course identities in the captured pages carry this Area of Knowledge attribute. Membership in this subset does not certify a course is available, that the full pool was captured, or that it can overlap another degree requirement. Multi-area entries are one course, not multiple credits.'))
    return dict(id=pid, courses=courses, requirements=requirements)


def parse_thematic(html, *, pid, plan):
    if plan not in PLANS: raise ValueError('Unreviewed thematic plan')
    title, area, unit = PLANS[plan]
    soup = BeautifulSoup(html, 'html.parser')
    h = soup.find('h1'); selector = soup.find(id='term_selector')
    selected = selector.find('option', selected=True) if selector else None
    if not h or clean(h.get_text()) != title or not selected or clean(selected.get_text()) != 'Fall 2026':
        raise ValueError('Thematic identity or reviewed semester changed')
    flat = clean(soup.get_text(' ',strip=True))
    for marker in (f'Academic Plan {plan}', f'Cognate {area}', 'Recommended for All students.',
                   'Students must complete at least 3 courses for at least 9 credits.',
                   'Complete 2 of the following option groups:', '*Indicates an inactive course'):
        if marker not in flat: raise ValueError('Thematic applicability changed: '+marker)
    academic = next((li for li in soup.find_all('li') if li.find('span') and clean(li.find('span').get_text())=='Responsible Academic Unit'),None)
    if not academic or clean(academic.find_all('span')[1].get_text()) != unit:
        raise ValueError('Responsible academic unit changed')
    sid='miami-cognate-'+plan.lower()+'-fall2026';url='https://cognates.miami.edu/'+plan
    root=pid+'-thematic-'+plan.lower()
    requirements=[rule(root, f'{plan}: {title} — optional thematic route', sid,
        parent=pid+'-policy-cognate-rules', kind='note', category='human_context',
        summary=f'Fall 2026 {area} thematic cognate, responsible unit {unit}, recommended for all students. Only if selected, complete at least three courses/nine credits and both groups below. This is one of 215 active directory entries observed, not a required AI component or the full thematic pool. Existing thematic unit/subject/overlap rules apply; individualized-cognate no-other-degree-requirement restrictions are not generalized to this distinct route.')]
    courses={}; inactive=[]
    tables=soup.find_all('table',class_='group_table')
    if len(tables)!=2: raise ValueError('Thematic group inventory changed')
    for index,table in enumerate(tables,1):
        panel=table.parent
        text=clean(panel.find('p').get_text(' ',strip=True))
        match=re.fullmatch(r'Complete (at least|exactly) (\d+) courses? from the following:',text)
        if not match: raise ValueError('Unreviewed selection rule')
        mode,count=match.groups(); ids=[]; variable=[]
        for row in table.find_all('tr',class_='course'):
            cells=row.find_all('td',recursive=False)
            if len(cells)!=5:raise ValueError('Thematic table columns changed')
            code=clean(cells[0].get_text(' ',strip=True));flag='*' in code
            code=clean(code.replace('*',''))
            if not re.fullmatch(r'[A-Z]{2,4} \d{3}[A-Z]?',code):raise ValueError('Invalid course code')
            anchor=cells[2].find('a');name=clean(anchor.get_text(' ',strip=True)) if anchor else ''
            if not name:raise ValueError('Missing course title')
            limits=re.fullmatch(r'(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)',clean(cells[3].get_text()))
            if not limits:raise ValueError('Changed credit range')
            low,high=map(float,limits.groups());credit=low if low==high else None
            if low!=high:variable.append(f'{code}: {low:g}–{high:g} credits')
            c=course(pid,code,name,sid,url,credit,'semester_hours',category='human_context')
            extras=clean(cells[2].get_text(' ',strip=True))[len(name):].strip()
            if extras:
                if not extras.startswith(('Prerequisite:', 'Pre/Corequisite:')):raise ValueError('Unreviewed course qualification')
                c['prerequisites']=extras
            if flag:
                inactive.append(code)
                continue # Preserve source flags in note, not in the eligible choice list.
            courses[c['id']]=c;ids.append(c['id'])
        if not ids or int(count)>len(ids):raise ValueError('Insufficient active options')
        summary=f'If this thematic cognate is selected: complete {mode} {count} from the displayed active options. '
        if variable:summary+='Published variable credit ranges: '+ '; '.join(variable)+'. '
        requirements.append(rule(root+f'-group-{index}',f'Group {index}: {mode} {count} courses',sid,ids,parent=root,kind='choose_courses',count=int(count),summary=summary,category='human_context'))
    if inactive:
        requirements.append(rule(root+'-inactive','Source flags inactive options',sid,parent=root,kind='note',category='human_context',summary='The Fall 2026 page marks '+', '.join(inactive)+' inactive. They are retained here as source context and excluded from the displayed eligible option groups; no university-wide withdrawal conclusion is inferred.'))
    return dict(id=pid,courses=list(courses.values()),requirements=requirements)


def register(pid,sources,parsers):
    for plan in PLANS:
        url='https://cognates.miami.edu/'+plan
        if url not in sources:sources.append(url)
        parsers[url]=lambda html,plan=plan:parse_thematic(html,pid=pid,plan=plan)
