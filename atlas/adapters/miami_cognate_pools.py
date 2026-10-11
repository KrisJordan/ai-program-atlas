"""Miami public thematic HTML observations; full PDF parser is miami_cognate_export.

Observations never promote a curriculum audit or invent verification dates.
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
