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
