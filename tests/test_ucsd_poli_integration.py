import importlib
import json
from pathlib import Path
import pytest
from atlas.adapters import ucsd_poli_reviews as m
from atlas.curriculum_profile import requirement_profile

PID = m.SPEC['program_id']


def test_poli_integration_preserves_scope_and_ambiguous_units():
    d = json.loads(Path('data/programs', PID + '.json').read_text())
    c = {x['code']: x for x in d['courses']}
    assert c['POLI 170A']['category'] == 'mathematics'
    assert c['POLI 149']['category'] == 'applications'
    assert c['POLI 143']['category'] == 'human_context'
    assert c['POLI 191A']['credits'] is None
    assert 'Corequisites: POLI 197SD' in c['POLI 194SD']['prerequisites']
    assert 'for POLI 120J' in c['POLI 120J']['prerequisites']
    assert 'for POLI 220J, graduate standing' in c['POLI 120J']['prerequisites']
    assert c['POLI 132B']['category_review']['status'] == 'unclassified'
    assert not any(c['POLI 124']['id'] in g['course_ids'] for g in d.get('course_identity_groups', []))
    assert [requirement_profile(d)[k]['count'] for k in ('required','options','unresolved')] == [8,119,2241]


def test_registered_poli_observer_replays_only_approved_observations():
    source = m.SPEC['sources']['POLI']
    p = Path(source['cache_path'])
    if not p.exists():
        pytest.skip('Optional official chapter cache')
    adapter = importlib.import_module('atlas.adapters.' + PID + '.adapter')
    result = adapter.SOURCE_PARSERS[source['url']](p.read_text())
    assert adapter.SOURCES.count(source['url']) == 1
    assert len(result['courses']) == 113
    assert len(result['source_dispositions']) == 3
    saved = {c['id']: c for c in json.loads(Path('data/programs',PID+'.json').read_text())['courses']}
    for c in result['courses']:
        assert 'category_review' not in c
        assert all(saved[c['id']][k] == v for k,v in c.items() if k != 'notes')
        assert set(c['notes']).issubset(saved[c['id']]['notes'])
