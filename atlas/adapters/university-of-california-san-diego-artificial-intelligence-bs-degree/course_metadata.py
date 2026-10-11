"""Bounded official course metadata; prerequisites preserve the catalog's logical wording."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import course,text
PID='university-of-california-san-diego-artificial-intelligence-bs-degree'
URL='https://catalog.ucsd.edu/courses/CSE.html'
CODES={'CSE 12','CSE 30','CSE 25','CSE 55','CSE 100','CSE 101','CSE 150A','CSE 151A'}

def parse(html):
    soup=BeautifulSoup(html,'html.parser'); courses=[]
    for heading in soup.find_all('p',class_='course-name'):
        match=re.match(r'^(CSE \d+[A-Z]*)\. (.*?) \((\d+)\)',text(heading))
        if not match or match[1] not in CODES:continue
        code,name,credits=match.groups();c=course(code,name,PID+'-courses',URL,credits=int(credits),institution='ucsd',unit='quarter_hours')
        parts=[]
        for sibling in heading.find_next_siblings():
            if 'course-name' in sibling.get('class',[]) or sibling.name in ['h1','h2','h3']:
                break
            if 'course-descriptions' in sibling.get('class',[]):
                parts.append(text(sibling))
        prose=' '.join(parts)
        if 'Prerequisites:' not in prose:
            raise ValueError('UCSD reviewed core prerequisite field missing')
        # Keep full logical wording, subsequent eligibility and credit rules.
        c['prerequisites']=prose.split('Prerequisites:',1)[1].strip()
        before=prose.split('Prerequisites:',1)[0]
        if 'Recommended preparation:' in before:
            c['prerequisites']+=' Recommended preparation (not a prerequisite): '+before.split('Recommended preparation:',1)[1].strip()
        if code=='CSE 151A':
            restriction='Students may not receive credit for both CSE 151A and COGS 188.'
            if restriction not in before:raise ValueError('CSE151Acredit restriction changed')
            c['prerequisites']+=' Credit restriction: '+restriction
        courses.append(c)
    if {c['code'] for c in courses}!=CODES:raise ValueError('UCSD selected course metadata inventory changed')
    return {'id':PID,'courses':courses,'notes':['Selected CSE course metadata only. Mixed and/or prerequisites retain catalog wording; no additional logical grouping is inferred. Enrollment and equivalent-credit restrictions remain in the linked course source.']}

MATH_URL = 'https://catalog.ucsd.edu/courses/MATH.html'


def parse_math(html):
    soup = BeautifulSoup(html, 'html.parser')
    courses = []
    if not any(text(h) == 'Mathematics' for h in soup.find_all('h1')):
        raise ValueError('UCSD mathematics catalog heading changed')
    for heading in soup.find_all('p', class_='course-name'):
        match = re.fullmatch(r'(MATH 20[AB])\. (.*?) \((\d+)\)', text(heading))
        if not match:
            continue
        code, name, credits = match.groups()
        parts = []
        for sibling in heading.find_next_siblings():
            if 'course-name' in sibling.get('class', []) or sibling.name in ['h1', 'h2', 'h3']:
                break
            parts.append(text(sibling))
        prose = ' '.join(parts)
        if 'Prerequisites:' not in prose:
            raise ValueError('UCSD calculus prerequisite section missing')
        c = course(code, name, PID+'-math-courses', MATH_URL, credits=int(credits),
                   institution='ucsd', unit='quarter_hours', category='mathematics')
        c['prerequisites'] = prose.split('Prerequisites:', 1)[1].strip()
        courses.append(c)
    if {c['code'] for c in courses} != {'MATH 20A', 'MATH 20B'}:
        raise ValueError('UCSD fixed calculus course inventory changed')
    return {'id': PID, 'courses': courses,
            'notes': ['Mathematics prerequisites may be replaced by equivalent or higher courses under the catalog preamble. Credit reductions for prior calculus remain source conditions, not a change to ordinary four-unit course values.']}
