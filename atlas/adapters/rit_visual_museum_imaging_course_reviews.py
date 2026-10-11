"""Observe the 38 reviewed museum/visual/imaging menu-label observations.

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
TITLES = {s['url']: s['page_title'] for s in MANIFEST['sources']}
# Routing scope only. Reviews/summaries are never runtime output.
LABELS_BY_URL = {url: {c['popup_code']: label for label, c in MANIFEST['courses'].items() if c['url'] == url} for url in SOURCES}


def parse(html, *, url):
    if url not in SOURCE_BY_URL:
        raise ValueError('Unreviewed source URL')
    observed = observe_rules(html, title=TITLES[url])
    bound = {code for table in observed['observed_tables'] for row in table['rows'] for code in row['course_codes']}
    soup = BeautifulSoup(html, 'html.parser')
    courses = []
    associations = []
    for card in soup.select('.courseblock'):
        def value(selector):
            node = card.select_one(selector)
            return (clean(node.get_text(' ', strip=True)) or None) if node else None
        code, title = value('.detail-code'), value('.detail-title')
        label = LABELS_BY_URL[url].get(code)
        if not label or label not in bound or not title:
            raise ValueError('Unbound museum/visual/imaging course card')
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
        body_no_prerequisite = None
        if code in ('MUSE-225', 'MUSE-360'):
            match = re.search(r'The course has no pre-?requisite and is open to students of all majors\.', description)
            body_no_prerequisite = match[0] if match else None
        item.update(description=description, prerequisites=value('.detail-requisites') or body_no_prerequisite)
        notes = ['Published course credit amount: ' + amount + '. No route-total conversion was used.']
        if body_no_prerequisite:
            notes.append('The course description explicitly states: ' + body_no_prerequisite)
        if label != code:
            notes.append('Visible source label ' + label + ' opened actual card ' + code + '; this does not establish additional aliases or split requirements.')
        if not item['prerequisites']:
            notes.append('No prerequisite field is published in this inspected card; this does not establish unrestricted enrollment.')
        for selector in ('.detail-contact_hours', '.detail-ge_attrs', '.detail-typically_offered'):
            text = value(selector)
            if text:
                notes.append(text)
        item['notes'] = notes
        courses.append(item)
        associations.append({'source_label': label, 'popup_code': code, 'source_id': SOURCE_BY_URL[url]['id']})
    if not courses:
        raise ValueError('No rendered assigned course cards')
    if len({c['id'] for c in courses}) != len(courses):
        raise ValueError('Duplicate course cards')
    return {'id': PID, 'courses': courses, 'requirements': [],
            'observed_immersion_tables': observed['observed_tables'],
            'observed_course_label_associations': associations}


def register(sources, parsers):
    from functools import partial
    for url in SOURCES:
        if url not in sources:
            sources.append(url)
        parsers[url] = partial(parse, url=url)
