"""Observe pathway policies even when server HTML has unresolved course IDs."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.business_society_minors import requirement,clean
PROGRAM_ID='stevens-institute-of-technology-artificial-intelligence-minor-minor'
SOURCES=('https://stevens.catalog.prod.coursedog.com/programs/9a968dad026510010633ba4bf9db0000/requirements-and-concentrations-n90Np',)
SOURCE_ID='stevens-ai-minor-curriculum'
def parse(html: str)->dict:
    soup=BeautifulSoup(html,'html.parser');text=clean(soup.get_text(' ',strip=True))
    if not any(clean(h.get_text())=='Minor in Artificial Intelligence' for h in soup.find_all('h1')):raise ValueError('Minor identity missing')
    words={'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8}
    matches=re.findall(r'As many as (\w+) of the (\w+) courses may be double-counted',text)
    if len(matches)!=2 or not all(x in words and y in words for x,y in matches):raise ValueError('Pathway overlap policy missing or changed')
    req=[]
    for key,label,(overlap,total) in zip(['cs-policy','other-policy'],['CS, Cybersecurity or Quantitative Finance pathway','Other-major pathway'],matches):
        req.append(requirement(PROGRAM_ID,key,label,SOURCE_ID,[],kind='note',summary=f'{words[total]} courses; up to {words[overlap]} may also satisfy the major if accepted by that major.'))
    if not re.search(r'grade of [“\"]C[”\"] or better',text):raise ValueError('Minor grade policy missing')
    req.append(requirement(PROGRAM_ID,'grade','Minor grade minimum',SOURCE_ID,[],kind='note',summary='Every minor course requires C or better. Institute-wide minor requirements also apply.'))
    return dict(id=PROGRAM_ID,title='Artificial Intelligence',award_level='minor',program_kind='minor',curriculum_status='partial',requirements=req)

from atlas.adapters.stevens_public_policies import register
SOURCES=list(SOURCES)
SOURCE_PARSERS=globals().get("SOURCE_PARSERS", {})
register(PROGRAM_ID,SOURCES,SOURCE_PARSERS,minor=True)
