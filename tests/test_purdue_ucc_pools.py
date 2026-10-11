import csv
import io
import json
from pathlib import Path
from collections import Counter

import pytest
from atlas.adapters import purdue_ucc_pools as m
from atlas.curriculum_profile import requirement_profile


def fixture(rows):
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=m.SPEC['fields'], delimiter='\t')
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def test_synthetic_parser_preserves_campus_and_term_limits(monkeypatch):
    rows = [dict(zip(m.SPEC['fields'], values)) for values in [
        ['UCC08 - Science, Tech & Society', 'DEMO-Example', 'DEMO12300 - Example', 'Fall 2026', 'PWL, PIN', 'Winter 2027'],
        ['UCC08 - Science, Tech & Society', 'DEMO-Example', 'DEMO12400 - Elsewhere', 'Fall 2026', 'PFW', 'The End of Time'],
        ['UCC09 - AI Working Competency', 'DEMO-Example', 'DEMO12500 - Future', 'Spring 2027', 'PWL', 'The End of Time'],
    ]]
    monkeypatch.setitem(m.SPEC, 'source_rows', 3)
    monkeypatch.setitem(m.SPEC, 'all_row_digests', sorted(m._digest(r) for r in rows))
    result = m.parse_tsv(fixture(rows))
    assert len(result['pool_memberships']) == 2
    first, future = result['pool_memberships']
    assert first['code'] == 'DEMO 12300' and first['approval_end'] == 'Winter 2027'
    assert first['eligible_in_reviewed_term'] is True
    assert future['eligible_in_reviewed_term'] is False
    assert 'courses' not in result and 'category_review' not in str(result)
    with pytest.raises(ValueError):
        m.parse_tsv(fixture(rows).replace('Winter 2027', 'Winter 2028'))
    with pytest.raises(ValueError):
        m.parse_tsv('<html>Tableau loading</html>')


def test_current_export_and_seed_keep_approval_not_content_claims():
    rows = m.SPEC['entries']
    assert len(rows) == 135
    assert Counter(r['outcome'][:5] for r in rows) == {'UCC01': 10, 'UCC03': 9, 'UCC08': 94, 'UCC09': 22}
    assert all('PWL' in r['campuses'] for r in rows)
    d = json.loads(Path('data/programs/purdue-ai-bs.json').read_text())
    rules = {r['id']: r for r in d['requirements']}
    assert len(rules['purdue-ai-bs-college-core-written-communication']['course_ids']) == 10
    assert len(rules['purdue-ai-bs-college-core-science-technology-and-society']['course_ids']) == 94
    assert rules['purdue-ai-bs-ucc-ucc09-pool']['kind'] == 'note'
    assert [requirement_profile(d)[k]['count'] for k in ('required','options','unresolved')] == [9,140,1684]
    courses = {c['id']: c for c in d['courses']}
    assert courses['purdue-cs-17300']['category'] == 'other'
    assert courses['purdue-cs-17300']['credits'] is None
    assert courses['purdue-cs-17300']['description'] is None
    assert courses['purdue-cs-10100']['category_review']['status'] == 'mixed'
    assert any('Winter 2027' in n for n in courses['purdue-abe-22600']['notes'])


def test_optional_actual_export_replay():
    p = Path('.cache/research/purdue-course-content/ucc-export.csv')
    if not p.exists():
        pytest.skip('Optional public dashboard export')
    result = m.parse_tsv(p.read_bytes())
    assert len(result['pool_memberships']) == 135
    assert all(r['eligible_in_reviewed_term'] for r in result['pool_memberships'])
