"""Exact observed option metadata; finite manifest certifies no requirement roles."""
import hashlib
import json
import re
from functools import partial
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean

PID = 'drexel-ai-ml-bs'
SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())


def parse(html, code):
    soup = BeautifulSoup(html, 'html.parser')
    if soup.select_one('input[type=password]') or any(re.search(r'^(sign in|log ?in|access denied)', n.get_text(' ',strip=True), re.I) for n in soup.select('title,h1')):
        raise ValueError('Access page is not course evidence')
    entry = SPEC[code]
    matches = [r for r in soup.select('article.search-courseresult') if r.h3 and clean(r.h3.get_text(' ',strip=True)).startswith(code+' ')]
    if len(matches) != 1:
        raise ValueError('Drexel exact course result missing or ambiguous: '+code)
    result = matches[0]
    if hashlib.sha256(clean(result.get_text(' ',strip=True)).encode()).hexdigest() != entry['digest']:
        raise ValueError('Drexel reviewed option result changed: '+code)
    match = re.fullmatch(re.escape(code)+r' (.+) (\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?) Credits?', clean(result.h3.get_text(' ',strip=True)))
    block = result.select_one('.courseblock')
    if not match or block is None:
        raise ValueError('Drexel option structure changed')
    value = clean(block.get_text(' ',strip=True))
    clauses = []
    for label in ('Restrictions','Prerequisites','Corequisites?'):
        found = re.search(label+r'\s*: (.*?)(?= (?:Restrictions|Prerequisites|Corequisites?)\s*:|$)', value)
        if found:clauses.append(label.replace('?', '')+': '+found[1])
    repeat = re.search(r'Repeat Status: (.*?)(?= (?:Restrictions|Prerequisites|Corequisites?)\s*:|$)',value)
    return {'id':PID,'courses':[dict(id=entry['id'],code=code,name=match[1].removeprefix('[WI] '),description=entry['description'],prerequisites='; '.join(clauses) or None,credits=None if '-' in match[2] else float(match[2]),credit_unit='unknown',category=entry['category'],source_id=entry['source_id'],url=entry['url'])], 'observed_repeat_status':{code:repeat[1] if repeat else None}, 'observed_credit_ranges':{code:match[2]} if '-' in match[2] else {}}


def register(sources, parsers):
    for code, entry in SPEC.items():
        if entry['url'] in parsers:raise ValueError('Duplicate Drexel option source')
        sources.append(entry['url'])
        parsers[entry['url']] = partial(parse, code=code)
