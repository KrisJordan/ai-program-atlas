"""Exact-current-code science contribution; observations never certify a review.

The manifest contains separately authored manual taxonomy reviews. Its seven
missing headings are dispositions, not manufactured course records. Chapter
introductions, full heading inventories, section membership and complete bodies
must still match before a reviewed summary can accompany fresh observations.
"""
import hashlib
import json
import re
from functools import partial
from pathlib import Path

from bs4 import BeautifulSoup, Comment, NavigableString

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())
HEADINGS = ['h1', 'h2', 'h3', 'h4']


def clean(value):
    return ' '.join(value.split())


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def following_text(node):
    parts = []
    for sibling in node.next_siblings:
        if getattr(sibling, 'name', None) in HEADINGS or 'course-name' in getattr(sibling, 'attrs', {}).get('class', []):
            break
        if isinstance(sibling, Comment) or getattr(sibling, 'name', None) in ['script', 'style']:
            continue
        value = clean(str(sibling)) if isinstance(sibling, NavigableString) else clean(sibling.get_text(' ', strip=True))
        if value:
            parts.append(value)
    return clean(' '.join(parts))


def chapter_context_hash(soup):
    parts = []
    for heading in soup.find_all(HEADINGS):
        parts.extend([clean(heading.get_text(' ', strip=True)), following_text(heading)])
    return digest(clean(' '.join(parts)))


def section_path(node):
    parts = []
    for heading in node.find_all_previous(HEADINGS):
        level = int(heading.name[1])
        if not parts or level < parts[-1][0]:
            parts.append((level, clean(heading.get_text(' ', strip=True))))
        if level == 1:
            break
    return [value for _, value in reversed(parts)]


def parse_observations(html, *, subject):
    if subject not in SPEC['sources']:
        raise ValueError('Unreviewed UCSD science chapter')
    source = SPEC['sources'][subject]
    soup = BeautifulSoup(html, 'html.parser')
    if soup.find('input', attrs={'type': 'password'}):
        raise ValueError('Access gate is not course evidence')
    if source['heading'] not in [clean(h.get_text(' ', strip=True)) for h in soup.find_all('h1')]:
        raise ValueError('UCSD science chapter identity changed')
    disclaimers = [p for p in soup.find_all('p') if clean(p.get_text(' ', strip=True)).startswith('For course descriptions not found in the UC San Diego General Catalog')]
    if len(disclaimers) != 1 or source['catalog_year'] not in clean(disclaimers[0].get_text(' ', strip=True)):
        raise ValueError('UCSD science catalog edition changed')
    if chapter_context_hash(soup) != source['chapter_context_sha256']:
        raise ValueError('UCSD science chapter context changed')
    headings = soup.select('p.course-name')
    texts = [clean(h.get_text(' ', strip=True)) for h in headings]
    if digest('\n'.join(texts)) != source['heading_inventory_sha256']:
        raise ValueError('UCSD science heading inventory changed')
    courses, dispositions = [], []
    for entry in SPEC['entries']:
        if entry['source_key'] != subject:
            continue
        code = entry['code']
        if not entry['approved_for_integration']:
            # Inventory guard catches newly inserted exact, joint or range headings.
            dispositions.append({'code': code, 'status': 'no_current_heading', 'source_id': source['source_id'], 'url': source['url'], 'catalog_year': source['catalog_year']})
            continue
        matches = [node for node, title in zip(headings, texts) if title == entry['heading']]
        if len(matches) != 1:
            raise ValueError('Expected one exact reviewed heading: ' + code)
        node = matches[0]
        body = following_text(node)
        if section_path(node) != entry['section_path'] or digest(body) != entry['description_hash']:
            raise ValueError('Reviewed UCSD science block or section changed: ' + code)
        credit_match = re.search(r'\((\d+)\)$', entry['heading'])
        if not credit_match or int(credit_match[1]) != entry['credits']:
            raise ValueError('Reviewed scalar credit observation changed')
        prerequisite_parts = body.split('Prerequisites:', 1)
        courses.append({
            'id': entry['id'], 'code': code, 'name': entry['name'],
            'description': entry['description'],
            'prerequisites': prerequisite_parts[1].strip() if len(prerequisite_parts) == 2 else None,
            'credits': int(credit_match[1]), 'credit_unit': 'quarter_hours',
            'source_id': source['source_id'], 'url': source['url'], 'notes': entry['notes'],
        })
    return {'id': SPEC['program_id'], 'courses': courses, 'source_dispositions': dispositions}


SOURCE_PARSERS = {source['url']: partial(parse_observations, subject=key) for key, source in SPEC['sources'].items()}
