"""Current exact-code observations for manually reviewed Maryland course blocks.

Topic-specific rows never inherit their generic parent block. Observations do not
carry the manual subject-review certification or completeness status.
"""
from functools import partial
import hashlib
import json
from pathlib import Path
import re
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean
from atlas.adapters.cmu_bs.common import course

BASE = 'https://academiccatalog.umd.edu/undergraduate/approved-courses/'
SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())
TARGETS = json.loads(Path(__file__).with_name('maryland_full_course_targets.json').read_text())


def parse(html, *, pid, prefix, codes):
    soup = BeautifulSoup(html, 'html.parser')
    h1 = soup.find('h1')
    if h1 is None or not clean(h1.get_text()).startswith(prefix.upper() + ' - '):
        raise ValueError('Maryland subject heading changed: ' + prefix)
    found = {}
    for block in soup.select('.courseblock'):
        title = block.select_one('.courseblocktitle')
        if title is None:
            continue
        match = re.fullmatch(r'([A-Z]+\d+[A-Z]?) (.+) \(([^()]+) Credits?\)', clean(title.get_text(' ', strip=True)))
        if not match or match[1] not in codes:
            continue
        code, name, amount = match.groups()
        if code in found:
            raise ValueError('Duplicate Maryland exact course: ' + code)
        entry = SPEC[code]
        observed = clean(block.get_text(' ', strip=True))
        if hashlib.sha256(observed.encode()).hexdigest() != entry['digest']:
            raise ValueError('Maryland reviewed block changed; manual review required: ' + code)
        c = course(code, name, pid + '-courses-' + prefix, BASE + prefix + '/',
                   institution='umd', unit='semester_hours',
                   credits=int(amount) if amount.isdigit() else None,
                   category=entry['category'])
        c['description'] = entry['description']
        clauses = []
        for extra in block.select('.courseblockextra'):
            label = extra.find('strong')
            if label and clean(label.get_text()).rstrip(':') in {
                'Prerequisite', 'Corequisite', 'Restriction', 'Credit Only Granted for',
                'Additional Information', 'Recommended', 'Repeatable to',
            }:
                clauses.append(clean(extra.get_text(' ', strip=True)))
        if not amount.isdigit():
            clauses.append('Published credit range: ' + amount + '; no scalar amount inferred.')
        c['prerequisites'] = ' '.join(clauses) or None
        found[code] = c
    if set(found) != set(codes):
        raise ValueError('Reviewed Maryland exact courses missing: ' + ', '.join(sorted(set(codes) - set(found))))
    return {'id': pid, 'courses': list(found.values())}


def parsers(pid):
    return {BASE + prefix + '/': partial(parse, pid=pid, prefix=prefix, codes=codes)
            for prefix, codes in TARGETS[pid].items()}
