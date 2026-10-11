"""Observed metadata for the 78 independently reviewed Case major identities.

Descriptions/category rationales are original editorial summaries. Exact source
body hashes guard their reuse; changed evidence is queued without stale judgment.
Independent category_review remains seed-only.
"""
import hashlib
import json
from pathlib import Path
import re
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, course

BASE = 'https://bulletin.case.edu/course-descriptions/'
REVIEWS = json.loads(Path(__file__).with_name('case_degree_subject_reviews.json').read_text())
HEADINGS = {
 'csds':'Computer and Data Sciences (CSDS)', 'dsci':'Applied Data Science (DSCI)',
 'econ':'Economics (ECON)', 'ecse':'Electrical, Computer, and Systems Engineering (ECSE)',
 'engr':'Engineering Science (ENGR)', 'humn':'Humanities (HUMN)', 'math':'Mathematics (MATH)',
 'mbap':'Master of Business Administration (MBAP)', 'phil':'Philosophy (PHIL)',
 'phys':'Physics (PHYS)', 'pqhs':'Population & Quantitative Health Sciences (PQHS)',
 'scmg':'Supply Chain Management (SCMG)', 'stat':'Statistics (STAT)',
 'sybb':'Systems Biology and Bioinformatics (SYBB)',
}


def eligibility(body):
    """Keep explicit prerequisite/permission/credit exclusions, never infer none."""
    # The full suffix also retains qualifiers and cross-list text following a rule.
    match = re.search(r'\b(?:Prereq(?:uisites?)?(?: or Coreq)?\s*:|Coreq\s*:|Recommended (?:preparation|background)|Admission to this course|Credit for at most|Students may earn credit for only|Students may not (?:receive|earn) credit)', body, re.I)
    return body[match.start():] if match else None


def parse_descriptions(html, *, pid, award, department):
    soup = BeautifulSoup(html, 'html.parser')
    if [clean(h.get_text(' ',strip=True)) for h in soup.find_all('h1')] != [HEADINGS[department]]:
        raise ValueError('Case department identity changed: '+department)
    observations=[]; digests={}; changed=[]
    for code,review in REVIEWS.items():
        if not code.startswith(department.upper()+' ') or award not in review['awards']:continue
        blocks=[b for b in soup.select('.courseblock') if b.select_one('.courseblocktitle') and clean(b.select_one('.courseblocktitle').get_text(' ',strip=True)).startswith(code+'. ')]
        if len(blocks)!=1:raise ValueError('Case course block missing or duplicated: '+code)
        block=blocks[0]; title=clean(block.select_one('.courseblocktitle').get_text(' ',strip=True))
        match=re.fullmatch(re.escape(code)+r'\. (.+)\. (\d+(?:\.\d+)?) Units?\.',title)
        desc=block.select_one('.courseblockdesc')
        if not match or desc is None:raise ValueError('Case course structure changed: '+code)
        if match[1]!=review['title']:raise ValueError('Case reviewed title changed: '+code)
        body=clean(desc.get_text(' ',strip=True)); digest=hashlib.sha256(body.encode()).hexdigest()
        row=course('case-'+award.lower(),code,match[1],'case-degree-courses-'+department,BASE+department+'/',credits=float(match[2]),unit='unknown')
        row['prerequisites']=eligibility(body)
        if digest==review['description_sha256']:
            row['description']=review['description']; row['category']=review['category']
        else:
            row['description']=None; row['category']='other'; changed.append(code)
        observations.append(row);digests[row['id']]=digest
    return dict(id=pid,curriculum_status='partial',courses=observations,requirements=[],
                observed_description_digests=digests,
                notes=['Amounts are source-stated Units; no independent semester-hour conversion. Missing prerequisite field means unknown. No independent category/completeness audit emitted.']+(['Changed description requires review: '+', '.join(changed)] if changed else []))


def register(pid, award, sources, parsers):
    for department in HEADINGS:
        if not any(c.startswith(department.upper()+' ') and award in r['awards'] for c,r in REVIEWS.items()):continue
        url=BASE+department+'/'
        if url not in sources:sources+=(url,)
        parsers[url]=lambda html,department=department:parse_descriptions(html,pid=pid,award=award,department=department)
    return sources
