"""Offline guard tests use synthetic source rows, never committed catalog prose."""
import csv
import hashlib
import io
import json
from copy import deepcopy
from pathlib import Path

import pytest

from atlas.adapters import ucsb_ge_social_reviews as adapter


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
    ), (subject, number, 'Synthetic ' + number, 'Synthetic source body', '-', '-', flag, '5', 'Area F: Arts')))
        for subject, number, flag in [('ANTH W', '3', 'No'), ('ANTH', '2', 'Yes')]]
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
    assert [c['id'] for c in result['courses']] == ['ucsb-anth-w-3', 'ucsb-anth-2']
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
    assert len(entries) == 84
    assert sum(e['category'] == 'human_context' for e in entries) == 80
    assert {e['code'] for e in entries if e['category_review']['status']=='mixed'} == {'ANTH 8','BL ST 122','BL ST 131','CH ST 188C'}
    assert all(e['prerequisites'] is None for e in entries)
    assert all(e['credits'] in (4,5) for e in entries)
    assert all('null does not establish absence' in e['notes'][0] for e in entries)
    assert all(e['category_review']['rationale'] for e in entries)
    by = {e['code']: e for e in entries}
    assert any('Fall 1969' in n and 'Winter 2011' in n for n in by['BL ST 2']['notes'])
    assert any('Illegal Repeat' in n for n in by['BL ST 38A']['notes'])
    assert any('same ANTH Major' in n for n in by['ANTH W 3']['notes'])
    assert any('Weekly film screening is mandatory' in n for n in by['FEMST 40']['notes'])
    assert by['BL ST 68']['category']=='human_context'
    assert all(e['category']=='other' and e['category_review']['candidate_categories']==['human_context','applications'] for e in entries if e['category_review']['status']=='mixed')


def test_optional_actual_cached_export():
    path = Path('.cache/research/ucsb-course-content/ge-defg-export.csv')
    if not path.exists():
        pytest.skip('Ignored official UI export is unavailable')
    result = adapter.parse_csv(path.read_text())
    assert len(result['courses']) == 84
    assert all(c['prerequisites'] is None for c in result['courses'])
