"""Parse the exact Tepper AI concentration and its local catalog policies."""
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
PROGRAM_ID='cmu-ai-business-concentration'
SOURCES=('https://coursecatalog.web.cmu.edu/schools-colleges/tepper/undergraduatebusinessadministrationprogram/business-administration-bs/',)
def clean(node): return re.sub(r'\s+', ' ', node.get_text(' ',strip=True)).strip()
def parse(html):
    s=BeautifulSoup(html,'html.parser')
    for n in s.select('nav,header,footer'): n.decompose()
    h=s.select_one('main h1.page-title')
    panel=s.find(id='concentrationstextcontainer')
    if not h or clean(h)!='Business Administration, B.S.' or not panel: raise ValueError('Expected undergraduate business catalog')
    heading=next((x for x in panel.find_all('h3') if clean(x)=='AI and Business'),None)
    policy=clean(panel)
    minimum=re.search(r'Business concentrations require at least (\d+) units beyond the Business Core',policy)
    if not heading or not minimum or 'not allowed to double count' not in policy or 'including the minor requirement' not in policy or 'prerequisites from courses outside the concentration' not in policy or 'consult with their academic advisor' not in policy: raise ValueError('Concentration identity or local policy missing')
    sid=PROGRAM_ID+'-catalog'; courses=[]; requirements=[]
    def rule(suffix,title,kind='note',count=None,credits=None,ids=None,summary=''):
        requirements.append(dict(id=PROGRAM_ID+'-'+suffix,parent_id=None,title=title,kind=kind,count=count,credits=credits,credit_unit='units',category='applications',source_id=sid,source_text=None,summary=summary,course_ids=ids or []))
    rule('minimum','Concentration minimum',credits=int(minimum[1]),summary='Minimum units beyond the Business Core; the host BS has additional requirements.')
    rule('overlap','No double counting',summary='Concentration courses cannot also fulfill other Business Administration degree requirements, including the minor.')
    rule('prerequisites','Prerequisite and advising context',summary='Concentration courses may have prerequisites outside this inventory; consult the academic advisor when selecting a concentration.')
    group=0
    for node in heading.next_siblings:
        if getattr(node,'name',None)=='h3': break
        if getattr(node,'name',None) not in {'p','hr',None}: raise ValueError('Unexpected concentration structure')
        if getattr(node,'name',None)!='p': continue
        spans=node.select('span.sc_courseinline'); text=clean(node)
        if not spans: raise ValueError('Unmodeled concentration prose')
        group+=1
        if text.startswith('Required:'): count=None;kind='all'
        else:
            match=re.match(r'Choose (\d+) course(?:s)?:',text)
            if not match: raise ValueError('Unrecognized selection instruction')
            count=int(match[1]);kind='choose_courses'
            if count>len(spans): raise ValueError('Choice exceeds pool')
        ids=[]
        for span in spans:
            a=span.find('a',class_='code')
            if not a or not re.fullmatch(r'\d{2}-\d{3}',clean(a)): raise ValueError('Unrecognized course code')
            code=clean(a); name=clean(span)[len(code):].strip();cid=PROGRAM_ID+'-'+code
            if not name: raise ValueError('Course name missing')
            ids.append(cid)
            courses.append(dict(id=cid,code=code,name=name,description=None,prerequisites=None,credits=None,credit_unit='units',category='applications',source_id=sid,url=urljoin(SOURCES[0],a['href']),public_site=None,syllabus=None))
        rule('group-'+str(group),'Required course' if kind=='all' else 'Elective group '+str(group-1),kind,count,ids=ids,summary='Complete every listed course.' if kind=='all' else 'Select within this group independently of the other elective groups.')
    if group!=4 or len({c['id'] for c in courses})!=len(courses): raise ValueError('Changed group structure or duplicate course requires review')
    return dict(id=PROGRAM_ID,title='AI and Business',program_kind='concentration',award_level='concentration',curriculum_status='partial',courses=courses,requirements=requirements)

from importlib import import_module
policies=import_module('atlas.adapters.cmu-ai-business-concentration.policies')

def parse_catalog_with_context(html):
    result=parse(html)
    result['requirements']+=policies.parse_host_context(html)['requirements']
    return result

SOURCE_PARSERS={SOURCES[0]:parse_catalog_with_context,**policies.SOURCE_PARSERS}
SOURCES=(*SOURCES,*policies.SOURCE_PARSERS)
