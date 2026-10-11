"""Bounded source observations must not extend degree or review scope."""
import hashlib
import json
from pathlib import Path
import pytest
from bs4 import BeautifulSoup
from atlas.adapters import miami_fixed_course_reviews as m
from atlas.adapters.business_society_minors import clean


def fixture(monkeypatch, eligibility='Prerequisites: TEST 100 or TEST 200 and TEST 300.'):
    html = '<div class="courseblock"><p class="courseblocktitle">ABC 101. Example methods. 0 Credit Hours.</p><p>Invented course text. '+eligibility+' Components: LEC.</p></div>'
    text = clean(BeautifulSoup(html, 'html.parser').get_text(' ', strip=True))
    monkeypatch.setattr(m, 'SPEC', {'ABC 101': dict(key='abc', url='https://example.edu/abc/',
        program_ids=['example'], digest=hashlib.sha256(text.encode()).hexdigest(),
        category='foundations', description='Invented methods description.')})
    return html


@pytest.mark.parametrize('eligibility', [
    'Prerequisite:TEST100 or TEST200.',
    'Prerequisites: TEST 100 or TEST 200 and TEST 300.',
    'Pre/Corequisite: TEST 100 or TEST 200.',
    'Prerequisite: TEST 100. Or Corequisites: TEST 100 including equivalents.',
])
def test_literal_eligibility_and_observed_zero(monkeypatch, eligibility):
    result = m.parse(fixture(monkeypatch, eligibility), 'example', 'abc')
    c = result['courses'][0]
    assert c['prerequisites'] == eligibility
    assert c['credits'] == 0 and c['credit_unit'] == 'semester_hours'
    assert 'category_review' not in c and 'curriculum_audit' not in result


def test_changes_missing_duplicate_and_wrong_scope_fail(monkeypatch):
    html = fixture(monkeypatch)
    with pytest.raises(ValueError, match='changed'):
        m.parse(html.replace('Invented course', 'Altered course'), 'example', 'abc')
    for bad in ['<h1>Log in</h1>', html + html]:
        with pytest.raises(ValueError, match='missing or duplicate'):
            m.parse(bad, 'example', 'abc')
    with pytest.raises(ValueError, match='missing or duplicate'):
        m.parse(html, 'unrelated-program', 'abc')


def test_actual_fixed_review_scope_and_qualified_metadata():
    p = json.loads(Path('data/programs/miami-data-science-ai-bs.json').read_text())
    main = {c['code']: c for c in p['courses'] if c['id'].startswith(p['id'] + '-')}
    assert main['CSC 345']['id'] != main['CSC 545']['id']
    assert main['CSC 345']['name'] == main['CSC 545']['name']
    assert main['CSC 345']['prerequisites'].startswith('Published unlabeled')
    assert main['CSC 113']['category_review']['status'] == 'mixed'
    assert main['CSC 315']['category'] == 'foundations'
    assert main['CSC 546']['category'] == 'ai_ml'
    # No broad code match may stamp these reviews on separately sourced cognates.
    assert not any(c.get('category_review', {}).get('source_ids', [''])[0].startswith('miami-fixed-courses-')
                   for c in p['courses'] if not c['id'].startswith(p['id'] + '-'))
    b = json.loads(Path('data/programs/miami-ai-technologies-business-bsba.json').read_text())
    courses = {c['code']: c for c in b['courses'] if c['id'].startswith(b['id'] + '-')}
    assert courses['UMX 100']['credits'] == 0
    assert courses['UMX 100']['category_review']['status'] == 'unclassified'
    assert 'major in finance' in courses['FIN 302']['prerequisites']
    assert 'Or Corequisites:' in courses['MAS 311']['prerequisites']
    assert courses['MAS 311']['category'] == 'mathematics'
