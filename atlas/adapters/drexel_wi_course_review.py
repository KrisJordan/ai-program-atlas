"""Exact current-quarter WI course evidence; no role or audit certification."""
import hashlib
import json
import re
from functools import partial
from pathlib import Path
from atlas.adapters.national_curriculum_common import clean, content

PID='drexel-ai-ml-bs'
SPEC=json.loads(Path(__file__).with_suffix('.json').read_text())


def parse(html,prefix):
    page=SPEC['pages'][prefix]
    root=content(html,page['heading'])
    h=root.find('h1')
    if h is None or clean(h.get_text(' ',strip=True))!=page['heading']:
        raise ValueError('Wrong Drexel subject heading')
    blocks=root.select('.courseblock')
    titles=[clean(b.select_one('.courseblocktitle').get_text(' ',strip=True)) for b in blocks if b.select_one('.courseblocktitle')]
    if len(titles)!=len(blocks) or hashlib.sha256('\n'.join(titles).encode()).hexdigest()!=page['inventory_digest']:
        raise ValueError('Drexel quarter course identity inventory changed')
    def exact(code):
        matches=[b for b in blocks if clean(b.select_one('.courseblocktitle').get_text(' ',strip=True)).startswith(code+' ')]
        if len(matches)!=1:raise ValueError('Exact Drexel course missing or ambiguous: '+code)
        return matches[0]
    for code,digest in page['auxiliary'].items():
        if hashlib.sha256(clean(exact(code).get_text(' ',strip=True)).encode()).hexdigest()!=digest:
            raise ValueError('Drexel continuation context changed: '+code)
    courses=[];missing=[];ranges={};repeat={}
    for code,e in SPEC['courses'].items():
        if e['prefix']!=prefix:continue
        if e.get('missing'):
            if any(t.startswith(code+' ') for t in titles):raise ValueError('Previously missing Drexel course now present: '+code)
            missing.append(code);continue
        b=exact(code)
        if hashlib.sha256(clean(b.get_text(' ',strip=True)).encode()).hexdigest()!=e['digest']:
            raise ValueError('Drexel reviewed WI course changed: '+code)
        title=clean(b.select_one('.courseblocktitle').get_text(' ',strip=True))
        match=re.fullmatch(re.escape(code)+r' (?:\[WI\] )?(.+) (\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?) Credits?',title)
        if not match:raise ValueError('Drexel WI credit/title structure changed')
        value=clean(b.get_text(' ',strip=True));clauses=[]
        for label in ('Restrictions','Prerequisites','Corequisites?'):
            m=re.search(label+r'\s*: (.*?)(?= (?:Restrictions|Prerequisites|Corequisites?)\s*:|$)',value)
            if m:clauses.append(label.replace('?','')+': '+m[1])
        r=re.search(r'Repeat Status: (.*?)(?= (?:Restrictions|Prerequisites|Corequisites?)\s*:|$)',value)
        repeat[code]=r[1] if r else None
        if '-' in match[2]:ranges[code]=match[2]
        summary=e['description']
        if code in ranges:summary+=' Published credit range: '+ranges[code]+'.'
        courses.append(dict(id=e['id'],code=code,name=match[1],description=summary,prerequisites='; '.join(clauses) or None,credits=None if code in ranges else float(match[2]),credit_unit='unknown',category=e['category'],source_id=page['source_id'],url=page['url']))
    return {'id':PID,'courses':courses,'observed_missing_courses':missing,'observed_credit_ranges':ranges,'observed_repeat_status':repeat}


def register(sources,parsers):
    for prefix,page in SPEC['pages'].items():
        if page['url'] in parsers:raise ValueError('Duplicate Drexel WI source')
        sources.append(page['url']);parsers[page['url']]=partial(parse,prefix=prefix)
