"""Observe the individually read, explicitly scoped primary-table options."""
import hashlib
import json
import re
from functools import partial
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.business_society_minors import clean, course

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())


def parse(html, pid, key):
    wanted = {code for code, item in SPEC.items()
              if item['key'] == key and pid in item['program_ids']}
    result = []
    for block in BeautifulSoup(html, 'html.parser').select('.courseblock'):
        heading = block.select_one('.courseblocktitle')
        match = re.fullmatch(r'([A-Z]+ \d+)\. (.*?)\. (\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?) Credit Hours?\.',
                             clean(heading.get_text(' ', strip=True))) if heading else None
        if not match or match[1] not in wanted:
            continue
        code, name, raw = match.groups()
        item = SPEC[code]
        text = clean(block.get_text(' ', strip=True))
        if hashlib.sha256(text.encode()).hexdigest() != item['digest']:
            raise ValueError('Miami named option changed; review required: ' + code)
        record = course(code, name, pid, 'miami-named-options-' + key, item['url'],
                        float(raw) if '-' not in raw else None, unit='semester_hours')
        record.update(description=item['description'], category=item['category'])
        if '-' in raw:
            record['description'] += ' Published credit range: ' + raw + ' credit hours; no single per-course amount is asserted.'
        eligibility = re.search(r'((?:Pre-?requisites?(?: or Corequisite)?|Pre/Corequisites?|Requisites?):\s*.*?)(?= Components:)', text, re.I)
        clauses = [eligibility[1]] if eligibility else []
        if item.get('eligibility_note'):
            clauses.append(item['eligibility_note'])
        record['prerequisites'] = ' '.join(clauses) or None
        result.append(record)
    if not wanted or {c['code'] for c in result} != wanted or len(result) != len(wanted):
        raise ValueError('Reviewed Miami named option identities missing or duplicate')
    return {'id': pid, 'courses': result}


def _compose(previous, html, pid, key):
    old = previous(html)
    new = parse(html, pid, key)
    old_ids = [c['id'] for c in old.get('courses', [])]
    if old.get('id') != pid or len(old_ids) != len(set(old_ids)) or set(old_ids) & {c['id'] for c in new['courses']}:
        raise ValueError('Cannot compose overlapping or unrelated Miami observations')
    return {**old, 'courses': old.get('courses', []) + new['courses']}


def register(pid, sources, parsers):
    for key in sorted({item['key'] for item in SPEC.values() if pid in item['program_ids']}):
        url = 'https://bulletin.miami.edu/courses-az/' + key + '/'
        if url not in sources:
            sources.append(url)
        previous = parsers.get(url)
        if getattr(previous, '_miami_named_options', None) == pid:
            continue
        callback = partial(_compose, previous, pid=pid, key=key) if previous else partial(parse, pid=pid, key=key)
        callback._miami_named_options = pid
        parsers[url] = callback
