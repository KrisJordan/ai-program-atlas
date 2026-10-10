"""Observe Minnesota's announced minor course choices without certifying review."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.business_society_minors import course, requirement, clean

PROGRAM_ID='minnesota-ai-ml-minor'
SOURCES=('https://cse.umn.edu/cs/artificial-intelligence-and-machine-learning-ai-ml-minor',)
SOURCE_ID='minnesota-ai-ml-curriculum'


def parse(html: str) -> dict:
    soup=BeautifulSoup(html,'html.parser')
    h=soup.find('h1')
    if not h or 'Artificial Intelligence and Machine Learning' not in h.get_text() or 'Minor' not in h.get_text():
        raise ValueError('Minor identity missing')
    groups={}
    for title in ['Required Computer Science Coursework','Required Math Coursework','Minor Electives']:
        heading=next((h for h in soup.find_all('h3') if clean(h.get_text())==title),None)
        if not heading:raise ValueError('Required section missing: '+title)
        groups[title]=heading.find_next('ul')
    courses={};req=[]
    def extract(text):
        result=[]
        for m in re.finditer(r'([A-Z]+)\s*(\d{4}[HW]?)\s*[-–]\s*(.*?)\s*\((\d+) credit\)',text):
            code=m[1]+' '+m[2]
            c=course(code,m[3],PROGRAM_ID,SOURCE_ID,SOURCES[0],int(m[4]))
            courses[c['id']]=c;result.append(c['id'])
        if not result:raise ValueError('Course list format changed')
        return result
    for i,li in enumerate(groups['Required Computer Science Coursework'].find_all('li',recursive=False)):
        cs=extract(clean(li.get_text(' ',strip=True)))
        req.append(requirement(PROGRAM_ID,'cs-'+str(i),'Computer science requirement '+str(i+1),SOURCE_ID,cs,'choose_courses' if len(cs)>1 else 'all',1 if len(cs)>1 else None))
    math=groups['Required Math Coursework'].find_all('li',recursive=False)
    if len(math)!=2:raise ValueError('Math option structure changed')
    for i,li in enumerate(math):
        req.append(requirement(PROGRAM_ID,'math-'+str(i),'Calculus choice' if i==0 else 'Linear algebra choice',SOURCE_ID,extract(clean(li.get_text(' ',strip=True))),'choose_courses',1))
    req.append(requirement(PROGRAM_ID,'electives','Published elective pool',SOURCE_ID,extract(clean(groups['Minor Electives'].get_text(' ',strip=True))),'choose_courses',1))
    return dict(id=PROGRAM_ID,title='Artificial Intelligence and Machine Learning',award_level='minor',program_kind='minor',curriculum_status='partial',courses=list(courses.values()),requirements=req)
