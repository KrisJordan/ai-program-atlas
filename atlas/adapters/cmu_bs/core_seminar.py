"""Observe the current university-wide Core@CMU description, not the search popup."""
import hashlib
import re
from bs4 import BeautifulSoup
from .common import course, text

URL = 'https://coursecatalog.web.cmu.edu/intercollegeprograms/courses/'
SITE = 'https://www.cmu.edu/c-cm/'
PID = 'cmu-bs-ai'
SOURCE = PID + '-university-course-directory'


def parse(html):
    soup = BeautifulSoup(html, 'html.parser')
    if not any(text(h) == 'Carnegie Mellon University-Wide Studies Courses' for h in soup.find_all(['h1', 'h2'])):
        raise ValueError('University-wide course directory heading missing')
    edition = re.search(r'20\d{2}[-–]20\d{2}\s+Catalog', text(soup))
    if not edition:
        raise ValueError('University-wide course catalog edition missing')
    blocks = [b for b in soup.find_all('dl', class_='courseblock') if b.dt and text(b.dt).startswith('99-101 ')]
    if len(blocks) != 1 or text(blocks[0].dt) != '99-101 Core@CMU' or not blocks[0].dd:
        raise ValueError('Expected unique Core@CMU identity')
    body = text(blocks[0].dd)
    for phrase in ['Collaboration', 'Teamwork', 'Communication', 'Presentation', 'Information', 'Data Literacy', 'Intercultural', 'Global Literacy']:
        if phrase not in body:
            raise ValueError('Core4 description changed: ' + phrase)
    units = re.match(r'Fall and Spring:\s*(\d+(?:\.\d+)?) units', body)
    if not units:
        raise ValueError('Core@CMU unit statement changed')
    c = course('99-101', 'Core@CMU', SOURCE, URL, 'human_context', float(units[1]))
    return dict(id=PID, catalog_year=edition[0].split()[0], curriculum_status='partial', courses=[c], requirements=[], observed_description_digests={'99-101':hashlib.sha256(body.encode()).hexdigest()})
