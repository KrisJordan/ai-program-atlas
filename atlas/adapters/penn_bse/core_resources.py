"""Public BSE core offering observations, preserving term and description boundaries."""
import hashlib,re
from bs4 import BeautifulSoup
from .common import penn_course,text
PID='penn-bse-ai'
RESOURCES={
 'cis1100':('https://www.engineering.upenn.edu/~cis110/current/py/index.html','CIS 1100',None,'fundamentals of computer programming in Python','foundations'),
 'cis1200':('https://www.engineering.upenn.edu/~cis120/current/','CIS 1200','Fall 2026','design aspects of programming','foundations'),
 'cis1200-syllabus':('https://www.engineering.upenn.edu/~cis120/current/syllabus/','CIS 1200','Fall 2026','fundamental concepts of programming','foundations'),
 'cis1210':('https://www.engineering.upenn.edu/~cis1210/current/','CIS 1210','Fall 2026','Data Structures and Algorithms','foundations'),
 'cis1600':('https://www.cis.upenn.edu/~cis1600/current/','CIS 1600','Fall 2026','discrete probability, expectation, mathematical Induction','mathematics'),
 'cis2450':('https://sites.google.com/seas.upenn.edu/cis-2450-spring-2026/home','CIS 2450','Spring 2026','fundamentals of scaling computation','systems'),
}


def parse_resource(html,key):
 url,code,term,marker,category=RESOURCES[key]
 soup=BeautifulSoup(html,'html.parser');body=text(soup)
 if code.replace(' ','') not in body.replace(' ','') or marker not in body or term and term not in body:
  raise ValueError('Penn public course identity, term or subject changed: '+key)
 if key=='cis1200-syllabus' and 'Syllabus' not in body:raise ValueError('Penn syllabus heading missing')
 c=penn_course(code,None,PID+'-core-'+key,url,category)
 c['public_site']=url
 if key=='cis1200-syllabus':c['syllabus']=url
 # These values are offering-specific observations, not inferred catalog-wide prerequisites.
 if key=='cis1210':
  m=re.search(r'Prerequisites: (.+?) Grading:',body)
  if not m:raise ValueError('Penn1210 prerequisite section changed')
  c['prerequisites']=term+' offering: '+m[1]
 return dict(id=PID,courses=[c],requirements=[],observed_description_digests={c['id']:hashlib.sha256(body.encode()).hexdigest()},observed_offering=term,notes=['Public offering evidence; no individual course units or current catalog edition inferred.'])


def register(sources,parsers):
 for key,(url,*_)in RESOURCES.items():
  if url not in sources:sources.append(url)
  parsers[url]=lambda html,key=key:parse_resource(html,key)
