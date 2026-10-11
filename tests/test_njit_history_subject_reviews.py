import hashlib
import json
from pathlib import Path
import pytest
from bs4 import BeautifulSoup
from atlas.adapters import njit_history_subject_reviews as m
from atlas.adapters.national_curriculum_common import clean


def test_history_observer_rejects_stale_or_missing_content(monkeypatch):
    html = '<div class="courseblock"><p class="courseblocktitle">HIST 999. Example history. 3 credits, 3 contact hours.</p><p>Invented historical inquiry. Prerequisites: ENGL 102 with C or higher.</p></div>'
    text = clean(BeautifulSoup(html,'html.parser').get_text(' ',strip=True))
    monkeypatch.setattr(m,'SPEC',{'HIST 999':dict(digest=hashlib.sha256(text.encode()).hexdigest(),description='Invented interpretation.',category='human_context')})
    result = m.parse(html)
    assert result['courses'][0]['prerequisites'] == 'Prerequisites: ENGL 102 with C or higher.'
    assert 'category_review' not in result['courses'][0]
    assert 'curriculum_audit' not in result
    with pytest.raises(ValueError,match='changed'):
        m.parse(html.replace('historical inquiry','technical methods'))
    for bad in ['<h1>Sign in</h1>',html+html]:
        with pytest.raises(ValueError,match='missing or duplicate'):
            m.parse(bad)


def test_current_history_scope_excludes_title_only_rutgers_records():
    p = json.loads(Path('data/programs/'+m.PID+'.json').read_text())
    courses = {c['code']:c for c in p['courses']}
    assert len(m.SPEC) == 44
    assert all(courses[code]['category_review']['status']=='reviewed' for code in m.SPEC)
    assert courses['HIST 322']['category'] == 'human_context'  # Actual AI-law description.
    assert courses['HIST 328']['category'] == 'human_context'  # Database is a research tool.
    assert courses['HIST 387']['category'] == 'human_context'  # Computer history.
    rutgers = [c for c in p['courses'] if c['code'].startswith(('R510 ','R512 '))]
    assert len(rutgers) == 143
    assert all('category_review' not in c for c in rutgers)
