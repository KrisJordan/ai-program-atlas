"""BS-only observations of quantitative directories, history and public resources."""
import hashlib
import re
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import course, text

PID = 'cmu-bs-ai'
MATH = 'https://coursecatalog.web.cmu.edu/schools-colleges/melloncollegeofscience/departmentofmathematicalsciences/courses/'
STATS = 'https://coursecatalog.web.cmu.edu/schools-colleges/dietrichcollegeofhumanitiesandsocialsciences/departmentofstatistics/courses/'
HISTORY = 'https://coursecatalog.web.cmu.edu/schools-colleges/schoolofcomputerscience/artificialintelligence/'
DIRECTORIES = {
    MATH: ('Department of Mathematical Sciences Courses', 'cmu-bs-ai-mathematics-directory', ('21-120', '21-122', '21-127', '21-241', '21-259', '21-266', '21-268', '21-269', '21-325', '21-425')),
    STATS: ('Department of Statistics and Data Science Courses', 'cmu-bs-ai-statistics-directory', ('36-218', '36-225', '36-226', '36-235', '36-236', '36-401', '36-402')),
}
RESOURCES = {
    'https://www.math.cmu.edu/~jmackey/151_128/welcome.html': ('15-151', 'Mathematical Foundations for Computer Science', 'Fall 2023', 'cmu-15151-fall-2023-site', False),
    'https://www.math.cmu.edu/~jmackey/151_128/syll.html': ('15-151', 'Mathematical Foundations for Computer Science', 'Fall 2023', 'cmu-15151-fall-2023-syllabus', True),
    'https://www.cs.cmu.edu/~harchol/PnC/class.html': ('15-259', 'Probability and Computing', 'FALL 2026', 'cmu-15259-fall-2026-site', False),
    'https://www.cs.cmu.edu/~15122/home.shtml': ('15-122', 'Principles of Imperative Computation', 'Fall 2026', 'cmu-15122-fall-2026-site', False),
    'https://www.cs.cmu.edu/~15122/syllabus.shtml': ('15-122', 'Principles of Imperative Computation', 'Fall 2026', 'cmu-15122-fall-2026-syllabus', True),
    'https://www.cs.cmu.edu/~15210/': ('15-210', 'Parallel and Sequential Data Structures and Algorithms', 'Fall 26', 'cmu-15210-fall-2026-site', False),
    'https://www.cs.cmu.edu/~15210/policies.html': ('15-210', 'Parallel and Sequential Data Structures and Algorithms', 'Fall 26', 'cmu-15210-fall-2026-policies', False),
    'https://www.cs251.com': ('15-251', 'Great Ideas in Theoretical Computer Science', None, 'cmu-15251-undated-site', False),
}


def _document(html):
    soup = BeautifulSoup(html, 'html.parser')
    if soup.find('input', attrs={'type': 'password'}) or (soup.title and re.search(r'^(Access denied|Sign in|Just a moment)', text(soup.title), re.I)):
        raise ValueError('Protected page is not course evidence')
    for node in soup.find_all(['script', 'style']):
        node.decompose()
    return soup


def parse_directory(html, url):
    heading, source, codes = DIRECTORIES[url]
    soup = _document(html)
    if not any(text(h) == heading for h in soup.find_all(['h1', 'h2'])):
        raise ValueError('CMU quantitative directory heading missing')
    year = re.search(r'(20\d{2}[-–]20\d{2})\s+Catalog', text(soup))
    if not year:
        raise ValueError('CMU quantitative directory edition missing')
    records, digests, eligibility = {}, {}, {}
    for block in soup.find_all('dl', class_='courseblock'):
        title, body = block.find('dt'), block.find('dd')
        if not title or not body:
            raise ValueError('CMU course block structure changed')
        match = re.fullmatch(r'(\d{2}-\d{3})\s+(.+)', text(title))
        if not match or match[1] not in codes:
            continue
        code, name = match.groups()
        if code in records:
            raise ValueError('Duplicate CMU course: ' + code)
        for br in body.find_all('br'):
            br.replace_with('\n')
        lines = [' '.join(x.split()) for x in body.get_text(' ', strip=False).splitlines() if x.strip()]
        units = re.fullmatch(r'[^:]+:\s*(\d+(?:\.\d+)?) units', lines[0])
        record = course(code, name, source, url, category='mathematics', credits=float(units[1]) if units else None)
        prereqs = [re.sub(r'^Prerequisites?:\s*', '', line) for line in lines if re.match(r'^Prerequisites?:', line)]
        if len(prereqs) > 1:
            raise ValueError('Repeated prerequisite field: ' + code)
        record['prerequisites'] = prereqs[0] if prereqs else None
        description = ' '.join(line for line in lines[1:] if not re.match(r'^(Prerequisites?|Corequisites?|Course Website):', line))
        # Include prose eligibility/recommendations in observed evidence so changes
        # trigger review; never turn a recommendation into a required prerequisite.
        eligibility[code] = [s.strip() for s in re.split(r'(?<=[.!?])\s+', description) if re.search(r'open only|not open|sophomore standing|strongly recommend|highly recommend|not an official prerequisite|CS majors|grade of [BC]|grade [BC]|major or minor|majors .*minors', s, re.I)]
        digests[code] = hashlib.sha256(description.encode()).hexdigest()
        records[code] = record
    if not records:
        raise ValueError('No requested CMU quantitative courses observed')
    return dict(id=PID, catalog_year=year[1], curriculum_status='partial', courses=list(records.values()), requirements=[], observed_description_digests=digests, observed_eligibility=eligibility,
                notes=['Course metadata only; omitted prerequisites and descriptions remain unknown. Inline eligibility and recommendations require review separately from formal prerequisite fields.'])


def parse_history(html):
    soup = _document(html)
    main = soup.find('main') or soup.find(id='content') or soup
    if not any(text(h) == 'Artificial Intelligence Program' for h in main.find_all(['h1', 'h2'])):
        raise ValueError('CMU AI program heading missing')
    value = text(main)
    # Retrospective start statement, deliberately not a future launch announcement.
    match = re.search(r"bachelor[’']s degree in Artificial Intelligence, which started in ((?:Fall|Spring|Summer) 20\d{2})", value)
    if not match or 'BSAI' not in value:
        raise ValueError('Explicit BSAI retrospective start statement missing')
    return dict(id=PID, curriculum_status='partial', courses=[], requirements=[], first_offered=dict(value=match[1], precision='term', evidence_url=HISTORY, uncertainty=None))


def parse_resource(html, url):
    code, name, term, source, syllabus = RESOURCES[url]
    soup = _document(html)
    value = text(soup)
    headings = ' '.join(text(h) for h in soup.find_all(['title', 'h1', 'h2']))
    identity = code in headings if code != '15-251' else name in headings and 'CS251 at CMU' in value
    if not identity or (term and term not in value):
        raise ValueError('Core course identity or reviewed term missing')
    syllabus_sections = ['Syllabus for 15-151 and 21-128', 'Course Outline:', 'Tentative week by week schedule'] if code == '15-151' else ['Course syllabus', 'Grading', 'Prerequisites', 'Learning Objectives']
    if syllabus and not all(x in value for x in syllabus_sections):
        raise ValueError('Public syllabus content missing')
    c = course(code, name, source, url, category='foundations')
    if not url.endswith(('syllabus.shtml', 'policies.html', 'syll.html')):
        c['public_site'] = url
    if syllabus:
        c['syllabus'] = url
    return dict(id=PID, curriculum_status='partial', courses=[c], requirements=[], observed_resource_digest=hashlib.sha256(value.encode()).hexdigest(), notes=[(term or 'Undated') + ' public resource only; no inferred catalog prerequisites, offering date or program-level outcomes. The 15-210 policies page is not its Ed-hosted syllabus.'])


def register(sources, parsers):
    for url in DIRECTORIES:
        sources.append(url)
        parsers[url] = lambda html, url=url: parse_directory(html, url)
    sources.append(HISTORY)
    parsers[HISTORY] = parse_history
    for url in RESOURCES:
        sources.append(url)
        parsers[url] = lambda html, url=url: parse_resource(html, url)

MINOR = 'https://coursecatalog.web.cmu.edu/schools-colleges/dietrichcollegeofhumanitiesandsocialsciences/departmentofstatistics/statistics-data-science-minor/'
OPTIONS = 'https://coursecatalog.web.cmu.edu/aboutcmu/undergraduate-options/additional-majors-dual-degrees-minors/'


def parse_minor_access(html, url):
    soup = _document(html)
    main = soup.find('main') or soup.find(id='content') or soup
    value = text(main)
    heading = 'Statistics and Data Science, Minor' if url == MINOR else 'Additional Majors, Dual Degrees and Minors'
    if not any(text(h) == heading for h in main.find_all(['h1', 'h2'])):
        raise ValueError('CMU minor policy heading missing')
    if url == OPTIONS:
        match = re.search(r'Unless otherwise indicated, minors are generally open to all university undergraduate students\.', value)
        if not match:
            raise ValueError('University minor eligibility statement changed')
        observation = match[0]
    else:
        if not all(x in value for x in ['36-235', '36-236', 'Double Counting', 'three statistics courses', 'primary major']):
            raise ValueError('Statistics minor conditional route or double-counting policy changed')
        observation = value[value.index('Double Counting'):value.index('Sample Programs for the Minor')]
    return dict(id=PID, curriculum_status='partial', courses=[], requirements=[], observed_minor_access=observation,
                observed_policy_digest=hashlib.sha256(value.encode()).hexdigest(), notes=['Conditional minor access evidence only. This source does not certify unrestricted BSAI enrollment in statistics courses.'])
