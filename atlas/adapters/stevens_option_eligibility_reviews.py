"""Bounded public Eligibility observations; no inferred unrestricted admission.

Manual review dispositions and access blockers live in the adjacent manifest.
Only already reviewed, settled tabs can emit course-field observations.
"""
import hashlib
import json
from functools import partial
from pathlib import Path

from bs4 import BeautifulSoup

from atlas.adapters.national_curriculum_common import clean
from atlas.adapters.stevens_degree_course_review import PID, field

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())


def parse(html, code):
    entry = SPEC[code]
    if not entry['review_status'].startswith('reviewed_'):
        raise ValueError('Stevens eligibility has not been reviewed: ' + code)
    soup = BeautifulSoup(html, 'html.parser')
    root = soup.select_one('article.flex-1')
    heading = root.find('h1') if root else None
    titles = [clean(h.get_text(' ', strip=True)) for h in root.select('h2')] if root else []
    if (not heading or clean(heading.get_text(' ', strip=True)) != entry['source_heading']
            or entry['name'] not in titles):
        raise ValueError('Stevens eligibility identity changed: ' + code)
    selected = root.select_one('[role="tab"][aria-selected="true"]')
    if not selected or clean(selected.get_text()) != 'Eligibility':
        raise ValueError('Stevens Eligibility tab is not selected: ' + code)
    labels = [clean(h.get_text()) for h in root.select('h3')]
    expected = ['Student Eligibility Rule'] if entry['eligibility_rule'] is not None else []
    if labels != expected or root.select_one('[aria-busy="true"]'):
        raise ValueError('Stevens eligibility changed or transition unsettled: ' + code)
    value = field(root, 'Student Eligibility Rule')
    digest = hashlib.sha256(value.encode()).hexdigest() if value is not None else None
    if digest != entry['eligibility_digest']:
        raise ValueError('Stevens eligibility rule changed: ' + code)
    # Blank selected tabs cannot clear previously recorded prerequisites. A held
    # course version cannot contribute metadata to the conflicting GE identity.
    if value is None or entry['held']:
        return {'id': PID, 'courses': []}
    prior = entry.get('description_prerequisites')
    prerequisites = prior + ' Published eligibility: ' + value if prior else value
    return {'id': PID, 'courses': [{
        'id': entry['id'], 'code': code, 'prerequisites': prerequisites,
        'source_id': entry['source_id'], 'url': entry['eligibility_url'],
    }]}


def register(sources, parsers):
    for code, entry in SPEC.items():
        if not entry['review_status'].startswith('reviewed_'):
            continue
        url = entry['eligibility_url']
        prior = parsers.get(url)
        if prior is not None:
            if isinstance(prior, partial) and prior.func is parse and prior.keywords == {'code': code}:
                continue
            raise ValueError('Stevens eligibility parser already registered: ' + url)
        if url not in sources:
            sources.append(url)
        parsers[url] = partial(parse, code=code)
