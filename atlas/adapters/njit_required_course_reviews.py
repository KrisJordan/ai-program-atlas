"""Individually reviewed NJIT required-course blocks; never certify the whole degree."""
import hashlib
import json
import re
from functools import partial
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, course
PID='new-jersey-institute-of-technology-business-with-ai-bs-degree'
SPEC=json.loads(Path(__file__).with_suffix('.json').read_text())


def parse_courses(html,key):
    soup=BeautifulSoup(html,'html.parser')
    wanted={code for code,spec in SPEC.items() if spec['key']==key}
    result=[]
    for block in soup.select('.courseblock'):
        heading=block.select_one('.courseblocktitle')
        if heading is None:continue
        title=clean(heading.get_text(' ',strip=True))
        match=re.fullmatch(r'([A-Z]+ \d+)\.\s+(.+?)\.\s+(\d+) credits?,.*',title)
        if not match or match[1] not in wanted:continue
        code,name,credits=match.groups();spec=SPEC[code]
        text=clean(block.get_text(' ',strip=True))
        if hashlib.sha256(text.encode()).hexdigest()!=spec['digest']:
            raise ValueError('NJIT required course changed; review required: '+code)
        c=course('njit',code,name,PID+'-courses-'+key,spec['url'],credits=int(credits),unit='semester_hours',category=spec['category'])
        c['description']=spec['description']
        clauses=re.findall(r'(?:Prerequisites?|Prerquisites|Restrictions?|Pre or Corequisites):\s*[^.]+\.?',text,re.I)
        if spec.get('eligibility_note'):clauses.append(spec['eligibility_note'])
        c['prerequisites']=' '.join(clauses) or None
        result.append(c)
    if {c['code'] for c in result}!=wanted or len(result)!=len(wanted):
        raise ValueError('Reviewed NJIT required course identities missing or duplicate')
    return {'id':PID,'courses':result}


SOURCE_PARSERS={spec['url']:partial(parse_courses,key=spec['key']) for spec in SPEC.values()}
