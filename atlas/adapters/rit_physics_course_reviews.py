"""Observe actual current physics cards; curated subject reviews remain separate."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, course
from atlas.adapters.rit_immersion_rule_observer import parse as observe_rules
from atlas.adapters.rit_writing_closure import PID

SPECS = {
 'https://www.rit.edu/study/physics-immersion': ('Physics Immersion','rit-physics-course-cards-2026-2027'),
 'https://www.rit.edu/study/astronomy-immersion': ('Astronomy Immersion','rit-astronomy-course-cards-2026-2027'),
 'https://www.rit.edu/study/quantum-information-science-and-technology-immersion': ('Quantum Information Science and Technology Immersion','rit-quantum-physics-card-2026-2027'),
}

def parse(html, *, url):
    title,sid=SPECS[url]
    observed=observe_rules(html,title=title)
    codes={c for t in observed['observed_tables'] for row in t['rows'] for c in row['course_codes']}
    soup=BeautifulSoup(html,'html.parser');courses=[]
    for card in soup.select('.courseblock'):
        def value(selector):
            n=card.select_one(selector)
            return clean(n.get_text(' ',strip=True)) if n else None
        code,name=value('.detail-code'),value('.detail-title')
        if not code or code not in codes or not re.fullmatch(r'PHYS-\d{3}',code) or not name:
            raise ValueError('Unbound physics course card')
        m=re.fullmatch(r'\((\d+(?:\.\d+)?) Credits?\)',value('.detail-hours_html') or '')
        if not m:raise ValueError('Unrecognized physics credit amount')
        description=value('.courseblockextra')
        if not description:raise ValueError('Physics description missing')
        c=course(PID,code,name,sid,url,float(m[1]));c.update(description=description,prerequisites=value('.detail-requisites'));courses.append(c)
    if not courses:raise ValueError('No settled physics cards')
    if len({c['id'] for c in courses})!=len(courses):raise ValueError('Duplicate physics cards')
    return {'id':PID,'courses':courses,'requirements':[],'observed_immersion_tables':observed['observed_tables']}


def register(sources, parsers):
    from functools import partial
    for slug in ['physics-immersion', 'astronomy-immersion']:
        url = "https://www.rit.edu/study/" + slug
        if url not in sources:
            sources.append(url)
        parsers[url] = partial(parse, url=url)
