"""Observe bounded Purdue departmental outlines without claiming current catalog access."""
import hashlib
import json
from functools import partial
from pathlib import Path

from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import text

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())
DIRECTORY_URL = 'https://www.cs.purdue.edu/academic-programs/courses/canonical_syllabi.html'
TERM_URL = 'https://www.cs.purdue.edu/academic-programs/courses/index.html'


def parse_directory(html, *, program_id):
    soup = BeautifulSoup(html, 'html.parser')
    main = soup.find('main')
    anchor = next((a for a in soup.find_all('a') if text(a) == 'CS 48300'), None)
    if not main or 'Syllabi of courses marked * are proposed' not in text(main):
        raise ValueError('Purdue canonical status definition missing')
    if not anchor or '*' not in text(anchor.find_parent('li')):
        raise ValueError('Purdue CS483 proposed status changed')
    return {'id': program_id, 'courses': [], 'requirements': [],
            'notes': ['The canonical directory marks CS48300 proposed; dated outlines do not certify the current course catalog.']}


def parse_current_directory(html, *, program_id):
    soup = BeautifulSoup(html, 'html.parser')
    heading = soup.find('h1')
    if not heading or text(heading) != 'Computer Science Courses: Fall 2026':
        raise ValueError('Purdue reviewed term changed')
    section = next((h for h in soup.find_all('h2') if text(h) == 'Undergraduate West Lafayette'), None)
    table = section.find_next('table') if section else None
    if not table:
        raise ValueError('Purdue West Lafayette course table missing')
    notes = []
    for code in ['CS 17600', 'CS 24300']:
        row = next((r for r in table.find_all('tr') if r.find('a') and text(r.find('a')) == code), None)
        cells = row.find_all('td') if row else []
        if len(cells) < 2:
            raise ValueError('Purdue reviewed course row missing')
        notes.append(code + ': Fall 2026 West Lafayette directory title is ' + text(cells[1]) +
                     '. This directory supplies no full description or prerequisite. Preserve any older degree-source title separately.')
    return {'id': program_id, 'courses': [], 'requirements': [], 'notes': notes}


def parse(html, *, program_id, code):
    entry = SPEC[code]
    if program_id not in entry['program_ids']:
        raise ValueError('Purdue canonical course outside reviewed scope')
    soup = BeautifulSoup(html, 'html.parser')
    main = soup.find('main')
    if not main or not any(text(h) == entry['heading'] for h in main.find_all(['h1', 'h2'])):
        raise ValueError('Purdue canonical heading changed')
    if hashlib.sha256(text(main).encode()).hexdigest() != entry['main_digest']:
        raise ValueError('Purdue canonical outline or dated context changed')
    course = dict(id=entry['course_id'], code=code, description=entry['description'],
                  prerequisites=entry['prerequisites'], category=entry['category'],
                  source_id=program_id+'-canonical-'+entry['course_id'], url=entry['url'])
    return {'id': program_id, 'courses': [course], 'requirements': [],
            'notes': [code + ': ' + entry['version_note']]}


def attach(namespace):
    pid = namespace['PROGRAM_ID']
    for url, parser in [(DIRECTORY_URL, parse_directory), (TERM_URL, parse_current_directory)]:
        if url not in namespace['SOURCES']:
            namespace['SOURCES'] += (url,)
        namespace['SOURCE_PARSERS'][url] = partial(parser, program_id=pid)
    for code, entry in SPEC.items():
        if pid not in entry['program_ids']:
            continue
        if entry['url'] not in namespace['SOURCES']:
            namespace['SOURCES'] += (entry['url'],)
        namespace['SOURCE_PARSERS'][entry['url']] = partial(parse, program_id=pid, code=code)
