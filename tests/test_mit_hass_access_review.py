"""Concentration access observations must not import another credential's rules."""
from collections import Counter
from datetime import datetime
from importlib import import_module
import json
from pathlib import Path

import pytest

m = import_module('atlas.adapters.mit-ai-decision-making-bs.hass_access_review')
ROOT = Path(__file__).resolve().parents[1]


def fixture(key):
    _, title, markers = m.CATALOGS[key]
    return '<main><h1>' + title + '</h1>' + ''.join('<p>' + x + '</p>' for x in markers) + '<h2>Minor requirements</h2><p>Six subjects including a seminar.</p></main>'


@pytest.mark.parametrize('key', m.CATALOGS)
def test_catalog_context_is_not_a_concentration_inventory(key):
    observed = m.parse_catalog(key, fixture(key))
    assert set(observed) == {'id', 'requirements'}
    assert len(observed['requirements']) == 1
    rule = observed['requirements'][0]
    assert rule['kind'] == 'note' and rule['course_ids'] == []
    assert rule['count'] is None
    assert 'not a finding that no concentration exists' in rule['summary']


@pytest.mark.parametrize('key', m.CATALOGS)
def test_new_concentration_section_requires_fresh_review(key):
    html = fixture(key).replace('</main>', '<h2>Concentration requirements</h2><p>Three subjects.</p></main>')
    with pytest.raises(ValueError, match='concentration-specific'):
        m.parse_catalog(key, html)
    with pytest.raises(ValueError):
        m.parse_catalog(key, fixture(key).replace(m.CATALOGS[key][2][0], 'Changed credential'))


def test_field_review_has_evidence_for_every_status_and_preserves_open_questions():
    review = json.loads((ROOT / 'research/mit-hass-field-review-2026-10-11.json').read_text())
    program = json.loads((ROOT / 'data/programs/mit-ai-decision-making-bs.json').read_text())
    sources = {s['id']: s for s in program['sources']}
    rows = review['fields']
    assert len({r['field'] for r in rows}) == len(rows)
    assert dict(Counter(r['status'] for r in rows)) == review['counts']
    expected_accessible = {'Music', 'Theater Arts'}
    accessible = {r['field'] for r in rows if r['status'] == 'accessible_unreviewed'}
    assert expected_accessible <= accessible
    for row in rows:
        if row['field'] in {'Comparative Media Studies', 'Education', 'English Language Studies (ELS)', 'Writing'}:
            assert row['previous_barrier'] and row['browser_followup']
            assert row['status'] != 'department_detail_blocked'
    questions = {r['field'] for r in rows if r['status'] == 'mapped_with_source_question'}
    assert {'Ethics', 'Art, Culture, and Technology', 'Urban Studies'} <= questions
    for row in rows:
        assert row['directory_url'].startswith(('http://', 'https://'))
        assert row['next_action'] and row['source_ids'] and row['inspected_sources']
        assert set(row['source_ids']) <= sources.keys()
        for observed in row['inspected_sources']:
            source = sources[observed['id']]
            assert observed['url'] == source['url']
            assert datetime.fromisoformat(observed['fetched_at']).tzinfo is not None
        if row['status'] == 'accessible_unreviewed':
            assert row['previous_barrier'] and row['transport_correction']
            assert '/program/degree-requirements/' in row['next_action']
