from copy import deepcopy
from bs4 import BeautifulSoup
from atlas.site import build, program_page, required_directory_counts, requirement_tree
from tests.test_site import site_data  # noqa: F401


def test_detail_section_order_and_requirement_disclosure(site_data):
    p = deepcopy(site_data['programs'][0])
    p['requirements'] = [dict(id=f'r-{n}',parent_id=f'r-{n-1}' if n else None,title=f'Group {n}',kind='all',course_ids=[],summary='A rule') for n in range(4)]
    soup=BeautifulSoup(program_page(p,'/nested/atlas/'),'html.parser')
    ids=[node.get('id') for node in soup.select('main > section[id]')]
    assert ids.index('outcomes') < ids.index('curriculum') < ids.index('requirements') < ids.index('sources') < ids.index('evidence-context')
    assert soup.select_one('.cohort-context').find_previous_sibling('section')['id']=='curriculum'
    assert soup.select_one('#evidence-context .evidence-notice')
    assert soup.select_one('#evidence-context .degree-audit-program')
    for n in range(4):
        node=soup.select_one(f'#requirement-r-{n} > details')
        assert node.has_attr('open') == (n<2)
        assert node.select_one('summary .requirement-title').get_text()==f'Group {n}'
    assert 'Group 3' in soup.select_one('#requirement-r-2 > details > summary .requirement-preview').get_text()


def test_counts_match_fixed_profile_without_elective_pool_inflation(site_data):
    p=deepcopy(site_data['programs'][0]);course=p['courses'][0];course['category']='foundations';p['courses']=[course,deepcopy(course)]
    other=deepcopy(course);other.update(id='choice-course',code='AI 201',category='ai_ml');p['courses'].append(other)
    p['requirements']=[dict(id='fixed',parent_id=None,kind='all',course_ids=[course['id']]),dict(id='choice',parent_id=None,kind='choose_courses',count=1,course_ids=[other['id']])]
    assert required_directory_counts(p)==dict(foundations=1,mathematics=0,ai_ml=1,systems=0,human_context=0,applications=0,other=0)
    p['courses']=[];assert required_directory_counts(p) is None


def test_table_grouped_headers_and_award_prefix(site_data,tmp_path):
    build(site_data,tmp_path)
    soup=BeautifulSoup((tmp_path/'index.html').read_text(),'html.parser')
    table=soup.select_one('#cohort-nu-majors .directory-table')
    assert table.select_one('thead th[colspan="7"]').get_text()=='Required Curriculum'
    assert [node.get_text() for node in table.select('thead tr:nth-child(2) th')]==['Computing','Math','AIML','Systems','Human Context','Applications','Other']
    row=table.select_one('tbody tr')
    assert row.select_one('td:first-child [data-row-compare]')
    assert '(BS)' in row.select_one('.directory-program-link').get_text()
    assert not row.select('td:nth-child(4) small,td:nth-child(5) small')
    additional=soup.select_one('[data-row-id=test-ai-2] .directory-program-link')
    assert '(2ndMaj)' in additional.get_text()
