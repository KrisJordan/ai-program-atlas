"""Reviewed USF public details; changed fields require a new human review."""
from functools import partial
import hashlib
import json
from pathlib import Path

from atlas.adapters.national_curriculum_common import clean, content, course

PID = 'university-of-south-florida-artificial-intelligence-bs-degree'
REVIEWS = json.loads(Path(__file__).with_name('remaining_course_reviews.json').read_text())
FIELDS = ('lblDescription', 'lblcredithours', 'lblprereq', 'lblCorequisites',
          'lblcoprereq', 'lblcreq', 'lblOtherInfo')
LABELS = (('Prerequisites', 'lblprereq'), ('Corequisites', 'lblCorequisites'),
          ('Co-prerequisites', 'lblcoprereq'), ('Course restrictions', 'lblcreq'),
          ('Other information', 'lblOtherInfo'))


def parse_reviewed_course(html, review):
    root = content(html, 'Course Details')
    heading = next((clean(h.get_text(' ', strip=True)) for h in root.find_all('h2')
                    if clean(h.get_text()).startswith(review['code'] + ':')), None)
    if heading is None:
        raise ValueError('Reviewed USF course identity is missing')
    values = {}
    for field in FIELDS:
        element = root.find(id='MainContent_' + field)
        if element is None:
            raise ValueError('Reviewed USF field is missing: ' + field)
        values[field] = clean(element.get_text(' ', strip=True))
    digest = hashlib.sha256(json.dumps({'heading': heading, 'fields': values},
                            sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    if digest != review['observed_fields_sha256']:
        raise ValueError('USF course source changed; content review required')
    observed = course('usf', review['code'], heading.split(':', 1)[1].strip(),
                      review['source_id'], review['url'],
                      credits=float(values['lblcredithours']), category=review['category'])
    observed['id'] = review['course_id']
    observed['description'] = '2026–2027 public course inventory: ' + review['summary']
    observed['prerequisites'] = '; '.join(label + ': ' + values[field]
                                         for label, field in LABELS if values[field]) or None
    # Observers do not certify manual taxonomy review or degree eligibility.
    return {'id': PID, 'courses': [observed], 'notes': [
        'Public course detail observations preserve grade, Boolean, permission and concurrent/drop conditions. '
        'Empty fields and normalized units remain unknown. Course metadata do not recertify brochure requirements.'
    ]}


PARSERS = {r['url']: partial(parse_reviewed_course, review=r) for r in REVIEWS}
