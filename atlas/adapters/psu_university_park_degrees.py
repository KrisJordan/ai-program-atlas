"""Current University Park AI degree tables; alternatives are not extra requirements."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.confirmed_depth3 import parse_psu
from atlas.adapters.national_curriculum_common import clean, course, rule, require_phrases

CREDIT_URL='https://senate.psu.edu/students/policies-and-rules-for-undergraduate-students/42-00-acquisition-of-credit/'
CONFIG={
 'penn-state-ai-engineering-bs':('Artificial Intelligence Engineering, B.S.','AIE_BS','engineering/artificial-intelligence-engineering-bs/'),
 'penn-state-ai-methods-applications-ist-bs':('Artificial Intelligence Methods and Applications, B.S. (Information Sciences and Technology)','AIMA_BS','information-sciences-technology/artificial-intelligence-methods-applications-bs/'),
}

def parse_degree(html,pid):
 title,plan,path=CONFIG[pid]; result=parse_psu(html,pid,title,plan)
 url='https://bulletins.psu.edu/undergraduate/colleges/'+path;sid=pid+'-catalog'
 soup=BeautifulSoup(html,'html.parser');root=soup.find(id='programrequirementstextcontainer')
 table=root.select_one('table.sc_courselist')
 if table is None: raise ValueError('Major course table missing')
 rows=table.find('tbody').find_all('tr',recursive=False)
 courses={};reqs=result['requirements'];major=rule(pid+'-major','Requirements for the Major',sid)
 reqs.append(major);section=major;pool=None;previous=None
 def add(title,kind='all',ids=(),parent=None,credits=None,summary=None):
  r=rule(pid+'-major-r'+str(len(reqs)),title,sid,ids,parent=parent or section['id'],kind=kind,credits=credits,unit='semester_hours',summary=summary)
  reqs.append(r);return r
 for row in rows:
  cells=row.find_all('td',recursive=False)
  if not cells:continue
  label=clean(cells[0].get_text(' ',strip=True));hours=row.find('td',class_='hourscol');raw=clean(hours.get_text(' ',strip=True)) if hours else ''
  amount=int(raw) if raw.isdigit() else None
  if raw and not re.fullmatch(r'\d+(?:-\d+)?',raw):raise ValueError('Unexpected major credit expression')
  if 'areaheader' in row.get('class',[]):
   section=add(label,parent=major['id']);pool=None;previous=None;continue
  links=cells[0].select('a.code')
  if not links:
   if not label:raise ValueError('Empty requirement comment')
   if re.fullmatch(r'Select \d+ credits from the following:',label):
    pool=add(label,kind='choose_credits',credits=amount);previous=None
   else:
    add(label,kind='note',credits=amount,summary=label+' This is an unexpanded source condition, not an all-required course list.')
    pool=None;previous=None
   continue
  codes=[clean(a.get_text(' ',strip=True)) for a in links]
  names=[clean(s) for s in cells[1].stripped_strings]
  names=[re.sub(r'^(?:and\s+|&\s*)','',n) for n in names]
  names=[n for n in names if n not in ['and','&']]
  if len(codes)!=len(names):raise ValueError('Course sequence titles do not match codes')
  ids=[]
  for code,name in zip(codes,names):
   if not re.fullmatch(r'[A-Z-]+ \d+[A-Z]*',code):raise ValueError('Unexpected PSU course identity')
   c=course('psu',code,name,sid,url,credits=amount if len(codes)==1 else None,unit='semester_hours')
   courses[c['id']]=c;ids.append(c['id'])
  is_or='orclass' in row.get('class',[])
  if is_or:
   if previous is None or pool is not None:raise ValueError('Unattached alternative row')
   if previous['kind']!='alternative':
    primary_ids=previous['course_ids'];previous['course_ids']=[];previous['kind']='alternative'
    # Amount on first row describes the alternative group, not every option.
    for cid in primary_ids:courses[cid]['credits']=None
    add('First course route',ids=primary_ids,parent=previous['id'])
   add('Alternative course route',ids=ids,parent=previous['id'])
  elif pool is not None:
   if len(ids)>1:add('Complete the listed course sequence',ids=ids,parent=pool['id'],credits=amount)
   else:pool['course_ids'].extend(ids)
  else:
   previous=add(' + '.join(codes),ids=ids,credits=amount)
   if raw and amount is None:previous['summary']='Source group credit range: '+raw+'; no single amount is inferred.'
 if not courses:raise ValueError('No major courses observed')
 # These source policy sections contain no additions to the course identity set.
 for section_id,label in [('howtogetintextcontainer','Entrance to major'),('programrequirementstextcontainer','Degree and general education policies')]:
  node=soup.find(id=section_id)
  if node is None:raise ValueError('Required degree policy section missing')
  text=clean(node.get_text(' ',strip=True))
  if section_id.startswith('how'):
   match=re.search(r'minimum grade point average of ([\d.]+)',text)
   if not match or 'grade of C or better' not in text:raise ValueError('Entrance policy changed')
   reqs.append(rule(pid+'-entrance',label,sid,kind='note',summary='Entrance requires GPA '+match[1]+' through the request semester and C or better in the source-listed entry courses. Entry conditions do not create additional course identities: '+text.split('Academic Advising')[0]))
 require_phrases(root,['2.00 grade-point average','6 credits are required and may satisfy other requirements','3 credits required from the college of graduation','up to 24 credits of course work in the major','Foundations (grade of C or better is required','Inter-Domain Courses (Inter-Domain): 6 credits'])
 reqs.extend([
  rule(pid+'-ge','General Education distribution',sid,kind='note',credits=45,unit='semester_hours',summary='45 semester hours: GQ 6 and GWS 9 with C or better; breadth GA, GHW, GH, GS and GN 3 each; Inter-Domain 6; exploration GN 3 plus eligible domains 6. Foundations/breadth exclude Inter-Domain. Exploration permits the stated advanced-world-language condition. Major overlap is limited to the program-specific allocation.'),
  rule(pid+'-cultures','Cultures and writing overlays',sid,kind='note',summary='US cultures 3 plus international cultures 3 may satisfy other requirements. Three writing-across-curriculum credits must come from the college of graduation; no extra course count is inferred from overlays.'),
  rule(pid+'-completion','University completion and credit-source conditions',sid,kind='note',summary='Complete the major and earn at least 2.00 GPA within the degree program. University minimum is 120 credits, overridden by a higher program minimum. The dean/chancellor and faculty may require up to 24 major credits at the degree location/program; source/time restrictions remain subject to Senate 83-80. First-year engagement depends on the college plan.'),
 ])
 if plan=='AIE_BS':
  require_phrases(root,['102-103','21 of the 45 credits','remaining 24 General Education credits must be distinct'])
  reqs.append(rule(pid+'-overlap','Engineering major and GE accounting',sid,kind='note',summary='Major 102–103 semester hours; 21 GE hours overlap (GN 6, GQ 6, GWS 9). The remaining 24 GE hours must be distinct from the major. The degree minimum is 126, not the sum of all option identities. C-minimum designations are scoped to the table sections that explicitly require them.'))
 else:
  require_phrases(root,['A grade of C or better is required for all courses in the major','6 of the 45 credits','Electives 14','Requirements for the Major 67'])
  reqs.append(rule(pid+'-overlap','IST major and GE accounting',sid,kind='note',summary='Major 67 semester hours; six GQ hours overlap the 45-hour GE requirement; 14 free-elective hours. Every major course requires C or better. The 120-hour total is not a sum of every alternative. The capstone row requires six credits selected from the paired AIMA430/440 sequence or A-I494 research; repetition/combination details require course and departmental confirmation.'))
  parse_ist_supporting(soup,pid,sid,url,courses,reqs)
 result['courses']=list(courses.values());result['requirements']=reqs
 return result

def parse_ist_supporting(soup,pid,sid,url,courses,reqs):
 """Read the actual supporting lists, not the illustrative semester plan."""
 plan=soup.find(id='suggestedacademicplantextcontainer')
 if plan is None:raise ValueError('IST supporting-list section missing')
 def list_after(label):
  marker=plan.find('strong',string=lambda s:s and clean(s)==label)
  listing=marker.parent.find_next_sibling('ul') if marker else None
  if listing is None:raise ValueError('Supporting list missing: '+label)
  return listing
 technical=list_after('Technical Supporting Courses:')
 application=list_after('Application Supporting Courses:')
 require_phrases(technical,['Select 9 credits','at least 3 credits must be at the 400-level','Any CYBER course at the 300- or 400-level'])
 require_phrases(application,['Select 9 credits','at least 3 credits must be at the 300- or 400-level','up to 6 credits of ROTC','choose a focus area and take a sequence of courses from the chosen focus area'])
 def node(title,parent,kind='choose_credits',credits=9):
  r=rule(pid+'-support-'+str(len(reqs)),title,sid,parent=parent,kind=kind,credits=credits,unit='semester_hours')
  reqs.append(r);return r
 def entries(listing,target):
  for item in listing.find_all('li',recursive=False):
   # CourseLeaf retains some printed identities without a linked description.
   # Those are evidence of list membership, not evidence of current metadata.
   codes=[clean(a.get_text(' ',strip=True)) for a in item.select('.sc_courseinline')]
   if any(not re.fullmatch(r'[A-Z-]+ \d+[A-Z]*',code) for code in codes):
    raise ValueError('Supporting course identity changed')
   text=clean(item.get_text(' ',strip=True))
   if not codes:
    reqs.append(rule(pid+'-support-note-'+str(len(reqs)),text,sid,parent=target['id'],kind='note',summary=text+' This source-defined open predicate adds no invented course IDs.'))
    continue
   ids=[]
   for code in codes:
    c=course('psu',code,None,sid,url,unit='semester_hours')
    courses.setdefault(c['id'],c);ids.append(c['id'])
   if len(ids)>1:
    alt=node(text,target['id'],kind='alternative',credits=None)
    alt['course_ids']=ids;alt['summary']='The source lists these as one alternative/cross-listed option: '+text+'. Do not count cross-listed identities as multiple earned courses.'
   else:target['course_ids'].extend(ids)
 technical_rule=node('Technical supporting courses: nine hours, including three at 400 level',pid+'-major')
 technical_rule['summary']='Select at least nine semester hours including at least three at 400 level from the printed options or the explicit open CYBER 300/400-level range. Research and internship amounts are variable; the list does not establish reuse of capstone credit.'
 for group in technical.find_all('li'):
  if group.find('strong',recursive=False):
   listing=group.find('ul',recursive=False)
   if listing:entries(listing,technical_rule)
 focus=node('Choose one application supporting focus',pid+'-major',kind='alternative',credits=None)
 focus['summary']='Choose one focus and complete a sequence of at least nine semester hours from that focus, including three at 300/400 level; at most six ROTC credits. The alternate Commonwealth-campus business list is not the University Park route.'
 headings=[]
 for group in application.find_all('li'):
  heading=group.find('strong',recursive=False)
  if not heading:continue
  title=clean(heading.get_text(' ',strip=True));headings.append(title)
  if 'Commonwealth Campuses' in title:continue
  r=node(title,focus['id']);r['summary']='Complete the chosen focus sequence: nine semester hours, including three at 300/400 level; up to six ROTC credits. Source list eligibility does not waive prerequisites.'
  listing=group.find('ul',recursive=False)
  if listing:entries(listing,r)
 if len(headings)!=11:raise ValueError('Application focus scope changed; review campus applicability')

def parse_units(html,pid):
 soup=BeautifulSoup(html,'html.parser')
 require_phrases(soup,['Courses at Penn State carry semester hours of credit'])
 return {'id':pid,'requirements':[rule(pid+'-credit-unit','Credit unit definition',pid+'-credit-policy',kind='note',summary='Penn State courses carry semester hours of credit; the institution evaluates conversion from other credit systems. This is an explicit unit definition, not an inference from the academic calendar.')]}

DEGREE_POLICY_URL='https://senate.psu.edu/students/policies-and-rules-for-undergraduate-students/82-00-and-83-00-degree-requirements/'
def parse_residence_notice(html,pid):
 soup=BeautifulSoup(html,'html.parser')
 require_phrases(soup,['83-80 Limitations on Source and Time for Credit Acquisition','June 23, 2026','Pending implementation procedures','at least 36 of the last 60 credits','five calendar years','Any college may make more restrictive limitations'])
 return {'id':pid,'requirements':[rule(pid+'-residence-notice','Residence policy version requires clarification',pid+'-degree-policy',kind='note',summary='Senate 83-80 displays 36 of the final 60 baccalaureate credits in university/cooperative programs and a five-calendar-year limit for the last 60, plus stricter college authority and appeals. It also announces June 23, 2026 revisions with implementation procedures pending. Effective revised/cohort applicability is unresolved; this observation does not silently select a policy version.')]}
