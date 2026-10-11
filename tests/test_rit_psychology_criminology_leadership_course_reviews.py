import pytest
from atlas.adapters.rit_psychology_criminology_leadership_course_reviews import parse, SOURCES, TITLES, CODES_BY_URL, MANIFEST


def fixture(code='PSYC-224H', url=SOURCES[0], amount='3', prereq='Honors status or GPA at least3.3.'):
    return f'''<main><h1>{TITLES[url]}</h1><h2>Curriculum for 2026-2027 for {TITLES[url]}</h2>
    <table class="sc_courselist"><tbody><tr><td><a class="code_bubble">{code}</a></td><td>Route amount9</td><td>9</td></tr></tbody></table></main>
    <div class="courseblock"><span class="detail-code">{code}</span><span class="detail-title">Synthetic changed title</span>
    <span class="detail-hours_html">({amount} Credits)</span><div class="courseblockextra">Synthetic changed account of empirical perception.</div>
    <span class="detail-requisites">{prereq}</span><span class="detail-contact_hours">Contact Hours: Lecture1</span></div>'''


def test_refresh_observes_changed_facts_without_replaying_subject_review():
    c=parse(fixture(amount='4',prereq='Department permission required.'),url=SOURCES[0])['courses'][0]
    assert c['credits']==4 and c['credit_unit']=='unknown'
    assert c['name']=='Synthetic changed title'
    assert c['description']=='Synthetic changed account of empirical perception.'
    assert c['prerequisites']=='Department permission required.'
    assert c['category']=='other' and 'category_review' not in c
    assert 'Contact Hours: Lecture1' in c['notes']
    assert parse(fixture(),url=SOURCES[0])['requirements']==[]


def test_variable_zero_and_unreported_prerequisites_preserve_missingness():
    c=parse(fixture(amount='1–4',prereq=''),url=SOURCES[0])['courses'][0]
    assert c['credits'] is None and c['prerequisites'] is None
    assert any('(1–4 Credits)' in n for n in c['notes'])
    assert any('does not establish unrestricted' in n for n in c['notes'])
    assert parse(fixture(amount='0'),url=SOURCES[0])['courses'][0]['credits']==0


@pytest.mark.parametrize('before,after',[
    ('2026-2027','2025-2026'),
    ('<h1>Psychology Immersion</h1>','<h1>Unrelated Immersion</h1>'),
    ('class="courseblockextra"','class="missing"'),
    ('class="sc_courselist"','class="shell"'),
    ('class="detail-code">PSYC-224H','class="detail-code">PSYC-999'),
    ('(3 Credits)','(3 Contact Hours)'),
])
def test_rejects_wrong_source_identity_year_and_unsettled_card(before,after):
    with pytest.raises(ValueError):parse(fixture().replace(before,after),url=SOURCES[0])


def test_rejects_unassigned_card_wrong_route_and_duplicates():
    with pytest.raises(ValueError):parse(fixture(),url='https://example.com')
    with pytest.raises(ValueError):parse(fixture(code='PSYC-101'),url=SOURCES[0])
    with pytest.raises(ValueError):parse(fixture(code='PSYC-431'),url=SOURCES[0])
    html=fixture();card=html[html.index('<div class="courseblock">'):]
    with pytest.raises(ValueError):parse(html+card,url=SOURCES[0])


def test_all54_scope_is_exact_and_manual_review_sources_registered():
    c=MANIFEST['courses']
    assert len(c)==54 and sum(len(v) for v in CODES_BY_URL.values())==54
    assert sum(v['prerequisites'] is not None for v in c.values())==24
    assert all(v['credits']==3 and v['published_credit_text']=='(3 Credits)' for v in c.values())
    expected={
        'PSYC':'101H 221 221H 222 224 224H 225 226 231 234 235 236 237 238 239 240 241 242 255 300 431',
        'CRIM':'110 210 215 220 225 230 240 260 265 275 285 290 299 315 350 489 510',
        'LEAD':'200 201 203 300 301 303 304 305 306 307 308 309 310 311 312 313',
    }
    assert set(c)=={prefix+'-'+number for prefix,numbers in expected.items() for number in numbers.split()}
    assert all(v['category_review']['rationale'] and v['category_review']['source_ids']==[v['source_id']] for v in c.values())
    assert all(code in v['category_review']['locator'] for code,v in c.items())


def test_individual_subject_and_honors_prerequisite_decisions():
    c=MANIFEST['courses']
    assert c['PSYC-222']['category']=='applications'
    assert c['PSYC-235']['category']=='applications' # Learning is biological/behavioral, not ML.
    assert c['PSYC-431']['category']=='applications' # Discussing AI does not establish AI methods.
    assert c['CRIM-510']['category']=='human_context'
    assert c['LEAD-301']['category']=='applications'
    assert c['LEAD-303']['category']=='human_context'
    assert c['PSYC-237']['category_review']['status']=='mixed'
    assert {code for code,v in c.items() if v['category_review']['status']=='unclassified'}=={'PSYC-300','CRIM-489','LEAD-308'}
    assert '3.3 cumulative GPA' in c['PSYC-224H']['prerequisites']
    assert '200 level' in c['PSYC-221']['prerequisites'] and 'equivalent course' in c['PSYC-221H']['prerequisites']
    assert c['PSYC-255']['prerequisites']=='Pre-requisites: PSYC-101 and (STAT-145 or MATH-251) or equivalent courses.'
    assert any('Lecture 1' in n for n in c['PSYC-255']['notes'])
    assert all(v['prerequisites'] is None for code,v in c.items() if code.startswith('LEAD-'))
    assert 'course_identity_groups' not in MANIFEST
