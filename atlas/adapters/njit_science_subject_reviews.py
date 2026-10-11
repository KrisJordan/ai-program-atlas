"""Content observations for individually read NJIT science GER options."""
import hashlib
import json
import re
from functools import partial
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, course
from atlas.adapters.njit_degree_policies import PID

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())


def parse(html, key):
    wanted = {code for code, item in SPEC.items() if item['key'] == key}
    courses = []
    for block in BeautifulSoup(html, 'html.parser').select('.courseblock'):
        heading = block.select_one('.courseblocktitle')
        match = re.fullmatch(r'([A-Z]+ \d+[A-Z]?)\.\s+(.+?)\.\s+(\d+) credits?,.*',
                             clean(heading.get_text(' ', strip=True))) if heading else None
        if not match or match[1] not in wanted:
            continue
        code, name, credits = match.groups()
        item = SPEC[code]
        text = clean(block.get_text(' ', strip=True))
        if hashlib.sha256(text.encode()).hexdigest() != item['digest']:
            raise ValueError('NJIT science content changed; review required: ' + code)
        c = course('njit', code, name, PID + '-science-subject-' + key, item['url'],
                   credits=int(credits), unit='semester_hours', category=item['category'])
        c['description'] = item['description']
        clauses = re.findall(r'((?:Pre|Co-?)requisites?:\s*.*?)(?:\.\s|\.$|$)', text, re.I)
        c['prerequisites'] = '; '.join(clean(x) for x in clauses) or None
        courses.append(c)
    if not wanted or {c['code'] for c in courses} != wanted or len(courses) != len(wanted):
        raise ValueError('Reviewed NJIT science content identities missing or duplicate')
    return {'id': PID, 'courses': courses}


def _compose(previous, html, key):
    old = previous(html)
    new = parse(html, key)
    if old.get('id') != PID:
        raise ValueError('Wrong program in NJIT science observations')
    courses = {c['id']: c for c in old.get('courses', [])}
    if len(courses) != len(old.get('courses', [])):
        raise ValueError('Duplicate NJIT science observations')
    # Deliberate metadata enrichment of the same source identities; keep the
    # original conditional laboratory requirement nodes without adding copies.
    for c in new['courses']:
        courses[c['id']] = {**courses.get(c['id'], {}), **c}
    return {**old, 'courses': list(courses.values())}


def register(parsers):
    for key in sorted({item['key'] for item in SPEC.values()}):
        url = next(item['url'] for item in SPEC.values() if item['key'] == key)
        parsers[url] = partial(_compose, parsers[url], key=key)
