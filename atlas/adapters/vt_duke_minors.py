"""Source-sensitive observations for VT and Duke minors; never certifies completeness."""
import hashlib
import re

from bs4 import BeautifulSoup

from atlas.adapters.reviewed_minors_2026 import clean, slug


def rule(key, title, source, *, kind='note', parent=None, ids=(), number=None, credits=None, summary='', unit='unknown'):
    return dict(id=key,parent_id=parent,title=title,kind=kind,count=number,credits=credits,credit_unit=unit,category='other',source_id=source,source_text=None,summary=summary,course_ids=list(ids))


def observation(pid, text, courses, requirements):
    return dict(id=pid,program_kind='minor',award_level='minor',curriculum_status='partial',courses=list(courses),requirements=requirements,observed_policy_digest=hashlib.sha256(text.encode()).hexdigest())


def parse_vt(html,pid,source,url):
    soup=BeautifulSoup(html,'html.parser');body=soup.find('main') or soup
    h=body.find('h1')
    if not h or 'Artificial Intelligence (AI) Minor' not in clean(h.get_text()):raise ValueError('VT AI minor heading missing')
    req=[]
    for label in ['Who should pursue this minor','How to pursue the minor']:
        heading=body.find('h3',string=lambda s:s and label==s.strip())
        if not heading:raise ValueError('VT eligibility/declaration section missing')
        parts=[]
        for item in heading.next_siblings:
            if getattr(item,'name',None) in ['h2','h3']:break
            if getattr(item,'get_text',None):parts.append(clean(item.get_text(' ',strip=True)))
        if not parts:raise ValueError('VT policy text missing')
        req.append(rule('vt-'+slug(label),label,source,summary=' '.join(parts)))
    return observation(pid,clean(body.get_text(' ',strip=True)),[],req)


def policy_observation(html,pid,source,kind):
    soup=BeautifulSoup(html,'html.parser');body=soup.find('main') or soup
    for e in body.find_all(['script','style']):e.decompose()
    text=clean(body.get_text(' ',strip=True))
    terms={'vt':['Non-Restricted Engineering Minors','Artificial Intelligence','application'], 'trinity':['At least half','Duke course credits','combined number','three'], 'bulletin':['U-ECE-MLAI','Upper-Level Focus Courses','primary major'], 'concentration':['Concentration Electives','Stellic','Fall 2026']}[kind]
    if any(t not in text for t in terms):raise ValueError('Secondary policy layout/content changed: '+kind)
    return observation(pid,text,[],[])


class Courses:
    def __init__(self,source,url):self.rows={};self.source=source;self.url=url
    def add(self,code,name=None,category='other',topic=False):
        code=clean(code)
        key='duke-'+slug(code)+(('-'+slug(name)) if topic and name else '')
        self.rows.setdefault(key,dict(id=key,code=code,name=name or None,description=None,prerequisites=None,credits=None,credit_unit='unknown',category=category,source_id=self.source,url=self.url,public_site=None,syllabus=None))
        return key
    def line(self,text,category='ai_ml',topic=False):
        # Slash-separated official cross-listings stay one course; a title is optional.
        text=clean(text)
        match=re.search(r'((?:ECE|COMPSCI|CS|STA|Stat|MATH|BME|ME) \d+[A-Z]*(?:/(?:ECE|COMPSCI|CS|STA|Stat|MATH) \d+[A-Z]*)*)(.*)',text)
        if not match:raise ValueError('Course row changed: '+text)
        name=re.sub(r'^\s*(?:\([^)]*\))?\s*[:\-]?\s*','',match[2]) or None
        return self.add(match[1],name,category,topic)


def parse_duke_ml(html,pid,source,url):
    soup=BeautifulSoup(html,'html.parser');anchor=soup.find('a',attrs={'name':'ml'})
    if not anchor:raise ValueError('ML minor anchor missing')
    body=anchor.find_parent('section')
    if not body or 'Minor in Machine Learning & Artificial Intelligence' not in body.get_text(' ',strip=True):raise ValueError('ML minor section missing')
    text=clean(body.get_text(' ',strip=True));courses=Courses(source,url)
    total=re.search(r'minimum of \w+ \((\d+)\) technical courses',text)
    if not total:raise ValueError('ML minimum course rule missing')
    req=[rule('duke-ml-minor','ML/AI minor local curriculum',source,kind='all',number=int(total[1]),summary='Department requirements; current bulletin conflicts remain unresolved. Preparatory examples below are not all compulsory.')]
    sections={clean(h.get_text()):h.find_parent('li',class_='accordion').find('div',class_='accordion__text') for h in body.find_all('h3')}
    for label in ['Fundamental Courses','Upper-Level Focus Courses','Note on Prerequisites','Notes on Course Counting']:
        if label not in sections:raise ValueError('ML required section missing: '+label)
    core=sections['Fundamental Courses'];core_items=core.find('ul').find_all('li',recursive=False)
    if len(core_items)!=3:raise ValueError('ML foundational structure changed')
    req.append(rule('duke-ml-fundamentals','Foundational courses',source,kind='all',parent='duke-ml-minor',number=3))
    for i,li in enumerate(core_items):
        nested=li.find('ul')
        if nested:
            ids=[courses.line(clean(e.get_text(' ',strip=True))) for e in nested.find_all('li',recursive=False)]
            req.append(rule('duke-ml-foundation-'+str(i),'Intermediate ML/AI: choose one',source,kind='choose_courses',parent='duke-ml-fundamentals',ids=ids,number=1))
        else:
            key=courses.line(clean(li.get_text(' ',strip=True)),'mathematics' if i==0 else 'ai_ml')
            req.append(rule('duke-ml-foundation-'+str(i),'Required foundational course',source,kind='all',parent='duke-ml-fundamentals',ids=[key]))
    focus=sections['Upper-Level Focus Courses'];heading=clean(focus.find('h4').get_text())
    amount=re.search(r'\((\d+)\)',heading)
    if not amount:raise ValueError('Focus selection count missing')
    req.append(rule('duke-ml-focus','Upper-level focus courses',source,kind='choose_courses',parent='duke-ml-minor',number=int(amount[1]),summary='Choose from the listed pool at level 300 or above. Special topics and independent study require approval; examples can be historical offerings.'))
    focus_ids=[]
    for i,li in enumerate(focus.find('ul').find_all('li',recursive=False)):
        nested=li.find('ul')
        if nested:
            label=clean(' '.join(str(t) for t in li.find_all(string=True,recursive=False)))
            ids=[courses.line(clean(e.get_text(' ',strip=True)),topic=True) for e in nested.find_all('li',recursive=False)]
            focus_ids.extend(ids)
            for j,item in enumerate(nested.find_all('li',recursive=False)):
                req.append(rule('duke-ml-topic-example-'+str(i)+'-'+str(j),'Special-topic example and offering context',source,parent='duke-ml-topics-'+str(i),ids=[ids[j]],summary=clean(item.get_text(' ',strip=True))))
            req.append(rule('duke-ml-topics-'+str(i),'Approved special-topic options',source,parent='duke-ml-focus',ids=ids,summary=label+' Listed offerings are examples, not a guarantee of availability.'))
        else:focus_ids.append(courses.line(clean(li.get_text(' ',strip=True))))
    next(r for r in req if r['id']=='duke-ml-focus')['course_ids']=focus_ids
    for label in ['Note on Prerequisites','Notes on Course Counting']:
        section=sections[label]
        for i,item in enumerate(section.find_all(['p','li'])):
            req.append(rule('duke-ml-'+slug(label)+'-'+str(i),label,source,parent='duke-ml-minor',summary=clean(item.get_text(' ',strip=True))))
    return observation(pid,text,courses.rows.values(),req)


CODE=re.compile(r'\b(COMPSCI|MATH|STA|BME|LAW|LINGUIST|NEUROSCI|PHIL|JAM|POLSCI|PSY|PUBPOL|SCISOC)\s+(\d+[A-Z]*)\b')


def parse_duke_apps(html,pid,source,url):
    soup=BeautifulSoup(html,'html.parser')
    heading=next((h for h in soup.find_all('h4') if 'Minor in Artificial Intelligence: Applications and Implications' in h.get_text()),None)
    if not heading:raise ValueError('AI applications minor heading missing')
    body=heading.parent;text=clean(body.get_text(' ',strip=True));courses=Courses(source,url)
    req=[rule('duke-apps-minor','AI applications and implications minor',source,kind='all',summary='Three core units plus two elective units, with five prerequisite units documented separately. Elective eligibility wording is unresolved; this is a partial inventory.')]
    headings=body.find_all('h5')
    if len(headings)!=4:raise ValueError('Expected four local requirement groups')
    for ix,h in enumerate(headings):
        title=clean(h.get_text());amount=re.search(r'\((\d+) [Uu]nit',title)
        if not amount:raise ValueError('Group unit count missing')
        key='duke-apps-group-'+str(ix);parts=[]
        for sib in h.next_siblings:
            if getattr(sib,'name',None)=='h5':break
            if getattr(sib,'get_text',None):parts.append(sib)
        group_text=clean(' '.join(e.get_text(' ',strip=True) for e in parts))
        req.append(rule(key,title,source,kind='all' if ix<2 else 'choose_courses',parent='duke-apps-minor',number=1 if ix>=2 else None,credits=int(amount[1]),unit='units',summary=group_text if ix>=2 else 'Complete each choice group below.'))
        if ix<2:
            listing=next((e for e in parts if e.name=='ol'),None)
            if not listing:raise ValueError('Required course list missing')
            for j,li in enumerate(listing.find_all('li',recursive=False)):
                line=clean(li.get_text(' ',strip=True));ids=[];last_subject=None
                for option in re.split(r'\s+OR\s+',line):
                    # COMPSCI 231D and 232 omit the repeated prefix in the official text.
                    if re.match(r'^\d',option) and last_subject:option=last_subject+' '+option
                    matches=list(CODE.finditer(option))
                    if not matches:raise ValueError('Required course code missing: '+option)
                    last_subject=matches[0][1]
                    code=' / '.join(m[1]+' '+m[2] for m in matches)
                    tail=option[matches[-1].end():].lstrip(' -') or None
                    ids.append(courses.add(code,tail,'mathematics' if last_subject in ['MATH','STA'] else 'foundations' if ix==0 or code=='COMPSCI 201' else 'ai_ml'))
                req.append(rule(key+'-choice-'+str(j),' / '.join(courses.rows[k]['code'] for k in ids),source,kind='choose_courses' if len(ids)>1 else 'all',parent=key,ids=ids,number=1 if len(ids)>1 else None))
        elif ix==2:
            ids=[]
            listing=next((e for e in parts if e.name=='ul'),None)
            if not listing:raise ValueError('Outside elective list missing')
            for li in listing.find_all('li',recursive=False):
                line=clean(li.get_text(' ',strip=True));matches=list(CODE.finditer(line))
                if '(cross ' in line:
                    ids.append(courses.add(' / '.join(m[1]+' '+m[2] for m in matches),category='electives'))
                else:
                    ids.extend(courses.add(m[1]+' '+m[2],category='electives') for m in matches)
            next(r for r in req if r['id']==key)['course_ids']=ids
        else:
            req.append(rule('duke-apps-free-paths','Free elective alternatives and unresolved linked pool',source,parent=key,summary='The source offers the prior list, the CS BS AI/ML concentration approved electives, or an AI research independent study. The linked concentration list is not enumerated here; its comprehensive list refers to student-only Stellic. Do not apply BS-specific constraints automatically to this minor.'))
    full=clean((soup.find('main') or soup).get_text(' ',strip=True))
    for term in ['not receive more than one','Computer Science majors']:
        if term not in full:raise ValueError('CS minor eligibility policy changed: '+term)
    req.append(rule('duke-apps-eligibility','Computer Science minor eligibility',source,parent='duke-apps-minor',summary='Students may not pursue more than one CS minor. CS majors may pursue only the computational biology/bioinformatics minor, so are not eligible for this AI minor.'))
    return observation(pid,full,courses.rows.values(),req)
