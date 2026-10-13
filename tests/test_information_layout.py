from copy import deepcopy
from bs4 import BeautifulSoup
from atlas.site import build, program_page, required_directory_counts, requirement_tree
from tests.test_site import site_data  # noqa: F401


def test_detail_section_order_and_requirement_disclosure(site_data):
    p = deepcopy(site_data['programs'][0])
    p['requirements'] = [dict(id=f'r-{n}',parent_id=f'r-{n-1}' if n else None,title=f'Group {n}',kind='all',course_ids=[p['courses'][0]['id']] if n==3 else [],summary='A rule') for n in range(4)]
    soup=BeautifulSoup(program_page(p,'/nested/atlas/'),'html.parser')
    ids=[node.get('id') for node in soup.select('main > section[id]')]
    assert ids.index('outcomes') < ids.index('requirements') < ids.index('curriculum') < ids.index('sources') < ids.index('evidence-context')
    assert soup.select_one('.cohort-context').find_previous_sibling('section')['id']=='courses'
    assert soup.select_one('.cohort-context').find_next_sibling('section')['id']=='sources'
    assert soup.select_one('#evidence-context .evidence-notice')
    assert soup.select_one('#evidence-context .degree-audit-program')
    for n in range(4):
        node=soup.select_one(f'#requirement-r-{n} > details')
        assert node.has_attr('open') == (n < 2)
        assert node.select_one('summary .requirement-title').get_text().startswith(f'Group {n}')
    assert soup.select_one('#requirement-r-3 .requirement-course-name').get_text().startswith(p['courses'][0]['code'])
    assert not soup.select('.requirement-preview')


def test_counts_match_fixed_profile_without_elective_pool_inflation(site_data):
    p=deepcopy(site_data['programs'][0]);course=p['courses'][0];course['category']='foundations';p['courses']=[course,deepcopy(course)]
    other=deepcopy(course);other.update(id='choice-course',code='AI 201',category='ai_ml');p['courses'].append(other)
    p['requirements']=[dict(id='fixed',parent_id=None,kind='all',course_ids=[course['id']]),dict(id='choice',parent_id=None,kind='choose_courses',count=1,course_ids=[other['id']])]
    assert required_directory_counts(p)==dict(mathematics=0,computing_systems=1,ai_ml=1,human_context=0,applications=0,other=0)
    p['courses']=[];assert required_directory_counts(p) is None


def test_table_grouped_headers_and_award_prefix(site_data,tmp_path):
    build(site_data,tmp_path)
    soup=BeautifulSoup((tmp_path/'index.html').read_text(),'html.parser')
    table=soup.select_one('#cohort-nu-majors .directory-table')
    assert table.select_one('thead th[colspan="6"]').get_text()=='Required Curriculum (Electives Counted Separately)'
    assert [node.get_text() for node in table.select('thead tr:nth-child(2) th')]==['Math + Statistics','Computing + Systems','AI + ML','Human Context','Applications','Other']
    row=table.select_one('tbody tr')
    assert row.select_one('td:first-child [data-row-compare]')
    assert '(BS)' in row.select_one('.directory-program-link').get_text()
    assert not row.select('td:nth-child(4) small,td:nth-child(5) small')
    additional=soup.select_one('[data-row-id=test-ai-2] .directory-program-link')
    assert '(2ndMaj)' in additional.get_text()


def test_concentration_parent_line_and_minor_award_prefixes(site_data,tmp_path):
    p=site_data['programs'][3]
    p['parent_programs']=[dict(title='Business Administration',award_level='B.S.'),dict(title='Computer Science',award_level='BA')]
    build(site_data,tmp_path)
    soup=BeautifulSoup((tmp_path/'index.html').read_text(),'html.parser')
    row=soup.select_one('[data-row-id=test-ai-3]')
    assert row.select_one('.directory-parent em').get_text()=='Parent: BS Business Administration; BA Computer Science'
    assert not row.select_one('.directory-award')
    assert not soup.select_one('[data-row-id=test-ai-1] .directory-award')
    p['parent_programs']=[]
    build(site_data,tmp_path)
    assert 'Parent: Not yet verified' in (tmp_path/'index.html').read_text()
    minor=BeautifulSoup((tmp_path/'programs/test-ai-1/index.html').read_text(),'html.parser')
    assert [n.get_text() for n in minor.select('.detail-badges .badge')]==['Minor','Active']


def test_combined_computing_display_preserves_deduplication_and_choice_load(site_data):
    from atlas.curriculum_profile import requirement_profile
    p=deepcopy(site_data['programs'][0]);template=p['courses'][0]
    p['courses']=[dict(template,id='compute',category='foundations'),
                  dict(template,id='compute',category='foundations'),
                  dict(template,id='system',category='systems')]
    p['courses'] += [dict(template,id=f'option-{n}',category='systems') for n in range(3)]
    p['requirements']=[dict(id='fixed-a',kind='all',course_ids=['compute','system']),
                       dict(id='fixed-b',kind='all',course_ids=['system']),
                       dict(id='choice',kind='choose_courses',count=1,course_ids=[f'option-{n}' for n in range(3)])]
    before=deepcopy(p)
    canonical=requirement_profile(p)
    assert canonical['required']['categories']['foundations']==1
    assert canonical['required']['categories']['systems']==1
    assert canonical['options']['categories']['systems']==3
    assert required_directory_counts(p)['computing_systems']==3  # two fixed plus one mandatory selection
    assert sum(required_directory_counts(p).values())==canonical['required_obligations']['count']
    assert 'computing_systems' not in canonical['required']['categories']
    assert p==before


def test_joint_range_uses_each_program_sum_not_sum_of_category_extremes(site_data):
    from atlas.site import program_table
    members=[]
    for n in range(2):
        p=deepcopy(site_data['programs'][0]);p['id']=f'joint-{n}'
        p['family']={'id':'northeastern-ai-combined-degrees'}
        category='foundations' if n==0 else 'systems'
        p['courses']=[dict(p['courses'][0],id=f'course-{n}-{i}',category=category) for i in range(2)]
        p['requirements']=[dict(id='fixed',kind='all',course_ids=[c['id'] for c in p['courses']])]
        members.append(p)
    table=BeautifulSoup(program_table(members,'/nested/atlas/'),'html.parser')
    assert table.select_one('[data-joint-count=computing_systems]').get_text()=='2'
    assert [td.get_text() for td in table.select('[data-required-category=computing_systems]')]==['2','2']
    assert not table.select('[data-required-category=foundations],[data-required-category=systems]')
    assert len(table.select('colgroup col'))==11
