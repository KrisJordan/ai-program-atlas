"""Source-specific Case minor course observations from public department catalogs.

Descriptions are reviewer paraphrases in seeds; digests flag changed source prose.
Search endpoints are robots-blocked and are not used here.
"""
import hashlib
import re
from bs4 import BeautifulSoup
from atlas.adapters.business_society_minors import clean, course, slug

APPLIED = 'case-applied-ai-minor'
TECHNICAL = 'case-western-reserve-university-artificial-intelligence-minor-minor'
BASE = 'https://bulletin.case.edu/course-descriptions/'
POOLS = {
    APPLIED: {
        'csds': ['CSDS 101', 'CSDS 102', 'CSDS 225'],
        'cogs': ['COGS/ENGL/HUMN/RLGN 250', 'COGS 330/430/DSCI 330/430'],
        'phil': ['PHIL 210', 'PHIL 393'],
        'bafi': ['BAFI 335', 'BAFI 351', 'BAFI 357', 'BAFI 432'],
        'buai': ['BUAI 446'], 'econ': ['ECON 327', 'ECON 334', 'ECON 380', 'ECON 381'],
        'ftec': ['FTEC 412'], 'humn': ['HUMN 305/405'], 'mbap': ['MBAP 429H'],
        'pqhs': ['PQHS 416'], 'sass': ['SASS 471', 'SASS 472'],
        'scmg': ['SCMG 462', 'SCMG 463'], 'sybb': ['SYBB 464'],
    },
    TECHNICAL: {
        'csds': ['CSDS 330', 'CSDS 340', 'CSDS 225', 'CSDS 102'],
        'cogs': ['COGS/ENGL/HUMN/RLGN 250'], 'phil': ['PHIL 210', 'PHIL 393'],
    },
}
ALIASES = {
    'COGS/ENGL/HUMN/RLGN 250': ['COGS 250', 'ENGL 250', 'HUMN 250', 'RLGN 250'],
    'COGS 330/430/DSCI 330/430': ['COGS 330', 'COGS 430', 'DSCI 330', 'DSCI 430'],
    'HUMN 305/405': ['HUMN 305', 'HUMN 405'],
}


def parse_department(html, *, pid, department):
    soup = BeautifulSoup(html, 'html.parser')
    headings = [clean(h.get_text(' ', strip=True)) for h in soup.find_all('h1')]
    if len(headings) != 1 or not headings[0].endswith('(' + department.upper() + ')'):
        raise ValueError('Case department identity missing or changed')
    courses = []; digests = {}
    for code in POOLS[pid][department]:
        canonical = ALIASES.get(code, [code])[0]
        found = []
        for block in soup.find_all(class_='courseblock'):
            title = block.find(class_='courseblocktitle')
            label = clean(title.get_text(' ', strip=True)) if title else ''
            if label.startswith(canonical + '. '):
                found.append((block, label))
        if len(found) != 1:
            raise ValueError('Exact Case course block missing or duplicated: ' + canonical)
        block, label = found[0]
        match = re.fullmatch(re.escape(canonical) + r'\. (.+)\. (\d+(?:\.\d+)?) Units?\.', label)
        if not match:
            raise ValueError('Unrecognized Case title/credit structure: ' + canonical)
        desc = block.find(class_='courseblockdesc')
        if desc is None:
            raise ValueError('Case course description missing: ' + canonical)
        value = clean(desc.get_text(' ', strip=True))
        if code in ALIASES:
            offered = re.search(r'Offered as (.+?)\.', value)
            if not offered or not all(re.search(r'\b' + re.escape(alias) + r'\b', offered[1]) for alias in ALIASES[code]):
                raise ValueError('Case cross-list identity changed: ' + code)
        prerequisite = re.search(r'\bPrereq(?: or Coreq)?:.*$', value)
        prerequisite = prerequisite[0] if prerequisite else None
        # Two catalog conditions occur in the prose rather than a Prereq field.
        if canonical == 'CSDS 101':
            extra = re.search(r'The recommended pre-requisite is [^.]+\.', value)
            if extra and extra[0] not in (prerequisite or ''): prerequisite = ' '.join(filter(None, [prerequisite, extra[0]]))
        elif canonical == 'CSDS 225':
            extra = re.search(r'The class is open to all majors, but [^.]+\.', value)
            if extra and extra[0] not in (prerequisite or ''): prerequisite = ' '.join(filter(None, [prerequisite, extra[0]]))
        elif canonical == 'FTEC 412':
            extra = re.search(r'Coding experience [^.]+\.', value)
            if extra and extra[0] not in (prerequisite or ''): prerequisite = ' '.join(filter(None, [prerequisite, extra[0]]))
        c = course(code, match[1], pid, 'case-courses-' + department, BASE + department + '/', float(match[2]), 'semester_hours')
        if pid == TECHNICAL: c['id'] = 'case-western-reserve-' + slug(code)
        c['prerequisites'] = prerequisite
        courses.append(c)
        digests[c['id']] = hashlib.sha256(value.encode()).hexdigest()
    return dict(id=pid, curriculum_status='partial', courses=courses, requirements=[],
                observed_description_digests=digests,
                notes=['Course amounts retain catalog Units wording; semester-hour normalization follows the separately reviewed university credit definition. Missing prerequisite text remains unknown. Cross-listed options use the named canonical course block and its explicit Offered as aliases.'])


def register(pid, sources, parsers):
    for department in POOLS[pid]:
        url = BASE + department + '/'
        if url not in sources: sources.append(url)
        parsers[url] = lambda html, department=department: parse_department(html, pid=pid, department=department)
