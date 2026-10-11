import hashlib
import json
from pathlib import Path
import pytest
from bs4 import BeautifulSoup
from atlas.adapters import njit_seminar_art_reviews as m
from atlas.adapters.national_curriculum_common import clean


def test_seminar_policy_guard_does_not_manufacture_credit_amount(monkeypatch):
    html = '<div class="field--name-field-content"><h4>Example policy</h4><p>Invented completion rule.</p></div>'
    text = clean(BeautifulSoup(html,'html.parser').get_text(' ',strip=True))
    monkeypatch.setitem(m.SPEC,'seminar',dict(url='https://example.edu/',digest=hashlib.sha256(text.encode()).hexdigest()))
    out = m.seminar(html)
    assert 'credits' not in out['courses'][0]
    assert 'category_review' not in out['courses'][0]
    assert 'curriculum_audit' not in out
    assert out['requirements'][0]['kind']=='note'
    assert 'new first-time' in out['requirements'][0]['summary']
    with pytest.raises(ValueError,match='missing or changed'):
        m.seminar(html.replace('Invented completion rule','Changed rule'))
    with pytest.raises(ValueError,match='missing or changed'):
        m.seminar('<h1>Sign in</h1>')


def test_seed_retains_actual_zero_and_scope():
    p = json.loads(Path('data/programs/'+m.PID+'.json').read_text())
    c = {c['code']:c for c in p['courses']}
    assert c['FYS SEM']['credits']==0
    assert c['FYS SEM']['category_review']['status']=='unclassified'
    assert c['AD 333']['category']=='human_context'
    assert 'Not for ID, INTD, or DD majors' in c['AD 333']['prerequisites']
    r = next(r for r in p['requirements'] if r['id'].endswith('-seminar-completion'))
    assert 'S grade' in r['summary'] and 'risk' in r['summary']
