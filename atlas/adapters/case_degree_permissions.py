"""Case registrar's conditional permission process; no guaranteed student approval."""
from bs4 import BeautifulSoup
from atlas.adapters.business_society_minors import clean, requirement

PERMISSIONS_URL='https://case.edu/registrar/registration-classes/registration-information/permissions'
FACULTY_URL='https://case.edu/registrar/general/student-information-system-sis/sis-resources/faculty-reviewing-permission-requests'


def parse_permissions(html,pid):
    soup=BeautifulSoup(html,'html.parser')
    if not any(clean(h.get_text())=='Permissions' for h in soup.find_all('h1')):raise ValueError('Case permission heading changed')
    headings={clean(h.get_text()):h for h in soup.find_all('h2')};values={}
    for name in ['Requisites Have Not Been Met','There is a Career Restriction']:
        if name not in headings:raise ValueError('Case permission category changed')
        values[name]=clean(headings[name].find_next('p').get_text(' ',strip=True))
    if not all(x in values['Requisites Have Not Been Met'] for x in ['other requirement conditions','not allowed unless a Requisites Not Met permission is granted']):raise ValueError('Case requisite permission condition changed')
    if not all(x in values['There is a Career Restriction'] for x in ['registrar or dean','without receiving permission']):raise ValueError('Case career permission authority changed')
    row=requirement(pid,'registration-exception-process','Conditional requisite and career permission','case-registration-permissions',[],kind='note',summary='Course prerequisites, corequisites and other enrollment conditions remain binding unless Requisites Not Met permission is granted. Cross-career restrictions can additionally require approval from the student’s or course’s school registrar/dean. Listed graduate-program-restricted electives such as SCMG 462/463 are conditional options requiring the relevant permissions if the student does not meet their published conditions. Listing is not guaranteed enrollment or blanket waiver; after approval the student must still register.')
    return dict(id=pid,curriculum_status='partial',requirements=[row])


def parse_faculty(html,pid):
    soup=BeautifulSoup(html,'html.parser')
    if not any(clean(h.get_text())=='Faculty - Permission Requests' for h in soup.find_all('h1')):raise ValueError('Case faculty permission heading changed')
    text=clean(soup.get_text(' ',strip=True))
    if not all(x in text for x in ['career restrictions are managed by school registrars or administrators','forwarded to the appropriate administrator for further action','Granting permission does not enroll the student']):raise ValueError('Case career routing policy changed')
    row=requirement(pid,'career-permission-routing','Career permission requires administrator action','case-faculty-permissions',[],kind='note',summary='Career-restricted enrollment requests require action by the appropriate school registrar or administrator in addition to any instructor action. Permission can be granted or denied; approval does not itself enroll the student.')
    return dict(id=pid,curriculum_status='partial',requirements=[row])


def register(pid,sources,parsers):
    parsers[PERMISSIONS_URL]=lambda html:parse_permissions(html,pid)
    parsers[FACULTY_URL]=lambda html:parse_faculty(html,pid)
    return sources+(PERMISSIONS_URL,FACULTY_URL)
