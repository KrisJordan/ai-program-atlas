"""Cohort and degree-award groupings require explicit evidence."""
from bs4 import BeautifulSoup
from atlas.site import build, directory_payload
from tests.test_site import site_data  # noqa: F401


def test_cohort_membership_uses_rankings_and_renders_each_program_once(site_data,tmp_path):
    site_data['programs'][0]['institution']['name']='A name containing Liberal Arts College'
    site_data['institutions'][1]['rankings']=[]
    build(site_data,tmp_path)
    root=BeautifulSoup((tmp_path/'index.html').read_text(),'html.parser')
    assert root.select_one('[data-cohort-group=nu] [data-program-id=test-ai-0]')
    assert root.select_one('[data-cohort-group=unclassified] [data-program-id=test-ai-1]')
    assert root.select_one('[data-cohort-group=lac] [data-program-id=test-ai-2]')
    assert len(root.select('[data-program-id]'))==5
    assert root.select_one('#cohort-lac-majors [data-program-id=test-ai-2]')
    assert root.select_one('#cohort-lac-concentrations [data-program-id=test-ai-3]')
    assert root.select_one('#cohort-lac-minors [data-program-id=test-ai-4]')


def test_award_options_labels_provenance_and_safe_projection(site_data,tmp_path):
    p=site_data['programs'][0]
    p['award_level']='other'
    p['award_options']=[dict(label='Bachelor of Arts',normalized='BA',source_id='outcome-source',locator='Award heading'),dict(label='Bachelor of Science',normalized='BS',source_id='outcome-source',locator='Award heading')]
    view=directory_payload(site_data,'/nested/atlas/')
    assert view['programs'][0]['major_awards']==['BS','BA']
    assert view['programs'][2]['major_awards']==['other']
    assert [o['label'] for o in view['programs'][0]['award_options']]==['Bachelor of Arts','Bachelor of Science']
    build(site_data,tmp_path)
    for path in ['index.html','programs/test-ai-0/index.html']:
        root=BeautifulSoup((tmp_path/path).read_text(),'html.parser')
        labels=root.select_one('.award-options')
        assert labels.get_text(' ',strip=True)=='Offered awards: Bachelor of Arts ↗ · Bachelor of Science ↗'
        assert all(a['href']=='https://example.edu/outcome' for a in labels.find_all('a'))
