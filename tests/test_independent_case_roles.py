"""Independent source-table/identity checkpoint; not a full description reread."""
import json
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from atlas.curriculum_profile import requirement_profile
from atlas.site import category_chart

ROOT = Path(__file__).resolve().parents[1]
REPORT = json.loads((ROOT/'research/degree-audit/independent-case-roles.json').read_text())


def load(award):
    return json.loads((ROOT/'data/programs'/f'case-western-reserve-university-artificial-intelligence-{award}-degree.json').read_text())


@pytest.mark.parametrize('award',['ba','bs'])
def test_case_every_canonical_role_matches_independent_source_sets(award):
    p = load(award)
    expected = next(e for e in REPORT['programs'] if e['program_id']==p['id'])
    courses = {c['id']:c for c in p['courses']}
    aliases = {cid:cid for cid in courses}
    for group in p['course_identity_groups']:
        for cid in group['course_ids']:
            aliases[cid] = group['canonical_course_id']
    canonical = {aliases[cid] for cid in courses}
    assert {courses[cid]['code'] for cid in canonical}==set().union(*(set(codes) for codes in expected['expected_course_codes'].values()))
    for role,codes in expected['expected_course_codes'].items():
        for code in codes:
            cid = next(cid for cid in canonical if courses[cid]['code']==code)
            represented = [c for c in courses.values() if aliases[c['id']]==cid]
            isolated = {**p,'courses':represented,'course_identity_groups':[]}
            # Source sets are canonical; alias workload must also resolve to the same role.
            if len(represented)>1:
                isolated['course_identity_groups']=[g for g in p['course_identity_groups'] if g['canonical_course_id']==cid]
            actual = requirement_profile(isolated)
            assert actual[role]['count']==1,(award,role,code)
            assert sum(actual[r]['count'] for r in ['required','options','unresolved'])==1
    observed = requirement_profile(p)
    assert observed['identity']==expected['expected_identity']
    for role in ['required','options','unresolved']:
        manual = expected['expected_profile'][role]
        for field in ['count','source_record_count']:
            assert observed[role][field]==manual[field]
        for field in ['categories','classification']:
            assert observed[role][field]=={k:manual[field].get(k,0) for k in observed[role][field]}


@pytest.mark.parametrize('award',['ba','bs'])
def test_case_registered_aliases_and_distinct_versions_match_source_review(award):
    p = load(award)
    byid = {c['id']:c['code'] for c in p['courses']}
    groups = {frozenset(byid[c] for c in g['course_ids']) for g in p['course_identity_groups']}
    reviewed = {frozenset(g['codes']) for g in REPORT['identity_reviews']}
    if award=='ba':
        reviewed.remove(frozenset(['MATH 406','PHIL 306']))
    assert groups==reviewed
    for g in REPORT['identity_reviews']:
        assert all(set(g['codes'])<=set(member['offered_as_codes']) for member in g['evidence'])
    for codes in [['CHIN 350','CHIN 350D'],['ENGL 364','ENGL 364C'],['CSDS 132','CSDS 134']]:
        assert not any(set(codes)<=g for g in groups)
    assert frozenset(['ENGL 364','HUMN 364']) in groups


@pytest.mark.parametrize('award',['ba','bs'])
def test_case_chart_distinguishes_profile_scope_from_missing_evidence(award):
    p = load(award)
    expected = next(e for e in REPORT['programs'] if e['program_id']==p['id'])
    soup = BeautifulSoup(category_chart(p),'html.parser')
    note = soup.select_one('.profile-uncertainty').get_text()
    assert '97 course identities are outside the fixed/option count profiles' in note
    assert 'unresolved requirement roles' not in note
    assert 'see individual requirement rules' in note
    for role in ['required','options']:
        panel = soup.select_one(f'[data-profile={role}]')
        manual = expected['expected_profile'][role]
        assert f"{manual['count']} distinct" in panel.select_one('.profile-total').get_text()
        assert str(manual['source_record_count'])+' retained source-code records' in panel.select_one('.profile-identity').get_text()
        for key,value in manual['categories'].items():
            assert panel.select_one(f'[data-category={key}] strong').get_text()==str(value)
    # The source-role check cannot certify every description/category.
    assert REPORT['second_pass_status']=='partial' and not REPORT['full_degree_verified']


def test_mixed_context_and_unbound_records_receive_neutral_copy():
    p = {'courses':[
        {'id':'fixed','category':'foundations'},
        {'id':'duration','category':'applications'},
        {'id':'unknown','category':'other'},
    ],'requirements':[
        {'id':'core','parent_id':None,'kind':'all','course_ids':['fixed']},
        {'id':'wellness','parent_id':None,'kind':'note','course_ids':['duration'],'summary':'Two semesters of wellness; credits do not determine duration.'},
    ]}
    profile = requirement_profile(p)
    assert profile['required']['count']==1 and profile['options']['count']==0 and profile['unresolved']['count']==2
    note = BeautifulSoup(category_chart(p),'html.parser').select_one('.profile-uncertainty').get_text()
    assert '2 course records are outside the fixed/option count profiles' in note
    assert 'unresolved requirement roles' not in note
    assert 'verified' not in note and 'complete' not in note


@pytest.mark.parametrize('award',['ba','bs'])
def test_case_all_source_approval_pools_and_whole_bundles_remain_intact(award):
    p = load(award)
    courses = {c['id']:c['code'] for c in p['courses']}
    for pool in REPORT['approval_pools']:
        parent = next(r for r in p['requirements'] if r['title']==pool['name']+' approved options')
        children = [r for r in p['requirements'] if r.get('parent_id')==parent['id']]
        mapped = {courses[cid] for r in [parent]+children for cid in r.get('course_ids',[])}
        assert mapped==set(pool['source_codes'])
        assert len(mapped)==pool['source_code_count']
        for bundle in pool['bundles']:
            row = next(r for r in children if {courses[cid] for cid in r.get('course_ids',[])}==set(bundle))
            assert row['kind']=='all'
        if pool['role']=='duration_context':
            assert parent['kind']=='note'
