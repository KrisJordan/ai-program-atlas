"""Offline source guards and manually checked CHIN content dispositions."""
import csv
import hashlib
import io
import json
from copy import deepcopy
from pathlib import Path

import pytest

from atlas.adapters import ucsb_ge_asia_portuguese_lais_reviews as adapter


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
    ), ('CHIN', number, 'Synthetic ' + number, 'Synthetic source body', '-', '-', flag,
        credits, '-', '0', '0', 'Area E: Culture and Thought', '-', '-')))
        for number, flag, credits in [('32', 'No', '5'), ('40', 'No', '5')]]
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
    assert [c['id'] for c in result['courses']] == ['ucsb-chin-32', 'ucsb-chin-40']
    assert [c['credits'] for c in result['courses']] == [5, 5]
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
        rows[0]['Subject & Prefix'] = 'CHINW'
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
    assert len(entries) == 76
    assert len({e['id'] for e in entries}) == 76
    assert all(e['id'] == 'ucsb-' + e['code'].lower().replace(' ', '-') for e in entries)
    for subject, count in {'CHIN': 13, 'EACS': 20, 'JAPAN': 17, 'KOR': 1, 'LAIS W': 2, 'LAIS': 9, 'PORT': 14}.items():
        assert sum(e['source_code'].rsplit(' ', 1)[0] == subject for e in entries) == count
    assert sum(e['category'] == 'human_context' for e in entries) == 76
    assert sum(e['category_review']['status'] == 'reviewed' for e in entries) == 76
    assert all(e['category_review']['candidate_categories'] == [] for e in entries)
    assert sum(e['credits'] == 5 for e in entries) == 25
    assert sum(e['credits'] == 4 for e in entries) == 51
    assert sum(e['prerequisite_flag'] == 'Yes' for e in entries) == 46
    assert sum(e['prerequisite_flag'] == 'No' for e in entries) == 30
    assert all(e['prerequisites'] is None for e in entries)
    assert all('Exact prerequisite rules are unavailable' in e['notes'][0] for e in entries)
    assert all(e['category_review']['rationale'] for e in entries)
    assert all(e['category_review']['source_ids'] == [adapter.SPEC['source_id']] for e in entries)


def test_manual_restrictions_versions_and_boundary_decisions_survive():
    entries = {e['code']: e for e in adapter.SPEC['entries']}
    assert any('code/content conflict' in n for n in entries['EACS 5']['notes'])
    assert any('ARTHI 134D' in n and 'Yes' in n for n in entries['CHIN 134D']['notes'])
    assert any('KOR 82' in n for n in entries['EACS 103C']['notes'])
    assert any('advanced Chinese' in n for n in entries['CHIN 124A']['notes'])
    assert any('Fall 1969 - Winter 2011' in n for n in entries['LAIS 2']['notes'])
    assert any('GLOBL 195' in n for n in entries['LAIS W 13']['notes'])
    assert entries['LAIS W 13']['category'] == 'human_context'
    assert any('online version' in n for n in entries['LAIS W 10']['notes'])
    assert any('JAPAN 180DL' in n for n in entries['JAPAN 153']['notes'])
    assert any('legal repeat' in n for n in entries['LAIS 102']['notes'])
    assert any('20 units' in n for n in entries['PORT 129']['notes'])
    assert any('8 units' in n for n in entries['PORT 115']['notes'])
    assert any('Portuguese version' in n for n in entries['PORT 105']['notes'])
    for code in ('LAIS 127', 'LAIS 127E'):
        assert entries[code]['category'] == 'human_context'
        assert 'preparation of traditional dishes' in entries[code]['description']
        assert 'preparation of traditional dishes' in entries[code]['category_review']['rationale']
        assert 'cultural inquiry' in entries[code]['category_review']['rationale']


def test_raw_source_code_is_guarded_separately_from_stable_identity(synthetic):
    rows, _ = synthetic
    rows[0]['Course Number'] = '32 '
    entry = adapter.SPEC['entries'][0]
    entry['source_code'] = 'CHIN 32 '
    entry['row_digest'] = hashlib.sha256(json.dumps(
        rows[0], sort_keys=True, ensure_ascii=False, separators=(',', ':')
    ).encode()).hexdigest()
    result = adapter.parse_csv(csv_text(rows))
    assert result['courses'][0]['id'] == 'ucsb-chin-32'
    assert result['courses'][0]['code'] == 'CHIN 32'
    rows[0]['Course Number'] = '32'
    with pytest.raises(ValueError, match='scope changed'):
        adapter.parse_csv(csv_text(rows))


def test_optional_actual_cached_export():
    path = Path('.cache/research/ucsb-course-content/ge-defg-export.csv')
    if not path.exists():
        pytest.skip('Ignored official UI export is unavailable')
    result = adapter.parse_csv(path.read_text())
    assert len(result['courses']) == 76
    assert all(c['prerequisites'] is None for c in result['courses'])
