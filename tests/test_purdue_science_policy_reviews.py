"""Synthetic complete-block guards plus optional exact cached policy replay."""
import copy
import hashlib
from pathlib import Path

import pytest

from atlas.adapters import purdue_science_policy_reviews as policy

KEYS = tuple(policy.SPEC['sources'])


@pytest.fixture
def synthetic(monkeypatch):
    spec = copy.deepcopy(policy.SPEC)
    pages = {}
    for key, source in spec['sources'].items():
        html = (
            '<main id="content"><div class="breadcrumbs">Old navigation</div>'
            '<div class="page-sidebar"><nav>Sidebar</nav></div>'
            f'<section><h1>{source["heading"]}</h1>'
            '<p>Eligibility requires approval and a grade threshold.</p>'
            '<p>Withdrawals count; exceptions are conditional.</p>'
            '<a href="/public-rule">Published rule</a></section></main>'
        )
        source['block_sha256'] = policy.policy_block(html)[1]
        pages[key] = html
    monkeypatch.setattr(policy, 'SPEC', spec)
    return pages


@pytest.mark.parametrize('key', KEYS)
def test_reviewed_observation_scope(synthetic, key):
    result = policy.parse(synthetic[key], key=key)
    assert set(result) == {'id', 'requirements'}
    assert result['id'] == 'purdue-ai-bs'
    assert len(result['requirements']) == len(policy.SPEC['sources'][key]['notes'])
    for row in result['requirements']:
        assert row['kind'] == 'note'
        assert row['count'] is None and row['credits'] is None
        assert row['credit_unit'] == 'semester_hours'
        assert row['category'] == 'other'
        assert row['course_ids'] == []
        assert row['source_text'] is None
        assert row['source_id'] == policy.SPEC['sources'][key]['id']


@pytest.mark.parametrize('change', [
    lambda s: s.replace('grade threshold', 'lower grade threshold'),
    lambda s: s.replace('<p>Withdrawals count; exceptions are conditional.</p>', ''),
    lambda s: s.replace('</section>', '<p>New exemption.</p></section>'),
    lambda s: s.replace('/public-rule', '/different-rule'),
    lambda s: s.replace('<main id="content">', '<main>'),
    lambda s: s.replace('</main>', '<h1>Second policy</h1></main>'),
    lambda s: s + '<input type="password">',
])
def test_rejects_partial_changed_or_access_evidence(synthetic, change):
    with pytest.raises(ValueError):
        policy.parse(change(synthetic['course-repeat']), key='course-repeat')


def test_navigation_and_whitespace_are_not_policy(synthetic):
    html = synthetic['core-overlap'].replace('Old navigation', 'New navigation')
    html = html.replace('Eligibility requires', 'Eligibility\n  requires')
    assert policy.parse(html, key='core-overlap')['requirements']


def test_scope_does_not_expand(synthetic):
    with pytest.raises(ValueError, match='scope'):
        policy.parse(synthetic['advising'], key='advising', pid='purdue-other-bs')
    with pytest.raises(ValueError, match='scope'):
        policy.parse(synthetic['advising'], key='other')
    with pytest.raises(ValueError, match='changed'):
        policy.parse(synthetic['advising'], key='course-repeat')


def test_manifest_scope_and_material_qualifications():
    assert len(KEYS) == 6
    notes = [n for s in policy.SPEC['sources'].values() for n in s['notes']]
    assert len(notes) == 15
    assert len({n['suffix'] for n in notes}) == 15
    text = {n['suffix']: n['summary'] for n in notes}
    assert 'W counts' in text['repeat-attempt-limit']
    assert '3.0' in text['credit-raise-eligibility']
    assert '21' in text['credit-raise-review']
    assert '5000-level' in text['pass-not-pass-scope']
    assert '20%' in text['pass-not-pass-limits'] and 'C-' in text['pass-not-pass-limits']
    assert 'two courses' in text['pass-not-pass-limits']
    assert 'Only for Spring 2020' in text['pass-not-pass-spring-2020']
    assert 'seven weeks' in text['math-transfer-prerequisite']
    assert 'year-round' in text['math-exam-delivery']


@pytest.mark.parametrize('key', KEYS)
def test_optional_cached_full_source_replay(key):
    source = policy.SPEC['sources'][key]
    path = Path('.cache/research/purdue-science-policy') / (
        hashlib.sha256(source['url'].encode()).hexdigest() + '.body')
    if not path.exists():
        pytest.skip('Optional ignored Purdue public policy cache absent')
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == source['content_hash']
    observed = policy.PARSERS[source['url']](data.decode())
    assert len(observed['requirements']) == len(source['notes'])
