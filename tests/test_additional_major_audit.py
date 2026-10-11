"""Credential review evidence cannot certify or contaminate whole-degree audits."""
import copy
import json

import pytest

from atlas import db
from atlas.additional_major_audit import audit_summary, review_fingerprint, validate_ledger
from atlas.cli import ingest_all
from atlas.site import degree_audit_program
from tests.test_core_review import program
from tests.test_core_dimension_integrity import review as core_review, reviewed_program


def record():
    p = reviewed_program()
    p.update(program_kind='additional_major', award_level='other', title='Artificial Intelligence Additional Major')
    p['major_relationship'] = dict(kind='second_major_only', official_term='Additional major',
        eligibility='Students must have a primary major.', source_ids=['catalog'],
        locator='Eligibility', reviewed_at='2026-10-11')
    for course in p['courses']:
        course.update(code=course['id'].upper(), name=course['id'], source_id='catalog',
                      credits=None, credit_unit='unknown')
    for requirement in p['requirements']:
        requirement.update(title=requirement['id'], source_id='catalog')
    return p


def review(p):
    row = core_review(p)
    row.update(scope='additional_major', scope_summary='Credential requirements and primary-major eligibility only.',
               reviewed_content_hash=review_fingerprint(p),
               eligibility_review=dict(status='verified', summary='A primary major is explicitly required.',
                   limitations=[], evidence=[dict(url='https://catalog.example.edu/ai', locator='Eligibility')]))
    return row


def test_additional_scope_is_separate_and_missing_reviews_are_explicit():
    p = record(); degree = program(); degree['id'] = 'another-degree'
    pending = copy.deepcopy(p); pending['id'] = 'another-additional'
    result = audit_summary({'programs': [review(p)]}, [p, degree, pending])
    assert result['scope_programs'] == 2 and result['reviewed_programs'] == 1
    assert result['dimensions']['fixed_requirements'] == {'verified': 1, 'not_reviewed': 1}
    assert 'audited' not in result
    with pytest.raises(ValueError, match='Unknown or duplicate'):
        validate_ledger({'programs': [review(degree)]}, [degree])


@pytest.mark.parametrize('change', ['choice', 'identity', 'eligibility', 'award', 'title', 'description'])
def test_changed_evidence_invalidates_review_even_with_same_counts(change):
    p = record(); ledger = {'programs': [review(p)]}
    if change == 'choice': p['requirements'][1]['count'] = 2
    elif change == 'identity': p['courses'][0]['code'] = 'CS 999'
    elif change == 'eligibility': p['major_relationship']['eligibility'] = 'A different admitted cohort.'
    elif change == 'award': p['award_level'] = 'BS'
    elif change == 'title': p['title'] = 'Applied Artificial Intelligence Additional Major'
    else: p['courses'][0]['description'] = 'Changed subject evidence.'
    with pytest.raises(ValueError, match='resolved content is stale'):
        validate_ledger(ledger, [p])


@pytest.mark.parametrize('mutation', ['duplicate', 'wrong_ids', 'wrong_count', 'scope', 'eligibility'])
def test_malformed_review_rejected(mutation):
    p = record(); row = review(p); ledger = {'programs': [row]}
    if mutation == 'duplicate': ledger['programs'].append(copy.deepcopy(row))
    elif mutation == 'wrong_ids': row['expected_course_ids']['required'] = ['ethics']
    elif mutation == 'wrong_count': row['expected_profile']['required']['count'] = 9
    elif mutation == 'scope': row['scope'] = 'degree'
    else: row['eligibility_review']['evidence'] = []
    with pytest.raises(ValueError): validate_ledger(ledger, [p])


def test_atomic_ingest_export_reruns_and_stale_rollback(tmp_path):
    p = record(); row = review(p)
    source = tmp_path/'data'; (source/'programs').mkdir(parents=True)
    program_path = source/'programs'/'additional.json'
    audit_path = source/'additional-major-audit.json'
    program_path.write_text(json.dumps(p)); audit_path.write_text(json.dumps({'programs': [row]}))
    conn = db.connect(tmp_path/'atlas.sqlite'); db.migrate(conn)
    assert ingest_all(conn, source) == 1
    data = db.export_data(conn)
    assert data['programs'][0]['additional_major_audit'] == row
    assert data['meta']['degree_audit']['scope_programs'] == 0
    assert ingest_all(conn, source) == 0
    p['major_relationship']['eligibility'] = 'Changed eligibility requires review.'
    program_path.write_text(json.dumps(p))
    with pytest.raises(ValueError, match='resolved content is stale'): ingest_all(conn, source)
    assert db.export_data(conn) == data
    assert not conn.execute('PRAGMA foreign_key_check').fetchall()
    conn.close()


def test_detail_shows_scoped_statuses_eligibility_and_escaped_evidence():
    p = record(); p['additional_major_audit'] = review(p)
    p['additional_major_audit']['scope_summary'] = '<unsafe> Credential only.'
    html = degree_audit_program(p)
    assert 'Additional-major correctness review' in html
    assert 'does not certify the complete host degree' in html
    assert 'Second-major eligibility' in html
    assert 'Whole-degree correctness audit' not in html
    assert '&lt;unsafe&gt;' in html and '<unsafe>' not in html
    assert html.count('class="review-dimension-status"') == 4
