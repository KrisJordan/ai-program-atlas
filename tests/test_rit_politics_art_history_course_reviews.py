import pytest
from atlas.adapters.rit_politics_art_history_course_reviews import parse, SOURCES, TITLES, MANIFEST, CODES_BY_URL

POLS=SOURCES[0];ART=SOURCES[1]


def fixture(code='ARTH-368',url=ART,amount='3',prereq='Prerequisites: ARTH-136 or equivalent course.'):
    return f'''<main><h1>{TITLES[url]}</h1><h2>Curriculum for 2026-2027 for {TITLES[url]}</h2>
    <table class="sc_courselist"><tbody><tr><td><a class="code_bubble">{code}</a></td><td>Group</td><td>9</td></tr></tbody></table></main>
    <div class="courseblock"><span class="detail-code">{code}</span><span class="detail-title">Changed current title</span>
    <span class="detail-hours_html">({amount} Credits)</span><div class="courseblockextra">Changed full source description.</div>
    <span class="detail-requisites">{prereq}</span></div>'''


def test_changed_source_fields_are_not_manual_certification():
    c=parse(fixture(amount='4'),url=ART)['courses'][0]
    assert c['name']=='Changed current title' and c['description']=='Changed full source description.'
    assert c['prerequisites']=='Prerequisites: ARTH-136 or equivalent course.'
    assert c['credits']==4 and c['credit_unit']=='unknown'
    assert c['category']=='other' and 'category_review' not in c
    assert parse(fixture(),url=ART)['requirements']==[]


def test_missing_conditions_ranges_and_zero_stay_explicit():
    c=parse(fixture('POLS-200',POLS,'1–4',''),url=POLS)['courses'][0]
    assert c['credits'] is None and c['prerequisites'] is None
    assert any('(1–4 Credits)' in n for n in c['notes'])
    assert any('does not establish unrestricted' in n for n in c['notes'])
    assert parse(fixture(amount='0'),url=ART)['courses'][0]['credits']==0
    with pytest.raises(ValueError):parse(fixture(amount='4–1'),url=ART)


@pytest.mark.parametrize('before,after',[
 ('2026-2027','2025-2026'),
 ('<h1>Art History Immersion</h1>','<h1>Different program</h1>'),
 ('class="sc_courselist"','class="shell"'),
 ('class="courseblockextra"','class="missing"'),
 ('Changed full source description.','Loading course description...'),
 ('class="detail-code">ARTH-368','class="detail-code">ARTH-999'),
 ('(3 Credits)','(3 Contact Hours)'),
])
def test_wrong_version_identity_or_incomplete_source_rejected(before,after):
    with pytest.raises(ValueError):parse(fixture().replace(before,after),url=ART)


def test_wrong_route_and_duplicate_cards_rejected():
    with pytest.raises(ValueError):parse(fixture(),url='https://example.com')
    with pytest.raises(ValueError):parse(fixture('POLS-200'),url=ART)
    html=fixture();card=html[html.index('<div class="courseblock">'):]
    with pytest.raises(ValueError):parse(html+card,url=ART)


def test_exact_manual_allocation_evidence_and_missingness():
    c=MANIFEST['courses']
    assert set(c)==set('''POLS-200 POLS-205 POLS-210 POLS-215 POLS-220 POLS-230 POLS-250 POLS-285 POLS-290 POLS-295 POLS-300 POLS-305 POLS-310 POLS-315 POLS-320 POLS-325 POLS-330 POLS-335 POLS-345 POLS-355 POLS-360 POLS-370 POLS-375 POLS-380 POLS-384 POLS-390 POLS-415 POLS-420 POLS-425 POLS-430 POLS-435 POLS-440 POLS-445 POLS-455 POLS-460 POLS-465 POLS-485 POLS-490 POLS-541 POLS-542 ARTH-366 ARTH-368 ARTH-369 ARTH-379 ARTH-400 ARTH-457 ARTH-521 ARTH-522 ARTH-541 ARTH-544 ARTH-550 ARTH-551 ARTH-555 ARTH-556 ARTH-558 ARTH-568 ARTH-573 ARTH-574 ARTH-577 ARTH-578 ARTH-584 ARTH-588'''.split())
    assert sum(map(len,CODES_BY_URL.values()))==62
    assert all(x['credits']==3 and x['published_credit_text']=='(3 Credits)' for x in c.values())
    assert sum(x['prerequisites'] is not None for x in c.values())==11
    assert all(x['category']=='human_context' and x['category_review']['status']=='reviewed' for x in c.values())
    assert all(x['description'] and x['category_review']['rationale'] and code in x['category_review']['locator'] for code,x in c.items())
    assert all(x['category_review']['source_ids']==[x['source_id']] for x in c.values())
    assert 'course_identity_groups' not in MANIFEST


def test_actual_content_and_conditional_preparation_distinctions():
    c=MANIFEST['courses']
    assert c['ARTH-400']['prerequisites']=='ARTH-124 or ARTH-135 or ARTH-136 or equivalent courses.'
    assert any('strongly recommended, not stated as mandatory' in n for n in c['ARTH-400']['notes'])
    assert any('degree-seeking undergraduate' in n for n in c['ARTH-551']['notes'])
    assert any('different topics' in n for n in c['ARTH-555']['notes'])
    assert any('repeated when that focus changes' in n for n in c['POLS-375']['notes'])
    assert 'not technical methods' in c['POLS-370']['category_review']['rationale']
    assert 'not taught as technical computing' in c['ARTH-568']['category_review']['rationale']
