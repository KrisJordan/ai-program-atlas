"""Observe the formal AI Thread and finite paired-thread context; no invented BS awards."""
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
PROGRAM_ID='georgia-tech-ai-thread'
CATALOG='https://catalog.gatech.edu/programs/computer-science-bs/'
THREAD='https://www.cc.gatech.edu/academics/threads/intelligence'
SOURCES=(CATALOG,THREAD)
def clean(node): return re.sub(r'\s+',' ',node.get_text(' ',strip=True)).strip()
def rule(suffix,title,source,kind='note',parent=None,count=None,credits=None,ids=None,summary=''):
    return dict(id=PROGRAM_ID+'-'+suffix,parent_id=parent,title=title,kind=kind,count=count,credits=credits,credit_unit='unknown',category='ai_ml',source_id=PROGRAM_ID+'-'+source,source_text=None,summary=summary,course_ids=ids or [])
def parse(html):
    s=BeautifulSoup(html,'html.parser')
    for n in s.select('nav,header,footer'):n.decompose()
    h=s.find('h1');overview=s.find(id='textcontainer');panel=s.find(id='threadstextcontainer')
    if not h or clean(h)!='Bachelor of Science in Computer Science' or not overview or not panel:raise ValueError('Expected BSCS catalog')
    text=clean(overview)
    if 'Each student selects two Threads' not in text:raise ValueError('Paired-thread rule changed')
    ai=next((h for h in panel.find_all('h3') if clean(h)=='Artificial Intelligence'),None)
    if not ai:raise ValueError('Current formal AI title missing')
    links=[]
    for node in ai.next_siblings:
        if getattr(node,'name',None)=='h3':break
        if getattr(node,'name',None)=='ul':links.extend(node.find_all('a'))
    if len(links)!=8 or any('Artificial Intelligence' not in clean(a) or not a.get('href','').startswith('/programs/') for a in links):raise ValueError('Paired-thread directory changed')
    root=rule('pairing','Pair AI with a second thread','catalog','alternative',summary='Every BSCS student selects two threads. Choose one of these eight catalog pairings with AI; each pairing has additional curriculum requirements.')
    req=[root]
    for a in links:
        name=clean(a);slug=re.sub('[^a-z0-9]+','-',name.lower()).strip('-')
        req.append(rule('pair-'+slug,name,'catalog',parent=root['id'],summary='Official paired curriculum: '+urljoin(CATALOG,a['href'])+' . Its full course requirements remain unexpanded.'))
    for phrase,label,summary in [
        ('All required CS courses','Required CS grades','Required CS courses need a grade of C or better.'),
        ('All courses listed as required for a Thread','Thread grades','Required thread courses, including non-CS courses, need a grade of C or better.')]:
        p=next((x for x in overview.find_all('li') if phrase in clean(x)),None)
        if not p or 'C or better' not in clean(p):raise ValueError('Thread grading policy changed')
        req.append(rule(re.sub('[^a-z]+','-',label.lower()),label,'catalog',summary=summary))
    return dict(id=PROGRAM_ID,title='Artificial Intelligence',award_level='concentration',program_kind='concentration',curriculum_status='partial',requirements=req)

def parse_thread(html):
    s=BeautifulSoup(html,'html.parser')
    for n in s.select('nav,header,footer'):n.decompose()
    if not any(clean(h)=='Artificial Intelligence' for h in s.find_all('h1')):raise ValueError('Exact AI thread heading missing')
    start=next((x for x in s.find_all('h4') if clean(x)=='Required Courses:'),None)
    if not start:raise ValueError('Required-course block missing')
    req=[];courses={};group=None
    for node in [start,*start.next_siblings]:
        tag=getattr(node,'name',None)
        if tag=='h4' and node is not start:break
        if tag in {'h4','h6'}:
            title=clean(node)
            if node is start:group=rule('core','Required thread courses','thread','all')
            else:
                m=re.fullmatch(r'Pick (\d+) of (.+)',title)
                if not m:raise ValueError('Changed thread selection heading')
                group=rule(re.sub('[^a-z0-9]+','-',m[2].lower()),m[2],'thread','choose_courses',count=int(m[1]))
            req.append(group)
        elif tag=='ul':
            for li in node.find_all('li',recursive=False):
                text=clean(li)
                m=re.fullmatch(r'((?:CS|PSYC)\s+\d{4})(?:\s+or\s+((?:CS|PSYC)?\s*\d{4}))?\s+(.+),\s*(\d+)(?:\s+\(social science elective\))?',text)
                if not m or not group:raise ValueError('Unrecognized required course row: '+text)
                codes=[m[1]]
                if m[2]:codes.append(m[2] if re.match('[A-Z]',m[2]) else m[1].split()[0]+' '+m[2])
                ids=[]
                for code in codes:
                    code=re.sub(r'\s+',' ',code.strip());cid=PROGRAM_ID+'-'+code.lower().replace(' ','-');ids.append(cid)
                    courses[cid]=dict(id=cid,code=code,name=m[3],description=None,prerequisites=None,credits=int(m[4]),credit_unit='unknown',category=('human_context' if code.startswith('PSYC') else 'systems' if code=='CS 2110' else 'ai_ml' if code in {'CS 3600','CS 3630','CS 3790','CS 4476','CS 4635','CS 4641','CS 4644','CS 4646','CS 4649','CS 4650','CS 4731'} else 'foundations'),source_id=PROGRAM_ID+'-thread',url=THREAD,public_site=None,syllabus=None)
                if group['kind']=='choose_courses':group['course_ids'].extend(ids)
                else:
                    item=rule('course-'+codes[0].lower().replace(' ','-'), ' or '.join(codes),'thread','alternative' if len(codes)>1 else 'all',parent=group['id'],ids=ids,summary='Choose one listed alternative.' if len(codes)>1 else 'Required thread course.')
                    req.append(item)
    if len([x for x in req if x['kind']=='choose_courses'])!=2 or not courses:raise ValueError('Missing required thread groups')
    req.append(rule('department-scope','Department-list boundary','thread',summary='This department list does not replace the paired catalog curriculum. Department free-elective suggestions are not expanded; credit amounts are source-stated but the unit is unnormalized.'))
    return dict(id=PROGRAM_ID,curriculum_status='partial',courses=list(courses.values()),requirements=req)
SOURCE_PARSERS={THREAD:parse_thread}
