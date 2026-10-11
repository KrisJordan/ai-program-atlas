from collections import Counter
import pytest
from atlas.adapters.rit_language_course_reviews import parse, SOURCES, TITLES, MANIFEST, CODES_BY_URL

ARABIC=SOURCES[0]
SPANISH=next(u for u in SOURCES if '-spanish-' in u)


def fixture(code='MLAR-202', url=ARABIC, amount='4', prereq='Prerequisites: Placement or prior course.'):
    return f'''<main><h1>{TITLES[url]}</h1><h2>Curriculum for 2026-2027 for {TITLES[url]}</h2>
    <table class="sc_courselist"><tbody><tr><td><a class="code_bubble">{code}</a></td><td>Route total</td><td>9</td></tr></tbody></table></main>
    <div class="courseblock"><span class="detail-code">{code}</span><span class="detail-title">New observed title</span>
    <span class="detail-hours_html">({amount} Credits)</span><div class="courseblockextra">New actual description of course work.</div>
    <span class="detail-requisites">{prereq}</span><span class="detail-typically_offered">Typically Offered: Spring</span></div>'''


def test_new_source_facts_are_observed_without_manual_certification():
    c=parse(fixture(),url=ARABIC)['courses'][0]
    assert c['name']=='New observed title' and c['description']=='New actual description of course work.'
    assert c['credits']==4 and c['credit_unit']=='unknown'
    assert c['prerequisites']=='Prerequisites: Placement or prior course.'
    assert c['category']=='other' and 'category_review' not in c
    assert 'Typically Offered: Spring' in c['notes']
    assert parse(fixture(),url=ARABIC)['requirements']==[]


def test_corequisite_label_and_unreported_fields_survive():
    rule='Corequisites: Placement score 2 or MLSP-202 or equivalent.'
    c=parse(fixture('MLSP-310',SPANISH,prereq=rule),url=SPANISH)['courses'][0]
    assert c['prerequisites']==rule
    c=parse(fixture(prereq=''),url=ARABIC)['courses'][0]
    assert c['prerequisites'] is None
    assert any('does not establish unrestricted' in n for n in c['notes'])


def test_ranges_and_zero_are_not_replaced_by_route_amount():
    c=parse(fixture(amount='1–4'),url=ARABIC)['courses'][0]
    assert c['credits'] is None and any('(1–4 Credits)' in n for n in c['notes'])
    assert parse(fixture(amount='0'),url=ARABIC)['courses'][0]['credits']==0
    with pytest.raises(ValueError):parse(fixture(amount='4–1'),url=ARABIC)


@pytest.mark.parametrize('before,after',[
    ('2026-2027','2025-2026'),
    ('<h1>'+TITLES[ARABIC]+'</h1>','<h1>Other program</h1>'),
    ('class="sc_courselist"','class="shell"'),
    ('class="courseblockextra"','class="missing"'),
    ('New actual description of course work.','Loading course description...'),
    ('class="detail-code">MLAR-202','class="detail-code">MLAR-999'),
    ('(4 Credits)','(4 Contact Hours)'),
])
def test_rejects_wrong_source_version_identity_or_incomplete_observation(before,after):
    with pytest.raises(ValueError):parse(fixture().replace(before,after),url=ARABIC)


def test_wrong_route_and_duplicate_card_rejected():
    with pytest.raises(ValueError):parse(fixture(),url='https://example.com')
    with pytest.raises(ValueError):parse(fixture('MLSP-310'),url=ARABIC)
    html=fixture();card=html[html.index('<div class="courseblock">'):]
    with pytest.raises(ValueError):parse(html+card,url=ARABIC)


def test_exact_reviewed_scope_and_source_evidence():
    c=MANIFEST['courses']
    assert len(c)==107 and sum(map(len,CODES_BY_URL.values()))==107 and len(SOURCES)==8
    assert Counter(x['credits'] for x in c.values())=={3:91,4:16}
    assert Counter(x['category'] for x in c.values())=={'human_context':107}
    assert sum(x['prerequisites'] is not None for x in c.values())==61
    assert all(x['description'] and x['category_review']['rationale'] for x in c.values())
    assert all(code in x['category_review']['locator'] for code,x in c.items())
    assert all(x['category_review']['source_ids']==[x['source_id']] for x in c.values())
    assert all(x['credit_unit_source']=='https://www.rit.edu/policies/d014' for x in c.values())
    assert 'course_identity_groups' not in MANIFEST


def test_observed_conflicts_and_content_distinctions_are_preserved():
    c=MANIFEST['courses']
    assert c['MLSP-310']['prerequisites'].startswith('Corequisites:')
    assert any('prose says MLSP 201' in n and 'MLSP-202/202T' in n for n in c['MLSP-301']['notes'])
    assert 'MLJP-302 and (MLJP-315 or MLJP-310)' in c['MLJP-415']['prerequisites']
    assert c['MLJP-310']['prerequisites']=='Permission of the Instructor to enroll.'
    assert c['MLFR-401']['category']=='human_context'
    assert c['MLSP-315']['category']=='human_context'
    assert c['MLCH-410']['category']=='human_context'
    assert all(c[k]['category']=='human_context' for k in ['HIST-130','HIST-135','MLJP-451'])
    assert any('both' in n and 'language' in n for n in c['HIST-130']['notes'])
    assert any('six total credits' in n for n in c['ENGL-418']['notes'])
