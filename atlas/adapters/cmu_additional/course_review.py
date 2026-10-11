"""Owned CMU additional-major observations pinned to independently read descriptions."""
import hashlib
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import course, text, requirement

PID = 'cmu-additional-ai'
REVIEWS = json.loads(Path(__file__).with_name('reviewed_courses.json').read_text())
DIRECTORIES = {r['url']: r['directory_heading'] for r in REVIEWS.values()}


def blocks(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    if not any(text(h) == DIRECTORIES[url] for h in soup.find_all(['h1', 'h2'])):
        raise ValueError('Additional-major course directory heading changed')
    year = re.search(r'(20\d{2}[-–]20\d{2})\s+Catalog', text(soup))
    if not year:
        raise ValueError('Additional-major course edition missing')
    records = {}
    for block in soup.select('dl.courseblock'):
        if not block.dt or not block.dd:
            raise ValueError('Additional-major course block structure changed')
        match = re.fullmatch(r'(\d{2}-\d{3})\s+(.+)', text(block.dt))
        if not match or match[1] not in REVIEWS or REVIEWS[match[1]]['url'] != url:
            continue
        code, name = match.groups()
        if code in records:
            raise ValueError('Duplicate additional-major course code: ' + code)
        body = BeautifulSoup(str(block.dd), 'html.parser')
        for br in body.find_all('br'):
            br.replace_with('\n')
        lines = [' '.join(line.split()) for line in body.get_text(' ', strip=False).splitlines() if line.strip()]
        units = re.fullmatch(r'[^:]+:\s*(\d+(?:\.\d+)?) units', lines[0])
        prereqs = [re.sub(r'^Prerequisites?:\s*', '', line) for line in lines if re.match(r'^Prerequisites?:', line)]
        if len(prereqs) > 1:
            raise ValueError('Repeated prerequisite field: ' + code)
        description = ' '.join(line for line in lines[1:] if not re.match(r'^(Prerequisites?|Corequisites?|Course Website):', line))
        records[code] = dict(name=name, credits=float(units[1]) if units else None,
                             prerequisites=prereqs[0] if prereqs else None,
                             description_digest=hashlib.sha256(description.encode()).hexdigest())
    expected = {c for c, r in REVIEWS.items() if r['url'] == url}
    if set(records) != expected:
        raise ValueError('Additional-major course inventory changed')
    return year[1], records


def parse(html, url):
    year, facts = blocks(html, url)
    courses = []
    requirements = []
    for code, fact in facts.items():
        reviewed = REVIEWS[code]
        same = (year == reviewed['catalog_year'] and fact['name'] == reviewed['name']
                and fact['description_digest'] == reviewed['description_digest'])
        c = course(code, fact['name'], reviewed['source_id'], url,
                   reviewed['category'] if same else 'other', fact['credits'])
        c['prerequisites'] = fact['prerequisites']
        if reviewed.get('course_entry_note'):
            if not same:
                raise ValueError('Additional-major course-entry evidence changed: ' + code)
            requirements.append(requirement(PID, 'course-entry-' + code,
                'Course-entry condition: ' + code, reviewed['source_id'], kind='note',
                category='other', summary=reviewed['course_entry_note']))
        # No category_review, manual audit, or refreshed certification is emitted.
        courses.append(c)
    return dict(id=PID, catalog_year=year, curriculum_status='partial', courses=courses,
                requirements=requirements, observed_description_digests={c: f['description_digest'] for c, f in facts.items()})


def classify_observed(observation):
    # Requirements pages contain titles, not course content. Their candidates
    # stay unclassified until a guarded directory observation is considered.
    for c in observation.get('courses', []):
        c['category'] = 'other'
    return observation


def register(sources, parsers):
    for url in DIRECTORIES:
        if url not in sources:
            sources.append(url)
        parsers[url] = lambda html, url=url: parse(html, url)
