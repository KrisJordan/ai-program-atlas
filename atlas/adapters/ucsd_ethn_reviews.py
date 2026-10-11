"""Bounded manual ETHN content review with complete course-block guards.

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


def content_after(node):
    parts = []
    for sibling in node.next_siblings:
        classes = getattr(sibling, 'attrs', {}).get('class', [])
        if getattr(sibling, 'name', None) in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'] or 'course-name' in classes:
            break
        if isinstance(sibling, Comment) or getattr(sibling, 'name', None) in ['script', 'style']:
            continue
        text = clean(str(sibling) if isinstance(sibling, NavigableString) else sibling.get_text(' ', strip=True))
        if text:
            parts.append(text)
    return clean(' '.join(parts))


def source_blocks(html, subject):
    source=SPEC['sources'][subject]
    soup=BeautifulSoup(html,'html.parser')
    if source['heading'] not in [clean(h.get_text(' ',strip=True)) for h in soup.find_all('h1')]:
        raise ValueError('UCSD course chapter identity changed')
    disclaimer=soup.select_one('.course-disclaimer')
    if disclaimer is None or source['catalog_year'] not in clean(disclaimer.get_text(' ',strip=True)):
        raise ValueError('UCSD catalog edition changed')
    policy = SPEC['section_policies'][subject]
    policy_nodes = [h for h in soup.find_all(policy['heading_tag'])
                    if clean(h.get_text(' ', strip=True)) == policy['heading']]
    if len(policy_nodes) != 1 or content_after(policy_nodes[0]) != policy['text']:
        raise ValueError('UCSD section preparation policy changed')
    blocks={}
    for heading in soup.select('p.course-name'):
        title=clean(heading.get_text(' ',strip=True));match=re.match(r'('+subject+r' \d+[A-Z]*)\.',title)
        if not match:continue
        if match[1] not in {e['code'] for e in SPEC['entries']}:continue
        section = heading.find_previous(['h1','h2','h3','h4','h5','h6'])
        region = heading.find_previous('h2')
        blocks.setdefault(match[1], []).append(dict(
            heading=title, body=content_after(heading),
            section=clean(section.get_text(' ', strip=True)) if section else None,
            region=clean(region.get_text(' ', strip=True)) if region else None))
    resolved={}
    for code,variants in blocks.items():
        expected=SPEC.get('reviewed_duplicate_blocks',{}).get(code)
        if expected:
            observed=[dict(heading=v['heading'], description_hash=hashlib.sha256(v['body'].encode()).hexdigest(), section=v['section'], region=v['region']) for v in variants]
            if observed!=expected:
                raise ValueError('Reviewed UCSD duplicate blocks changed: '+code)
        elif len(variants)>1:
            raise ValueError('Duplicate UCSD course heading: '+code)
        resolved[code]=variants[-1]
    return resolved


def parse_observations(html, *, subject="ETHN"):
    source=SPEC['sources'][subject];blocks=source_blocks(html,subject);courses=[];dispositions=[]
    for entry in SPEC['entries']:
        if not entry['code'].startswith(subject+' '):continue
        code=entry['code']
        if entry['heading'] is None:
            if code in blocks:raise ValueError('Previously unmatched UCSD identifier appeared: '+code)
            dispositions.append(dict(code=code,status='no_current_heading'))
            continue
        block=blocks.get(code)
        if block is None or block['heading']!=entry['heading'] or hashlib.sha256(block['body'].encode()).hexdigest()!=entry['description_hash']:
            raise ValueError('Reviewed UCSD course source changed: '+code)
        if block['section'] != entry['section'] or block['region'] != entry['region']:
            raise ValueError('Reviewed section membership changed: '+code)
        if not entry['approved_for_integration']:
            dispositions.append(dict(code=code,status='source_title_conflict',observed_name=entry['name']))
            continue
        prereq=re.split(r'Prerequisites\s*:',block['body'],maxsplit=1)
        parts=[]
        if block['region'] == SPEC['section_policies'][subject]['heading']:
            parts.append('Section preparation rule: '+SPEC['section_policies'][subject]['text'])
        if len(prereq)==2:
            parts.append('Course-specific prerequisite: '+prereq[1].strip())
        prerequisites='\n'.join(parts) or None
        courses.append(dict(id=entry['id'],code=code,name=entry['name'],description=entry['description'],
                            prerequisites=prerequisites,credits=entry['credits'],credit_unit='quarter_hours',
                            category=entry['category'],source_id=source['source_id'],url=source['url'],
                            notes=entry['notes']))
    return dict(id=SPEC['program_id'],courses=courses,source_dispositions=dispositions)


SOURCE_PARSERS={source['url']:partial(parse_observations,subject=subject) for subject,source in SPEC['sources'].items()}
