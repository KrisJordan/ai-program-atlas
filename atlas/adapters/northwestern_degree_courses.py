"""Exact Northwestern core observations; independent reviews remain seed-only."""
import hashlib
import re
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean,course
BASE='https://catalogs.northwestern.edu/undergraduate/courses-az/'
# Category and source title are reviewed independently of the requirement slot.
IDENTITIES={
 'COMP_SCI 111-0':('Fundamentals of Computer Programming','foundations','recursive algorithms'),
 'COMP_SCI 180-0':('Software Design & Composition','foundations','testing of software'),
 'COMP_SCI 208-0':('Data Structures & Algorithms','foundations','data structures and their algorithms'),
 'COMP_SCI 211-0':('Programming in Systems-Level Languages','foundations','foundational software design'),
 'COMP_SCI 212-0':('Math Foundations of CS Part 1: Discrete Math for CS','mathematics','finite and structural mathematics'),
 'COMP_SCI 348-0':('Introduction to Artificial Intelligence','ai_ml','core techniques and applications of ai'),
 'COMP_SCI 349-0':('Machine Learning','ai_ml','algorithms that improve through experience'),
 'GEN_ENG 150-0':('Programming for Engineers','foundations','object-oriented programming'),
 'GEN_ENG 151-0':('Honors Programming for Engineers','foundations','object-oriented programming'),
 'GEN_ENG 231-0':('Probability and Statistics for Engineers','mathematics','probability theory'),
 'GEN_ENG 241-0':('Linear Algebra for Engineers','mathematics','vector spaces and bases'),
 'DSGN 106-1':('Design Thinking and Communication','other','user-centered design process and technical communication'),
 'DSGN 106-2':('Design Thinking and Communication','other','user-centered design process and technical communication'),
 'ENGLISH 106-1':('Writing in Special Contexts','human_context','expository writing'),
 'ENGLISH 106-2':('Writing in Special Contexts','human_context','expository writing'),
}

def classify_observed(courses):
 for c in courses:
  if c['code'] not in IDENTITIES:continue
  title,category,_=IDENTITIES[c['code']]
  observed=(c['name'] or '').removesuffix(' (Formerly Comp_Sci 214)')
  if observed != title:raise ValueError('Reviewed Northwestern title changed: '+c['code'])
  c['category']=category
 return courses


def parse_descriptions(html,*,pid,department):
 s=BeautifulSoup(html,'html.parser')
 heading={'comp_sci':'Computer Science (COMP_SCI)','gen_eng':'General Engineering (GEN_ENG)','dsgn':'Segal Design Institute (DSGN)','english':'English (ENGLISH)'}[department]
 if [clean(h.get_text(' ',strip=True))for h in s.find_all('h1') if clean(h.get_text(' ',strip=True)) != 'Academic Catalog']!=[heading]:raise ValueError('Northwestern description heading changed')
 courses=[];digests={}
 for code,(title,category,marker) in IDENTITIES.items():
  if not code.startswith(department.upper()+' '):continue
  blocks=[b for b in s.select('.courseblock') if b.select_one('.courseblocktitle, .couresblocktitle') and clean(b.select_one('.courseblocktitle, .couresblocktitle').get_text(' ',strip=True)).startswith(code+' ')]
  if len(blocks)!=1:raise ValueError('Exact Northwestern course missing or duplicated: '+code)
  b=blocks[0];label=clean(b.select_one('.courseblocktitle, .couresblocktitle').get_text(' ',strip=True))
  m=re.fullmatch(re.escape(code)+r' (.+) \((\d+(?:\.\d+)?) Units?\)',label)
  desc=b.select_one('.courseblockdesc');body=clean(desc.get_text(' ',strip=True))if desc else ''
  if not m or m[1]!=title or marker not in body.casefold():raise ValueError('Reviewed Northwestern subject changed: '+code)
  c=course('nw-bse',code,m[1],pid+'-courses-'+department,BASE+department+'/',credits=float(m[2]),unit='units',category=category)
  prereq=re.search(r'Prerequisites?:.*',body)
  c['prerequisites']=prereq[0]if prereq else None
  courses.append(c);digests[c['id']]=hashlib.sha256(body.encode()).hexdigest()
 return dict(id=pid,curriculum_status='partial',courses=courses,requirements=[],observed_description_digests=digests)


def register(pid,sources,parsers):
 for dep in ['comp_sci','gen_eng','dsgn','english']:
  url=BASE+dep+'/';sources+=(url,)
  parsers[url]=lambda html,dep=dep:parse_descriptions(html,pid=pid,department=dep)
 return sources
