import copy
import hashlib
import json
from pathlib import Path

from bs4 import BeautifulSoup
import pytest
from atlas.adapters.cmu_bs.common import text
from atlas.adapters import purdue_canonical_course_reviews as m
from atlas.db import validate_program


def test_guarded_dated_outline_observes_no_credit_or_review(monkeypatch):
    code='CS 34800';e=copy.deepcopy(m.SPEC[code]);html=f'<main><h1>{e["heading"]}</h1><p>Synthetic database material.</p><p>Last Updated: Jun 20, 2025</p></main>'
    e['main_digest']=hashlib.sha256(text(BeautifulSoup(html,'html.parser').find('main')).encode()).hexdigest();monkeypatch.setitem(m.SPEC,code,e)
    out=m.parse(html,program_id='purdue-ai-bs',code=code)
    assert out['courses'][0]['category']=='systems'
    assert not {'credits','credit_unit','name','category_review'} & out['courses'][0].keys()
    assert not out['requirements'] and 'not verified Fall 2026' in out['notes'][0]
    for changed in [html.replace('database','new'),html.replace('2025','2026'),html.replace(e['heading'],'Different course')]:
        with pytest.raises(ValueError):m.parse(changed,program_id='purdue-ai-bs',code=code)
    with pytest.raises(ValueError):m.parse(html,program_id='purdue-ai-ba',code=code)


def test_proposed_directory_status_and_current_term_scope():
    directory='<main><p>Syllabi of courses marked * are proposed for canonical status.</p><ul><li><p><a>CS 48300</a> Theory*</p></li></ul></main>'
    assert not m.parse_directory(directory,program_id='purdue-ai-bs')['courses']
    with pytest.raises(ValueError):m.parse_directory(directory.replace('Theory*','Theory'),program_id='purdue-ai-bs')
    html='<h1>Computer Science Courses: Fall 2026</h1><h2>Undergraduate West Lafayette</h2><table><tr><td><a>CS 17600</a></td><td>Synthetic current title</td></tr><tr><td><a>CS 24300</a></td><td>Synthetic AI</td></tr></table><h2>Undergraduate Indianapolis</h2><table><tr><td><a>CS 17600</a></td><td>Other campus title</td></tr></table>'
    out=m.parse_current_directory(html,program_id='purdue-ai-ba')
    assert not out['courses'] and len(out['notes'])==2
    assert 'Synthetic current title' in out['notes'][0] and 'Other campus' not in str(out)
    with pytest.raises(ValueError):m.parse_current_directory(html.replace('Fall 2026','Spring 2027'),program_id='purdue-ai-ba')


def test_curated_sources_keep_credit_and_version_boundaries():
    for pid in ['purdue-ai-ba','purdue-ai-bs']:
        p=json.loads(Path('data/programs',pid+'.json').read_text());validate_program(p)
        c={c['code']:c for c in p['courses']}
        assert c['CS 18000']['credits']==(None if pid.endswith('-ba') else 4)
        assert 'Dated canonical' in c['CS 18200']['prerequisites']
        assert c['CS 18200']['category_review']['status']=='mixed'
        if pid.endswith('-ba'):
            assert c['CS 17600']['name']=='Introduction to Python'
            assert c['CS 24300']['description'] is None
        else:
            assert c['CS 34800']['category']=='systems'
            assert m.SPEC['CS 48300']['canonical_status']=='proposed'
            assert len(c['CS 48300']['category_review']['source_ids'])==2
    assert m.SPEC['CS 47100']['outline_date']=='1998.08'


def test_optional_full_source_cache():
    root=Path('.cache/research/purdue-course-content')
    if not root.exists():pytest.skip('Ignored official source cache unavailable')
    for code,e in m.SPEC.items():
        p=root/(code.lower().replace(' ','-')+'.html')
        if not p.exists():pytest.skip('Optional source unavailable')
        for pid in e['program_ids']:
            assert m.parse(p.read_text(),program_id=pid,code=code)==m.parse(p.read_text(),program_id=pid,code=code)
    m.parse_directory((root/'canonical-index.html').read_text(),program_id='purdue-ai-bs')
    m.parse_current_directory((root/'current-directory.html').read_text(),program_id='purdue-ai-ba')
