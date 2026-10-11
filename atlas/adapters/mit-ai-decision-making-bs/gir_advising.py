"""Public advising and course-page observations, with bounded manual reuse."""
import hashlib
import json
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, content, course, rule

PID = 'mit-ai-decision-making-bs'
SCIENCE = 'https://firstyear.mit.edu/academics-exploration/general-institute-requirements-girs/science-core/'
CALCULUS = 'https://canvas.mit.edu/courses/39048/assignments/syllabus'
REVIEWS = json.loads(Path(__file__).with_name('reviewed_gir_advising.json').read_text())


def observed(html, url):
    if url == SCIENCE:
        root = content(html, 'Science Core')
        sections = {}
        for heading in ['8.01 Physics I: Classical Mechanics', 'Physics II: 8.02 Electricity and Magnetism']:
            h = next((h for h in root.find_all('h3') if clean(h.get_text()) == heading), None)
            if h is None:
                raise ValueError('Physics advising section missing: ' + heading)
            parts = [heading]
            for node in h.next_siblings:
                if getattr(node, 'name', None) == 'h3':
                    break
                if getattr(node, 'get_text', None):
                    parts.append(clean(node.get_text(' ', strip=True)))
            sections[heading[:4]] = ' '.join(parts)
        result = {}
        for code in ['8.01', '8.01L', '8.011', '8.012', '8.02', '8.022']:
            evidence = sections['8.01' if code.startswith('8.01') else 'Phys']
            if code not in evidence:
                raise ValueError('Physics advising subject missing: ' + code)
            result[code] = evidence
        return result
    root = BeautifulSoup(html, 'html.parser')
    title = clean(root.title.get_text()) if root.title else ''
    body = root.find(id='course_syllabus')
    if title != 'Syllabus for 18.01L Calculus' or body is None:
        raise ValueError('Public calculus syllabus identity changed')
    term = 'Fall Term (AY 2026-2027)'
    if term not in clean(root.get_text(' ', strip=True)):
        raise ValueError('Public calculus syllabus term changed')
    return {'18.01L': title + ' ' + term + ' ' + clean(body.get_text(' ', strip=True))}


def parse(html, url):
    evidence = observed(html, url)
    rows = []
    digests = {}
    rules = []
    sid = PID + ('-science-advising' if url == SCIENCE else '-calculus-public-syllabus')
    for code, text in evidence.items():
        digest = hashlib.sha256(text.encode()).hexdigest()
        saved = REVIEWS[code]
        c = course('mit-ai-gir', code, None, sid, url, unit='units')
        if saved['digest'] == digest:
            c.update(name=saved['name'], category=saved['category'],
                     description=saved['summary'], prerequisites=saved['prerequisites'],
                     notes=saved['notes'])
            if code == '18.01L':
                c['public_site'] = url
                c['syllabus'] = url
            if code in {'8.01', '8.02'}:
                rules.append(rule('mit-ai-gir-advising-' + code.replace('.', '-'),
                                  'Conditional Physics ' + ('I' if code == '8.01' else 'II') + ' routes',
                                  sid, kind='note', summary=saved['policy_summary']))
        rows.append(c)
        digests[c['id']] = digest
    if url == SCIENCE:
        text = clean(BeautifulSoup(html, 'html.parser').get_text(' ', strip=True))
        if 'Only for students who successfully complete 18.01A in first half of fall term' in text:
            rules.append(rule('mit-ai-gir-advising-accelerated-calculus',
                              'First-year accelerated calculus sequence eligibility', sid,
                              kind='note', summary='The first-year advising page limits its 18.02A route to students who successfully complete 18.01A in the first half of fall. The mathematics department also states general prerequisite equivalence across forms of 18.01; that general statement does not waive the specific sequence condition.'))
    return dict(id=PID, courses=rows, requirements=rules,
                observed_gir_advising_digests=digests)


SOURCE_PARSERS = {url: (lambda html, url=url: parse(html, url)) for url in [SCIENCE, CALCULUS]}
