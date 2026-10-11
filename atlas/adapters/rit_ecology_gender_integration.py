"""Compose only observed course panels and local rules from current RIT routes."""
from functools import partial
from bs4 import BeautifulSoup
from atlas.adapters.rit_writing_closure import PID
from atlas.adapters.rit_biology_course_reviews import parse as biology
from atlas.adapters.rit_applied_science_course_reviews import parse as applied, CODES_BY_URL
from atlas.adapters.rit_gender_sts_course_reviews import SOURCE_PARSERS as GENDER
from atlas.adapters.rit_immersion_rule_observer import parse as rules

ECOLOGY='https://www.rit.edu/study/biology-ecology-and-evolution-immersion'
CLIMATE='https://www.rit.edu/study/climate-change-interdisciplinary-problem-immersion'
RULES={
 'https://www.rit.edu/study/gender-and-stem-studies-immersion':'Gender and STEM Studies Immersion',
 'https://www.rit.edu/study/gender-equity-social-institutions-and-public-affairs-immersion':'Gender Equity, Social Institutions, and Public Affairs Immersion',
 'https://www.rit.edu/study/queer-and-transgender-studies-immersion':'Queer and Transgender Studies Immersion',
}


def parse_ecology(html):
    soup=BeautifulSoup(html,'html.parser');panels=soup.select('.courseblock')
    if not panels:raise ValueError('No settled ecology course cards')
    codes=[]
    for panel in panels:
        node=panel.select_one('.detail-code');code=node.get_text(' ',strip=True) if node else ''
        if not (code.startswith('BIOL-') or code in CODES_BY_URL[ECOLOGY]):
            raise ValueError('Ecology card outside reviewed source dispatch')
        codes.append(code)
    results=[]
    for is_biology,parser in [(True,biology),(False,applied)]:
        if not any(c.startswith('BIOL-')==is_biology for c in codes):continue
        filtered=BeautifulSoup(html,'html.parser')
        for panel in filtered.select('.courseblock'):
            code=panel.select_one('.detail-code').get_text(' ',strip=True)
            if code.startswith('BIOL-')!=is_biology:panel.decompose()
        results.append(parser(str(filtered),url=ECOLOGY))
    courses=[c for result in results for c in result['courses']]
    if len({c['id'] for c in courses})!=len(courses):raise ValueError('Duplicate ecology course cards')
    return dict(id=PID,courses=courses,requirements=[],observed_immersion_tables=results[0]['observed_immersion_tables'])


def parse_rules(html, *, title):
    return dict(id=PID, **rules(html,title=title))


def register(sources,parsers):
    selected={ECOLOGY:parse_ecology,CLIMATE:partial(applied,url=CLIMATE)}
    selected.update({u:p for u,p in GENDER.items() if any(k in u for k in ['gender-art-and-media','womens-and-gender'])})
    selected.update({u:partial(parse_rules,title=t) for u,t in RULES.items()})
    for url,parser in selected.items():
        if url not in sources:sources.append(url)
        parsers[url]=parser
