"""Reviewed general-education identities, with independent source freshness guards."""
import hashlib
import json
from pathlib import Path
import re
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, course
from atlas.adapters.case_degree_metadata import BASE, HEADINGS

REVIEWS=json.loads(Path(__file__).with_name('case_uger_subject_reviews.json').read_text())
DEPARTMENTS={**HEADINGS,'aiqs':'Academic Inquiry Seminar (AIQS)'}
# Exact fragments selected from reviewed blocks; additions require source review.
EXTRA_RULES={
 'CSDS 101':['The recommended pre-requisite is comfort with high school algebra.'],
 'ENGR 350U':["The class is open to all majors but enrollment is by application and instructors' consent."],
 'ENGR 350':['Participation by instructor consent.','Registration is limited to students who are active members of the project team.'],
 'ENGR 395':['In order to enroll, a student must already be part of an approved project team.'],
 'MATH 352':['In order to register, a student must first obtain the consent of a Capstone Advisor.'],
 'STAT 395':['A student must obtain consent of a capstone advisor to register for the course.'],
 'PHIL 222':['Open to all students (no pre-requisites)'],
 'PHIL 366':['The only pre-requisite to enroll in this course is curiosity, although students may benefit from having previously taken courses in philosophy, neuroscience, psychology and/or computer science.'],
}


def eligibility(body,code):
    # Extract only explicit rule sentences, never all trailing descriptive prose.
    labels=r'(?:Prereq(?:uisites?)?(?: or Coreq)?\s*:|Coreq\s*:|Recommended (?:preparation|background)\s*:|Credit given for only|Credit for at most|A student may (?:not receive|receive) credit|Students cannot earn credit|Students may earn credit for only)'
    pieces=[m[0] for m in re.finditer(r'\b'+labels+r'[^.]*\.',body,re.I)]
    for fragment in EXTRA_RULES.get(code,[]):
        if fragment in body:pieces.append(fragment)
    return ' '.join(dict.fromkeys(pieces)) or None


def parse_descriptions(html,*,pid,award,department):
    soup=BeautifulSoup(html,'html.parser')
    if [clean(h.get_text(' ',strip=True)) for h in soup.find_all('h1')]!=[DEPARTMENTS[department]]:
        raise ValueError('Case UGER department identity changed: '+department)
    courses=[];digests={};changed=[]
    for code,review in REVIEWS.items():
        if not code.startswith(department.upper()+' ') or award not in review['course_ids']:continue
        blocks=[b for b in soup.select('.courseblock') if b.select_one('.courseblocktitle') and clean(b.select_one('.courseblocktitle').get_text(' ',strip=True)).startswith(code+'. ')]
        if len(blocks)!=1:raise ValueError('Case UGER course missing or duplicated: '+code)
        b=blocks[0];header=clean(b.select_one('.courseblocktitle').get_text(' ',strip=True));desc=b.select_one('.courseblockdesc')
        match=re.fullmatch(re.escape(code)+r'\. (.+)\. (\d+(?:\.\d+)?) Units?\.',header)
        if not match or desc is None or match[1]!=review['title']:raise ValueError('Case UGER reviewed identity changed: '+code)
        body=clean(desc.get_text(' ',strip=True));digest=hashlib.sha256(body.encode()).hexdigest()
        row=course('unused',code,match[1],'case-uger-courses-'+department,BASE+department+'/',credits=float(match[2]),unit='unknown');row['id']=review['course_ids'][award]
        row['prerequisites']=eligibility(body,code)
        if digest==review['description_sha256']:
            row['description']=review['description'];row['category']=review['category']
        else:
            row['description']=None;row['category']='other';changed.append(code)
        courses.append(row);digests[row['id']]=digest
    return dict(id=pid,curriculum_status='partial',courses=courses,requirements=[],observed_description_digests=digests,notes=['UGER course descriptions are distinct from approval-table membership. Units are not independently normalized; no prerequisite statement means unknown. No independent review emitted.']+(['Changed description needs review: '+', '.join(changed)] if changed else []))


def register(pid,award,sources,parsers):
    for department in DEPARTMENTS:
        if not any(c.startswith(department.upper()+' ') and award in r['course_ids'] for c,r in REVIEWS.items()):continue
        url=BASE+department+'/'
        previous=parsers.get(url)
        def parse(html,department=department,previous=previous):
            current=parse_descriptions(html,pid=pid,award=award,department=department)
            if previous:
                earlier=previous(html)
                current['courses']=earlier['courses']+current['courses']
                current['observed_description_digests']={**earlier.get('observed_description_digests',{}),**current['observed_description_digests']}
                current['notes']=earlier.get('notes',[])+current['notes']
            return current
        parsers[url]=parse
        if url not in sources:sources+=(url,)
    return sources
