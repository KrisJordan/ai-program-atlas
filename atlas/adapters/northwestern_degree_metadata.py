"""Source-guarded course observations; manual reviews remain seed-only."""
import hashlib
import json
from pathlib import Path
import re
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, course

MANIFEST = json.loads(Path(__file__).with_name('northwestern_degree_subject_reviews.json').read_text())
REVIEWS = MANIFEST['reviews']


def eligibility(body):
    match = re.search(r'\b(?:Prerequisites?:|Must be taken|May not receive credit|Students (?:may not|are not allowed)|For McCormick|Not open to|Does not count|Recommended Background:|Taught with)', body, re.I)
    return body[match.start():] if match else None


def parse_descriptions(html, *, pid, department):
    soup = BeautifulSoup(html, 'html.parser')
    headings = [clean(h.get_text(' ', strip=True)) for h in soup.find_all('h1') if clean(h.get_text(' ', strip=True)) != 'Academic Catalog']
    if headings != MANIFEST['headings'][department]:
        raise ValueError('Northwestern course directory identity changed: '+department)
    observations = []; digests = {}; changed = []
    for cid, review in REVIEWS.items():
        if review['department'] != department: continue
        code = review['code']
        blocks = [b for b in soup.select('.courseblock') if b.select_one('.courseblocktitle, .couresblocktitle') and clean(b.select_one('.courseblocktitle, .couresblocktitle').get_text(' ', strip=True)).startswith(code+' ')]
        if len(blocks) != 1: raise ValueError('Northwestern exact course missing or duplicated: '+code)
        block = blocks[0]
        label = clean(block.select_one('.courseblocktitle, .couresblocktitle').get_text(' ', strip=True))
        match = re.fullmatch(re.escape(code)+r' (.+) \((\d+(?:\.\d+)?) Units?\)', label)
        if not match or match[1] != review['title']: raise ValueError('Northwestern course title changed: '+code)
        desc = block.select_one('.courseblockdesc')
        body = clean(desc.get_text(' ', strip=True)) if desc else ''
        digest = hashlib.sha256(body.encode()).hexdigest()
        row = course('nw-bse', code, review['program_title'] if review['topic_specific'] else match[1], pid+'-courses-'+department, review['url'], credits=float(match[2]), unit='units')
        row['id'] = cid
        row['prerequisites'] = eligibility(body)
        # A generic special-topics description cannot certify a particular topic.
        if digest == review['description_sha256'] and not review['topic_specific']:
            row['description'] = review['description']; row['category'] = review['category']
        elif digest != review['description_sha256']:
            changed.append(code)
        observations.append(row); digests[cid] = digest
    return dict(id=pid, curriculum_status='partial', courses=observations, requirements=[],
                observed_description_digests=digests,
                notes=['Source-stated units; no quarter-hour conversion. Topic-specific subjects require the exact major-table title, not the generic directory block.'] + (['Changed bodies require review: '+', '.join(sorted(set(changed)))] if changed else []))


def register(pid, sources, parsers):
    for dep in MANIFEST['headings']:
        url = next(r['url'] for r in REVIEWS.values() if r['department'] == dep)
        previous = parsers.get(url)
        if url not in sources: sources += (url,)
        def combined(html, dep=dep, previous=previous):
            result = parse_descriptions(html, pid=pid, department=dep)
            if previous:
                prior = previous(html); seen = {c['id'] for c in result['courses']}
                result['courses'].extend(c for c in prior.get('courses', []) if c['id'] not in seen)
                result['observed_description_digests'].update(prior.get('observed_description_digests', {}))
            return result
        parsers[url] = combined
    return sources
