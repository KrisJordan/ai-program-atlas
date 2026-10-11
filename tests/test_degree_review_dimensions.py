"""Evidence judgments stay separate from mechanical and whole-degree checks."""
import copy
import json

import pytest

from atlas.degree_audit import (CORE_DIMENSIONS, audit_summary, collect_ledgers,
                                core_review_fingerprint, validate_core_review)
from tests.test_degree_audit import entry
from tests.test_core_review import program


def reviewed_program():
    p = program()
    p['courses'] = [dict(id='programming', category='foundations'),
                    dict(id='ethics', category='human_context')]
    p['requirements'] = [dict(id='core', kind='all', course_ids=['programming']),
                         dict(id='choice', kind='choose_courses', count=1,
                              course_ids=['ethics'])]
    return p


def review(p):
    return dict(program_id=p['id'], reviewer='Independent source reviewer',
                reviewed_at='2026-10-11', reviewed_content_hash=core_review_fingerprint(p),
                dimensions={key: dict(status='verified', summary='Exact cited table reviewed.',
                    evidence=[dict(url='https://catalog.example.edu/ai', locator='Core table')],
                    limitations=[]) for key in CORE_DIMENSIONS},
                expected_course_ids=dict(required=['programming'], options=['ethics'], unresolved=[]),
                expected_profile=dict(required=dict(count=1, categories={'foundations': 1}),
                                      options=dict(count=1, categories=None), unresolved=None))


def ledger(p):
    return {'programs': [{**entry(), 'core_review': review(p)}]}


def test_verified_fixed_review_does_not_promote_blocked_policy_or_full_second_pass():
    p = reviewed_program()
    result = audit_summary(ledger(p), [p])
    assert result['blocked'] == 1
    assert result['audited'] == result['second_pass_verified'] == 0
    assert result['core_review_dimensions']['fixed_requirements'] == {'verified': 1}


def test_choice_count_change_invalidates_review_even_when_profile_counts_do_not_change():
    p = reviewed_program()
    recorded = ledger(p)
    p['requirements'][1]['count'] = 2
    with pytest.raises(ValueError, match='resolved content is stale'):
        audit_summary(recorded, [p])


def test_same_count_wrong_course_identity_is_rejected():
    p = reviewed_program()
    recorded = ledger(p)
    recorded['programs'][0]['core_review']['expected_course_ids']['required'] = ['ethics']
    with pytest.raises(ValueError, match='exact identities are stale'):
        audit_summary(recorded, [p])


def test_unreviewed_category_totals_are_not_compared_to_zero_or_certified():
    p = reviewed_program()
    recorded = ledger(p)
    dimension = recorded['programs'][0]['core_review']['dimensions']['classification']
    dimension.update(status='partial', limitations=['Options subjects have not been independently checked.'])
    result = audit_summary(recorded, [p])
    assert result['core_review_dimensions']['classification'] == {'partial': 1}


@pytest.mark.parametrize('change', ['missing_dimension', 'no_evidence', 'unsafe_url',
                                  'partial_without_limit', 'no_digest'])
def test_invalid_review_evidence_fails_closed(change):
    p = reviewed_program()
    r = review(p)
    d = r['dimensions']['choice_rules']
    if change == 'missing_dimension': del r['dimensions']['classification']
    if change == 'no_evidence': d['evidence'] = []
    if change == 'unsafe_url': d['evidence'][0]['url'] = 'javascript:alert(1)'
    if change == 'partial_without_limit': d['status'] = 'partial'
    if change == 'no_digest': del r['reviewed_content_hash']
    with pytest.raises(ValueError): validate_core_review(r, p['id'])


def test_compiler_attaches_distinct_review_and_rejects_two_review_owners(tmp_path):
    p = reviewed_program()
    (tmp_path/'primary.json').write_text(json.dumps({'programs': [entry()]}))
    payload = json.dumps({'programs': [review(p)]})
    (tmp_path/'independent-core-one.json').write_text(payload)
    result = collect_ledgers(tmp_path, [p])
    assert result['programs'][0]['status'] == 'blocked'
    assert result['programs'][0]['core_review']['reviewer'] == 'Independent source reviewer'
    (tmp_path/'independent-core-two.json').write_text(payload)
    with pytest.raises(ValueError, match='duplicate core review'):
        collect_ledgers(tmp_path, [p])


def test_snapshot_does_not_invalidate_for_optional_course_site_but_does_for_identity():
    p = reviewed_program()
    baseline = core_review_fingerprint(p)
    changed = copy.deepcopy(p)
    changed['courses'][0]['public_site'] = 'https://example.edu/class/'
    assert core_review_fingerprint(changed) == baseline
    changed['courses'][0]['code'] = 'CS 999'
    assert core_review_fingerprint(changed) != baseline
