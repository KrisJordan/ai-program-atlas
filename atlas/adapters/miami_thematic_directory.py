"""Guarded, semester-specific observations of the visible Miami cognate directory.

Course/group inventory is extracted, not replayed. Reviewed description digests gate
manual contextual summaries. No endpoint discovery, audit promotion or dates inferred.
"""
import hashlib
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, course, rule

INDEX = 'https://cognates.miami.edu/explore/all'
INDIVIDUALIZED = {'AT_0080', 'PS_0070', 'ST_0026'}
MANIFEST = Path(__file__).resolve().parents[2] / 'research/miami-thematic-cognate-pools.json'


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def extract_plan(html, plan):
    soup = BeautifulSoup(html, 'html.parser')
    selector = soup.find(id='term_selector')
    selected = selector.find('option', selected=True) if selector else None
    heading = soup.find('h1')
    if not selector or selector.get('data-acadplan') != plan or not selected or not heading:
        raise ValueError('Missing plan identity or selected semester')
    details = {}
    for li in soup.find_all('li'):
        span = li.find('span', recursive=False)
        if not span: continue
        label = clean(span.get_text(' ', strip=True))
        if label in ('Academic Plan', 'Cognate', 'Recommended for', 'Required Courses', 'Number of Groups:'):
            details[label] = clean(li.get_text(' ', strip=True))[len(label):].strip()
        elif label == 'Responsible Academic Unit':
            spans = li.find_all('span', recursive=False)
            details[label] = clean(spans[1].get_text(' ', strip=True)) if len(spans)>1 else None
    if details.get('Academic Plan') != plan: raise ValueError('Plan identity mismatch')
    for key in ('Cognate', 'Responsible Academic Unit', 'Recommended for', 'Required Courses', 'Number of Groups:'):
        if key not in details: raise ValueError('Missing plan field: '+key)
    area = details['Cognate']
    if area not in ('Arts and Humanities', 'People and Society', 'STEM'):
        raise ValueError('Unreviewed area: '+area)
    dh = next((h for h in soup.find_all('h2') if clean(h.get_text()) == 'Description'), None)
    gh = next((h for h in soup.find_all('h2') if clean(h.get_text()) == 'Option Groups'), None)
    if not dh or not gh: raise ValueError('Missing description or option groups')
    description = clean(dh.parent.get_text(' ', strip=True))[len('Description'):].strip()
    group_rule = clean(gh.parent.find('p').get_text(' ', strip=True))
    tables = soup.find_all('table', class_='group_table')
    if not details['Number of Groups:'].isdigit() or int(details['Number of Groups:']) != len(tables):
        raise ValueError('Declared/table group counts disagree')
    if '*Indicates an inactive course' not in clean(soup.get_text(' ',strip=True)):
        raise ValueError('Inactive-course legend missing or changed')
    groups = []
    for index, table in enumerate(tables, 1):
        panel = table.parent
        link = soup.find('a', href='#'+panel.get('id',''))
        paragraphs = panel.find_all('p', recursive=False)
        text = paragraphs[0] if len(paragraphs)==1 else None
        if len(table.find_all('tr')) != len(table.find_all('tr',class_='course'))+1:
            raise ValueError('Unaccounted table row')
        if not link or not text: raise ValueError('Missing group title/rule')
        rows=[]
        for number, tr in enumerate(table.find_all('tr', class_='course'), 1):
            cells=tr.find_all('td', recursive=False)
            if len(cells)!=5: raise ValueError('Course column count changed')
            code=clean(cells[0].get_text(' ',strip=True)); inactive='*' in code
            code=clean(code.replace('*',''))
            if not re.fullmatch(r'[A-Z]{2,4} (?:\d{3}[A-Z]?|[A-Z]{3})',code):
                raise ValueError('Unsupported course code: '+code)
            anchor=cells[2].find('a')
            if not anchor: raise ValueError('Missing course title')
            name=clean(anchor.get_text(' ',strip=True))
            limits=re.fullmatch(r'(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)', clean(cells[3].get_text()))
            if not name or not limits: raise ValueError('Missing title or credit range')
            low,high=map(float,limits.groups())
            if low>high: raise ValueError('Reversed credit range')
            qualification=clean(cells[2].get_text(' ',strip=True))[len(name):].strip()
            rows.append(dict(row=number,code=code,name=None if name.endswith(('...', '…')) else name,
                displayed_title=name,inactive=inactive,credit_min=low,credit_max=high,
                qualification=qualification or None,typically_offered=clean(cells[4].get_text(' ',strip=True)) or None))
        groups.append(dict(index=index,title=clean(link.get_text(' ',strip=True)),
            selection_rule=clean(text.get_text(' ',strip=True)),rows=rows))
    return dict(id=plan,url='https://cognates.miami.edu/'+plan,title=clean(heading.get_text()),
        semester=clean(selected.get_text()),area=area,unit=details['Responsible Academic Unit'],
        recommended_for=details['Recommended for'] or None,required_courses=details['Required Courses'],
        group_selection_rule=group_rule,description_sha256=digest(description),groups=groups)


def rule_context_digest(observed):
    return digest(json.dumps([observed['required_courses'], observed['group_selection_rule'],
        [(g['title'],g['selection_rule']) for g in observed['groups']]],ensure_ascii=False))


def reviewed_specs():
    return {p['id']:p for p in json.loads(MANIFEST.read_text())['plans']}


def parse_thematic(html, *, pid, plan, spec=None):
    spec = spec or reviewed_specs()[plan]
    observed = extract_plan(html, plan)
    for field in ('title','semester','area','unit','recommended_for','description_sha256'):
        if observed[field]!=spec[field]: raise ValueError('Reviewed plan context changed: '+field)
    if spec.get('context_rule_sha256') and rule_context_digest(observed)!=spec['context_rule_sha256']:
        raise ValueError('Reviewed conditional/group context changed')
    if plan == 'PS_0051' and 'business' in pid:
        sid='miami-cognate-ps_0051-fall2026'
        return dict(id=pid,courses=[],requirements=[rule(pid+'-thematic-business-exclusion',
            'Understanding Business cognate is not a business-degree option',sid,
            parent=pid+'-policy-cognate-rules',kind='note',category='human_context',summary=spec['context_note'])])
    if plan in INDIVIDUALIZED: raise ValueError('Individualized routes use the Master List adapter')
    sid='miami-cognate-'+plan.lower()+'-fall2026'
    root=pid+'-thematic-'+plan.lower(); category='other' if plan.startswith('ST_') else 'human_context'
    summary=(f"{observed['semester']} {observed['area']} thematic cognate; responsible unit {observed['unit'] or 'not stated'}. "
        f"Source recommendation: {observed['recommended_for'] or 'not stated'}. If selected: "
        f"{observed['required_courses']} {observed['group_selection_rule']} "
        'This is an optional cognate route, not a required AI component. Thematic unit, subject, language and overlap policies still apply. '
        'The individualized no-other-degree-requirement restriction is not generalized to this distinct route. ')
    if spec.get('context_note'): summary+=spec['context_note']+' '
    requirements=[rule(root,f'{plan}: {observed["title"]} — optional thematic route',sid,
        parent=pid+'-policy-cognate-rules',kind='note',category=category,summary=summary.strip())]
    courses={}; inactive=[]
    for g in observed['groups']:
        ids=[];extra=[]
        for r in g['rows']:
            code=r['code']
            if r['inactive']:
                inactive.append(f"{code} (group {g['index']}, row {r['row']})");continue
            credits=r['credit_min'] if r['credit_min']==r['credit_max'] else None
            c=course(pid,code,r['name'],sid,observed['url'],credits,'semester_hours',category=category)
            q=r['qualification']
            if q and q.startswith(('Prerequisite:', 'Pre/Corequisite:', 'Prerequisites:', 'Corequisite:')):
                c['prerequisites']=q
            if q: extra.append(code+': '+q)
            if credits is None:extra.append(f"{code}: {r['credit_min']:g}–{r['credit_max']:g} published credit range")
            previous=courses.get(c['id'])
            if previous and previous != c: raise ValueError('Conflicting course facts within plan: '+code)
            courses[c['id']]=c
            if c['id'] not in ids:ids.append(c['id'])
        # A cap, conditional branch, optional group, or approval is not a minimum selection.
        simple=re.fullmatch(r'Complete (at least|exactly) (\d+) courses? from the following:?',g['selection_rule'])
        all_groups=observed['group_selection_rule']==f"Complete {len(observed['groups'])} of the following option groups:"
        kind='choose_courses' if simple and all_groups and int(simple.group(2))<=len(ids) else 'note'
        count=int(simple.group(2)) if kind=='choose_courses' else None
        requirements.append(rule(root+f"-group-{g['index']}",g['title'],sid,ids,parent=root,kind=kind,count=count,
            summary='Only within this selected thematic route, subject to its overall course/credit minimum and group-selection rule: '+g['selection_rule']+
                (' Additional row conditions: '+'; '.join(extra)+'.' if extra else '')+
                ' Listed courses are options, not all individually required; inactive rows are excluded.',category=category))
    if inactive:
        requirements.append(rule(root+'-inactive','Source flags inactive options',sid,parent=root,kind='note',category=category,
            summary='The '+observed['semester']+' page marks '+', '.join(inactive)+' inactive. They are excluded from eligible option groups; no university-wide withdrawal is inferred.'))
    from atlas.adapters.miami_limited_identity_reviews import apply_observed_categories
    return apply_observed_categories(dict(id=pid,courses=list(courses.values()),requirements=requirements))


def register(pid,sources,parsers):
    for plan,spec in reviewed_specs().items():
        if plan in INDIVIDUALIZED or spec['area']=='STEM':continue
        url=spec['url']
        if url not in sources:sources.append(url)
        parsers[url]=lambda html,plan=plan:parse_thematic(html,pid=pid,plan=plan)
