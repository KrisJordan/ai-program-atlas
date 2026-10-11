"""Guarded actual remaining literature content, separate from manual review."""
import hashlib
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

SPEC=json.loads(Path(__file__).with_suffix('.json').read_text())


def clean(value):
    return ' '.join(value.split())


def section_text(heading):
    parts=[]
    for node in heading.next_siblings:
        if getattr(node,'name',None) in ['h1','h2','h3','h4'] or 'course-name' in getattr(node,'attrs',{}).get('class',[]):break
        if getattr(node,'name',None):parts.append(clean(node.get_text(' ',strip=True)))
    return clean(' '.join(parts))


def source_blocks(html):
    soup=BeautifulSoup(html,'html.parser')
    if [clean(h.get_text(' ',strip=True))for h in soup.find_all('h1')]!=['Literature']:
        raise ValueError('UCSD Literature chapter identity changed')
    disclaimer=soup.select_one('.course-disclaimer')
    if disclaimer is None or '2026–27' not in clean(disclaimer.get_text(' ',strip=True)):
        raise ValueError('UCSD Literature catalog edition changed')
    for context in SPEC['additional_contexts']:
        matches=[h for h in soup.find_all(context['heading_tag'])if clean(h.get_text(' ',strip=True))==context['heading']]
        if context.get('parent'):
            matches=[h for h in matches if h.find_previous('h2')and clean(h.find_previous('h2').get_text(' ',strip=True))==context['parent']]
        if len(matches)!=1 or section_text(matches[0])!=context['text']:
            raise ValueError('Literature language/context rule changed')
    assigned={e['code']:e for e in SPEC['entries']};supplementary={e['code']:e for e in SPEC['supplementary_blocks']};blocks={}
    for node in soup.select('p.course-name'):
        heading=clean(node.get_text(' ',strip=True));match=re.match(r'((?:LTCS|LTRU|LTWR|LTAF|LTAM|LTSP|LTCH|LTKO|LTFR|LTGK|LTGM|LTIT) \d+[A-Z]*)\.',heading)
        codes=SPEC.get('grouped_headings',{}).get(heading,[match[1]]if match else [])
        for code in codes:
            if code not in assigned and code not in supplementary:continue
            if code in blocks:raise ValueError('Duplicate assigned Literature heading: '+code)
            entry=assigned.get(code)
            if entry and entry['heading'] is None:raise ValueError('Previously absent Literature heading appeared: '+code)
            if entry:
                region=node.find_previous('h2');division=node.find_previous(['h2','h3','h4'])
                if region is None or clean(region.get_text(' ',strip=True))!=entry['region']or division is None or clean(division.get_text(' ',strip=True))!=entry['division']:
                    raise ValueError('Literature course moved outside reviewed section: '+code)
                if section_text(division)!=entry['section_text']:
                    raise ValueError('Literature section eligibility changed: '+code)
            body=[]
            for part in node.next_siblings:
                if getattr(part,'name',None)in['h1','h2','h3','h4']or'course-name'in getattr(part,'attrs',{}).get('class',[]):break
                if set(getattr(part,'attrs',{}).get('class',[]))&{'course-description','course-descriptions'}:body.append(clean(part.get_text(' ',strip=True)))
            blocks[code]=(heading,clean(' '.join(body)))
    for evidence in SPEC['supplementary_blocks']:
        heading,body=blocks.get(evidence['code'],(None,''))
        if heading!=evidence['heading'] or hashlib.sha256(body.encode()).hexdigest()!=evidence['description_hash']:
            raise ValueError('Related successor course evidence changed: '+evidence['code'])
    return blocks


def parse_observations(html,*,subject=None):
    blocks=source_blocks(html);rows=[];dispositions=[]
    for entry in SPEC['entries']:
        code=entry['code']
        if subject and not code.startswith(subject+' '):continue
        if entry['heading'] is None:
            if code in blocks:raise ValueError('Previously absent Literature heading appeared: '+code)
            dispositions.append(dict(code=code,status='no_current_heading'));continue
        heading,body=blocks.get(code,(None,''))
        if heading!=entry['heading']or hashlib.sha256(body.encode()).hexdigest()!=entry['description_hash']:
            raise ValueError('Reviewed Literature block changed: '+code)
        if not entry['approved_for_integration']:
            dispositions.append(dict(code=code,status=entry['disposition'],observed_name=entry['name']));continue
        source=SPEC['sources'][code.split()[0]]
        rows.append(dict(id=entry['id'],code=code,name=entry['name'],description=entry['description'],
                         prerequisites=entry['observed_prerequisites'],credits=entry['credits'],credit_unit='quarter_hours',
                         category=entry['category'],source_id=source['source_id'],url=source['url'],notes=entry['notes']))
    return dict(id=SPEC['program_id'],courses=rows,source_dispositions=dispositions)


SOURCE_PARSERS={s['url']:parse_observations for s in SPEC['sources'].values()}
