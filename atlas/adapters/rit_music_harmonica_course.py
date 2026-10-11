"""Observe the actual harmonica card and compose existing music observations."""
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean,course
from atlas.adapters.rit_immersion_rule_observer import parse as rules
from atlas.adapters.rit_performance_course_reviews import parse as performance
from atlas.adapters.rit_writing_closure import PID
import re
URL='https://www.rit.edu/study/music-immersion'
SOURCE_ID='rit-music-harmonica-card-2026-2027'

def parse(html):
    observed=rules(html,title='Music Immersion')
    bound={c for t in observed['observed_tables'] for r in t['rows'] for c in r['course_codes']}
    soup=BeautifulSoup(html,'html.parser');courses=[]
    for card in soup.select('.courseblock'):
        def value(selector):
            n=card.select_one(selector)
            return (clean(n.get_text(' ',strip=True)) or None) if n else None
        code,name=value('.detail-code'),value('.detail-title')
        if code!='SOIS-240' or code not in bound or not name:raise ValueError('Unbound harmonica course identity')
        description=value('.courseblockextra')
        if not description or description.startswith('Loading course description'):raise ValueError('Unsettled harmonica description')
        match=re.fullmatch(r'\((\d+(?:\.\d+)?) Credits?\)',value('.detail-hours_html') or '')
        if not match:raise ValueError('Unrecognized actual card credit amount')
        c=course(PID,code,name,SOURCE_ID,URL,float(match[1]));c.update(description=description,prerequisites=value('.detail-requisites'));courses.append(c)
    if len(courses)!=1:raise ValueError('Exactly one observed harmonica card expected')
    return dict(id=PID,courses=courses,requirements=[],observed_immersion_tables=observed['observed_tables'])

def parse_composed(html):
    soup=BeautifulSoup(html,'html.parser');codes=[]
    for card in soup.select('.courseblock'):
        n=card.select_one('.detail-code');code=clean(n.get_text(' ',strip=True)) if n else None
        if code!='SOIS-240' and not (code or '').startswith('PRFL-'):raise ValueError('Unknown music card scope')
        codes.append(code)
    if not codes or len(set(codes))!=len(codes):raise ValueError('Missing or duplicate music cards')
    results=[]
    for harmonica in [True,False]:
        if not any((c=='SOIS-240')==harmonica for c in codes):continue
        filtered=BeautifulSoup(html,'html.parser')
        for card in filtered.select('.courseblock'):
            if (clean(card.select_one('.detail-code').get_text(' ',strip=True))=='SOIS-240')!=harmonica:card.decompose()
        results.append(parse(str(filtered)) if harmonica else performance(str(filtered),url=URL))
    return dict(id=PID,courses=[c for r in results for c in r['courses']],requirements=[],observed_immersion_tables=results[0]['observed_immersion_tables'])
