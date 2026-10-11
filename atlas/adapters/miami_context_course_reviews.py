"""Exact-source observations for manually reviewed contextual Miami courses.

Course content review does not promote contextual cognate membership into a
primary-table option or grant credit/enrollment eligibility.
"""
import hashlib
import json
import re
from functools import partial
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.business_society_minors import clean, course

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())


def parse(html, *, pid, key):
    wanted = {code: item for code, item in SPEC['courses'].items()
              if item['key'] == key and pid in item['program_ids']}
    if not wanted:
        raise ValueError('Unreviewed Miami contextual source/program scope')
    soup = BeautifulSoup(html, 'html.parser')
    heading = soup.find('h1')
    if not heading or clean(heading.get_text(' ', strip=True)) != SPEC['sources'][key]['heading']:
        raise ValueError('Miami contextual chapter identity changed')
    courses = []
    for block in soup.select('.courseblock'):
        title = block.select_one('.courseblocktitle')
        if not title:
            continue
        text = clean(title.get_text(' ', strip=True))
        code = text.split('.')[0]
        if code not in wanted:
            continue
        item = wanted[code]
        if hashlib.sha256(clean(block.get_text(' ', strip=True)).encode()).hexdigest() != item['block_hash']:
            raise ValueError('Miami contextual course changed; review required: ' + code)
        match = re.fullmatch(r'([A-Z]+ \d+)\. (.*?)\. (\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?) Credit Hours?\.', text)
        if not match or match[2] != item['name']:
            raise ValueError('Miami contextual course identity/credit format changed')
        record = course(code, match[2], pid, 'miami-context-courses-' + key, item['url'],
                        float(match[3]) if '-' not in match[3] else None, unit='semester_hours')
        record.update(description=item['description'], prerequisites=item['prerequisites'], category=item['category'])
        courses.append(record)
    if len(courses) != len(wanted) or {c['code'] for c in courses} != set(wanted):
        raise ValueError('Missing or duplicate Miami contextual course identities')
    return {'id': pid, 'courses': courses}


def _compose(previous, html, *, pid, key):
    old = previous(html)
    new = parse(html, pid=pid, key=key)
    records = old.get('courses', [])
    if old.get('id') != pid or len({c['id'] for c in records}) != len(records):
        raise ValueError('Invalid prior Miami course observations')
    merged = {c['id']: c for c in records}
    for record in new['courses']:
        before = merged.get(record['id'])
        if before and before['code'] != record['code']:
            raise ValueError('Conflicting Miami course identity')
        merged[record['id']] = {**(before or {}), **record}
    return {**old, 'courses': list(merged.values())}


def register(pid, sources, parsers):
    keys = {item['key'] for item in SPEC['courses'].values() if pid in item['program_ids']}
    for key in sorted(keys):
        url = SPEC['sources'][key]['url']
        if url not in sources:
            sources.append(url)
        previous = parsers.get(url)
        if getattr(previous, '_miami_context_courses', None) == pid:
            continue
        callback = partial(_compose, previous, pid=pid, key=key) if previous else partial(parse, pid=pid, key=key)
        callback._miami_context_courses = pid
        parsers[url] = callback
