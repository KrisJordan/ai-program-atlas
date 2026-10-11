"""Observe Miami policy text without replaying a manual curriculum audit."""
import hashlib
from bs4 import BeautifulSoup
from atlas.adapters.business_society_minors import clean

BASE='https://bulletin.miami.edu/general-university-information/undergraduate-policies-and-procedures/'
SPECS={
 'transfer':(BASE+'undergraduate-transfer-credit-policy/','Transfer Credit Policy for Undergraduate Students',['Transfer Credit Policy','Transfer Credit Process','Specific Department Rules']),
 'grades':(BASE+'grades/','Grades',['Credit Only Option','Grade Point Average']),
 'courses':('https://bulletin.miami.edu/general-university-information/university-policies/course-information/','Course Information',['Academic Credit','Credit/No Credit','Repeat Rules']),
 'graduation':(BASE+'graduation/','Graduation',['Degrees']),
 'general':(BASE+'general-education-requirements/','General Education Requirements',['Areas of Proficiency','Areas of Knowledge']),
 'writing':(BASE+'advanced-writing-and-communication-requirement/','Advanced Writing and Communication Requirement',['Requirement']),
 'undergraduate':(BASE,'Undergraduate Policies and Procedures',[]),
 'business':('https://bulletin.miami.edu/undergraduate-academic-programs/business/','Business',['Academic Policies','Degree Programs']),
 'arts':('https://bulletin.miami.edu/undergraduate-academic-programs/arts-sciences/','Arts and Sciences',['Requirements for Graduation']),
}


def parse_policy(html, *, pid, code):
    soup=BeautifulSoup(html,'html.parser');_,title,headings=SPECS[code]
    if not any(clean(h.get_text(' ',strip=True))==title for h in soup.find_all('h1')):
        raise ValueError('Miami policy identity missing or changed')
    content=soup.find(id='content')
    if not content:raise ValueError('Miami policy content missing')
    for nav in content.find_all('nav'):nav.decompose()
    sections={}
    for name in headings:
        matches=[h for h in content.find_all(['h2','h3','h4']) if clean(h.get_text(' ',strip=True))==name]
        if len(matches)!=1:raise ValueError('Miami policy section missing or duplicated: '+name)
        h=matches[0];rank=int(h.name[1]);parts=[]
        for sibling in h.next_siblings:
            if getattr(sibling,'name',None) in ['h2','h3','h4'] and int(sibling.name[1])<=rank:break
            parts.append(sibling.get_text(' ',strip=True) if hasattr(sibling,'get_text') else str(sibling))
        value=clean(' '.join(parts))
        if len(value)<40:raise ValueError('Miami policy body empty: '+name)
        sections[name]=hashlib.sha256(value.encode()).hexdigest()
    if not headings:
        value=clean(content.get_text(' ',strip=True))
        if len(value)<100:raise ValueError('Miami policy body empty')
        sections[title]=hashlib.sha256(value.encode()).hexdigest()
    return dict(id=pid,curriculum_status='partial',courses=[],requirements=[],observed_policy_sections=sections,
                notes=['Policy content hashes require reviewer interpretation; this observation does not certify applicability, credit-unit normalization or completeness.'])


def register(pid,sources,parsers, *, minor=False,business=False):
    codes=['transfer','grades','courses']
    if not minor:codes+=['graduation','general','writing','undergraduate']
    codes+=['business' if business else 'arts']
    for code in codes:
        url=SPECS[code][0]
        if url not in sources:sources.append(url)
        parsers[url]=lambda html,code=code:parse_policy(html,pid=pid,code=code)
