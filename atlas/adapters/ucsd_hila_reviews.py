"""Bounded manual HILA content review with complete course-block guards.

Only facts from unchanged current catalog blocks are emitted. Manual taxonomy
reviews and identity dispositions live in the manifest and require integration
by the program owner; no requirement or equivalence inference occurs here.
"""
import hashlib
import json
import re
from functools import partial
from pathlib import Path
from bs4 import BeautifulSoup, Comment, NavigableString

SPEC=json.loads(Path(__file__).with_suffix('.json').read_text())


def clean(value):
    return ' '.join(value.split())


def source_blocks(html, subject):
    source=SPEC['sources'][subject]
    soup=BeautifulSoup(html,'html.parser')
    if source['heading'] not in [clean(h.get_text(' ',strip=True)) for h in soup.find_all('h1')]:
        raise ValueError('UCSD course chapter identity changed')
    disclaimer=soup.select_one('.course-disclaimer')
    if disclaimer is None or source['catalog_year'] not in clean(disclaimer.get_text(' ',strip=True)):
        raise ValueError('UCSD catalog edition changed')
    if SPEC['chapter_marker'] not in [clean(p.get_text(' ',strip=True)) for p in soup.select('p.course-subhead-1')]:
        raise ValueError('History period marker changed')
    blocks={}
    nodes={}
    for heading in soup.select('p.course-name'):
        title=clean(heading.get_text(' ',strip=True));match=re.match(r'('+subject+r' \d+[A-Z]*)\.',title)
        codes=SPEC.get('grouped_headings',{}).get(title)
        if codes is None:codes=[match[1]] if match else []
        if not codes:continue
        parts=[]
        for sibling in heading.next_siblings:
            classes=getattr(sibling,'attrs',{}).get('class',[])
            if getattr(sibling,'name',None) in ['h1','h2','h3','h4','h5','h6'] or 'course-name' in classes:break
            if isinstance(sibling,Comment) or getattr(sibling,'name',None) in ['script','style']:continue
            value=clean(str(sibling)) if isinstance(sibling,NavigableString) else clean(sibling.get_text(' ',strip=True))
            if value:parts.append(value)
        for code in codes:
            if code in blocks:raise ValueError('Duplicate UCSD course heading: '+code)
            blocks[code]=(title,clean(' '.join(parts)))
            nodes[code]=heading
    policy=SPEC.get('colloquium_policy')
    if policy:
        anchor=nodes.get(policy['anchor_code'])
        section=anchor.find_previous('h4') if anchor else None
        note=section.find_next_sibling('p',class_='course-note') if section else None
        value=clean(note.get_text(' ',strip=True)) if note else ''
        if section is None or clean(section.get_text(' ',strip=True))!=policy['heading'] or hashlib.sha256(value.encode()).hexdigest()!=policy['body_hash']:
            raise ValueError('History undergraduate colloquium policy changed')
        for code in policy['course_codes']:
            if code not in nodes or nodes[code].find_previous('h4') is not section:
                raise ValueError('History colloquium policy scope changed: '+code)
    return blocks


def parse_observations(html, *, subject="HILA"):
    source=SPEC['sources'][subject];blocks=source_blocks(html,subject);courses=[];dispositions=[]
    for evidence in SPEC['supplementary_blocks']:
        heading,body=blocks.get(evidence['code'],(None,''))
        if heading!=evidence['heading'] or hashlib.sha256(body.encode()).hexdigest()!=evidence['description_hash']:
            raise ValueError('Supplementary History restriction changed: '+evidence['code'])
    for entry in SPEC['entries']:
        if not entry['code'].startswith(subject+' '):continue
        code=entry['code']
        if entry['heading'] is None:
            if code in blocks:raise ValueError('Previously unmatched UCSD identifier appeared: '+code)
            dispositions.append(dict(code=code,status='no_current_heading'))
            continue
        heading,body=blocks.get(code,(None,''))
        if heading!=entry['heading'] or hashlib.sha256(body.encode()).hexdigest()!=entry['description_hash']:
            raise ValueError('Reviewed UCSD course source changed: '+code)
        if not entry['approved_for_integration']:
            dispositions.append(dict(code=code,status='source_title_conflict',observed_name=entry['name']))
            continue
        prereq=re.split(r'Prerequisites\s*:',body,maxsplit=1)
        prerequisites=prereq[1].strip() if len(prereq)==2 else None
        courses.append(dict(id=entry['id'],code=code,name=entry['name'],description=entry['description'],
                            prerequisites=prerequisites,credits=entry['credits'],credit_unit='quarter_hours',
                            category=entry['category'],source_id=source['source_id'],url=source['url'],
                            notes=entry['notes']))
    return dict(id=SPEC['program_id'],courses=courses,source_dispositions=dispositions)


SOURCE_PARSERS={source['url']:partial(parse_observations,subject=subject) for subject,source in SPEC['sources'].items()}
