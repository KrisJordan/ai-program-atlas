"""Guarded UCSD language observations; manual reviews remain in the manifest.

One source chapter per call. No guessed suffix equivalence, identity groups,
requirement nodes, or audit certification are emitted.
"""
import hashlib
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())


def clean(value):
    return ' '.join(value.split())


def section_text(heading):
    parts = []
    for node in heading.next_siblings:
        if getattr(node, 'name', None) in ['h1', 'h2', 'h3', 'h4'] or 'course-name' in getattr(node, 'attrs', {}).get('class', []):
            break
        if getattr(node, 'name', None):
            parts.append(clean(node.get_text(' ', strip=True)))
    return clean(' '.join(parts))


def parse_observations(html, *, subject=None):
    soup = BeautifulSoup(html, 'html.parser')
    titles = [clean(h.get_text(' ', strip=True)) for h in soup.find_all('h1')]
    matching = [key for key, source in SPEC['sources'].items() if titles == [source['heading']]]
    if not matching or subject and subject not in matching:
        raise ValueError('UCSD language chapter identity changed')
    source = SPEC['sources'][matching[0]]
    disclaimer = soup.select_one('.course-disclaimer')
    if disclaimer is None or source['catalog_year'] not in clean(disclaimer.get_text(' ', strip=True)):
        raise ValueError('UCSD language catalog edition changed')
    for key, context in SPEC['chapter_contexts'].items():
        if key not in matching:
            continue
        nodes = [h for h in soup.find_all(context['tag']) if clean(h.get_text(' ', strip=True)) == context['heading']]
        if len(nodes) != 1 or section_text(nodes[0]) != context['text']:
            raise ValueError('UCSD language placement/context changed')
    headings = [clean(n.get_text(' ', strip=True)) for n in soup.select('p.course-name')]
    for key, guards in SPEC['identity_heading_guards'].items():
        if key in matching and any(headings.count(heading) != 1 for heading in guards):
            raise ValueError('Chinese placement-track identity evidence changed')
    entries = {e['code']: e for e in SPEC['entries'] if e['source_key'] in matching}
    blocks = {}
    for node in soup.select('p.course-name'):
        heading = clean(node.get_text(' ', strip=True))
        match = re.match(r'([A-Z]+ \d+[A-Z]*)\.', heading)
        codes = SPEC['grouped_headings'].get(heading, [match[1]] if match else [])
        for code in codes:
            if code not in entries:
                continue
            if code in blocks:
                raise ValueError('Duplicate assigned course: ' + code)
            entry = entries[code]
            if entry['heading'] is None:
                raise ValueError('Previously absent exact heading appeared: ' + code)
            region = node.find_previous('h2')
            division = node.find_previous(['h2', 'h3', 'h4'])
            if region is None or division is None or clean(region.get_text(' ', strip=True)) != entry['region'] or clean(division.get_text(' ', strip=True)) != entry['division']:
                raise ValueError('Course section identity changed: ' + code)
            if section_text(region) != entry['region_text'] or section_text(division) != entry['section_text']:
                raise ValueError('Course section eligibility/context changed: ' + code)
            body = []
            for part in node.next_siblings:
                if getattr(part, 'name', None) in ['h1', 'h2', 'h3', 'h4'] or 'course-name' in getattr(part, 'attrs', {}).get('class', []):
                    break
                if set(getattr(part, 'attrs', {}).get('class', [])) & {'course-description', 'course-descriptions'}:
                    body.append(clean(part.get_text(' ', strip=True)))
            blocks[code] = heading, clean(' '.join(body))
    rows, dispositions = [], []
    for code, entry in entries.items():
        if entry['heading'] is None:
            dispositions.append({'code': code, 'status': entry['disposition']})
            continue
        heading, body = blocks.get(code, (None, ''))
        if heading != entry['heading'] or hashlib.sha256(body.encode()).hexdigest() != entry['description_hash']:
            raise ValueError('Reviewed course block changed: ' + code)
        if subject and entry['source_key'] != subject:
            continue
        evidence = SPEC['sources'][entry['source_key']]
        rows.append(dict(id=entry['id'], code=code, name=entry['name'], description=entry['description'],
                         prerequisites=entry['observed_prerequisites'], credits=entry['credits'],
                         credit_unit='quarter_hours', category=entry['category'],
                         source_id=evidence['source_id'], url=evidence['url'], notes=entry['notes']))
    if subject:
        dispositions = [d for d in dispositions if d['code'].startswith(subject + ' ')]
    return {'id': SPEC['program_id'], 'courses': rows, 'source_dispositions': dispositions}


SOURCE_PARSERS = {source['url']: parse_observations for source in SPEC['sources'].values()}
