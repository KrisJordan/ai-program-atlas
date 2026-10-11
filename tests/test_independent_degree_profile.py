"""Source-anchored second-pass examples; no keyword-based category inference."""
import json
import pytest
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
    return {**p,'courses':[c for c in p['courses'] if c['id']==cid], 'course_identity_groups':[]}


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
        assert sum(r[k]['count'] for k in ['required','options','unresolved']) == r['identity']['mapped_identities']
        assert sum(r[k]['source_record_count'] for k in ['required','options','unresolved']) == len({c['id'] for c in p['courses']})


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


def test_cmu_plain_required_math_singletons_are_not_optional_menus():
    p=load('cmu-bs-ai');profile=requirement_profile(p)
    expected={'foundations':4,'mathematics':4,'systems':1,'ai_ml':2,'human_context':1,'other':1}
    assert profile['required']['count']==13
    assert profile['required']['categories']=={k:expected.get(k,0) for k in profile['required']['categories']}
    for code in ['21-120','21-122','21-241','36-401']:
        assert requirement_profile(only_course(p,'cmu-'+code))['required']['count']==1
    assert requirement_profile(only_course(p,'cmu-15-112'))['unresolved']['count']==1
    for code in ['15-151','21-127']:
        assert requirement_profile(only_course(p,'cmu-'+code))['options']['count']==1
    assert next(c for c in p['courses'] if c['id']=='cmu-15-213')['category']=='systems'
    core = next(c for c in p['courses'] if c['id']=='cmu-99-101')
    assert core['category']=='human_context' and core['credits']==3
    assert core['category_review']['status']=='reviewed'


def test_rice_full_independent_inventory_preserves_manual_roles_and_crosslists():
    ledger = json.loads((ROOT/'research/degree-audit/independent-review.json').read_text())
    entry = next(e for e in ledger['programs'] if e['institution_id']=='rice-university')
    p = load(entry['program_id'])
    courses = {c['code']:c for c in p['courses']}
    assert len(entry['course_review']) == len(courses) == 43
    assert {r['code'] for r in entry['course_review']} == set(courses)
    for reviewed in entry['course_review']:
        course = courses[reviewed['code']]
        assert course['name'] == reviewed['title']
        assert course['category'] == reviewed['category']
        assert course['category_review']['status'] == reviewed['status']
        assert course['credits'] == reviewed['credits']
        assert course['credit_unit'] == reviewed['credit_unit']
        assert course['prerequisites'] == reviewed['prerequisites']
        profile = requirement_profile(only_course(p, course['id']))
        assert profile[reviewed['role']]['count'] == 1
        assert sum(profile[role]['count'] for role in ['required','options','unresolved']) == 1
    profile = requirement_profile(p)
    assert profile['identity'] == entry['expected_identity']
    for role in ['required','options','unresolved']:
        manual = entry['expected_profile'][role]
        assert profile[role]['count'] == manual['count']
        assert profile[role]['categories'] == {k:manual['categories'].get(k,0) for k in profile[role]['categories']}
    assert profile['required']['source_record_count'] == 13
    assert profile['options']['source_record_count'] == 30
    assert profile['options']['classification'] == dict(reviewed=24,mixed=2,unclassified=0,unreviewed=0)
    assert entry['second_pass_status']=='partial' and not entry['full_degree_verified']


def test_rice_rendered_required_chart_cannot_lose_reviewed_computing_foundations():
    from bs4 import BeautifulSoup
    from atlas.site import category_chart
    p = load('rice-university-artificial-intelligence-bs-degree')
    soup = BeautifulSoup(category_chart(p), 'html.parser')
    required = soup.select_one('[data-profile=required]')
    options = soup.select_one('[data-profile=options]')
    assert required.select_one('[data-category=foundations] strong').get_text() == '3'
    assert required.select_one('[data-category=systems] strong').get_text() == '2'
    assert '13 distinct' in required.select_one('.profile-total').get_text()
    assert '13 reviewed' in required.select_one('.profile-taxonomy').get_text()
    assert '26 distinct' in options.select_one('.profile-total').get_text()
    assert '30 retained source-code records' in options.get_text()


def test_northeastern_four_manual_sets_survive_family_resolution_and_rendering():
    from bs4 import BeautifulSoup
    from atlas.site import category_chart
    ledger = json.loads((ROOT/'research/degree-audit/independent-review.json').read_text())
    manual = ledger['northeastern_four_course_review']
    entries = [e for e in ledger['programs'] if e.get('course_review_reference')=='northeastern_four_course_review']
    assert len(entries)==4 and len(manual)==108
    assert sum(len(e['reviewed_course_codes']) for e in entries)==195
    for entry in entries:
        p = load(entry['program_id'])
        courses = {c['id']:c for c in p['courses']}
        observed = requirement_profile(p)
        chart = BeautifulSoup(category_chart(p), 'html.parser')
        assert set(courses)==set().union(*(set(ids) for ids in entry['expected_course_ids'].values()))
        for role,ids in entry['expected_course_ids'].items():
            expected = entry['expected_profile'][role]
            assert observed[role]['count']==expected['count']
            assert observed[role]['categories']=={k:expected['categories'].get(k,0) for k in observed[role]['categories']}
            assert observed[role]['classification']=={k:expected['classification'].get(k,0) for k in observed[role]['classification']}
            for cid in ids:
                course = courses[cid]
                source_review = manual[course['code']]
                assert course['name']==source_review['title']
                assert course['category']==source_review['category']
                assert course['category_review']['status']==source_review['status']
                assert requirement_profile(only_course(p,cid))[role]['count']==1
            if role!='unresolved':
                panel = chart.select_one(f'[data-profile={role}]')
                assert f"{expected['count']} distinct" in panel.select_one('.profile-total').get_text()
                for category,value in observed[role]['categories'].items():
                    assert panel.select_one(f'[data-category={category}] strong').get_text()==(str(value) if value else '0 mapped')
        assert observed['identity']['source_records']==len(courses)
        assert observed['identity']['mapped_identities']==len(courses)
        assert observed['identity']['crosslisted_aliases']==0
        assert all(observed[r]['classification']['unreviewed']==0 for r in ['required','options','unresolved'])
        assert not entry['full_degree_verified'] and entry['second_pass_status']=='partial'


def test_northeastern_role_overlays_corequisites_and_variable_hours_do_not_inflate_workload():
    journalism = load('northeastern-university-artificial-intelligence-and-journalism-bs-boston-bs-degree')
    courses = {c['code']:c for c in journalism['courses']}
    for code in ['CY 4170','JRNL 2301']:
        cid = courses[code]['id']
        assert len([r for r in journalism['requirements'] if cid in r.get('course_ids',[])])>1
        role = requirement_profile(only_course(journalism,cid))
        assert role['required']['count']==1 and role['options']['count']==0
    role = requirement_profile(only_course(journalism,courses['JRNL 3700']['id']))
    assert role['required']['count']==0 and role['options']['count']==1
    # Equivalent wording alone is not source proof of a cross-list identity.
    for code in ['DS 1300','PHIL 1300']:
        assert requirement_profile(only_course(journalism,courses[code]['id']))['options']['count']==1
    for code in ['CS 1800','CS 1802']:
        assert requirement_profile(only_course(journalism,courses[code]['id']))['required']['categories']['mathematics']==1
    speech = load('northeastern-university-artificial-intelligence-and-speech-language-pathology-and-audiology-bs-boston-bs-degree')
    course = next(c for c in speech['courses'] if c['code']=='SLPA 5107')
    assert course['credits'] is None
    assert any(r.get('credits')==4 and course['id'] in r.get('course_ids',[]) for r in speech['requirements'])
    assert next(c for c in speech['courses'] if c['code']=='SLPA 4219')['credits']==3


@pytest.mark.parametrize(('pid','record_count'), [
    ('northeastern-university-artificial-intelligence-and-economics-bs-boston-bs-degree',50),
    ('northeastern-chemical-engineering-ai-bsche',46),
    ('northeastern-university-artificial-intelligence-and-chemistry-bs-boston-bs-degree',56),
    ('northeastern-university-artificial-intelligence-and-biochemistry-bs-boston-bs-degree',54),
])
def test_northeastern_additional_full_manual_inventory_and_rendered_profile(pid,record_count):
    import hashlib
    from bs4 import BeautifulSoup
    from atlas.site import category_chart
    ledger = json.loads((ROOT/'research/degree-audit/independent-review.json').read_text())
    entry = next(e for e in ledger['programs'] if e['program_id']==pid)
    p = load(pid)
    courses = {c['code']:c for c in p['courses']}
    profile = requirement_profile(p)
    assert len(entry['course_review'])==len(courses)==record_count
    assert profile['identity']==entry['expected_identity']
    for source in entry['course_review']:
        c = courses[source['code']]
        assert (c['name'],c['category'],c['category_review']['status'],c['credits'],c['credit_unit']) == (
            source['title'],source['category'],source['status'],source['credits'],source['credit_unit'])
        assert (hashlib.sha256(c['prerequisites'].encode()).hexdigest() if c['prerequisites'] else None)==source['prerequisites_sha256']
        assert requirement_profile(only_course(p,c['id']))[source['role']]['count']==1
    chart = BeautifulSoup(category_chart(p), 'html.parser')
    for role in ['required','options','unresolved']:
        manual = entry['expected_profile'][role]
        assert profile[role]['count']==manual['count']
        assert profile[role]['categories']=={k:manual['categories'].get(k,0) for k in profile[role]['categories']}
        assert profile[role]['classification']=={k:manual['classification'].get(k,0) for k in profile[role]['classification']}
        assert set(entry['expected_course_ids'][role])=={courses[r['code']]['id'] for r in entry['course_review'] if r['role']==role}
        if role!='unresolved':
            panel = chart.select_one(f'[data-profile={role}]')
            assert f"{manual['count']} distinct" in panel.select_one('.profile-total').get_text()
            for key,value in profile[role]['categories'].items():
                assert panel.select_one(f'[data-category={key}] strong').get_text()==(str(value) if value else '0 mapped')
    assert entry['second_pass_status']=='partial' and not entry['full_degree_verified']


def test_northeastern_economics_calculus_choices_gpa_overlay_and_local_pool_scope():
    p = load('northeastern-university-artificial-intelligence-and-economics-bs-boston-bs-degree')
    courses = {c['code']:c for c in p['courses']}
    for code in ['MATH 1231','MATH 1241','MATH 1245','MATH 1340','MATH 1341']:
        profile = requirement_profile(only_course(p,courses[code]['id']))
        assert profile['required']['count']==0 and profile['options']['count']==1
    assert courses['MATH 1340']['credits']==6
    assert 'PHIL 1300' not in courses  # This degree's local social-issues menu differs.
    for code in ['ECON 2315','ECON 2316','ECON 2350','ECON 2560']:
        cid = courses[code]['id']
        assert len([r for r in p['requirements'] if cid in r.get('course_ids',[])])==2
        profile = requirement_profile(only_course(p,cid))
        assert profile['required']['count']==1 and profile['options']['count']==0
    gpa = next(r for r in p['requirements'] if r['id'].endswith('economics-gpa-requirement-policy'))
    assert 'average' in gpa['summary'] and '2.000' in gpa['summary']
    elective = next(r for r in p['requirements'] if r['id'].endswith('economics-electives-course-choice'))
    assert (elective['count'],elective['credits'],elective['credit_unit'])==(5,20,'semester_hours')
    assert 'no more than two' in elective['summary'] and 'cannot be counted as electives' in elective['summary']
    assert not elective['course_ids']  # Open ranges do not fabricate finite course members.
    for code in ['ECON 1115','ECON 1116','ECON 2315','ECON 2316']:
        assert courses[code]['category']=='human_context'
    for code in ['ECON 2350','ECON 2560']:
        assert courses[code]['category']=='mathematics'
    for code in ['ECON 4692','ECON 4997']:
        assert courses[code]['category_review']['status']=='unclassified'
        assert requirement_profile(only_course(p,courses[code]['id']))['options']['count']==1


def test_northeastern_chemical_engineering_preserves_pairs_zero_hours_and_entry_constraints():
    p = load('northeastern-chemical-engineering-ai-bsche')
    assert not p.get('family')
    courses = {c['code']:c for c in p['courses']}
    nodes = {r['id']:r for r in p['requirements']}
    pair = next(r for r in nodes.values() if r['id'].endswith('introductory-engineering-bundle'))
    assert pair['kind']=='alternative'
    children = [r for r in nodes.values() if r.get('parent_id')==pair['id']]
    assert len(children)==2 and all(r['kind']=='all' for r in children)
    assert {frozenset(r['course_ids']) for r in children}=={
        frozenset(courses[c]['id'] for c in ['GE 1501','GE 1502']),
        frozenset(courses[c]['id'] for c in ['GE 1110','GE 1111']),
    }
    for code in ['GE 1501','GE 1502','GE 1110','GE 1111']:
        profile = requirement_profile(only_course(p,courses[code]['id']))
        assert profile['required']['count']==0 and profile['options']['count']==1
    for code in ['CHME 3306','CHME 4705','CHEM 1153','MATH 3082']:
        assert courses[code]['credits']==0 and courses[code]['credit_unit']=='semester_hours'
        assert requirement_profile(only_course(p,courses[code]['id']))['required']['count']==1
    process = courses['CHME 4512']
    assert process['category']=='applications'  # Physical process control is not computing infrastructure.
    assert len([r for r in nodes.values() if process['id'] in r.get('course_ids',[])])==2
    assert requirement_profile(only_course(p,process['id']))['required']['count']==1
    # Retain the catalog option and the distinct lab prerequisite; do not invent a waiver.
    assert requirement_profile(only_course(p,courses['ENGW 3307']['id']))['options']['count']==1
    lab = courses['CHME 3305']['prerequisites']
    assert 'ENGW 3302' in lab and 'ENGW 3315' in lab and 'ENGW 3307' not in lab
    assert 'MATH 1341 or permission' in courses['MATH 1342']['prerequisites']
    assert not any('Khoury Approved Electives' in r['title'] for r in nodes.values())


@pytest.mark.parametrize('slug',['chemistry','biochemistry'])
def test_northeastern_chemistry_pair_preserves_elective_corequisite_ancestry(slug):
    p = load(f'northeastern-university-artificial-intelligence-and-{slug}-bs-boston-bs-degree')
    courses = {c['code']:c for c in p['courses']}
    nodes = {r['id']:r for r in p['requirements']}
    assert not {'CS 1800','CS 1802'} & set(courses)
    for code in ['MATH 1365','MATH 1465','EECE 2322','EECE 2323']:
        profile = requirement_profile(only_course(p,courses[code]['id']))
        assert profile['required']['count']==0 and profile['options']['count']==1
    lab = next(r for r in nodes.values() if courses['EECE 2323']['id'] in r.get('course_ids',[]))
    lecture = nodes[lab['parent_id']]
    choice = nodes[lecture['parent_id']]
    assert lab['kind']==lecture['kind']=='all'
    assert lecture['course_ids']==[courses['EECE 2322']['id']]
    assert choice['kind']=='choose_credits' and choice['credits']==4
    assert courses['EECE 2323']['credits']==1
    for code in ['ENVR 2500','ENVR 2501']:
        assert courses[code]['category']=='mathematics'  # R implements the statistical lab subject.
        role = 'required' if slug=='chemistry' else 'options'
        assert requirement_profile(only_course(p,courses[code]['id']))[role]['count']==1
    for code in ['CHEM 1163'] + (['CHEM 2163','CHEM 2323'] if slug=='chemistry' else []):
        assert courses[code]['credits']==0
        assert requirement_profile(only_course(p,courses[code]['id']))['required']['count']==1
    if slug=='chemistry':
        for code in ['CHEM 2324','CHEM 2325']:
            assert courses[code]['credits']==0
            assert requirement_profile(only_course(p,courses[code]['id']))['options']['count']==1
        assert courses['CHEM 2316']['credits']==courses['CHEM 2318']['credits']==2
        assert requirement_profile(only_course(p,courses['CHEM 4750']['id']))['required']['count']==1
    else:
        for code in ['MATH 3081','CHEM 3331','CHEM 3332','CHEM 5620','BINF 6310','BIOL 5591','BIOL 4701','CHEM 4750']:
            assert requirement_profile(only_course(p,courses[code]['id']))['options']['count']==1
        assert courses['CHEM 5620']['credits']==3
        assert courses['BINF 6310']['category_review']['status']=='mixed'
        assert 'BINF 6200 (may be taken concurrently)' in courses['BINF 6310']['prerequisites']
        assert 'DS 2500' in courses['BINF 6310']['prerequisites']
        assert 'BINF 6200' not in courses  # Conditional enrollment preparation is not fabricated degree workload.
