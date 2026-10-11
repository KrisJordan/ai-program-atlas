from copy import deepcopy
import hashlib
import json
from pathlib import Path
from bs4 import BeautifulSoup
import pytest
from atlas.adapters import miami_context_course_reviews as m
from atlas.adapters.business_society_minors import clean


@pytest.fixture
def synthetic(monkeypatch):
    html='<h1>Example (XYZ)</h1><div class="courseblock"><p class="courseblocktitle">XYZ 100. Example context. 1-3 Credit Hours.</p><p>Source content. Requisite: Nonbusiness students. Components: LEC.</p></div>'
    block=BeautifulSoup(html,'html.parser').select_one('.courseblock')
    item=dict(key='xyz',name='Example context',program_ids=['example'],url='https://example.edu/xyz/',block_hash=hashlib.sha256(clean(block.get_text(' ',strip=True)).encode()).hexdigest(),description='Original concise summary.',prerequisites='Requisite: Nonbusiness students.',category='applications')
    monkeypatch.setattr(m,'SPEC',dict(sources={'xyz':dict(heading='Example (XYZ)')},courses={'XYZ 100':item}))
    return html


def test_observation_does_not_certify_review_or_promote_context(synthetic):
    result=m.parse(synthetic,pid='example',key='xyz');c=result['courses'][0]
    assert c['credits'] is None and c['credit_unit']=='semester_hours'
    assert c['prerequisites']=='Requisite: Nonbusiness students.'
    assert 'category_review'not in c and 'requirements'not in result
    previous=lambda _:dict(id='example',courses=[dict(c)],requirements=[{'id':'existing-context','kind':'note'}])
    composed=m._compose(previous,synthetic,pid='example',key='xyz')
    assert len(composed['courses'])==1 and composed['requirements']==previous('')['requirements']


@pytest.mark.parametrize('old,new',[('Example (XYZ)','Wrong (XYZ)'),('Source content.','Changed description.'),('Nonbusiness students.','All students.'),('1-3 Credit','3 Credit')])
def test_changed_identity_content_eligibility_or_credit_requires_review(synthetic,old,new):
    with pytest.raises(ValueError):m.parse(synthetic.replace(old,new),pid='example',key='xyz')


def test_missing_duplicate_and_unreviewed_scope_rejected(synthetic):
    block=str(BeautifulSoup(synthetic,'html.parser').select_one('.courseblock'))
    for html in ['<h1>Example (XYZ)</h1>',synthetic+block]:
        with pytest.raises(ValueError):m.parse(html,pid='example',key='xyz')
    with pytest.raises(ValueError):m.parse(synthetic,pid='unrelated',key='xyz')


def test_actual_reviewed_blocks_and_seed_provenance():
    observations=0
    for key,source in m.SPEC['sources'].items():
        cache=Path('.cache/http')/(hashlib.sha256(source['url'].encode()).hexdigest()+'.body')
        if not cache.exists():pytest.skip('Ignored actual official source capture unavailable')
        for pid in {pid for x in m.SPEC['courses'].values()if x['key']==key for pid in x['program_ids']}:
            result=m.parse(cache.read_text(),pid=pid,key=key)
            seed=json.loads(Path('data/programs',pid+'.json').read_text());bycode={c['code']:c for c in seed['courses']}
            for c in result['courses']:
                assert 'category_review'not in c
                assert {k:bycode[c['code']][k]for k in c}==c
                assert bycode[c['code']]['category_review']['source_ids']==[c['source_id']]
                observations+=1
    assert observations==sum(len(x['program_ids'])for x in m.SPEC['courses'].values())


def test_business_credit_exclusions_and_existing_concurrent_route_retained():
    assert 'no credit for business' in m.SPEC['courses']['FIN 300']['prerequisites']
    assert 'no credit toward any business' in m.SPEC['courses']['BUS 201']['prerequisites']
    assert 'Non Business Majors' in m.SPEC['courses']['BUS 200']['prerequisites']
    assert 'Or Corequisites:' in m.SPEC['courses']['MAS 311']['prerequisites']
    # Similar titles and credit exclusions are not identity-group evidence.
    assert m.SPEC['courses']['ECO 301']['name']==m.SPEC['courses']['ECO 303']['name']
    assert m.SPEC['courses']['ECO 301']['block_hash']!=m.SPEC['courses']['ECO 303']['block_hash']


def test_content_distinguishes_ai_tools_statistics_and_unknown_topics():
    assert m.SPEC['courses']['WRS 250']['category']=='human_context'
    assert m.SPEC['courses']['WRS 310']['category']=='human_context'
    assert m.SPEC['courses']['WRS 306']['credits'] is None
    assert '1–3' in m.SPEC['courses']['WRS 306']['description']
    assert 'working understanding' in m.SPEC['courses']['WRS 335']['prerequisites']
    assert m.SPEC['courses']['PSY 291']['category']=='mathematics'
    assert m.SPEC['courses']['PSY 250']['category']=='applications'
    assert m.SPEC['courses']['PSY 390']['review']['status']=='mixed'
    assert m.SPEC['courses']['PSY 375']['review']['status']=='unclassified'
    assert m.SPEC['courses']['PSY 225']['prerequisites'] is None
    assert 'PSY Major or PSY Minor or NEU major' in m.SPEC['courses']['PSY 291']['prerequisites']


def test_language_heritage_exclusions_and_external_credit_stay_explicit():
    assert 'Closed to native speakers' in m.SPEC['courses']['ARB 101']['prerequisites']
    assert 'equivalent of ARB 201' in m.SPEC['courses']['ARB 207']['prerequisites']
    assert 'does not fulfill' in m.SPEC['courses']['ARB 410']['prerequisites']
    assert 'native or native-level' in m.SPEC['courses']['CHI 322']['prerequisites']
    assert m.SPEC['courses']['CHI 295']['review']['status']=='unclassified'
    assert m.SPEC['courses']['CHI 295']['credits'] is None
    assert '1-3' in m.SPEC['courses']['CHI 295']['description']
    assert 'at most three' in m.SPEC['courses']['ARB 394']['prerequisites']
    assert 'ARB 295' not in m.SPEC['courses']  # No invented match to the current Arabic chapter.


def test_french_german_language_and_credit_scopes_remain_individual():
    assert 'two or more years' in m.SPEC['courses']['FRE 101']['prerequisites']
    assert m.SPEC['courses']['FRE 432']['category']=='human_context'
    assert 'departmental stipulations' in m.SPEC['courses']['FRE 310']['prerequisites']
    assert 'twentieth' in m.SPEC['courses']['FRE 365']['description']
    assert m.SPEC['courses']['GER 321']['review']['status']=='unclassified'
    assert m.SPEC['courses']['GER 395']['credits'] is None
    assert 'GER 400' not in m.SPEC['courses']
    assert m.SPEC['courses']['GER 442']['prerequisites'] is None


def test_italian_portuguese_japanese_routes_do_not_erase_restrictions():
    assert 'formally educated' in m.SPEC['courses']['ITA 301']['prerequisites']
    assert 'departmental stipulations' in m.SPEC['courses']['ITA 310']['prerequisites']
    assert 'excludes foreign-language' in m.SPEC['courses']['ITA 315']['prerequisites']
    assert 'Portuguese minors must' in m.SPEC['courses']['POR 354']['prerequisites']
    assert 'native Portuguese' in m.SPEC['courses']['POR 105']['prerequisites']
    j=m.SPEC['courses']['JPN 210']
    assert 'JPN 102' in j['prerequisites'] and 'not resolved' in j['prerequisites']
    assert m.SPEC['courses']['JPN 432']['category']=='human_context'
    assert 'two college years' in m.SPEC['courses']['JPN 432']['prerequisites']
    assert m.SPEC['courses']['ITA 399']['category']=='other'
    assert m.SPEC['courses']['JPN 495']['credits'] is None


def test_classical_hebrew_creole_exact_scopes_remain_separate():
    assert m.SPEC['courses']['LAT 103']['credits']==3
    assert 'extra weekly' in m.SPEC['courses']['LAT 103']['prerequisites']
    assert 'placement depends' in m.SPEC['courses']['LAT 103']['prerequisites']
    assert m.SPEC['courses']['GRE 491']['category']=='other'
    assert m.SPEC['courses']['GRE 491']['credits'] is None
    assert 'title-supported' in m.SPEC['courses']['GRE 401']['review']['rationale']
    assert m.SPEC['courses']['GRE 411']['prerequisites'] is None
    assert 'Normally closed' in m.SPEC['courses']['HEB 101']['prerequisites']
    assert m.SPEC['courses']['HAI 202']['category']=='human_context'
    assert m.SPEC['courses']['HAI 495']['review']['status']=='unclassified'


def test_spanish_digital_methods_and_credit_exclusions_are_scoped():
    assert m.SPEC['courses']['MLL 210']['category']=='human_context'
    assert 'critically evaluates' in m.SPEC['courses']['MLL 210']['description']
    assert m.SPEC['courses']['SPA 410']['category']=='human_context'
    assert 'topic-modeling' in m.SPEC['courses']['SPA 410']['description']
    assert m.SPEC['courses']['SPA 333']['category']=='human_context'
    assert m.SPEC['courses']['SPA 433']['category']=='human_context'
    for code in ['SPA 301','SPA 307']:
        assert 'does not establish identical courses' in m.SPEC['courses'][code]['prerequisites']
    assert 'no second prerequisite' in m.SPEC['courses']['SPA 361']['prerequisites']
    assert m.SPEC['courses']['SPA 280']['review']['status']=='unclassified'
    assert m.SPEC['courses']['MLL 295']['credits'] is None


def test_media_methods_design_and_ai_creation_are_not_conflated():
    assert m.SPEC['courses']['JMM 285']['category']=='mathematics'
    assert m.SPEC['courses']['JMM 301']['category']=='human_context'
    assert m.SPEC['courses']['JMM 341']['category']=='applications'
    assert m.SPEC['courses']['CIM 103']['review']['status']=='mixed'
    assert m.SPEC['courses']['CIM 103']['review']['candidate_categories']==['human_context','applications']
    assert m.SPEC['courses']['CIM 104']['category']=='human_context'
    assert m.SPEC['courses']['CIM 204']['category']=='applications'
    assert 'Approved Statistics' in m.SPEC['courses']['STC 311']['prerequisites']
    assert 'Permission of Instructor' in m.SPEC['courses']['JMM 461']['prerequisites']
    assert 'Requisite: Junior Standing' in m.SPEC['courses']['STC 482']['prerequisites']


def test_communication_and_cinema_practice_follow_content_and_amounts():
    assert m.SPEC['courses']['COS 304']['credits']==1
    assert m.SPEC['courses']['COS 377']['category']=='human_context'
    assert m.SPEC['courses']['COS 324']['category']=='human_context'
    assert m.SPEC['courses']['CCA 126']['category']=='human_context'
    assert m.SPEC['courses']['CCA 151']['category']=='applications'
    assert m.SPEC['courses']['CCA 403']['category']=='human_context'
    assert 'Junior Standing' in m.SPEC['courses']['CCA 404']['prerequisites']
    assert m.SPEC['courses']['COS 545']['prerequisites'] is None
    assert m.SPEC['courses']['COM 250']['category']=='human_context'


def test_health_statistics_science_and_policy_scopes():
    for code in ['BPH 202','HCS 202','NUR 202']:
        c=m.SPEC['courses'][code]
        assert c['category']=='mathematics' and c['credits']==3
        assert 'ALEKS 40' in c['prerequisites'] and 'ACT 22' in c['prerequisites']
    assert m.SPEC['courses']['ATM 306']['review']['status']=='mixed'
    assert 'Major or Minor in Meteorology' in m.SPEC['courses']['ATM 103']['prerequisites']
    assert m.SPEC['courses']['GSC 109']['category']=='applications'
    assert m.SPEC['courses']['PHY 110']['category']=='applications'
    assert m.SPEC['courses']['NUR 536']['category']=='human_context'
    assert 'no IP Credit' in m.SPEC['courses']['NUR 536']['prerequisites']
    assert m.SPEC['courses']['BPH 301']['review']['status']=='mixed'
    assert m.SPEC['courses']['BPH 319']['category']=='human_context'
    assert m.SPEC['courses']['MSC 191']['credits'] is None
    assert m.SPEC['courses']['MSC 191']['review']['status']=='unclassified'
    assert 'excludes Marine Science major/minor students' in m.SPEC['courses']['MSC 101']['prerequisites']
    assert m.SPEC['courses']['MSC 313']['category']=='human_context'
    assert m.SPEC['courses']['MSC 346']['review']['status']=='mixed'


def test_source_verified_health_statistics_identity_preserves_context_and_records():
    from atlas.curriculum_profile import requirement_profile
    pids=m.SPEC['courses']['BPH 202']['program_ids']
    for pid in pids:
        p=json.loads(Path('data/programs',pid+'.json').read_text())
        groups=[g for g in p['course_identity_groups'] if g['id'].endswith('crosslisted-health-statistics-202')]
        assert len(groups)==1
        byid={c['id']:c for c in p['courses']};g=groups[0]
        assert {byid[x]['code']for x in g['course_ids']}=={'BPH 202','HCS 202','NUR 202'}
        assert 'miami-general-education-policy' in g['source_ids']
        assert {byid[x]['category']for x in g['course_ids']}=={'mathematics'}
        before=deepcopy(p);before['course_identity_groups'].remove(g)
        a,b=requirement_profile(before),requirement_profile(p)
        assert a['required']==b['required'] and a['options']==b['options']
        assert a['unresolved']['count']==b['unresolved']['count']+2
        assert a['unresolved']['source_record_count']==b['unresolved']['source_record_count']
        assert len(before['courses'])==len(p['courses'])
    cache=Path('.cache/research/miami-degree-audit/policy-general.html')
    if cache.exists():
        text=clean(BeautifulSoup(cache.read_text(),'html.parser').get_text(' ',strip=True))
        assert 'NUR 202 Introductory Statistics in Health Care (also listed as BPH 202 and HCS 202 )' in text
        assert 'BPH 202 Introductory Statistics in Health Care (also listed as NUR 202 and HCS 202 )' in text


def test_art_practice_interpretation_unspecified_topics_and_conditions():
    for code in ['ART 109','ART 254','ART 292','ART 354','ART 554']:
        assert m.SPEC['courses'][code]['category']=='applications'
    assert m.SPEC['courses']['ART 407']['category']=='human_context'
    assert m.SPEC['courses']['ART 517']['category']=='human_context'
    assert m.SPEC['courses']['ART 315']['review']['status']=='mixed'
    for code in ['ART 180','ART 206','ART 255','ART 306','ART 406','ART 506','ART 555']:
        assert m.SPEC['courses'][code]['review']['status']=='unclassified'
    assert m.SPEC['courses']['ART 555']['credits'] is None
    assert m.SPEC['courses']['ART 593']['credits'] is None
    assert 'Portfolio required' in m.SPEC['courses']['ART 593']['prerequisites']
    assert 'ART 251 OR ART 252 OR ART 253 OR ART 254 OR ART 255' in m.SPEC['courses']['ART 356']['prerequisites']
    assert 'prohibits repeated credit' in m.SPEC['courses']['ART 510']['prerequisites']
    assert m.SPEC['courses']['ART 305']['prerequisites'] is None
    assert 'referenced course' in m.SPEC['courses']['ART 305']['description']


def test_performance_content_and_nonstandard_eligibility_are_scoped():
    assert m.SPEC['courses']['THA 201']['category']=='applications'
    assert 'algorithm instruction is not established' in m.SPEC['courses']['THA 201']['description']
    assert m.SPEC['courses']['THA 253']['category']=='applications'
    assert m.SPEC['courses']['THA 107']['category']=='human_context'
    assert m.SPEC['courses']['THA 301']['category']=='human_context'
    assert m.SPEC['courses']['DAN 130']['review']['status']=='unclassified'
    assert m.SPEC['courses']['DAN 250']['category']=='human_context'
    assert 'formal ballet training or permission' in m.SPEC['courses']['DAN 221']['prerequisites']
    assert 'for BGS students only' in m.SPEC['courses']['THA 302']['prerequisites']
    assert 'BFA Comprehensive Musical Theatre majors only' in m.SPEC['courses']['THA 112']['prerequisites']
    assert 'THA 101 OR THA 141 OR THA 142' in m.SPEC['courses']['THA 245']['prerequisites']
    assert m.SPEC['courses']['THA 143']['credits']==1
    assert m.SPEC['courses']['THA 161']['credits'] is None
    assert m.SPEC['courses']['THA 384']['credits'] is None


def test_environment_education_and_related_methods_keep_exact_scope():
    assert m.SPEC['courses']['ECS 204']['category']=='mathematics'
    assert m.SPEC['courses']['ISE 311']['category']=='mathematics'
    assert m.SPEC['courses']['ECS 342']['category']=='applications'
    assert m.SPEC['courses']['ECS 403']['review']['status']=='mixed'
    assert m.SPEC['courses']['ECS 201']['review']['status']=='unclassified'
    assert m.SPEC['courses']['ECS 572']['credits'] is None
    assert '0-3' in m.SPEC['courses']['ECS 572']['description']
    assert 'transfer credit only' in m.SPEC['courses']['ECS 391']['description']
    assert 'Department of Biology' in m.SPEC['courses']['ECS 485']['prerequisites']
    assert 'Requisite: ECS Major or ECS Minor or Prerequisite: ECS 215' in m.SPEC['courses']['ECS 415']['prerequisites']
    assert 'Or Co-requisite: EPS 311' in m.SPEC['courses']['EPS 321']['prerequisites']
    assert m.SPEC['courses']['TAL 103']['review']['status']=='mixed'
    assert 'Co-Requisite: TAL 306' in m.SPEC['courses']['TAL 308']['prerequisites']
    assert 'Pre- or Co-Requisite TAL 330 and TAL 332' in m.SPEC['courses']['TAL 434']['prerequisites']
    assert 'FOOTE FELLOW' in m.SPEC['courses']['KIN 308']['prerequisites']
    assert 'does not qualify' in m.SPEC['courses']['EPS 420']['description']
