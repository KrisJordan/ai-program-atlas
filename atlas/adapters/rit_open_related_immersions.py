"""Observe current local route text, including a genuinely open credit criterion."""
import re
from functools import partial
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean
from atlas.adapters.rit_writing_closure import PID
from atlas.adapters.rit_immersion_rule_observer import parse as observe_rules
from atlas.adapters.rit_gender_sts_course_reviews import parse as observe_sts

BASE='https://www.rit.edu/study/'
TITLES={
 'american-indian-and-indigenous-studies-immersion':'American Indian and Indigenous Studies Immersion',
 'latino-latina-latin-american-studies-immersion':'Latino/Latina/Latin American Studies Immersion',
 'urban-studies-immersion':'Urban Studies Immersion',
}
GLOBAL=BASE+'global-experience-immersion'


def parse_global(html):
    soup=BeautifulSoup(html,'html.parser');main=soup.find('main')
    if soup.select('input[type="password"]') or not main:raise ValueError('Global Experience main content missing')
    if not any(clean(h.get_text(' ',strip=True))=='Global Experience Immersion' for h in main.find_all('h1')):raise ValueError('Global Experience identity missing')
    if not any(clean(h.get_text(' ',strip=True))=='Curriculum for 2026-2027 for Global Experience Immersion' for h in main.find_all('h2')):raise ValueError('Global Experience catalog version missing')
    text=clean(main.get_text(' ',strip=True))
    m=re.search(r'All (\w+) credits must contain a substantial global or study away experiential component and all must be GE Electives or Perspectives to qualify',text)
    amounts={'three':3,'six':6,'nine':9,'twelve':12}
    if not m or m[1] not in amounts:raise ValueError('Open global-credit criterion absent or changed')
    if 'approved by RIT Global and the RIT General Education Committee' not in text:raise ValueError('Global Experience approval authority missing')
    return dict(id=PID,courses=[],requirements=[],observed_credits=amounts[m[1]],observed_credit_unit='unknown',observed_policy_text=text)


def parse_rules(html,*,title):
    return dict(id=PID,**observe_rules(html,title=title))


def register(sources,parsers):
    routes={BASE+slug:partial(parse_rules,title=title) for slug,title in TITLES.items()}
    routes[GLOBAL]=parse_global
    routes[BASE+'environmental-studies-immersion']=partial(observe_sts,url=BASE+'environmental-studies-immersion')
    for url,parser in routes.items():
        if url not in sources:sources.append(url)
        parsers[url]=parser
