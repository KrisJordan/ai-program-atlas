"""Synthetic source observations, not a substitute for the manual public-card reads."""
import pytest
from atlas.adapters.rit_final_interdisciplinary_course_reviews import MANIFEST, parse

def fixture(label='DHSS/ITDL-500',code='DHSS-500',amount='(3 Credits)',body='Synthetic current description.'):
    c=MANIFEST['courses'][label];s=next(s for s in MANIFEST['sources'] if s['url']==c['url'])
    return f'<main><h1>{s["page_title"]}</h1><h2>Curriculum for 2026-2027 for {s["page_title"]}</h2><table class="sc_courselist"><tbody><tr><td><a class="code_bubble">{label}</a></td><td>Title</td><td>9</td></tr></tbody></table></main><div class="courseblock"><span class="detail-code">{code}</span><span class="detail-title">Changed source title</span><span class="detail-hours_html">{amount}</span><div class="courseblockextra">{body}</div></div>',c['url']

def test_combined_label_binds_actual_card_without_inventing_aliases():
    h,u=fixture();o=parse(h,url=u)
    assert [c['code'] for c in o['courses']]==['DHSS-500']
    assert o['observed_course_label_associations'][0]['source_label']=='DHSS/ITDL-500'
    assert o['courses'][0]['name']=='Changed source title'
    assert o['courses'][0]['description']=='Synthetic current description.'
    assert o['courses'][0]['credit_unit']=='unknown'
    assert o['requirements']==[] and 'course_identity_groups' not in o
    assert 'category_review' not in o['courses'][0] and 'curriculum_audit' not in o

@pytest.mark.parametrize('before,after',[
 ('2026-2027','2025-2026'),('class="detail-code">DHSS-500','class="detail-code">ITDL-500'),
 ('class="code_bubble">DHSS/ITDL-500','class="code_bubble">DHSS-500'),
 ('class="courseblockextra"','class="loading"'),('(3 Credits)','(3-1 Credits)')])
def test_rejects_wrong_source_binding_version_and_unsettled_content(before,after):
    h,u=fixture()
    with pytest.raises(ValueError):parse(h.replace(before,after),url=u)

def test_credit_range_and_body_permission_are_observed_separately():
    h,u=fixture('ITDL-511','ITDL-511','(1-3 Credits)','Synthetic project. Registration by permission of instructor.')
    c=parse(h,url=u)['courses'][0]
    assert c['credits'] is None and c['prerequisites']=='Registration by permission of instructor.'
    h,u=fixture('ISCH-201','ISCH-201',body='Computing majors may take this course only with department approval.')
    assert 'degree requirements' not in parse(h,url=u)['courses'][0]['prerequisites']

def test_manual_review_preserves_scope_and_credit_use_boundaries():
    c=MANIFEST['courses'];assert len(c)==19
    assert c['ISCH-370']['category_review']['status']=='mixed'
    assert 'No GCCIS students' in c['ISCH-370']['prerequisites']
    assert 'Computer Science majors' in c['ISCH-110']['prerequisites']
    assert 'GCCIS' not in c['ISCH-110']['prerequisites']
    assert 'GIS-IM students' in c['IGME-489']['prerequisites']
    assert c['IGME-489']['category']=='ai_ml' and c['IGME-386']['category']=='foundations'
    assert c['DHSS-488']['category_review']['status']=='unclassified'
    assert 'Topic ID #4' in c['DHSS-488']['notes'][0]
    assert c['ITDL-151H']['prerequisites']=='This class is restricted to students in the Honors program.'
    assert c['ITDL-211']['credits'] is c['ITDL-511']['credits'] is None
    assert all(c[x]['category']=='human_context' for x in ['DHSS-377','DHSS/ITDL-500','PRFL/WGST-330','UWRT-365'])
