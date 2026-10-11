"""Bounded engineering metadata observations guarded by complete current course blocks.

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


def source_blocks(html, subject=None):
    if subject not in SPEC['sources']:
        raise ValueError('Unreviewed UCSD subject scope')
    source = SPEC['sources'][subject]
    soup = BeautifulSoup(html, 'html.parser')
    if soup.find('input', attrs={'type': 'password'}):
        raise ValueError('Access page is not UCSD course evidence')
    if source['heading'] not in [clean(h.get_text(' ', strip=True)) for h in soup.find_all('h1')]:
        raise ValueError('UCSD course chapter identity changed')
    disclaimers = [p for p in soup.find_all('p') if clean(p.get_text(' ', strip=True)).startswith('For course descriptions not found in the UC San Diego General Catalog')]
    if len(disclaimers) != 1 or source['catalog_year'] not in clean(disclaimers[0].get_text(' ', strip=True)):
        raise ValueError('UCSD catalog edition changed')
    blocks = {}
    for heading in soup.select('p.course-name'):
        title = clean(heading.get_text(' ', strip=True))
        match = re.match(r'((?:' + '|'.join(re.escape(s) for s in source['subjects']) + r') \d+[A-Z]*)\.', title)
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


def chapter_context_hash(html):
    """Guard each section introduction, including future eligibility additions."""
    soup = BeautifulSoup(html, 'html.parser')
    parts = []
    for heading in soup.find_all(['h1', 'h2', 'h3']):
        parts.append(clean(heading.get_text(' ', strip=True)))
        for node in heading.next_siblings:
            if getattr(node, 'name', None) in ['h1', 'h2', 'h3'] or 'course-name' in getattr(node, 'attrs', {}).get('class', []):
                break
            if isinstance(node, Comment) or getattr(node, 'name', None) in ['script', 'style']:
                continue
            value = clean(str(node)) if isinstance(node, NavigableString) else clean(node.get_text(' ', strip=True))
            if value:
                parts.append(value)
    return hashlib.sha256(clean(' '.join(parts)).encode()).hexdigest()


def parse_observations(html, *, subject=None):
    if subject is None:
        soup = BeautifulSoup(html, 'html.parser')
        headings = {clean(h.get_text(' ', strip=True)) for h in soup.find_all('h1')}
        matches = [key for key, source in SPEC['sources'].items() if source['heading'] in headings]
        if len(matches) != 1:
            raise ValueError('Expected one reviewed engineering chapter')
        subject = matches[0]
    blocks = source_blocks(html, subject)
    if chapter_context_hash(html) != SPEC['sources'][subject]['chapter_context_sha256']:
        raise ValueError('Engineering chapter context changed; review required')
    source = SPEC['sources'][subject]
    courses, dispositions = [], []
    for entry in SPEC['entries']:
        if entry['source_key'] != subject:
            continue
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
