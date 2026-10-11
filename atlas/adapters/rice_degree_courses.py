"""Rice fixed-core description observations; no automatic reviewer certification."""
import hashlib,re
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean,course,rule
BASE='https://ga.rice.edu/programs-study/courses/'
IDENTITIES={
 'COMP 140':('COMPUTATIONAL THINKING','foundations','computational problem solving'),
 'COMP 182':('ALGORITHMIC THINKING','foundations','algorithmic techniques'),
 'COMP 215':('INTRODUCTION TO PROGRAM DESIGN','foundations','principles of software design'),
 'COMP 222':('INTRODUCTION TO COMPUTER ORGANIZATION','systems','instruction set architecture'),
 'COMP 282':('COMPUTATIONAL OPTIMIZATION FOR AI','mathematics','multi-variate calculus and optimization'),
 'COMP 329':('SYSTEMS FOR ARTIFICAL INTELLIGENCE','systems','systems and infrastructure'),
 'COMP 345':('FOUNDATIONS OF MACHINE LEARNING','ai_ml','supervised and unsupervised learning'),
 'COMP 346':('INTRODUCTION TO ARTIFICAL INTELLIGENCE','ai_ml','designing agents that make decisions'),
 'COMP 348':('INTRODUCTION TO DEEP LEARNING','ai_ml','deep neural network architectures'),
 'COMP 456':('AI SENIOR DESIGN I','ai_ml','complete intelligent system'),
 'COMP 457':('AI SENIOR DESIGN II','ai_ml','complete intelligent system'),
 'PHIL 108':('ETHICS OF ARTIFICIAL INTELLIGENCE','human_context','ethical issues and challenges'),
 'PSYC 203':('INTRODUCTION TO COGNITIVE PSYCHOLOGY','applications','topics in cognitive psychology'),
}

# Each option identity and marker was individually read; subjects are not inferred from pools.
IDENTITIES.update({'MATH 101': ('SINGLE VARIABLE CALCULUS I', 'mathematics', 'limits, continuity'),
 'MATH 105': ('AP/OTH CREDIT IN CALCULUS I', 'mathematics', 'approved examinations in calculus'),
 'MATH 102': ('SINGLE VARIABLE CALCULUS II', 'mathematics', 'infinite sequences and series'),
 'MATH 106': ('AP/OTH CREDIT IN CALCULUS II', 'mathematics', 'approved examinations in calculus'),
 'MATH 221': ('HONORS CALCULUS III', 'mathematics', 'linear and multilinear algebra'),
 'MATH 354': ('HONORS LINEAR ALGEBRA', 'mathematics', 'construct mathematical proofs'),
 'MATH 355': ('LINEAR ALGEBRA', 'mathematics', 'systems of linear equations'),
 'CMOR 302': ('MATRIX ANALYSIS', 'mathematics', 'singular value decomposition'),
 'CMOR 303': ('MATRIX ANALYSIS FOR DATA SCIENCE', 'mathematics', 'gradient based methods'),
 'STAT 310': ('PROBABILITY AND STATISTICS', 'mathematics', 'confidence intervals'),
 'STAT 311': ('HONORS PROBABILITY AND MATHEMATICAL STATISTICS',
              'mathematics',
              'asymptotic statistical theory'),
 'STAT 314': ('COMPUTING FOR STATISTICAL ANALYSIS BRIDGE',
              'mathematics',
              'implement statistical methodology'),
 'STAT 315': ('PROBABILITY AND STATISTICS FOR DATA SCIENCE',
              'mathematics',
              'mathematical statistics and computation'),
 'DSCI 301': ('PROBABILITY AND STATISTICS FOR DATA SCIENCE',
              'mathematics',
              'mathematical statistics and computation'),
 'COMP 409': ('LOGIC AND COMPUTER SCIENCE AND ARTIFICIAL INTELLIGENCE',
              'foundations',
              'fundamental role in computer science'),
 'COMP 414': ('OPTIMIZATION: ALGORITHMS, COMPLEXITY AND APPROXIMATIONS',
              'mathematics',
              'smooth optimization techniques'),
 'COMP 480': ('PROBABILISTIC ALGORITHMS AND DATA STRUCTURE',
              'foundations',
              'advanced data structures and algorithms'),
 'COMP 585': ('PROBABILISTIC TOOLKIT FOR LEARNING AND COMPUTING',
              'foundations',
              'apply it in algorithm design'),
 'COMP 459': ('MACHINE LEARNING WITH GRAPHS', 'ai_ml', 'graph-based machine learning algorithms'),
 'COMP 631': ('INTRODUCTION TO INFORMATION RETRIEVAL', 'other', 'information retrieval systems'),
 'COMP 447': ('INTRODUCTION TO COMPUTER VISION', 'ai_ml', 'computer vision algorithms'),
 'ELEC 447': ('INTRODUCTION TO COMPUTER VISION', 'ai_ml', 'computer vision algorithms'),
 'COMP 484': ('NATURAL LANGUAGE PROCESSING', 'ai_ml', 'deep learning approaches'),
 'COMP 442': ('REINFORCEMENT LEARNING', 'ai_ml', 'algorithms for reinforcement learning'),
 'COMP 450': ('ALGORITHMIC AND AI-ENABLED ROBOTICS', 'ai_ml', 'artificial intelligence frameworks'),
 'ELEC 450': ('ALGORITHMIC AND AI-ENABLED ROBOTICS', 'ai_ml', 'artificial intelligence frameworks'),
 'MECH 450': ('ALGORITHMIC AND AI-ENABLED ROBOTICS', 'ai_ml', 'artificial intelligence frameworks'),
 'COMP 462': ('INTRODUCTION TO MODERN ROBOTICS', 'other', 'kinematics, dynamics'),
 'PSYC 430': ('COMPUTATIONAL MODELING OF COGNITIVE PROCESSES',
              'applications',
              'modeling cognitive processes'),
 'PSYC 468': ('HUMAN FACTORS IN ARTIFICIAL INTELLIGENCE',
              'human_context',
              'societal impacts of ai')})
HEADINGS={'comp': 'Computer Science (COMP)', 'phil': 'Philosophy (PHIL)', 'psyc': 'Psychology (PSYC)', 'math': 'Mathematics (MATH)', 'cmor': 'Computational Applied Mathematics and Operations Research (CMOR)', 'stat': 'Statistics (STAT)', 'dsci': 'Data Science (DSCI)', 'elec': 'Electrical and Computer Engineering (ELEC)', 'mech': 'Mechanical Engineering (MECH)'}


def classify_observed(courses):
 for c in courses:
  if c['code']not in IDENTITIES:continue
  title,category,_=IDENTITIES[c['code']]
  if c['name']!=title:raise ValueError('Reviewed Rice title changed: '+c['code'])
  c['category']=category
 return courses


def parse_descriptions(html,*,pid,department):
 s=BeautifulSoup(html,'html.parser');heading=HEADINGS[department]
 if [clean(h.get_text(' ',strip=True))for h in s.find_all('h1')]!=[heading]:raise ValueError('Rice description heading changed')
 courses=[];digests={};requirements=[]
 for code,(title,category,marker) in IDENTITIES.items():
  if not code.startswith(department.upper()+' '):continue
  blocks=[b for b in s.select('.courseblock')if b.select_one('.courseblocktitle')and clean(b.select_one('.courseblocktitle').get_text(' ',strip=True)).startswith(code+' - ')]
  if len(blocks)!=1:raise ValueError('Exact Rice course missing or duplicated: '+code)
  b=blocks[0];label=clean(b.select_one('.courseblocktitle').get_text(' ',strip=True));desc=b.select_one('.courseblockdesc');body=clean(desc.get_text(' ',strip=True))if desc else ''
  if label!=code+' - '+title or marker not in body.casefold():raise ValueError('Reviewed Rice subject changed: '+code)
  credit=b.select_one('.credits');m=re.fullmatch(r'Credit Hours?: (\d+(?:\.\d+)?)',clean(credit.get_text(' ',strip=True)))if credit else None
  if not m:raise ValueError('Rice credit amount changed: '+code)
  sid=pid+'-courses-'+department
  c=course('rice-ai',code,title,sid,BASE+department+'/',credits=float(m[1]),unit='unknown',category=category)
  extras=[clean(x.get_text(' ',strip=True))for x in b.select('.courseblockextra')]
  prerequisites=[x for x in extras if x.startswith(('Prerequisite(s):','Corequisite(s):'))]
  c['prerequisites']=' '.join(prerequisites)or None
  # Rice appends recommendations, cross-lists and exclusions inside the description paragraph.
  label_pattern=r'(?:Cross-list:|Recommended [Pp]rerequisite\(s\):|Mutually Exclusive:|Graduate/Undergraduate Equivalency:|Course URL:)'
  embedded=re.findall(r'('+label_pattern+r'.*?)(?='+label_pattern+r'|$)',body)
  extras += [x for x in embedded if not x.startswith('Course URL:')]
  facts=[x for x in extras if x.startswith(('Restrictions:', 'Recommended Prerequisite(s):', 'Recommended prerequisite(s):', 'Mutually Exclusive:', 'Cross-list:', 'Graduate/Undergraduate Equivalency:'))]
  if facts:
   requirements.append(rule(pid+'-course-entry-'+code.lower().replace(' ','-'),'Course-specific entry and credit conditions: '+code,sid,kind='note',summary=' '.join(facts)))
  if code in ['MATH 101','MATH 102']:
   marker='Should not be taken if student already has credit for'
   if marker not in body or 'without permission' not in body:
    raise ValueError('Rice calculus prior-credit permission changed')
   eligibility=body[body.index(marker):].split('without permission',1)[0]+'without permission.'
   if code=='MATH 101':
    if 'Pre-Calculus Diagnostic Test is required for registration' not in body:
     raise ValueError('Rice calculus diagnostic changed')
    eligibility+=' Pre-Calculus Diagnostic Test is required for registration.'
   requirements.append(rule(pid+'-calculus-entry-'+code.lower().replace(' ','-'),'Calculus prior-credit and placement conditions: '+code,sid,kind='note',summary=eligibility))
  courses.append(c);digests[c['id']]=hashlib.sha256(body.encode()).hexdigest()
  if code=='COMP 457':
   if 'both COMP 456 and COMP 457 must be taken in sequence, in the same academic year'not in body:raise ValueError('Rice senior design sequence condition changed')
   requirements.append(rule(pid+'-senior-design-sequence','AI senior design sequencing',sid,kind='note',summary='COMP 456 and COMP 457 must be completed in sequence within the same academic year. This timing condition does not add another course to the two fixed senior-design requirements.'))
 if department=='comp':
  def full(code):
   matches=[b for b in s.select('.courseblock')if b.select_one('.courseblocktitle')and clean(b.select_one('.courseblocktitle').get_text(' ',strip=True)).startswith(code+' - ')]
   if len(matches)!=1:raise ValueError('Rice applicability course missing: '+code)
   return clean(matches[0].get_text(' ',strip=True))
  if 'Cannot register for COMP 345 if student has credit for COMP 447'not in full('COMP 345')or 'Cannot register for COMP 447 if student has credit for COMP 345'not in full('COMP 447'):raise ValueError('Rice reciprocal credit restriction changed')
  if any('Enrollment is limited to Graduate level students'not in full(code)for code in ['COMP 585','COMP 631']):raise ValueError('Rice graduate-only restriction changed')
  if any('STAT 315'not in (next(c['prerequisites']for c in courses if c['code']==code)or '')for code in ['COMP 345','COMP 346']):raise ValueError('Rice statistics prerequisite changed')
  for key,title,summary in [
   ('vision-conflict','Published vision elective applicability conflict','COMP 345 and COMP 447 contain reciprocal registration exclusions for credit in the other. The major requires COMP 345 and lists COMP 447 as an elective; no permission or waiver is presumed.'),
   ('graduate-options','Graduate-only elective restrictions','COMP 585 and COMP 631 descriptions limit enrollment to Graduate level students. The undergraduate major lists these electives, but undergraduate permission has not been established.'),
   ('statistics-route','Conditional statistics preparation','COMP 345 and COMP 346 specifically list STAT 315 as a prerequisite. Choosing a different published degree statistics route does not establish a STAT 315 waiver and may require additional preparation. This known course-entry condition is not an extra universal fixed degree requirement or, by itself, a curriculum contradiction.')]:
   requirements.append(rule(pid+'-'+key,title,pid+'-courses-comp',kind='note',summary=summary))
 return dict(id=pid,curriculum_status='partial',courses=courses,requirements=requirements,observed_description_digests=digests)


def register(pid,sources,parsers):
 for dep in HEADINGS:
  url=BASE+dep+'/';sources+=(url,)
  parsers[url]=lambda html,dep=dep:parse_descriptions(html,pid=pid,department=dep)
 return sources
