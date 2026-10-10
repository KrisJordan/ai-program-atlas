"""Observe department course choices, without resolving catalog disagreements."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.business_society_minors import course,requirement,clean
PROGRAM_ID='florida-international-university-artificial-intelligence-minor-minor'
SOURCES=('https://cec.fiu.edu/degrees-programs/undergraduate/minor-in-artificial-intelligence/',)
SOURCE_ID='fiu-ai-minor-department'
def parse(html: str)->dict:
    soup=BeautifulSoup(html,'html.parser')
    if not any(clean(h.get_text())=='Get a Minor in Artificial Intelligence' for h in soup.find_all('h2')):raise ValueError('Minor identity missing')
    courses=[];requirements=[]
    for i,h in enumerate(h for h in soup.find_all('h3') if re.search(r'\(\d+ Credits\)',h.get_text())):
        title=clean(h.get_text());amount=int(re.search(r'\((\d+) Credits\)',title)[1]);cs=[]
        for li in h.find_next('ul').find_all('li',recursive=False):
            m=re.match(r'([A-Z]+ \d{4}): (.+)',clean(li.get_text()))
            if m:
                c=course(m[1],m[2],PROGRAM_ID,SOURCE_ID,SOURCES[0]);courses.append(c);cs.append(c['id'])
        if not cs:raise ValueError('Course choices missing')
        requirements.append(requirement(PROGRAM_ID,'observed-area-'+str(i),title,SOURCE_ID,cs,'choose_courses',1,amount,summary='Choose one course in this published area. Additional approved options and discrepancies require independent catalog review.'))
    if len(requirements)!=4:raise ValueError('Four-area curriculum structure changed')
    return dict(id=PROGRAM_ID,title='Artificial Intelligence',award_level='minor',program_kind='minor',curriculum_status='partial',courses=courses,requirements=requirements)
