from collections import Counter
import pytest
from atlas.adapters.rit_history_economics_course_reviews import parse, SOURCES, TITLES, MANIFEST, CODES_BY_URL

ECON=SOURCES[0]
HIST=SOURCES[1]


def fixture(code='ECON-403', url=ECON, amount='3', prereq='Prerequisites: Calculus and statistics.'):
    return f'''<main><h1>{TITLES[url]}</h1><h2>Curriculum for 2026-2027 for {TITLES[url]}</h2>
    <table class="sc_courselist"><tbody><tr><td><a class="code_bubble">{code}</a></td><td>Group</td><td>9</td></tr></tbody></table></main>
    <div class="courseblock"><span class="detail-code">{code}</span><span class="detail-title">Changed source title</span>
    <span class="detail-hours_html">({amount} Credits)</span><div class="courseblockextra">New source description.</div>
    <span class="detail-requisites">{prereq}</span><span class="detail-typically_offered">Typically Offered: Fall</span></div>'''


def test_observes_changed_fields_without_certifying_manual_content():
    c=parse(fixture(amount='4'),url=ECON)['courses'][0]
    assert c['credits']==4 and c['credit_unit']=='unknown'
    assert c['description']=='New source description.' and c['name']=='Changed source title'
    assert c['prerequisites']=='Prerequisites: Calculus and statistics.'
    assert c['category']=='other' and 'category_review' not in c
    assert 'Typically Offered: Fall' in c['notes']
    assert parse(fixture(),url=ECON)['requirements']==[]


def test_missing_prerequisite_range_and_zero_preserved():
    c=parse(fixture('HIST-101',HIST,amount='1–4',prereq=''),url=HIST)['courses'][0]
    assert c['credits'] is None and c['prerequisites'] is None
    assert any('(1–4 Credits)' in n for n in c['notes'])
    assert any('does not establish unrestricted' in n for n in c['notes'])
    assert parse(fixture(amount='0'),url=ECON)['courses'][0]['credits']==0
    with pytest.raises(ValueError):parse(fixture(amount='4–1'),url=ECON)


@pytest.mark.parametrize('before,after',[
 ('2026-2027','2025-2026'),
 ('<h1>Economics Immersion</h1>','<h1>Other program</h1>'),
 ('class="sc_courselist"','class="shell"'),
 ('class="courseblockextra"','class="missing"'),
 ('New source description.','Loading course description...'),
 ('class="detail-code">ECON-403','class="detail-code">ECON-999'),
 ('(3 Credits)','(3 Contact Hours)'),
])
def test_rejects_unbound_or_incomplete_evidence(before,after):
    with pytest.raises(ValueError):parse(fixture().replace(before,after),url=ECON)


def test_wrong_route_and_duplicates_rejected():
    with pytest.raises(ValueError):parse(fixture(),url='https://example.com')
    with pytest.raises(ValueError):parse(fixture('HIST-101'),url=ECON)
    html=fixture();card=html[html.index('<div class="courseblock">'):]
    with pytest.raises(ValueError):parse(html+card,url=ECON)


def test_exact_manual_scope_and_content_evidence():
    c=MANIFEST['courses']
    assert set(c)==set('''ECON-101 ECON-201 ECON-401 ECON-402 ECON-403 ECON-404 ECON-405 ECON-406 ECON-407 ECON-408 ECON-410 ECON-411 ECON-421 ECON-422 ECON-430 ECON-431 ECON-433 ECON-441 ECON-445 ECON-448 ECON-450 ECON-453 ECON-520 HIST-101 HIST-102 HIST-103 HIST-104 HIST-125 HIST-150 HIST-170 HIST-180 HIST-190 HIST-221 HIST-230 HIST-240 HIST-242 HIST-250 HIST-251 HIST-255 HIST-282 HIST-290 HIST-301 HIST-302 HIST-311 HIST-322 HIST-323 HIST-324 HIST-325 HIST-326 HIST-330 HIST-333 HIST-335 HIST-340 HIST-345 HIST-350 HIST-351 HIST-355 HIST-360 HIST-369 HIST-370 HIST-391 HIST-421 HIST-439 HIST-480'''.split())
    assert sum(map(len,CODES_BY_URL.values()))==64
    assert all(x['credits']==3 and x['published_credit_text']=='(3 Credits)' for x in c.values())
    assert sum(x['prerequisites'] is not None for x in c.values())==22
    assert Counter(x['category'] for x in c.values())=={'human_context':43,'applications':17,'mathematics':3,'other':1}
    assert all(x['description'] and x['category_review']['rationale'] and code in x['category_review']['locator'] for code,x in c.items())
    assert all(x['category_review']['source_ids']==[x['source_id']] for x in c.values())
    assert 'course_identity_groups' not in MANIFEST


def test_methods_versus_domain_or_history_and_exact_eligibility():
    c=MANIFEST['courses']
    assert {k for k,v in c.items() if v['category']=='mathematics'}=={'ECON-403','ECON-404','ECON-410'}
    assert c['ECON-411']['category']==c['ECON-430']['category']=='applications'
    assert c['ECON-408']['category_review']['status']=='mixed'
    assert c['ECON-408']['category_review']['candidate_categories']==['applications','human_context']
    assert all(c[k]['category']=='human_context' for k in ['HIST-180','HIST-282','HIST-326','HIST-480'])
    assert '1016-171T' in c['ECON-403']['prerequisites']
    assert any('not resolved' in n for n in c['ECON-401']['notes'])
    assert any('same topic' in n for n in c['HIST-302']['notes'])
