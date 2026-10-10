"""Observe Miami degree tables, preserving source alternatives and elective pools."""
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from atlas.adapters.business_society_minors import course,requirement,clean

def observe(html,pid,title,award,heading,sid,url):
 s=BeautifulSoup(html,'html.parser')
 if not any(clean(h.get_text())==heading for h in s.find_all('h1')):raise ValueError('Degree heading missing')
 block=s.find(id='curriculumtextcontainer')
 if not block or not block.find('table'):raise ValueError('Curriculum table missing')
 for sup in block.find_all('sup'):sup.decompose()
 courses={};req=[];section=None;previous=None;pool=False;serial=0
 def node(title,kind='all',ids=None,count=None,credits=None,summary=None,parent=None):
  nonlocal serial
  serial+=1;r=requirement(pid,'table-'+str(serial),title,sid,ids or [],kind,count,credits,summary=summary);r['parent_id']=parent;req.append(r);return r
 for row in block.find('table').find_all('tr'):
  cells=row.find_all('td',recursive=False)
  if not cells:continue
  label=clean(cells[0].get_text(' ',strip=True));classes=row.get('class',[])
  value=clean(cells[-1].get_text());amount=float(value) if re.fullmatch(r'\d+(?:\.\d+)?',value) else None
  a=row.find('a',class_='code')
  # Inline references in an uncoded requirement are not a course row.
  if a and len(cells)<3 and 'orclass' not in classes:
   node(label,'note',credits=amount,summary=label+(' — '+value+' published credits' if value else ''),parent=section['id'] if section else None)
   continue
  if 'listsum' in classes:
   node(label,'note',credits=amount,summary='Published total: '+value+' credit hours.');continue
  if a:
   code=clean(a.get_text(' ',strip=True));name=clean(cells[1].get_text(' ',strip=True))
   c=course(code,name,pid,sid,urljoin(url,a['href']),amount if len(cells)==3 else None)
   # A repeated course can be listed with contextual annotations; preserve first label and observed credit amount.
   if c['id'] not in courses:courses[c['id']]=c
   elif courses[c['id']]['credits'] is None and c['credits'] is not None:courses[c['id']]['credits']=c['credits']
   if section is None:raise ValueError('Course before section')
   if pool:
    if c['id'] not in section['course_ids']:section['course_ids'].append(c['id'])
    if 'orclass' in classes:
     if previous is None:raise ValueError('Or choice without predecessor')
     node('Alternative within elective pool','note',[previous,c['id']],summary='The source lists these as alternatives within the elective pool; they are not two independently required courses.',parent=section['id'])
    previous=c['id'];continue
   if 'orclass' in classes:
    if previous is None:raise ValueError('Alternative without required predecessor')
    if previous['kind']!='choose_courses':
     previous.update(kind='choose_courses',count=1,title='Course alternatives',summary=previous['summary']+' Complete one listed alternative for this requirement.')
    previous['course_ids'].append(c['id'])
   else:
    previous=node(name,ids=[c['id']],summary=name+(' — published credit amount/range: '+value if value else ''),parent=section['id'])
   continue
  # Every table label remains visible, including uncoded cognates and credit ranges.
  is_pool=('Electives'==label and amount is not None) or label in ['Techniques','Applications'] or 'Major Choice Courses' in label or 'Quantitative Choice -' in label
  if not is_pool and ('areaheader' in classes or label in ['Core Computer Science Courses','Core Mathematics Courses','Additional Required Course for the Major']):
   section=node(label,credits=amount,summary=label+(' — '+value+' published credits' if value else ''))
   pool=False;previous=None
  if is_pool:
   if label in ['Techniques','Applications'] and amount is None and section and pool:
    node(label+' pool label','note',parent=section['id']);continue
   m=re.search(r'Select (one|two|three)\b',label);count={'one':1,'two':2,'three':3}[m[1]] if m else None
   section=node(label,'choose_courses' if count else 'note',count=count,credits=amount,summary=label+(' — '+value+' published credits' if value else '')+'. Listed courses are options, not all required. Credit units require independent review.')
   pool=True;previous=None
  elif 'areaheader' not in classes and label not in ['Core Computer Science Courses','Core Mathematics Courses','Additional Required Course for the Major']:
   r=node(label,'note',credits=amount,summary=label+(' — '+value+' published credits' if value else ''),parent=section['id'] if section else None)
   if 'Advanced Writing and Communication Requirement' in label:
    section=r;pool=False;previous=None
 if not courses or not req:raise ValueError('Empty curriculum')
 return dict(id=pid,title=title,award_level=award,program_kind='degree',curriculum_status='partial',courses=list(courses.values()),requirements=req)
