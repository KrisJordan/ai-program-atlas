"""Observe the 12 reviewed policy public course cards.

Only rendered, source-bound cards are observations. Loading an ordinary HTTP
shell cannot replay these manually reviewed courses or their subject judgments.
The primary adapter owner composes this observer with the existing route parser.
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
TITLES = dict(zip(SOURCES, ('Climate Change: An Interdisciplinary Problem Immersion', 'Public Policy Immersion')))
# Routing scope only. Reviews/summaries are never runtime output.
CODES_BY_URL = {url: {code for code, c in MANIFEST['courses'].items() if c['url'] == url} for url in SOURCES}


def parse(html, *, url):
    if url not in SOURCE_BY_URL:
        raise ValueError('Unreviewed source URL')
    observed = observe_rules(html, title=TITLES[url])
    bound = {code for table in observed['observed_tables'] for row in table['rows'] for code in row['course_codes']}
    soup = BeautifulSoup(html, 'html.parser')
    courses = []
    for card in soup.select('.courseblock'):
        def value(selector):
            node = card.select_one(selector)
            return (clean(node.get_text(' ', strip=True)) or None) if node else None
        code, title = value('.detail-code'), value('.detail-title')
        if code not in CODES_BY_URL[url] or code not in bound or not title:
            raise ValueError('Unbound policy course card')
        description = value('.courseblockextra')
        if not description:
            raise ValueError('Settled full course description required')
        amount = value('.detail-hours_html')
        fixed = re.fullmatch(r'\((\d+(?:\.\d+)?) Credits?\)', amount or '')
        variable = re.fullmatch(r'\((\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?) Credits?\)', amount or '')
        if not fixed and not variable:
            raise ValueError('Missing or unrecognized course credit format')
        if variable and float(variable[1]) > float(variable[2]):
            raise ValueError('Reversed course credit range')
        item = course(PID, code, title, SOURCE_BY_URL[url]['id'], url, float(fixed[1]) if fixed else None)
        item.update(description=description, prerequisites=value('.detail-requisites'))
        notes = ['Published course credit amount: ' + amount + '. No route-total conversion was used.']
        if not item['prerequisites']:
            notes.append('No prerequisite field is published in this inspected card; this does not establish unrestricted enrollment.')
        for selector in ('.detail-contact_hours', '.detail-ge_attrs', '.detail-typically_offered'):
            text = value(selector)
            if text:
                notes.append(text)
        item['notes'] = notes
        courses.append(item)
    if not courses:
        raise ValueError('No rendered assigned course cards')
    if len({c['id'] for c in courses}) != len(courses):
        raise ValueError('Duplicate course cards')
    return {'id': PID, 'courses': courses, 'requirements': [],
            'observed_immersion_tables': observed['observed_tables']}
