import hashlib
import json
from pathlib import Path
import pytest
from bs4 import BeautifulSoup
from atlas.adapters import njit_science_subject_reviews as m
from atlas.adapters.national_curriculum_common import clean


def fixture(monkeypatch):
    html = '<div class="courseblock"><p class="courseblocktitle">TEST 101. Example laboratory. 1 credit, 2 contact hours.</p><p>Example domain. Corequisite: TEST 100.</p></div>'
    text = clean(BeautifulSoup(html, 'html.parser').get_text(' ', strip=True))
    monkeypatch.setattr(m, 'SPEC', {'TEST 101': dict(key='example', url='https://example.edu/',
        digest=hashlib.sha256(text.encode()).hexdigest(), category='applications', description='An invented laboratory subject.')})
    return html


def test_observation_preserves_condition_and_requires_same_content(monkeypatch):
    html = fixture(monkeypatch)
    out = m.parse(html, 'example')
    c = out['courses'][0]
    assert c['prerequisites'] == 'Corequisite: TEST 100'
    assert c['credits'] == 1 and c['category'] == 'applications'
    assert 'category_review' not in c and 'curriculum_audit' not in out
    with pytest.raises(ValueError, match='changed'):
        m.parse(html.replace('Example domain', 'Different domain'), 'example')
    for bad in ['<h1>Log in</h1>', html + html]:
        with pytest.raises(ValueError, match='missing or duplicate'):
            m.parse(bad, 'example')


def test_composition_enriches_identity_without_duplicating_lab_rule(monkeypatch):
    html = fixture(monkeypatch)
    old = lambda _: {'id':m.PID, 'courses':[{'id':'njit-test-101','description':None}],
                     'requirements':[{'id':'conditional-lab'}]}
    out = m._compose(old, html, 'example')
    assert len(out['courses']) == 1
    assert out['requirements'] == [{'id':'conditional-lab'}]


def test_science_scope_and_real_evidence_missingness():
    p = json.loads(Path('data/programs/'+m.PID+'.json').read_text())
    courses = {c['code']:c for c in p['courses']}
    assert len(m.SPEC) == 22
    assert sum(courses[code]['category_review']['status']=='reviewed' for code in m.SPEC)==20
    assert all(courses[code]['category_review']['status']=='mixed' for code in ['BIOL 115','BIOL 150'])
    assert all('category_review' not in courses[code] for code in ['R120 101','R120 102','R120 207','R120 208','R120 237'])
    assert courses['PHYS 203']['prerequisites'] == 'Prerequisite: None'
    assert courses['R216 206']['credits'] == 3
    assert sum('-science-option-' in r['id'] for r in p['requirements']) == 9
