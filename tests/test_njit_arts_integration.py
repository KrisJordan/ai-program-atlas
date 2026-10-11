import hashlib
import importlib.util
import json
from pathlib import Path

import pytest
from atlas import db
from atlas.adapters import njit_arts_communication_reviews as m
from atlas.curriculum_profile import requirement_profile


def test_integrated_arts_preserve_roles_identity_and_manual_review_scope():
    p = json.loads(Path('data/programs', m.PID + '.json').read_text())
    db.validate_program(p)
    courses = {c['code']: c for c in p['courses']}
    for code, evidence in m.SPEC.items():
        c = courses[code]
        assert c['category'] == evidence['category']
        assert c['category_review']['status'] == evidence['review_status']
        assert c['category_review']['source_ids'] == [m.SOURCE_ID]
    assert sum('category_review' in c for c in p['courses']) == 220
    assert len([c for c in p['courses'] if 'category_review' not in c]) == 161
    assert all(c['code'].startswith('R') for c in p['courses'] if 'category_review' not in c)
    profile = requirement_profile(p)
    assert profile['required']['count'] == 32
    assert profile['options']['count'] == 348
    assert profile['options']['source_record_count'] == 349
    assert courses['LIT 370']['description'] is None
    assert courses['THTR 261']['prerequisites'] == 'Departmental approval required.'


def test_combined_actual_humanities_source_has_disjoint_observations():
    cache = Path('.cache/http', hashlib.sha256(m.URL.encode()).hexdigest() + '.body')
    if not cache.exists():
        pytest.skip('Ignored source cache unavailable')
    spec = importlib.util.spec_from_file_location('njit_integrated_adapter', Path('atlas/adapters', m.PID, 'adapter.py'))
    a = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(a)
    result = a.SOURCE_PARSERS[m.URL](cache.read_text())
    assert len(result['courses']) == len({c['id'] for c in result['courses']}) == 125
    assert len(result['requirements']) == 5  # Original conditional GER allocation rules retained.
    assert len(result['observed_ger_allocations']) > 0
    assert all('category_review' not in c for c in result['courses'])
    assert 'curriculum_audit' not in result
