"""Observed Stevens fixed-course fields; manual taxonomy reviews stay in the manifest.

Only settled public Course Information / Eligibility HTML is accepted. Initial
Coursedog placeholders and stale pre-transition descriptions are not evidence.
"""
import hashlib
import json
from functools import partial
from pathlib import Path

from bs4 import BeautifulSoup

from atlas.adapters.national_curriculum_common import clean
from atlas.adapters.stevens_degree_course_review import PID, field

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())


def parse(html, code, eligibility=False):
    entry = SPEC[code]
    soup = BeautifulSoup(html, 'html.parser')
    root = soup.select_one('article.flex-1')
    heading = root.find('h1') if root else None
    titles = [clean(h.get_text(' ', strip=True)) for h in root.select('h2')] if root else []
    if not heading or clean(heading.get_text(' ', strip=True)) != code or entry['name'] not in titles:
        raise ValueError('Stevens fixed-course identity changed: ' + code)
    selected = root.select_one('[role="tab"][aria-selected="true"]')
    expected_tab = 'Eligibility' if eligibility else 'Course Information'
    if not selected or clean(selected.get_text()) != expected_tab:
        raise ValueError('Stevens source is not the settled selected tab: ' + code)
    label = 'Student Eligibility Rule' if eligibility else 'Course Description'
    value = field(root, label)
    digest = hashlib.sha256(value.encode()).hexdigest() if value is not None else None
    key = 'eligibility_digest' if eligibility else 'description_digest'
    if digest != entry[key] or (not eligibility and value is None):
        raise ValueError('Stevens reviewed field changed: ' + code)
    course = {'id': entry['id'], 'code': code}
    if eligibility:
        if field(root, 'Course Description') is not None:
            raise ValueError('Stevens eligibility transition has not settled: ' + code)
        # Null means no published rule was observed, never unrestricted entry.
        prior = entry.get('description_prerequisites')
        course.update(prerequisites=(prior + ' Published eligibility: ' + value) if prior and value else value,
                      source_id=entry['source_id'] + '-eligibility', url=entry['eligibility_url'])
    else:
        credit_text = field(root, 'Credits')
        if credit_text is None or not credit_text.isdigit() or int(credit_text) != entry['credits']:
            raise ValueError('Stevens reviewed credits changed: ' + code)
        course.update(name=entry['name'], description=entry['description'], category=entry['category'],
                      credits=int(credit_text), credit_unit='unknown', source_id=entry['source_id'],
                      url=entry['url'], prerequisites=entry.get('description_prerequisites'))
    return {'id': PID, 'courses': [course]}


def register(sources, parsers):
    """Register disjoint per-course URLs without replacing another observer."""
    for code, entry in SPEC.items():
        for eligibility, key in ((False, 'url'), (True, 'eligibility_url')):
            url = entry[key]
            current = parsers.get(url)
            if current is not None:
                if (isinstance(current, partial) and current.func is parse
                        and current.keywords == {'code': code, 'eligibility': eligibility}):
                    continue
                raise ValueError('Stevens source parser already registered: ' + url)
            if url not in sources:
                sources.append(url)
            parsers[url] = partial(parse, code=code, eligibility=eligibility)
