"""Parse the Responsible AI minor section only, including whole foundation options."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean,content,course,rule,policy
PROGRAM_ID='santa-clara-responsible-ai-minor'
SOURCES=('https://www.scu.edu/bulletin/undergraduate/chapter-5-school-of-engineering/computer-science-and-engineering.html',)
SOURCE_ID=PROGRAM_ID+'-identity'

def parse(html):
    root=content(html,'Minor in Responsible Artificial Intelligence')
    heading=next((n for n in root.find_all(['h2','h3']) if clean(n.get_text(' ',strip=True))=='Requirements for the Minor in Responsible Artificial Intelligence'),None)
    if not heading:raise ValueError('Responsible AI requirements heading missing')
    nodes=[]
    for node in heading.next_siblings:
        if getattr(node,'name',None) in ('h1','h2'):break
        nodes.append(str(node))
    section=BeautifulSoup(''.join(nodes),'html.parser');courses={};groups=[];starred=[]
    def item(text):
        text=clean(text);star=text.startswith('*');text=text.lstrip('*')
        units=re.search(r'\((\d+) units\)',text);credits=int(units[1]) if units else None
        text=re.sub(r'\(\d+ units\)\.?','',text).strip()
        # Explicit math alternative in foundation A is handled by its parent slot.
        if text.startswith('AMATH 108 (or MATH 122)'):
            title=text.split(').',1)[1].strip(' .');ids=[]
            for code in ('AMATH 108','MATH 122'):
                c=course('scu',code,title,SOURCE_ID,SOURCES[0],credits=credits,unit='units',category='mathematics');courses[c['id']]=c;ids.append(c['id'])
            return ids
        text=text.replace('CSEN 19 (cross-listed as MATH 51)','CSEN 19/MATH 51')
        m=re.fullmatch(r'([A-Z]+ \d+[A-Za-z]?(?:(?:&\d+[A-Za-z]?)|(?:/\d+)|(?:/[A-Z]+ \d+))?)\s*[.:]\s*(.+)',text)
        if not m:raise ValueError('Unrecognized course item: '+text)
        code,title=m.groups();title=title.strip(' .')
        cat='foundations' if code.startswith(('CSEN 1','CSCI 10','CSCI 60','CSCI 61','CSCI 62','OMIS 30','OMIS 114')) else 'human_context' if code.startswith(('PHIL','COMM','ENGL','HIST','FREN','SOCI','ENGR 19')) else 'applications'
        if code in ('CSEN 166','OMIS 116','CSCI 183'):cat='ai_ml'
        c=course('scu',code,title,SOURCE_ID,SOURCES[0],credits=credits,unit='units' if credits else 'unknown',category=cat);courses[c['id']]=c
        if star:starred.append(c['id'])
        return [c['id']]
    lists=section.find_all('ul')
    if len(lists)!=5:raise ValueError('Expected five requirement lists')
    groups.append(rule('scu-foundation','Computing foundation: choose one complete option',SOURCE_ID,kind='alternative',summary='Choose one whole option A,B,orC; take every slot within that option. CSEN lecture/lab bundles carry their combined published units.'))
    for li in lists[0].find_all('li',recursive=False):
        text=clean(li.get_text(' ',strip=True));m=re.match(r'Option ([ABC]): (.+)',text)
        if not m:raise ValueError('Foundation option label missing')
        parent='scu-option-'+m[1].lower();groups.append(rule(parent,'Foundation option '+m[1],SOURCE_ID,parent='scu-foundation'))
        for i,part in enumerate(m[2].split(';')):
            ids=item(part)
            groups.append(rule(parent+'-'+str(i),'Foundation course slot',SOURCE_ID,ids,parent=parent,kind='choose_courses' if len(ids)>1 else 'all',count=1 if len(ids)>1 else None))
    for idx,gid,title,kind,count in [(1,'scu-tech-ethics','Technology ethics','choose_courses',1),(2,'scu-ai-ethics','AI ethics','all',None),(3,'scu-ai-tech','AI technology','choose_courses',1),(4,'scu-electives','Electives','choose_credits',None)]:
        ids=[]
        for li in lists[idx].find_all('li',recursive=False):
            texts=re.split(r'\s+or\s+(?=[A-Z]+ \d)',clean(li.get_text(' ',strip=True))) if idx==3 else [clean(li.get_text(' ',strip=True))]
            for text in texts:ids+=item(text)
        groups.append(rule(gid,title,SOURCE_ID,ids,kind=kind,count=count,credits=4 if idx==4 else None,unit='units' if idx==4 else 'unknown',summary='At least4units from the listed pool. Individual elective credits require course-page review.' if idx==4 else title))
    groups.append(policy(section,'All undergraduate students are eligible','scu-eligibility','Eligibility','All undergraduate students are eligible; check and satisfy individual course prerequisites before scheduling or registering.',SOURCE_ID))
    groups.append(policy(section,'cannot be used to satisfy university core requirements','scu-core-overlap','University core exclusion','Asterisk-marked minor courses cannot also satisfy university core requirements.',SOURCE_ID));groups[-1]['course_ids']=starred
    return dict(id=PROGRAM_ID,title='Responsible Artificial Intelligence',award_level='minor',program_kind='minor',courses=list(courses.values()),requirements=groups)
