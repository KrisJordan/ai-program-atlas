"""Narrow public-resource observations; catalog course facts remain separate."""
import hashlib
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from atlas.adapters.northeastern_courseleaf import clean, slug

AUTHORITY = 'https://dbp.io/'
SITE = 'https://neu-pdi.github.io/cs2000-public-resources/'
SYLLABUS = SITE + 'syllabus/'
TERM_SCOPE = 'Dates are for Fall 2026, Boston & Oakland campuses; they will differ for other semesters or campuses.'


def parse_resource(html, *, program_id, url):
    soup = BeautifulSoup(html, 'html.parser')
    title = clean(soup.title) if soup.title else ''
    if soup.find('input', attrs={'type': 'password'}) or re.search(r'^(?:Sign in|Access denied|Just a moment)', title, re.I):
        raise ValueError('Protected resource is not public course evidence')
    main = soup.find('main')
    if main is None:
        raise ValueError('Expected course-resource main content missing')
    courses = []
    if url == AUTHORITY:
        if not all(s in clean(main) for s in ('Associate Teaching Professor', 'Khoury College of Computer Sciences', 'Northeastern University')):
            raise ValueError('Expected Northeastern instructor affiliation missing')
        heading = main.find('h3', id='teaching')
        if not heading:
            raise ValueError('Instructor teaching section missing')
        matched = []
        for node in heading.find_next_siblings():
            if node.name in {'h1', 'h2', 'h3'}:
                break
            if node.name != 'p' or not clean(node).startswith('Fall 2026:'):
                continue
            links = [a for a in node.find_all('a') if urljoin(url, a.get('href', '')) == SITE
                     and clean(a).startswith('CS2000: Introduction to Program Design and Implementation')]
            matched.extend(links)
        if len(matched) != 1:
            raise ValueError('Expected current instructor course link missing or ambiguous')
        source = program_id + '-cs2000-fall-2026-instructor'
        note = 'Instructor teaching page links the CS 2000 public site for Fall 2026; this is authorship/offering evidence, not a degree launch date.'
    elif url == SITE:
        h1 = main.find('h1')
        if not h1 or clean(h1) != 'CS 2000: Introduction to Program Design and Implementation':
            raise ValueError('CS 2000 course identity missing')
        if not any(clean(p) == TERM_SCOPE for p in main.find_all('p')):
            raise ValueError('Expected Fall 2026 Boston/Oakland offering scope changed')
        if not any(urljoin(url, a.get('href', '')) == SYLLABUS and clean(a) == 'Syllabus' for a in soup.find_all('a')):
            raise ValueError('Expected public syllabus link missing')
        source = program_id + '-cs2000-fall-2026-site'
        courses = [dict(id=program_id+'-cs-2000', code='CS 2000', public_site=SITE)]
        note = 'Public CS 2000 site explicitly covers Fall 2026 Boston and Oakland. This is an example offering, not a promise for every term or campus.'
    elif url == SYLLABUS:
        if title != 'Syllabus | NEU CS 2000 Public Resources':
            raise ValueError('Expected CS 2000 syllabus identity missing')
        for section, code, prefix in [('classes', 'CS2000', 'Each class period'), ('labs', 'CS2001', 'The lab period')]:
            heading = main.find('h4', id=section)
            paragraph = heading.find_next_sibling() if heading else None
            if not paragraph or paragraph.name != 'p' or not clean(paragraph).startswith(prefix) or not re.search(r'\((?:of )?'+code+r'\)', clean(paragraph)):
                raise ValueError('Expected syllabus class/lab identity missing')
        if not any(urljoin(url, a.get('href', '')) == SITE for a in soup.find_all('a')):
            raise ValueError('Syllabus public-site relationship missing')
        source = program_id + '-cs2000-2001-public-syllabus'
        courses = [dict(id=program_id+'-'+slug(code), code=code, syllabus=SYLLABUS) for code in ('CS 2000', 'CS 2001')]
        courses[1]['public_site'] = SITE
        note = 'Public syllabus explicitly covers CS 2000 classes and CS 2001 labs. It is linked by the separately verified Fall 2026 site but does not itself state an offering year; catalog credits and prerequisites remain separate.'
    else:
        raise ValueError('Unreviewed course resource URL')
    for course in courses:
        course.update(source_id=source, url=url)
    return dict(id=program_id, courses=courses, requirements=[], curriculum_status='partial',
                observed_resource_digest=hashlib.sha256(clean(main).encode()).hexdigest(), notes=[note])


def register_resources(program_id):
    return {url: (lambda html, url=url: parse_resource(html, program_id=program_id, url=url))
            for url in (AUTHORITY, SITE, SYLLABUS)}
