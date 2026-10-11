"""Bounded instructor identification, not a missing full course description."""
import hashlib
import json
from pathlib import Path
from bs4 import BeautifulSoup

URL='https://edgerton.mit.edu/about/staff/james-w-bales'
COURSE_URL='https://edgerton.mit.edu/courses/strobe-project-laboratory'
SID='mit-ai-strobe-instructor'
REVIEW=json.loads(Path(__file__).with_name('reviewed_strobe.json').read_text())


def observe(html):
    soup=BeautifulSoup(html,'html.parser')
    main=soup.find('main')
    if main is None or 'James W. Bales'not in main.get_text(' ',strip=True):
        raise ValueError('Strobe instructor identity missing')
    link=main.find('a',href=COURSE_URL)
    if link is None or link.get_text(' ',strip=True)!='6.9030 Strobe Project Lab':
        raise ValueError('Explicit Strobe course link missing')
    paragraph=link.find_parent('p')
    if paragraph is None:raise ValueError('Strobe identification paragraph missing')
    text=' '.join(paragraph.get_text(' ',strip=True).split())
    return hashlib.sha256(text.encode()).hexdigest()


def parse(html):
    if observe(html)!=REVIEW['paragraph_digest']:
        return dict(id='mit-ai-decision-making-bs',courses=[],requirements=[])
    return dict(id='mit-ai-decision-making-bs',requirements=[],courses=[dict(
        id='mit-ai-6-9030',code='6.9030',name='Strobe Project Laboratory',
        description=REVIEW['description_summary'],prerequisites=None,credits=None,
        credit_unit='units',category='applications',source_id=SID,url=URL,
        public_site=None,syllabus=None,notes=list(REVIEW['notes']))])


SOURCE_PARSERS={URL:parse}
