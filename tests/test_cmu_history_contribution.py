"""Independent History contribution; synthetic mutation test, optional raw-cache replay."""
import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest
from atlas.adapters.cmu_bs.reviewed_departments import observe

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / 'atlas/adapters/cmu_bs/reviewed_history_subjects.json').read_text())
SPEC = next(iter(MANIFEST.values()))


def test_history_review_keeps_missing_descriptions_and_source_conflicts_explicit():
    assert len(SPEC['subjects']) == 52
    assert set(SPEC['unresolved']) == {'79-156', '79-177', '79-244', '79-286'}
    assert set(SPEC['subjects']) | set(SPEC['unresolved']) == set(SPEC['review_metadata']['claimed_codes'])
    assert set(SPEC['subjects']).isdisjoint(SPEC['unresolved'])
    assert set(SPEC['review_metadata']['title_differences']) == {'79-240', '79-300', '79-329'}
    for row in SPEC['subjects'].values():
        assert row['category'] == 'human_context' and row['status'] == 'reviewed'
        assert row['description'] and row['rationale'] and len(row['description_digest']) == 64
        assert (row['credits'], row['credit_unit'], row['catalog_year']) == (9, 'units', '2026-2027')
        assert row['prerequisites'] is None
    for row in SPEC['unresolved'].values():
        assert row['description'] is None and row['credits'] is None
        assert row['status'] == 'unclassified'
    qatar = {code for code, notes in SPEC['conditions'].items()
             if any('Qatar campus' in n['summary'] for n in notes)}
    assert qatar == {'79-253', '79-293', '79-361', '79-378', '79-391', '79-392', '79-393', '79-465'}


def test_history_contribution_uses_changed_response_metadata_without_replaying_review():
    spec = deepcopy(SPEC)
    spec['subjects'] = {'79-101': deepcopy(SPEC['subjects']['79-101'])}
    spec['conditions'] = {}
    description = 'Synthetic historical inquiry content.'
    spec['subjects']['79-101']['description_digest'] = hashlib.sha256(description.encode()).hexdigest()
    html = ('<h1>Department of History Courses</h1><p>2026-2027 Catalog</p>'
            '<dl class="courseblock"><dt>79-101 Making History: How to Think About the Past (and Present)</dt>'
            '<dd>Fall: 9 units<br>' + description + '<br>Prerequisite: 79-001</dd></dl>')
    c = observe(html, spec)['courses'][0]
    assert (c['credits'], c['prerequisites'], c['category']) == (9, '79-001', 'human_context')
    assert c['description'] is None and 'category_review' not in c
    changed = observe(html.replace(description, 'A changed substantive topic.').replace('9 units', '6 units'), spec)['courses'][0]
    assert changed['category'] == 'other' and changed['credits'] == 6


def test_history_optional_actual_cache_replay():
    cache = Path('/tmp/cmu-remaining-9.html')
    if not cache.exists():
        pytest.skip('Raw official cache deliberately excluded from repository')
    observed = observe(cache.read_text(), SPEC)
    assert observed['catalog_year'] == '2026-2027'
    assert len(observed['courses']) == 52
    for c in observed['courses']:
        expected = SPEC['subjects'][c['code']]
        assert (c['name'], c['credits'], c['prerequisites'], c['category']) == (
            expected['name'], expected['credits'], expected['prerequisites'], expected['category'])
        assert observed['observed_description_digests'][c['code']] == expected['description_digest']
    assert len(observed['requirements']) == sum(map(len, SPEC['conditions'].values()))
