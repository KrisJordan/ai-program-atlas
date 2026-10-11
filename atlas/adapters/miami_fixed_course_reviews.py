"""Observe reviewed fixed-course blocks without extending cognate/option scope."""
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
    courses = []
    for block in BeautifulSoup(html, 'html.parser').select('.courseblock'):
        heading = block.select_one('.courseblocktitle')
        match = re.fullmatch(r'([A-Z]+ \d+)\. (.*?)\. (\d+(?:\.\d+)?) Credit Hours\.',
                             clean(heading.get_text(' ', strip=True))) if heading else None
        if not match or match[1] not in wanted:
            continue
        code, name, credits = match.groups()
        item = SPEC[code]
        text = clean(block.get_text(' ', strip=True))
        if hashlib.sha256(text.encode()).hexdigest() != item['digest']:
            raise ValueError('Miami fixed course changed; review required: ' + code)
        record = course(code, name, pid, 'miami-fixed-courses-' + key,
                        item['url'], float(credits), unit='semester_hours')
        record.update(description=item['description'], category=item['category'])
        # Preserve the entire original eligibility expression, including plural
        # labels, absent spaces, AND/OR precedence and concurrent alternatives.
        eligibility = re.search(r'((?:Prerequisites?|Pre/Corequisites?|Requisite):\s*.*?)(?= Components:)', text)
        clauses = [eligibility[1]] if eligibility else []
        if item.get('eligibility_note'):
            clauses.append(item['eligibility_note'])
        record['prerequisites'] = ' '.join(clauses) or None
        courses.append(record)
    if not wanted or {c['code'] for c in courses} != wanted or len(courses) != len(wanted):
        raise ValueError('Reviewed Miami fixed course identities missing or duplicate')
    return {'id': pid, 'courses': courses}


def register(pid, sources, parsers):
    for key in sorted({item['key'] for item in SPEC.values() if pid in item['program_ids']}):
        url = 'https://bulletin.miami.edu/courses-az/' + key + '/'
        sources.append(url)
        parsers[url] = partial(parse, pid=pid, key=key)
