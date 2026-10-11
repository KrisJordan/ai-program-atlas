"""Guarded observations from ordinarily rendered UCSB catalog course pages.

Initial loading HTML is not course evidence. Refresh callers must supply the
rendered public page; a missing or altered body requires a fresh human review.
"""
import hashlib
import json
from functools import partial
from pathlib import Path

from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import text

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())


def parse(html, *, code):
    entry = SPEC[code]
    soup = BeautifulSoup(html, 'html.parser')
    main = soup.find('main') or soup.select_one('[role=main]')
    heading = main.find('h1') if main is not None else None
    if heading is None or text(heading) != entry['heading']:
        raise ValueError('UCSB rendered course identity unavailable or changed')
    body = text(main)
    if 'Full Course Title ' not in body:
        raise ValueError('UCSB rendered course fields unavailable')
    fields = body.split('Full Course Title ', 1)[1].split(' Programs ', 1)[0]
    if hashlib.sha256(fields.encode()).hexdigest() != entry['fields_digest']:
        raise ValueError('UCSB catalog course fields changed; review required')
    course = dict(id=entry['course_id'], code=code, name=entry['name'],
                  description=entry['summary'], credits=entry['credits'],
                  credit_unit='quarter_hours', prerequisites=entry['prerequisites'],
                  category=entry['category'], source_id=entry['source_id'],
                  url=entry['url'])
    if not entry.get('observe_category', True):
        # Generic current metadata cannot certify the subject of specific terms.
        course.pop('category')
    # Identity certification and taxonomy review are manual seed annotations.
    return dict(id='ucsb-ai-bs', courses=[course], requirements=[], notes=[
        'Observed current catalog metadata does not itself certify a manual '
        'taxonomy review, identity group or mandatory degree role.'])


def attach(namespace):
    for code, entry in SPEC.items():
        namespace['SOURCES'] += (entry['url'],)
        namespace['SOURCE_PARSERS'][entry['url']] = partial(parse, code=code)
