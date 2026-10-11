"""Compose reviewed visual/imaging observations without replaying seed content."""
from functools import partial
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean
from atlas.adapters.rit_visual_museum_imaging_course_reviews import parse as visual, MANIFEST
from atlas.adapters.rit_language_health_course_reviews import parse as language_health
from atlas.adapters.rit_policy_political_immersion_integration import parse_rules
from atlas.adapters.rit_writing_closure import PID
SLUGS={
 'american-arts-immersion':'American Arts Immersion',
 'art-history-immersion':'Art History Immersion',
 'film-studies-immersion':'Film Studies Immersion',
 'journalism-immersion':'Journalism Immersion',
 'museum-studies-immersion':'Museum Studies Immersion',
 'science-film-photography-and-imaging-immersion':'Science of Film, Photography, and Imaging Immersion',
 'visual-culture-immersion':'Visual Culture Immersion',
}
FILM='https://www.rit.edu/study/film-studies-immersion'

from atlas.adapters import rit_visual_museum_imaging_course_reviews as visual_module
from atlas.adapters import rit_language_health_course_reviews as language_module
from atlas.adapters import rit_politics_art_history_course_reviews as art_module
from atlas.adapters import rit_performance_course_reviews as performance_module
from atlas.adapters import rit_english_communication_course_reviews as writing_module
MODULES=[visual_module,language_module,art_module,performance_module,writing_module]

def parse_composed(html, *, url):
    title=SLUGS[url.rsplit('/',1)[-1]]
    soup=BeautifulSoup(html,'html.parser');seen=[];dispatch={}
    for module in MODULES:
        for label,c in module.MANIFEST['courses'].items():
            if c['url']==url:
                code=c.get('popup_code',label)
                if code in dispatch and dispatch[code] is not module:
                    raise ValueError('Ambiguous reviewed observer ownership')
                dispatch[code]=module
    for card in soup.select('.courseblock'):
        n=card.select_one('.detail-code');code=clean(n.get_text(' ',strip=True)) if n else None
        if code not in dispatch:raise ValueError('Unknown visual-route contribution card')
        seen.append(code)
    if not seen or len(seen)!=len(set(seen)):raise ValueError('Missing or duplicate visual-route cards')
    results=[]
    for module in MODULES:
        if not any(dispatch[c] is module for c in seen):continue
        filtered=BeautifulSoup(html,'html.parser')
        for card in filtered.select('.courseblock'):
            code=clean(card.select_one('.detail-code').get_text(' ',strip=True))
            if dispatch[code] is not module:card.decompose()
        results.append(module.parse(str(filtered),url=url))
    return dict(id=PID,courses=[c for r in results for c in r['courses']],requirements=[],observed_immersion_tables=results[0]['observed_immersion_tables'],observed_course_label_associations=[a for r in results for a in r.get('observed_course_label_associations',[])])

def register(sources,parsers):
    for slug,title in SLUGS.items():
        url='https://www.rit.edu/study/'+slug
        if url not in sources:sources.append(url)
        parsers[url]=partial(parse_composed,url=url)
