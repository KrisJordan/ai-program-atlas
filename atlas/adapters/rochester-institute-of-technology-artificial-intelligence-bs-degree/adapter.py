"""Observe accessible study-page facts; browser-reviewed catalog remains curated."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.business_society_minors import clean,requirement
PROGRAM_ID='rochester-institute-of-technology-artificial-intelligence-bs-degree'
SOURCES=('https://www.rit.edu/study/artificial-intelligence-bs',)
SOURCE_ID=PROGRAM_ID+'-official'
def parse(html):
 s=BeautifulSoup(html,'html.parser')
 if not any(clean(h.get_text(' ',strip=True))=='Artificial Intelligence Bachelor of Science Degree' for h in s.find_all('h1')):raise ValueError('AI degree heading missing')
 text=clean(s.get_text(' ',strip=True))
 m=re.search(r'Students in the BS in artificial intelligence are required to complete (\w+) blocks of cooperative education experience\.',text)
 numbers={'one':1,'two':2,'three':3,'four':4}
 if not m or m[1] not in numbers:raise ValueError('Co-op block requirement missing or changed')
 r=requirement(PROGRAM_ID,'coop','Cooperative education blocks',SOURCE_ID,[],kind='note',summary='Complete '+str(numbers[m[1]])+' cooperative education blocks.')
 result=dict(id=PROGRAM_ID,title='Artificial Intelligence',award_level='BS',program_kind='degree',curriculum_status='partial',requirements=[r])
 if s.select('.courseblock'):
  from atlas.adapters.rit_ai_degree_courses import parse_rendered_courses
  result['courses']=parse_rendered_courses(html)['courses']
 return result

from atlas.adapters.rit_policies import register
SOURCES = list(SOURCES)
SOURCE_PARSERS = globals().get("SOURCE_PARSERS", {})
register(PROGRAM_ID, SOURCES, SOURCE_PARSERS, minor=False)

from atlas.adapters.rit_general_education import register as register_general_education
register_general_education(PROGRAM_ID,SOURCES,SOURCE_PARSERS)
