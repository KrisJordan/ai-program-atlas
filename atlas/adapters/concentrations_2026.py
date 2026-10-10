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


def parse_bc_courses(raw,pid,source,url):
    import json
    data=json.loads(raw)
    if data.get('msg')!='OK' or not isinstance(data.get('payload'),list):raise ValueError('BC course feed schema changed')
    rows={}
    # Exact core title establishes membership; do not infer the approved cluster from titles.
    for item in data['payload']:
        if item.get('dept_code')!='CSCI' or item.get('title') not in ['Machine Learning','Deep Learning']:continue
        code='CSCI '+str(item['crs_number']);key='bc-'+slug(code)
        c=course(key,code,item['title'],source,url,'ai_ml')
        c.update(description=item.get('crs_desc') or None,prerequisites=item.get('prereq') or None,credits=float(item['credits']) if item.get('credits') and re.fullmatch(r'\d+(?:\.\d+)?',item['credits']) else None)
        rows[key]=c
    if not rows:raise ValueError('No named concentration core found in BC course feed')
    return observation(pid,json.dumps(list(rows.values()),sort_keys=True),list(rows.values()),[])


DUKE_CODE=re.compile(r'\b(COMPSCI|MATH|STA|ECE|ECON|LINGUIST)\s*(\d+[A-Z]*)\b')


def parse_duke_concentration(html,pid,source,url):
    soup=BeautifulSoup(html,'html.parser');heading=soup.find('h1')
    if not heading or 'AI and Machine Learning' not in heading.get_text():raise ValueError('Duke AI/ML concentration heading missing')
    sections={i:soup.find(id=f'collapse-accordion-1385-{i}') for i in range(1,9)}
    if any(x is None for x in sections.values()):raise ValueError('Duke required section missing')
    courses={};req=[rule('duke-ai-concentration','CS BS AI/ML concentration: current requirements',source,kind='all')]
    def add(code,name=None,category='other',topic=False):
        key='duke-'+slug(code)+(('-'+slug(name)) if topic and name else '')
        if key not in courses:courses[key]=course(key,code,name,source,url,category)
        elif name and not courses[key]['name']:courses[key]['name']=name
        return key
    def ids(text,category='other',names=False):
        result=[]
        for option in re.split(r'\s+OR\s+',text):
            option=re.split(r',?\s*renumbered from',option)[0]
            matches=list(DUKE_CODE.finditer(option))
            if not matches:continue
            if '(cross ' in option or re.search(r'\d+[A-Z]*\s*/\s*(?:MATH|STA)',option):
                code=' / '.join(m[1]+' '+m[2] for m in matches)
                name=option[matches[0].end():].split('(cross ')[0].strip(' -*') if names else None
                if re.match(r'^/(STA|MATH)',name or ''):name=option[matches[-1].end():].strip(' -')
                result.append(add(code,name or None,category))
            else:
                for m in matches:
                    name=option[m.end():].strip(' -') if names and len(matches)==1 else None
                    result.append(add(m[1]+' '+m[2],name or None,category))
        return list(dict.fromkeys(result))
    def group(i,title,kind='all',number=None):
        text=clean(sections[i].get_text(' ',strip=True));units=re.search(r'\((\d+) units?\)',text)
        if not units:raise ValueError('Duke group unit total missing')
        key='duke-ai-group-'+str(i)
        req.append(rule(key,title,source,kind=kind,parent='duke-ai-concentration',number=number,credits=int(units[1]),unit='units'))
        return key
    def choice(key,parent,text,category='other'):
        selected=ids(text,category);req.append(rule(key,text,source,kind='choose_courses' if len(selected)>1 else 'all',parent=parent,number=1 if len(selected)>1 else None,ids=selected))
    g=group(1,'Prerequisite requirements')
    lis=sections[1].find('ol').find_all('li',recursive=False)
    if len(lis)!=3:raise ValueError('Duke prerequisite structure changed')
    choice('duke-ai-intro',g,clean(lis[0].get_text(' ',strip=True)),'foundations')
    req[-1]['summary']='Published introductory alternatives or equivalent. Successful completion of COMPSCI 201 waives COMPSCI 101L.'
    calc=clean(lis[1].get_text(' ',strip=True));req.append(rule('duke-ai-calculus','Calculus alternatives',source,kind='alternative',parent=g))
    for j,part in enumerate(re.split(r'\s+OR\s+',calc)):
        req.append(rule('duke-ai-calculus-'+str(j),'Calculus pair '+str(j+1),source,kind='all',parent='duke-ai-calculus',ids=ids(part,'mathematics')))
    req.append(rule('duke-ai-calculus-equivalent','Other calculus equivalents',source,parent='duke-ai-calculus',summary='The source permits other equivalents; confirm acceptance with the department.'))
    stats=lis[2].find('ul')
    if not stats:raise ValueError('Duke statistics alternatives missing')
    req.append(rule('duke-ai-statistics','Mathematics/statistics: choose one',source,kind='choose_courses',parent=g,number=1,ids=[k for li in stats.find_all('li',recursive=False) for k in ids(clean(li.get_text(' ',strip=True)),'mathematics')]))
    g=group(2,'Core requirements');lis=sections[2].find('ol').find_all('li',recursive=False)
    if len(lis)!=5:raise ValueError('Duke core structure changed')
    for j,li in enumerate(lis):
        text=clean(li.get_text(' ',strip=True));nested=li.find('ul');key='duke-ai-core-'+str(j)
        if nested:
            req.append(rule(key,'AI mathematics core or two-course substitute',source,kind='alternative',parent=g))
            direct=text.split(' OR ')[0];req.append(rule(key+'-direct','Direct core course',source,kind='all',parent=key,ids=ids(direct,'mathematics')))
            req.append(rule(key+'-pair','Two-course mathematics substitute',source,kind='all',parent=key))
            for n,child in enumerate(nested.find_all('li',recursive=False)):choice(key+'-math-'+str(n),key+'-pair',clean(child.get_text(' ',strip=True)),'mathematics')
        else:choice(key,g,text,'systems' if j==2 else 'foundations')
    for i,title,cat in [(3,'Systems core','systems'),(4,'Artificial intelligence core','ai_ml'),(5,'Machine learning core','ai_ml')]:
        g=group(i,title,'choose_courses',1)
        selected=[k for li in sections[i].find('ul').find_all('li',recursive=False) for k in ids(clean(li.get_text(' ',strip=True)),cat)]
        req[-1]['course_ids']=list(dict.fromkeys(selected))
    g=group(6,'Concentration electives','choose_courses',3);selected=list(next(r for r in req if r['id']=='duke-ai-group-5')['course_ids'])
    heading_text=clean(sections[6].get_text(' ',strip=True));count=re.search(r'(\d+) COMPSCI courses',heading_text)
    if not count:raise ValueError('Duke elective course count missing')
    req[-1]['count']=int(count[1]);req[-1]['summary']='200-level or higher with QC code; machine-learning core list and the public elective list are eligible sources. The page conflicts on whether two or all three electives must be COMPSCI. Reuse of a course for multiple requirements is not permitted.'
    for li in sections[6].find_all('li'):
        if li.find_parent('li'):continue
        text=clean(li.get_text(' ',strip=True));nested=li.find('ul')
        if nested:
            match=DUKE_CODE.search(text)
            if not match:raise ValueError('Special topic course code missing')
            for topic in nested.find_all('li',recursive=False):
                name=clean(topic.get_text(' ',strip=True));selected.append(add(match[1]+' '+match[2],name,'ai_ml',True))
        elif 'independent study' in text:
            req.append(rule('duke-ai-independent','Conditional independent study option',source,parent=g,summary='At most one independent study with substantial AI/ML emphasis in COMPSCI, MATH, STA, ECE, or a related area approved by the DUS may count.'))
        else:selected.extend(ids(text,'ai_ml',True))
    # ECE480 is explicitly excluded for this BS; historical numbers are not separate options.
    excluded=[k for k in selected if courses[k]['code']=='ECE 480']
    selected=[k for k in selected if k not in excluded]
    next(r for r in req if r['id']==g)['course_ids']=list(dict.fromkeys(selected))
    req.append(rule('duke-ai-elective-restrictions','Offering, renumbering and BS eligibility restrictions',source,parent=g,summary='Only STA 332 / MATH 343, not ECE 480, satisfies the BS option. STA 332 was renumbered from STA 432 in Fall 2025; COMPSCI 575 from COMPSCI 572 in Fall 2026. Topics may not be offered regularly; ECON 490 Causality and ML is the Spring 2026 offering. The full elective list is available only in student Stellic.'))
    for k in excluded:del courses[k]
    req.append(rule('duke-ai-declaration','Concentration declaration',source,parent='duke-ai-concentration',summary='Use the Academic Plan Change form to add, drop or change the concentration.'))
    req.append(rule('duke-ai-substitutions','Substitutions require review',source,parent='duke-ai-concentration',summary='Eligibility depends on the academic plan. Consult the DUS and receive approval before counting a substitution; see the department substitution guide.'))
    text=clean((soup.find('main') or soup).get_text(' ',strip=True))
    if 'Fall 2026' not in text or 'Stellic' not in text:raise ValueError('Duke catalog-scope evidence changed')
    total=re.search(r'at least (\d+) required units',text,re.I)
    if not total:raise ValueError('Duke major unit total missing')
    req[0]['credits']=int(total[1]);req[0]['credit_unit']='units'
    req.append(rule('duke-ai-current-scope','Catalog applicability and host degree context',source,parent='duke-ai-concentration',summary='The revised curriculum applies to Fall 2026 first-year matriculants. Earlier matriculants retain prior requirements. The source separately requires 34 units for the BS; host college and general-education requirements are not fully mapped here.'))
    return observation(pid,text,list(courses.values()),req)


def parse_duke_substitutions(html,pid,source,url):
    soup=BeautifulSoup(html,'html.parser');body=soup.find('main') or soup;text=clean(body.get_text(' ',strip=True))
    if not all(t.lower() in text.lower() for t in ['COMPSCI 201','COMPSCI 230','COMPSCI 270','No online courses']):raise ValueError('Duke substitution guide layout changed')
    return observation(pid,text,[],[rule('duke-ai-substitution-observation','Substitution guide observation',source,summary='Source digest records changes for review; full conditional substitutions are not automatically applied to this concentration.')])
