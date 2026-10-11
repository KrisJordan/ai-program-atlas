"""Observe individually read HIST course blocks, excluding title-only Rutgers rows."""
import hashlib
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, course
from atlas.adapters.njit_degree_policies import PID

URL = 'https://catalog.njit.edu/undergraduate/science-liberal-arts/history/'
SOURCE_ID = PID + '-history-subject-review'
SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())


def parse(html):
    courses = []
    for block in BeautifulSoup(html, 'html.parser').select('.courseblock'):
        heading = block.select_one('.courseblocktitle')
        match = re.fullmatch(r'(HIST \d+)\.\s+(.+?)\.\s+(\d+) credits?,.*',
                             clean(heading.get_text(' ', strip=True))) if heading else None
        if not match or match[1] not in SPEC:
            continue
        code, name, credits = match.groups()
        spec = SPEC[code]
        text = clean(block.get_text(' ', strip=True))
        if hashlib.sha256(text.encode()).hexdigest() != spec['digest']:
            raise ValueError('NJIT history content changed; review required: ' + code)
        c = course('njit', code, name, SOURCE_ID, URL, int(credits), 'semester_hours', spec['category'])
        c['description'] = spec['description']
        clauses = re.findall(r'(?:Prerequisites?|Restrictions?):\s*[^.]+\.?', text, re.I)
        c['prerequisites'] = ' '.join(clauses) or None
        courses.append(c)
    if {c['code'] for c in courses} != set(SPEC) or len(courses) != len(SPEC):
        raise ValueError('Reviewed NJIT history identities missing or duplicate')
    return {'id': PID, 'courses': courses}
