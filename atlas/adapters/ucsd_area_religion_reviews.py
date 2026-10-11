"""Actual bounded area/religion chapter metadata with literal shared-heading guards."""
import hashlib
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

SPEC=json.loads(Path(__file__).with_suffix('.json').read_text())


def clean(text):
    return ' '.join(text.split())


def source_blocks(html,subject):
    source=SPEC['sources'][subject];soup=BeautifulSoup(html,'html.parser')
    if [clean(h.get_text(' ',strip=True))for h in soup.find_all('h1')]!=[source['heading']]:
        raise ValueError('UCSD chapter identity changed')
    disclaimer=soup.select_one('.course-disclaimer')
    if disclaimer is None or source['catalog_year']not in clean(disclaimer.get_text(' ',strip=True)):
        raise ValueError('UCSD catalog edition changed')
    entries={e['code']:e for e in SPEC['entries']if e['code'].startswith(subject+' ')};blocks={}
    for node in soup.select('p.course-name'):
        heading=clean(node.get_text(' ',strip=True));match=re.match(r'('+subject+r' \d+[A-Z]*)\.',heading)
        codes=SPEC['grouped_headings'].get(heading,[match[1]]if match else[])
        for code in codes:
            if code not in entries:continue
            entry=entries[code]
            if entry['heading']is None:raise ValueError('Previously absent identifier appeared: '+code)
            if code in blocks:raise ValueError('Duplicate assigned course heading: '+code)
            section=node.find_previous(['h1','h2','h3','h4'])
            if section is None or clean(section.get_text(' ',strip=True))!=entry['section']:
                raise ValueError('Course section changed: '+code)
            body=[]
            for part in node.next_siblings:
                if getattr(part,'name',None)in['h1','h2','h3','h4']or'course-name'in getattr(part,'attrs',{}).get('class',[]):break
                if 'course-descriptions'in getattr(part,'attrs',{}).get('class',[]):body.append(clean(part.get_text(' ',strip=True)))
            blocks[code]=(heading,clean(' '.join(body)))
    return blocks


def parse_observations(html,*,subject):
    source=SPEC['sources'][subject];blocks=source_blocks(html,subject);rows=[];dispositions=[]
    for entry in SPEC['entries']:
        code=entry['code']
        if not code.startswith(subject+' '):continue
        if entry['heading']is None:dispositions.append(dict(code=code,status='no_current_heading'));continue
        heading,body=blocks.get(code,(None,''))
        if heading!=entry['heading']or hashlib.sha256(body.encode()).hexdigest()!=entry['description_hash']:
            raise ValueError('Reviewed course block changed: '+code)
        parts=re.split(r'Prerequisites\s*:',body,maxsplit=1);prep=parts[1].strip()if len(parts)==2 else None
        rows.append(dict(id=entry['id'],code=code,name=entry['name'],description=entry['description'],prerequisites=prep,credits=entry['credits'],credit_unit='quarter_hours',category=entry['category'],source_id=source['source_id'],url=source['url'],notes=entry['notes']))
    return dict(id=SPEC['program_id'],courses=rows,source_dispositions=dispositions)


SOURCE_PARSERS={s['url']:(lambda html,subject=subject:parse_observations(html,subject=subject))for subject,s in SPEC['sources'].items()}
