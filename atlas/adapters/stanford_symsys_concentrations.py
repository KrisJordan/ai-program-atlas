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
  summary=('Conditional electives maintain five courses beyond the host core; approved courses from the other concentration areas or an already-satisfied core area also qualify. The displayed list is not the entire eligibility universe.' if contingent else ('One course about AI interaction with humans and social structures or institutions; listed courses are examples, not a finite pool.' if heading=='Human Impact' else 'One course developing human-centered design methods or tools so AI can communicate, collaborate with and augment people; listed courses are examples, not a finite pool.') if examples else 'Choose one listed integrative course or a standard Core Capstone option; no earlier than junior year. The standard options require separate review.' if integrative else 'Choose '+str(count)+' listed course'+('s.' if count==2 else '.'))
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
  if integrative:t.group('Standard Core Capstone option',parent=g['id'],kind='note',summary='An approved standard Core Capstone route is an alternative to the displayed concentration-specific course pool; its details have not been mapped.')
  if not any(r['parent_id']==g['id'] for r in t.rules):raise ValueError('Empty observed section')
 t.group('Dated list and restricted approved additions',kind='note',summary='The publicly linked requirements document is updated September 27, 2024. Later approved nominations are kept on a Stanford-login spreadsheet, which was not accessed. The public list cannot establish the full current approved pool.')
 t.group('Unit minimum and host-core overlap',kind='note',summary='Each course must carry at least three units; this is a minimum, not verified exact course credit. If the earlier concentration requirements overlap the core, add approved contingent electives to reach five courses beyond the core.')
 if route=='ai':
  if 'urged to take CS 161' not in text:raise ValueError('Recommendation wording changed')
  t.group('Recommended preparation',kind='note',summary='CS 161 before CS 221 is recommended, not stated here as an unconditional prerequisite.')
 return dict(id=pid,courses=list(t.courses.values()),requirements=t.rules)
