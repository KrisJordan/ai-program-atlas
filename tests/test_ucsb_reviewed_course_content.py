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
    assert 'mobile applications' in c['CMPSC 184']['description']
    assert m.SPEC['CMPSC 184']['catalog_year']=='Fall 2017'
    assert c['CMPSC 192']['credits'] is c['CMPSC 196']['credits'] is None
    assert any('1–5' in note and '2–4' in note for note in d['notes'])
    assert c['CMPSC 41']['credits'] is None
    assert 'CMPSC 130A, CMPSC 165A, and CMPSC 165B' in c['CMPSC 188']['prerequisites']
    assert 'recommended' in c['CMPSC 174A']['prerequisites'].lower()
    p=requirement_profile(d)
    assert [p[k]['count']for k in ['required','options','unresolved']]==[20,827,2]
    assert p['options']['categories']['systems']==12
    assert p['options']['categories']['foundations']==10
    assert d['course_identity_groups'][0]['course_ids']==['ucsb-c-lit-155','ucsb-ger-155','ucsb-engl-155ai']


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
        if not courses[code]['source_id'].endswith('-catalog-2026'):
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
        assert c['category']==courses[c['code']]['category']=='mathematics'
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
    assert 'professional environmental writing' in c['WRIT 109ES']['description']
    assert any('formerly WRIT109ES' in n for n in c['WRIT 107EP']['notes'])
    assert 'Writing 2 or 2E or 2LK' in c['WRIT 50E']['prerequisites']
    assert 'freshmen only' in c['WRIT 50E']['prerequisites']
    assert requirement_profile(d)['options']['categories']['human_context']==736


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
        assert x['category']==c[x['code']]['category']
        assert x['source_id']!=c[x['code']]['source_id']  # exact older source observation, not a current refresh
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
    assert courses['ENGL 197']['name']=='Upper-Division Seminar'
    assert len(courses['ENGL 197']['category_review']['source_ids'])==4
    assert courses['ENGL 146AI']['code']!='ENGL 155AI'
    assert 'Winter 2021' in english.SPEC['engl146ai']['term']
    assert courses['ENGL 146AI']['credits']==4
    assert requirement_profile(d)['options']['categories']['human_context']==736


def test_english_all_five_actual_dated_offerings_are_guarded():
    from atlas.adapters import ucsb_english_content as english
    root=Path('.cache/research/ucsb-course-content')
    if not (root/'engl146ai.html').exists():pytest.skip('Optional ignored official-source cache')
    for key in english.SPEC:
        result=english.parse((root/(key+'.html')).read_text(),key=key)
        assert len(result['courses'])==1 and result['requirements']==[]
        if result['courses'][0]['code']=='ENGL 197':
            assert 'description'not in result['courses'][0]  # individual topic cannot certify all sections


def test_current_catalog_guard_keeps_manual_identity_and_roles_separate(monkeypatch):
    from atlas.adapters import ucsb_catalog_course_content as current
    html = '<main><h1>GER155</h1><h3>Full Course Title</h3><p>Synthetic critical analysis; Units Fixed 4; same-course statement.</p><h3>Programs</h3><p>Synthetic optional program.</p></main>'
    fields = 'Synthetic critical analysis; Units Fixed 4; same-course statement.'
    entry = dict(current.SPEC['GER 155'], fields_digest=hashlib.sha256(fields.encode()).hexdigest())
    monkeypatch.setitem(current.SPEC, 'GER 155', entry)
    result = current.parse(html, code='GER 155')
    assert result['requirements'] == []
    assert 'course_identity_groups' not in result
    assert 'category_review' not in result['courses'][0]
    assert result['courses'][0]['prerequisites'] is None
    for changed in [html.replace('Fixed 4', 'Fixed 5'), html.replace('same-course', 'different-course'), html.replace('GER155', 'GER156'), '<main>Loading</main>']:
        with pytest.raises(ValueError):
            current.parse(changed, code='GER 155')


def test_current_crosslisting_uses_reciprocal_evidence_and_retains_raw_codes():
    d=json.loads(Path('data/programs/ucsb-ai-bs.json').read_text())
    group=d['course_identity_groups'][0]
    assert group['canonical_course_id']=='ucsb-c-lit-155'
    assert set(group['source_ids'])=={'ucsb-ai-bs-ger155-catalog-2026','ucsb-ai-bs-clit155-catalog-2026','ucsb-ai-bs-ge-defg-export'}
    assert 'ucsb-engl-146ai'not in group['course_ids']
    profile=requirement_profile(d)
    assert profile['options']['count']==827
    assert profile['options']['source_record_count']==917
    assert profile['options']['categories']['human_context']==736
    assert profile['options']['categories']['other']==44
    from atlas.adapters import ucsb_catalog_course_content as current
    for code, entry in current.SPEC.items():
        key='clit155' if code=='C LIT 155' else code.lower().replace(' ','')
        cache=Path('.cache/research/ucsb-course-content')/(key+'-catalog-visible.html')
        if cache.exists():
            result=current.parse(cache.read_text(), code=code)
            assert result==current.parse(cache.read_text(),code=code)
            seed=next(c for c in d['courses']if c['code']==code)
            assert all(seed[k]==v for k,v in result['courses'][0].items() if not (code in {'CMPSC 41','WRIT 1','WRIT 50'} and k=='credits'))


def test_current_catalog_required_vision_identity_and_precise_eligibility():
    d=json.loads(Path('data/programs/ucsb-ai-bs.json').read_text())
    c={c['code']:c for c in d['courses']}
    assert len(d['course_identity_groups'])==82
    vision=next(r for r in d['requirements']if r['id']=='ucsb-ai-bs-ucsb-cmpsc-181')
    assert vision['kind']=='all' and vision['count'] is None
    assert vision['course_ids']==['ucsb-cmpsc-181','ucsb-ece-181']
    assert c['CMPSC 181']['prerequisites']==c['ECE 181']['prerequisites']
    assert 'Artificial Intelligence' in c['ECE 181']['prerequisites']
    assert 'Computer Engineering majors only' in c['CMPSC 42']['prerequisites']
    assert 'pre-Computer Engineering majors only' in c['ECE 139']['prerequisites']
    assert c['ME 107']['credits']==3
    assert 'consent of instructor' in c['ME 107']['prerequisites']
    assert 'not a required prerequisite' in c['ME 107']['prerequisites']
    assert c['CMPSC 1A']['category']=='ai_ml'
    assert c['CMPSC 25']['category']==c['CMPSC 42']['category']=='foundations'
    assert c['CMPSC 135']['category']=='mathematics'
    profile=requirement_profile(d)
    assert [profile[k]['count']for k in ['required','options','unresolved']]==[20,827,2]
    assert [profile[k]['source_record_count']for k in ['required','options','unresolved']]==[21,917,2]


def test_all_fixed_course_versions_and_recommendation_fields_are_current():
    d=json.loads(Path('data/programs/ucsb-ai-bs.json').read_text());c={x['code']:x for x in d['courses']}
    assert 'CMPSC 130A, CMPSC 165A, and CMPSC 165B' in c['CMPSC 188']['prerequisites']
    assert 'CMPSC 138' in c['CMPSC 188']['prerequisites']
    assert 'prerequisite field independently includes' in c['CMPSC 130A']['prerequisites']
    assert c['MATH 3A']['credits']==4 and 'only receive 2 units' in c['MATH 3A']['prerequisites']
    assert '3BI' in c['MATH 4A']['prerequisites'] and '4AI' in c['MATH 4B']['prerequisites']
    audit=json.loads(Path('research/degree-audit/west-purdue-wpi.json').read_text())
    row=next(x for x in audit['programs']if x['program_id']==d['id'])
    fixed=set(row['expected_course_ids']['required'])
    assert len(fixed)==20
    assert all(x['source_id'].endswith('-catalog-2026') for x in d['courses']if x['id']in fixed)


def test_registration_policy_guards_conditions_without_automatic_major_waiver(monkeypatch):
    from atlas.adapters import ucsb_registration_review as registration
    html='<main><h1>Course Registration</h1><p>GPA 3.0; subject to instructor and department approval.</p></main>'
    entry={**registration.SPEC['registration'],'body_digest':hashlib.sha256(text(BeautifulSoup(html,'html.parser').main).encode()).hexdigest()}
    monkeypatch.setitem(registration.SPEC,'registration',entry)
    result=registration.parse(html,key='registration')
    assert result['courses']==[]
    assert all(r['kind']=='note' and not r['course_ids']for r in result['requirements'])
    assert any('does not say' in r['summary']for r in result['requirements'])
    assert any('LettersandScience' in r['summary']for r in result['requirements'])
    result['requirements'].clear()
    assert registration.parse(html,key='registration')['requirements']
    with pytest.raises(ValueError):registration.parse(html.replace('3.0','2.0'),key='registration')


def test_optional_registration_source_replay():
    from atlas.adapters import ucsb_registration_review as registration
    for key in registration.SPEC:
        cache=Path('.cache/research/ucsb-course-content')/('policy-'+key+'-reviewed.html')
        if not cache.exists():pytest.skip('Optional private source cache')
        result=registration.parse(cache.read_text(),key=key)
        assert result==registration.parse(cache.read_text(),key=key)
        assert 'curriculum_audit'not in result


def test_current_english_metadata_does_not_generalize_seminar_subject(monkeypatch):
    from atlas.adapters import ucsb_catalog_course_content as current
    html='<main><h1>ENGL197</h1><h3>Full Course Title</h3><p>Synthetic variable seminar, four units.</p><h3>Programs</h3><p>Synthetic program.</p></main>'
    entry={**current.SPEC['ENGL 197'],'fields_digest':hashlib.sha256(b'Synthetic variable seminar, four units.').hexdigest()}
    monkeypatch.setitem(current.SPEC,'ENGL 197',entry)
    observation=current.parse(html,code='ENGL 197')['courses'][0]
    assert observation['credits']==4
    assert 'category'not in observation and 'category_review'not in observation
    assert 'upper-division standing' in observation['prerequisites']
    d=json.loads(Path('data/programs/ucsb-ai-bs.json').read_text());c={x['code']:x for x in d['courses']}
    for code in ['ENGL 146AI','ENGL 146DS']:
        assert c[code]['credits']==4 and c[code]['category']=='human_context'
        assert c[code]['source_id'].endswith('-catalog-2026')
        assert 'Writing 2' in c[code]['prerequisites']
    assert 'Fall 2026' in c['ENGL 197']['category_review']['rationale']
    assert 'future' in c['ENGL 197']['category_review']['rationale']
    assert all('ucsb-engl-146ai'not in g['course_ids'] for g in d['course_identity_groups'])


def test_current_entry_writing_preserves_narrow_eligibility_and_unit_conflict():
    from atlas.adapters import ucsb_catalog_course_content as current
    d=json.loads(Path('data/programs/ucsb-ai-bs.json').read_text());c={x['code']:x for x in d['courses']}
    assert current.SPEC['WRIT 1']['credits']==5 and c['WRIT 1']['credits'] is None
    assert c['WRIT 1E']['credits']==4
    assert 'Freshmen only' in c['WRIT 1E']['prerequisites']
    assert 'Computer Engineering majors only' in c['WRIT 1E']['prerequisites']
    assert 'AI is not among' in c['WRIT 1E']['prerequisites']
    assert '6 or lower' in c['WRIT 1']['prerequisites']
    assert c['WRIT 1']['source_id'].endswith('-catalog-2026')
    assert requirement_profile(d)['unresolved']['count']==2


def test_all_represented_writing_versions_preserve_exact_alternatives():
    from atlas.adapters import ucsb_catalog_course_content as current
    d=json.loads(Path('data/programs/ucsb-ai-bs.json').read_text());c={x['code']:x for x in d['courses']}
    writing=[x for x in d['courses']if x['code'] in current.SPEC and x['code'].startswith('WRIT ')]
    assert len(writing)==26
    assert all(x['source_id'].endswith('-catalog-2026')for x in writing)
    assert c['WRIT 50']['credits'] is None and current.SPEC['WRIT 50']['credits']==5
    assert 'Exam: AP 36 >=4' in c['WRIT 105CW']['prerequisites']
    assert 'Exam: IB BL >= 6' in c['WRIT 105SW']['prerequisites']
    assert 'Spring 2005 and Summer 2011' in c['WRIT 107G']['prerequisites']
    assert 'Summer 2003 and Spring 2010' in c['WRIT 107M']['prerequisites']
    assert 'legal repeat' in c['WRIT 107WC']['prerequisites']
    assert c['WRIT 105CD']['category_review']['status']=='mixed'
    assert {i for g in d['course_identity_groups'] for i in g['course_ids'] if i.startswith('ucsb-writ-')} == {'ucsb-writ-w-6r'}


def test_current_cs_options_keep_permission_alternatives_and_source_barrier():
    d=json.loads(Path('data/programs/ucsb-ai-bs.json').read_text());c={x['code']:x for x in d['courses']}
    assert 'no required-prerequisite field' in c['CMPSC 132']['prerequisites'].lower()
    assert 'not a required prerequisite' in c['CMPSC 132']['prerequisites']
    assert 'B or better' in c['CMPSC 134']['prerequisites']
    assert 'or by consent of department' in c['CMPSC 172']['prerequisites']
    assert 'Winter 2003-Summer 2021' in c['CMPSC 172']['prerequisites']
    assert c['CMPSC 176C']['source_id'].endswith('-catalog-2026')
    assert not c['CMPSC 177']['source_id'].endswith('-catalog-2026')
    ledger=json.loads(Path('research/degree-audit/west-purdue-wpi.json').read_text())
    audit=next(r for r in ledger['programs']if r['program_id']=='ucsb-ai-bs')
    assert audit['status']=='in_progress' and 'downloaded856' in audit['accessible_work_remaining']
    assert any(s['access_status']=='human_verification_challenge_not_bypassed'for s in audit['sources'])
