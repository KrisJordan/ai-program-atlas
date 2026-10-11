"""Offline guard tests use synthetic source rows, never committed catalog prose."""
import csv
import hashlib
import io
import json
from copy import deepcopy
from pathlib import Path

import pytest

from atlas.adapters import ucsb_ge_performing_arts_reviews as adapter


def csv_text(rows):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


@pytest.fixture
def synthetic(monkeypatch):
    rows = [dict(zip((
        'Subject & Prefix', 'Course Number', 'Full Course Title',
        'Course Description', 'Advisor Enrollment Comments', 'Repeat Comments',
        'Prerequisites', 'Units - Units Fixed - Unit Value', 'General Subject Areas'
    ), ('ART', number, 'Synthetic ' + number, 'Synthetic source body', '-', '-', flag, '5', 'Area F: Arts')))
        for number, flag in [('1A', 'No'), ('7A', 'No')]]
    spec = deepcopy(adapter.SPEC)
    spec['entries'] = spec['entries'][:2]
    for entry, row in zip(spec['entries'], rows):
        entry['row_digest'] = hashlib.sha256(json.dumps(
            row, sort_keys=True, ensure_ascii=False, separators=(',', ':')
        ).encode()).hexdigest()
    monkeypatch.setattr(adapter, 'SPEC', spec)
    calls = []
    monkeypatch.setattr(adapter.pools, 'parse_csv', lambda data: calls.append(data))
    return rows, calls


def test_emits_only_bounded_facts_without_certifying_reviews(synthetic):
    rows, calls = synthetic
    result = adapter.parse_csv(csv_text(rows))
    assert calls == [csv_text(rows)]
    assert set(result) == {'id', 'courses'}
    assert result['id'] == 'ucsb-ai-bs'
    assert [c['id'] for c in result['courses']] == ['ucsb-art-1a', 'ucsb-art-7a']
    for course in result['courses']:
        assert course['prerequisites'] is None
        assert course['credit_unit'] == 'quarter_hours'
        assert course['credits'] == 5
        assert course['source_id'] == 'ucsb-ai-bs-ge-defg-export'
        assert course['url'] == adapter.SPEC['source_url']
        assert 'category_review' not in course
        assert 'curriculum_audit' not in course
    assert result['courses'][1]['category'] == 'other'
    result['courses'][0]['notes'].append('caller edit')
    assert 'caller edit' not in adapter.SPEC['entries'][0]['notes']


@pytest.mark.parametrize('field', [
    'Course Description', 'Full Course Title', 'Advisor Enrollment Comments',
    'Repeat Comments', 'Prerequisites', 'Units - Units Fixed - Unit Value',
    'General Subject Areas'
])
def test_changed_complete_row_is_rejected(synthetic, field):
    rows, _ = synthetic
    rows[0][field] += ' changed'
    with pytest.raises(ValueError, match='source row changed'):
        adapter.parse_csv(csv_text(rows))


@pytest.mark.parametrize('change', ['missing', 'duplicate', 'new'])
def test_scope_and_duplicates_are_rejected(synthetic, change):
    rows, _ = synthetic
    if change == 'missing':
        rows.pop()
    elif change == 'duplicate':
        rows.append(dict(rows[0]))
    else:
        rows.append(dict(rows[0], **{'Course Number': '999'}))
    with pytest.raises(ValueError, match='scope changed|Duplicate'):
        adapter.parse_csv(csv_text(rows))


def test_full_export_validation_cannot_be_skipped(synthetic, monkeypatch):
    rows, _ = synthetic
    def reject(data):
        raise ValueError('full export changed')
    monkeypatch.setattr(adapter.pools, 'parse_csv', reject)
    with pytest.raises(ValueError, match='full export changed'):
        adapter.parse_csv(csv_text(rows))


def test_manifest_manual_review_counts_and_limitations():
    entries = adapter.SPEC['entries']
    by_code = {e['code']: e for e in entries}
    assert len(entries) == 69
    assert sum(e['category'] == 'human_context' for e in entries) == 55
    assert sum(e['category'] == 'applications' for e in entries) == 5
    assert sum(e['category_review']['status'] == 'mixed' for e in entries) == 8
    assert by_code['MUS 115']['category_review']['status'] == 'unclassified'
    assert sum(e['credits'] == 5 for e in entries) == 15
    assert sum(e['credits'] == 4 for e in entries) == 53
    assert by_code['THTR 5']['credits'] == 3
    assert all(e['prerequisites'] is None for e in entries)
    assert all('Exact prerequisite rules are unavailable' in e['notes'][0] for e in entries)
    assert all(e['category_review']['rationale'] for e in entries)
    assert all(e['category_review']['source_ids'] == [adapter.SPEC['source_id']] for e in entries)
    assert by_code['FAMST 55AI']['category'] == 'human_context'
    assert by_code['FAMST 55CY']['category'] == 'human_context'
    assert by_code['FAMST 56AI']['category_review']['status'] == 'mixed'
    assert by_code['ART 106W']['category'] == 'applications'


def test_advisor_and_repeat_conditions_preserve_scope_without_alias_inference():
    entries = {e['code']: e for e in adapter.SPEC['entries']}
    assert any('Music 3A' in n and 'permission' in n for n in entries['MUS 3B']['notes'])
    assert entries['MUS 3B']['prerequisites'] is None
    assert any('Source numbering discrepancy' in n and '178BR' in n for n in entries['MUS 175BR']['notes'])
    assert any('8 units' in n and '43 and 143' in n for n in entries['THTR 143']['notes'])
    assert any('Not open for credit' in n and 'DANCEW 36' in n for n in entries['DANCE 36']['notes'])
    assert any('spring 2018' in n for n in entries['MUS 16']['notes'])
    assert any('12 units' in n and 'letter designations' in n for n in entries['FAMST 55AI']['notes'])
    assert 'course_identity_groups' not in adapter.SPEC


def test_optional_actual_cached_export():
    path = Path('.cache/research/ucsb-course-content/ge-defg-export.csv')
    if not path.exists():
        pytest.skip('Ignored official UI export is unavailable')
    result = adapter.parse_csv(path.read_text())
    assert len(result['courses']) == 69
    assert all(c['prerequisites'] is None for c in result['courses'])
