"""Observe the final reviewed immersion-card sources without certifying reviews."""
from functools import partial
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean
from atlas.adapters.rit_writing_closure import PID
from atlas.adapters import rit_final_interdisciplinary_course_reviews as final
from atlas.adapters import rit_language_health_course_reviews as language
from atlas.adapters import rit_visual_museum_imaging_course_reviews as visual
from atlas.adapters import rit_english_communication_course_reviews as writing
from atlas.adapters import rit_applied_science_course_reviews as applied
from atlas.adapters import rit_philosophy_course_reviews as philosophy
from atlas.adapters import rit_performance_course_reviews as performance
from atlas.adapters import rit_psychology_criminology_leadership_course_reviews as psychology
MODULES=[final,language,visual,writing,applied,philosophy,performance,psychology]
SLUGS=['american-sign-language-and-deaf-cultural-studies-immersion','analytic-and-expressive-communication-immersion','comics-studies-immersion','computational-linguistics-immersion','free-culture-and-free-and-open-source-computing-immersion','geographic-information-systems-immersion','global-justice-immersion','global-public-health-immersion','health-culture-and-society-immersion','language-science-immersion','principles-computing-immersion','transmedia-storytelling-and-entertainment-immersion','vertically-integrated-projects-immersion']

def parse(html, *, url):
    if url not in ['https://www.rit.edu/study/'+s for s in SLUGS]:raise ValueError('Unreviewed remaining route')
    dispatch={}
    for module in MODULES:
        for label,c in module.MANIFEST['courses'].items():
            if c['url']==url:
                code=c.get('popup_code',label)
                if code in dispatch and dispatch[code] is not module:raise ValueError('Ambiguous source-card owner')
                dispatch[code]=module
    soup=BeautifulSoup(html,'html.parser');seen=[]
    for card in soup.select('.courseblock'):
        n=card.select_one('.detail-code');code=clean(n.get_text(' ',strip=True)) if n else None
        if code not in dispatch:raise ValueError('Unbound remaining-route card')
        seen.append(code)
    if not seen or len(seen)!=len(set(seen)):raise ValueError('Missing or duplicate course card')
    results=[]
    for module in MODULES:
        if not any(dispatch[c] is module for c in seen):continue
        filtered=BeautifulSoup(html,'html.parser')
        for card in filtered.select('.courseblock'):
            code=clean(card.select_one('.detail-code').get_text(' ',strip=True))
            if dispatch[code] is not module:card.decompose()
        results.append(module.parse(str(filtered),url=url))
    return dict(id=PID,courses=[c for r in results for c in r.get('courses',[])],requirements=[],observed_immersion_tables=results[0].get('observed_immersion_tables',[]),observed_course_label_associations=[a for r in results for a in r.get('observed_course_label_associations',[])])

def register(sources,parsers):
    for slug in SLUGS:
        url='https://www.rit.edu/study/'+slug
        if url not in sources:sources.append(url)
        parsers[url]=partial(parse,url=url)
