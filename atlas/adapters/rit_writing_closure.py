"""Observe public RIT writing policy and example-resource evidence.

The current approved WI inventory is an SIS attribute search, not the UWP's
three course descriptions. No observation promotes an independent audit.
"""
import hashlib
import json
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, content

PID = 'rochester-institute-of-technology-artificial-intelligence-bs-degree'
STUDENTS = 'https://www.rit.edu/writing/students-and-wi'
COMMITTEE = 'https://www.rit.edu/facultysenate/uwc'
FIRST_YEAR = 'https://www.rit.edu/generaleducation/first-year-writing'
SPECS = {
    STUDENTS: ('Students and WI', ['UWRT 150', 'What counts as First Year Writing Intensive?', "What happens if I'm missing a WI course?"]),
    COMMITTEE: ('The University Writing Committee', ['Writing-Intensive FAQs']),
    FIRST_YEAR: ('First Year Writing', []),
}


def parse(html, *, url):
    title, headings = SPECS[url]
    root = content(html, title)
    if not any(clean(h.get_text(' ', strip=True)) == title for h in root.find_all('h1')):
        raise ValueError('RIT writing source heading missing')
    for heading in headings:
        if not any(clean(h.get_text(' ', strip=True)) == heading for h in root.find_all(['h2', 'h3'])):
            raise ValueError('RIT writing section missing: ' + heading)
    text = clean(root.get_text(' ', strip=True))
    if len(text) < 300:
        raise ValueError('RIT writing source incomplete')
    result = {'id': PID, 'courses': [], 'requirements': [],
              'observed_source_content_sha256': hashlib.sha256(text.encode()).hexdigest()}
    if url == STUDENTS:
        h = next(h for h in root.find_all('h2') if clean(h.get_text(' ', strip=True)) == 'UWRT 150')
        section = h.parent
        if 'Course Description' not in section.get_text(' ', strip=True):
            raise ValueError('UWRT 150 description section missing')
        links = [urljoin(url, a['href']) for a in section.select('a[href]')
                 if clean(a.get_text(' ', strip=True)) == 'Sample Syllabus']
        if len(links) != 1 or not links[0].startswith('https://www.rit.edu/writing/'):
            raise ValueError('UWRT 150 sample syllabus link missing or changed host')
        result['courses'] = [{'id': PID + '-uwrt-150', 'code': 'UWRT-150',
                              'public_site': STUDENTS, 'syllabus': links[0]}]
        result['observed_uwrt150_section_sha256'] = hashlib.sha256(clean(section.get_text(' ', strip=True)).encode()).hexdigest()
    return result


def parse_reviewed_document(text, *, key):
    """Manual-format replay after PDF visual or DOCX source review.

    The reviewed manifest supplies the text digest. This never infers a
    current pool from the 2013 science list or treats a sample as a current term.
    """
    manifest = json.loads(Path(__file__).with_name('rit_writing_documents.json').read_text())
    expected_digest = manifest[key]['normalized_text_sha256']
    digest = hashlib.sha256(clean(text).encode()).hexdigest()
    if digest != expected_digest:
        raise ValueError('RIT reviewed document changed; source review required')
    return {'id': PID, 'courses': [], 'requirements': [],
            'observed_document_content_sha256': digest}


def register(sources, parsers):
    for url in SPECS:
        if url not in sources:
            sources.append(url)
        parsers[url] = lambda html, url=url: parse(html, url=url)
