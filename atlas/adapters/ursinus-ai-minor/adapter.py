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
