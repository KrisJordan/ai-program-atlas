"""Current quantitative descriptions; interdisciplinary rows are not auto-math."""
import json
from pathlib import Path
from .core_enrichment import DIRECTORIES, parse_directory, STATS
from .common import requirement

SUBJECTS = json.loads(Path(__file__).with_name('reviewed_quantitative_subjects.json').read_text())


def parse(html, url):
    observed = parse_directory(html, url)
    expected = set(DIRECTORIES[url][2])
    if {c['code']for c in observed['courses']} != expected:
        raise ValueError('Reviewed quantitative course inventory changed')
    for c in observed['courses']:
        r = SUBJECTS[c['code']]
        same = c['name'] == r['name'] and observed['observed_description_digests'][c['code']] == r['description_digest']
        c['category'] = r['category'] if same else 'other'
    if url == STATS:
        facts = observed['observed_eligibility']
        if not any('receive at least a B' in x for x in facts['36-218']):
            raise ValueError('Statistics direct-entry eligibility changed')
        if not any('sophomore standing' in x for x in facts['36-225']):
            raise ValueError('Statistics standing restriction changed')
        source = DIRECTORIES[url][1]
        observed['requirements'].append(requirement('cmu-bs-ai','statistics-direct-entry','Statistics course-entry routes',source,kind='note',summary='Students outside a Statistics major/minor who earn at least B in36-218 may enter36-401 directly. Statistics majors/minors instead complete36-226. The descriptions require at least C in36-226 or36-236 for progression to36-401. These are conditional entry rules; no course is added to every AI degree route.'))
        observed['requirements'].append(requirement('cmu-bs-ai','statistics-standing','Standing for introductory probability',source,kind='note',summary='36-225 requires sophomore standing or above. The separate36-235/236 option retains its published Statistics-status, prior-credit and grade restrictions, represented in the conditional probability-route note.'))
    return observed


def classify_titles(observed):
    for c in observed.get('courses', []):
        r = SUBJECTS.get(c['code'])
        if r:
            c['category'] = r['category'] if c['name'] == r['name'] else 'other'
    return observed
