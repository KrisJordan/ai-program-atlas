"""Home-college scope, format boundaries and changed evidence fail closed."""
import hashlib
from pathlib import Path
import pytest
from atlas.adapters import umich_home_policies as a

READERS = {
    'ross-bulletin': (a.parse_ross_bulletin_reviewed, 'ross-bulletin.txt'),
    'ford': (a.parse_ford_reviewed, 'ford-reader.txt'),
    'kinesiology': (a.parse_kinesiology_reviewed, 'kines.txt'),
    'stamps': (a.parse_stamps_reviewed, 'stamps-reader.txt'),
    'public-health': (a.parse_public_health_reviewed, 'sph-reader.txt'),
}

@pytest.mark.parametrize('key', READERS)
def test_reviewed_readers_reject_changed_or_unavailable_text(key, monkeypatch):
    reader, _ = READERS[key]
    synthetic = 'Synthetic independently reviewed ' + key + ' policy text'
    monkeypatch.setitem(a.REVIEWED_HASHES, key, hashlib.sha256(a.normalize(synthetic).encode()).hexdigest())
    observation = reader(synthetic)
    assert observation['id'] == a.PROGRAM_ID
    assert len(observation['requirements']) == len(a.POLICIES[key])
    assert all(r['parent_id'] == 'umich-hcai-root' and r['kind'] == 'note' for r in observation['requirements'])
    assert all(r['source_id'] == a.SOURCE_INFO[key]['id'] for r in observation['requirements'])
    assert not {'curriculum_status', 'curriculum_audit', 'last_verified'} & observation.keys()
    for changed in (synthetic + ' changed', '<h1>Access denied</h1>', '%PDF-1.7', '<h1>Sign in</h1>'):
        with pytest.raises(ValueError): reader(changed)


def test_ross_html_boundaries_and_changes(monkeypatch):
    html = '<main><h1>BBA Minors</h1><p>BBA students may pursue academic minors. Synthetic policy.</p><h2>Other Questions?</h2></main>'
    monkeypatch.setitem(a.REVIEWED_HASHES, 'ross', hashlib.sha256(a.ross_text(html).encode()).hexdigest())
    assert len(a.parse(html)['requirements']) == 4
    for changed in (html.replace('Synthetic', 'Changed'), html.replace('BBA Minors','Different unit'), '<h1>Access denied</h1>', html.replace('Other Questions?', 'New heading')):
        with pytest.raises(ValueError): a.parse(changed)


def test_conditional_scope_and_no_invented_hcai_permissions():
    policies = {key: ' '.join(row[2] for row in rows) for key, rows in a.POLICIES.items()}
    assert 'Required BBA business credits' in policies['ross']
    assert 'not a blanket cap' in policies['ross']
    assert 'written confirmation' in policies['ross-bulletin']
    assert 'does not establish that HCAI accepts partial-course credit' in policies['ross-bulletin']
    assert 'focus-area rule' in policies['ford']
    assert '2025–26' in policies['kinesiology'] and 'later bulletin cohorts is unverified' in policies['kinesiology']
    assert 'One semester before graduation' in policies['stamps']
    assert 'does not establish a course-sharing limit' in policies['public-health']
    assert set(a.POLICIES) == {'ross','ross-bulletin','ford','kinesiology','stamps','public-health'}
    assert sum(map(len,a.POLICIES.values())) == 12
    assert all(s['source_date'] is None for s in a.SOURCE_INFO.values())


@pytest.mark.parametrize('key', READERS)
def test_optional_reviewed_source_cache(key):
    reader, filename = READERS[key]
    path = Path('/tmp/umich-home') / filename
    if not path.exists(): pytest.skip('Optional raw public-source cache stays outside repository')
    assert len(reader(path.read_text())['requirements']) == len(a.POLICIES[key])


def test_optional_ross_html_cache():
    path = Path('/tmp/umich-home/ross.html')
    if not path.exists(): pytest.skip('Optional raw public-source cache stays outside repository')
    assert len(a.parse(path.read_text())['requirements']) == 4
