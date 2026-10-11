import hashlib
import json
from pathlib import Path
import pytest
from bs4 import BeautifulSoup
from atlas.adapters import njit_humanities_subject_reviews as m
from atlas.adapters.national_curriculum_common import clean
from atlas.curriculum_profile import requirement_profile


def fixture(monkeypatch):
    html = '<div class="courseblock"><p class="courseblocktitle">TEST 101. Example seminar. 3 credits, 3 contact hours.</p><p>Invented content. Prerequisites: ENGL 102; three credits may be concurrent. Restrictions: Senior standing.</p></div>'
    text = clean(BeautifulSoup(html, 'html.parser').get_text(' ', strip=True))
    monkeypatch.setattr(m, 'SPEC', {'TEST 101':dict(digest=hashlib.sha256(text.encode()).hexdigest(),
        category='human_context', description='Invented seminar content.',
        allocation_condition='Choose one of two allocations, not both.')})
    return html


def test_observes_exact_conditions_without_certifying_manual_review(monkeypatch):
    out = m.parse(fixture(monkeypatch))
    assert 'may be concurrent' in out['courses'][0]['prerequisites']
    assert 'Senior standing' in out['courses'][0]['prerequisites']
    assert out['requirements'][0]['kind'] == 'note'
    assert 'not both' in out['requirements'][0]['summary']
    assert 'category_review' not in out['courses'][0] and 'course_identity_groups' not in out
    assert 'curriculum_audit' not in out


def test_changed_missing_duplicate_rejected(monkeypatch):
    html = fixture(monkeypatch)
    with pytest.raises(ValueError, match='changed'):
        m.parse(html.replace('Invented content', 'New content'))
    for bad in ['<h1>Sign in</h1>', html+html]:
        with pytest.raises(ValueError, match='missing or duplicate'):
            m.parse(bad)


def test_reciprocal_identity_and_individually_reviewed_subjects():
    p = json.loads(Path('data/programs/'+m.PID+'.json').read_text())
    c = {c['code']:c for c in p['courses']}
    assert len(m.SPEC) == 50
    assert c['STS 307']['category'] == 'mathematics'
    assert c['STS 375']['category'] == 'human_context'
    assert c['PSY 325']['category_review']['status'] == 'unclassified'
    assert c['STS 380']['category_review']['status'] == 'mixed'
    assert c['LIT 378']['name'] != c['STS 378']['name']
    group = p['course_identity_groups'][0]
    assert set(group['course_ids']) == {c['LIT 378']['id'],c['STS 378']['id']}
    profile = requirement_profile(p)
    assert profile['required']['count'] == 32
    assert profile['options']['count'] == 348
    assert profile['options']['source_record_count'] == 349
    assert profile['identity']['source_records'] == 381
    assert profile['identity']['mapped_identities'] == 380
    assert sum('-allocation-' in r['id'] for r in p['requirements']) == 5
