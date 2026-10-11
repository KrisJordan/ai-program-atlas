"""Review-gated observations from the current Rutgers catalog's rendered tabs.

HTTP SSR renders only the first tab. Call these parsers with an actual public
rendered course-tab capture; a normal SSR landing must fail rather than replay
cached metadata. The manual manifest explicitly maps reviewed NJIT identities.
"""
import hashlib
import json
import re
from functools import partial
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, course
from atlas.adapters.njit_degree_policies import PID

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())
BASE = 'https://newark-undergrad-26-27.catalogs.rutgers.edu/schools/school-arts-sciences-newark/programs-faculty-and-courses/history-510-and-512'
URLS = {'510': BASE + '#courses-history-5101', '512': BASE + '#courses-american-history-5121'}
HEADINGS = {'510': 'Courses (History 510)', '512': 'Courses (American History 512)'}


def parse(html, subject):
    soup = BeautifulSoup(html, 'html.parser')
    selected = soup.select('[role=tab][aria-selected=true]')
    panels = soup.select('[role=tabpanel]')
    if len(selected) != 1 or clean(selected[0].get_text(' ', strip=True)) != HEADINGS[subject] or len(panels) != 1:
        raise ValueError('Actual selected Rutgers history course tab required; landing or other tab is insufficient')
    panel = panels[0]
    if not panel.find(['h2', 'h3'], string=HEADINGS[subject]):
        raise ValueError('Rutgers history course heading missing')
    wanted = {code for code, s in SPEC.items() if s['source_url'] == URLS[subject]}
    seen, courses, conflicts = set(), [], []
    for block in panel.select('p'):
        text = clean(block.get_text(' ', strip=True))
        match = re.match(r'21:(510|512):(\d+(?:,\d+)*) (.*?) \(([^)]+)\)(.*)', text)
        if not match or match[1] != subject:
            continue
        for n in match[2].split(','):
            code = 'R' + subject + ' ' + n
            if code in {'R510 489', 'R512 364'}:
                raise ValueError('Previously missing Rutgers identity now appears; review required: ' + code)
            if code not in wanted:
                continue
            if code in seen:
                raise ValueError('Duplicate reviewed Rutgers identity: ' + code)
            seen.add(code)
            spec = SPEC[code]
            if match[3] != spec['title'] or hashlib.sha256(text.encode()).hexdigest() != spec['digest']:
                raise ValueError('Rutgers history content changed; review required: ' + code)
            if spec['identity_conflict']:
                conflicts.append({'njit_code': code, 'njit_title': spec['njit_title'],
                                  'rutgers_code': spec['rutgers_code'], 'rutgers_title': match[3]})
                continue
            c = course('njit', code, match[3], PID + '-rutgers-history-' + subject,
                       URLS[subject], spec['credits'], 'semester_hours', 'human_context')
            c['description'] = spec['description']
            c['prerequisites'] = spec['prerequisites']
            courses.append(c)
    if seen != wanted:
        raise ValueError('Reviewed Rutgers history identities missing')
    return {'id': PID, 'courses': courses, 'requirements': [], 'observed_identity_conflicts': conflicts}


SOURCE_PARSERS = {url: partial(parse, subject=subject) for subject, url in URLS.items()}


POLICY_URL = 'https://policies.rutgers.edu/B.aspx?BookId=11905&PageId=459222'
POLICY_DIGEST = 'f0450f349297101ee770119ddbfe46c5c1a5ecb6e012a85c5f9daccee0569f09'

def parse_credit_policy(html):
    root = BeautifulSoup(html, 'html.parser').select_one('#divContent459222')
    if root is None or hashlib.sha256(clean(root.get_text(' ', strip=True)).encode()).hexdigest() != POLICY_DIGEST:
        raise ValueError('Rutgers rendered unit-of-credit policy missing or changed')
    return {'id': PID, 'observed_credit_unit': 'semester_hours',
            'observed_policy_scope': 'Rutgers course credit is the unit of record across schools subject to the explicitly listed professional-school exceptions; a standard fifteen-week semester supports the credit-hour definition. Laboratory clock hours are not counted one-for-one.'}

SOURCE_PARSERS[POLICY_URL] = parse_credit_policy
