"""Observed departmental GIR descriptions, separate from eligibility inventory."""
import hashlib
import json
import re
from pathlib import Path
from atlas.adapters.national_curriculum_common import clean, content, course, rule, require_phrases
from importlib import import_module
units=import_module('atlas.adapters.mit-ai-decision-making-bs.subject_conventions')
PID='mit-ai-decision-making-bs'
CALCULUS='https://math.mit.edu/academics/undergrad/first/calculus.html'
BIOLOGY='https://biology.mit.edu/undergraduate/major-minor-requirements/general-institute-requirement/'
CHEMISTRY='https://chemistry.mit.edu/classes/'
SOLID='https://3091.mit.edu/'
FIRST='https://math.mit.edu/academics/undergrad/first/index.html'
SPECS={CALCULUS:('calculus',['18.01','18.02','18.022','18.01A','18.02A']),BIOLOGY:('biology',['7.012','7.014','7.015','7.016']),CHEMISTRY:('chemistry',['5.111','5.112']),SOLID:('solid',['3.091'])}
REVIEWS=json.loads(Path(__file__).with_name('reviewed_gir_subjects.json').read_text()) if Path(__file__).with_name('reviewed_gir_subjects.json').exists()else{}


def blocks(html,url):
    key,codes=SPECS[url]
    heading={'calculus':'Calculus','biology':'General Institute Requirement','chemistry':'Classes','solid':'3.091'}[key]
    root=content(html,heading);root=root.find('main')or root
    if key=='calculus':
        require_phrases(root,['Any form of 18.01 credit fulfills the prerequisite for all forms of 18.02.','12 units of credit','high school algebra and trigonometry'])
    if key=='biology':require_phrases(root,['chemical bonding and molecular interactions','Enrollment limited','7.01x Comparison Sheet'])
    result={}
    for code in codes:
        name=None;prereq=None;credit=None
        if key in {'biology','chemistry'}:
            h=next((h for h in root.find_all('h3')if clean(h.get_text()).split(' ')[0]==code),None)
            if h is None:raise ValueError('GIR subject heading missing: '+code)
            panel=root.find(id=h.get('aria-controls'))
            if panel is None:raise ValueError('GIR subject panel missing: '+code)
            evidence=clean(panel.get_text(' ',strip=True))
            if key=='chemistry':
                name=clean(h.get_text())[len(code)+1:]
                credit=units.credits(evidence)
                match=re.search(r'Prereq:\s*(.*?)(?:\s+Introduction|$)',evidence)
                prereq=match[1]if match else None
            else:
                # Shared core description is required evidence for each variant.
                common=clean(root.get_text(' ',strip=True)).split('Subject options')[0]
                evidence=common+' '+evidence
        elif key=='calculus':
            h=next((h for h in root.find_all('h3')if clean(h.get_text()).startswith(code+' ')or(code in {'18.01A','18.02A'}and clean(h.get_text()).startswith('18.01A-18.02A '))),None)
            if h is None:raise ValueError('Calculus subject heading missing: '+code)
            parts=[]
            for n in h.next_siblings:
                if getattr(n,'name',None)in {'h1','h2','h3'}:break
                if getattr(n,'get_text',None):parts.append(clean(n.get_text(' ',strip=True)))
            evidence=' '.join(parts)
            if not evidence:raise ValueError('Calculus description missing')
            name=clean(h.get_text())[len(code)+1:]if code not in {'18.01A','18.02A'}else None
            credit=12
            prereq={'18.01':'High school algebra and trigonometry; any MIT student eligible.','18.02':'Any form of 18.01 credit.','18.022':'18.01 credit.','18.01A':'AP Calculus AB score 5 or passing the first half of the 18.01 Advanced Standing Exam.','18.02A':'Any form of 18.01 credit; the paired 18.01A–18.02A sequence has additional registration conditions.'}[code]
        else:
            require_phrases(root,['3.091: Introduction to Solid-State Chemistry','atomic and molecular scale','semiconductors'])
            evidence=clean(root.get_text(' ',strip=True));name='Introduction to Solid-State Chemistry'
        result[code]=dict(name=name,prerequisites=prereq,credits=credit,evidence=evidence)
    return result


def parse(html,url):
    key,_=SPECS[url];sid=PID+'-gir-'+key;observed=blocks(html,url);courses=[];digests={}
    for code,o in observed.items():
        c=course('mit-ai-gir',code,o['name'],sid,url,unit='units');c['credits']=o['credits'];c['prerequisites']=o['prerequisites']
        digest=hashlib.sha256(o['evidence'].encode()).hexdigest();digests[c['id']]=digest
        reviewed=REVIEWS.get(code)
        if reviewed and reviewed['digest']==digest and reviewed['name']==o['name']:
            c['category']=reviewed['category'];c['description']=reviewed['summary'];c['notes']=list(reviewed.get('notes',[]))
        courses.append(c)
    return dict(id=PID,courses=courses,requirements=[],observed_gir_description_digests=digests)


def parse_first_year(html):
    root=content(html,'First Year Subjects')
    require_phrases(root,['first year students are not allowed to take graduate level classes'])
    return dict(id=PID,courses=[],requirements=[rule('mit-ai-first-year-math-graduate','First-year mathematics enrollment restriction',PID+'-gir-first-year',kind='note',summary='The mathematics department states first-year students may not take graduate-level classes. Its introductory and advanced undergraduate alternatives remain available; this is a conditional registration constraint on the open Course 18 route, not an extra fixed subject.')])


SOURCE_PARSERS={url:(lambda html,url=url:parse(html,url))for url in SPECS}
SOURCE_PARSERS[FIRST]=parse_first_year
