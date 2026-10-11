"""Observe individually reviewed BTE blocks; changed text requires fresh review."""
import hashlib
import json
import re
from functools import partial
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.business_society_minors import clean, course

URL = 'https://bulletin.miami.edu/courses-az/bte/'
SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())

def parse(html, pid):
    soup = BeautifulSoup(html, 'html.parser')
    courses = []
    for block in soup.select('.courseblock'):
        title = block.select_one('.courseblocktitle')
        match = re.fullmatch(r'(BTE \d+)\. (.*?)\. ([\d.-]+) Credit Hours\.', clean(title.get_text(' ', strip=True))) if title else None
        if not match or match[1] not in SPEC:
            continue
        code, name, raw = match.groups()
        observed = clean(block.get_text(' ', strip=True))
        entry = SPEC[code]
        if hashlib.sha256(observed.encode()).hexdigest() != entry['digest']:
            raise ValueError('Miami BTE course description changed: ' + code)
        record = course(code, name, pid, pid+'-bte-course-catalog', URL,
                        float(raw) if re.fullmatch(r'\d+(?:\.\d+)?', raw) else None,
                        unit='semester_hours')
        record.update(description=entry['description'], category=entry['category'])
        # Inline links may split prerequisite text; use full block text with
        # published section delimiters, preserving AND/OR rather than resolving it.
        prerequisite = re.search(r'((?:Prerequisite:|Pre-Requisite|Requisite:) .*?)(?= Components:)', observed)
        record['prerequisites'] = prerequisite[1] if prerequisite else None
        courses.append(record)
    if {record['code'] for record in courses} != set(SPEC):
        raise ValueError('Reviewed Miami BTE identities missing')
    return {'id': pid, 'courses': courses}

def register(pid, sources, parsers):
    sources.append(URL)
    parsers[URL] = partial(parse, pid=pid)
