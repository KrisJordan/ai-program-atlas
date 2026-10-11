"""Observed local curricula for the bounded National Universities depth pass.

Audits are manual. Placeholder codes and unresolved publisher IDs are preserved
as requirement notes, never fabricated course identities.
"""
import re
from bs4 import BeautifulSoup
from atlas.adapters.national_depth_discovery import CONFIG, parse_identity

URLS = {
 'fsu': 'https://www.cs.fsu.edu/academics/undergraduate-programs/artificial-intelligence-concentration/',
 'umass': 'https://www.cics.umass.edu/academics/academic-policies/undergraduate-programs-policies/bs-ai-concentration-requirements',
 'rpi': 'https://hass.rpi.edu/cognitive-science/cognitive-science-artificial-intelligence',
 'smu-ba': 'https://catalog.smu.edu/programs/CS-BA/requirements-krhha',
 'smu-bs': 'https://catalog.smu.edu/programs/CS-BS/requirements-krhha',
}
UMASS_BS = 'https://www.cics.umass.edu/academics/academic-policies/undergraduate-programs-policies/bs-computer-science-degree-requirements'
UMASS_TRANSFER = 'https://www.cics.umass.edu/academics/academic-policies/undergraduate-programs-policies/credit-prior-coursework'
SMU_CREDIT = 'https://catalog.smu.edu/policies/credithourpolicy'
FSU_FLOW = 'https://www.cs.fsu.edu/wp-content/uploads/2026/09/AI_Concentration_Flowchart.pdf'
# Crosswalk independently reviewed in the rendered BA and BS requirements, then
# verified at each linked official course record. No unrelated IDs are guessed.
SMU_COURSES = {'0046401': ('CS 5320', 'Artificial Intelligence'), '0268171': ('CS 5324', 'Machine Learning in Python')}
SMU_COURSE_URLS = {k: 'https://catalog.smu.edu/courses/'+k+'/overview-aoYks' for k in SMU_COURSES}



def clean(text):
 return ' '.join(text.split())


def slug(text):
 return re.sub(r'[^a-z0-9]+','-',text.lower()).strip('-')


def root(html, heading):
 s=BeautifulSoup(html,'html.parser')
 if s.find('input',{'type':'password'}) or any(re.match(r'^(Access denied|Forbidden|Sign in|Log ?in|Just a moment)',x.get_text(' ',strip=True),re.I) for x in s.find_all(['h1','title'])):
  raise ValueError('Access gate is not curriculum evidence')
 for n in s.find_all(['script','style','nav','footer','aside']) + s.find_all(attrs={'aria-hidden':'true'}):
  if n.parent is not None:n.decompose()
 if not any(clean(h.get_text(' ',strip=True))==heading for h in s.find_all('h1')):raise ValueError('Expected curriculum heading missing')
 return s.find('main') or s


def course(key,code,name):
 pid=CONFIG[key][0]
 return dict(id=pid+'-'+slug(code),code=code,name=name,description=None,prerequisites=None,credits=None,credit_unit='unknown',category='ai_ml' if code.startswith('CAP') or key=='umass' else 'other',source_id=pid+'-identity',url=URLS[key],public_site=None,syllabus=None)


def rule(key,suffix,title,summary,ids=(),kind='note',count=None,credits=None,parent=None,sid=None,unit='unknown'):
 pid=CONFIG[key][0]
 return dict(id=pid+'-'+suffix,parent_id=pid+'-'+parent if parent else None,title=title,kind=kind,count=count,credits=credits,credit_unit=unit,category='other',source_id=sid or pid+'-identity',source_text=None,summary=summary,course_ids=list(ids))


def result(key,courses,rules):
 pid,title,kind,_=CONFIG[key]
 return dict(id=pid,title=title,award_level=kind,program_kind=kind,curriculum_status='partial',courses=courses,requirements=rules)


def parse_fsu(html):
 key='fsu';parse_identity(html,key);s=root(html,CONFIG[key][3]);block=s.find('div',class_='ai-concentration')
 h=block.find('h3') if block else None
 if not h or clean(h.get_text())!='Required Coursework':raise ValueError('Required coursework section missing')
 listing=h.find_next_sibling('ul')
 items=listing.find_all('li',recursive=False) if listing else []
 if len(items)!=5:raise ValueError('Local requirement structure changed; review needed')
 courses=[];rules=[rule(key,'local','Concentration coursework','Complete the two named core courses and each of the three choices below.',kind='all')]
 def item(text,group,parent):
  m=re.fullmatch(r'([A-Z]{3}) ([0-9X]{4}) — (.+)',clean(text))
  if not m:raise ValueError('Course row format changed')
  code=m[1]+' '+m[2]
  if 'X' in code:
   rules.append(rule(key,group+'-placeholder','Unresolved course placeholder',f'The source lists {code} — {m[3]}; a final catalog course identity is unverified.',parent=parent))
   return None
  c=course(key,code,m[3]);courses.append(c);return c['id']
 core=[]
 for i in range(2):core.append(item(items[i].get_text(' ',strip=True),'core-'+str(i),'local'))
 rules.append(rule(key,'core','AI core','Complete both core courses.',core,'all',parent='local'))
 for idx,label in [(2,'project'),(3,'computing'),(4,'database')]:
  li=items[idx];nested=li.find('ul')
  if nested:
   if not clean(li.get_text(' ',strip=True)).startswith('One of the following:'):raise ValueError('Computing choice rule changed')
   options=[x.get_text(' ',strip=True) for x in nested.find_all('li',recursive=False)]
  else:options=re.split(r'\s+OR\s+',li.get_text(' ',strip=True))
  if len(options)<2:raise ValueError('Alternative course rule missing')
  ids=[];placeholder=any(re.search(r'\b\dXXX\b',x) for x in options)
  rules.append(rule(key,label,label.capitalize()+' choice','Choose one option. Unresolved publisher placeholders remain explicit and are not silently removed from the choice.' if placeholder else 'Choose one of the listed courses.',kind='alternative' if placeholder else 'choose_courses',count=None if placeholder else 1,parent='local'))
  for j,option in enumerate(options):
   cid=item(option,label+'-'+str(j),label)
   if cid:ids.append(cid)
  if placeholder:
   for j,cid in enumerate(ids):rules.append(rule(key,label+'-known-'+str(j),'Named course option','One eligible named option.',[cid],'all',parent=label))
  else:next(r for r in rules if r['id'].endswith('-'+label))['course_ids']=ids
 return result(key,courses,rules)


def parse_umass(html):
 key='umass';parse_identity(html,key);s=root(html,CONFIG[key][3]);tables=s.find_all('table')
 if len(tables)!=2:raise ValueError('Core/elective tables changed')
 courses={};pools=[]
 for table in tables:
  ids=[]
  for tr in table.find_all('tr')[1:]:
   cells=tr.find_all('td')
   if len(cells)!=2:raise ValueError('Course table columns changed')
   code,name=[clean(c.get_text(' ',strip=True)) for c in cells]
   m=re.fullmatch(r'COMPSCI (\d{3})\*?(?: or (\d{3}))?',code)
   if not m:raise ValueError('Course identity format changed')
   for number in filter(None,m.groups()):
    c=course(key,'COMPSCI '+number,name);courses[c['id']]=c;ids.append(c['id'])
  pools.append(ids)
 t=clean(s.get_text(' ',strip=True));pid=CONFIG[key][0]
 m=re.search(r'AI Electives \(Choose (\d+)\)',t)
 if not m or m[1]!='2' or 'At least one elective must be numbered 400 or above' not in t:raise ValueError('Elective selection rules missing')
 required=[pid+'-compsci-311',pid+'-compsci-383',pid+'-compsci-389']; substitute=pid+'-compsci-589'
 if pools[0]!=required or substitute not in courses or 'may substitute COMPSCI 589 Machine Learning for COMPSCI 389' not in t or 'Students may count both courses toward concentration requirements when applicable' not in t:raise ValueError('Core substitution changed; review required')
 rules=[rule(key,'eligibility','Host-degree eligibility','Available to BS Computer Science students; consult the academic advisor about fit and timely completion.'),rule(key,'core','Three core courses','Complete algorithms, AI and the machine-learning core or qualified substitution.',kind='all'),rule(key,'fixed-core','Algorithms and AI','Complete both courses.',required[:2],'all',parent='core'),rule(key,'ml-core','Machine-learning core','COMPSCI 389 is the standard course; students who qualify may substitute COMPSCI 589.',[required[2],substitute],'choose_courses',1,parent='core'),rule(key,'substitution','Conditional substitution and overlap','Qualification criteria for the 589 substitution are not stated here. Both 389 and 589 may count when applicable; this does not establish unrestricted double counting.'),rule(key,'electives','AI electives','Choose two approved AI electives; at least one must be 400 level or above.',pools[1],'choose_courses',int(m[1])),rule(key,'upper-level','Upper-level elective condition','At least one of the two electives must be numbered 400 or above; this is a subset condition, not a third elective.',[x for x in pools[1] if int(courses[x]['code'].split()[-1])>=400],parent='electives')]
 return result(key,list(courses.values()),rules)


def parse_rpi(html):
 key='rpi';parse_identity(html,key);s=root(html,CONFIG[key][3]);t=clean(s.get_text(' ',strip=True));m=re.search(r'must complete a minimum of (\d+) credits',t)
 if not m or 'Course topics may include:' not in t:raise ValueError('Minor minimum or example-topic context missing')
 return result(key,[],[rule(key,'minimum','Published minor minimum','Complete at least '+m[1]+' published credits. The normalized unit and full catalog inventory remain unverified.',credits=float(m[1])),rule(key,'topic-boundary','Illustrative course topics','The department supplies example topics rather than an exhaustive required-course pool; the catalog requirements remain inaccessible.')])


def parse_smu(html,key):
 degree='BA' if key=='smu-ba' else 'BS';s=root(html,f'CS-{degree} - Computer Science');t=clean(s.get_text(' ',strip=True));pid=CONFIG[key][0];sid=pid+'-requirements'
 if degree=='BA':
  b=next((b for b in s.find_all('button',attrs={'aria-controls':True}) if re.fullmatch(r'Artificial Intelligence and Machine Learning Track \(\d+ Credit Hours\)',clean(b.get_text(' ',strip=True)))),None)
  if not b:raise ValueError('BA AI track section missing')
  section=clean(b.get_text(' ',strip=True))+' '+clean(s.find(id=b['aria-controls']).get_text(' ',strip=True))
 else:
  marker='Computer Science B.S. with a specialization in Artificial Intelligence and Machine Learning Specialization'
  if marker not in t:raise ValueError('BS AI specialization heading missing')
  section=re.split(r'Computer Science B\.S\.|Total Credits',t.split(marker,1)[1],maxsplit=1)[0]
 total=re.search(r'\((\d+) Credit Hours\)',section);elective=re.search(r'(\d+) credit hours of track electives approved by adviser',section)
 ids=re.findall(r'\b\d{7}\b',section)
 if not total or not elective or not ids or 'Complete ALL of the following Courses:' not in section:raise ValueError('Track rule or unresolved course list missing')
 rules=[rule(key,'total','Local track minimum','Complete '+total[1]+' credit hours for this '+degree+' track/specialization. Semester unit is independently verified by SMU credit-hour policy.',credits=float(total[1]),sid=sid,unit='semester_hours'),rule(key,'required-identities','Required course identities unresolved','Complete all required entries. The public catalog renders publisher IDs '+', '.join(ids)+' without course codes or titles; these have not been converted into fabricated course records.',sid=sid),rule(key,'approved-elective','Advisor-approved track elective','Complete '+elective[1]+' credit hours of track electives approved by the advisor. The source states an approval criterion rather than a finite elective pool.',credits=float(elective[1]),sid=sid,unit='semester_hours')]
 overlap='Technical electives cannot be satisfied by courses that are part of the student’s chosen track.'
 if overlap in t:rules.append(rule(key,'overlap','Host-degree technical elective separation','Track courses cannot also satisfy the separate host-degree technical electives.',sid=sid))
 else:raise ValueError('Host-degree track overlap policy missing')
 courses=[];unresolved=[]
 for publisher_id in ids:
  if publisher_id not in SMU_COURSES:
   unresolved.append(publisher_id);continue
  code,name=SMU_COURSES[publisher_id];entry=course(key,code,name);entry.update(source_id=sid,url=SMU_COURSE_URLS[publisher_id],category='ai_ml');courses.append(entry)
 rules[1]=rule(key,'required-courses','Required AI/ML courses','Complete both courses. Publisher IDs are matched to course identities independently verified in the rendered program page and linked course records.',[x['id'] for x in courses],'all',sid=sid)
 if unresolved:rules.append(rule(key,'unresolved-identities','Unresolved publisher course IDs','Unresolved course entries: '+', '.join(unresolved)+'. No code or title is inferred.',sid=sid))
 return result(key,courses,rules)


def parse_umass_bs(html):
 key='umass';s=root(html,'BS in Computer Science Degree Requirements');t=clean(s.get_text(' ',strip=True));sid=CONFIG[key][0]+'-bs-policies'
 if 'may not use any course taken on a pass/fail basis' not in t or 'at least C (2.0)' not in t or 'Courses saved must not be used for any requirements for the undergraduate degree' not in t:raise ValueError('Major grade policy changed')
 return {'id':CONFIG[key][0],'requirements':[rule(key,'host-grading','Host-major grading','Courses used for the CS program cannot be taken pass/fail. The major requires a C (2.0) average; lower passing grades may count but normally do not satisfy later-course prerequisites.',sid=sid),rule(key,'graduate-saving','Courses reserved for graduate study','A course saved for a graduate program cannot meet any undergraduate degree requirement.',sid=sid)]}


def parse_umass_transfer(html):
 key='umass';s=root(html,'Credit for Prior Coursework');t=clean(s.get_text(' ',strip=True));sid=CONFIG[key][0]+'-prior-coursework'
 if 'No Credit for the Same Course Twice' not in t or 'official UMass transcript' not in t or 'this option does not apply to transfer credit' not in t:raise ValueError('Prior-coursework policy missing')
 return {'id':CONFIG[key][0],'requirements':[rule(key,'transfer-entry','Prior coursework and prerequisites','Enrollment eligibility relies on prerequisites posted to the UMass transcript; disputed or unmapped transfer work needs evaluation and approval. An override does not waive the requirement to document prerequisites.',sid=sid),rule(key,'duplicate-credit','No duplicate AP/transfer course credit','Retaking an AP/transfer-equivalent course earns zero credits unless eligible AP credit is removed; the removal option does not apply to transfer credit.',sid=sid)]}


def parse_smu_credit(html,key):
 s=root(html,'SMU Credit Hour Policy');t=clean(s.get_text(' ',strip=True))
 if 'Semester Credit Hour at SMU' not in t or 'applies to all courses, academic programs' not in t:raise ValueError('SMU credit unit policy missing')
 return {'id':CONFIG[key][0],'requirements':[rule(key,'credit-unit','Credit-unit definition','SMU defines its program credit hours as semester credit hours.',sid=CONFIG[key][0]+'-credit-policy')]}


def parse_fsu_flowchart_text(text):
 """Reviewed PDF text adapter; caller must first verify the PDF layout visually."""
 key='fsu';pid=CONFIG[key][0];sid=pid+'-flowchart'
 if 'Computer Science Concentration in AI' not in text:raise ValueError('Flowchart heading missing')
 m=re.search(r'This Concentration requires (\d+) Credits',text)
 if not m:raise ValueError('Flowchart credit total missing')
 courses=[]
 pattern=r'^([A-Z]{3})\s+(\d{4})(?:\s*\((\d+)\))?\s*(.*?)\*Prerequisites?\s*-\s*([^*]+)\*'
 for match in re.finditer(pattern,text,re.S|re.M):
  prefix,number,credits,name,prereq=match.groups()
  # Stop a malformed block from swallowing a separate course or the diagram.
  if re.search(r'\b[A-Z]{3}\s+\d{4}',name):continue
  c=course(key,prefix+' '+number,clean(name));c.update(credits=float(credits) if credits else None,prerequisites=clean(prereq),source_id=sid,url=FSU_FLOW);courses.append(c)
 if len(courses)<8:raise ValueError('Flowchart prerequisite blocks missing')
 return {'id':pid,'courses':courses,'requirements':[rule(key,'credit-minimum','Published concentration minimum','The linked flowchart states '+m[1]+' credits. Normalized credit unit remains unverified.',credits=float(m[1]),sid=sid)]}


def parse_smu_course(html,key,publisher_id):
 code,_=SMU_COURSES[publisher_id];s=root(html,code.replace(' ',''))
 fields={}
 for heading in s.find_all('h3',class_='field-label'):
  value=heading.parent.find(class_='field-value')
  if value:fields[clean(heading.get_text())]=clean(value.get_text(' ',strip=True))
 if fields.get('Career')!='Undergraduate' or not fields.get('Title') or not fields.get('Description'):raise ValueError('Undergraduate course fields missing')
 description=fields['Description'];parts=re.split(r'Prerequisites?:\s*',description,maxsplit=1)
 if len(parts)!=2:raise ValueError('Published prerequisite statement missing')
 minimum=fields.get('Min Credits');maximum=fields.get('Max Credits')
 if not minimum or minimum!=maximum or not re.fullmatch(r'\d+(?:\.\d+)?',minimum):raise ValueError('Fixed course credits missing or changed')
 entry=course(key,code,fields['Title']);entry.update(description=parts[0].split('. ',1)[0].rstrip('.')+'.',prerequisites=parts[1],credits=float(minimum),credit_unit='semester_hours',category='ai_ml',source_id=CONFIG[key][0]+'-course-'+publisher_id,url=SMU_COURSE_URLS[publisher_id])
 return {'id':CONFIG[key][0],'courses':[entry]}
