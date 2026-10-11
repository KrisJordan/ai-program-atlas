"""Bounded ANAR metadata observations guarded by complete current course blocks.

Manual taxonomy reviews and version holds remain in the manifest for primary
integration. This helper cannot certify requirements, reviews or equivalence.
"""
import hashlib
import json
import re
from functools import partial
from pathlib import Path

from bs4 import BeautifulSoup, Comment, NavigableString

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())


def clean(value):
    return ' '.join(value.split())


def source_blocks(html, subject='ANAR'):
    if subject not in SPEC['sources']:
        raise ValueError('Unreviewed UCSD subject scope')
    source = SPEC['sources'][subject]
    soup = BeautifulSoup(html, 'html.parser')
    if soup.find('input', attrs={'type': 'password'}):
        raise ValueError('Access page is not UCSD course evidence')
    if source['heading'] not in [clean(h.get_text(' ', strip=True)) for h in soup.find_all('h1')]:
        raise ValueError('UCSD course chapter identity changed')
    disclaimer = soup.select_one('.course-disclaimer')
    if disclaimer is None or source['catalog_year'] not in clean(disclaimer.get_text(' ', strip=True)):
        raise ValueError('UCSD catalog edition changed')
    blocks = {}
    for heading in soup.select('p.course-name'):
        title = clean(heading.get_text(' ', strip=True))
        match = re.match(r'(' + re.escape(subject) + r' \d+[A-Z]*)\.', title)
        if not match:
            continue
        code = match[1]
        if code in blocks:
            raise ValueError('Duplicate UCSD course heading: ' + code)
        parts = []
        for sibling in heading.next_siblings:
            classes = getattr(sibling, 'attrs', {}).get('class', [])
            if getattr(sibling, 'name', None) in ['h1', 'h2', 'h3'] or 'course-name' in classes:
                break
            if isinstance(sibling, Comment) or getattr(sibling, 'name', None) in ['script', 'style']:
                continue
            if isinstance(sibling, NavigableString):
                value = clean(str(sibling))
            else:
                value = clean(sibling.get_text(' ', strip=True))
            if value:
                parts.append(value)
        blocks[code] = (title, clean(' '.join(parts)))
    return blocks


def parse_observations(html, *, subject='ANAR'):
    blocks = source_blocks(html, subject)
    source = SPEC['sources'][subject]
    courses, dispositions = [], []
    for entry in SPEC['entries']:
        code = entry['code']
        if entry['heading'] is None:
            if code in blocks:
                raise ValueError('Previously unmatched UCSD identifier appeared: ' + code)
            dispositions.append(dict(code=code, status='no_current_heading'))
            continue
        heading, body = blocks.get(code, (None, ''))
        if heading != entry['heading'] or hashlib.sha256(body.encode()).hexdigest() != entry['description_hash']:
            raise ValueError('Reviewed UCSD course source changed: ' + code)
        if not entry['approved_for_integration']:
            dispositions.append(dict(code=code, status='source_title_conflict', observed_name=entry['name']))
            continue
        prerequisites = re.split(r'Prerequisites\s*:', body, maxsplit=1)
        courses.append(dict(
            id=entry['id'], code=code, name=entry['name'], description=entry['description'],
            prerequisites=prerequisites[1].strip() if len(prerequisites) == 2 else None,
            credits=entry['credits'], credit_unit='quarter_hours', category=entry['category'],
            source_id=source['source_id'], url=source['url'], notes=entry['notes'],
        ))
    return dict(id=SPEC['program_id'], courses=courses, source_dispositions=dispositions)


SOURCE_PARSERS = {
    source['url']: partial(parse_observations, subject=subject)
    for subject, source in SPEC['sources'].items()
}
