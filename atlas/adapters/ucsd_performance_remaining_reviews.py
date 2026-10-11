"""Source-guarded observations for 103 formerly code-only UCSD art records.

Manual content reviews live only in the adjacent manifest. Neither this parser
nor code membership certifies requirement roles, cross-list identity or access.
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


def _text(node):
    if isinstance(node, Comment) or getattr(node, 'name', None) in ('script', 'style'):
        return ''
    return clean(str(node) if isinstance(node, NavigableString) else node.get_text(' ', strip=True))


def chapter_context_hash(html):
    soup = BeautifulSoup(html, 'html.parser')
    parts = []
    for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
        parts.append(clean(heading.get_text(' ', strip=True)))
        for node in heading.next_siblings:
            if getattr(node, 'name', None) in ('h1', 'h2', 'h3', 'h4') or 'course-name' in getattr(node, 'attrs', {}).get('class', []):
                break
            value = _text(node)
            if value:
                parts.append(value)
    return hashlib.sha256(clean(' '.join(parts)).encode()).hexdigest()


def source_blocks(html, subject):
    if subject not in SPEC['sources']:
        raise ValueError('Unreviewed performance chapter')
    source = SPEC['sources'][subject]
    soup = BeautifulSoup(html, 'html.parser')
    if soup.find('input', attrs={'type': 'password'}):
        raise ValueError('Access page is not course evidence')
    if source['heading'] not in [clean(h.get_text(' ', strip=True)) for h in soup.find_all('h1')]:
        raise ValueError('UCSD chapter identity changed')
    disclaimers = [p for p in soup.find_all('p') if clean(p.get_text(' ', strip=True)).startswith('For course descriptions not found in the UC San Diego General Catalog')]
    if len(disclaimers) != 1 or source['catalog_year'] not in clean(disclaimers[0].get_text(' ', strip=True)):
        raise ValueError('UCSD catalog edition changed')
    blocks = {}
    for heading in soup.select('p.course-name'):
        title = clean(heading.get_text(' ', strip=True))
        match = re.match(r'([A-Z]+ \d+[A-Z]*)\.', title)
        # This is the one explicitly read shared heading in this assigned set.
        # Never generically expand ranges or infer aliases from a hyphen.
        if title.startswith('MUS 2A-B-C.'):
            identifiers = ['MUS 2A', 'MUS 2B', 'MUS 2C']
        elif match:
            identifiers = [match[1]]
        else:
            continue
        if any(code.split()[0] not in source['subjects'] for code in identifiers):
            continue
        parts = []
        for node in heading.next_siblings:
            if getattr(node, 'name', None) in ('h1', 'h2', 'h3', 'h4') or 'course-name' in getattr(node, 'attrs', {}).get('class', []):
                break
            value = _text(node)
            if value:
                parts.append(value)
        section = heading.find_previous(['h2', 'h3', 'h4'])
        section_text = clean(section.get_text(' ', strip=True)) if section else None
        for code in identifiers:
            if code in blocks:
                raise ValueError('Duplicate course identity: ' + code)
            blocks[code] = (title, clean(' '.join(parts)), section_text)
    return blocks


def parse_observations(html, *, subject):
    blocks = source_blocks(html, subject)
    source = SPEC['sources'][subject]
    if chapter_context_hash(html) != source['chapter_context_sha256']:
        raise ValueError('Chapter context changed; review required')
    courses, dispositions = [], []
    for entry in SPEC['entries']:
        if entry['source_key'] != subject:
            continue
        code = entry['code']
        if entry['heading'] is None:
            if code in blocks:
                raise ValueError('Previously unmatched identifier appeared: ' + code)
            dispositions.append(dict(code=code, status='no_current_heading'))
            continue
        heading, body, section = blocks.get(code, (None, '', None))
        if section != entry['section'] or heading != entry['heading'] or hashlib.sha256(body.encode()).hexdigest() != entry['description_hash']:
            raise ValueError('Reviewed course source changed: ' + code)
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
