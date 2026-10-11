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
