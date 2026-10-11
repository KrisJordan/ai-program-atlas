import copy
import json
from pathlib import Path
import pytest
from atlas.curriculum_profile import requirement_profile
from atlas.degree_audit import core_review_fingerprint, validate_core_review

PID='university-of-california-san-diego-artificial-intelligence-bs-degree'

def seed(pid):return json.loads(Path('data/programs',pid+'.json').read_text())
def reviews():return json.loads(Path('research/degree-audit/independent-core-west.json').read_text())['programs']


def test_pinned_manual_fixed_sets_and_explicit_partial_scope():
    for review in reviews():
        program=seed(review['program_id']);validate_core_review(review,program['id'])
        assert review['reviewed_content_hash']==core_review_fingerprint(program)
        assert review['independence']=='same_author_recheck_with_separate_core_confirmation'
        actual=requirement_profile(program,include_course_ids=True)
        for role,ids in review['expected_course_ids'].items():
            if ids is not None:assert set(ids)==set(actual['course_ids'][role])
        assert review['expected_course_ids']['unresolved'] is None
        assert review['dimensions']['choice_rules']['status']=='partial'
        assert review['dimensions']['classification']['status']=='partial'
    assert len(reviews()[0]['expected_course_ids']['required'])==8
    assert len(reviews()[1]['expected_course_ids']['required'])==20


def test_ucsd_actual_choice_rows_and_source_loads_remain_distinct():
    d=seed(PID);by={r['id'].removeprefix(PID+'-'):r for r in d['requirements']};review=reviews()[0]
    mapping={'intro':'lower-core-0','tools':'lower-core-2','discrete':'lower-core-3','discrete2':'lower-core-4','lower4':'lower-elective','multivariable':'math-1','linear':'math-3','science':'science','probability':'probability','data_structures':'upper-core-0','AIcore':'upper-core-2','ethics':'ethics','AI12':'ai-electives'}
    assert len(review['reviewed_choice_groups'])==13
    for group,suffix in mapping.items():assert set(by[suffix]['course_ids'])==set(review['reviewed_choice_groups'][group])
    assert by['science']['count']==1 and by['science']['credits']==4
    assert by['ai-electives']['credits']==12 and by['cse-electives']['credits']==32
    assert all(by['breadth-'+tag]['credits']==8 for tag in ['systems','theory-abstraction','applications-of-computing'])
    assert by['open-electives']['credits']==8
    assert len(review['expected_course_ids']['options'])==119
    assert review['expected_profile']['options']['categories'] is None


def test_ucsb_closed_alias_core_and_bounded_field_subset():
    d=seed('ucsb-ai-bs');p=requirement_profile(d,include_course_ids=True);review=reviews()[1];rs={r['id']:r for r in d['requirements']}
    assert p['required']['count']==20 and p['required']['source_record_count']==21
    assert {'ucsb-cmpsc-181','ucsb-ece-181'}==set(rs['ucsb-ai-bs-ucsb-cmpsc-181']['course_ids'])
    assert rs['ucsb-ai-bs-ucsb-cmpsc-181']['kind']=='all'
    assert rs['ucsb-ai-bs-worksheet-field']['count']==9 and rs['ucsb-ai-bs-worksheet-field']['credits']==36
    assert len(review['reviewed_option_subset'])==37
    assert set(review['reviewed_option_subset'])<=set(p['course_ids']['options'])
    assert review['expected_profile']['options'] is None
    assert rs['ucsb-ai-bs-science-list-a']['credits']==8 and not rs['ucsb-ai-bs-science-list-a']['course_ids']
    assert rs['ucsb-ai-bs-science-list-b']['credits']==12 and not rs['ucsb-ai-bs-science-list-b']['course_ids']


def test_reciprocal_pair_deduplicates_only_explicit_source_identity():
    d=seed(PID);c={c['code']:c for c in d['courses']};p=requirement_profile(d)
    assert len(d['course_identity_groups'])==1
    assert set(d['course_identity_groups'][0]['course_ids'])=={'ucsd-sio-109','ucsd-poli-117'}
    assert c['POLI 117']['category_review']['status']==c['SIO 109']['category_review']['status']=='mixed'
    assert p['unresolved']['count']==2240 and p['unresolved']['source_record_count']==2241
    assert p['unresolved']['categories']['other']==396
    assert 'POLI 117R'not in c and 'SIO 109R'in c
    assert c['SIO 109']['prerequisites'] is None and 'upper-division' in c['POLI 117']['prerequisites']
    assert c['SIO 141']['description'] is None and c['SIO 141']['credits'] is None
    assert PID+'-chem-courses' in c['SIO 141']['category_review']['source_ids']
    assert 'ucsd-sio-141'not in d['course_identity_groups'][0]['course_ids']


def test_actual_cached_reciprocal_and_one_sided_source_evidence():
    from bs4 import BeautifulSoup
    paths={x:Path('/tmp/ucsd-'+x.lower()+'.html')for x in ['SIO','POLI','CHEM']}
    if not all(p.exists()for p in paths.values()):pytest.skip('Optional ignored official captures unavailable')
    def body(subject,code):
        soup=BeautifulSoup(paths[subject].read_text(),'html.parser')
        h=next((n for n in soup.select('p.course-name')if n.get_text(' ',strip=True).startswith(code+'.')),None)
        if h is None:return None
        parts=[]
        for n in h.next_siblings:
            if getattr(n,'name',None)in ['h1','h2','h3','h4']or'course-name'in getattr(n,'attrs',{}).get('class',[]):break
            if hasattr(n,'get_text'):parts.append(n.get_text(' ',strip=True))
        return ' '.join(parts)
    assert 'Cross-listed with POLI 117' in body('SIO','SIO 109')
    assert 'Same as SIO 109' in body('POLI','POLI 117')
    assert 'Cross-listed with POLI 117R' in body('SIO','SIO 109R')
    assert 'Cross-listed with SIO 109R' in body('POLI','POLI 117R')
    assert 'Cross-listed with SIO 141' in body('CHEM','CHEM 174')
    assert body('SIO','SIO 141')is None


def test_ucsb_independent_mixed_fixed_content_corrections():
    d=seed('ucsb-ai-bs');c={c['code']:c for c in d['courses']}
    for code,candidates in [('CMPSC 25',{'foundations','mathematics'}),('CMPSC 183',{'ai_ml','human_context'})]:
        assert c[code]['category']=='other'
        assert c[code]['category_review']['status']=='mixed'
        assert set(c[code]['category_review']['candidate_categories'])==candidates
    assert {k:v for k,v in requirement_profile(d)['required']['categories'].items() if v}=={'foundations':4,'mathematics':8,'ai_ml':6,'other':2}
