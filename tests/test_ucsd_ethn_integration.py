import importlib
import json
from pathlib import Path
import pytest
from atlas.adapters import ucsd_ethn_reviews as m
from atlas.curriculum_profile import requirement_profile
from atlas.db import validate_program

PID = m.SPEC['program_id']


def test_integrated_ethn_keeps_unknown_topics_and_course_credit_scope():
    d = json.loads(Path('data/programs', PID + '.json').read_text())
    validate_program(d)
    c = {c['code']: c for c in d['courses']}
    assert c['ETHN 110']['category'] == 'human_context'
    assert c['ETHN 179']['credits'] == 4
    assert any('eight' in n.lower() or '8' in n for n in c['ETHN 179']['notes'])
    assert all(c[code]['category_review']['status'] == 'mixed' for code in ('ETHN 114B', 'ETHN 136', 'ETHN 146A', 'ETHN 162'))
    assert c['ETHN 189']['category_review']['status'] == 'unclassified'
    assert any('latin american' in n.lower() for n in c['ETHN 189']['notes'])
    assert all(c['ETHN ' + code]['category_review']['status'] == 'unclassified' for code in ('107', '124', '154', '190', '1A', '1B', '1C'))
    assert c['ETHN 140']['id'] != c['ETHN 140A']['id']
    assert [requirement_profile(d)[k]['count'] for k in ('required', 'options', 'unresolved')] == [8, 119, 2240]


def test_current_ethn_observer_registration_and_saved_facts():
    s = m.SPEC['sources']['ETHN']
    cache = Path(s['cache_path'])
    if not cache.exists():
        pytest.skip('Optional ignored official chapter')
    adapter = importlib.import_module('atlas.adapters.' + PID + '.adapter')
    assert adapter.SOURCES.count(s['url']) == 1
    result = adapter.SOURCE_PARSERS[s['url']](cache.read_text())
    assert len(result['courses']) == 110 and len(result['source_dispositions']) == 10
    saved = {c['id']: c for c in json.loads(Path('data/programs', PID + '.json').read_text())['courses']}
    for c in result['courses']:
        assert 'category_review' not in c
        assert all(saved[c['id']][k] == v for k, v in c.items() if k != 'notes')
        assert set(c['notes']).issubset(saved[c['id']]['notes'])
