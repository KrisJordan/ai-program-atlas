"""Observe the individually reviewed NJIT humanities/social-science subset."""
import hashlib
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, course, rule
from atlas.adapters.njit_degree_policies import PID

URL = 'https://catalog.njit.edu/undergraduate/science-liberal-arts/humanities-and-social-sciences/'
SOURCE_ID = PID + '-humanities-subject-review'
SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())


def parse(html):
    courses = []
    rules = []
    for block in BeautifulSoup(html, 'html.parser').select('.courseblock'):
        heading = block.select_one('.courseblocktitle')
        match = re.fullmatch(r'([A-Z]+ \d+)\.\s+(.+?)\.\s+(\d+) credits?,.*',
                             clean(heading.get_text(' ', strip=True))) if heading else None
        if not match or match[1] not in SPEC:
            continue
        code, name, credits = match.groups()
        spec = SPEC[code]
        text = clean(block.get_text(' ', strip=True))
        if hashlib.sha256(text.encode()).hexdigest() != spec['digest']:
            raise ValueError('NJIT humanities content changed; review required: ' + code)
        c = course('njit', code, name, SOURCE_ID, URL, int(credits), 'semester_hours', spec['category'])
        c['description'] = spec['description']
        clauses = re.findall(r'(?:Prerequisites?|Restrictions?):\s*[^.]+\.?', text, re.I)
        c['prerequisites'] = ' '.join(clauses) or None
        courses.append(c)
        if spec.get('allocation_condition'):
            rules.append(rule(PID+'-allocation-'+code.lower().replace(' ','-'),
                code+' alternative GER allocation', SOURCE_ID, [c['id']], kind='note',
                summary='Conditional when this option is selected; not an additional course requirement. '+spec['allocation_condition']))
    if {c['code'] for c in courses} != set(SPEC) or len(courses) != len(SPEC):
        raise ValueError('Reviewed NJIT humanities identities missing or duplicate')
    return {'id': PID, 'courses': courses, 'requirements': rules}


def combine(previous, html):
    old = previous(html)
    new = parse(html)
    if old.get('id') != PID or {c['id'] for c in old.get('courses', [])} & {c['id'] for c in new['courses']}:
        raise ValueError('Overlapping NJIT humanities observations')
    return {**old, 'courses': old.get('courses', []) + new['courses'],
            'requirements': old.get('requirements', []) + new['requirements']}
