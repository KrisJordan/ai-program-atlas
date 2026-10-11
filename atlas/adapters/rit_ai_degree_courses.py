"""Observe course cards rendered by RIT's public AI BS curriculum page.

The ordinary HTTP page may omit cards loaded by the public browser UI. This
parser accepts only a rendered card with the degree and version context. It
does not fetch restricted catalog endpoints or manufacture taxonomy reviews.
"""
import re
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, course

PROGRAM_ID = 'rochester-institute-of-technology-artificial-intelligence-bs-degree'
SOURCE_ID = 'rit-ai-bs-rendered-2026-2027'
URL = 'https://www.rit.edu/study/artificial-intelligence-bs'


def parse_rendered_courses(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = clean(soup.get_text(' ', strip=True))
    if not any(clean(h.get_text(' ', strip=True)) == 'Artificial Intelligence Bachelor of Science Degree' for h in soup.find_all('h1')):
        raise ValueError('RIT AI BS heading missing')
    if 'Curriculum for 2026-2027 for Artificial Intelligence BS' not in text:
        raise ValueError('RIT AI BS curriculum version changed or missing')
    courses = []
    for card in soup.select('.courseblock'):
        def value(selector):
            node = card.select_one(selector)
            return clean(node.get_text(' ', strip=True)) if node else None
        code, title, hours = value('.detail-code'), value('.detail-title'), value('.detail-hours_html')
        if not code or not re.fullmatch(r'[A-Z]+-\d+', code) or not title:
            raise ValueError('Course card identity missing')
        match = re.fullmatch(r'\((\d+(?:\.\d+)?) Credits?\)', hours or '')
        if not match:
            raise ValueError('Unrecognized course credit amount')
        item = course(PROGRAM_ID, code, title, SOURCE_ID, URL, float(match[1]))
        # D01.4 supplies reviewed semester-unit evidence in the curated record;
        # an isolated card says only Credits and must not normalize it itself.
        item['description'] = value('.courseblockextra')
        item['prerequisites'] = value('.detail-requisites')
        courses.append(item)
    if not courses or len({c['id'] for c in courses}) != len(courses):
        raise ValueError('Missing or duplicate rendered course cards')
    return {'id': PROGRAM_ID, 'courses': courses}
