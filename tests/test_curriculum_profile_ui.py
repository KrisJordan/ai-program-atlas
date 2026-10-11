"""Profile presentation preserves resolved requirement semantics and units."""
from copy import deepcopy
import json
from bs4 import BeautifulSoup
from atlas.site import build, directory_payload
from tests.test_site import site_data  # noqa: F401


def profile_fixture(data):
    program=data['programs'][0]
    base=program['courses'][0]
    program['courses']=[dict(base,id='required-ai',code='AI 101',category='ai_ml'),
        dict(base,id='required-other',code='CORE 102',category='other'),
        dict(base,id='math-a',code='MATH 201',category='mathematics'),
        dict(base,id='math-b',code='MATH 202',category='mathematics'),
        dict(base,id='unresolved',code='TOPIC 999',category='human_context')]
    program['courses'] += [dict(base,id='system-'+str(i),code='SYS '+str(300+i),category='systems') for i in range(12)]
    def rule(id,kind,ids,**extra):
        return dict(id=id,parent_id=None,title=id.replace('-',' ').capitalize(),kind=kind,course_ids=ids,source_id='outcome-source',**extra)
    program['requirements']=[
        rule('shared-required','all',['required-ai'],origin='family'),
        rule('local-required','all',['required-other'],origin='variant'),
        rule('math-choice','choose_courses',['math-a','math-b'],count=1,summary='Choose one mathematics course.'),
        rule('systems-credit-choice','choose_credits',['required-ai']+['system-'+str(i) for i in range(12)],credits=6,credit_unit='quarter_hours',summary='Select six quarter hours from the documented pool.'),
        rule('unresolved-note','note',['unresolved'],summary='Topic eligibility needs separate review.')]
    return data


def test_detail_required_default_and_choice_evidence(site_data,tmp_path):
    profile_fixture(site_data)
    build(site_data,tmp_path)
    page=BeautifulSoup((tmp_path/'programs/test-ai-0/index.html').read_text(),'html.parser')
    profile=page.find(class_='curriculum-profile')
    assert profile.find('input',value='required').has_attr('checked')
    assert not profile.find('input',value='options').has_attr('checked')
    required=profile.find(attrs={'data-profile':'required'})
    options=profile.find(attrs={'data-profile':'options'})
    assert '2 distinct fixed required course records' in required.get_text(' ',strip=True)
    assert '14 distinct elective option records' in options.get_text(' ',strip=True)
    assert 'Other / unclassified' in required.get_text()
    assert '1 course record' in profile.find(class_='profile-uncertainty').get_text()
    choices=profile.find(class_='profile-choices')
    assert '1 course' in choices.get_text()
    assert '6 Quarter hours' in choices.get_text()
    assert choices.find('a',href='https://example.edu/outcome')
    assert 'not credit totals' in profile.get_text()


def test_projection_preserves_aggregate_profile_and_full_export(site_data,tmp_path):
    profile_fixture(site_data)
    original=deepcopy(site_data)
    view=directory_payload(site_data,'/nested/atlas/')
    assert site_data==original
    assert 'curriculum_profile' in view['programs'][0]
    assert 'outcome-source' in [s['id'] for s in view['programs'][0]['sources']]
    build(site_data,tmp_path,'/nested/atlas/')
    assert json.loads((tmp_path/'data.json').read_text())==original


def test_selection_labels_preserve_both_count_and_credits():
    from atlas.site import profile_selection
    assert profile_selection(dict(kind='alternative',count=None,credits=12,credit_unit='units')) == 'Choose an alternative · 12 Units recorded'
    assert profile_selection(dict(kind='choose_courses',count=2,credits=6,credit_unit='semester_hours')) == 'Choose 2 courses · 6 Semester hours recorded'


def test_zero_category_is_mapping_absence_and_complete_inventory_is_not_taxonomy_review(site_data,tmp_path):
    profile_fixture(site_data)
    program=site_data['programs'][0]
    program['curriculum_status']='complete'
    build(site_data,tmp_path)
    page=BeautifulSoup((tmp_path/'programs/test-ai-0/index.html').read_text(),'html.parser')
    profile=page.find(class_='curriculum-profile')
    required=profile.find(attrs={'data-profile':'required'})
    assert required.find(attrs={'data-category':'foundations'}).find('strong').get_text()=='0 mapped'
    assert 'not evidence that the curriculum lacks that subject' in profile.get_text()
    assert '2 unreviewed, of 2 mapped identities' in required.find(class_='profile-taxonomy').get_text()
    assert 'Requirement inventory completeness is separate' in profile.get_text()
    assert 'Legacy / unreviewed classification' in page.find(class_='course-table').get_text()


def test_reviewed_mixed_and_unclassified_course_evidence_is_explicit(site_data,tmp_path):
    profile_fixture(site_data)
    program=site_data['programs'][0]
    program['courses'][0]['category_review']=dict(status='reviewed',taxonomy_version='1',reviewed_at='2026-10-11',source_ids=['outcome-source'],locator='AI 101 official description',rationale='Specific AI methods description.',candidate_categories=[])
    program['courses'][1]['category_review']=dict(status='mixed',taxonomy_version='1',reviewed_at='2026-10-11',source_ids=['outcome-source'],locator='CORE 102 official description',rationale='Combined computing and mathematical methods with no primary focus.',candidate_categories=['foundations','mathematics'])
    build(site_data,tmp_path)
    page=BeautifulSoup((tmp_path/'programs/test-ai-0/index.html').read_text(),'html.parser')
    row=page.find(id='course-required-other').find_parent('tr')
    assert 'Mixed subject matter' in row.get_text()
    assert 'Candidate subjects: Computing foundations, Mathematics' in row.get_text()
    assert row.find(class_='category-review').find('a')['href']=='https://example.edu/outcome'


def test_degree_correctness_audit_is_separate_from_inventory_status(site_data,tmp_path):
    site_data['meta']['degree_audit']=dict(scope_programs=63,audited=0,blocked=0,in_progress=2,pending=61,second_pass_verified=0,audit_date='2026-10-11')
    site_data['programs'][0]['degree_audit']=dict(status='in_progress',second_pass_status='partial')
    build(site_data,tmp_path)
    for name in ['coverage','methodology']:
        page=BeautifulSoup((tmp_path/name/'index.html').read_text(),'html.parser')
        audit=page.find(class_='degree-audit-summary')
        assert '63 standalone degree records' in audit.get_text()
        assert 'do not certify this separate correctness review' in audit.get_text()
        assert 'Independent second pass verified' in audit.get_text()
    detail=BeautifulSoup((tmp_path/'programs/test-ai-0/index.html').read_text(),'html.parser')
    assert 'Whole-degree correctness audit: In progress' in detail.find(class_='degree-audit-program').get_text()
    assert detail.find(class_='degree-audit-program').get_text().count('Not independently reviewed') == 3


def test_identity_note_appears_only_for_documented_aliases():
    from atlas.site import profile_identity_note
    group={'count':2,'source_record_count':3}
    assert profile_identity_note({},group)==''
    assert profile_identity_note({'identity':{'crosslisted_aliases':0}},group)==''
    note=profile_identity_note({'identity':{'crosslisted_aliases':1}},group)
    assert '2 mapped course identities from 3 retained source-code records' in note
    assert 'Only explicitly verified cross-lists' in note


def test_real_penn_state_aliases_keep_codes_and_source_evidence(site_data,tmp_path):
    from pathlib import Path
    pid='penn-state-ai-methods-applications-ist-bs'
    program=json.loads((Path(__file__).resolve().parents[1]/'data/programs'/f'{pid}.json').read_text())
    site_data['programs']=[program]
    site_data['institutions']=[program['institution']]
    build(site_data,tmp_path)
    soup=BeautifulSoup((tmp_path/'programs'/pid/'index.html').read_text(),'html.parser')
    note=soup.select_one('[data-profile=options] .profile-identity').get_text()
    assert '156 mapped course identities from 160 retained source-code records' in note
    evidence=soup.select_one('.profile-identities')
    assert 'DS 410 / CMPSC 410' in evidence.get_text()
    assert 'MATH 318 / STAT 318' in evidence.get_text()
    assert evidence.find('a',href='https://bulletins.psu.edu/university-course-descriptions/undergraduate/ds/')
    assert 'IST 301 / ETI 301' not in evidence.get_text()
