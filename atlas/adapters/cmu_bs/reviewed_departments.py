"""Reviewed department descriptions, with factual metadata read from each response."""
import hashlib
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from .common import course, text, requirement

PID = 'cmu-bs-ai'
MANIFEST = json.loads(Path(__file__).with_name('reviewed_department_subjects.json').read_text())
MANIFEST.update(json.loads(Path(__file__).with_name('reviewed_history_subjects.json').read_text()))


def observe(html, spec):
    soup = BeautifulSoup(html, 'html.parser')
    if not any(text(h) == spec['heading']for h in soup.find_all(['h1','h2'])):
        raise ValueError('CMU department directory heading missing')
    year = re.search(r'(20\d{2}[-–]20\d{2})\s+Catalog',text(soup))
    if not year:raise ValueError('CMU department directory edition missing')
    records=[];digests={};bodies={}
    for b in soup.find_all('dl',class_='courseblock'):
        if not b.dt or not b.dd:raise ValueError('Course block changed')
        match=re.fullmatch(r'(\d{2}-\d{3})\s+(.+)',text(b.dt))
        if not match or match[1]not in spec['subjects']:continue
        code,name=match.groups()
        if code in digests:raise ValueError('Duplicate course code')
        body=BeautifulSoup(str(b.dd),'html.parser')
        for br in body.find_all('br'):br.replace_with('\n')
        lines=[' '.join(x.split())for x in body.get_text(' ',strip=False).splitlines()if x.strip()]
        units=re.fullmatch(r'[^:]+:\s*(\d+(?:\.\d+)?) units',lines[0])
        c=course(code,name,spec['source_id'],spec['url'],'other',float(units[1])if units else None)
        prereq=[re.sub(r'^Prerequisites?:\s*','',x)for x in lines if re.match(r'^Prerequisites?:',x)]
        if len(prereq)>1:raise ValueError('Repeated formal prerequisite field')
        c['prerequisites']=prereq[0]if prereq else None
        desc=' '.join(x for x in lines[1:]if not re.match(r'^(Prerequisites?|Corequisites?|Course Website):',x))
        digests[code]=hashlib.sha256(desc.encode()).hexdigest();bodies[code]=text(b.dd)
        r=spec['subjects'][code]
        if name==r['name']and digests[code]==r.get('description_digest'):c['category']=r['category']
        records.append(c)
    if {c['code']for c in records}!=set(spec['subjects']):raise ValueError('Reviewed department course inventory changed')
    rules=[]
    for code,items in spec.get('conditions',{}).items():
        for i,item in enumerate(items):
            if item['marker']not in bodies[code]:raise ValueError('Course-entry condition changed: '+code)
            rules.append(requirement(PID,'department-entry-'+code+'-'+str(i),'Course-entry condition: '+code,spec['source_id'],kind='note',summary=item['summary']))
    return dict(id=PID,catalog_year=year[1],curriculum_status='partial',courses=records,requirements=rules,observed_description_digests=digests)


def parse(html,url):return observe(html,MANIFEST[url])


def register(sources,parsers):
    for url in MANIFEST:
        if url not in sources:sources.append(url)
        parsers[url]=lambda html,url=url:parse(html,url)


def classify_titles(observed):
    subjects={code:r for spec in MANIFEST.values()for code,r in spec['subjects'].items()}
    for c in observed.get('courses',[]):
        r=subjects.get(c['code'])
        if r:c['category']=r['category']if c['name']==r['name']else'other'
        elif any(c['code']in spec.get('unresolved',{})for spec in MANIFEST.values()):c['category']='other'
    return observed
