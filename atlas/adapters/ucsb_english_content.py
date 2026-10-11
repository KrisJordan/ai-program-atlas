"""Dated English offerings, with variable seminar and unavailable prerequisites explicit."""
import hashlib
import json
from pathlib import Path
from functools import partial
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import text
SPEC=json.loads(Path(__file__).with_suffix('.json').read_text())


def parse(html, *, key):
    e=SPEC[key];soup=BeautifulSoup(html,'html.parser');main=soup.find('main')
    if not main or hashlib.sha256(text(main).encode()).hexdigest()!=e['main_digest']:
        raise ValueError('UCSB dated English offering changed')
    if 'Course Number: '+e['code']not in text(main) or 'Quarter: '+e['term']not in text(main):
        raise ValueError('UCSB English course/version identity changed')
    course=dict(id=e['course_id'],code=e['code'],category='human_context',source_id=e['source_id'],url=e['url'])
    # A single seminar offering cannot speak for the whole variable course.
    if e['code']!='ENGL 197':
        course.update(name=e['name'],description=e['summary'],prerequisites=None)
    return {'id':'ucsb-ai-bs','courses':[course],'requirements':[],
            'notes':[e['term']+': '+e['summary']+' '+e['limits']]}


def attach(namespace):
    for key,e in SPEC.items():
        namespace['SOURCES']+=(e['url'],)
        namespace['SOURCE_PARSERS'][e['url']]=partial(parse,key=key)
