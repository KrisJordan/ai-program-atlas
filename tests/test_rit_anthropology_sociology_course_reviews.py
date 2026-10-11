import json
from pathlib import Path
import pytest
from atlas.adapters.rit_anthropology_sociology_course_reviews import parse, SOURCES, TITLES, CODES_BY_URL, MANIFEST


def fixture(code='ANTH-303', url=SOURCES[0], amount='3', prereq='Permission of instructor.'):
    return f'''<main><h1>{TITLES[url]}</h1><h2>Curriculum for 2026-2027 for {TITLES[url]}</h2>
    <table class="sc_courselist"><tbody><tr><td><a class="code_bubble">{code}</a></td><td>Table amount intentionally 9</td><td>9</td></tr></tbody></table></main>
    <div class="courseblock"><span class="detail-code">{code}</span><span class="detail-title">Synthetic changed title</span>
    <span class="detail-hours_html">({amount} Credits)</span><div class="courseblockextra">Synthetic changed description of methods.</div>
    <span class="detail-requisites">{prereq}</span><span class="detail-contact_hours">Contact Hours: Laboratory 2, Lecture 2</span></div>'''


def test_reads_actual_observation_fields_not_manual_review_or_route_amount():
    c=parse(fixture(amount='4'),url=SOURCES[0])['courses'][0]
    assert c['credits']==4 and c['credit_unit']=='unknown'
    assert c['name']=='Synthetic changed title'
    assert c['description']=='Synthetic changed description of methods.'
    assert c['prerequisites']=='Permission of instructor.'
    assert c['category']=='other' and 'category_review' not in c
    assert 'Contact Hours: Laboratory 2, Lecture 2' in c['notes']
    assert parse(fixture(),url=SOURCES[0])['requirements']==[]


def test_variable_zero_and_missing_prerequisites_are_preserved():
    variable=parse(fixture(amount='1–4',prereq=''),url=SOURCES[0])['courses'][0]
    assert variable['credits'] is None and variable['prerequisites'] is None
    assert any('(1–4 Credits)' in n for n in variable['notes'])
    assert any('does not establish unrestricted' in n for n in variable['notes'])
    assert parse(fixture(amount='0'),url=SOURCES[0])['courses'][0]['credits']==0


@pytest.mark.parametrize('before,after', [
    ('2026-2027','2025-2026'),
    ('<h1>Cultural Anthropology Immersion</h1>','<h1>Unrelated Immersion</h1>'),
    ('class="courseblockextra"','class="missing"'),
    ('class="sc_courselist"','class="shell"'),
    ('class="detail-code">ANTH-303','class="detail-code">ANTH-999'),
    ('(3 Credits)','(3 Contact Hours)'),
])
def test_rejects_wrong_identity_version_unbound_or_incomplete_cards(before,after):
    with pytest.raises(ValueError):parse(fixture().replace(before,after),url=SOURCES[0])


def test_rejects_wrong_source_route_and_duplicate_cards():
    with pytest.raises(ValueError):parse(fixture(),url='https://example.com')
    with pytest.raises(ValueError):parse(fixture('ANTH-215'),url=SOURCES[0])
    html=fixture();card=html[html.index('<div class="courseblock">'):]
    with pytest.raises(ValueError):parse(html+card,url=SOURCES[0])


def test_all_57_manual_records_have_individual_evidence_and_exact_scope():
    c=MANIFEST['courses']
    assert len(c)==57 and sum(len(v) for v in CODES_BY_URL.values())==57
    assert len([v for v in c.values() if v['prerequisites'] is not None])==5
    assert all(v['credits']==3 and v['published_credit_text']=='(3 Credits)' for v in c.values())
    assert set(c)==set('''ANTH-102 ANTH-103 ANTH-104 ANTH-105 ANTH-205 ANTH-210 ANTH-215 ANTH-220 ANTH-230 ANTH-244 ANTH-245 ANTH-246 ANTH-250 ANTH-260 ANTH-265 ANTH-270 ANTH-295 ANTH-301 ANTH-302 ANTH-303 ANTH-310 ANTH-312 ANTH-325 ANTH-328 ANTH-341 ANTH-345 ANTH-360 ANTH-361 ANTH-375 ANTH-380 ANTH-385 ANTH-410 ANTH-415 ANTH-420 ANTH-425 ANTH-430 ANTH-435 ANTH-489 INGS-205 INGS-270 SOCI-210 SOCI-220 SOCI-225 SOCI-230 SOCI-235 SOCI-240 SOCI-246 SOCI-295 SOCI-301 SOCI-302 SOCI-303 SOCI-322 SOCI-330 SOCI-345 SOCI-355 SOCI-361 SOCI-370'''.split())
    assert all(v['category_review']['rationale'] and v['category_review']['source_ids']==[v['source_id']] for v in c.values())
    assert all(v['description'] and code in v['category_review']['locator'] for code,v in c.items())


def test_subject_and_eligibility_distinctions_are_not_title_inference():
    c=MANIFEST['courses']
    assert c['ANTH-303']['category']==c['SOCI-303']['category']=='mathematics'
    assert c['ANTH-361']['category']==c['SOCI-361']['category']=='human_context'
    assert c['ANTH-415']['category']=='applications'
    assert c['ANTH-435']['category_review']['status']=='mixed'
    assert c['ANTH-489']['category_review']['status']=='unclassified'
    assert '2nd year' in c['SOCI-370']['prerequisites']
    for code in ['ANTH-380','SOCI-235','SOCI-355']:
        assert any('Global campuses' in n for n in c[code]['notes'])
    assert 'ANTH-235' not in c and 'SOCI-395' not in c
    assert 'course_identity_groups' not in MANIFEST
