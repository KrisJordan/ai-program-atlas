import pytest
from atlas.adapters.rit_visual_museum_imaging_course_reviews import parse, SOURCES, TITLES, LABELS_BY_URL, MANIFEST


def fixture(label='MUSE/HIST-221', popup='MUSE-221', url=SOURCES[1], amount='3', prereq='', description='Synthetic changed public-history description.'):
    return f'''<main><h1>{TITLES[url]}</h1><h2>Curriculum for 2026-2027 for {TITLES[url]}</h2>
    <table class="sc_courselist"><tbody><tr><td><a class="code_bubble">{label}</a></td><td>Route amount9</td><td>9</td></tr></tbody></table></main>
    <div class="courseblock"><span class="detail-code">{popup}</span><span class="detail-title">Synthetic current title</span>
    <span class="detail-hours_html">({amount} Credits)</span><div class="courseblockextra">{description}</div>
    <span class="detail-requisites">{prereq}</span></div>'''


def test_literal_combined_label_maps_only_to_observed_heading():
    out=parse(fixture(),url=SOURCES[1])
    assert len(out['courses'])==1 and out['courses'][0]['code']=='MUSE-221'
    assert out['observed_course_label_associations']==[{'source_label':'MUSE/HIST-221','popup_code':'MUSE-221','source_id':MANIFEST['sources'][1]['id']}]
    assert out['requirements']==[] and 'course_identity_groups' not in out
    with pytest.raises(ValueError):parse(fixture(popup='HIST-221'),url=SOURCES[1])
    with pytest.raises(ValueError):parse(fixture(label='MUSE-221'),url=SOURCES[1])


def test_changed_current_fields_and_ranges_do_not_replay_manual_review():
    out=parse(fixture(label='MUSE-249',popup='MUSE-249',amount='1-3',prereq='Chair permission required.'),url=SOURCES[1])
    c=out['courses'][0]
    assert c['credits'] is None and c['credit_unit']=='unknown'
    assert c['name']=='Synthetic current title' and c['description']=='Synthetic changed public-history description.'
    assert c['prerequisites']=='Chair permission required.'
    assert c['category']=='other' and 'category_review' not in c
    assert any('(1-3 Credits)' in n for n in c['notes'])
    assert parse(fixture(amount='4'),url=SOURCES[1])['courses'][0]['credits']==4
    assert parse(fixture(amount='0'),url=SOURCES[1])['courses'][0]['credits']==0


def test_explicit_body_no_prerequisite_differs_from_absent_field():
    desc='Current museum description. The course has no pre-requisite and is open to students of all majors.'
    c=parse(fixture(label='MUSE-225',popup='MUSE-225',description=desc),url=SOURCES[1])['courses'][0]
    assert c['prerequisites']=='The course has no pre-requisite and is open to students of all majors.'
    changed=parse(fixture(label='MUSE-225',popup='MUSE-225',description='Current changed course scope.'),url=SOURCES[1])['courses'][0]
    assert changed['prerequisites'] is None
    assert any('does not establish unrestricted' in n for n in changed['notes'])


@pytest.mark.parametrize('before,after',[
    ('2026-2027','2025-2026'),
    ('<h1>Museum Studies Immersion</h1>','<h1>Other Immersion</h1>'),
    ('class="courseblockextra"','class="missing"'),
    ('class="sc_courselist"','class="shell"'),
    ('(3 Credits)','(3 Contact Hours)'),
])
def test_source_guards_reject_wrong_or_incomplete_sources(before,after):
    with pytest.raises(ValueError):parse(fixture().replace(before,after),url=SOURCES[1])


def test_wrong_url_duplicate_and_unverified_combined_heading_rejected():
    with pytest.raises(ValueError):parse(fixture(),url='https://example.com')
    h=fixture();card=h[h.index('<div class="courseblock">'):]
    with pytest.raises(ValueError):parse(h+card,url=SOURCES[1])
    with pytest.raises(ValueError):parse(fixture(label='MUSE/VISL-388',popup='VISL-388'),url=SOURCES[1])


def test_exact38_labels_37_popup_codes_credit_and_condition_facts():
    c=MANIFEST['courses']
    assert len(c)==38 and len({v['popup_code'] for v in c.values()})==37
    assert {label:v['popup_code'] for label,v in c.items() if '/' in label}=={
        'MUSE/HIST-221':'MUSE-221','MUSE/VISL-388':'MUSE-388','COMM/VISL-390':'COMM-390'}
    assert c['IMGS-261']['credits']==c['IMGS-351']['credits']==4
    assert c['MUSE-249']['credits'] is None and c['MUSE-249']['published_credit_text']=='(1-3 Credits)'
    assert sum(v['credits']==3 for v in c.values())==35
    assert 'Co-requisite:' in c['SOFA-103']['prerequisites']
    assert 'SCIMGS-IM' in c['IMGS-221']['prerequisites']
    assert c['IMGS-111']['prerequisites'] is None
    assert c['MUSE-225']['prerequisites'].startswith('The course has no pre-requisite')
    assert c['MUSE-360']['prerequisites'].startswith('The course has no prerequisite')
    assert 'VISL-234' not in c
    assert all(v['category_review']['source_ids']==[v['source_id']] for v in c.values())


def test_individual_art_history_math_and_production_classifications():
    c=MANIFEST['courses']
    assert all(c[x]['category']=='human_context' for x in ('MUSE-224','MUSE-388','VISL-384','VISL-388'))
    assert c['IMGS-261']['category']=='mathematics'
    assert all(c[x]['category']=='applications' for x in ('SOFA-103','IMGS-111','IMGS-221','IMGS-321','IMGS-341','IMGS-351'))
    assert c['VISL-440']['category_review']['status']=='mixed'
    assert c['MUSE-249']['category_review']['status']=='unclassified'
    assert 'course_identity_groups' not in MANIFEST
