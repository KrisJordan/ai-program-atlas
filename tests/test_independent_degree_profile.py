"""Source-anchored second-pass examples; no keyword-based category inference."""
import json
from pathlib import Path

from atlas.curriculum_profile import requirement_profile
from atlas.families import resolve_program

ROOT=Path(__file__).resolve().parents[1]


def load(pid):
    p=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text())
    if p.get('family'):
        families=[json.loads(path.read_text()) for path in (ROOT/'data/families').glob('*.json')]
        f=next(f for f in families if f['id']==p['family']['id'])
        p=resolve_program(p,f)
    return p


def only_course(p,cid):
    """Isolate a known identity to test its graph role, independent of taxonomy."""
    return {**p,'courses':[c for c in p['courses'] if c['id']==cid]}


def test_case_manual_fixed_sets_and_intro_route_are_not_interchangeable():
    expected={'foundations':2,'mathematics':3,'ai_ml':3,'systems':0,'human_context':0,'applications':0,'electives':0,'other':0}
    for award in ['ba','bs']:
        p=load(f'case-western-reserve-university-artificial-intelligence-{award}-degree')
        fixed={f'case-{award}-{suffix}' for suffix in ['math-121','math-307','csds-233','csds-302','csds-310','csds-330','csds-340','csds-395a']}
        if award=='bs':fixed.add('case-bs-engr-399')
        r=requirement_profile(p)
        assert r['required']['count']==len(fixed)
        assert r['required']['categories']=={**expected,'human_context':int(award=='bs')}
        assert r['required']['classification']==dict(reviewed=len(fixed),mixed=0,unclassified=0,unreviewed=0)
        for cid in fixed:
            assert requirement_profile(only_course(p,cid))['required']['count']==1
        for code in ['132','134','237']:
            cid=f'case-{award}-csds-{code}'
            course=next(c for c in p['courses'] if c['id']==cid)
            assert course['category']=='foundations'
            role=requirement_profile(only_course(p,cid))
            assert role['required']['count']==0 and role['options']['count']==1
        # Quantities describe two alternative routes, never three mandatory courses.
        assert sum(r[k]['count'] for k in ['required','options','unresolved'])==len({c['id'] for c in p['courses']})


def test_cmu_and_penn_source_identified_data_structures_are_comparable_fixed_records():
    # CMU official CS core table and Penn Computing(5CUs), respectively.
    for pid,cid in [('cmu-bs-ai','cmu-15-210'),('penn-bse-ai','penn-cis-1210')]:
        p=load(pid);c=next(c for c in p['courses'] if c['id']==cid)
        assert c['category']=='foundations'
        assert 'Data Structures' in c['name']
        assert c['source_id'] in {s['id'] for s in p['sources']}
        assert requirement_profile(only_course(p,cid))['required']['count']==1
    # CMU's prior programming preparation stays contextual, not added to degree core.
    p=load('cmu-bs-ai')
    assert requirement_profile(only_course(p,'cmu-15-112'))['unresolved']['count']==1


def test_mit_conflicted_catalog_and_versioned_core_have_distinct_evidence_roles():
    p=load('mit-ai-decision-making-bs')
    versioned=only_course(p,'mit-ai-v2025-6-1210')
    assert requirement_profile(versioned)['required']['count']==1
    catalog=next(c for c in p['courses'] if c['code']=='6.1210' and c['id']!='mit-ai-v2025-6-1210')
    assert requirement_profile(only_course(p,catalog['id']))['unresolved']['count']==1
    # Same code in two source versions is not silently treated as an extra obligation.
    assert requirement_profile(only_course(p,catalog['id']))['required']['count']==0


def test_family_core_after_resolution_and_context_only_family_remain_distinct():
    pid='northeastern-university-artificial-intelligence-and-biology-bs-boston-bs-degree'
    p=load(pid)
    for code in ['cs-2000','cs-2001']:
        cid=pid+'-'+code
        assert requirement_profile(only_course(p,cid))['required']['count']==1
        assert any(r.get('origin')=='family' and cid in r['course_ids'] for r in p['requirements'])
    p=load('university-at-buffalo-suny-ai-and-policy-analysis-bs-degree')
    profile=requirement_profile(p)
    assert profile['required']['count']==0  # Source framework notes cannot invent a fixed core.
    assert profile['unresolved']['count']>0


def test_lehigh_explicit_fixed_and_options_match_independent_source_enumeration():
    ledger=json.loads((ROOT/'research/degree-audit/independent-review.json').read_text())
    entry=next(e for e in ledger['programs'] if e['program_id'].startswith('lehigh-'))
    p=load(entry['program_id']);expected=entry['expected_course_ids']
    assert len(expected['required'])==20 and len(expected['options'])==28
    for role,ids in expected.items():
        assert requirement_profile(p)[role]['count']==len(ids)
        for cid in ids:
            assert requirement_profile(only_course(p,cid))[role]['count']==1
    assert set(expected['required']).isdisjoint(expected['options'])
    assert set(expected['required'])|set(expected['options'])=={c['id'] for c in p['courses']}
    subjects={c['code']:c['category'] for c in p['courses']}
    assert subjects['CSE 027']=='foundations'  # Its AI title does not override software content.
    assert subjects['CSE 140']=='mathematics'
    assert subjects['CSE 211']=='systems'
    assert subjects['CSE 252']=='human_context'
    assert subjects['ISE 230']=='mathematics'
    assert subjects['ECE 303']=='other'


def test_northwestern_manual_fixed_set_excludes_oral_choice_menu():
    ledger=json.loads((ROOT/'research/degree-audit/independent-review.json').read_text())
    entry=next(e for e in ledger['programs'] if e['institution_id']=='northwestern-university')
    p=load(entry['program_id']);profile=requirement_profile(p)
    fixed=entry['expected_course_ids']['required']
    assert profile['required']['count']==14==len(fixed)
    expected=entry['expected_profile']['required']['categories']
    assert profile['required']['categories']=={k:expected.get(k,0) for k in profile['required']['categories']}
    for cid in fixed:
        assert requirement_profile(only_course(p,cid))['required']['count']==1
    for cid in entry['verified_option_subset']:
        role=requirement_profile(only_course(p,cid))
        assert role['required']['count']==0 and role['options']['count']==1
    half_units=[c for c in p['courses'] if c['id'] in fixed and c['code'].startswith(('DSGN','ENGLISH'))]
    assert len(half_units)==4 and sum(c['credits'] for c in half_units)==2


def test_northeastern_source_reviewed_subjects_survive_family_resolution():
    # Official CS/DS descriptions establish subjects independently of family/pool role.
    expected={'CS 2000':'foundations','CS 2001':'foundations','CS 2100':'foundations',
              'CS 3200':'systems','DS 3000':'mathematics','DS 3500':'foundations',
              'DS 4200':'other','DS 4300':'systems'}
    for variant in ['biology','design']:
        p=load(f'northeastern-university-artificial-intelligence-and-{variant}-bs-boston-bs-degree')
        courses={c['code']:c for c in p['courses']}
        for code,category in expected.items():
            c=courses[code]
            assert c['category']==category
            assert c['category_review']['status']==('mixed' if code=='DS 4200' else 'reviewed')
            assert c['category_review']['source_ids']
            role=requirement_profile(only_course(p,c['id']))
            assert sum(role[k]['count'] for k in ['required','options','unresolved'])==1


def test_rice_manual_fixed_subjects_preserve_infrastructure_and_domain_distinctions():
    ledger=json.loads((ROOT/'research/degree-audit/independent-review.json').read_text())
    entry=next(e for e in ledger['programs'] if e['institution_id']=='rice-university')
    p=load(entry['program_id']);profile=requirement_profile(p)
    assert profile['required']['count']==13
    expected=entry['expected_profile']['required']['categories']
    assert profile['required']['categories']=={k:expected.get(k,0) for k in profile['required']['categories']}
    assert profile['required']['classification']==dict(reviewed=13,mixed=0,unclassified=0,unreviewed=0)
    for cid in entry['expected_course_ids']['required']:
        assert requirement_profile(only_course(p,cid))['required']['count']==1
    courses={c['code']:c for c in p['courses']}
    assert courses['COMP 329']['category']=='systems'
    assert courses['COMP 282']['category']=='mathematics'
    assert courses['PSYC 203']['category']=='applications'
    for code in ['COMP 447','COMP 585','COMP 631']:
        assert requirement_profile(only_course(p,courses[code]['id']))['required']['count']==0
    timing=[r for r in p['requirements'] if 'same academic year' in (r.get('summary') or '')]
    assert len(timing)==1 and timing[0]['kind']=='note' and not timing[0]['course_ids']


def test_penn_state_fixed_subjects_and_degree_specific_programming_roles():
    for pid,count in [('penn-state-ai-engineering-bs',17),('penn-state-ai-methods-applications-ist-bs',9)]:
        p=load(pid);r=requirement_profile(p)
        assert r['required']['count']==count
        courses={c['code']:c for c in p['courses']}
        for code,category in {'A-I 341W':'human_context','A-I 370':'ai_ml','MATH 225':'mathematics','STAT 401':'mathematics'}.items():
            assert courses[code]['category']==category
            assert courses[code]['category_review']['status']=='reviewed'
        programming=requirement_profile(only_course(p,courses['CMPSC 132']['id']))
        assert programming['required' if count==9 else 'options']['count']==1
        # Actual enrollment metadata must survive without manufacturing extra fixed courses.
        assert 'DS 305' in courses['A-I 370']['prerequisites']
        assert 'CMPSC 465' in courses['A-I 370']['prerequisites']
    p=load('penn-state-ai-engineering-bs');courses={c['code']:c for c in p['courses']}
    assert courses['A-I 305']['category']=='foundations'
    assert courses['A-I 410']['category']=='systems'
    assert courses['AIE 355']['category']=='mathematics'
    assert courses['PHYS 211']['category']=='applications'


def test_rit_actual_zero_credits_and_context_do_not_create_elective_memberships():
    p=load('rochester-institute-of-technology-artificial-intelligence-bs-degree')
    courses={c['code']:c for c in p['courses']};r=requirement_profile(p)
    assert [r[k]['count'] for k in ['required','options','unresolved']]==[23,17,3]
    for code in ['YOPS-10','IDAI-499']:
        assert courses[code]['credits']==0
        assert courses[code]['credit_unit']=='semester_hours'
        assert requirement_profile(only_course(p,courses[code]['id']))['required']['count']==1
        rows=[g for g in p['requirements'] if courses[code]['id'] in g['course_ids']]
        assert any(g['credits']==0 for g in rows)
    prep=[g for g in p['requirements'] if 'Co-op preparation' in g['title'] or 'Co-Op Preparation' in g['title']]
    assert prep and all(g['credits']==0 and not g['course_ids'] for g in prep)
    for code,subject in {'IDAI-360':'mathematics','IDAI-485':'systems','IDAI-490':'foundations'}.items():
        assert courses[code]['category']==subject
    for code in ['CSCI-431','SWEN-566','PUBL-550']:
        cid=courses[code]['id']
        for g in p['requirements']:
            if any(term in g['title'].lower() for term in ['global perspective','immersion','wellness','open elective']):
                assert cid not in g['course_ids']
