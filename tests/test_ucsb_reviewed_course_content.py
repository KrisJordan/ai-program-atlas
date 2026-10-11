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
    assert any('1–5' in note and '2–4' in note for note in d['notes'])
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


def test_math_source_does_not_invent_units_or_degree_obligations(monkeypatch):
    from atlas.adapters import ucsb_math_content as math
    html=''.join(f'<h2>Math {code.split()[1]}</h2><p>Synthetic prerequisite.</p><p>Synthetic calculus.</p>'for code in math.SPEC)
    digest=hashlib.sha256(b'Synthetic prerequisite. Synthetic calculus.').hexdigest()
    monkeypatch.setattr(math,'SPEC',{code:{**e,'block_digest':digest}for code,e in math.SPEC.items()})
    result=math.parse(html)
    assert len(result['courses'])==5 and result['requirements']==[]
    assert all('credits'not in c and 'category_review'not in c for c in result['courses'])
    with pytest.raises(ValueError):math.parse(html.replace('Synthetic calculus.','Changed calculus.',1))


def test_math_actual_cache_matches_reviewed_metadata():
    from atlas.adapters import ucsb_math_content as math
    cache=Path('.cache/research/ucsb-course-content/math-courses.html')
    if not cache.exists():pytest.skip('Optional ignored official-source cache')
    observed=math.parse(cache.read_text());d=json.loads(Path('data/programs/ucsb-ai-bs.json').read_text());courses={c['code']:c for c in d['courses']}
    for c in observed['courses']:
        assert all(c[k]==courses[c['code']][k]for k in c)
        assert courses[c['code']]['credits']==4


def test_writing_series_guard_and_no_automatic_identity_or_prerequisite_role(monkeypatch):
    from atlas.adapters import ucsb_writing_content as writing
    html='<main><h3>Writing 105AI. Synthetic writing</h3><p>4 units; synthetic eligibility.</p></main>'
    e=dict(writing.SPEC['upper']['courses']['WRIT 105AI']);e['heading']='Writing 105AI. Synthetic writing'
    data={**writing.SPEC['upper'],'courses':{'WRIT 105AI':e},'main_digest':hashlib.sha256(text(BeautifulSoup(html,'html.parser').main).encode()).hexdigest()}
    monkeypatch.setitem(writing.SPEC,'upper',data)
    result=writing.parse(html,section='upper')
    assert result['requirements']==[] and result['courses'][0]['category']=='human_context'
    assert 'category_review'not in result['courses'][0]
    with pytest.raises(ValueError):writing.parse(html.replace('4 units','5 units'),section='upper')
    d=json.loads(Path('data/programs/ucsb-ai-bs.json').read_text());c={x['code']:x for x in d['courses']}
    assert c['WRIT 2']['credits']==5 and c['WRIT 2E']['credits']==4
    assert c['WRIT 105CD']['category_review']['status']=='mixed'
    assert c['WRIT 109ES']['description'] is None
    assert 'formerly' in c['WRIT 107EP']['prerequisites']
    assert 'does not independently restate' in c['WRIT 50E']['prerequisites']
    assert requirement_profile(d)['options']['categories']['human_context']==26


def test_writing_actual_cache_matches_all25_read_blocks():
    from atlas.adapters import ucsb_writing_content as writing
    root=Path('.cache/research/ucsb-course-content')
    if not (root/'writing-upper.html').exists():pytest.skip('Optional ignored official-source cache')
    d=json.loads(Path('data/programs/ucsb-ai-bs.json').read_text());c={x['code']:x for x in d['courses']}
    observed=[]
    for section in writing.SPEC:
        observed+=writing.parse((root/('writing-'+section+'.html')).read_text(),section=section)['courses']
    assert len(observed)==25
    for x in observed:
        excluded={'credits','description'} if x['code']=='WRIT 1' else set()
        assert all(x[k]==c[x['code']][k]for k in x if k not in excluded)
        if x['code']=='WRIT 1':
            assert x['credits']==5 and c[x['code']]['credits'] is None


def test_alternate_gear_comparison_does_not_claim_pdf_html_refresh_or_resolve_conflict():
    adapter=importlib.import_module('atlas.adapters.ucsb-ai-bs.adapter')
    url='https://engineering.ucsb.edu/sites/default/files/images/26-27_GEAR.pdf'
    assert url in adapter.SOURCES and url not in adapter.SOURCE_PARSERS
    d=json.loads(Path('data/programs/ucsb-ai-bs.json').read_text())
    assert any(s['url']==url and 'visually' in s['locator']for s in d['sources'])
    assert next(c for c in d['courses']if c['code']=='CMPSC 41')['credits'] is None
    assert any('190 AA–ZZ' in r.get('summary','')for r in d['requirements'])


def test_english_offering_guards_do_not_infer_current_version_or_gold_prerequisites(monkeypatch):
    from atlas.adapters import ucsb_english_content as english
    html='<main>Course Number: ENGL 146AI Quarter: Winter 2021 Synthetic literary description.</main>'
    e={**english.SPEC['engl146ai'],'main_digest':hashlib.sha256(text(BeautifulSoup(html,'html.parser').main).encode()).hexdigest()}
    monkeypatch.setitem(english.SPEC,'engl146ai',e)
    result=english.parse(html,key='engl146ai');c=result['courses'][0]
    assert c['prerequisites'] is None and 'credits'not in c
    assert c['category']=='human_context' and 'category_review'not in c
    with pytest.raises(ValueError):english.parse(html.replace('Winter 2021','Fall 2026'),key='engl146ai')
    d=json.loads(Path('data/programs/ucsb-ai-bs.json').read_text());courses={c['code']:c for c in d['courses']}
    assert courses['ENGL 197']['name']=='Upper Division Seminar'
    assert len(courses['ENGL 197']['category_review']['source_ids'])==3
    assert courses['ENGL 146AI']['code']!='ENGL 155AI'
    assert 'Winter2021' in courses['ENGL 146AI']['description']
    assert requirement_profile(d)['options']['categories']['human_context']==26


def test_english_all_five_actual_dated_offerings_are_guarded():
    from atlas.adapters import ucsb_english_content as english
    root=Path('.cache/research/ucsb-course-content')
    if not (root/'engl146ai.html').exists():pytest.skip('Optional ignored official-source cache')
    for key in english.SPEC:
        result=english.parse((root/(key+'.html')).read_text(),key=key)
        assert len(result['courses'])==1 and result['requirements']==[]
        if result['courses'][0]['code']=='ENGL 197':
            assert 'description'not in result['courses'][0]  # individual topic cannot certify all sections
