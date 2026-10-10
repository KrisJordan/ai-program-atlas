"""Bounded official course metadata; prerequisites preserve the catalog's logical wording."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import course,text
PID='university-of-california-san-diego-artificial-intelligence-bs-degree'
URL='https://catalog.ucsd.edu/courses/CSE.html'
CODES={'CSE 25','CSE 55','CSE 100','CSE 101','CSE 150A','CSE 151A'}

def parse(html):
    soup=BeautifulSoup(html,'html.parser'); courses=[]
    for heading in soup.find_all('p',class_='course-name'):
        match=re.match(r'^(CSE \d+[A-Z]*)\. (.*?) \((\d+)\)',text(heading))
        if not match or match[1] not in CODES:continue
        code,name,credits=match.groups();c=course(code,name,PID+'-courses',URL,credits=int(credits),institution='ucsd',unit='quarter_hours')
        sibling=heading.find_next_sibling()
        if sibling and sibling.name=='p' and 'course-name' not in sibling.get('class',[]):
            prose=text(sibling)
            if 'Prerequisites:' in prose:
                # Do not invent parenthesization of the catalog's mixed and/or chains.
                c['prerequisites']=prose.split('Prerequisites:',1)[1].split(';',1)[0].split('. ',1)[0].strip().rstrip('.')
        courses.append(c)
    if {c['code'] for c in courses}!=CODES:raise ValueError('UCSD selected course metadata inventory changed')
    return {'id':PID,'courses':courses,'notes':['Selected CSE course metadata only. Mixed and/or prerequisites retain catalog wording; no additional logical grouping is inferred. Enrollment and equivalent-credit restrictions remain in the linked course source.']}
