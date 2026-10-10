"""Observe the department's minimum; blocked catalog coverage stays unresolved."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.business_society_minors import requirement,clean
PROGRAM_ID='clemson-university-artificial-intelligence-minor-minor'
SOURCES=('https://www.clemson.edu/cecas/departments/computing/academics/undergrad/degrees/',)
SOURCE_ID='clemson-ai-minor-department'
def parse(html: str)->dict:
    soup=BeautifulSoup(html,'html.parser')
    h=next((x for x in soup.find_all('h2') if clean(x.get_text())=='Artificial Intelligence'),None)
    if not h:raise ValueError('AI minor heading missing')
    text=clean(h.find_next('p').get_text())
    m=re.search(r'minor in Artificial Intelligence requires a minimum of (\d+) credits',text)
    if not m:raise ValueError('Minor minimum changed or missing')
    return dict(id=PROGRAM_ID,title='Artificial Intelligence',award_level='minor',program_kind='minor',curriculum_status='partial',courses=[],requirements=[requirement(PROGRAM_ID,'minimum','Published credit minimum',SOURCE_ID,[],kind='note',credits=int(m[1]),summary='Minimum '+m[1]+' published credits, including programming fundamentals and statistical foundations; individual courses and normalized credit unit remain unverified.')])
