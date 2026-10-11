"""Source-backed category decisions must not become broad automatic heuristics."""
import json
from pathlib import Path
from importlib import import_module

import pytest

from atlas.adapters.northeastern_courseleaf import CATEGORY_DECISIONS, category
from atlas.adapters.northeastern_course_metadata import parse_subject

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('code,expected', [
    ('CS 1800','mathematics'), ('DS 3000','mathematics'), ('CS 4120','ai_ml'),
    ('CY 4170','human_context'), ('CY 5240','human_context'), ('DS 1300','human_context'),
    ('ECON 1115','human_context'), ('ECON 2350','mathematics'), ('ECON 2560','mathematics'),
    ('CS 1200','other'), ('CS 1210','other'), ('CS 4991','other'), ('DS 4200','other'),
])
def test_individual_decisions_follow_reviewed_content(code,expected):
    decision = CATEGORY_DECISIONS[code]
    assert category(code, decision['name'], decision['guard']) == expected
    assert category(code, 'Changed Course Identity', decision['guard']) == 'other'
    assert category(code, decision['name'], 'Entirely different description') == 'other'


@pytest.mark.parametrize('code,title', [('ECON 9999','Economics'),('MATH 9999','Orientation'),
    ('CS 9999','Artificial Intelligence'),('DS 9999','Machine Learning'),('PHIL 9999','Ethics')])
def test_unknown_identity_is_not_classified_by_prefix_or_title_keyword(code,title):
    assert category(code,title) == 'other'


def test_changed_description_has_no_review_and_no_stale_category():
    html = '''<header id="site-title"><h1>Data Science (DS)</h1></header>
    <div id="textcontainer"><div class="courseblock"><p class="courseblocktitle">
    DS 3000. Mathematical Foundations of Artificial Intelligence. (4 Hours)</p>
    <p class="cb_desc">New unrelated material.</p></div></div>'''
    d = parse_subject(html,program_id='synthetic',subject='DS',heading='Data Science (DS)',
                      codes=['DS 3000'],url='https://catalog.northeastern.edu/course-descriptions/ds/')
    assert d['courses'][0]['category'] == 'other'
    assert 'category_review' not in d['courses'][0]


def test_minimum_credit_wording_is_preserved_without_fixing_an_exact_course_count():
    from test_northeastern_curriculum import document, row, parse
    html = document('<tr><td>Complete a minimum of 16 semester hours of general electives.</td><td class="hourscol">16</td></tr>' + row('CS 9999','Synthetic Subject'))
    d = parse(html)
    choice = next(r for r in d['requirements'] if r['kind'] == 'choose_credits')
    assert choice['credits'] == 16 and choice['count'] is None
    assert 'minimum' in choice['summary']
    with pytest.raises(ValueError,match='Conflicting credit'):
        parse(html.replace('minimum of 16','minimum of 12'))


def test_each_degree_has_individual_audit_entry_and_registered_category_evidence():
    ledger = json.loads((ROOT/'research/degree-audit/northeastern.json').read_text())
    entries = {r['program_id']:r for r in ledger['programs']}
    degrees = [json.loads(p.read_text()) for p in (ROOT/'data/programs').glob('northeastern*.json')]
    degrees = [p for p in degrees if p['program_kind'] == 'degree']
    assert len(degrees) == len(entries) == 24
    for program in degrees:
        entry = entries[program['id']]
        assert entry['status'] in {'in_progress','blocked','audited'}
        assert entry['sources'] and len(entry['checks']) == 8
        source_ids = {s['id'] for s in program['sources']}
        for c in program['courses']:
            review = c.get('category_review')
            if not review:
                continue
            assert set(review['source_ids']) <= source_ids
            decision = CATEGORY_DECISIONS[c['code']]
            assert c['name'] == decision['name'] and c['category'] == decision['category']
            assert review['rationale'] == decision['rationale']
            assert review['status'] == decision['status']
            if review['status'] in {'mixed','unclassified'}:
                assert c['category'] == 'other'


def test_optional_communication_catalog_minimum_phrase_replays():
    pid='northeastern-university-artificial-intelligence-and-communication-studies-bs-boston-bs-degree'
    file=ROOT/'.cache/research/degree-audit-northeastern'/f'{pid}.html'
    if not file.exists():pytest.skip('Optional official catalog cache')
    parsed=import_module('atlas.adapters.'+pid+'.adapter').parse(file.read_text())
    node=next(r for r in parsed['requirements'] if r['id']==pid+'-req-required-general-electives-credit-choice')
    assert node['credits']==16 and node['kind']=='choose_credits'


def test_engineering_substitution_is_two_complete_bundles_not_four_fixed_courses():
    from test_confirmed_depth4 import ne
    from atlas.curriculum_profile import requirement_profile
    pid='northeastern-chemical-engineering-ai-bsche'
    module=import_module('atlas.adapters.'+pid+'.adapter')
    parsed=module.parse(ne())
    profile=requirement_profile(parsed)
    assert profile['required']['count']==2  # Synthetic CHME 4512 and CS 1800.
    assert profile['options']['count']==4
    bundles=[r for r in parsed['requirements'] if r['parent_id']==pid+'-req-introductory-engineering-bundle']
    assert {tuple(c.rsplit('-ge-',1)[1] for c in r['course_ids']) for r in bundles}=={('1501','1502'),('1110','1111')}
    assert all(r['kind']=='all' for r in bundles)
    allocations=[r for r in parsed['requirements'] if r['id'].startswith(pid+'-req-ge-150')]
    assert len(allocations)==5 and all(r['kind']=='note' for r in allocations)
    with pytest.raises(ValueError,match='substitution'):
        module.parse(ne().replace('Students can substitute','Students cannot substitute'))
    with pytest.raises(ValueError,match='substitution'):
        module.parse(ne().replace('Computation (GE 1111)','Computation (GE 1112)'))


def test_engineering_reviewed_seed_has_no_fixed_cornerstone_override():
    from atlas.curriculum_profile import requirement_profile
    pid='northeastern-chemical-engineering-ai-bsche'
    seed=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text())
    # Independent delta: original 40 fixed minus the two substituted GE
    # identities plus the independently verified concurrent CS 1802 seminar;
    # three writing options plus all four engineering identities.
    profile=requirement_profile(seed)
    assert profile['required']['count']==39
    assert profile['options']['count']==7
    assert profile['unresolved']['count']==0
    assert len(seed['courses'])==46
    for code in ['GE 1110','GE 1111']:
        c=next(c for c in seed['courses'] if c['code']==code)
        assert c['credits']==4 and c['credit_unit']=='semester_hours'
        assert c['category_review']['status']=='reviewed'


def cs_concurrency_document():
    return '<div id="site-title"><h1>Computer Science (CS)</h1></div><div id="textcontainer">'+''.join(
        '<div class="courseblock"><p class="courseblocktitle">'+code+'. '+name+'. ('+hours+' Hour'+('s' if hours!='1' else '')+')</p>'
        '<p class="cb_desc">'+description+'</p><p class="courseblockextra">Corequisite(s): '+concurrent+'</p></div>'
        for code,name,hours,description,concurrent in [
            ('CS 1800','Discrete Structures','4','Studies discrete mathematical structures.','CS 1802'),
            ('CS 1802','Seminar for CS 1800','1','Accompanies CS 1800 through discussion.','CS 1800')])+'</div>'


def test_concurrent_seminar_observer_requires_reciprocal_evidence_and_never_emits_review():
    from atlas.adapters.northeastern_corequisites import observe_cs1802
    def base(html):
        return parse_subject(html,program_id='test',subject='CS',heading='Computer Science (CS)',
                             codes=['CS 1800'],url='https://catalog.northeastern.edu/course-descriptions/cs/')
    result=observe_cs1802(cs_concurrency_document(),'test',base)
    rule=result['requirements'][0]
    assert rule['parent_id']=='test-req-cs-1800' and rule['course_ids']==['test-cs-1802']
    assert rule['credits']==1 and rule['source_id']=='test-cs-courses'
    assert all('category_review' not in c for c in result['courses'])
    for before,after in [('Corequisite(s): CS 1802','Prerequisite(s): CS 1802'),
                         ('Corequisite(s): CS 1800','Corequisite(s): CS 9999'),
                         ('Seminar for CS 1800','Unrelated seminar'),('(1 Hour)','(2 Hours)')]:
        with pytest.raises(ValueError):
            observe_cs1802(cs_concurrency_document().replace(before,after),'test',base)


def test_degree_concurrency_guard_rejects_missing_policy_and_conditional_ancestry():
    from atlas.adapters.northeastern_corequisites import guard_degree
    policy='<div id="programrequirementstextcontainer">Also complete any corequisite labs, recitations, clinicals, or tools courses where specified</div>'
    def observer(kind):
        return lambda html: dict(requirements=[
            dict(id='root',parent_id=None,kind=kind,course_ids=[]),
            dict(id='test-req-cs-1800',parent_id='root',kind='all',course_ids=['test-cs-1800'])])
    assert guard_degree(observer('all'),'test')(policy)
    for kind in ['alternative','choose_courses','choose_credits','note']:
        with pytest.raises(ValueError,match='conditional ancestry'):
            guard_degree(observer(kind),'test')(policy)
    with pytest.raises(ValueError,match='applicability'):
        guard_degree(observer('all'),'test')(policy.replace('Also complete','Optionally take'))


def test_exact_fourteen_degree_seminars_inherit_existing_fixed_parent():
    from atlas.families import resolve_program
    families={x['id']:x for p in (ROOT/'data/families').glob('*.json') for x in [json.loads(p.read_text())]}
    affected=[]
    for path in (ROOT/'data/programs').glob('northeastern*.json'):
        program=json.loads(path.read_text())
        if not any(c['code']=='CS 1800' for c in program['courses']):continue
        affected.append(program['id'])
        resolved=resolve_program(program,families.get(program.get('family',{}).get('id')))
        groups={r['id']:r for r in resolved['requirements']}
        node=groups[program['id']+'-req-cs-1802-concurrent']
        assert node['parent_id']==program['id']+'-req-cs-1800'
        while node:
            assert node['kind']=='all'
            node=groups.get(node['parent_id']) if node.get('parent_id') else None
        course=next(c for c in program['courses'] if c['code']=='CS 1802')
        assert course['credits']==1 and course['category']=='mathematics'
        assert course['category_review']['status']=='reviewed'
    assert len(affected)==14


def test_optional_reviewed_live_degree_and_cs_sources_reconstruct_concurrent_children():
    cache=ROOT/'.cache/research/degree-audit-northeastern'
    if not (cache/'cs.html').exists():pytest.skip('Optional official CS source cache')
    count=0
    for path in (ROOT/'data/programs').glob('northeastern*.json'):
        p=json.loads(path.read_text())
        if not any(c['code']=='CS 1802' for c in p['courses']):continue
        source=cache/(p['id']+'.html')
        if not source.exists():pytest.skip('Optional official degree source cache')
        m=import_module('atlas.adapters.'+p['id']+'.adapter')
        degree=m.parse(source.read_text())
        assert any(r['id']==p['id']+'-req-cs-1800' for r in degree['requirements'])
        observed=m.SOURCE_PARSERS['https://catalog.northeastern.edu/course-descriptions/cs/']((cache/'cs.html').read_text())
        assert all(r in p['requirements'] for r in observed['requirements'])
        course=next(c for c in observed['courses'] if c['code']=='CS 1802')
        reviewed=next(c for c in p['courses'] if c['code']=='CS 1802')
        assert course=={k:v for k,v in reviewed.items() if k!='category_review'}
        count+=1
    assert count==14


@pytest.mark.parametrize('code,expected', [
    ('ENGW 1111','human_context'),('ENGW 3302','human_context'),('ENGW 3304','human_context'),
    ('ENGW 3307','human_context'),('PHYS 1151','applications'),('PHYS 1163','applications'),
    ('PHYS 1191','applications'),('PHYS 4115','applications'),('PHYS 5116','mathematics')])
def test_writing_and_physics_content_categories_are_identity_guarded(code,expected):
    d=CATEGORY_DECISIONS[code]
    assert category(code,d['name'],d['guard'])==expected
    assert category(code,d['name'],'New topic without the reviewed content')=='other'
    assert category(code,'Unrelated course with the same code',d['guard'])=='other'
    assert d['rationale'] and d['url'].startswith('https://catalog.northeastern.edu/course-descriptions/')


def test_zero_hour_physics_recitations_remain_distinct_domain_observations():
    pid='northeastern-university-artificial-intelligence-and-physics-bs-boston-bs-degree'
    p=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text())
    found=[]
    for c in p['courses']:
        if c['code'] not in ['PHYS 1163','PHYS 1167','PHYS 1193']:continue
        found.append(c['code'])
        assert c['credits']==0 and c['credit_unit']=='semester_hours'
        assert c['category']=='applications' and c['category_review']['status']=='reviewed'
    assert set(found)=={'PHYS 1163','PHYS 1167','PHYS 1193'}


@pytest.mark.parametrize('code,expected,status', [
    ('BIOL 2329','human_context','reviewed'),('BIOL 2407','applications','reviewed'),
    ('BIOL 3405','applications','reviewed'),('BIOL 4709','applications','reviewed'),
    ('BIOL 5595','applications','reviewed'),('BIOL 5601','applications','reviewed'),
    ('BIOL 4701','other','mixed'),('BIOL 4991','other','unclassified'),
    ('BIOL 4994','other','unclassified'),('CHEM 2321','applications','reviewed'),
    ('CHEM 4750','other','unclassified')])
def test_biological_learning_is_not_ai_and_unspecified_research_is_not_inherited(code,expected,status):
    decision=CATEGORY_DECISIONS[code]
    assert decision['status']==status
    assert category(code,decision['name'],decision['guard'])==expected
    assert category(code,decision['name'],'Different undocumented research subject')=='other'
    if status=='mixed':assert decision['candidate_categories']==['applications','human_context']
    if status=='unclassified':assert decision['candidate_categories']==[]


def test_independently_transcribed_named_course_roles_match_current_four_degree_graphs():
    from atlas.families import resolve_program
    from atlas.curriculum_profile import requirement_profile
    ledger=json.loads((ROOT/'research/degree-audit/northeastern.json').read_text())
    families={x['id']:x for p in (ROOT/'data/families').glob('*.json') for x in [json.loads(p.read_text())]}
    checked=0
    for entry in ledger['programs']:
        sets=entry.get('expected_course_ids')
        if sets is None:continue
        seed=json.loads((ROOT/'data/programs'/f"{entry['program_id']}.json").read_text())
        program=resolve_program(seed,families.get(seed.get('family',{}).get('id')))
        lookup={c['id']:c for c in program['courses']}
        assert set(lookup)==set().union(*(set(v) for v in sets.values()))
        assert sum(map(len,sets.values()))==len(lookup)
        for role,ids in sets.items():
            for cid in ids:
                # The source-transcribed expected identity sets are independent
                # inputs; ask the actual public algorithm for that identity's role.
                singleton={**program,'courses':[lookup[cid]]}
                assert requirement_profile(singleton)[role]['count']==1,(entry['program_id'],cid,role)
        checked+=1
    assert checked>=4


@pytest.mark.parametrize('code,expected,status', [
    ('EECE 2160','other','mixed'),('EECE 2322','systems','reviewed'),('EECE 2323','systems','reviewed'),
    ('INSH 3102','mathematics','reviewed'),('SOCL 2320','mathematics','reviewed'),
    ('INSH 3101','human_context','reviewed'),('SOCL 2321','human_context','reviewed'),
    ('SOCL 4528','human_context','reviewed'),('MKTG 4606','applications','reviewed'),
    ('SOCL 4600','other','unclassified'),('INPR 1000','other','unclassified')])
def test_individual_sociology_and_partner_content_does_not_follow_ai_degree_or_robotics_name(code,expected,status):
    d=CATEGORY_DECISIONS[code]
    assert d['status']==status and category(code,d['name'],d['guard'])==expected
    assert category(code,d['name'],'Different content without reviewed evidence')=='other'
    if code=='EECE 2160':assert d['candidate_categories']==['systems','foundations','applications']


def test_sociology_manual_profile_has_no_unread_classifications_or_hidden_course_ids():
    from atlas.families import resolve_program
    from atlas.curriculum_profile import requirement_profile
    pid='northeastern-university-artificial-intelligence-and-sociology-bs-boston-bs-degree'
    p=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text());f=json.loads((ROOT/'data/families/northeastern-ai-combined-degrees.json').read_text())
    entry=next(e for e in json.loads((ROOT/'research/degree-audit/northeastern.json').read_text())['programs'] if e['program_id']==pid)
    assert len(p['courses'])==37 and all(c.get('category_review') for c in p['courses'])
    actual=requirement_profile(resolve_program(p,f))
    for role in ['required','options','unresolved']:
        assert actual[role]['count']==entry['expected_profile'][role]['count']
        assert actual[role]['categories']==entry['expected_profile'][role]['categories']
        assert actual[role]['classification']['unreviewed']==0
    assert entry['blockers']  # Exact home-college applicability, not unknown dates/resources.


@pytest.mark.parametrize('code,expected,status', [
    ('HLTH 1000','other','unclassified'),('SLPA 2000','other','unclassified'),
    ('PHIL 1145','human_context','reviewed'),('PHTH 2210','mathematics','reviewed'),
    ('SLPA 1101','applications','reviewed'),('SLPA 4219','applications','reviewed'),
    ('SLPA 5107','applications','reviewed')])
def test_speech_clinical_content_and_orientation_have_separate_reviewed_categories(code,expected,status):
    decision=CATEGORY_DECISIONS[code]
    assert decision['status']==status
    assert category(code,decision['name'],decision['guard'])==expected
    assert category(code,'Different identity',decision['guard'])=='other'
    assert category(code,decision['name'],'Changed content without reviewed evidence')=='other'


def test_speech_manual_profile_and_variable_offering_hours_remain_separate():
    from atlas.families import resolve_program
    from atlas.curriculum_profile import requirement_profile
    pid='northeastern-university-artificial-intelligence-and-speech-language-pathology-and-audiology-bs-boston-bs-degree'
    program=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text())
    family=json.loads((ROOT/'data/families/northeastern-ai-combined-degrees.json').read_text())
    entry=next(e for e in json.loads((ROOT/'research/degree-audit/northeastern.json').read_text())['programs'] if e['program_id']==pid)
    assert len(program['courses'])==44 and all(c.get('category_review') for c in program['courses'])
    actual=requirement_profile(resolve_program(program,family))
    for role in ['required','options','unresolved']:
        assert actual[role]['count']==entry['expected_profile'][role]['count']
        assert actual[role]['categories']==entry['expected_profile'][role]['categories']
        assert actual[role]['classification']['unreviewed']==0
    course=next(c for c in program['courses'] if c['code']=='SLPA 5107')
    assert course['credits'] is None
    rows=[r for r in program['requirements'] if course['id'] in r.get('course_ids',[])]
    assert any(r['credits']==4 and r['kind']=='all' for r in rows)
    assert next(c for c in program['courses'] if c['code']=='SLPA 4219')['credits']==3
    assert entry['status'] in {'in_progress','blocked'} and entry['blockers']
    if entry['status']=='in_progress':assert 'accessible conditional' in entry['checks']['degree_wide_requirements']


@pytest.mark.parametrize('code,expected,status', [
    ('CRIM 2370','human_context','reviewed'),('CRIM 3600','human_context','reviewed'),
    ('CRIM 3700','mathematics','reviewed'),('CRIM 3040','applications','reviewed'),
    ('CRIM 3540','other','mixed'),('CRIM 4949','human_context','reviewed'),
    ('PHIL 1300','human_context','reviewed'),('JRNL 3700','human_context','reviewed'),
    ('JRNL 5500','foundations','reviewed'),('JRNL 1102','human_context','reviewed'),
    ('JRNL 1000','other','unclassified'),('EEAM 2000','other','unclassified')])
def test_criminology_and_journalism_categories_follow_individual_content(code,expected,status):
    d=CATEGORY_DECISIONS[code]
    assert d['status']==status and category(code,d['name'],d['guard'])==expected
    assert category(code,d['name'],'Changed subject without the reviewed descriptive evidence')=='other'
    assert category(code,'Another course title',d['guard'])=='other'
    if code=='CRIM 3540':assert d['candidate_categories']==['human_context','applications']


@pytest.mark.parametrize('subject,size,fixed,options', [('criminal-justice',68,19,49),('journalism',46,25,21)])
def test_criminal_and_journalism_independent_profiles_have_no_unread_records(subject,size,fixed,options):
    from atlas.families import resolve_program
    from atlas.curriculum_profile import requirement_profile
    pid=f'northeastern-university-artificial-intelligence-and-{subject}-bs-boston-bs-degree'
    p=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text())
    f=json.loads((ROOT/'data/families/northeastern-ai-combined-degrees.json').read_text())
    e=next(e for e in json.loads((ROOT/'research/degree-audit/northeastern.json').read_text())['programs'] if e['program_id']==pid)
    assert len(p['courses'])==size and all(c.get('category_review') for c in p['courses'])
    profile=requirement_profile(resolve_program(p,f))
    assert profile['required']['count']==fixed and profile['options']['count']==options
    for role in ['required','options','unresolved']:
        assert profile[role]['count']==e['expected_profile'][role]['count']
        assert profile[role]['categories']==e['expected_profile'][role]['categories']
        assert profile[role]['classification']['unreviewed']==0
    if subject=='journalism':
        assert next(c for c in p['courses'] if c['code']=='JRNL 1102')['credits']==1
        assert next(c for c in p['courses'] if c['code']=='JRNL 5500')['category']=='foundations'
    assert e['status'] in {'in_progress','blocked'} and e['blockers']
    if e['status']=='in_progress':assert 'accessible conditional' in e['checks']['degree_wide_requirements']


@pytest.mark.parametrize('subject,size,fixed,options', [('economics',50,18,32),('mathematics',34,20,14),('physics',49,25,24)])
def test_economics_math_physics_manual_role_and_category_partitions(subject,size,fixed,options):
    from atlas.families import resolve_program
    from atlas.curriculum_profile import requirement_profile
    pid=f'northeastern-university-artificial-intelligence-and-{subject}-bs-boston-bs-degree'
    p=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text())
    f=json.loads((ROOT/'data/families/northeastern-ai-combined-degrees.json').read_text())
    e=next(e for e in json.loads((ROOT/'research/degree-audit/northeastern.json').read_text())['programs'] if e['program_id']==pid)
    assert len(p['courses'])==size and all(c.get('category_review') for c in p['courses'])
    profile=requirement_profile(resolve_program(p,f))
    assert profile['required']['count']==fixed and profile['options']['count']==options
    for role in ['required','options','unresolved']:
        assert profile[role]['count']==e['expected_profile'][role]['count']
        assert profile[role]['categories']==e['expected_profile'][role]['categories']
        assert profile[role]['classification']['unreviewed']==0
    bycode={c['code']:c for c in p['courses']}
    if subject in ['mathematics','physics']:
        assert 'CS 1800' not in bycode and 'CS 1802' not in bycode
        assert bycode['INSC 1000']['category_review']['status']=='unclassified'
        assert bycode['EESC 2000']['category_review']['status']=='unclassified'
    if subject=='physics':
        for code in ['PHYS 1163','PHYS 1193']:
            assert bycode[code]['id'] in e['expected_course_ids']['options']
            assert bycode[code]['credits']==0
        assert bycode['PHYS 1167']['id'] in e['expected_course_ids']['required']
        assert bycode['PHYS 1167']['credits']==0
    if subject=='economics':
        assert bycode['ECON 4692']['id'] in e['expected_course_ids']['options']
        assert bycode['ECON 4997']['id'] in e['expected_course_ids']['options']
        assert 'ECON 2990' not in bycode and 'ECON 4996' not in bycode


@pytest.mark.parametrize('code,expected', [
    ('LING 1150','applications'), ('LING 2350','applications'),
    ('LING 3412','human_context'), ('LING 3422','applications'),
    ('LING 3424','applications'), ('LING 3450','applications'),
    ('PSYC 1101','applications'), ('PSYC 2320','mathematics'),
    ('PSYC 4610','applications'), ('PSYC 4658','applications'),
    ('DEAF 2700','applications'), ('LING 4654','other'),
    ('LING 4891','other'), ('LING 4991','other'),
])
def test_linguistics_decisions_do_not_confuse_language_structure_with_computing(code,expected):
    decision=CATEGORY_DECISIONS[code]
    assert category(code,decision['name'],decision['guard'])==expected
    assert category(code,decision['name'],'Different current topic')=='other'
    assert category(code,'Different identity',decision['guard'])=='other'


def test_linguistics_named_options_preserve_eligibility_and_nonreuse_scope():
    from atlas.families import resolve_program
    from atlas.curriculum_profile import requirement_profile
    pid='northeastern-university-artificial-intelligence-and-linguistics-bs-boston-bs-degree'
    seed=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text())
    family=json.loads((ROOT/'data/families'/f"{seed['family']['id']}.json").read_text())
    resolved=resolve_program(seed,family)
    profile=requirement_profile(resolved)
    assert profile['required']['count']==18 and profile['options']['count']==27
    assert profile['unresolved']['count']==0
    courses={c['code']:c for c in seed['courses']}
    assert all('category_review' in c for c in courses.values())
    assert 'PSYC 3464' in courses['PSYC 4610']['prerequisites']
    assert 'AMSL 1102' in courses['DEAF 2700']['prerequisites']
    assert 'PSYC 3464' not in courses and 'AMSL 1102' not in courses
    assert 'CS 1800' not in courses and 'CS 1802' not in courses
    assert courses['LING 4891']['category_review']['status']=='unclassified'
    assert courses['PSYC 4658']['category_review']['status']=='reviewed'
    rules=resolved['requirements']
    assert any('not used to fulfill other degree requirements' in r['summary'] for r in rules)
    assert any(r['kind']=='choose_courses' and r['count']==4 for r in rules)


@pytest.mark.parametrize('code,expected,status', [('ENVR 2500','mathematics','reviewed'),('ENVR 2501','mathematics','reviewed'),('BIOC 1000','other','unclassified'),('BINF 6310','other','mixed')])
def test_science_statistics_and_bioinformatics_content_scope(code,expected,status):
    d=CATEGORY_DECISIONS[code]
    assert d['status']==status
    assert category(code,d['name'],d['guard'])==expected
    assert category(code,d['name'],'New subject content')=='other'
    if code=='BINF 6310':assert set(d['candidate_categories'])=={'foundations','applications'}


@pytest.mark.parametrize('code,expected', [('ENVR 2502','mathematics'),('HSCI 1000','other'),('HSCI 2000','other'),('PHTH 1260','human_context'),('PHTH 1261','human_context'),('PHTH 2300','human_context'),('PHTH 2350','applications'),('PHTH 2515','human_context'),('PHTH 4120','human_context'),('PHTH 4202','applications'),('PHTH 4540','applications'),('PHIL 1165','human_context')])
def test_health_context_does_not_override_actual_content(code,expected):
    d=CATEGORY_DECISIONS[code]
    assert category(code,d['name'],d['guard'])==expected
    assert category(code,'New identity',d['guard'])=='other'
    assert category(code,d['name'],'Entirely different course content')=='other'


def test_health_science_manual_roles_preserve_statistics_bundle_and_recommendations():
    from atlas.families import resolve_program
    from atlas.curriculum_profile import requirement_profile
    pid='northeastern-university-artificial-intelligence-and-health-science-bs-boston-bs-degree'
    p=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text())
    f=json.loads((ROOT/'data/families/northeastern-ai-combined-degrees.json').read_text())
    result=requirement_profile(resolve_program(p,f));cs={c['code']:c for c in p['courses']}
    assert result['required']['count']==26 and result['options']['count']==26 and result['unresolved']['count']==0
    assert all('category_review' in c for c in cs.values())
    assert cs['ENVR 2502']['credits']==0
    assert cs['PHTH 2350']['prerequisites'] is None
    assert 'PHTH 2300' not in (cs['PHTH 4540']['prerequisites'] or '')
    assert 'ENGW 3302' in cs['PHTH 4540']['prerequisites']
    assert any('recommended' in n and 'PHTH 2350' in n for n in p['notes'])
    assert 'EECE 2322' not in cs  # No elective pool copied from another variant.


@pytest.mark.parametrize('code,expected', [('PSYC 3402','human_context'),('PSYC 4614','human_context'),('PSYC 4664','human_context'),('PSYC 4540','mathematics'),('PSYC 3450','applications'),('PSYC 3451','applications'),('PSYC 3458','applications'),('PSYC 3464','applications'),('PSYC 3466','applications'),('PSYC 4600','applications'),('PSYC 4674','applications'),('PSYC 4682','applications')])
def test_psychological_learning_neural_and_modeling_terms_need_actual_subject(code,expected):
    d=CATEGORY_DECISIONS[code]
    assert category(code,d['name'],d['guard'])==expected
    assert category(code,d['name'],'New unrelated descriptive content')=='other'
    assert category(code,'Different identity',d['guard'])=='other'


def test_psychology_nested_behavior_choice_and_nontransferable_lab_stay_separate():
    from atlas.families import resolve_program
    from atlas.curriculum_profile import requirement_profile
    pid='northeastern-university-artificial-intelligence-and-psychology-bs-boston-bs-degree'
    p=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text());f=json.loads((ROOT/'data/families/northeastern-ai-combined-degrees.json').read_text());resolved=resolve_program(p,f);profile=requirement_profile(resolved)
    assert profile['required']['count']==14 and profile['options']['count']==48 and profile['unresolved']['count']==0
    nodes={r['id']:r for r in resolved['requirements']}
    selection=nodes[pid+'-req-cognitive-biological-basis-of-behavior-course-choice']
    assert selection['kind']=='choose_courses' and selection['count']==2
    alt=nodes[pid+'-req-psyc-3450-alternatives']
    assert alt['kind']=='alternative' and alt['parent_id']==selection['id']
    children=[r for r in nodes.values() if r['parent_id']==alt['id']]
    assert {c for r in children for c in r['course_ids']}=={pid+'-psyc-3450',pid+'-psyc-3451'}
    lab=nodes[pid+'-req-psychology-laboratory-course-choice']
    assert lab['count']==1 and 'may not be fulfilled via transfer credit' in lab['summary']
    assert len(p['courses'])==62 and all('category_review' in c for c in p['courses'])


@pytest.mark.parametrize('code,expected', [('BINF 6200','foundations'),('BNSC 1000','other'),('PT 5410','applications'),('PT 5411','applications'),('PSYC 3506','applications'),('PSYC 3510','applications'),('PSYC 4510','applications'),('PSYC 4570','applications')])
def test_behavioral_neuroscience_subjects_preserve_biological_versus_software_scope(code,expected):
    d=CATEGORY_DECISIONS[code]
    assert category(code,d['name'],d['guard'])==expected
    assert category(code,d['name'],'Unrelated changed content')=='other'
    assert category(code,'Different course identity',d['guard'])=='other'


def test_behavioral_manual_roles_keep_anatomy_bundle_and_advanced_nonreuse():
    from atlas.families import resolve_program
    from atlas.curriculum_profile import requirement_profile
    pid='northeastern-university-artificial-intelligence-and-behavioral-neuroscience-bs-boston-bs-degree'
    p=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text());f=json.loads((ROOT/'data/families/northeastern-ai-combined-degrees.json').read_text());resolved=resolve_program(p,f);profile=requirement_profile(resolved)
    assert profile['required']['count']==23 and profile['options']['count']==49 and profile['unresolved']['count']==0
    assert len(p['courses'])==72 and all('category_review'in c for c in p['courses'])
    nodes={r['id']:r for r in resolved['requirements']}
    pair=next(r for r in nodes.values() if set(r['course_ids'])=={pid+'-pt-5410',pid+'-pt-5411'})
    assert pair['kind']=='all' and nodes[pair['parent_id']]['kind']=='alternative'
    assert any('not taken to fulfill previous requirements' in r['summary'] and r['count']==2 for r in nodes.values())
    assert sum(c['code']=='BIOL 5595' for c in p['courses'])==1
    assert next(c for c in p['courses']if c['code']=='PT 5411')['credits']==1
    assert next(c for c in p['courses']if c['code']=='BINF 6200')['category']=='foundations'
    assert next(c for c in p['courses']if c['code']=='BINF 6310')['category_review']['status']=='mixed'
