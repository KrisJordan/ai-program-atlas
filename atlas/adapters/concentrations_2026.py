"""Source-specific concentration observations; curated review is always separate."""
import hashlib
import re
from bs4 import BeautifulSoup
from atlas.adapters.reviewed_minors_2026 import clean, slug
from atlas.adapters.vt_duke_minors import rule


def observation(pid, text, courses, requirements):
    return dict(id=pid, program_kind='concentration', award_level='concentration', curriculum_status='partial', courses=courses, requirements=requirements, observed_policy_digest=hashlib.sha256(text.encode()).hexdigest())


def course(key, code, name, source, url, category='other'):
    return dict(id=key,code=code,name=name,description=None,prerequisites=None,credits=None,credit_unit='unknown',category=category,source_id=source,url=url,public_site=None,syllabus=None)


def parse_emory(html,pid,source,url):
    soup=BeautifulSoup(html,'html.parser');body=soup.find('main') or soup
    heading=body.find('h1');table=body.find('table')
    if not heading or 'CS BS, AI Concentration' not in heading.get_text() or not table:raise ValueError('Emory concentration heading/table missing')
    text=clean(body.get_text(' ',strip=True));courses={};req=[rule('emory-ai','CS BS AI concentration requirements',source,kind='all'),rule('emory-ai-core','Required courses',source,kind='all',parent='emory-ai')];choices=0
    def add(code,name):
        code=re.sub('Math','MATH',code);key='emory-'+slug(code)
        cat='mathematics' if code.startswith('MATH') else 'ai_ml' if re.search(r'Intelligence|Learning|Neural|Vision|Linguistics|Mining',name) else 'systems' if re.search(r'Systems|Architecture',name) else 'foundations'
        courses[key]=course(key,code,name,source,url,cat);return key
    for row in table.find_all('tr'):
        cells=row.find_all('td',recursive=False)
        if len(cells)!=2:continue
        label=clean(cells[0].get_text(' ',strip=True));value=clean(cells[1].get_text(' ',strip=True))
        if label=='Requirement':continue
        if re.fullmatch(r'(?:Math|CS)\s+\d+[A-Z]*',label):
            key=add(label,value);req[1]['course_ids'].append(key)
        elif 'chosen from' in label:
            count=re.search(r'\((\d+)\)',label)
            if not count:raise ValueError('Elective selection count missing')
            choices+=1;key='emory-ai-choice-'+str(choices)
            ids=[]
            for li in cells[1].find_all(['li','p']):
                match=re.match(r'(Math|CS)\s+(\d+[A-Z]*)\s*:\s*(.+)',clean(li.get_text(' ',strip=True)))
                if not match:
                    if re.match(r'^(Math|CS)\s+\d',clean(li.get_text(' ',strip=True))):raise ValueError('Elective course row changed')
                    continue
                ids.append(add(match[1]+' '+match[2],match[3]))
            level=re.search(r'Any (\d+)-level CS classroom course not taken above',value)
            req.append(rule(key,'Elective selection '+str(choices),source,kind='alternative' if level and ids else 'choose_courses',parent='emory-ai',number=int(count[1]),ids=[] if level else ids,summary=value))
            if level:
                req.append(rule(key+'-open',level[1]+'-level CS classroom elective',source,parent=key,summary='Choose '+count[1]+' CS classroom course at the '+level[1]+' level not already used above.'))
                if ids:req.append(rule(key+'-math','Mathematics substitution',source,kind='choose_courses',parent=key,number=int(count[1]),ids=ids))
        else:raise ValueError('Unrecognized Emory requirement row: '+label)
    if not req[1]['course_ids'] or choices!=3:raise ValueError('Emory requirement structure changed')
    # These source paragraphs carry policy changes into the candidate diff.
    for i,p in enumerate(body.find_all(['p','li'])):
        value=clean(p.get_text(' ',strip=True))
        if any(x in value for x in ['minimum GPA','letter grade','better of the grades','cannot be combined','prerequisite courses before','CS 485 topics','CS 323:']):
            req.append(rule('emory-ai-policy-'+str(i),'Program completion policy',source,parent='emory-ai',summary=value))
    if not any('minimum GPA' in r['summary'] for r in req):raise ValueError('Emory GPA policy missing')
    return observation(pid,text,list(courses.values()),req)


EMORY_FAQ_QUESTIONS=[
 'When can I declare a major/minor with CS?',
 'Are there any special requirements for declaring a major/minor with CS?',
 'How do I declare a major/minor with CS?',
 'Can I enroll in a course if I have not completed the prerequisite?',
 'Can I use an S grade to satisfy a prerequisite requirement?',
 'Can I use research credits (CS 497R) to replace a CS major elective?',
 'Can I take a graduate course and count it towards my major?',
 'I am also completing a major/minor with another department; how many courses can I double count between my two programs?',
]

def parse_emory_faq(html,pid,source,url):
    soup=BeautifulSoup(html,'html.parser');req=[]
    for i,question in enumerate(EMORY_FAQ_QUESTIONS):
        button=next((b for b in soup.find_all('button') if clean(b.get_text(' ',strip=True))==question),None)
        answer=soup.find(id=button.get('aria-controls')) if button else None
        if not answer:raise ValueError('Emory policy question missing: '+question)
        req.append(rule('emory-ai-faq-'+str(i),question,source,summary=clean(answer.get_text(' ',strip=True))))
    return observation(pid,' '.join(r['summary'] for r in req),[],req)


def parse_bc(html,pid,source,url):
    soup=BeautifulSoup(html,'html.parser')
    button=next((b for b in soup.find_all('button') if clean(b.get_text())=='Artificial Intelligence Concentration'),None)
    section=soup.find(id=button.get('data-target','').lstrip('#')) if button else None
    if not section:raise ValueError('BC AI concentration section missing')
    text=clean(section.get_text(' ',strip=True));total=re.search(r'take (\d+) courses',text)
    if not total:raise ValueError('BC total course rule missing')
    req=[rule('bc-ai','AI concentration local requirements',source,kind='all',number=int(total[1]))]
    listing=section.find('ul')
    if not listing:raise ValueError('BC requirement list missing')
    words={'One':1,'An':1,'Two':2,'Three':3,'Four':4}
    for i,li in enumerate(listing.find_all('li',recursive=False)):
        value=clean(li.get_text(' ',strip=True));number=next((n for w,n in words.items() if value.startswith(w+' ')),None)
        credits=re.search(r'\((\d+) credits',value)
        req.append(rule('bc-ai-group-'+str(i),['AI core','AI applications / embodied AI','AI ethics','Senior capstone'][i] if i<4 else 'Additional requirement',source,kind='note',parent='bc-ai',number=number,credits=int(credits[1]) if credits else None,summary=value))
    for i,p in enumerate(section.find_all('p')):
        value=clean(p.get_text(' ',strip=True))
        if any(t in value for t in ['double counting','additional preparation','consult']):req.append(rule('bc-ai-policy-'+str(i),'Concentration planning and overlap',source,parent='bc-ai',summary=value))
    return observation(pid,text,[],req)
