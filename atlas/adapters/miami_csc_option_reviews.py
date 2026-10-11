"""Observe reviewed Miami CSC option blocks; source changes require renewed review."""
import hashlib
import json
import re
from functools import partial
from pathlib import Path

from bs4 import BeautifulSoup
from atlas.adapters.business_society_minors import clean, course

URL = 'https://bulletin.miami.edu/courses-az/csc/'
SOURCE_ID = 'miami-csc-option-course-catalog'
SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())


def parse(html, pid):
    wanted = {code for code, entry in SPEC.items() if pid in entry['program_ids']}
    soup = BeautifulSoup(html, 'html.parser')
    if not any(clean(h.get_text(' ', strip=True)) == 'Computer Science (CSC)'
               for h in soup.find_all(['h1', 'h2'])):
        raise ValueError('Miami CSC directory heading missing')
    courses = []
    ranges = {}
    for block in soup.select('.courseblock'):
        heading = block.select_one('.courseblocktitle')
        match = re.fullmatch(
            r'(CSC \d+)\. (.*?)\. (\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?) Credit Hours?\.',
            clean(heading.get_text(' ', strip=True))) if heading else None
        if not match or match[1] not in wanted:
            continue
        code, name, raw = match.groups()
        entry = SPEC[code]
        observed = clean(block.get_text(' ', strip=True))
        if hashlib.sha256(observed.encode()).hexdigest() != entry['digest']:
            raise ValueError('Miami CSC option course changed; review required: ' + code)
        amount = float(raw) if '-' not in raw else None
        record = course(code, name, pid, SOURCE_ID, URL, amount, unit='semester_hours')
        record.update(description=entry['description'], category=entry['category'])
        eligibility = re.search(
            r'((?:Prerequisites?|Pre/Corequisites?|Requisite):\s*.*?)(?= Components:)', observed)
        record['prerequisites'] = eligibility[1] if eligibility else None
        if '-' in raw:
            low, high = map(float, raw.split('-'))
            ranges[code] = {'minimum': low, 'maximum': high, 'credit_unit': 'semester_hours'}
        courses.append(record)
    if not wanted or len(courses) != len(wanted) or {c['code'] for c in courses} != wanted:
        raise ValueError('Reviewed Miami CSC option identities missing or duplicate')
    return {'id': pid, 'courses': courses, 'observed_credit_ranges': ranges}


def _compose(previous, html, pid):
    old = previous(html)
    new = parse(html, pid)
    if old.get('id') != pid:
        raise ValueError('Cannot compose Miami observations for different programs')
    old_ids = [c['id'] for c in old.get('courses', [])]
    new_ids = [c['id'] for c in new['courses']]
    if len(old_ids) != len(set(old_ids)) or set(old_ids) & set(new_ids):
        raise ValueError('Duplicate Miami course identity across CSC observers')
    old_ranges = old.get('observed_credit_ranges', {})
    if set(old_ranges) & set(new['observed_credit_ranges']):
        raise ValueError('Duplicate Miami observed credit range')
    return {**old, 'courses': old.get('courses', []) + new['courses'],
            'observed_credit_ranges': {**old_ranges, **new['observed_credit_ranges']}}


def register(pid, sources, parsers):
    """Register after the fixed-course helper, composing its same-URL response."""
    if not any(pid in entry['program_ids'] for entry in SPEC.values()):
        return
    if URL not in sources:
        sources.append(URL)
    previous = parsers.get(URL)
    if getattr(previous, '_miami_csc_options_program', None) == pid:
        return
    callback = partial(_compose, previous, pid=pid) if previous else partial(parse, pid=pid)
    callback._miami_csc_options_program = pid
    parsers[URL] = callback
