"""Guarded second-major course observations; independent reviews stay seed-only."""
import hashlib
import json
from pathlib import Path
import re
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, course
from atlas.adapters.northwestern_degree_metadata import eligibility

MANIFEST=json.loads(Path(__file__).with_name('northwestern_second_major_course_reviews.json').read_text())


def parse_descriptions(html, *, pid, department):
    soup=BeautifulSoup(html,'html.parser')
    headings=[clean(h.get_text(' ',strip=True)) for h in soup.find_all('h1') if clean(h.get_text(' ',strip=True))!='Academic Catalog']
    if headings!=MANIFEST['headings'][department]:
        raise ValueError('Second-major course directory heading changed: '+department)
    observations=[];digests={};changed=[]
    for suffix,review in MANIFEST['reviews'].items():
        if review['department']!=department or pid not in review['program_ids']:continue
        code=review['code']
        blocks=[b for b in soup.select('.courseblock') if b.select_one('.courseblocktitle,.couresblocktitle') and clean(b.select_one('.courseblocktitle,.couresblocktitle').get_text(' ',strip=True)).startswith(code+' ')]
        if len(blocks)!=1:raise ValueError('Exact second-major course missing/duplicated: '+code)
        block=blocks[0];label=clean(block.select_one('.courseblocktitle,.couresblocktitle').get_text(' ',strip=True))
        match=re.fullmatch(re.escape(code)+r' (.+) \((\d+(?:\.\d+)?) Units?\)',label)
        if not match or match[1]!=review['title']:raise ValueError('Second-major course title changed: '+code)
        desc=block.select_one('.courseblockdesc');body=clean(desc.get_text(' ',strip=True))if desc else ''
        digest=hashlib.sha256(body.encode()).hexdigest()
        c=course(pid,code,review['program_title'] if review['topic_specific']else match[1],pid+'-courses-'+department,review['url'],credits=float(match[2]),unit='units')
        c['id']=pid+'-'+suffix;c['prerequisites']=eligibility(body)
        if digest==review['description_sha256'] and not review['topic_specific']:
            c['description']=review['description'];c['category']=review['category']
        elif digest!=review['description_sha256']:changed.append(code)
        observations.append(c);digests[c['id']]=digest
    return dict(id=pid,courses=observations,requirements=[],observed_description_digests=digests,
                notes=['Changed course descriptions need independent review: '+', '.join(sorted(set(changed)))]if changed else [])


def register(pid,sources,parsers):
    for dep in {r['department']for r in MANIFEST['reviews'].values()if pid in r['program_ids']}:
        url=next(r['url']for r in MANIFEST['reviews'].values()if r['department']==dep)
        if url not in sources:sources+=(url,)
        parsers[url]=lambda html,dep=dep:parse_descriptions(html,pid=pid,department=dep)
    return sources
