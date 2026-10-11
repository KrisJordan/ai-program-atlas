"""Reviewed public PSU policy observations, distinct from certification of the degree."""
import hashlib
import json
from functools import partial
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, rule

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())


def policy_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    root = soup.select_one('main') or soup.select_one('.entry-content') or soup.select_one('#content')
    if root is None:
        raise ValueError('Penn State policy main content missing')
    for element in root.select('nav, aside, footer, script, style'):
        element.decompose()
    return clean(root.get_text(' ', strip=True))


def parse_policy(html, pid, key):
    spec = SPEC[key]
    text = policy_text(html)
    if hashlib.sha256(text.encode()).hexdigest() != spec['digest']:
        raise ValueError('Penn State policy changed; manual review required: ' + key)
    return {'id': pid, 'requirements': [
        rule(pid+'-'+key, spec['title'], pid+'-'+key,
             kind='note', summary=spec['summary'])
    ]}


def source_parsers(pid):
    return {spec['url']: partial(parse_policy, pid=pid, key=key)
            for key, spec in SPEC.items()
            if not spec.get('program_ids') or pid in spec['program_ids']}
