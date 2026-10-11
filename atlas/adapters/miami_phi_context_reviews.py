"""Guarded observations for the separately reviewed Miami Philosophy context set.

The manifest holds manual subject reviews. Runtime observations never certify
those reviews or promote contextual membership into a degree requirement.
"""
import hashlib
import json
import re
from functools import partial
from pathlib import Path

from bs4 import BeautifulSoup
from atlas.adapters.business_society_minors import clean, course

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())
URL = SPEC['sources']['phi']['url']
SOURCE_ID = 'miami-context-courses-phi'


def parse(html, *, pid):
    wanted = {code: item for code, item in SPEC['courses'].items()
              if pid in item['program_ids']}
    if not wanted:
        raise ValueError('Unreviewed Miami Philosophy program scope')
    soup = BeautifulSoup(html, 'html.parser')
    heading = soup.find('h1')
    if not heading or clean(heading.get_text(' ', strip=True)) != SPEC['sources']['phi']['heading']:
        raise ValueError('Miami Philosophy chapter identity changed')
    inventory = sorted(clean(title.get_text(' ', strip=True)).split('.')[0]
                       for title in soup.select('.courseblock .courseblocktitle'))
    missing = {code: item for code, item in SPEC['missing_courses'].items()
               if pid in item['program_ids']}
    if set(inventory) & set(missing):
        raise ValueError('Previously missing Philosophy course now appears; review required')
    if hashlib.sha256('\n'.join(inventory).encode()).hexdigest() != SPEC['sources']['phi']['course_code_inventory_hash']:
        raise ValueError('Philosophy chapter inventory changed; missing-code review required')
    records, ranges, seen = [], {}, set()
    for block in soup.select('.courseblock'):
        title = block.select_one('.courseblocktitle')
        if title is None:
            continue
        label = clean(title.get_text(' ', strip=True))
        code = label.split('.')[0]
        if code not in wanted:
            continue
        if code in seen:
            raise ValueError('Duplicate Miami Philosophy course: ' + code)
        seen.add(code)
        entry = wanted[code]
        digest = hashlib.sha256(clean(block.get_text(' ', strip=True)).encode()).hexdigest()
        if digest != entry['block_hash']:
            raise ValueError('Miami Philosophy course changed; review required: ' + code)
        match = re.fullmatch(r'([A-Z]+ \d+)\. (.*?)\. (\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?) Credit Hours?\.', label)
        if not match or match[2] != entry['name']:
            raise ValueError('Miami Philosophy course identity/credits changed')
        amount = float(match[3]) if '-' not in match[3] else None
        record = course(code, match[2], pid, SOURCE_ID, URL, amount,
                        unit=entry['credit_unit'])
        record.update(description=entry['description'], prerequisites=entry['prerequisites'],
                      category=entry['category'])
        records.append(record)
        if amount is None:
            lo, hi = map(float, match[3].split('-'))
            ranges[code] = {'minimum': lo, 'maximum': hi, 'credit_unit': entry['credit_unit']}
    if seen != set(wanted):
        raise ValueError('Missing reviewed Miami Philosophy course identities')
    return {'id': pid, 'courses': records, 'observed_credit_ranges': ranges,
            'observed_missing_courses': {c: {'source_url': URL, 'scope': 'No exact block in this inspected chapter'} for c in missing}}


def _compose(previous, html, *, pid):
    old = previous(html)
    new = parse(html, pid=pid)
    records = old.get('courses', [])
    if old.get('id') != pid or len({c['id'] for c in records}) != len(records):
        raise ValueError('Invalid prior Miami Philosophy observations')
    merged = {c['id']: c for c in records}
    for record in new['courses']:
        before = merged.get(record['id'])
        if before and before['code'] != record['code']:
            raise ValueError('Conflicting Miami Philosophy course identity')
        merged[record['id']] = {**(before or {}), **record}
    return {**old, 'courses': list(merged.values()), 'observed_credit_ranges': {
        **old.get('observed_credit_ranges', {}), **new['observed_credit_ranges']},
        'observed_missing_courses': {**old.get('observed_missing_courses', {}), **new['observed_missing_courses']}}


def register(pid, sources, parsers):
    if not any(pid in c['program_ids'] for c in SPEC['courses'].values()):
        raise ValueError('Unreviewed Miami Philosophy program scope')
    if URL not in sources:
        sources.append(URL)
    previous = parsers.get(URL)
    if getattr(previous, '_miami_phi_context', None) == pid:
        return
    callback = (partial(_compose, previous, pid=pid) if previous
                else partial(parse, pid=pid))
    callback._miami_phi_context = pid
    parsers[URL] = callback
