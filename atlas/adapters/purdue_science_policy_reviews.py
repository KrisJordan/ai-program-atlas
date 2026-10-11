"""Guarded observations from six reviewed Purdue Science handbook pages.

Raw pages remain in the ignored Fetcher cache. This helper does not register
sources, certify a degree audit, or infer course metadata or approvals.
"""

from functools import partial
import hashlib
import json
from pathlib import Path

from bs4 import BeautifulSoup

from atlas.adapters.national_curriculum_common import rule

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())
PROGRAM_ID = 'purdue-ai-bs'
SOURCES = tuple(source['url'] for source in SPEC['sources'].values())


def clean(value):
    return ' '.join(value.split())


def policy_block(html):
    """Retain all policy content and link destinations, excluding site navigation."""
    soup = BeautifulSoup(html, 'html.parser')
    if soup.find('input', attrs={'type': 'password'}):
        raise ValueError('Access page is not Purdue policy evidence')
    blocks = soup.select('main#content')
    if len(blocks) != 1:
        raise ValueError('Expected one Purdue policy main block')
    main = blocks[0]
    for node in main.select('nav, aside, footer, script, style, .breadcrumbs, .page-sidebar'):
        node.decompose()
    headings = main.find_all('h1')
    if len(headings) != 1:
        raise ValueError('Expected one Purdue policy heading')
    payload = {
        'text': clean(main.get_text(' ', strip=True)),
        'links': [
            {'text': clean(a.get_text(' ', strip=True)), 'href': a.get('href', '')}
            for a in main.find_all('a')
        ],
    }
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return clean(headings[0].get_text(' ', strip=True)), hashlib.sha256(serialized.encode()).hexdigest()


def parse(html, *, key, pid=PROGRAM_ID):
    if pid != PROGRAM_ID or key not in SPEC['sources']:
        raise ValueError('Unreviewed Purdue policy scope')
    source = SPEC['sources'][key]
    heading, digest = policy_block(html)
    if heading != source['heading'] or digest != source['block_sha256']:
        raise ValueError('Purdue policy block changed; full source review required')
    return {
        'id': PROGRAM_ID,
        'requirements': [
            rule(PROGRAM_ID + '-policy-' + note['suffix'], note['title'], source['id'],
                 kind='note', unit='semester_hours', summary=note['summary'])
            for note in source['notes']
        ],
    }


PARSERS = {source['url']: partial(parse, key=key) for key, source in SPEC['sources'].items()}
