"""Source-reviewed content must not change conditional college course roles."""
import importlib
import json
from pathlib import Path
import pytest
from atlas.adapters import ucsd_soci_reviews, ucsd_anth_ansc_reviews
from atlas.curriculum_profile import requirement_profile
from atlas.db import validate_program

PID = ucsd_soci_reviews.SPEC['program_id']


def seed():
    return json.loads(Path('data/programs', PID + '.json').read_text())


def test_source_facts_preserve_context_and_unknown_identities():
    d = seed()
    validate_program(d)
    courses = {c['code']: c for c in d['courses']}
    profile = requirement_profile(d)
    assert [profile[k]['count'] for k in ('required', 'options', 'unresolved')] == [8, 119, 2241]
    assert {k: v for k, v in profile['unresolved']['categories'].items() if v} == {
        'other': 397, 'human_context': 1418, 'applications': 349,
        'foundations': 13, 'systems': 24, 'mathematics': 37, 'ai_ml': 3,
    }
    assert courses['SOCI 105']['credits'] == 6
    assert 'SOCI for SOCI 105' in courses['SOCI 105']['prerequisites']
    assert courses['SOCI 194']['credits'] == 4
    assert courses['SOCI 194']['category'] == 'other'
    assert courses['ANTH 128A']['credits'] == 6
    assert courses['ANTH 43']['category_review']['status'] == 'mixed'
    assert 'B+ or better' in courses['ANTH 196B']['prerequisites']
    assert all(courses[code]['category'] == 'applications' for code in ('SOCI 102', 'SOCI 108', 'ANSC 138', 'ANSC 171'))
    assert courses['SOCI 171']['name'] == 'Technology and Science'
    assert 'Southeast Asia' in courses['ANSC 190GS']['name']
    for code in ('SOCI 171', 'ANSC 190GS', 'SOCI 123', 'SOCI 144P', 'SOCI 158J', 'ANSC 116', 'ANTH 44'):
        assert courses[code]['category_review']['status'] == 'unclassified'


@pytest.mark.parametrize('module', [ucsd_soci_reviews, ucsd_anth_ansc_reviews])
def test_guarded_observers_registered_without_replaying_review(module):
    adapter = importlib.import_module('atlas.adapters.' + PID + '.adapter')
    courses = {c['id']: c for c in seed()['courses']}
    for url, source in {s['url']: s for s in module.SPEC['sources'].values()}.items():
        assert adapter.SOURCES.count(url) == 1
        cache = Path(source['cache_path'])
        if not cache.exists():
            pytest.skip('Optional ignored official chapter capture')
        result = adapter.SOURCE_PARSERS[url](cache.read_text())
        assert set(result) == {'id', 'courses', 'source_dispositions'}
        assert all('category_review' not in c for c in result['courses'])
        for observation in result['courses']:
            saved = courses[observation['id']]
            assert all(saved[key] == value for key, value in observation.items() if key != 'notes')
            assert set(observation['notes']).issubset(saved['notes'])
        withheld = {e['id'] for e in module.SPEC['entries'] if not e['approved_for_integration']}
        assert not withheld.intersection(c['id'] for c in result['courses'])
