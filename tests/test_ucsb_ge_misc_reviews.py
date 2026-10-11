import csv
import hashlib
import io
from pathlib import Path
import json
import pytest
from atlas.adapters import ucsb_ge_misc_reviews as m


def test_manual_subject_boundaries_and_conditional_amounts():
    e = {e['code']: e for e in m.SPEC['entries']}
    assert len(e) == 58
    assert e['GLOBL 12']['category'] == 'mathematics'
    assert e['PHIL 3']['category'] == 'human_context'
    assert e['PHIL 100D']['category'] == 'human_context'
    assert e['ENV S 1']['category_review']['status'] == 'mixed'
    assert e['SOC 152A']['category_review']['status'] == 'mixed'
    assert e['PSY 159']['category'] == 'applications'
    assert e['ECON 9']['credits'] == 5
    assert any('Reduced credit of 2' in n for n in e['ECON 9']['notes'])
    assert e['INT 35HD']['credits'] == e['INT 35LT']['credits'] == 8
    assert any('pass time 3' in n for n in e['PSY 183']['notes'])
    assert any('GLOBL 195' in n for n in e['GLOBLW 13']['notes'])


def synthetic(monkeypatch):
    row = {'Subject & Prefix': 'TEST', 'Course Number': '1', 'Course Description': 'Synthetic body', 'Prerequisites': 'Yes'}
    entry = {**m.SPEC['entries'][0], 'code': 'TEST 1', 'row_digest': hashlib.sha256(json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()}
    monkeypatch.setattr(m, 'SPEC', {**m.SPEC, 'subjects': ['TEST'], 'entries': [entry]})
    monkeypatch.setattr(m.pools, 'parse_csv', lambda data: {})
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=row)
    writer.writeheader()
    writer.writerow(row)
    return stream.getvalue()


def test_exact_row_guard_has_no_manual_certification(monkeypatch):
    data = synthetic(monkeypatch)
    result = m.parse_csv(data)
    assert set(result) == {'id', 'courses'}
    assert result['courses'][0]['prerequisites'] is None
    assert 'category_review' not in result['courses'][0]
    for changed in [data.replace('Yes', 'No'), data.replace('Synthetic body', 'Changed body')]:
        with pytest.raises(ValueError):
            m.parse_csv(changed)
    result['courses'][0]['notes'].clear()
    assert m.parse_csv(data)['courses'][0]['notes']


def test_actual_cached_rows_optional():
    p = Path('.cache/research/ucsb-course-content/ge-defg-export.csv')
    if not p.exists():
        pytest.skip('Optional ignored official export')
    observed = m.parse_csv(p.read_text())
    assert len(observed['courses']) == 58
    assert observed == m.parse_csv(p.read_text())
    assert all(c['prerequisites'] is None for c in observed['courses'])
    assert all('category_review' not in c for c in observed['courses'])
