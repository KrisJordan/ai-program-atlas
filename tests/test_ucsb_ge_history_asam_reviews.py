"""Offline guard tests use synthetic source rows, never committed catalog prose."""
import csv
import hashlib
import io
import json
from copy import deepcopy
from pathlib import Path

import pytest

from atlas.adapters import ucsb_ge_history_asam_reviews as adapter


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
    ), ('AS AM', number, 'Synthetic ' + number, 'Synthetic source body', '-', '-', flag, '5', 'Area F: Arts')))
        for number, flag in [('1', 'No'), ('10', 'Yes')]]
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
    assert [c['id'] for c in result['courses']] == ['ucsb-as-am-1', 'ucsb-as-am-10']
    for course in result['courses']:
        assert course['prerequisites'] is None
        assert course['credit_unit'] == 'quarter_hours'
        assert course['credits'] == 5
        assert course['source_id'] == 'ucsb-ai-bs-ge-defg-export'
        assert course['url'] == adapter.SPEC['source_url']
        assert 'category_review' not in course
        assert 'curriculum_audit' not in course
    assert result['courses'][1]['category'] == 'human_context'
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
    assert len(entries) == 97
    assert sum(e['code'].startswith('HIST ') and not e['code'].startswith('HIST W ') for e in entries) == 56
    assert sum(e['code'].startswith('HIST W ') for e in entries) == 6
    assert sum(e['code'].startswith('AS AM ') for e in entries) == 33
    assert sum(e['code'].startswith('AS AMW ') for e in entries) == 2
    assert sum(e['category'] == 'human_context' for e in entries) == 96
    assert sum(e['category'] == 'applications' for e in entries) == 1
    assert all(e['category_review']['status'] == 'reviewed' for e in entries)
    assert {c: sum(e['credits'] == c for e in entries) for c in (1,4,5)} == {1:1,4:52,5:44}
    assert all(e['prerequisites'] is None for e in entries)
    assert all('null does not establish absence' in e['notes'][0] for e in entries)
    assert all(e['category_review']['rationale'] for e in entries)
    assert all(e['category_review']['source_ids'] == [adapter.SPEC['source_id']] for e in entries)
    by = {e['code']: e for e in entries}
    honors = by['HIST 2CH']
    assert honors['credits'] == 1 and by['HIST 2C']['credits'] == 5
    assert any('four units' in n and 'five fixed units' in n and 'concurrently' in n for n in honors['notes'])
    assert any('online version' in n for n in by['AS AMW 1']['notes'])
    assert any('171II' in n for n in by['AS AM 157']['notes'])
    assert any('Recommended' in n for n in by['AS AM 156']['notes'])
    assert by['AS AM 79']['category'] == 'applications'


def test_optional_actual_cached_export():
    path = Path('.cache/research/ucsb-course-content/ge-defg-export.csv')
    if not path.exists():
        pytest.skip('Ignored official UI export is unavailable')
    result = adapter.parse_csv(path.read_text())
    assert len(result['courses']) == 97
    assert all(c['prerequisites'] is None for c in result['courses'])
