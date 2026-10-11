"""Guarded observations of independently published UCSB department course pages."""
import hashlib
import json
from functools import partial
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import text

PROGRAM_ID = 'ucsb-ai-bs'
SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())
OVERVIEW_URL = 'https://cs.ucsb.edu/education/courses/overview'


def field(article, name):
    node = article.select_one('.field--name-field-' + name + ' .field--item')
    return text(node) if node else None


def parse(html, *, code):
    entry = SPEC[code]
    soup = BeautifulSoup(html, 'html.parser')
    article = soup.select_one('article.course')
    if not article or field(article, 'course-number') != code:
        raise ValueError('UCSB reviewed course identity missing or changed')
    if text(soup.find('h1')) != entry['name']:
        raise ValueError('UCSB reviewed course title changed')
    if hashlib.sha256(text(article).encode()).hexdigest() != entry['article_digest']:
        raise ValueError('UCSB course description, units or eligibility changed')
    units = field(article, 'course-units')
    credits = int(units) if units and units.isdigit() else None
    return {'id': PROGRAM_ID, 'courses': [dict(
        id=entry['course_id'], code=code, name=entry['name'],
        description=entry['description'], prerequisites=entry['prerequisites'],
        credits=credits, credit_unit='quarter_hours', category=entry['category'],
        source_id=entry['source_id'], url=entry['url'])], 'requirements': [],
        'notes': [entry['version_note']]}


def attach(namespace):
    for code, entry in SPEC.items():
        if entry['url'] not in namespace['SOURCES']:
            namespace['SOURCES'] += (entry['url'],)
        namespace['SOURCE_PARSERS'][entry['url']] = partial(parse, code=code)
