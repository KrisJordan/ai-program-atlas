"""Manually reviewed CSE summaries guarded by the complete source field.

This helper observes course facts only. The program owner must deliberately
apply category_review from the manifest; a scraper cannot certify that review.
It neither changes requirement membership nor infers course equivalence.
"""
import hashlib
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())
URL = SPEC['source_url']


def normalized(value):
    return ' '.join(value.split())


def source_blocks(html):
    soup = BeautifulSoup(html, 'html.parser')
    headings = [normalized(h.get_text(' ', strip=True)) for h in soup.select('h1')]
    if 'Computer Science and Engineering (CSE)' not in headings:
        raise ValueError('UCSD CSE chapter identity changed')
    blocks = {}
    for heading in soup.select('p.course-name'):
        text = normalized(heading.get_text(' ', strip=True))
        match = re.match(r'(CSE \d+[A-Z]*)\.', text)
        if not match:
            continue
        parts = []
        for sibling in heading.next_siblings:
            if getattr(sibling, 'name', None) in ('h1', 'h2', 'h3'):
                break
            classes = getattr(sibling, 'attrs', {}).get('class', [])
            if 'course-name' in classes:
                break
            if 'course-descriptions' in classes:
                parts.append(normalized(sibling.get_text(' ', strip=True)))
        code = match[1]
        if code in blocks:
            raise ValueError('Duplicate UCSD CSE heading: ' + code)
        blocks[code] = (text, normalized(' '.join(parts)))
    return blocks


def parse_observations(html):
    """Fail atomically on new, missing or changed reviewed course content."""
    blocks = source_blocks(html)
    courses = []
    for entry in SPEC['entries']:
        code = entry['code']
        if entry['heading'] is None:
            if code in blocks:
                raise ValueError('Previously unmatched UCSD CSE identifier appeared: ' + code)
            continue
        heading, body = blocks.get(code, (None, ''))
        if heading != entry['heading'] or hashlib.sha256(body.encode()).hexdigest() != entry['description_hash']:
            raise ValueError('Reviewed UCSD CSE source changed: ' + code)
        # Preserve the source's unparenthesized AND/OR wording and subsequent
        # restrictions. "None" is explicit; absence of the label stays unknown.
        prerequisites = body.split('Prerequisites:', 1)[1].strip() if 'Prerequisites:' in body else None
        if code == 'CSE 89':
            prerequisites = 'Restricted to students in the CSE-PACE program. Prerequisites: ' + prerequisites
        elif code == 'CSE 95':
            prerequisites = 'Concurrent tutor appointment in a CSE course is required.'
        courses.append({
            'id': entry['id'], 'code': code, 'name': entry['name'],
            'description': entry['description'], 'prerequisites': prerequisites,
            'credits': entry['credits'], 'credit_unit': 'quarter_hours',
            'category': entry['category'], 'source_id': SPEC['source_id'], 'url': URL,
        })
    return {'id': SPEC['program_id'], 'courses': courses}
