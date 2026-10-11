"""Source-specific departmental observations preserve roles and uncertainty."""
import hashlib
import importlib
import json
from pathlib import Path
import pytest
from atlas.adapters import ucsb_reviewed_course_content as m
from atlas.adapters.cmu_bs.common import text
from atlas.curriculum_profile import requirement_profile
from bs4 import BeautifulSoup


def fixture(code='CMPSC 192', units='1-5'):
    return f'''<h1>Synthetic project</h1><article class="course">
    <div class="field--name-field-course-number"><div class="field--item">{code}</div></div>
    <div class="field--name-field-course-units"><div class="field--item">{units}</div></div>
    <div class="field--name-field-course-des"><div class="field--item">Synthetic description; consent required.</div></div></article>'''


def test_full_article_guard_drops_changed_units_and_prerequisites(monkeypatch):
    html=fixture();entry=dict(m.SPEC['CMPSC 192']);entry['name']='Synthetic project'
    entry['article_digest']=hashlib.sha256(text(BeautifulSoup(html,'html.parser').article).encode()).hexdigest()
    monkeypatch.setitem(m.SPEC,'CMPSC 192',entry)
    result=m.parse(html,code='CMPSC 192');course=result['courses'][0]
    assert course['credits'] is None and course['credit_unit']=='quarter_hours'
    assert result['requirements']==[] and 'category_review'not in course
    for changed in [html.replace('1-5','4'),html.replace('consent required','no consent'),html.replace('CMPSC 192','CMPSC 196'),html.replace('Synthetic project','Changed')]:
        with pytest.raises(ValueError):m.parse(changed,code='CMPSC 192')


def test_real_seed_exact_roles_and_limits():
    d=json.loads(Path('data/programs/ucsb-ai-bs.json').read_text());c={x['code']:x for x in d['courses']}
    assert len(m.SPEC)==35
    assert c['CMPSC 111']['category']==c['CMPSC 178']['category']=='mathematics'
    assert c['CMPSC 156']['category']=='foundations'
    assert c['CMPSC 186']['category']=='systems'
    assert c['CMPSC 185']['category_review']['status']=='mixed'
    assert c['CMPSC 184']['description'] is None
    assert m.SPEC['CMPSC 184']['catalog_year']=='Fall 2017'
    assert c['CMPSC 192']['credits'] is c['CMPSC 196']['credits'] is None
    assert '1–5' in d['notes'][-1] and '2–4' in d['notes'][-1]
    assert c['CMPSC 41']['credits'] is None
    assert 'No required prerequisites' in c['CMPSC 188']['prerequisites']
    assert 'recommended' in c['CMPSC 174A']['prerequisites']
    p=requirement_profile(d)
    assert [p[k]['count']for k in ['required','options','unresolved']]==[19,65,2]
    assert p['options']['categories']['systems']==12
    assert p['options']['categories']['foundations']==8
    assert not d.get('course_identity_groups')


def test_registered_parsers_observe_all_available_cached_pages():
    adapter=importlib.import_module('atlas.adapters.ucsb-ai-bs.adapter')
    root=Path('.cache/research/ucsb-course-content')
    if not (root/'cmpsc-9.html').exists():pytest.skip('Optional ignored official-source cache')
    d=json.loads(Path('data/programs/ucsb-ai-bs.json').read_text());courses={c['code']:c for c in d['courses']}
    for code,e in m.SPEC.items():
        html=(root/(code.lower().replace(' ','-')+'.html')).read_text()
        result=adapter.SOURCE_PARSERS[e['url']](html)
        assert result==adapter.SOURCE_PARSERS[e['url']](html)
        c=result['courses'][0]
        assert all(c[k]==courses[code][k]for k in c)
        assert 'category_review'not in c
