"""Observe rendered public catalog policy tabs; unrendered responses fail closed."""
import hashlib
from bs4 import BeautifulSoup
from atlas.adapters.business_society_minors import clean
BASE='https://stevens.catalog.prod.coursedog.com/academic-policies-procedures/undergraduate-education/requirements-procedures'
TABS={'course-options':('Course Options','Graduate Courses'), 'transfer-credits':('Transfer Credits','Transferring Courses While At Stevens'),'graduation-requirements':('Graduation Requirements','50%'),'humanities-requirements':('Humanities Requirements','Artificial Intelligence')}
def parse_policy(html, *, pid, tab):
    soup=BeautifulSoup(html,'html.parser');title,anchor=TABS[tab]
    articles=[a for a in soup.find_all('article') if any(clean(h.get_text(' ',strip=True))==title for h in a.find_all(['h1','h2']))]
    if len(articles)!=1:raise ValueError('Expected rendered Stevens policy tab missing: '+title)
    value=clean(articles[0].get_text(' ',strip=True))
    if anchor not in value:raise ValueError('Stevens policy content incomplete: '+title)
    return dict(id=pid,curriculum_status='partial',courses=[],requirements=[],observed_policy_digest=hashlib.sha256(value.encode()).hexdigest(),notes=['Rendered policy observation only. Ordinary HTTP may return the default tab; it cannot recertify this policy or curriculum.'])
def register(pid,sources,parsers, *, minor=False):
    for tab in (['course-options','transfer-credits'] if minor else TABS):
        url=BASE+'#'+tab
        if url not in sources:sources.append(url)
        parsers[url]=lambda html,tab=tab:parse_policy(html,pid=pid,tab=tab)
