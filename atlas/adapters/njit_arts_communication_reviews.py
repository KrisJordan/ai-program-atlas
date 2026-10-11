"""Guarded observations for 71 individually reviewed NJIT GER options.

The adjacent manifest holds editorial review evidence, not a runtime audit.
"""
import hashlib
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

from atlas.adapters.national_curriculum_common import clean, course
from atlas.adapters.njit_degree_policies import PID

URL = 'https://catalog.njit.edu/undergraduate/science-liberal-arts/humanities-and-social-sciences/'
SOURCE_ID = PID + '-arts-communication-subject-review'
SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())


def eligibility(text, spec):
    """Keep observed labeled clauses and specifically reviewed exceptions."""
    boundary = spec.get('eligibility_end_before')
    scope = text.split(boundary, 1)[0] if boundary else text
    clauses = re.findall(r'(?:Prerequisites?|Corequisites?|Restrictions?):\s*[^.]+\.?', scope, re.I)
    if 'Departmental approval required.' in text:
        clauses.append('Departmental approval required.')
    clauses.extend(spec.get('extra_eligibility_fragments', []))
    return ' '.join(clauses) or None


def parse(html):
    soup = BeautifulSoup(html, 'html.parser')
    headings = {clean(h.get_text(' ', strip=True)) for h in soup.select('h1')}
    if not {'University Catalog 2026-2027', 'Humanities and Social Sciences'} <= headings:
        raise ValueError('NJIT arts catalog version or chapter identity changed')
    courses, allocations = [], {}
    for block in soup.select('.courseblock'):
        heading = block.select_one('.courseblocktitle')
        match = re.fullmatch(r'([A-Z]+ \d+)\.\s+(.+?)\.\s+(\d+) credits?,.*',
                            clean(heading.get_text(' ', strip=True))) if heading else None
        if not match or match[1] not in SPEC:
            continue
        code, name, credits = match.groups()
        spec = SPEC[code]
        text = clean(block.get_text(' ', strip=True))
        if (name != spec['title'] or
                hashlib.sha256(text.encode()).hexdigest() != spec['digest']):
            raise ValueError('NJIT arts content changed; review required: ' + code)
        c = course('njit', code, name, SOURCE_ID, URL, int(credits),
                   'semester_hours', spec['category'])
        c['description'] = spec['description']
        c['prerequisites'] = eligibility(text, spec)
        courses.append(c)
        if spec.get('ger_allocation_statement'):
            allocations[c['id']] = spec['ger_allocation_statement']
    if {c['code'] for c in courses} != set(SPEC) or len(courses) != len(SPEC):
        raise ValueError('Reviewed NJIT arts identities missing or duplicate')
    return {'id': PID, 'courses': courses, 'requirements': [],
            'observed_ger_allocations': allocations}


def combine(previous, html):
    old, new = previous(html), parse(html)
    if old.get('id') != PID or {c['id'] for c in old.get('courses', [])} & {c['id'] for c in new['courses']}:
        raise ValueError('Overlapping NJIT arts observations')
    return {**old, 'courses': old.get('courses', []) + new['courses'],
            'requirements': old.get('requirements', []) + new['requirements'],
            'observed_ger_allocations': {
                **old.get('observed_ger_allocations', {}), **new['observed_ger_allocations']}}
