import copy
import hashlib
from collections import Counter
from pathlib import Path

import pytest
from atlas.adapters import ucsd_codeonly_language_reviews as m


def fixture(monkeypatch, codes, body='Language and cultural interpretation.'):
    entries = [copy.deepcopy(e) for e in m.SPEC['entries'] if e['code'] in codes]
    for e in entries:
        if e['heading']:
            e['description_hash'] = hashlib.sha256(body.encode()).hexdigest()
    monkeypatch.setattr(m, 'SPEC', {**m.SPEC, 'entries': entries, 'chapter_contexts': {}, 'identity_heading_guards': {}})
    e = next(e for e in entries if e['heading'])
    source = m.SPEC['sources'][e['source_key']]
    section = f'<h2>{e["region"]}</h2><p>{e["region_text"]}</p>'
    if e['division'] != e['region']:
        section += f'<h3>{e["division"]}</h3><p>{e["section_text"]}</p>'
    return f'<h1>{source["heading"]}</h1><p class="course-disclaimer">2026–27</p>{section}<p class="course-name">{e["heading"]}</p><p class="course-description">{body}</p>'


def test_grouped_sequence_is_three_four_unit_courses_not_three_twelve_unit_courses(monkeypatch):
    rows = m.parse_observations(fixture(monkeypatch, ['JAPN 150A', 'JAPN 150B', 'JAPN 150C']))['courses']
    assert [c['code'] for c in rows] == ['JAPN 150A', 'JAPN 150B', 'JAPN 150C']
    assert [c['credits'] for c in rows] == [4, 4, 4]
    assert all(c['credit_unit'] == 'quarter_hours' for c in rows)
    assert all('previous course or consent' in c['prerequisites'] for c in rows)
    assert all(any('placement' in n for n in c['notes']) for c in rows)
    assert all('category_review' not in c for c in rows)


def test_french_standing_local_preparation_and_language_are_distinct(monkeypatch):
    row = m.parse_observations(fixture(monkeypatch, ['LTFR 115']))['courses'][0]
    assert row['prerequisites'] == 'Section prerequisite: upper-division standing or consent of instructor. Course prerequisite: LTFR 104.'
    assert 'All upper-division French courses are taught in French.' in row['notes']
    assert any('three times' in n for n in row['notes'])


@pytest.mark.parametrize('old,new', [
    ('Language and cultural interpretation.', 'New prerequisite: graduate standing.'),
    ('2026–27', '2027–28'),
    ('upper-division standing or consent of instructor', 'graduate standing'),
    ('LTFR 115.', 'LTFR 115X.'),
    ('(4)', '(8)'),
])
def test_source_mutations_require_new_review(monkeypatch, old, new):
    html = fixture(monkeypatch, ['LTFR 115'])
    assert old in html
    with pytest.raises(ValueError):
        m.parse_observations(html.replace(old, new))


def test_missing_exact_identity_does_not_copy_track_or_sibling_metadata(monkeypatch):
    html = fixture(monkeypatch, ['CHIN 160', 'CHIN 10A'])
    out = m.parse_observations(html)
    assert [c['code'] for c in out['courses']] == ['CHIN 160']
    assert out['source_dispositions'] == [{'code': 'CHIN 10A', 'status': 'no_exact_current_heading'}]
    assert not {'requirements', 'course_identity_groups', 'curriculum_audit'} & out.keys()
    assert any('no undergraduate/graduate identity merge' in n for n in out['courses'][0]['notes'])
    with pytest.raises(ValueError, match='absent exact heading'):
        m.parse_observations(html + '<p class="course-name">CHIN 10A. New exact course (5)</p>')


def test_manual_dispositions_subjects_and_restrictions():
    rows = {e['code']: e for e in m.SPEC['entries']}
    assert len(rows) == 102
    assert Counter(e['disposition'] for e in rows.values()) == {'reviewed_current_description': 87, 'no_exact_current_heading': 15}
    assert Counter(e['category'] for e in rows.values()) == {'human_context': 84, 'applications': 3, 'other': 15}
    assert rows['LTEN 30']['category'] == 'human_context'
    assert rows['LTWR 8A']['category'] == rows['LTWR 8B']['category'] == rows['LTWR 8C']['category'] == 'applications'
    assert any('PHYS 30' in n and 'not receive credit' in n for n in rows['LTEN 30']['notes'])
    assert any('concurrently enrolled' in n for n in rows['LTGK 101']['notes'])
    assert any('twelve units' in n for n in rows['LTIT 137']['notes'])
    assert any('P/NP' in n for n in rows['CHIN 160']['notes'])
    assert 'advanced knowledge' in rows['CHIN 160']['observed_prerequisites']
    assert rows['LTKO 140']['observed_prerequisites'].count('LTKO 130F') == 2
    assert rows['LTGK 1']['observed_prerequisites'] is None
    assert all(rows[c]['name'] is None for c in ['CHIN 10A', 'CHIN 20C', 'LTKO 130', 'LTIT 2C'])
    assert not any(e['code'].startswith('LTSP') for e in rows.values())


@pytest.mark.parametrize('key,count,gaps', [('LTCS', 71, 6), ('CHIN', 1, 9), ('JAPN', 15, 0)])
def test_actual_official_chapter_replay(key, count, gaps):
    path = Path(m.SPEC['sources'][key]['cache_path'])
    if not path.exists():
        pytest.skip('Optional ignored official source cache')
    html = path.read_text()
    out = m.parse_observations(html)
    assert len(out['courses']) == count
    assert len(out['source_dispositions']) == gaps
    assert all(c['name'] and c['description'] for c in out['courses'])
    if key == 'JAPN':
        with pytest.raises(ValueError, match='placement/context'):
            m.parse_observations(html.replace('an oral interview', 'automatic placement'))
    if key == 'CHIN':
        with pytest.raises(ValueError, match='track identity'):
            m.parse_observations(html.replace('CHIN 10AN.', 'CHIN 10AX.'))
    if key == 'LTCS':
        with pytest.raises(ValueError, match='block changed'):
            m.parse_observations(html.replace('Corequisites:', 'Recommended preparation:'))
