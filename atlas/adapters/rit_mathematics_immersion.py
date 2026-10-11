"""Observe an independently public, rendered RIT immersion route.

Caller supplies the actual browser-rendered HTML. An HTTP shell is not a
curriculum. This parser never selects this immersion for an AI student, merges
honors/credit-excluded courses or emits manual classification/audit reviews.
"""
import re
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, course
from atlas.adapters.rit_writing_closure import PID

URL='https://www.rit.edu/study/mathematics-immersion'
SID='rit-mathematics-immersion-2026-2027'


def parse(html):
    soup=BeautifulSoup(html,'html.parser')
    if soup.find('input',attrs={'type':'password'}):
        raise ValueError('Access page is not immersion evidence')
    main=soup.find('main')
    if not main or not any(clean(h.get_text(' ',strip=True))=='Mathematics Immersion' for h in main.find_all('h1')):
        raise ValueError('Mathematics immersion identity missing')
    if not any(clean(h.get_text(' ',strip=True))=='Curriculum for 2026-2027 for Mathematics Immersion' for h in main.find_all('h2')):
        raise ValueError('Immersion version missing or changed')
    tables=main.select('table.sc_courselist')
    if len(tables)!=2:
        raise ValueError('Rendered prerequisite and elective tables required')
    inventories=[]
    for table,expected in zip(tables,['Prerequisites','Electives']):
        text=clean(table.get_text(' ',strip=True))
        if expected not in text:
            raise ValueError('Immersion table role missing')
        rows=[]
        for tr in table.select('tbody tr'):
            codes=[clean(n.get_text(' ',strip=True)) for n in tr.select('.code_bubble')]
            if codes:
                if any(not re.fullmatch(r'MATH-\d+H?',c) for c in codes):
                    raise ValueError('Unexpected mathematics course identity')
                cells=tr.find_all('td')
                title=BeautifulSoup(str(cells[1]),'html.parser')
                for n in title.select('sup'):n.decompose()
                rows.append({'codes':codes,'title':clean(title.get_text(' ',strip=True))})
        if not rows:
            raise ValueError('Empty rendered immersion inventory')
        inventories.append({'role':expected,'rows':rows,'observed_rule_text':text})
    flattened=[c for x in inventories for r in x['rows'] for c in r['codes']]
    if len(set(flattened))!=len(flattened):
        raise ValueError('Duplicate immersion table code')
    result={'id':PID,'requirements':[],'courses':[],
            'observed_immersion_tables':inventories,
            'observed_immersion_policy':clean(main.get_text(' ',strip=True))}
    for card in soup.select('.courseblock'):
        def value(selector):
            node=card.select_one(selector)
            return clean(node.get_text(' ',strip=True)) if node else None
        code,name,hours=value('.detail-code'),value('.detail-title'),value('.detail-hours_html')
        if code not in flattened or not name:raise ValueError('Unbound or missing course-card identity')
        m=re.fullmatch(r'\((\d+(?:\.\d+)?) Credits?\)',hours or '')
        if not m:raise ValueError('Unrecognized credit amount')
        item=course(PID,code,name,SID,URL,float(m[1]))
        item['description']=value('.courseblockextra')
        if not item['description']:raise ValueError('Course description missing')
        item['prerequisites']=value('.detail-requisites')
        result['courses'].append(item)
    if len({c['id'] for c in result['courses']})!=len(result['courses']):
        raise ValueError('Duplicate rendered course cards')
    return result


def register(sources,parsers):
    if URL not in sources:sources.append(URL)
    parsers[URL]=parse
