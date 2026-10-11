"""Source-guarded public registration policies with exact local scope."""
import copy
import hashlib
import json
from functools import partial
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import text

SPEC=json.loads(Path(__file__).with_suffix('.json').read_text())


def parse(html, *, key):
    entry=SPEC[key]
    soup=BeautifulSoup(html,'html.parser')
    main=soup.find('main') or soup.select_one('[role=main]')
    if main is None or not any(text(h)==entry['heading'] for h in main.find_all('h1')):
        raise ValueError('UCSB public policy heading unavailable or changed')
    if hashlib.sha256(text(main).encode()).hexdigest()!=entry['body_digest']:
        raise ValueError('UCSB policy scope or conditions changed; review required')
    return {'id':'ucsb-ai-bs','courses':[],
            'requirements':copy.deepcopy(entry['requirements'])}


def attach(namespace):
    for key,entry in SPEC.items():
        namespace['SOURCES']+=(entry['url'],)
        namespace['SOURCE_PARSERS'][entry['url']]=partial(parse,key=key)
