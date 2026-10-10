"""Observe the separate applied minor's course pools and numeric choices."""
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from atlas.adapters.business_society_minors import clean,course,requirement
PROGRAM_ID='case-applied-ai-minor'
SOURCES=('https://bulletin.case.edu/engineering/computer-data-sciences/applied-artificial-intelligence-minor/',)
SOURCE_ID='case-applied-minor-catalog'
def parse(html):
 s=BeautifulSoup(html,'html.parser')
 if not any(clean(h.get_text())=='Applied Artificial Intelligence, Minor' for h in s.find_all('h1')):raise ValueError('Applied minor heading missing')
 block=s.find(id='programrequirementstextcontainer')
 if not block or not block.find('table'):raise ValueError('Requirements table missing')
 cs=[];req=[];current=None
 for tr in block.find('table').find_all('tr'):
  td=tr.find_all('td',recursive=False)
  if not td:continue
  classes=tr.get('class',[]);label=clean(td[0].get_text(' ',strip=True))
  hours=clean(td[-1].get_text());credits=float(hours) if re.fullmatch(r'\d+(?:\.\d+)?',hours) else None
  if 'areaheader' in classes:
   current=requirement(PROGRAM_ID,'group-'+str(len(req)),label,SOURCE_ID,[],credits=credits);req.append(current)
  elif 'areasubheader' in classes:
   if label=='Choose one of the following:':current.update(kind='choose_courses',count=1)
   else:
    m=re.fullmatch(r'Choose at least (\w+) of the following for at least (\w+) credits:',label);n={'one':1,'two':2,'three':3,'four':4,'five':5,'six':6}
    if not m or m[1] not in n or m[2] not in n:raise ValueError('Unrecognized elective choice')
    current.update(kind='choose_courses',count=n[m[1]],credits=n[m[2]],summary=f'Choose at least {n[m[1]]} listed courses totaling at least {n[m[2]]} published credits.')
  elif 'listsum' in classes:
   req.append(requirement(PROGRAM_ID,'total','Published minor total',SOURCE_ID,[],kind='note',credits=credits,summary=label+': '+hours))
  else:
   a=tr.find('a',class_='code')
   if not a:continue
   if current is None:raise ValueError('Course before group')
   c=course(clean(a.get_text(' ',strip=True)),clean(td[1].get_text(' ',strip=True)),PROGRAM_ID,SOURCE_ID,urljoin(SOURCES[0],a['href']),credits)
   cs.append(c);current['course_ids'].append(c['id'])
 if len(req)!=4 or not cs:raise ValueError('Applied minor group structure changed')
 return dict(id=PROGRAM_ID,title='Applied Artificial Intelligence',award_level='minor',program_kind='minor',curriculum_status='partial',courses=cs,requirements=req)

from atlas.adapters.case_minor_courses import register
SOURCES = list(SOURCES)
SOURCE_PARSERS = {}
register(PROGRAM_ID, SOURCES, SOURCE_PARSERS)
