import json
from pathlib import Path
import pytest
from atlas.adapters.rit_gender_sts_course_reviews import parse,SPECS,MANIFEST
URL='https://www.rit.edu/study/science-technology-and-society-immersion'


def fixture(code='STSO-489',amount='1-6',name='Topics in Science, Technology, &amp; Society'):
    title=SPECS[URL][0]
    return f'<main><h1>{title}</h1><h2>Curriculum for 2026-2027 for {title}</h2><table class="sc_courselist"><tbody><tr><td><a class="code_bubble">{code}</a></td><td></td><td></td></tr></tbody></table></main><div class="courseblock"><span class="detail-code">{code}</span><span class="detail-title">{name}</span><span class="detail-hours_html">({amount} Credits)</span><div class="courseblockextra">Variable topic. Department permission is required for immersion use.</div><span class="detail-contact_hours">Lecture 3</span><span class="detail-requisites">Two previous courses or permission.</span></div>'


def test_range_is_not_replaced_by_three_contact_hours_or_table_load():
    out=parse(fixture(),url=URL);c=out['courses'][0]
    assert c['credits'] is None and c['credit_unit']=='unknown'
    assert '1-6' in c['notes'][0]
    assert c['prerequisites']=='Two previous courses or permission.'
    assert c['category']=='other' and 'category_review'not in c
    assert not {'curriculum_audit','course_identity_groups'}&out.keys()
    assert parse(fixture(amount='3'),url=URL)['courses'][0]['credits']==3


def test_blank_table_title_can_be_resolved_only_by_actual_card():
    html=fixture(code='WGST-380',amount='3',name='Gender and Political Thought')
    assert parse(html,url=URL)['courses'][0]['name']=='Gender and Political Thought'
    with pytest.raises(ValueError,match='Unbound'):parse(html.replace('class="detail-title"','class="missing-title"'),url=URL)


@pytest.mark.parametrize('before,after',[('2026-2027','2025-2026'),('class="courseblockextra"','class="missing-description"'),('class="detail-code">STSO-489','class="detail-code">STSO-999'),('(1-6 Credits)','(unknown Credits)')])
def test_rejects_stale_missing_unbound_and_unknown_amounts(before,after):
    with pytest.raises(ValueError):parse(fixture().replace(before,after),url=URL)


def test_actual_new_text_is_observed_not_curated_seed_replayed():
    changed=fixture().replace('Variable topic.','Newly revised actual topic.')
    assert parse(changed,url=URL)['courses'][0]['description'].startswith('Newly revised')
    with pytest.raises(ValueError,match='Duplicate'):parse(fixture()+fixture(),url=URL)


def test_all_57_read_cards_keep_content_and_eligibility_distinctions():
    c=MANIFEST['courses'];assert len(c)==57
    assert sum(v['credits']==3 for v in c.values())==55
    assert {k for k,v in c.items()if v['credits']is None}=={'STSO-488','STSO-489'}
    assert c['WGST-282']['category']=='human_context'
    assert c['WGST-392']['category']=='applications'
    assert c['WGST-295']['category_review']['status']=='mixed'
    assert c['STSO-230']['category_review']['status']=='mixed'
    assert c['WGST-399']['category_review']['status']=='unclassified'
    assert c['WGST-380']['name']=='Gender and Political Thought'
    assert 'at least 2nd year' in c['WGST-370']['prerequisites']
    assert 'Completion of any 2' in c['STSO-510']['prerequisites']
    assert any('Enrollment in an STS' in n for n in c['STSO-510']['notes'])
    assert any('permission' in n for n in c['STSO-488']['notes'])
    assert c['WGST-200']['prerequisites'] is None
    assert all('/' not in code for code in c)  # No split/merged source aliases.
