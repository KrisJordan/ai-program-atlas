import importlib
import json
from pathlib import Path
import pytest
from atlas.adapters import ucsd_vis_reviews as m
from atlas.curriculum_profile import requirement_profile
from atlas.db import validate_program

PID = m.SPEC['program_id']


def test_integrated_visual_arts_distinguishes_computing_criticism_and_unknown_projects():
    d = json.loads(Path('data/programs', PID + '.json').read_text())
    validate_program(d)
    c = {c['code']: c for c in d['courses']}
    assert c['VIS 42']['category'] == 'foundations'
    assert c['VIS 42']['prerequisites'] == 'none.'
    assert c['VIS 6']['category'] == 'human_context'
    assert c['VIS 157']['category_review']['status'] == 'mixed'
    assert c['VIS 190']['credits'] == 8
    for code in ('VIS 160A', 'VIS 160B'):
        assert c[code]['category_review']['status'] == 'unclassified'
        assert 'ICAM majors only' in c[code]['prerequisites']
    for e in m.SPEC['entries']:
        if not e['approved_for_integration']:
            assert c[e['code']]['category_review']['status'] == 'unclassified'
            assert c[e['code']]['name'] == e['listed_name']
    assert [requirement_profile(d)[k]['count'] for k in ('required', 'options', 'unresolved')] == [8, 119, 2241]


def test_current_visual_arts_observer_withholds_twenty_identities():
    s = m.SPEC['sources']['VIS']
    cache = Path(s['cache_path'])
    if not cache.exists():
        pytest.skip('Optional ignored official chapter')
    adapter = importlib.import_module('atlas.adapters.' + PID + '.adapter')
    assert adapter.SOURCES.count(s['url']) == 1
    result = adapter.SOURCE_PARSERS[s['url']](cache.read_text())
    assert len(result['courses']) == 94 and len(result['source_dispositions']) == 20
    saved = {c['id']: c for c in json.loads(Path('data/programs', PID + '.json').read_text())['courses']}
    for c in result['courses']:
        assert 'category_review' not in c
        assert all(saved[c['id']][k] == v for k, v in c.items() if k != 'notes')
        assert set(c['notes']).issubset(saved[c['id']]['notes'])
