"""Focused observers for three reviewed minors; no inferred graduation audits."""
import hashlib
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

WORDS = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6}


def clean(value):
    return ' '.join(value.replace('\xa0', ' ').split())


def slug(value):
    return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')


def count(text, pattern):
    match = re.search(pattern, text, re.I)
    if not match:
        raise ValueError('Required numeric rule missing: ' + pattern)
    token = match[1].lower()
    return WORDS[token] if token in WORDS else float(token)


def node(id, title, kind='note', parent=None, courses=(), credits=None, number=None, summary='', source=None):
    return dict(id=id, parent_id=parent, title=title, kind=kind, count=number, credits=credits, credit_unit='semester_hours', category='other', source_id=source, source_text=None, summary=summary, course_ids=list(courses))


def extract(html, pid, source, url, scope='minorrequirementstextcontainer'):
    soup = BeautifulSoup(html, 'html.parser')
    h = soup.find('h1')
    if not h or 'Artificial Intelligence' not in h.get_text() or 'Minor' not in h.get_text():
        raise ValueError('Official AI minor heading missing')
    body = soup.find(id=scope)
    if not body:
        raise ValueError('Minor requirements container missing')
    courses, tables, aliases = {}, [], {}
    for table in body.find_all('table', class_='sc_courselist'):
        rows=[]
        for tr in table.find_all('tr'):
            cells=tr.find_all('td',recursive=False)
            if not cells:
                continue
            text=clean(tr.get_text(' ',strip=True))
            credit_cell=tr.find('td',class_='hourscol')
            credit_text=clean(credit_cell.get_text(' ',strip=True)) if credit_cell else ''
            credits=float(credit_text) if re.fullmatch(r'\d+(?:\.\d+)?',credit_text) else None
            codecell=tr.find('td',class_='codecol')
            anchors=codecell.find_all('a',class_='code') if codecell else []
            if anchors:
                names=[re.sub(r'^and\s+', '', clean(v)) for v in cells[1].stripped_strings]
                codes=[clean(a.get_text(' ',strip=True)) for a in anchors]
                if 'orclass' in tr.get('class',[]) and rows and rows[-1].get('course_ids'):
                    key=rows[-1]['course_ids'][-1]
                    for code in codes:
                        aliases[code]=key
                        if code not in courses[key]['code']:
                            courses[key]['code']+=' / '+code
                    continue
                ids=[]
                for index,(a,code) in enumerate(zip(anchors,codes)):
                    key=aliases.get(code) or slug(pid.split('-university')[0]+'-'+code)
                    aliases[code]=key
                    if key not in courses:
                        name=names[index] if index<len(names) else None
                        courses[key]=dict(id=key,code=code,name=name,description=None,prerequisites=None,credits=credits if len(codes)==1 else None,credit_unit='semester_hours',category='other',source_id=source,url=urljoin(url,a.get('href') or url),public_site=None,syllabus=None)
                    ids.append(key)
                rows.append(dict(type='course',text=text,course_ids=ids,credits=credits))
            else:
                rows.append(dict(type='heading' if 'areaheader' in tr.get('class',[]) else 'rule',text=text,credits=credits,course_ids=[]))
        tables.append(rows)
    text=clean(body.get_text(' ',strip=True))
    return soup, text, list(courses.values()), tables


def observed(pid,soup,text,courses,req):
    edition=re.search(r'20\d{2}[–-]20\d{2}',soup.get_text(' ',strip=True))
    return dict(id=pid,program_kind='minor',award_level='minor',curriculum_status='partial',catalog_year=edition[0].replace('–','-') if edition else None,courses=courses,requirements=req,observed_policy_digest=hashlib.sha256(text.encode()).hexdigest())


def parse_case(html,pid,source,url):
    soup,text,courses,tables=extract(html,pid,source,url,'programrequirementstextcontainer')
    if 'prior coursework in computer science and mathematics' not in clean(soup.get_text(' ',strip=True)):
        raise ValueError('Case preparation assumption needs review')
    total_courses=count(text,r'minor consists of (\w+) courses')
    overlap=count(text,r'No more than (\w+) courses can be double counted')
    total_credits=count(text,r'Total Credit Hours (\d+)')
    req=[node('case-ai-minor','AI minor local curriculum','all',credits=total_credits,summary=f'Complete {total_courses:g} courses and {total_credits:g} credit hours under the group rules.',source=source)]
    section=None
    members={}
    for row in tables[0]:
        if row['type']=='heading':
            title=re.sub(r'\s+\d+$','',row['text']).rstrip(':')
            section='case-'+slug(title)
            req.append(node(section,title,'all',parent='case-ai-minor',credits=row['credits'],source=source))
            members[section]=[]
        elif row['type']=='rule' and row['text'].startswith('Choose '):
            amount=int(count(row['text'],r'Choose (\w+) of'))
            group=next(r for r in req if r['id']==section)
            group.update(kind='choose_courses',count=amount,summary=f'Select {amount} course'+('' if amount==1 else 's')+' from the listed options.')
        elif row['type']=='course' and section:
            members[section].extend(row['course_ids'])
    if len(members)!=3:
        raise ValueError('Expected required, societal-impact and technical groups')
    for r in req:
        if r['id'] in members:
            r['course_ids']=list(dict.fromkeys(members[r['id']]))
    req.append(node('case-overlap','Overlap and preparation',parent='case-ai-minor',summary=f'At most {overlap:g} courses may also satisfy the major. The program assumes prior computer-science and mathematics coursework.',source=source))
    for c in courses:
        c['category']='human_context' if c['id'] in members.get('case-societal-impact-elective',[]) else 'ai_ml'
    return observed(pid,soup,text,courses,req)


def parse_neu_interdisciplinary(html,pid,source,url):
    soup,text,courses,tables=extract(html,pid,source,url)
    gpa=count(text,r'Minimum ([\d.]+) GPA')
    if 'not used to fulfill another requirement' not in text or 'prerequisite' not in text:
        raise ValueError('Elective uniqueness/preparation policy needs review')
    req=[node('neu-inter-ai-minor','Interdisciplinary AI minor local requirements','all',summary='Complete the technology/ethics, experiential and elective groups. Listed alternatives are not all compulsory.',source=source)]
    section=None
    for row in tables[0]:
        if row['type']=='heading':
            section='neu-inter-'+slug(row['text'])
            req.append(node(section,row['text'],'all',parent='neu-inter-ai-minor',source=source))
        elif row['type']=='rule' and row['text'].startswith('Complete '):
            group=next(r for r in req if r['id']==section)
            number=int(count(row['text'],r'Complete (\w+) of'))
            group.update(kind='choose_courses',count=number,credits=row['credits'],summary=f'Choose {number} course'+('' if number==1 else 's')+'. Elective selections must not fulfill another requirement within this minor.' if 'Electives' in group['title'] else f'Choose {number} course from these options; slash-listed codes are alternatives for the same course.')
        elif row['type']=='course' and section:
            next(r for r in req if r['id']==section)['course_ids'].extend(row['course_ids'])
    if len(req)!=4 or any(r['kind']!='choose_courses' for r in req[1:]):
        raise ValueError('Expected three explicit course-choice groups')
    req.append(node('neu-inter-academic-policy','GPA and prerequisite/corequisite obligations',parent='neu-inter-ai-minor',summary=f'Minimum minor GPA {gpa:.3f}. Complete any specified prerequisites, corequisite labs, recitations, clinicals or tools courses; some elective choices have prerequisites.',source=source))
    if any(c['code']=='PHIL 1300 / DS 1300' for c in courses):
        req.append(node('neu-inter-crosslist-scope','Course-code eligibility by group',parent='neu-inter-electives',summary='DS 1300 is explicitly listed as an alternative to PHIL 1300 in Technology and Ethics. The elective table names PHIL 1300; do not infer that a merged cross-listed record independently authorizes the DS code in the elective group.',source=source))
    ethics=set(req[1]['course_ids']);applied=set(req[2]['course_ids'])
    for c in courses:c['category']='human_context' if c['id'] in ethics else 'applications' if c['id'] in applied else 'electives'
    return observed(pid,soup,text,courses,req)


def parse_neu_ai(html,pid,source,url):
    soup,text,courses,tables=extract(html,pid,source,url)
    for phrase in ['non–Khoury majors','at most one Khoury minor','self-assessment','4-5 semester hours','3000 level or higher','not otherwise required in the degree','DS 2010 to DS 4989','Meaningful Minor']:
        if phrase not in text:raise ValueError('Khoury minor policy requires review: '+phrase)
    if len(tables)!=3:raise ValueError('Expected required, elective and Meaningful Minor tables')
    req=[node('neu-ai-minor','Khoury AI minor local requirements','all',summary='Complete foundational programming, AI foundations and a four-hour AI elective. The first programming pair has an assessed placement alternative.',source=source)]
    required=[r for r in tables[0] if r['type']=='course']
    if len(required)!=4 or len(required[0]['course_ids'])!=2 or len(required[1]['course_ids'])!=2:raise ValueError('Programming bundle or AI foundation structure changed')
    initial_codes={c['code'] for c in courses if c['id'] in required[0]['course_ids']}
    if initial_codes != {'CS 2000','CS 2001'}:raise ValueError('Initial placement pair changed; review substitution')
    req.append(node('neu-ai-placement','Initial programming or assessed placement','alternative',parent='neu-ai-minor',summary='Either take the initial lecture/lab pair or use the documented assessed-placement substitution.',source=source))
    req.append(node('neu-ai-first-programming','Initial programming lecture and lab','all',parent='neu-ai-placement',courses=required[0]['course_ids'],credits=required[0]['credits'],source=source))
    req.append(node('neu-ai-placement-substitution','Successful self-assessment substitution',parent='neu-ai-placement',summary='Students placing out of both CS 2000 and CS 2001 substitute 4–5 semester hours of CS, CY or DS coursework at level 3000 or above that is not otherwise required in the degree.',source=source))
    req.append(node('neu-ai-second-programming','Second programming lecture and lab','all',parent='neu-ai-minor',courses=required[1]['course_ids'],credits=required[1]['credits'],source=source))
    req.append(node('neu-ai-foundations','AI foundations','all',parent='neu-ai-minor',courses=[c for r in required[2:] for c in r['course_ids']],source=source))
    elective_rule=tables[1][0]
    number=int(count(elective_rule['text'],r'Complete (\w+) of'))
    if number != 1:raise ValueError('AI elective selection count changed; review alternatives')
    req.append(node('neu-ai-elective','AI elective alternatives','alternative',parent='neu-ai-minor',credits=elective_rule['credits'],summary=f'Select {number} elective. At most one Meaningful Minor course may contribute to this minor.',source=source))
    direct=[c for r in tables[1] for c in r['course_ids']]
    req.append(node('neu-ai-database','Database option','all',parent='neu-ai-elective',courses=direct,source=source))
    req.append(node('neu-ai-ds-range','DS numeric-range option',parent='neu-ai-elective',summary='An eligible DS course numbered 2010 through 4989 may fulfill the AI elective; the catalog defines an open numeric range rather than a finite table here.',source=source))
    req.append(node('neu-ai-meaningful','Meaningful Minor option','choose_courses',parent='neu-ai-elective',number=1,summary='Choose one from the full preapproved cross-college list represented by the following option groups; no more than one may count toward the minor.',source=source))
    active=None
    for row in tables[2]:
        if row['type']=='heading':
            active='neu-ai-meaningful-'+slug(row['text'])
            req.append(node(active,row['text']+' options',parent='neu-ai-meaningful',summary='Eligible options within the overall one-course Meaningful Minor choice.',source=source))
        elif row['type']=='course' and active:
            next(r for r in req if r['id']==active)['course_ids'].extend(row['course_ids'])
    req.append(node('neu-ai-eligibility','Eligibility and corequisites',parent='neu-ai-minor',summary='Only non-Khoury majors are eligible. Khoury-only and Khoury combined majors are excluded. At most one Khoury minor may be declared. Complete specified corequisite labs, recitations, clinicals and tools courses.',source=source))
    for c in courses:
        c['category']='foundations' if c['id'] in required[0]['course_ids']+required[1]['course_ids'] else 'mathematics' if c['id'] in required[2]['course_ids'] else 'ai_ml' if c['id'] in required[3]['course_ids'] else 'electives'
    return observed(pid,soup,text,courses,req)


def policy_observation(html,pid,source,kind):
    soup=BeautifulSoup(html,'html.parser');body=soup.find(id='textcontainer')
    if not body:raise ValueError('Policy content container missing')
    text=clean(body.get_text(' ',strip=True))
    if kind=='neu':
        cap=count(text,r'maximum of (\d+)% of the credits required for a minor')
        minimum_courses=count(text,r'minor consists of a minimum of (\w+) courses')
        minimum_hours=count(text,r'minimum of \w+ courses \((\d+) semester hours\)')
        for term in ['end of the junior year','concurrently','may not extend','subset of required courses']:
            if term not in text:raise ValueError('General minor policy changed: '+term)
        summary=f'Declare by the end of junior year; complete the minor and major concurrently without extending the degree to finish the minor. Major and minor may not be the same program when minor courses are a subset of required major courses. At most {cap:g}% of minor credits may be double counted from major, transfer or advanced-standing credit, subject to stricter local limits. The university defines a minor as at least {minimum_courses:g} courses/{minimum_hours:g} semester hours; background coursework may be extra.'
    elif kind=='case-grades':
        if 'regular evaluative grades' not in text or 'designated in SIS' not in text:raise ValueError('Case minor grade policy changed')
        summary='Minor courses require regular evaluative grades. Elected pass/no-pass courses do not count, except courses officially designated pass/no-pass-only in SIS. A later-declared minor may permit a request to reveal an earlier elected pass/no-pass grade at the start of the final academic term.'
    else:
        for term in ['major or minor declaration form','requirements term','grade of C or better','department chair or academic representative']:
            if term not in text:raise ValueError('Case declaration/transfer policy changed: '+term)
        summary='A signed minor declaration must be submitted and recorded in SIS; the requirements term normally follows matriculation unless a later catalog is selected. Minor changes/corrections should be submitted at least one semester before graduation. External coursework needs advance approval, including department approval for the minor, an official transcript, and a grade of C or better; no grade-point average is imported from the external course.'
    return dict(id=pid,program_kind='minor',curriculum_status='partial',courses=[],requirements=[node(source+'-rule','University minor policy',summary=summary,source=source)],observed_policy_digest=hashlib.sha256(text.encode()).hexdigest())
