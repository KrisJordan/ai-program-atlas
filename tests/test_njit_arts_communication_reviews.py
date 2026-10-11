import hashlib
from collections import Counter
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from atlas.adapters import njit_arts_communication_reviews as m
from atlas.adapters.national_curriculum_common import clean


HEADINGS = '<h1>University Catalog 2026-2027</h1><h1>Humanities and Social Sciences</h1>'


def fixture(monkeypatch, body='Prerequisites: ENGL 101. Corequisites: ENGL 102. Departmental approval required.', **extras):
    block = '<div class="courseblock"><p class="courseblocktitle">TEST 101. Example seminar. 3 credits, 3 contact hours.</p><p>' + body + '</p></div>'
    text = clean(BeautifulSoup(block, 'html.parser').get_text(' ', strip=True))
    spec = dict(digest=hashlib.sha256(text.encode()).hexdigest(), title='Example seminar',
                category='human_context', description='An invented test seminar.', **extras)
    monkeypatch.setattr(m, 'SPEC', {'TEST 101': spec})
    return HEADINGS + block


def test_observation_preserves_conditions_without_certifying_review(monkeypatch):
    result = m.parse(fixture(monkeypatch, ger_allocation_statement='Example GER statement.'))
    c = result['courses'][0]
    assert c['prerequisites'] == 'Prerequisites: ENGL 101. Corequisites: ENGL 102. Departmental approval required.'
    assert c['credits'] == 3 and c['credit_unit'] == 'semester_hours'
    assert 'category_review' not in c and 'curriculum_audit' not in result
    assert 'course_identity_groups' not in result and result['requirements'] == []
    assert result['observed_ger_allocations'] == {c['id']: 'Example GER statement.'}


def test_reviewed_malformed_boundary_does_not_swallow_description(monkeypatch):
    html = fixture(monkeypatch, 'Prerequisites: ENGL 102 may be concurrent Working with plays, students practice interpretation.',
                   eligibility_end_before=' Working with plays')
    assert m.parse(html)['courses'][0]['prerequisites'] == 'Prerequisites: ENGL 102 may be concurrent'


@pytest.mark.parametrize('before,after', [('2026-2027', '2027-2028'), ('Humanities and Social Sciences', 'Other chapter')])
def test_catalog_identity_guard(monkeypatch, before, after):
    with pytest.raises(ValueError, match='version or chapter'):
        m.parse(fixture(monkeypatch).replace(before, after))


@pytest.mark.parametrize('before,after', [('Example seminar', 'Changed title'), ('3 credits', '4 credits'), ('ENGL 101', 'ENGL 201')])
def test_changed_source_rejected(monkeypatch, before, after):
    with pytest.raises(ValueError, match='content changed'):
        m.parse(fixture(monkeypatch).replace(before, after))


def test_missing_duplicate_and_overlap_rejected(monkeypatch):
    html = fixture(monkeypatch)
    for bad in [HEADINGS, html + html]:
        with pytest.raises(ValueError, match='missing or duplicate'):
            m.parse(bad)
    with pytest.raises(ValueError, match='Overlapping'):
        m.combine(m.parse, html)
    result = m.combine(lambda _: {'id': m.PID, 'courses': []}, html)
    assert len(result['courses']) == 1


def test_manual_manifest_scope_and_unknowns():
    assert len(m.SPEC) == 71
    assert Counter(c.split()[0] for c in m.SPEC) == {'COM': 32, 'LIT': 21, 'THTR': 18}
    assert Counter(s['category'] for s in m.SPEC.values()) == {'human_context': 55, 'applications': 11, 'other': 5}
    assert Counter(s['review_status'] for s in m.SPEC.values()) == {'reviewed': 66, 'mixed': 4, 'unclassified': 1}
    assert m.SPEC['LIT 370']['description'] is None
    assert m.SPEC['COM 325']['review_status'] == 'unclassified'
    assert m.SPEC['COM 369']['category'] == 'human_context'
    assert m.SPEC['THTR 364']['category'] == 'applications'
    assert m.SPEC['THTR 384']['category'] == 'human_context'
    assert m.SPEC['COM 380']['ger_allocation_statement'].endswith('Cultural Literacy.')
    assert 'LIT 378' not in m.SPEC


def test_actual_source_when_cached():
    path = Path('.cache/http') / (hashlib.sha256(m.URL.encode()).hexdigest() + '.body')
    if not path.exists():
        pytest.skip('Ignored official source cache not available')
    result = m.parse(path.read_text())
    courses = {c['code']: c for c in result['courses']}
    assert len(courses) == 71
    assert sum(c['description'] is not None for c in courses.values()) == 70
    assert courses['LIT 370']['prerequisites'] is None
    assert 'Working with plays' not in courses['THTR 210']['prerequisites']
    assert courses['THTR 261']['prerequisites'] == 'Departmental approval required.'
    assert courses['THTR 262']['prerequisites'] == 'Departmental approval required.'
    assert 'Corequisites:' in courses['COM 201']['prerequisites']
    assert 'Spanish is not required' in courses['LIT 376']['prerequisites']
    assert 'Ableton Live' in courses['COM 381']['prerequisites']
    assert all(c['credits'] == 3 for c in courses.values())
