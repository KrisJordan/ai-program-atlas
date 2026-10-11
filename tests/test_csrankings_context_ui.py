"""Displayed publication context preserves upstream scores and missingness."""
from copy import deepcopy
import json
import pytest
from bs4 import BeautifulSoup
from atlas.research_context import FIELDS, institution_context
from atlas.site import build, directory_payload
from tests.test_site import site_data  # noqa: F401


def research_data():
    return {'methodology':{'fields':list(FIELDS)[:-1],'aggregate_field':'aggregate','year_start':2016,'year_end':2025,'geographic_filter':'us','status':'available','source_snapshot':'a'*40,'source_url':'https://csrankings.org/','method':'Pinned fractional publication method.','permission':{'statement':'Educational project permission.','confirmed_date':'2026-10-11','scope':'This educational project'},'field_membership':{'ai':['aaai','ijcai']}},'population':{'listed_us_institutions':201,'ranked_institutions_by_field':dict.fromkeys(FIELDS,197)},'observations':[{'institution_id':'test-0','field':field,'value':3.2,'rank':175,'missingness':'observed','adjusted_count':2.2345 if field!='aggregate' else None,'unrounded_score':3.2345,'upstream_institution':'Upstream Test Institution'} for field in FIELDS]+[{'institution_id':'test-1','field':field,'value':None,'rank':None,'missingness':'no_selected_output'} for field in FIELDS]}


@pytest.fixture
def research_site_data(site_data):
    site_data['csrankings']=research_data()
    return site_data


def test_scores_are_not_recomputed_or_reranked_inside_atlas(research_site_data):
    context=institution_context(research_site_data,'test-0')
    assert len(context['rows'])==6
    assert context['rows'][0]['score_text']=='3.2'
    assert context['rows'][0]['adjusted_count_text']=='2.235'
    assert context['rows'][0]['rank_text']=='#175 of 197'
    assert context['rows'][-1]['adjusted_count_text']=='Not applicable'
    assert directory_payload(research_site_data,'/nested/') ['programs'][0]['research_context']==context


@pytest.mark.parametrize('status',['no_selected_output','not_listed','outside_eligible','unmatched','source_missing'])
def test_missing_rows_cannot_leak_zero_or_stale_rank(research_site_data,status):
    for row in research_site_data['csrankings']['observations']:
        row.update(missingness=status,value=0,rank=999,adjusted_count=0)
    context=institution_context(research_site_data,'test-0')
    assert all(row['score_text']=='Not available' and row['rank_text']=='Not ranked in this selection' for row in context['rows'])
    absent=institution_context(research_site_data,'never-listed')
    assert all(row['missingness']=='source_missing' for row in absent['rows'])


def test_available_static_detail_methodology_and_absent_context(tmp_path,research_site_data):
    build(research_site_data,tmp_path,'/nested/atlas/')
    page=BeautifulSoup((tmp_path/'programs/test-ai-0/index.html').read_text(),'html.parser')
    panel=page.select_one('#research-context')
    assert len(panel.select('tbody tr'))==6
    assert '#175 of 197' in panel.get_text()
    assert 'Adjusted publications' in panel.get_text()
    assert 'not an average of ranks' in panel.get_text()
    assert panel.select_one('a')['href']=='/nested/atlas/methodology/#research'
    absent=BeautifulSoup((tmp_path/'programs/test-ai-1/index.html').read_text(),'html.parser').select_one('#research-context')
    assert 'No selected publication output' in absent.get_text()
    assert '#999' not in absent.get_text()
    method=(tmp_path/'methodology/index.html').read_text()
    for text in ['2016–2025','full eligible U.S.','October 11, 2026','COPYING','does not claim broader reuse','201','197','educational project']:
        assert text.lower() in method.lower()
    assert 'licensing remains unresolved' not in method
    before=deepcopy(research_site_data)
    directory_payload(research_site_data,'/nested/atlas/')
    assert before==research_site_data


def test_not_imported_snapshot_does_not_publish_stale_observations(tmp_path,research_site_data):
    research_site_data['csrankings']['methodology']['status']='not_imported'
    assert institution_context(research_site_data,'test-0') is None
    build(research_site_data,tmp_path)
    assert 'id="research-context"' not in (tmp_path/'programs/test-ai-0/index.html').read_text()
    assert 'not imported' in (tmp_path/'methodology/index.html').read_text()
