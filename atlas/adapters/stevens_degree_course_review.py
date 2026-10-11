"""Source-scoped Stevens course observations; manual reviews remain seed-only."""
import hashlib
import json
from functools import partial
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean
PID = 'stevens-institute-of-technology-artificial-intelligence-bs-degree'
SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())

def field(soup, label):
    heading = next((h for h in soup.select('h3.field-label') if clean(h.get_text()) == label), None)
    node = heading.parent.select_one('.field-value') if heading else None
    return clean(node.get_text(' ', strip=True)) if node else None

def parse(html, code, eligibility=False):
    soup = BeautifulSoup(html, 'html.parser');entry=SPEC[code]
    root=soup.select_one('article.flex-1')
    heading=root.find('h1') if root else None
    if not heading or clean(heading.get_text(' ',strip=True)) != code:
        raise ValueError('Stevens course identity changed: '+code)
    label='Student Eligibility Rule' if eligibility else 'Course Description'
    value=field(root,label)
    digest=entry['eligibility_digest'] if eligibility else entry['description_digest']
    if value is None or hashlib.sha256(value.encode()).hexdigest()!=digest:
        raise ValueError('Stevens reviewed course field changed: '+code)
    if eligibility:
        return {'id':PID,'courses':[{'id':entry['id'],'code':code,'prerequisites':value,'source_id':entry['source_id']+'-eligibility','url':entry['eligibility_url']}]}
    credits=field(root,'Credits')
    if credits is None or not credits.isdigit():
        raise ValueError('Stevens course credits missing or nonnumeric')
    return {'id':PID,'courses':[dict(id=entry['id'],code=code,name=entry['name'],description=entry['description'],category=entry['category'],credits=int(credits),credit_unit='unknown',source_id=entry['source_id'],url=entry['url'],prerequisites=entry.get('description_prerequisites'))]}

def register(sources, parsers):
    for code,entry in SPEC.items():
        sources.append(entry['url']);parsers[entry['url']]=partial(parse,code=code)
        if entry.get('eligibility_url'):
            sources.append(entry['eligibility_url']);parsers[entry['eligibility_url']]=partial(parse,code=code,eligibility=True)
