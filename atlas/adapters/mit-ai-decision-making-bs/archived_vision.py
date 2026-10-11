"""The instructor-linked Spring2024 site is dated supplementary metadata."""
import hashlib
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

URL='https://advances-in-vision.github.io/'
SID='mit-ai-vision-spring2024'
REVIEW=json.loads(Path(__file__).with_name('reviewed_archived_vision.json').read_text())


def observe(html):
    soup=BeautifulSoup(html,'html.parser')
    for tag in soup(['script','style']):tag.decompose()
    text=' '.join(soup.get_text(' ',strip=True).split())
    if '6.8300/6.8301: Advances in Computer Vision'not in text or 'Spring 2024'not in text:
        raise ValueError('Archived vision identity/term missing')
    overview=soup.find('h2',string='Course Overview')
    paragraph=overview.find_next_sibling('p')if overview else None
    if paragraph is None:raise ValueError('Archived vision overview missing')
    units=re.search(r'(\d+)-(\d+)-(\d+) for 6\.8301 \(Undergraduate Level, CI-M Subject\)',text)
    prereq=re.search(r'prerequisites of this course are (.*?)\. Good luck',text)
    if not units or not prereq:raise ValueError('Archived undergraduate units/prerequisites missing')
    return dict(digest=hashlib.sha256(text.encode()).hexdigest(),
                credits=sum(map(int,units.groups())),prerequisites=prereq[1])


def parse(html):
    observed=observe(html)
    if observed['digest']!=REVIEW['source_digest']:
        return dict(id='mit-ai-decision-making-bs',courses=[],requirements=[])
    c=dict(id='mit-ai-6-8301',code='6.8301',name='Advances in Computer Vision (CI-M)',
           description=REVIEW['description_summary'],prerequisites=observed['prerequisites'],
           credits=observed['credits'],credit_unit='units',category='ai_ml',source_id=SID,
           url=URL,public_site=URL,syllabus=None,notes=list(REVIEW['notes']))
    return dict(id='mit-ai-decision-making-bs',courses=[c],requirements=[])


SOURCE_PARSERS={URL:parse}
