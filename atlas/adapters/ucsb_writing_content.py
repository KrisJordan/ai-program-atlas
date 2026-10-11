"""Guarded Writing Program descriptions; series policies retained with exact scope."""
import hashlib
import json
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import text
SPEC=json.loads(Path(__file__).with_suffix('.json').read_text())


def parse(html, *, section):
    data=SPEC[section];soup=BeautifulSoup(html,'html.parser');main=soup.find('main')
    if not main or hashlib.sha256(text(main).encode()).hexdigest()!=data['main_digest']:
        raise ValueError('UCSB writing content, series eligibility or units changed')
    courses=[]
    for code,e in data['courses'].items():
        if not any(text(h)==e['heading']for h in main.find_all('h3')):
            raise ValueError('UCSB writing exact identity missing')
        courses.append(dict(id=e['course_id'],code=code,name=e['name'],description=e['description'],prerequisites=e['prerequisites'],credits=e['credits'],credit_unit='quarter_hours',category=e['category'],source_id=data['source_id'],url=data['url']))
    return {'id':'ucsb-ai-bs','courses':courses,'requirements':[],
            'notes':data['notes']}


def attach(namespace):
    from functools import partial
    for section,data in SPEC.items():
        namespace['SOURCES']+=(data['url'],)
        namespace['SOURCE_PARSERS'][data['url']]=partial(parse,section=section)
