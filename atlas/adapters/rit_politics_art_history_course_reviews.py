"""Observe the 62 reviewed politics and art-history public course cards.

The manual manifest routes observations only. It is never replayed as freshly
fetched metadata, and no manual taxonomy decision is emitted by this observer.
"""
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, course
from atlas.adapters.rit_immersion_rule_observer import parse as observe_rules
from atlas.adapters.rit_writing_closure import PID

MANIFEST = json.loads(Path(__file__).with_suffix('.json').read_text())
SOURCES = [s['url'] for s in MANIFEST['sources']]
SOURCE_BY_URL = {s['url']: s for s in MANIFEST['sources']}
TITLES = {s['url']: s['title'].split(' — actual public course cards')[0] for s in MANIFEST['sources']}
CODES_BY_URL = {url: {code for code, c in MANIFEST['courses'].items() if c['url'] == url} for url in SOURCES}


def parse(html, *, url):
    if url not in SOURCE_BY_URL:
        raise ValueError('Unreviewed politics/art-history route URL')
    observed = observe_rules(html, title=TITLES[url])
    bound = {c for t in observed['observed_tables'] for r in t['rows'] for c in r['course_codes']}
    soup = BeautifulSoup(html, 'html.parser')
    courses = []
    for card in soup.select('.courseblock'):
        def value(selector):
            node = card.select_one(selector)
            return (clean(node.get_text(' ', strip=True)) or None) if node else None
        code, title = value('.detail-code'), value('.detail-title')
        if code not in CODES_BY_URL[url] or code not in bound or not title:
            raise ValueError('Unbound politics/art-history course card')
        description = value('.courseblockextra')
        if not description or description.startswith('Loading course description'):
            raise ValueError('Settled course description required')
        amount = value('.detail-hours_html') or ''
        fixed = re.fullmatch(r'\((\d+(?:\.\d+)?) Credits?\)', amount)
        variable = re.fullmatch(r'\((\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?) Credits?\)', amount)
        if not fixed and not variable:
            raise ValueError('Unrecognized course credit format')
        if variable and float(variable[1]) > float(variable[2]):
            raise ValueError('Reversed course credit range')
        item = course(PID, code, title, SOURCE_BY_URL[url]['id'], url, float(fixed[1]) if fixed else None)
        item.update(description=description, prerequisites=value('.detail-requisites'))
        item['notes'] = ['Published course credit amount: '+amount+'. No route-total conversion was used.']
        if not item['prerequisites']:
            item['notes'].append('No separate prerequisite field is published in this card; this does not establish unrestricted enrollment.')
        for selector in ('.detail-contact_hours','.detail-ge_attrs','.detail-typically_offered'):
            text = value(selector)
            if text:
                item['notes'].append(text)
        courses.append(item)
    if not courses or len({c['id'] for c in courses}) != len(courses):
        raise ValueError('Missing or duplicate rendered politics/art-history cards')
    return {'id':PID,'courses':courses,'requirements':[],
            'observed_immersion_tables':observed['observed_tables']}


def register(sources, parsers):
    from functools import partial
    for url in SOURCES:
        if url not in sources:
            sources.append(url)
        parsers[url] = partial(parse, url=url)
