"""Guarded observations for an explicit ARTF/ARTG primary-review contribution.

The companion manifest contains manual subject decisions, never copied into an
observation as a category_review. Existing program targets restrict this helper's
scope; course eligibility is not converted into degree requirement membership.
"""
import hashlib
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

from atlas.adapters.northeastern_courseleaf import clean

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())
SOURCES = {subject: entry['url'] for subject, entry in SPEC['sources'].items()}


def parse_subject(html, *, program_id, subject, codes=None):
    source = SPEC['sources'][subject]
    entries = SPEC['courses']
    targets = {code: next((t for t in entry['targets'] if t['program_id'] == program_id), None)
               for code, entry in entries.items() if entry['subject'] == subject}
    targets = {code: target for code, target in targets.items() if target}
    requested = list(targets) if codes is None else list(codes)
    if not requested or len(requested) != len(set(requested)) or set(requested) - targets.keys():
        raise ValueError('Course selection outside reviewed program contribution')
    soup = BeautifulSoup(html, 'html.parser')
    site = soup.select_one('#site-title h1')
    content = soup.select_one('#textcontainer')
    if not site or clean(site) != source['heading'] or content is None:
        raise ValueError('Expected Northeastern subject catalog missing')
    if '2026-2027' not in soup.get_text(' ', strip=True):
        raise ValueError('Reviewed Northeastern catalog version missing')
    observed = {}
    for block in content.select('.courseblock'):
        heading = block.select_one('.courseblocktitle')
        if not heading:
            continue
        match = re.fullmatch(r'([A-Z]+ \d+)\.\s+(.+?)\.\s+\((\d+) Hours?\)', clean(heading))
        if not match or match[1] not in entries:
            continue
        code = match[1]
        if code in observed:
            raise ValueError('Duplicate reviewed course identity: ' + code)
        observed[code] = (block, match)
    # Generic accompanying-lab descriptions require their separately read lecture
    # evidence too, including when the caller selects only the laboratory record.
    dependencies = {'ARTG 1002':'ARTG 1001'}
    checked = set(requested) | {dependencies[c] for c in requested if c in dependencies}
    for code in checked:
        if code not in observed:
            raise ValueError('Reviewed course missing: ' + code)
        block, match = observed[code]
        if hashlib.sha256(clean(block).encode()).hexdigest() != entries[code]['block_digest']:
            raise ValueError('Reviewed complete course block changed: ' + code)
    courses, notes = [], []
    for code in requested:
        entry = entries[code]
        block, match = observed[code]
        body = block.select_one('.cb_desc')
        if not body or entry['description_guard'] not in clean(body):
            raise ValueError('Reviewed description missing: ' + code)
        prerequisite = None
        for extra in block.select('.courseblockextra'):
            value = clean(extra)
            if value.startswith('Prerequisite(s):'):
                prerequisite = value.removeprefix('Prerequisite(s):').strip() or None
            elif value.startswith('Corequisite(s):'):
                notes.append(code + ' concurrent corequisite(s): ' + value.removeprefix('Corequisite(s):').strip()
                             + '. This observation does not add degree requirement membership.')
        additions=[c['summary'] for c in entry['conditions'] if c['kind']=='additional_prerequisite']
        if additions:
            prerequisite=' '.join(([prerequisite] if prerequisite else [])+additions)
        notes.extend(code + ' ' + condition['kind'] + ': ' + condition['summary'] for condition in entry['conditions'])
        courses.append(dict(id=targets[code]['course_id'], code=code, name=match[2],
                            description=entry['description'], credits=int(match[3]),
                            credit_unit='semester_hours', prerequisites=prerequisite,
                            category=entry['category'], source_id=program_id+'-'+subject.lower()+'-courses',
                            url=source['url']))
    return {'id': program_id, 'courses': courses, 'requirements': [], 'notes': notes}


def attach_reviewed_sources(program_id, parsers):
    """Compose exact reviewed targets with an existing broader subject observer."""
    result=dict(parsers)
    for subject,url in SOURCES.items():
        if not any(t['program_id']==program_id for e in SPEC['courses'].values()
                   if e['subject']==subject for t in e['targets']):
            continue
        previous=result.get(url)
        def observe(html,subject=subject,previous=previous):
            reviewed=parse_subject(html,program_id=program_id,subject=subject)
            if previous is None:return reviewed
            original=previous(html)
            updates={c['id']:c for c in reviewed['courses']}
            courses=[updates.pop(c['id'],c) for c in original.get('courses',[])]
            courses.extend(updates.values())
            return {**original,'courses':courses,
                    'notes':list(dict.fromkeys(original.get('notes',[])+reviewed.get('notes',[])))}
        result[url]=observe
    return result


def attach_contextual_courses(result, html):
    """Map explicitly optional/recommended identities only to existing notes."""
    spec=SPEC['degree_review'];pid=spec['program_id']
    soup=BeautifulSoup(html,'html.parser');panel=soup.select_one('#programrequirementstextcontainer');title=soup.select_one('#site-title h1')
    if (result.get('id')!=pid or title is None or clean(title)!=spec['title']
            or '2026-2027' not in soup.get_text(' ',strip=True) or panel is None
            or hashlib.sha256(clean(panel).encode()).hexdigest()!=spec['requirements_digest']):
        raise ValueError('Reviewed Design degree identity or panel changed')
    rows={r['id']:r for r in result['requirements']}
    existing={c['id'] for c in result['courses']}
    for code,expected in spec['contextual_courses'].items():
        row=rows.get(expected['note_id']);cid=pid+'-'+code.lower().replace(' ','-')
        if (not row or row['kind']!='note' or row['summary']!=expected['note_summary']
                or row.get('course_ids') or cid in existing):
            raise ValueError('Design recommendation note changed or already mapped: '+code)
        row['course_ids']=[cid]
        result['courses'].append(dict(id=cid,code=code,name=SPEC['courses'][code]['name'],description=None,prerequisites=None,credits=None,credit_unit='semester_hours',category='other',source_id=pid+'-catalog',url=spec['url'],public_site=None,syllabus=None))
    return result
