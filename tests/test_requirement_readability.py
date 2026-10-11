from copy import deepcopy
from bs4 import BeautifulSoup
from atlas.site import requirement_tree, program_page, build
from atlas.course_references import reference_matcher, referenced_courses
from tests.test_site import site_data  # noqa: F401


def rule(rid,kind='all',parent=None,courses=(),title=None):
    return dict(id=rid,kind=kind,parent_id=parent,course_ids=list(courses),title=title or rid,summary='Exact recorded rule',source_id='source')


def test_all_course_titles_and_note_grouping_preserve_graph(site_data):
    p=site_data['programs'][0]
    p['courses']=[dict(id=f'c{i}',code=f'CS {100+i}',name=f'Course title {i}') for i in range(6)]
    p['requirements']=[rule('policy',kind='note'),rule('empty-container',title='Enrollment policies'),rule('main',title='Main curriculum'),rule('list',parent='main',courses=[f'c{i}' for i in range(6)]),rule('nested-note',kind='note',parent='main'),rule('context',kind='note'),rule('context-courses',parent='context',courses=['c0']),rule('optional',kind='note',title='Optional HASS field: Music'),rule('optional-course',parent='optional',courses=['c1'])]
    original=deepcopy(p)
    soup=BeautifulSoup(requirement_tree(p),'html.parser')
    assert p==original
    header=soup.select_one('#requirement-list > details > summary')
    assert not header.select('.requirement-preview')
    assert all(f'CS {100+i} · Course title {i}' in header.select_one('h3').get_text() for i in range(6))
    assert header.select_one('.requirement-rule').get_text()=='Complete all courses in this group'
    assert soup.select_one('.requirements > li')['id']=='requirement-main'
    for key in ['other-top','optional-top','notes-main']:
        assert not soup.select_one('#requirements-group-'+key+' > details').has_attr('open')
    assert soup.select_one('#requirements-group-other-top #requirement-policy')
    assert soup.select_one('#requirements-group-other-top #requirement-empty-container')
    assert soup.select_one('.requirements > #requirement-context #requirement-context-courses')
    assert not soup.select_one('#requirement-context > details').has_attr('open')
    assert not soup.select_one('#requirements-group-notes-top')
    assert soup.select_one('#requirements-group-optional-top #requirement-optional-course')
    assert not soup.select_one('#requirement-optional > details').has_attr('open')
    assert [n['id'] for n in soup.select('.requirement')].count('requirement-list')==1
    assert len(soup.select('.requirement'))==len(p['requirements'])


def test_choice_preview_is_bounded_but_empty_course_choices_stay_visible(site_data):
    p=site_data['programs'][0];p['courses']=[dict(id=f'c{i}',code=f'CS {i}',name=f'Topic {i}') for i in range(6)]
    p['requirements']=[dict(rule('choice','choose_courses',courses=[f'c{i}' for i in range(6)]),count=1),dict(rule('unextracted','choose_credits'),credits=6)]
    soup=BeautifulSoup(requirement_tree(p),'html.parser')
    assert len(soup.select('#requirement-choice .requirement-preview-item'))==4
    assert '+2 more' in soup.select_one('#requirement-choice .requirement-preview').get_text()
    assert soup.select_one('.requirements > #requirement-unextracted')
    assert not soup.select_one('#requirements-group-other-top')


def test_reference_titles_preserve_exact_prose_and_match_codes_without_prefix_guesses(site_data):
    p=site_data['programs'][0]
    p['courses']=[dict(id='python',code='6.100A',name='Python programming'),dict(id='joint',code='16.C20[J]',name='Computational science'),dict(id='data',code='CMSC 131',name='Data structures'),dict(id='target',code='CS 300',name='Target',prerequisites='6.100A or (16.C20 and CMSC131); CMSC1310 is not the same code.')]
    names=referenced_courses(p['courses'][-1]['prerequisites'],reference_matcher(p))
    assert [c['id'] for c in names]==['python','joint','data']
    soup=BeautifulSoup(program_page(p,'/nested/atlas/'),'html.parser')
    cell=soup.select_one('#course-target').find_next_sibling('td').find_next_sibling('td').find_next_sibling('td')
    assert cell.select_one('.prerequisite-text').get_text()==p['courses'][-1]['prerequisites']
    assert cell.select_one('.prerequisite-titles a')['href']=='#course-python'
    assert 'Python programming' in cell.get_text()


def test_titles_from_other_programs_are_institution_scoped_and_ambiguity_is_omitted(site_data,tmp_path):
    p,provider,outsider=site_data['programs'][:3]
    provider['institution']=deepcopy(p['institution'])
    provider['courses']=[dict(id='math',code='MATH 100',name='Calculus')]
    outsider['courses']=[dict(id='outside',code='MATH 100',name='Unrelated institution title')]
    p['courses']=p['courses'][:1]
    p['courses'][0]['prerequisites']='MATH100 or MATH1000'
    build(site_data,tmp_path,'/nested/atlas/')
    soup=BeautifulSoup((tmp_path/'programs/test-ai-0/index.html').read_text(),'html.parser')
    assert soup.select_one('.prerequisite-titles a')['href']=='/nested/atlas/programs/test-ai-1/#course-math'
    assert 'Calculus' in soup.select_one('.prerequisite-titles').get_text()
    assert 'Unrelated institution title' not in soup.get_text()
    provider['courses'].append(dict(id='ambiguous',code='MATH100',name='Different exact title'))
    assert referenced_courses('MATH100',reference_matcher(p,[provider]))==[]


def test_real_mit_course_contexts_and_general_education_preserve_source_graph():
    import json
    from pathlib import Path
    p=json.loads((Path(__file__).resolve().parents[1]/'data/programs/mit-ai-decision-making-bs.json').read_text())
    before=deepcopy(p);soup=BeautifulSoup(requirement_tree(p),'html.parser')
    assert p==before
    assert soup.select_one('.requirements > .requirement')['id']=='requirement-mit-ai-version-required'
    for focus in ['data-centric','model-centric','decision-centric','computation-centric','human-centric']:
        node=soup.select_one('#requirement-mit-ai-v2025-overlay-'+focus)
        assert node.select_one(':scope > details').has_attr('open')
        assert not node.find_parent(class_='requirement-bundle')
        assert 'Course grouping / context' in node.select_one(':scope > details > summary').get_text()
    general=soup.select_one('#requirements-group-general-top')
    assert not general.select_one(':scope > details').has_attr('open')
    assert len(general.select('.requirement'))==6
    assert general.select_one('#requirement-mit-ai-gir-science-1')
    assert not soup.select_one('#requirement-mit-ai-chart-reference > details').has_attr('open')
    assert {n['id'] for n in soup.select('.requirement')}=={'requirement-'+r['id'] for r in p['requirements']}


def test_general_education_scope_uses_explicit_source_labels_not_course_subject(site_data):
    p=site_data['programs'][0]
    p['sources']=[dict(id='general-source',title='General Education',url='https://example.edu/general/')]
    p['requirements']=[dict(rule('general',courses=[p['courses'][0]['id']],title='Science selection'),source_id='general-source'),rule('major',courses=[p['courses'][0]['id']],title='Biology for AI research')]
    soup=BeautifulSoup(requirement_tree(p),'html.parser')
    assert soup.select_one('.requirements > .requirement')['id']=='requirement-major'
    assert soup.select_one('#requirements-group-general-top #requirement-general')
    assert not soup.select_one('#requirements-group-general-top #requirement-major')



def test_nested_general_education_follows_program_courses(site_data):
    p=site_data['programs'][0]
    p['sources']=[dict(id='general-source',title='General Education',url='https://example.edu/general/')]
    p['requirements']=[rule('root',title='Degree curriculum'),dict(rule('general',parent='root',courses=[p['courses'][0]['id']],title='General education'),source_id='general-source'),rule('major',parent='root',courses=[p['courses'][0]['id']],title='Program core')]
    soup=BeautifulSoup(requirement_tree(p),'html.parser')
    children=soup.select('#requirement-root > details > .requirement-body > ul > .requirement')
    assert [n['id'] for n in children]==['requirement-major','requirement-general']
    assert soup.select_one('#requirement-major > details').has_attr('open')
    assert not soup.select_one('#requirement-general > details').has_attr('open')



def test_major_excluding_general_education_remains_program_scope(site_data):
    p=site_data['programs'][0]
    p['sources']=[dict(id='source',title='Computer Science and Engineering undergraduate curriculum')]
    p['requirements']=[rule('major',courses=[p['courses'][0]['id']],title='AI major: 124 units excluding college general education')]
    soup=BeautifulSoup(requirement_tree(p),'html.parser')
    assert soup.select_one('.requirements > #requirement-major')
    assert not soup.select_one('#requirements-group-general-top')
    assert soup.select_one('#requirement-major > details').has_attr('open')


def test_course_leaf_headers_credits_and_incomplete_references(site_data):
    p=site_data['programs'][0]
    p['courses']=[dict(id='one',code='CS 100',name='Programming',credits=99,credit_unit='quarter_hours'),dict(id='two',code='CS 200',name='Methods')]
    p['requirements']=[dict(rule('single',courses=['one'],title='CS 100'),credits=3.0,credit_unit='semester_hours'),rule('unknown',courses=['one'],title='CS 100'),dict(rule('bundle',courses=['one','two'],title='CS 100 + CS 200'),credits=12,credit_unit='units'),dict(rule('unknown-unit',courses=['two'],title='CS 200'),credits=4,credit_unit='unknown'),rule('partial',courses=['one','missing']),dict(rule('choice',kind='choose_courses',courses=['one']),count=1)]
    before=deepcopy(p);soup=BeautifulSoup(requirement_tree(p),'html.parser')
    assert p==before
    header=soup.select_one('#requirement-single > details > summary')
    assert header.h3.get_text()=='CS 100 · Programming'
    assert header.select_one('.requirement-rule').get_text()=='3 Semester hours'
    assert 'Complete all' not in header.get_text()
    assert not header.select('.requirement-preview')
    assert not soup.select_one('#requirement-unknown > details > summary .requirement-rule')
    assert '99' not in soup.select_one('#requirement-unknown > details > summary').get_text()
    bundle=soup.select_one('#requirement-bundle > details > summary')
    assert bundle.h3.get_text()=='CS 100 · Programming + CS 200 · Methods'
    assert bundle.select_one('.requirement-rule').get_text()=='Complete all courses in this group · 12 Units'
    assert soup.select_one('#requirement-unknown-unit > details > summary .requirement-rule').get_text()=='4 credit unit unknown'
    assert not soup.select_one('#requirement-partial').get('class')==['requirement','requirement-course-group']
    assert 'Choose courses' in soup.select_one('#requirement-choice > details > summary').get_text()
