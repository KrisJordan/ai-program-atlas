"""Offline source guards and manually checked CLASS content dispositions."""
import csv
import hashlib
import io
import json
from copy import deepcopy
from pathlib import Path

import pytest

from atlas.adapters import ucsb_ge_classics_german_slavic_reviews as adapter


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
        'Prerequisites', 'Units - Units Fixed - Unit Value', 'Units - Units Fixed',
        'Units - Units Variable - Min', 'Units - Units Variable - Max',
        'General Subject Areas', 'Special Subject Areas', 'University Requirements'
    ), ('CLASS', number, 'Synthetic ' + number, 'Synthetic source body', '-', '-', flag,
        credits, '-', '0', '0', 'Area E: Culture and Thought', '-', '-')))
        for number, flag, credits in [('20A', 'No', '4'), ('20B', 'No', '4')]]
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


def test_emits_bounded_facts_without_review_certification(synthetic):
    rows, calls = synthetic
    result = adapter.parse_csv(csv_text(rows))
    assert calls == [csv_text(rows)]
    assert set(result) == {'id', 'courses'}
    assert result['id'] == 'ucsb-ai-bs'
    assert [c['id'] for c in result['courses']] == ['ucsb-class-20a', 'ucsb-class-20b']
    assert [c['credits'] for c in result['courses']] == [4, 4]
    for course in result['courses']:
        assert course['prerequisites'] is None
        assert course['credit_unit'] == 'quarter_hours'
        assert course['source_id'] == 'ucsb-ai-bs-ge-defg-export'
        assert course['url'] == adapter.SPEC['source_url']
        assert 'category_review' not in course
        assert 'curriculum_audit' not in course
    result['courses'][0]['notes'].append('caller edit')
    assert 'caller edit' not in adapter.SPEC['entries'][0]['notes']


@pytest.mark.parametrize('field', [
    'Course Description', 'Full Course Title', 'Advisor Enrollment Comments',
    'Repeat Comments', 'Prerequisites', 'Units - Units Fixed - Unit Value',
    'Units - Units Fixed', 'Units - Units Variable - Min', 'Units - Units Variable - Max',
    'General Subject Areas', 'Special Subject Areas', 'University Requirements'
])
def test_changed_complete_row_is_rejected(synthetic, field):
    rows, _ = synthetic
    rows[0][field] += ' changed'
    with pytest.raises(ValueError, match='source row changed'):
        adapter.parse_csv(csv_text(rows))


@pytest.mark.parametrize('change', ['missing', 'duplicate', 'new', 'subject'])
def test_scope_and_duplicates_are_rejected(synthetic, change):
    rows, _ = synthetic
    if change == 'missing':
        rows.pop()
    elif change == 'duplicate':
        rows.append(dict(rows[0]))
    elif change == 'subject':
        rows[0]['Subject & Prefix'] = 'CLASSW'
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


def test_manifest_manual_counts_and_prerequisite_limits():
    entries = adapter.SPEC['entries']
    assert len(entries) == 61
    assert len({e['id'] for e in entries}) == 61
    assert all(e['id'] == 'ucsb-' + e['code'].lower().replace(' ', '-') for e in entries)
    for subject, count in {'CLASS': 20, 'CLASSW': 1, 'GER': 15, 'GREEK': 2, 'LATIN': 2, 'SLAV': 21}.items():
        assert sum(e['code'].startswith(subject + ' ') for e in entries) == count
    assert sum(e['category'] == 'human_context' for e in entries) == 58
    assert sum(e['category'] == 'foundations' for e in entries) == 1
    assert sum(e['category'] == 'applications' for e in entries) == 1
    assert sum(e['category_review']['status'] == 'reviewed' for e in entries) == 60
    mixed = next(e for e in entries if e['code'] == 'CLASS 190')
    assert mixed['category'] == 'other'
    assert mixed['category_review']['status'] == 'mixed'
    assert mixed['category_review']['candidate_categories'] == ['foundations', 'ai_ml', 'human_context']
    assert sum(e['credits'] == 5 for e in entries) == 5
    assert sum(e['credits'] == 4 for e in entries) == 56
    assert sum(e['prerequisite_flag'] == 'Yes' for e in entries) == 36
    assert sum(e['prerequisite_flag'] == 'No' for e in entries) == 25
    assert all(e['prerequisites'] is None for e in entries)
    assert all('Exact prerequisite rules are unavailable' in e['notes'][0] for e in entries)
    assert all(e['category_review']['rationale'] for e in entries)
    assert all(e['category_review']['source_ids'] == [adapter.SPEC['source_id']] for e in entries)


def test_manual_restrictions_versions_and_boundary_decisions_survive():
    entries = {e['code']: e for e in adapter.SPEC['entries']}
    assert entries['GER 152']['category'] == 'foundations'
    assert entries['GER 155']['category'] == 'human_context'
    assert 'design and construction' in entries['GER 155']['description']
    assert adapter.SPEC['existing_record_overlaps'][0]['course_id'] == 'ucsb-ger-155'
    assert any('ENGL 155AI' in n for n in entries['GER 155']['notes'])
    assert entries['CLASS 50']['category'] == 'applications'
    assert any('Instructor approval' in n for n in entries['CLASS 190']['notes'])
    assert any('prior Classics' in n for n in entries['CLASS 190']['notes'])
    assert any('online version' in n for n in entries['CLASSW 36']['notes'])
    assert any('24 units' in n and '12 units' in n for n in entries['SLAV 117G']['notes'])
    assert any('12-unit repeat cap' in n for n in entries['SLAV 117G']['notes'])
    assert any('differing code references' in n for n in entries['SLAV 164B']['notes'])
    assert any('Slavic 154' in n for n in entries['SLAV 164B']['notes'])
    assert any('Slavic 125A' in n for n in entries['SLAV 123C']['notes'])
    assert any('Slavic 125B' in n for n in entries['SLAV 123D']['notes'])
    assert any('intended audience' in n for n in entries['SLAV 33']['notes'])
    assert any('Armenian Literature' in n for n in entries['SLAV 175A']['notes'])


def test_optional_actual_cached_export():
    path = Path('.cache/research/ucsb-course-content/ge-defg-export.csv')
    if not path.exists():
        pytest.skip('Ignored official UI export is unavailable')
    result = adapter.parse_csv(path.read_text())
    assert len(result['courses']) == 61
    assert all(c['prerequisites'] is None for c in result['courses'])
