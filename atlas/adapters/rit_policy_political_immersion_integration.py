"""Source-bound observed panels and rules for seven reviewed RIT paths."""
from functools import partial
from bs4 import BeautifulSoup
from atlas.adapters import rit_applied_science_course_reviews as applied
from atlas.adapters import rit_policy_course_reviews as policy
from atlas.adapters import rit_politics_art_history_course_reviews as politics
from atlas.adapters import rit_physics_course_reviews as physics
from atlas.adapters import rit_chemistry_course_reviews as chemistry
from atlas.adapters import rit_gender_sts_course_reviews as gender
from atlas.adapters.rit_immersion_rule_observer import parse as rules
from atlas.adapters.rit_writing_closure import PID

BASE='https://www.rit.edu/study/'
CLIMATE=BASE+'climate-change-interdisciplinary-problem-immersion'
QUANTUM=BASE+'quantum-information-science-and-technology-immersion'
RULES={BASE+'american-politics-immersion':'American Politics Immersion',
       BASE+'international-relations-immersion':'International Relations Immersion',
       BASE+'cyberpolitics-immersion':'Cyberpolitics Immersion'}


def parse_panels(html, *, url):
    """Partition same-page observed cards without borrowing other source evidence."""
    routes={
        CLIMATE:[(applied.CODES_BY_URL[CLIMATE],applied.parse),
                 (policy.CODES_BY_URL[CLIMATE],policy.parse),
                 ({'CHEM-531'},chemistry.parse)],
        QUANTUM:[(applied.CODES_BY_URL[QUANTUM],applied.parse),
                 ({'PHYS-251'},physics.parse)],
    }
    if url not in routes:raise ValueError('Unreviewed composite route')
    soup=BeautifulSoup(html,'html.parser');codes=[]
    for card in soup.select('.courseblock'):
        node=card.select_one('.detail-code');code=node.get_text(' ',strip=True) if node else None
        if sum(code in scope for scope,_ in routes[url])!=1:
            raise ValueError('Course card outside unique reviewed source scope')
        codes.append(code)
    if not codes or len(codes)!=len(set(codes)):
        raise ValueError('Missing or duplicate course panels')
    results=[]
    for scope,parser in routes[url]:
        if not set(codes)&scope:continue
        filtered=BeautifulSoup(html,'html.parser')
        for card in filtered.select('.courseblock'):
            if card.select_one('.detail-code').get_text(' ',strip=True) not in scope:card.decompose()
        results.append(parser(str(filtered),url=url))
    return dict(id=PID,courses=[c for r in results for c in r['courses']],requirements=[],
                observed_immersion_tables=results[0]['observed_immersion_tables'])


def parse_rules(html, *, title):
    return dict(id=PID,**rules(html,title=title))


def register(sources,parsers):
    selected={CLIMATE:partial(parse_panels,url=CLIMATE),QUANTUM:partial(parse_panels,url=QUANTUM),
              BASE+'public-policy-immersion':partial(policy.parse,url=BASE+'public-policy-immersion'),
              BASE+'political-science-immersion':partial(politics.parse,url=BASE+'political-science-immersion')}
    # Existing environmental-studies evidence now supplies three selected STSO cards.
    env=BASE+'environmental-studies-immersion'
    selected[env]=partial(gender.parse,url=env)
    selected.update({url:partial(parse_rules,title=title) for url,title in RULES.items()})
    for url,parser in selected.items():
        if url not in sources:sources.append(url)
        parsers[url]=parser
