"""Observe Symbolic Systems concentration pages and public Google Docs exports.

The document parser accepts Markdown exported through the public document UI.
It is intentionally separate from HTTP refresh: the HTTP response is a JS shell.
"""
import re
from atlas.adapters.national_curriculum_common import content, clean, require_phrases, course
from atlas.adapters.degree_table_observations import Tables
BASE='https://symsys.stanford.edu/undergraduates/concentrations/'
CONFIG={
'ai':('stanford-symsys-ai-concentration','Artificial Intelligence (AI) - Concentration',BASE+'artificial-intelligence-ai-concentration','https://docs.google.com/document/d/1_sseXB7_q-DqWJ0dJp1RX7pIlPUBw5TSowzSU_2f4D8/edit'),
'hai':('stanford-symsys-hai-concentration','Human-Centered Artificial Intelligence (HAI) - Concentration',BASE+'human-centered-artificial-intelligence-hai-concentration','https://docs.google.com/document/d/1EPlLmOy_ilG18TLOG0CseuQT2Pysr3TIIZclFjKnEJE/edit#heading=h.ul46srog64pj')}
HEADINGS={'ai':['Programming','Introduction','Artificial Intelligence Depth','Integrative Requirement','Contingent Electives'], 'hai':['Digital Technology Ethics and Policy','Human Impact','Augmenting Human Capabilities','Intelligence','Integrative Requirement','Contingent Electives']}
def parse(html,route):
 pid,title,url,doc=CONFIG[route];root=content(html,title)
 if not any(clean(h.get_text(' ',strip=True))==title for h in root.find_all('h1')):raise ValueError('Exact concentration heading absent')
 require_phrases(root,['G4','Fall of 2020','3 units'])
 if not any(doc.split('/edit')[0] in a.get('href','') for a in root.find_all('a')):raise ValueError('Reviewed public requirements document link absent')
 t=Tables(pid+'-page',pid+'-page',url,unit='units')
 t.group('Current linked G4 requirements',kind='note',summary='The page identifies this as a Symbolic Systems concentration under the G4 core introduced in Fall 2020. The introduction date of that core is not the concentration launch date. Concentration courses must carry at least three units.')
 return dict(id=pid,title=title,award_level='concentration',program_kind='concentration',requirements=t.rules)
def parse_document(text,route):
 pid,_,_,url=CONFIG[route];title=('Human-Centered ' if route=='hai' else '')+'Artificial Intelligence Concentration'
 if not text.startswith('# '+title+'\n'):raise ValueError('Document title absent')
 for marker in ['Updated September 27, 2024','requires a Stanford login','3 units','5 courses beyond','Junior Year','Core Capstone']:
  if marker not in text:raise ValueError('Reviewed document condition absent: '+marker)
 sections=re.split(r'(?m)^\d+\. \*\*\*(.+?)\*\*\*\.',text)
 headings=sections[1::2]
 if headings!=HEADINGS[route]:raise ValueError('Concentration section structure changed')
 t=Tables(pid+'-doc',pid+'-document',url,unit='units')
 for heading,body in zip(headings,sections[2::2]):
  contingent=heading=='Contingent Electives';integrative=heading=='Integrative Requirement';examples='For example:' in body
  marker='Two courses chosen' if heading=='Artificial Intelligence Depth' else 'One course aimed' if heading in ['Human Impact','Augmenting Human Capabilities','Intelligence'] else 'One of the following' if heading in ['Programming','Digital Technology Ethics and Policy'] else 'Must be completed no earlier than the Junior Year' if integrative else None
  if marker and marker not in body:raise ValueError('Section selection condition changed: '+heading)
  kind='note' if contingent or examples else 'choose_courses'
  count=2 if heading=='Artificial Intelligence Depth' else None if kind=='note' else 1
  summary=('Conditional electives maintain five courses beyond the host core; approved courses from the other concentration areas or an already-satisfied core area also qualify. The displayed list is not the entire eligibility universe.' if contingent else ('One course about AI interaction with humans and social structures or institutions; listed courses are examples, not a finite pool.' if heading=='Human Impact' else 'One course developing human-centered design methods or tools so AI can communicate, collaborate with and augment people; listed courses are examples, not a finite pool.') if examples else 'Choose one listed integrative course or a standard Core Capstone option; no earlier than junior year. The standard routes are recorded from the linked Core Requirements source.' if integrative else 'Choose '+str(count)+' listed course'+('s.' if count==2 else '.'))
  g=t.group(heading,kind=kind,count=count,summary=summary)
  for raw in body.splitlines():
   line=re.sub(r'\\([&.()+\-])',r'\1',raw.strip())
   match=re.match(r'\* ([A-Z][A-Z&]+ \d+[A-Z]*)(?::|\.)\s+(.+)',line)
   if not match:continue
   code,name=match.groups();name=re.split(r'\s+(?:\\?\[|\()',name)[0].rstrip(' *\\')
   c=course(pid,code,name,pid+'-document',url,unit='units',category='ai_ml' if code.startswith('CS ') else 'other');t.courses.setdefault(c['id'],c)
   if '(or CS 181W)' in line:
    alt=course(pid,'CS 181W',None,pid+'-document',url,unit='units');t.courses.setdefault(alt['id'],alt)
    t.group(name+' or CS 181W',parent=g['id'],kind='alternative',ids=[c['id'],alt['id']])
   else:t.group(name,parent=g['id'],ids=[c['id']])
  if 'combination of SYMSYS 176S and OSPGEN 47' in body:
   ids=[]
   for code in ['SYMSYS 176S','OSPGEN 47']:
    c=course(pid,code,None,pid+'-document',url,unit='units');t.courses.setdefault(c['id'],c);ids.append(c['id'])
   t.group('Combined contingent-elective option: both courses',parent=g['id'],ids=ids)
  if integrative:t.group('Standard Core Capstone option',parent=g['id'],kind='note',summary='An approved standard Core Capstone route is an alternative to the displayed concentration-specific course pool; its publicly stated standard routes and approvals are recorded separately from the Core Requirements page.')
  if not any(r['parent_id']==g['id'] for r in t.rules):raise ValueError('Empty observed section')
 t.group('Dated list and restricted approved additions',kind='note',summary='The publicly linked requirements document is updated September 27, 2024. Later approved nominations are kept on a Stanford-login spreadsheet, which was not accessed. The public list cannot establish the full current approved pool.')
 t.group('Unit minimum and host-core overlap',kind='note',summary='Each course must carry at least three units; this is a minimum, not verified exact course credit. If the earlier concentration requirements overlap the core, add approved contingent electives to reach five courses beyond the core.')
 if route=='ai':
  if 'urged to take CS 161' not in text:raise ValueError('Recommendation wording changed')
  t.group('Recommended preparation',kind='note',summary='CS 161 before CS 221 is recommended, not stated here as an unconditional prerequisite.')
 return dict(id=pid,courses=list(t.courses.values()),requirements=t.rules)

POLICY_BASE='https://symsys.stanford.edu/undergraduates/'
CORE=POLICY_BASE+'major-policies-requirements/core-requirements'
POLICIES={
 'major':(POLICY_BASE+'major-policies-requirements','Major Policies & Requirements',[
  ('Concentration versus core grades',['a C- or better for Core courses','a D- or above for Concentration courses','a no-option pass grade','a CR grade'],'Concentration courses require D− or better, while core courses require C− or better. A compulsory no-option pass/S equivalent can qualify; optional credit/no-credit cannot. When a course also serves a core role, do not infer that the lower concentration threshold overrides the core rule.'),
  ('Five courses, units and cross-list equivalence',['five-course concentration','3 units or more','Cross-Listing Policy','same course listed by another department'],'The concentration comprises five courses, normally at least three units each. An approved cross-list registration can meet the same requirement unless explicitly excluded; aliases are not additional compulsory courses.'),
  ('Internal overlap and contingent electives',['at most one required course','Core or Concentration (not both)','Advanced Small Seminar','Capstone - Integrative Requirement','additional approved Contingent Elective'],'Ordinarily a course fills one required course in core or concentration. The seminar/integrative asterisk exceptions permit specified cross-application; if a core-counted course satisfies a concentration area, an approved contingent elective preserves five concentration courses beyond the core.'),
  ('Other major, minor and coterminal overlap',['Secondary Major','allows double counting without restriction','introductory skill requirement for both majors','not to both'],'A secondary major differs from a double/multiple major: the former permits broad overlap, while the latter normally requires separate courses except shared introductory skills. Minor overlap is generally restricted by the minor program. Units cannot count toward both undergraduate and graduate careers; an approved replacement may be needed.'),
  ('Version and graduation course plan',['at least two quarters prior','must complete the full set of requirements','declaration of the major is approved'],'Use requirements active when the declaration is approved or a complete later version, not an arbitrary blend. Submit the final course plan at least two quarters before graduation, verify future offerings and secure approval of unlisted replacements.')]),
 'declare':(POLICY_BASE+'how-declare','How To Declare',[
  ('Host-major declaration',['at least one quarter of coursework','SYMSYS 1 past the Drop deadline','declaration interview','Student Services Officer'],'To declare the host Symbolic Systems major, complete at least one Stanford quarter and take SYMSYS 1 or remain enrolled beyond its drop deadline; file Axess declaration and a course plan, attend an advising-fellow interview and receive the Student Services Officer’s approval. Junior declarations also require a confirmed concentration advisor.')]),
 'advising':(POLICY_BASE+'undergrad-advising','Undergrad Advising',[
  ('Concentration advisor eligibility and deadline',['Autumn Quarter of their junior year','Juniors declaring the major','ongoing instructional appointment','excludes Visiting or short term'],'Select a concentration advisor by junior autumn; juniors declaring the major need one already confirmed. The advisor must hold an ongoing Stanford instructional appointment, not a visiting/short-term role, and have relevant expertise; SymSys affiliation is unnecessary.'),
  ('Advisor confirmation and capstone changes',['cc to the Concentration Adviser','hold is placed on Winter Quarter registration','Any later change in your Capstone plan'],'Confirm the willing advisor through the program office with the advisor copied. Lack of an advisor can hold junior-winter registration. The advisor must approve the capstone and later revisions before the final graduation plan.')]),
 'replacement':(POLICY_BASE+'major-policies-requirements/nominations-and-petitions/replacement-petitions','Replacement Petitions',[
  ('Individual replacement petitions',['Updated April 8, 2026','at the latest prior to the beginning of classes','same level or higher','all of the courses'],'An individual replacement petition must fit a published category and be approved; submit before the relevant quarter where course planning depends on it. Same-area/level and minimum-unit/grade rules remain applicable. Approved combinations require all component courses; they are not interchangeable alternatives.'),
  ('External equivalence versus program elective',['Course-to-Course Equivalency','will not need to request additional approval from SymSys','Program Elective','certification from the Stanford Registrar'],'An external course with approved Stanford course equivalence can qualify without further SymSys approval if it meets major policies. Otherwise a program-elective replacement petition needs evidence of comparable content, rigor, prerequisites and units, plus official transcript and registrar certification; approval is conditional until all steps finish.'),
  ('Online mathematics date restriction',['Effective July 1, 2026','online math courses will no longer be eligible'],'Online external mathematics courses are ineligible for SymSys transfer consideration from July 1, 2026; the explicitly documented earlier accommodation is not a current blanket permission.'),
  ('Other replacement categories',['Instructor-Certified Equivalence','Requirement Versions Transition','Discontinued Course','unqualified grade'],'The public policy also governs certified individual equivalence, version transitions, discontinued courses and grade replacements. A grade-replacement approval requires the original unqualified course on the final transcript; a replacement alone does not erase that condition. Graduate-only core waivers are outside this undergraduate concentration scope.')]),
 'transfer':('https://studentservices.stanford.edu/my-academics/earn-my-degree/undergraduate-degree-progress/test-transfer-credit/undergraduate','Undergraduate Transfer Credit',[
  ('Transfer credit grade, units and duplicates',['“C-” or better','maximum of 45 quarter units','90 quarter units for transfer students','whole units rounded down','duplicating transfer credit removed'],'External work needs accredited college-level eligibility and C− or better; a pass must be documented equivalent. The university caps combined external/test credit at 45 quarter units, or 90 for transfer entrants. The registrar converts/rounds units under its published formula; later duplicate Stanford enrollment removes the matching transfer credit. These are university limits, not invented concentration-specific caps.'),
  ('Transfer evaluation deadlines',['first three quarters of enrollment','one year from the time','official transcript','Program Elective Credit is at the discretion'],'Course-to-course requests for prematriculation work belong in the first three quarters; postmatriculation requests generally have a one-year window. Final approval requires a directly submitted official transcript. Department discretion governs program-elective timing, and graduating students must meet the registrar’s final-quarter deadlines.')]),
 'nominations':(POLICY_BASE+'major-policies-requirements/nominations-and-petitions/course-nominations','Course Nominations',[
  ('Nomination decisions remain access-restricted',['Course Nominations spreadsheet (requires a Stanford login)','nominations and the decisions','open-ended'],'The public nomination policy confirms that decisions are maintained in a Stanford-login sheet. That sheet was not accessed. Open example-based areas may admit approved additions, but a nomination alone is not course approval.')])}
def parse_policy(html,route,key):
 pid=CONFIG[route][0];url,heading,specs=POLICIES[key];root=content(html,heading)
 t=Tables(pid+'-'+key,pid+'-'+key,url,unit='units')
 for title,markers,summary in specs:
  require_phrases(root,markers);t.group(title,kind='note',summary=summary)
 return dict(id=pid,requirements=t.rules)
def parse_core(html,route):
 pid=CONFIG[route][0];root=content(html,'Core Requirements')
 require_phrases(root,['Updated April 2, 2026','end of first week of Winter Quarter, Junior Year','3 or more units each','final approval by the Symbolic Systems Program office','Units must be applied to a student','must be completed no earlier than the Junior Year'])
 h=next((h for h in root.find_all('h4') if clean(h.get_text(' ',strip=True))=='Integrative Requirement*'),None)
 if h is None:raise ValueError('Integrative requirement section absent')
 listing=h.find_next('ul');items=listing.find_all('li',recursive=False) if listing else []
 if len(items)!=4:raise ValueError('Standard integrative option structure changed')
 phrases=['continuation of the course taken for the Practicum','195-series','Supervised research with a faculty member','Concentration-Specific Integrative Course']
 for li,phrase in zip(items,phrases):require_phrases(li,[phrase])
 t=Tables(pid+'-core',pid+'-core',CORE,unit='units')
 t.group('Capstone approval and integrative timing',kind='note',summary='The concentration advisor and SymSys office approve the capstone plan by the end of the first week of junior winter (eighth undergraduate quarter). Each component carries at least three units. The integrative requirement is no earlier than junior year and its units apply to the concentration; the practicum remains a separate host-core component.')
 summaries=['Eligible standard route: continuation of SYMSYS 190 from the honors practicum; this is not an unrelated first honors tutorial.','Eligible standard route: a SYMSYS 195-series project course or CS 177 meeting the stated integrative project criteria. The series is an open course-number criterion, not an invented single course.','Eligible standard route: faculty-supervised, approved symbolic-systems research registered through SYMSYS 196 or one of the displayed departmental research courses. The research/approval condition remains required.']
 for index,li in enumerate(items[:3]):
  ids=[]
  for link in li.find_all('a'):
   code=clean(link.get_text(' ',strip=True))
   if not re.fullmatch(r'[A-Z]+ \d+[A-Z]*',code):continue
   tail=str(link.next_sibling or '').lstrip(': ').strip();name=re.split(r'\s*\(',tail)[0].rstrip(',; ') or None
   c=course(pid,code,name,pid+'-core',link.get('href') or CORE,unit='units');t.courses.setdefault(c['id'],c);ids.append(c['id'])
  if not ids:raise ValueError('Standard integrative course identities absent')
  t.group('Standard integrative option '+str(index+1),kind='note',ids=ids,summary=summaries[index])
 t.group('Alternative to concentration-specific integrative course',kind='note',summary='The three standard routes are alternatives to the concentration-specific integrative course pool, not extra courses on top of it. The separate public presentation/core practicum requirements belong to the host major; they are not recast as extra concentration electives.')
 return dict(id=pid,courses=list(t.courses.values()),requirements=t.rules)
