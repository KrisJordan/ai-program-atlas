"""Additional reviewed Maryland policies; hashes guard the observed source scope."""
from functools import partial
import hashlib
import json
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, rule

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())


def policy_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    root = soup.select_one('#content') or soup.select_one('#main-content') or soup.select_one('main')
    if root is None:
        raise ValueError('Maryland policy content missing')
    for node in root.select('nav, script, style, footer'):
        node.decompose()
    return clean(root.get_text(' ', strip=True))


def parse(html, *, pid, key):
    entry = SPEC[key]
    if hashlib.sha256(policy_text(html).encode()).hexdigest() != entry['digest']:
        raise ValueError('Maryland policy changed; manual review required: ' + key)
    return {'id': pid, 'requirements': [
        rule(pid + '-closure-' + n['key'], n['title'], pid + '-closure-' + key,
             kind='note', summary=n['summary']) for n in entry['notes']]}


def parsers(pid):
    return {entry['url']: partial(parse, pid=pid, key=key) for key, entry in SPEC.items()
            if not entry.get('program_ids') or pid in entry['program_ids']}


def _compose(previous, added, html):
    old = previous(html)
    new = added(html)
    if old['id'] != new['id']:
        raise ValueError('Maryland policy observation identity mismatch')
    combined = dict(old)
    combined['requirements'] = old.get('requirements', []) + new.get('requirements', [])
    return combined


def register(existing, pid):
    """Preserve earlier observations when new rules use the same public page."""
    result = dict(existing)
    for url, added in parsers(pid).items():
        result[url] = partial(_compose, result[url], added) if url in result else added
    return result
