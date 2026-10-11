"""Manual content decisions and full-row guards for the cached Romance-language export."""
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path

import pytest

from atlas.adapters import ucsb_ge_romance_reviews as m


def test_reviewed_scope_and_content_based_subject_decisions():
    entries = {e['code']: e for e in m.SPEC['entries']}
    assert len(entries) == 88
    assert Counter(c.split()[0] for c in entries) == {'SPAN': 36, 'FR': 29, 'ITAL': 23}
    assert Counter(e['category'] for e in entries.values()) == {'human_context': 85, 'applications': 3}
    assert {c for c, e in entries.items() if e['category'] == 'applications'} == {'SPAN 100', 'SPAN 124', 'SPAN 124E'}
    assert all(e['category_review']['status'] == 'reviewed' for e in entries.values())
    assert 'brief' in entries['SPAN 100']['category_review']['rationale']
    assert 'Cognitive' in entries['SPAN 124']['category_review']['rationale']
    for c in ('SPAN 50', 'SPAN 127', 'FR 154I', 'FR 154J', 'ITAL 104', 'ITAL 139YX'):
        assert entries[c]['category'] == 'human_context'
    assert 'communication' in entries['ITAL 104']['category_review']['rationale']
    assert 'medical' in entries['FR 154J']['description']
    assert Counter(e['credits'] for e in entries.values()) == {4: 76, 5: 12}
    assert Counter(e['prerequisite_flag'] for e in entries.values()) == {'Yes': 55, 'No': 33}


def test_actual_conditions_and_relationships_remain_scoped_notes():
    entries = {e['code']: e for e in m.SPEC['entries']}
    notes = lambda c: ' '.join(entries[c]['notes'])
    for c in ('ITAL 101', 'ITAL 103', 'ITAL 104'):
        assert 'consent' in notes(c)
    assert 'maximum of 12 units' in notes('SPAN 148B')
    assert 'letter designation is different' in notes('SPAN 148B')
    assert 'maximum of 16 units' in notes('ITAL 139CX')
    assert 'may not be taken concurrently' in notes('FR 151G')
    assert 'French 154L' in notes('FR 151G')
    assert 'Spanish 180' in notes('SPAN 178')
    assert 'do not intend to enroll' in notes('ITAL 189X')
    assert 'EAP Summer Program' in notes('ITAL 189X')
    assert 'performance' in notes('SPAN 124')
    assert 'not guaranteed' in notes('SPAN 124E')
    assert 'former number' in notes('ITAL 139DX')
    assert 'legal repeat' in notes('SPAN 124') and 'legal repeat' in notes('SPAN 124E')
    assert 'same course' in notes('FR 158') and 'same course' in notes('ITAL 158X')
    assert 'English 119X' in notes('FR 153A')
    assert all('course_identity_groups' not in e for e in entries.values())
    assert entries['SPAN 137A']['id'] != entries['SPAN 137B']['id']
    assert entries['ITAL 138T']['id'] != entries['ITAL 139TX']['id']


def csv_text(rows):
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=rows[0])
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def test_changed_full_source_row_cannot_replay_old_review(monkeypatch):
    row = {'Subject & Prefix': 'SPAN', 'Course Number': '124E',
           'Full Course Title': 'Psycholinguistics', 'Course Description': 'Synthetic content',
           'Advisor Enrollment Comments': 'An enrollment condition', 'Repeat Comments': 'Repeat cap',
           'Prerequisites': 'Yes', 'Units - Units Fixed - Unit Value': '4'}
    entry = {**next(e for e in m.SPEC['entries'] if e['code'] == 'SPAN 124E'),
             'row_digest': hashlib.sha256(json.dumps(row, sort_keys=True, ensure_ascii=False,
                                                   separators=(',', ':')).encode()).hexdigest()}
    monkeypatch.setattr(m, 'SPEC', {**m.SPEC, 'entries': [entry]})
    monkeypatch.setattr(m.pools, 'parse_csv', lambda data: {})
    result = m.parse_csv(csv_text([row]))
    assert result['courses'][0]['prerequisites'] is None
    assert 'category_review' not in result['courses'][0]
    assert 'requirements' not in result and 'course_identity_groups' not in result
    for key, value in [('Course Description', 'New content'), ('Prerequisites', 'No'),
                       ('Advisor Enrollment Comments', '-'), ('Repeat Comments', '-'),
                       ('Units - Units Fixed - Unit Value', '5'), ('Full Course Title', 'New title')]:
        with pytest.raises(ValueError):
            m.parse_csv(csv_text([{**row, key: value}]))
    with pytest.raises(ValueError):
        m.parse_csv(csv_text([row, {**row, 'Course Number': '124E '}]))
    result['courses'][0]['notes'].clear()
    assert m.parse_csv(csv_text([row]))['courses'][0]['notes']


def test_optional_all_88_actual_rows_replay_without_network_or_review_emission():
    path = Path('.cache/research/ucsb-course-content/ge-defg-export.csv')
    if not path.exists():
        pytest.skip('Ignored ordinary public official CSV export')
    data = path.read_text()
    result = m.parse_csv(data)
    assert result == m.parse_csv(data)
    assert len(result['courses']) == 88
    assert all(c['prerequisites'] is None and c['credit_unit'] == 'quarter_hours' for c in result['courses'])
    assert all('category_review' not in c for c in result['courses'])
    assert {c['id'] for c in result['courses']} == {e['id'] for e in m.SPEC['entries']}
    with pytest.raises(ValueError):
        m.parse_csv('<html>Human verification challenge</html>')
    rows = list(csv.DictReader(io.StringIO(data)))
    with pytest.raises(ValueError):
        m.parse_csv(csv_text([r for r in rows if not (r['Subject & Prefix'] == 'ITAL' and r['Course Number'] == '189X')]))
