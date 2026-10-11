"""Current content for a bounded, previously code-only UCSD social-course set.

Exact course/section/edition observations are guarded. Manual category reviews
are separate manifest evidence; runtime never certifies a review or an alias.
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


def content_after(node):
    parts = []
    for sibling in node.next_siblings:
        classes = getattr(sibling, 'attrs', {}).get('class', [])
        if getattr(sibling, 'name', None) in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'] or 'course-name' in classes:
            break
        if isinstance(sibling, Comment) or getattr(sibling, 'name', None) in ['script', 'style']:
            continue
        text = clean(str(sibling) if isinstance(sibling, NavigableString) else sibling.get_text(' ', strip=True))
        if text:
            parts.append(text)
    return clean(' '.join(parts))


def source_blocks(html, subject):
    source = SPEC['sources'][subject]
    soup = BeautifulSoup(html, 'html.parser')
    if soup.find('input', attrs={'type': 'password'}):
        raise ValueError('Access page is not course evidence')
    if source['heading'] not in [clean(h.get_text(' ', strip=True)) for h in soup.find_all('h1')]:
        raise ValueError('UCSD chapter identity changed')
    disclaimer = soup.select_one('.course-disclaimer')
    if disclaimer is None or source['catalog_year'] not in clean(disclaimer.get_text(' ', strip=True)):
        raise ValueError('UCSD catalog edition changed')
    policy = SPEC['section_policies'].get(subject)
    if policy:
        headings = [h for h in soup.find_all(policy['heading_tag']) if clean(h.get_text(' ', strip=True)) == policy['heading']]
        if len(headings) != 1 or content_after(headings[0]) != policy['text']:
            raise ValueError('UCSD section preparation policy changed')
    blocks = {}
    for node in soup.select('p.course-name'):
        heading = clean(node.get_text(' ', strip=True))
        match = re.match(r'(' + re.escape(subject) + r' \d+[A-Z]*)\.', heading)
        codes = SPEC['grouped_headings'].get(heading, [match[1]] if match else [])
        for code in codes:
            if not code.startswith(subject + ' ') or code not in SPEC['target_codes']:
                continue
            if code in blocks:
                raise ValueError('Duplicate course heading: ' + code)
            section = node.find_previous(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            region = node.find_previous('h2')
            blocks[code] = {'heading': heading, 'body': content_after(node),
                            'section': clean(section.get_text(' ', strip=True)) if section else None,
                            'region': clean(region.get_text(' ', strip=True)) if region else None}
    return blocks


def parse_observations(html, *, subject):
    source = SPEC['sources'][subject]
    blocks = source_blocks(html, subject)
    courses, dispositions = [], []
    for entry in SPEC['entries']:
        code = entry['code']
        if not code.startswith(subject + ' '):
            continue
        block = blocks.get(code)
        if entry['heading'] is None:
            if block is not None:
                raise ValueError('Previously missing exact identifier appeared: ' + code)
            dispositions.append({'id': entry['id'], 'code': code, 'status': 'no_current_heading'})
            continue
        if block is None or block['heading'] != entry['heading'] or hashlib.sha256(block['body'].encode()).hexdigest() != entry['description_hash']:
            raise ValueError('Reviewed complete course block changed: ' + code)
        if block['section'] != entry['section'] or block['region'] != entry['region']:
            raise ValueError('Reviewed section membership changed: ' + code)
        courses.append({'id': entry['id'], 'code': code, 'name': entry['name'],
                        'description': entry['description'], 'prerequisites': entry['observed_prerequisites'],
                        'credits': entry['credits'], 'credit_unit': 'quarter_hours', 'category': entry['category'],
                        'source_id': source['source_id'], 'url': source['url'], 'notes': entry['notes']})
    return {'id': SPEC['program_id'], 'courses': courses, 'source_dispositions': dispositions}


SOURCE_PARSERS = {source['url']: partial(parse_observations, subject=subject) for subject, source in SPEC['sources'].items()}
