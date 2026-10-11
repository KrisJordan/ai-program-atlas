import pytest
from atlas.adapters.rit_performance_course_reviews import parse, SOURCES, TITLES, MANIFEST, CODES_BY_URL

POLS=SOURCES[0];ART=SOURCES[1]


def fixture(code='PRFL-251',url=ART,amount='3',prereq='Prerequisites: PRFL-250 or equivalent course.'):
    return f'''<main><h1>{TITLES[url]}</h1><h2>Curriculum for 2026-2027 for {TITLES[url]}</h2>
    <table class="sc_courselist"><tbody><tr><td><a class="code_bubble">{code}</a></td><td>Group</td><td>9</td></tr></tbody></table></main>
    <div class="courseblock"><span class="detail-code">{code}</span><span class="detail-title">Changed current title</span>
    <span class="detail-hours_html">({amount} Credits)</span><div class="courseblockextra">Changed full source description.</div>
    <span class="detail-requisites">{prereq}</span></div>'''


def test_changed_source_fields_are_not_manual_certification():
    c=parse(fixture(amount='4'),url=ART)['courses'][0]
    assert c['name']=='Changed current title' and c['description']=='Changed full source description.'
    assert c['prerequisites']=='Prerequisites: PRFL-250 or equivalent course.'
    assert c['credits']==4 and c['credit_unit']=='unknown'
    assert c['category']=='other' and 'category_review' not in c
    assert parse(fixture(),url=ART)['requirements']==[]


def test_missing_conditions_ranges_and_zero_stay_explicit():
    c=parse(fixture('PRFL-220',POLS,'1–4',''),url=POLS)['courses'][0]
    assert c['credits'] is None and c['prerequisites'] is None
    assert any('(1–4 Credits)' in n for n in c['notes'])
    assert any('does not establish unrestricted' in n for n in c['notes'])
    assert parse(fixture(amount='0'),url=ART)['courses'][0]['credits']==0
    with pytest.raises(ValueError):parse(fixture(amount='4–1'),url=ART)


@pytest.mark.parametrize('before,after',[
 ('2026-2027','2025-2026'),
 ('<h1>Music Immersion</h1>','<h1>Different program</h1>'),
 ('class="sc_courselist"','class="shell"'),
 ('class="courseblockextra"','class="missing"'),
 ('Changed full source description.','Loading course description...'),
 ('class="detail-code">PRFL-251','class="detail-code">PRFL-999'),
 ('(3 Credits)','(3 Contact Hours)'),
])
def test_wrong_version_identity_or_incomplete_source_rejected(before,after):
    with pytest.raises(ValueError):parse(fixture().replace(before,after),url=ART)


def test_wrong_route_and_duplicate_cards_rejected():
    with pytest.raises(ValueError):parse(fixture(),url='https://example.com')
    with pytest.raises(ValueError):parse(fixture('PRFL-220'),url=ART)
    html=fixture();card=html[html.index('<div class="courseblock">'):]
    with pytest.raises(ValueError):parse(html+card,url=ART)


def test_exact_manual_allocation_and_source_bound_provenance():
    c=MANIFEST['courses']
    expected_prfl='220 221 222 227 230 235 250 251 262 263 264 265 280 281 282 283 284 285 319 320 321 323 327 330 331 352 372 376 379 465'.split()
    expected_prfn='101 200 201 204 207 208 209 214 240 243 244 246 247 250 303 314 316 340 341 342 345 403'.split()
    assert set(c)=={'PRFL-'+x for x in expected_prfl}|{'PRFN-'+x for x in expected_prfn}
    assert len(SOURCES)==6 and sum(map(len,CODES_BY_URL.values()))==52
    assert all(x['description'] and x['category_review']['rationale'] and code in x['category_review']['locator'] for code,x in c.items())
    assert all(x['category_review']['source_ids']==[x['source_id']] for x in c.values())
    assert all(x['credit_unit']=='semester_hours' and x['credit_unit_source']=='https://www.rit.edu/policies/d014' for x in c.values())
    assert 'course_identity_groups' not in MANIFEST


def test_actual_variable_credits_are_not_route_totals_or_contact_hours():
    c=MANIFEST['courses']
    assert c['PRFL-220']['credits']==1
    assert all(c['PRFL-'+str(n)]['credits'] is None and c['PRFL-'+str(n)]['published_credit_text']=='(0-1 Credits)' for n in range(280,286))
    assert sum(x['credits']==3 for x in c.values())==45
    assert c['PRFN-246']['credits']==3 and any('Four lecture/lab' in n for n in c['PRFN-246']['notes'])
    assert all(c['PRFL-'+str(n)]['prerequisites'] for n in (280,281,282,284,285))
    assert c['PRFL-283']['prerequisites'] is None and any('regardless of musical proficiency' in n for n in c['PRFL-283']['notes'])


def test_language_writing_and_source_conditions_remain_distinct():
    c=MANIFEST['courses']
    assert c['PRFN-316']['category']=='human_context'
    assert c['PRFN-314']['category']=='human_context'
    assert 'minimum score of 3' in c['PRFN-214']['prerequisites']
    assert all(any('voice interpreters' in n for n in c[x]['notes']) for x in ('PRFN-214','PRFN-314'))
    assert c['PRFN-101']['prerequisites'].endswith('programs.')
    assert c['PRFL-265']['prerequisites']=='Elementary music reading ability.'
    assert any('not a displayed separately labeled' in n for n in c['PRFL-265']['notes'])
    assert c['PRFL-379']['category_review']['status']=='mixed'
    assert 'artificial intelligence' in ' '.join(c['PRFL-379']['notes'])
    assert c['PRFN-247']['category']=='applications'
    assert c['PRFN-341']['category']=='human_context'
