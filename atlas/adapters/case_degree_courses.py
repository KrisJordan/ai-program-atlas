"""Case degree core identities and source-specific course-description observations.

Editorial categories below are exact reviewed identities, not CSDS-wide heuristics.
Independent category_review objects live only in the reviewed seeds, never parsers.
"""
import hashlib
import re
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, course

BASE = 'https://bulletin.case.edu/course-descriptions/'
# Exact titles guard previously reviewed identity; renamed/new courses need review.
IDENTITIES = {
    'CSDS 132': ('Programming in Java', 'foundations'),
    'CSDS 134': ('Programming in Python', 'foundations'),
    'CSDS 233': ('Introduction to Data Structures', 'foundations'),
    'CSDS 237': ('The Python Programming Language', 'foundations'),
    'CSDS 302': ('Discrete Mathematics', 'mathematics'),
    'CSDS 310': ('Algorithms', 'foundations'),
    'CSDS 330': ('Introduction to Artificial Intelligence', 'ai_ml'),
    'CSDS 340': ('Introduction to Machine Learning', 'ai_ml'),
    'CSDS 395A': ('Senior Project in Artificial Intelligence', 'ai_ml'),
    'MATH 121': ('Calculus for Science and Engineering I', 'mathematics'),
    'MATH 307': ('Linear Algebra', 'mathematics'),
    'ENGR 399': ('Impact of Engineering on Society', 'human_context'),
}
# Description markers check meaning as well as identity on the independent source.
MARKERS = {
    'CSDS 132': ('algorithmic problem solving', 'object-oriented design'),
    'CSDS 134': ('introduction to computer science and programming', 'algorithmic problem solving'),
    'CSDS 233': ('different representations of data', 'asymptotic analysis'),
    'CSDS 237': ('programming in python', 'object-oriented programming'),
    'CSDS 302': ('discrete mathematics', 'mathematical induction'),
    'CSDS 310': ('algorithm design and analysis', 'dynamic programming'),
    'CSDS 330': ('artificial intelligence', 'knowledge representation'),
    'CSDS 340': ('algorithms for machine learning', 'implementation'),
    'CSDS 395A': ('artificial intelligence models', 'practical applications'),
    'ENGR 399': ('ethical and professional responsibilities', 'disparate impacts'),
}


def classify_observed(courses):
    """Correct exact Case identities; other major identities require description review."""
    for row in courses:
        expected = IDENTITIES.get(row['code'])
        if expected:
            if clean(row['name'] or '') != expected[0]:
                raise ValueError('Reviewed Case course title changed: ' + row['code'])
            row['category'] = expected[1]
        else:
            row['category'] = 'other'
    return courses


def parse_descriptions(html, *, pid, award, department):
    s = BeautifulSoup(html, 'html.parser')
    heading = {'csds': 'Computer and Data Sciences (CSDS)', 'engr': 'Engineering Science (ENGR)'}[department]
    if [clean(h.get_text(' ', strip=True)) for h in s.find_all('h1')] != [heading]:
        raise ValueError('Case course-description identity changed')
    codes = [c for c in MARKERS if c.startswith(department.upper() + ' ')]
    if department == 'engr' and award != 'BS':
        raise ValueError('Engineering requirement belongs to the BS audit')
    observations = []; digests = {}
    for code in codes:
        blocks = [b for b in s.select('.courseblock') if b.select_one('.courseblocktitle') and clean(b.select_one('.courseblocktitle').get_text(' ', strip=True)).startswith(code + '. ')]
        if len(blocks) != 1: raise ValueError('Exact Case course block missing or duplicated: ' + code)
        block = blocks[0]
        title = clean(block.select_one('.courseblocktitle').get_text(' ', strip=True))
        match = re.fullmatch(re.escape(code) + r'\. (.+)\. (\d+(?:\.\d+)?) Units?\.', title)
        desc = block.select_one('.courseblockdesc')
        if not match or desc is None: raise ValueError('Case course title/credit/description changed: ' + code)
        body = clean(desc.get_text(' ', strip=True))
        if any(marker not in body.casefold() for marker in MARKERS[code]):
            raise ValueError('Reviewed Case subject evidence changed: ' + code)
        c = course('case-' + award.lower(), code, match[1], 'case-degree-courses-' + department,
                   BASE + department + '/', credits=float(match[2]), unit='unknown')
        prerequisite = re.search(r'\bPrereq(?: or Coreq)?:.*$', body)
        c['prerequisites'] = prerequisite[0] if prerequisite else None
        observations.append(c)
        digests[c['id']] = hashlib.sha256(body.encode()).hexdigest()
    classify_observed(observations)
    return dict(id=pid, curriculum_status='partial', courses=observations, requirements=[],
                observed_description_digests=digests,
                notes=['Course block amounts say Units; the observation does not independently normalize those units. Missing prerequisite fields mean unknown. No independent review or completeness audit is emitted.'])


def register(pid, award, sources, parsers):
    for department in ['csds'] + (['engr'] if award == 'BS' else []):
        url = BASE + department + '/'
        sources += (url,)
        parsers[url] = lambda html, department=department: parse_descriptions(html, pid=pid, award=award, department=department)
    return sources
