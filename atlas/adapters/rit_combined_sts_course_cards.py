"""Observe actual STSO cards opened by two literal combined-subject labels.

The source label-to-card association is explicit. It is not certification that a
separately cataloged WGST identity is the same offering or a cross-list group.
"""
from functools import partial
import re
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean,course
from atlas.adapters.rit_immersion_rule_observer import parse as rules
from atlas.adapters.rit_gender_sts_course_reviews import parse as gender,TARGETS
from atlas.adapters.rit_writing_closure import PID
SPECS={
 'https://www.rit.edu/study/environmental-studies-immersion':('Environmental Studies Immersion','rit-environmental-combined-label-cards-2026-2027'),
 'https://www.rit.edu/study/science-technology-and-society-immersion':('Science, Technology, and Society Immersion','rit-sts-combined-label-cards-2026-2027'),
}
LABELS={'STSO-225':'STSO/WGST-225','STSO-342':'STSO/WGST-342'}

def parse(html, *, url):
    title,sid=SPECS[url];observed=rules(html,title=title)
    labels={c for t in observed['observed_tables'] for r in t['rows'] for c in r['course_codes']}
    soup=BeautifulSoup(html,'html.parser');courses=[];bindings=[]
    for card in soup.select('.courseblock'):
        def value(selector):
            n=card.select_one(selector)
            return (clean(n.get_text(' ',strip=True)) or None) if n else None
        code,name=value('.detail-code'),value('.detail-title')
        if code not in LABELS or LABELS[code] not in labels or not name:
            raise ValueError('Combined label does not bind the actual reviewed card identity')
        description=value('.courseblockextra')
        if not description or description.startswith('Loading course description'):
            raise ValueError('Full settled description required')
        amount=value('.detail-hours_html') or '';m=re.fullmatch(r'\((\d+(?:\.\d+)?) Credits?\)',amount)
        if not m:raise ValueError('Unrecognized actual card credits')
        c=course(PID,code,name,sid,url,float(m[1]));c.update(description=description,prerequisites=value('.detail-requisites'))
        c['notes']=['Menu link label '+LABELS[code]+' opened actual card '+code+'. This observation does not certify a separate WGST identity as an alias.']
        courses.append(c);bindings.append({'menu_label':LABELS[code],'observed_course_code':code})
    if not courses or len({c['id'] for c in courses})!=len(courses):raise ValueError('Missing or duplicate combined-label cards')
    return dict(id=PID,courses=courses,requirements=[],observed_label_bindings=bindings,observed_immersion_tables=observed['observed_tables'])

def parse_composed(html, *, url):
    soup=BeautifulSoup(html,'html.parser');codes=[]
    for card in soup.select('.courseblock'):
        n=card.select_one('.detail-code');code=clean(n.get_text(' ',strip=True)) if n else None
        if code not in LABELS and code not in TARGETS:raise ValueError('Unknown STS course scope')
        codes.append(code)
    if not codes or len(codes)!=len(set(codes)):raise ValueError('Missing or duplicate STS cards')
    results=[]
    for combined,parser in [(True,parse),(False,gender)]:
        if not any((c in LABELS)==combined for c in codes):continue
        filtered=BeautifulSoup(html,'html.parser')
        for card in filtered.select('.courseblock'):
            code=clean(card.select_one('.detail-code').get_text(' ',strip=True))
            if (code in LABELS)!=combined:card.decompose()
        results.append(parser(str(filtered),url=url))
    return dict(id=PID,courses=[c for r in results for c in r['courses']],requirements=[],observed_immersion_tables=results[0]['observed_immersion_tables'],observed_label_bindings=[b for r in results for b in r.get('observed_label_bindings',[])])

def register(sources,parsers):
    for url in SPECS:
        if url not in sources:sources.append(url)
        parsers[url]=partial(parse_composed,url=url)
