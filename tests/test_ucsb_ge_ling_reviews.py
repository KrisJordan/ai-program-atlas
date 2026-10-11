import csv
import hashlib
import io
import json
from pathlib import Path
import pytest
from atlas.adapters import ucsb_ge_ling_reviews as m
from atlas.curriculum_profile import requirement_profile


def test_complete_linguistics_subject_review_preserves_mixed_content_and_unknown_rules():
    assert len(m.SPEC['entries']) == 15
    assert sum(e['category_review']['status'] == 'reviewed' for e in m.SPEC['entries']) == 13
    assert {e['code'] for e in m.SPEC['entries'] if e['category_review']['status'] == 'mixed'} == {'LING 20', 'LING 34'}
    assert {e['code'] for e in m.SPEC['entries'] if e['prerequisite_flag'] == 'Yes'} == {'LING 36', 'LING 130', 'LING 133', 'LING 187'}
    d = json.loads(Path('data/programs/ucsb-ai-bs.json').read_text())
    courses = {c['id']: c for c in d['courses']}
    for e in m.SPEC['entries']:
        assert courses[e['id']]['prerequisites'] is None
        assert courses[e['id']]['category_review'] == e['category_review']
    assert [requirement_profile(d)[k]['count'] for k in ('required', 'options', 'unresolved')] == [20, 76, 2]
    r = {r['id']: r for r in d['requirements']}
    assert 'ucsb-ling-36' in r['ucsb-ai-bs-policy-area-d']['course_ids']
    assert 'ucsb-ling-36' in r['ucsb-ai-bs-policy-area-e']['course_ids']
    assert 'ucsb-ling-133' in r['ucsb-ai-bs-policy-area-g']['course_ids']
    assert r['ucsb-ai-bs-policy-area-d']['count'] == 2
    assert r['ucsb-ai-bs-policy-area-e']['count'] == 2


def test_row_guard_includes_prerequisite_flag_and_returns_no_review(monkeypatch):
    row = {'Subject & Prefix': 'LING', 'Course Number': '1', 'Course Description': 'Synthetic text', 'Prerequisites': 'Yes'}
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=row)
    writer.writeheader()
    writer.writerow(row)
    data = stream.getvalue()
    entry = {**m.SPEC['entries'][0], 'code': 'LING 1', 'row_digest': hashlib.sha256(json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()}
    monkeypatch.setattr(m, 'SPEC', {**m.SPEC, 'entries': [entry]})
    monkeypatch.setattr(m.pools, 'parse_csv', lambda data: {})
    result = m.parse_csv(data)
    assert result['courses'][0]['prerequisites'] is None
    assert 'category_review' not in result['courses'][0]
    for changed in [data.replace('Yes', 'No'), data.replace('Synthetic text', 'Changed text')]:
        with pytest.raises(ValueError):
            m.parse_csv(changed)
    result['courses'][0]['notes'].clear()
    assert m.parse_csv(data)['courses'][0]['notes']


def test_optional_actual_export_replay_is_idempotent():
    p = Path('.cache/research/ucsb-course-content/ge-defg-export.csv')
    if not p.exists():
        pytest.skip('Optional official public CSV export')
    result = m.parse_csv(p.read_text())
    assert result == m.parse_csv(p.read_text())
    assert len(result['courses']) == 15
    assert all('category_review' not in c for c in result['courses'])
