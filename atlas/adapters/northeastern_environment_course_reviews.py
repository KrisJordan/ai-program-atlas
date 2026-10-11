"""Guarded observations for an explicit ENVR/EEMB primary-review contribution.

The companion manifest contains manual subject decisions, never copied into an
observation as a category_review. Existing program targets restrict this helper's
scope; course eligibility is not converted into degree requirement membership.
"""
import hashlib
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

from atlas.adapters.northeastern_courseleaf import clean

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())
SOURCES = {subject: entry['url'] for subject, entry in SPEC['sources'].items()}


def parse_subject(html, *, program_id, subject, codes=None):
    source = SPEC['sources'][subject]
    entries = SPEC['courses']
    targets = {code: next((t for t in entry['targets'] if t['program_id'] == program_id), None)
               for code, entry in entries.items() if entry['subject'] == subject}
    targets = {code: target for code, target in targets.items() if target}
    requested = list(targets) if codes is None else list(codes)
    if not requested or len(requested) != len(set(requested)) or set(requested) - targets.keys():
        raise ValueError('Course selection outside reviewed program contribution')
    soup = BeautifulSoup(html, 'html.parser')
    site = soup.select_one('#site-title h1')
    content = soup.select_one('#textcontainer')
    if not site or clean(site) != source['heading'] or content is None:
        raise ValueError('Expected Northeastern subject catalog missing')
    if '2026-2027' not in soup.get_text(' ', strip=True):
        raise ValueError('Reviewed Northeastern catalog version missing')
    observed = {}
    for block in content.select('.courseblock'):
        heading = block.select_one('.courseblocktitle')
        if not heading:
            continue
        match = re.fullmatch(r'([A-Z]+ \d+)\.\s+(.+?)\.\s+\((\d+) Hours?\)', clean(heading))
        if not match or match[1] not in entries:
            continue
        code = match[1]
        if code in observed:
            raise ValueError('Duplicate reviewed course identity: ' + code)
        observed[code] = (block, match)
    # Generic accompanying-lab descriptions require their separately read lecture
    # evidence too, including when the caller selects only the laboratory record.
    dependencies = {'EEMB 1102': 'EEMB 1101', 'ENVR 1401': 'ENVR 1400',
                    'ENVR 2311': 'ENVR 2310', 'ENVR 2341': 'ENVR 2340',
                    'ENVR 3301': 'ENVR 3300', 'ENVR 4501': 'ENVR 4500'}
    checked = set(requested) | {dependencies[c] for c in requested if c in dependencies}
    for code in checked:
        if code not in observed:
            raise ValueError('Reviewed course missing: ' + code)
        block, match = observed[code]
        if hashlib.sha256(clean(block).encode()).hexdigest() != entries[code]['block_digest']:
            raise ValueError('Reviewed complete course block changed: ' + code)
    courses, notes = [], []
    for code in requested:
        entry = entries[code]
        block, match = observed[code]
        body = block.select_one('.cb_desc')
        if not body or entry['description_guard'] not in clean(body):
            raise ValueError('Reviewed description missing: ' + code)
        prerequisite = None
        for extra in block.select('.courseblockextra'):
            value = clean(extra)
            if value.startswith('Prerequisite(s):'):
                prerequisite = value.removeprefix('Prerequisite(s):').strip() or None
            elif value.startswith('Corequisite(s):'):
                notes.append(code + ' concurrent corequisite(s): ' + value.removeprefix('Corequisite(s):').strip()
                             + '. This observation does not add degree requirement membership.')
        if code == 'ENVR 3125':
            prerequisite = 'Additional course-description condition: one laboratory science course or permission of instructor.'
        notes.extend(code + ' ' + condition['kind'] + ': ' + condition['summary'] for condition in entry['conditions'])
        courses.append(dict(id=targets[code]['course_id'], code=code, name=match[2],
                            description=entry['description'], credits=int(match[3]),
                            credit_unit='semester_hours', prerequisites=prerequisite,
                            category=entry['category'], source_id=program_id+'-'+subject.lower()+'-courses',
                            url=source['url']))
    return {'id': program_id, 'courses': courses, 'requirements': [], 'notes': notes}
