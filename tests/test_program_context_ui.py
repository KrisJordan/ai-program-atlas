"""Source-backed second-major and parent-program presentation contracts."""
from copy import deepcopy
from bs4 import BeautifulSoup
from atlas.site import build, directory_payload, major_filter_buckets
from tests.test_site import site_data  # noqa: F401


def context_fixture(data):
    second=data['programs'][0]
    second.update(program_kind='additional_major',award_level='other',title='Artificial Intelligence Additional Major')
    second['major_relationship']=dict(kind='second_major_only',official_term='Additional Major',eligibility='Available alongside an eligible primary degree.',source_ids=['outcome-source'],locator='Official additional-major eligibility',reviewed_at='2026-10-11')
    data['programs'][1].update(program_kind='degree',award_level='BSAI')
    data['institutions'][1]['rankings'][0]['category'] = 'National Universities'
    for index in [2,3]:data['programs'][index].update(program_kind='concentration',award_level='concentration')
    known=data['programs'][2]
    known['sources'] = deepcopy(second['sources'])
    known['parent_programs']=[dict(id='parent-'+award.lower(),title='Computer Science',award_level=award,award_label=label,relationship='track',parent_program_id=None,eligibility=None,source_ids=['outcome-source'],locator='Official parent heading',reviewed_at='2026-10-11') for award,label in [('BA','Bachelor of Arts'),('BS','Bachelor of Science')]]
    known['parent_program_review']=dict(status='verified',reviewed_at='2026-10-11',source_ids=['outcome-source'],notes=[])
    return data


def test_second_major_is_a_source_relationship_not_an_award_guess(site_data):
    context_fixture(site_data)
    assert major_filter_buckets(site_data['programs'][0])==['second_major']
    assert major_filter_buckets(site_data['programs'][1])==['other']
    unverified=deepcopy(site_data['programs'][0]);unverified.pop('major_relationship')
    assert major_filter_buckets(unverified)==['other']


def test_parent_context_is_consistent_in_static_pages_and_comparison_projection(site_data,tmp_path):
    context_fixture(site_data);original=deepcopy(site_data)
    projected=directory_payload(site_data,'/ai-program-atlas/')
    build(site_data,tmp_path)
    assert site_data==original
    root=BeautifulSoup((tmp_path/'index.html').read_text(),'html.parser')
    card=root.select_one('[data-program-id=test-ai-2] .parent-programs')
    detail=BeautifulSoup((tmp_path/'programs/test-ai-2/index.html').read_text(),'html.parser').select_one('.parent-programs')
    compare=BeautifulSoup(projected['programs'][2]['parent_context_html'],'html.parser').select_one('.parent-programs')
    assert card.get_text()==detail.get_text()==compare.get_text()
    assert 'Bachelor of Arts (BA)' in card.get_text() and 'Bachelor of Science (BS)' in card.get_text()
    assert card.find('a',href='https://example.edu/outcome')
    assert 'Not yet verified' in root.select_one('[data-program-id=test-ai-3] .parent-programs').get_text()
    assert not root.select_one('#filter-panel').has_attr('open')
    second_detail = BeautifulSoup((tmp_path/'programs/test-ai-0/index.html').read_text(), 'html.parser')
    assert 'No separate award' in second_detail.select_one('.detail-badges').get_text()
    other_detail = BeautifulSoup((tmp_path/'programs/test-ai-1/index.html').read_text(), 'html.parser')
    assert 'BSAI' in other_detail.select_one('.detail-badges').get_text()


def test_verified_parent_can_have_full_award_without_invented_abbreviation(site_data):
    from atlas.site import parent_context_markup
    program = context_fixture(site_data)['programs'][2]
    program['parent_programs'] = [program['parent_programs'][1]]
    program['parent_programs'][0]['award_level'] = None
    markup = BeautifulSoup(parent_context_markup(program), 'html.parser')
    assert 'Bachelor of Science' in markup.get_text()
    assert '(BS)' not in markup.get_text()
    assert 'Award not yet verified' not in markup.get_text()
    assert 'Official parent heading' in markup.get_text()
