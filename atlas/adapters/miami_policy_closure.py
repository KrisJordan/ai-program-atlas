"""Source-scoped remaining Miami completion and conditional college policies."""
from functools import partial
import hashlib
import json
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.business_society_minors import clean
from atlas.adapters.national_curriculum_common import rule
from atlas.adapters.miami_policies import SPECS, parse_policy
from atlas.adapters.miami_enrollment_scope import PROGRAMS

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())
SOURCE_IDS = {'grades': 'miami-grades-policy', 'business': 'miami-business-policy', 'arts': 'miami-arts-sciences-policy'}


def parse(html, *, pid, key):
    if pid not in PROGRAMS or key not in SPEC['notes']:
        raise ValueError('Unreviewed Miami policy scope')
    business = 'business' in pid
    if key in {'arts', 'business'} and (key == 'business') != business:
        raise ValueError('Wrong college for concrete Miami degree')
    observed = parse_policy(html, pid=pid, code=key)
    content = BeautifulSoup(html, 'html.parser').select_one('#content')
    for nav in content.find_all('nav'): nav.decompose()
    if hashlib.sha256(clean(content.get_text(' ',strip=True)).encode()).hexdigest() != SPEC['hashes'][key]:
        raise ValueError('Miami completion policy changed; source review required')
    return {**observed, 'requirements': [rule(pid+'-policy-'+suffix, title,
        SOURCE_IDS[key], kind='note', summary=summary)
        for suffix, title, summary in SPEC['notes'][key]]}


def _compose(previous, html, *, pid, key):
    old = previous(html); new = parse(html,pid=pid,key=key)
    if old.get('id') != pid: raise ValueError('Wrong prior Miami identity')
    ids = {r['id'] for r in new['requirements']}
    if ids & {r['id'] for r in old.get('requirements',[])}: raise ValueError('Duplicate completion policy')
    return {**old, 'requirements': old.get('requirements',[]) + new['requirements'],
            'observed_policy_sections': {**old.get('observed_policy_sections',{}), **new['observed_policy_sections']}}


def register(pid, sources, parsers):
    if pid not in PROGRAMS: raise ValueError('Unreviewed Miami degree')
    for key in ['grades', 'business' if 'business' in pid else 'arts']:
        url = SPECS[key][0]
        if url not in sources: sources.append(url)
        previous = parsers.get(url)
        parsers[url] = partial(_compose,previous,pid=pid,key=key) if previous else partial(parse,pid=pid,key=key)
