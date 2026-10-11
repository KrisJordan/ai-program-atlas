import hashlib
from pathlib import Path
import pytest
from atlas.adapters import ucsd_ethn_reviews as review


def policy_html():
    policy=review.SPEC['section_policies']['ETHN']
    return '<h2>Upper Division</h2><p>'+policy['text']+'</p>'


def membership_html(entry):
    if entry['region'] != 'Upper Division':
        return '<h2>'+entry['region']+'</h2>'
    if entry['section'] != 'Upper Division':
        return '<h3>'+entry['section']+'</h3>'
    return ''


def fixture(monkeypatch,code='ETHN 100C',body='Social-justice capstone. Prerequisites: ETHN 100A and ETHN 100B, ethnic studies major or minor, or consent of instructor.',unclassed=False):
    entry=dict(next(e for e in review.SPEC['entries']if e['code']==code))
    entry['description_hash']=hashlib.sha256(body.encode()).hexdigest()
    monkeypatch.setattr(review,'SPEC',{**review.SPEC,'entries':[entry]})
    tag='<p>'if unclassed else'<p class="course-descriptions">'
    return '<h1>Ethnic Studies</h1><p class="course-disclaimer">General Catalog 2026–27</p>'+policy_html()+membership_html(entry)+f'<p class="course-name">{entry["heading"]}</p>{tag}{body}</p>'


def test_literal_eligibility_grouping_and_no_scraper_certification(monkeypatch):
    out=review.parse_observations(fixture(monkeypatch));c=out['courses'][0]
    assert c['prerequisites']=='Section preparation rule: '+review.SPEC['section_policies']['ETHN']['text']+'\nCourse-specific prerequisite: ETHN 100A and ETHN 100B, ethnic studies major or minor, or consent of instructor.'
    assert not {'requirements','course_identity_groups','curriculum_audit'}&out.keys()
    assert 'category_review'not in c


def test_unclassed_110_description_is_read_and_changed_prose_is_guarded(monkeypatch):
    html=fixture(monkeypatch,'ETHN 110','Indigenous ways of understanding land and kinship.',unclassed=True)
    assert len(review.parse_observations(html)['courses'])==1
    with pytest.raises(ValueError,match='source changed'):
        review.parse_observations(html.replace('land and kinship','a different topic'))
    assert len(review.parse_observations(html.replace('<p>Indigenous','<p class="unreviewed">Indigenous'))['courses'])==1


def test_complete_unclassed_nested_and_unwrapped_text_is_guarded(monkeypatch):
    html=fixture(monkeypatch,body='Unexpected unclassed paragraph.',unclassed=True)
    assert len(review.parse_observations(html)['courses'])==1
    with pytest.raises(ValueError,match='source changed'):
        review.parse_observations(html+'<div>Unreviewed nested restriction.</div>')


def test_changed_prerequisite_edition_and_duplicate_are_rejected(monkeypatch):
    html=fixture(monkeypatch)
    with pytest.raises(ValueError,match='source changed'):review.parse_observations(html.replace('100A and','100A or'))
    with pytest.raises(ValueError,match='edition changed'):review.parse_observations(html.replace('2026–27','2027–28'))
    with pytest.raises(ValueError,match='Duplicate'):review.parse_observations(html+html[html.index('<p class="course-name">'):])


def test_missing_heading_appearance_requires_fresh_review(monkeypatch):
    entry=next(e for e in review.SPEC['entries']if e['code']=='ETHN 1A')
    monkeypatch.setattr(review,'SPEC',{**review.SPEC,'entries':[entry]})
    html='<h1>Ethnic Studies</h1><p class="course-disclaimer">General Catalog 2026–27</p>'+policy_html()
    assert review.parse_observations(html)['source_dispositions']==[dict(code='ETHN 1A',status='no_current_heading')]
    with pytest.raises(ValueError,match='identifier appeared'):
        review.parse_observations(html+'<p class="course-name">ETHN 1A. Newly published (4)</p>')


def test_content_classifications_and_credit_topic_limits():
    by={e['code']:e for e in review.SPEC['entries']}
    assert len(by)==95 and sum(e['approved_for_integration']for e in by.values())==88
    assert by['ETHN 101TV']['category']=='human_context'
    assert by['ETHN 136']['category_review']['status']=='mixed'
    assert by['ETHN 189']['category_review']['status']=='unclassified'
    assert any('Latin American' in n and 'does not establish' in n for n in by['ETHN 189']['notes'])
    assert any('eight units' in n for n in by['ETHN 179']['notes'])
    assert by['ETHN 179']['credits']==4
    assert by['ETHN 179']['category']=='human_context'
    assert by['ETHN 179']['category_review']['status']=='reviewed'
    assert 'does not teach performance' in by['ETHN 179']['category_review']['rationale']
    assert by['ETHN 140']['id']!=by['ETHN 140A']['id']
    assert any('identical' in n for n in by['ETHN 140']['notes'])


def test_actual_course_chapter_full_inventory_replay():
    path=Path(review.SPEC['sources']['ETHN']['cache_path'])
    if not path.exists():pytest.skip('Optional ignored current chapter absent')
    out=review.parse_observations(path.read_text());by={c['code']:c for c in out['courses']}
    assert len(by)==88 and by['ETHN 110']['description']
    assert by['ETHN 110']['prerequisites']=='Section preparation rule: '+review.SPEC['section_policies']['ETHN']['text']
    assert by['ETHN 114B']['prerequisites'].endswith('\nCourse-specific prerequisite: ETHN 114A.')
    assert 'or consent' in by['ETHN 135A']['prerequisites']
    assert {d['code']for d in out['source_dispositions']}=={'ETHN 107','ETHN 124','ETHN 154','ETHN 190','ETHN 1A','ETHN 1B','ETHN 1C'}


def test_published_duplicate_blocks_are_all_guarded_not_silently_overwritten():
    path=Path(review.SPEC['sources']['ETHN']['cache_path'])
    if not path.exists():pytest.skip('Optional ignored current chapter absent')
    html=path.read_text()
    assert len(review.SPEC['reviewed_duplicate_blocks']['ETHN 180'])==2
    with pytest.raises(ValueError,match='duplicate blocks changed'):
        review.parse_observations(html.replace('Topics in Mexican-American History','Unreviewed topic',1))
    with pytest.raises(ValueError,match='duplicate blocks changed'):
        review.parse_observations(html.replace('influenced the dialogue between ideas','changed the content between ideas',1))


def test_section_policy_change_and_missing_policy_fail_closed(monkeypatch):
    html=fixture(monkeypatch, 'ETHN 100C', 'Reviewed content.')
    policy=review.SPEC['section_policies']['ETHN']['text']
    with pytest.raises(ValueError,match='policy changed'):
        review.parse_observations(html.replace(policy,policy.replace(' or ',' and ')))
    with pytest.raises(ValueError,match='policy changed'):
        review.parse_observations(html.replace(policy,''))


def test_actual_membership_not_course_number_controls_policy(monkeypatch):
    html=fixture(monkeypatch, 'ETHN 100C', 'Reviewed content.')
    with pytest.raises(ValueError,match='section membership changed'):
        review.parse_observations(html.replace('<p class="course-name">','<h2>Lower Division</h2><p class="course-name">'))
    with pytest.raises(ValueError,match='section membership changed'):
        review.parse_observations(html.replace('<p class="course-name">','<h3>Other subsection</h3><p class="course-name">'))


def test_lower_division_never_inherits_upper_policy(monkeypatch):
    code='ETHN 100C'
    entry=dict(next(e for e in review.SPEC['entries'] if e['code']==code))
    entry['section']=entry['region']='Lower Division'
    monkeypatch.setattr(review,'SPEC',{**review.SPEC,'entries':[entry]})
    out=review.parse_observations(fixture(monkeypatch,code,'Reviewed lower-division content.'))
    assert out['courses'][0]['prerequisites'] is None


def test_held_identity_has_no_metadata_even_with_section_membership(monkeypatch):
    entry=dict(next(e for e in review.SPEC['entries'] if e['heading']))
    entry['approved_for_integration']=False
    monkeypatch.setattr(review,'SPEC',{**review.SPEC,'entries':[entry]})
    out=review.parse_observations(fixture(monkeypatch,entry['code'],'Reviewed conflicting current content.'))
    assert out['courses']==[]
    assert out['source_dispositions'][0]['status']=='source_title_conflict'


def test_first_duplicate_section_move_is_rejected():
    path=Path(review.SPEC['sources']['ETHN']['cache_path'])
    if not path.exists():pytest.skip('Optional ignored chapter absent')
    html=path.read_text()
    from bs4 import BeautifulSoup
    soup=BeautifulSoup(html,'html.parser')
    node=next(n for n in soup.select('p.course-name') if n.get_text(' ',strip=True).startswith('ETHN 180.'))
    moved=soup.new_tag('h3');moved.string='Unreviewed subsection';node.insert_before(moved)
    # Restore the original section immediately before the next course so only
    # the first duplicate occurrence changes its reviewed membership.
    next_node=node.find_next('p',class_='course-name')
    restored=soup.new_tag('h3');restored.string='Upper Division';next_node.insert_before(restored)
    with pytest.raises(ValueError,match='duplicate blocks changed'):
        review.parse_observations(str(soup))


def test_manifest_prerequisite_scopes_match_guarded_observations():
    subject=next(iter(review.SPEC['sources']))
    path=Path(review.SPEC['sources'][subject]['cache_path'])
    if not path.exists():pytest.skip('Optional ignored chapter absent')
    by={e['code']:e for e in review.SPEC['entries']}
    for course in review.parse_observations(path.read_text())['courses']:
        assert course['prerequisites']==by[course['code']]['observed_prerequisites']
