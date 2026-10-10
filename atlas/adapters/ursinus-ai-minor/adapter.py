"""Extract required course codes and total credits from the Ursinus requirements page."""
import re
from bs4 import BeautifulSoup

PROGRAM_ID = 'ursinus-ai-minor'
SOURCES = ('https://www.ursinus.edu/academics/artificial-intelligence/courses-requirements/',)
SOURCE_ID = 'ursinus-ai-requirements'


def parse(html: str) -> dict:
    soup = BeautifulSoup(html, 'html.parser')
    heading = soup.find(['h2', 'h3'], string=lambda s: s and s.strip() == 'Requirements for Artificial Intelligence Minor')
    if not heading:
        raise ValueError('AI minor requirement identity missing')
    text = ' '.join(soup.get_text(' ', strip=True).split())
    total = re.search(r'minor in artificial intelligence consists of (\d+) credits', text)
    required = heading.find_next('ul')
    if not total or not required:
        raise ValueError('Total or required list missing')
    courses = []
    for li in required.find_all('li', recursive=False):
        code = li.get_text(' ', strip=True)
        if not re.fullmatch(r'[A-Z]+(?:/[A-Z]+)?-\d{3}[A-Z]?', code):
            raise ValueError('Required course format changed')
        courses.append(dict(id='ursinus-'+re.sub(r'[^a-z0-9]+','-',code.lower()),
            code=code, name=None, description=None, prerequisites=None, credits=None,
            credit_unit='unknown', category='other', source_id=SOURCE_ID,
            url=SOURCES[0], public_site=None, syllabus=None))
    if not courses:
        raise ValueError('Empty required list')
    return dict(id=PROGRAM_ID,title='Artificial Intelligence',award_level='minor',
        program_kind='minor',curriculum_status='partial',courses=courses,
        requirements=[dict(id=PROGRAM_ID+'-required',parent_id=None,title='Required courses',
            kind='all',count=None,credits=None,credit_unit='unknown',category='other',
            source_id=SOURCE_ID,source_text=None,summary='Complete the observed required courses; minor total '+total.group(1)+' credits. Elective and approval rules need separate review.',course_ids=[c['id'] for c in courses])])

COURSE_URL='https://www.ursinus.edu/academics/mathematics-computer-science-and-statistics/courses/'
def parse_audio_course(html):
    import hashlib
    soup=BeautifulSoup(html,'html.parser')
    if not any(h.get_text(' ',strip=True)=='Mathematics, Computer Science and Statistics Courses' for h in soup.find_all('h1')):raise ValueError('Ursinus department identity missing')
    found=[p for p in soup.find_all('p',class_='course-number-name') if p.get_text(' ',strip=True).startswith('CS/MUS-372. ')]
    if len(found)!=1:raise ValueError('Exact cross-listed course missing or duplicated')
    heading=found[0];desc=heading.find_next_sibling('p')
    if desc is None or 'course-text' not in desc.get('class',[]):raise ValueError('Course description missing')
    text=' '.join(desc.get_text(' ',strip=True).split())
    amount=re.search(r'\b(One|Two|Three|Four|Five|Six|\d+(?:\.\d+)?) semester hours\.',text)
    prerequisite=re.search(r'Prerequisite: (.+?)\. (?:\w+ hours per week\.|\w+ semester hours\.)',text)
    if not amount:raise ValueError('Ursinus course amount missing')
    words={'One':1,'Two':2,'Three':3,'Four':4,'Five':5,'Six':6}
    credits=words.get(amount[1]) or float(amount[1])
    return dict(id=PROGRAM_ID,curriculum_status='partial',requirements=[],courses=[dict(id='ursinus-cs-372',code='CS-372',name=heading.get_text(' ',strip=True).split('. ',1)[1],description=None,prerequisites=prerequisite[1] if prerequisite else None,credits=credits,credit_unit='semester_hours',category='applications',source_id='ursinus-cs-mus-372',url=COURSE_URL,public_site=None,syllabus=None)],observed_course_digest=hashlib.sha256(text.encode()).hexdigest())
SOURCES=list(SOURCES)+[COURSE_URL]
SOURCE_PARSERS={COURSE_URL:parse_audio_course}
