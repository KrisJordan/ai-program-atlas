"""Real reviewed family migration preserves each Northeastern award graph."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import pytest
from atlas import db
from atlas.families import resolve_program
from atlas.family_store import ingest_family

ROOT=Path(__file__).resolve().parents[1]
FID='northeastern-ai-combined-degrees'
# Mechanical before/after guard for the original reviewed flat requirement graphs.
# Catalog/semantic justification is separately documented in program-families.md.
EXPECTED={
'northeastern-university-artificial-intelligence-and-philosophy-bs-boston-bs-degree':'efcb5572e32f1123e5f8bd1139087f58ddbf0841a8939b41265aa9537e3bb57d',
'northeastern-university-artificial-intelligence-and-business-administration-bs-boston-bs-degree':'1eee64c4643fcaa63ba8146718d248ea56937324d304b6efe59e4e292213a0a3',
'northeastern-university-artificial-intelligence-and-biology-bs-boston-bs-degree':'343658372d30d271b2e8d632af4260feb6f446e8f5eb856c51b8e692dd0d3527',
'northeastern-university-artificial-intelligence-and-behavioral-neuroscience-bs-boston-bs-degree':'1a335b089cb01bef3168d69ad44a236bfb329aaf3bbf0bb3f985c3a11dcbf9a5',
'northeastern-university-artificial-intelligence-and-biochemistry-bs-boston-bs-degree':'f4be883aca3d85c9444765378ef690d89d9fd993ccbd07df2aa2597bf3533fe2',
'northeastern-university-artificial-intelligence-and-chemistry-bs-boston-bs-degree':'025254f254a272e3f7ae07ffb1cd7d334fba717a51ffe67f9955426307447ef6',
'northeastern-university-artificial-intelligence-and-design-bs-boston-bs-degree':'56ff673c81d4418438ffd23decab027f06d85bcda09a3bac465c0ac00b8faca9',
'northeastern-university-artificial-intelligence-and-ecology-and-evolutionary-biology-bs-boston-bs-degree':'6645ea5a06ec9a3d7eac84686778f01dc2de40ed566adb5da3104248f9b3f69c',
'northeastern-university-artificial-intelligence-and-economics-bs-boston-bs-degree':'a41b761c5c471b8acd29e8868b26983991343662ee61250c374fd292761e271c',
'northeastern-university-artificial-intelligence-and-environmental-and-sustainability-sciences-bs-boston-bs-degree':'8aa41b72e04b76a1c14b2d319a1226af05da4ffe4d5634e07f2adbb468213e9e',
'northeastern-university-artificial-intelligence-and-health-science-bs-boston-bs-degree':'a99967a5ae6ac5215f93c0fd5cb1ff53b1493ef03ab7fd5e92e3432566273b91',
'northeastern-university-artificial-intelligence-and-linguistics-bs-boston-bs-degree':'38333a87dd4275f6bcc78c0c5ef7c71476e009af65978461a020278fcc489cd0',
'northeastern-university-artificial-intelligence-and-mathematics-bs-boston-bs-degree':'790e576fa4d0abe5da7e33adae30eb8049a079fd3ebc63f79fb695bdb328e21b',
'northeastern-university-artificial-intelligence-and-physics-bs-boston-bs-degree':'ed987ff2ebced3c5d6a9ada366e61f393bdf62b3786f93480ee2d7c192b79571',
'northeastern-university-artificial-intelligence-and-psychology-bs-boston-bs-degree':'8a773598e253866f152109839ed8a78fa89781d19639d2e7fdf17c0abef22b90',
'northeastern-university-artificial-intelligence-and-public-health-bs-boston-bs-degree':'917f2270c49b948541e492007d021027611848ddc9fb43d4589d2ed18cc28133',
'northeastern-university-artificial-intelligence-and-criminal-justice-bs-boston-bs-degree':'3e821be086a0e85989e93f4f210ff1dff0ea9c29fa959dfb495482b501e43aee',
'northeastern-university-artificial-intelligence-and-communication-studies-bs-boston-bs-degree':'e5f1da07c7bb7b08046335d95017da4f2ecd9ed21049a39237e685b0f82ace7f',
'northeastern-university-artificial-intelligence-and-speech-language-pathology-and-audiology-bs-boston-bs-degree':'39384f58e1b6a0405104375f2ec5febad6419603b68dc156fc8ee6e19e56989f',
'northeastern-university-artificial-intelligence-and-sociology-bs-boston-bs-degree':'a3a9b40d873309214085b6b8f2a5b468437bdd605b660897bf5172fba204ac34',
'northeastern-university-environmental-engineering-and-artificial-intelligence-bsenve-boston-other-degree':'12763791974097de6bdddd9656a53b5a858d73b3a73efec67cc9acdd1be0dfef',
'northeastern-university-artificial-intelligence-and-international-affairs-bs-boston-bs-degree':'67acf02f9b46f44bb0ae0171d0b7002471575cef9e7ec0d38d04bb185043b796',
'northeastern-university-artificial-intelligence-and-journalism-bs-boston-bs-degree':'a5e24a0978049f466d59b63493edecffcfed3fc4bf0506fcf50883a61b32fc20',
}
ANNOTATIONS={'origin','component','component_classification','family_requirement_id','family_source_id'}


def family():return json.loads((ROOT/'data/families'/f'{FID}.json').read_text())
def program(pid):return json.loads((ROOT/'data/programs'/f'{pid}.json').read_text())


@pytest.mark.parametrize('pid',EXPECTED)
def test_reviewed_variant_reconstruction_preserves_entire_original_graph(pid):
    p=program(pid);f=family();db.validate_program(p,f);resolved=resolve_program(p,f)
    rows=[{k:v for k,v in r.items() if k not in ANNOTATIONS} for r in resolved['requirements'] if not r.get('family_requirement_id','').startswith('policy-')]
    # The audit adds a separately sourced concurrent seminar beneath the original
    # CS 1800 node. Preserve every historical degree node unchanged; dedicated
    # concurrency tests verify the added source rule, ancestry and course facts.
    added=[r for r in rows if r['id']==pid+'-req-cs-1802-concurrent']
    for r in added:
        assert r['parent_id']==pid+'-req-cs-1800' and r['source_id']==pid+'-cs-courses'
        assert r['kind']=='all' and r['course_ids']==[pid+'-cs-1802']
    rows=[r for r in rows if r not in added]
    science=[r for r in rows if r['id'].endswith('-concurrent') and r['source_id'] in {pid+'-chem-courses',pid+'-phys-courses',pid+'-eece-courses'}]
    for r in science:
        assert r['parent_id']==r['id'].removesuffix('-concurrent') and r['kind']=='all'
    # The independent source/role/delta tests in test_northeastern_science_corequisites
    # verify these additions; every original degree node still matches its hash.
    rows=[r for r in rows if r not in science]
    # New source-scoped conditional CSSH transfer nodes are replayed in the
    # college-policy suite; exclude only these five non-course additions.
    transfer=[r for r in rows if r['source_id']==pid+'-cssh-transfer-policy']
    if transfer:
        assert len(transfer)==5 and all(r['kind']=='note' and not r['course_ids'] for r in transfer)
        rows=[r for r in rows if r not in transfer]
    science_policy=[r for r in rows if r['source_id']==pid+'-science-college-policy']
    if science_policy:
        assert len(science_policy)==9 and all(r['kind']=='note' and not r['course_ids'] for r in science_policy)
        rows=[r for r in rows if r not in science_policy]
    bouve_policy=[r for r in rows if r['source_id']==pid+'-bouve-college-policy']
    if bouve_policy:
        assert len(bouve_policy)==15 and all(r['kind']=='note' and not r['course_ids'] for r in bouve_policy)
        rows=[r for r in rows if r not in bouve_policy]
    engineering_policy=[r for r in rows if r['source_id']==pid+'-engineering-college-policy']
    if engineering_policy:
        assert len(engineering_policy)==8 and all(r['kind']=='note' and not r['course_ids'] for r in engineering_policy)
        rows=[r for r in rows if r not in engineering_policy]
    camd_policy=[r for r in rows if r['source_id']==pid+'-camd-policy-review']
    if camd_policy:
        assert len(camd_policy)==1 and camd_policy[0]['id']==pid+'-conditional-camd-clearance'
        assert camd_policy[0]['kind']=='note' and not camd_policy[0]['course_ids']
        rows=[r for r in rows if r not in camd_policy]
    if pid=='northeastern-university-environmental-engineering-and-artificial-intelligence-bsenve-boston-other-degree':
        # Footnote 1 permits two complete introductory-engineering routes.
        # Verify the deliberate role correction, then project the five original
        # allocation rows solely for their historical preservation fingerprint.
        choice=pid+'-req-introductory-engineering-bundle'
        bundles=[r for r in rows if r['id']==choice or r.get('parent_id')==choice]
        assert len(bundles)==3
        assert {tuple(r['course_ids']) for r in bundles if r['kind']=='all'}=={
            (pid+'-ge-1501',pid+'-ge-1502'),(pid+'-ge-1110',pid+'-ge-1111')}
        rows=[r for r in rows if r not in bundles]
        allocations=[r for r in rows if r['id'] in {pid+'-req-'+key for key in ['ge-1501','ge-1502','ge-1501-2','ge-1501-3','ge-1502-2']}]
        assert len(allocations)==5
        for r in allocations:
            assert r['kind']=='note' and 'complete GE 1110/1111 substitute bundle' in r['summary']
            r['kind']='all';r['summary']='Listed course.'
    if 'business-administration' in pid:
        # The reviewed follow-up adds independent concentration-source subtrees
        # and two main-page selection nodes; test those in the concentration suite.
        # Preserve the original major graph hash. Only the two formerly unexpanded
        # pointer notes intentionally change; assert their new text before projecting
        # their old wording for this historical preservation check.
        rows=[r for r in rows if r['source_id']==pid+'-catalog' and r['id'] not in {
            pid+'-req-business-concentration-options',pid+'-req-business-concentration-second-only'}]
        for r in rows:
            if r['id'] in {pid+'-req-business-concentration-policy-2',pid+'-req-business-concentration-policy-4'}:
                assert r['summary']=='The degree links the finite concentration options below; their current requirements are observed independently from each linked concentration page.'
                r['summary']='Choose a business concentration from the linked catalog options; individual concentration curricula remain unexpanded.'
    digest=hashlib.sha256(json.dumps(sorted(rows,key=lambda r:r['id']),sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert digest==EXPECTED[pid]
    shared=[r for r in resolved['requirements'] if r['origin']=='family']
    assert len(shared)==len(f['shared_requirements'])
    assert len([r for r in shared if not r['family_requirement_id'].startswith('policy-')])==9
    assert not {r['id'] for r in p['requirements']} & {r['id'] for r in shared}
    assert p['award_level']==('other' if 'bsenve' in pid else 'BS') and p['curriculum_status']=='partial'
    assert p['curriculum_audit']['unresolved_requirements']
    assert p['family']['relationship']=='integrated'
    assert p['family']['classification_kind']=='source_stated'
    assert {'domain','integration','ai_core'} <= {r['component'] for r in resolved['requirements']}
    assert resolved['courses']==p['courses'] and resolved['last_verified']==p['last_verified']


def test_shared_change_propagates_once_without_changing_local_requirements():
    original=family();changed=deepcopy(original)
    next(r for r in changed['shared_requirements'] if r['id']=='machine-learning')['credits']=3
    for pid in EXPECTED:
        p=program(pid);before=resolve_program(p,original);after=resolve_program(p,changed)
        assert next(r for r in after['requirements'] if r.get('family_requirement_id')=='machine-learning')['credits']==3
        assert [r for r in before['requirements'] if r['origin']=='variant']==[r for r in after['requirements'] if r['origin']=='variant']
        assert after['curriculum_status']=='partial'


def test_real_family_persists_once_and_exports_distinct_awards(tmp_path):
    conn=db.connect(tmp_path/'atlas.sqlite');db.migrate(conn)
    variants={pid:program(pid) for pid in EXPECTED}
    for p in variants.values():db.upsert_institution(conn,p['institution'])
    assert ingest_family(conn,family(),program_updates=variants)
    assert not ingest_family(conn,family(),program_updates=variants)
    exported=db.export_data(conn)
    assert {p['id'] for p in exported['programs']}==set(EXPECTED)
    assert conn.execute('SELECT count(*) FROM family_requirement_groups').fetchone()[0]==len(family()['shared_requirements'])
    for p in exported['programs']:
        assert len([r for r in p['requirements'] if r['origin']=='family'])==len(family()['shared_requirements'])
        assert p['family']['id']==FID
    assert conn.execute('PRAGMA integrity_check').fetchone()[0]=='ok'


@pytest.mark.parametrize(('partner','shared_id'), [('design','data-visualization'),('mathematics','machine-learning')])
def test_shared_course_keeps_source_stated_integrative_role(partner,shared_id):
    pid=f'northeastern-university-artificial-intelligence-and-{partner}-bs-boston-bs-degree'
    p=program(pid);rows={r['id']:r for r in resolve_program(p,family())['requirements']}
    binding=next(b for b in p['family']['requirement_bindings'] if b['shared_id']==shared_id)
    row=rows[binding['id']]
    assert row['origin']=='family' and row['component']=='integration'
    assert row['component_classification']=='source_stated'
    assert row['parent_id']==binding['parent_id']
    assert rows[row['parent_id']]['title'].startswith('Integrative')


def test_pending_northeastern_variants_have_no_unreviewed_inheritance():
    for path in (ROOT/'data/programs').glob('northeastern-*.json'):
        p=json.loads(path.read_text())
        if p['curriculum_status']=='pending':assert not p.get('family')



def test_engineering_variant_keeps_distinct_award_and_verified_hosting_units():
    p=program('northeastern-university-environmental-engineering-and-artificial-intelligence-bsenve-boston-other-degree')
    r=resolve_program(p,family())
    assert r['award_level']=='other' and ', BSEnvE (Boston)' in r['title']
    assert {h['name'] for h in p['family']['hosting_units']}=={'College of Engineering','Civil and Environmental Engineering'}
    assert p['family']['disciplines']==['Environmental Engineering','Artificial Intelligence']
    assert p['family']['relationship']=='integrated'
    assert len([q for q in r['requirements'] if q['origin']=='family'])==len(family()['shared_requirements'])
    assert len(EXPECTED)==23



def test_communication_variant_uses_its_own_verified_college_context():
    p=program('northeastern-university-artificial-intelligence-and-communication-studies-bs-boston-bs-degree')
    assert {h['name'] for h in p['family']['hosting_units']}=={'College of Arts, Media and Design','Communication Studies'}
    assert all(h['source_id']==p['id']+'-catalog' for h in p['family']['hosting_units'])



def test_shared_policy_scope_is_proven_and_distinct_from_original_ai_core():
    f=family();policy=[r for r in f['shared_requirements'] if r['id'].startswith('policy-')]
    assert len(policy)==58 and all(r['component']=='other' and not r['course_codes'] for r in policy)
    for pid in EXPECTED:
        p=program(pid);resolved=resolve_program(p,f)
        assert len([r for r in resolved['requirements'] if r.get('family_requirement_id','').startswith('policy-')])==58
        assert all('college' in gap.lower() or 'concentration' in gap.lower() for gap in p['curriculum_audit']['unresolved_requirements'])
        assert all(any(s['url']==url for s in p['sources']) for url in [
            'https://catalog.northeastern.edu/undergraduate/university-academics/university-wide-requirements/',
            'https://catalog.northeastern.edu/undergraduate/university-academics/general-education-requirements/'])


@pytest.mark.parametrize(('partner','college','label'), [
    ('business-administration','D’Amore-McKim School of Business','Business Administration'),
    ('biology','College of Science','Biology'),
    ('design','College of Arts, Media and Design','Design'),
])
def test_participating_colleges_have_explicit_evidence_without_home_college_assignment(partner,college,label,tmp_path):
    p=program(f'northeastern-university-artificial-intelligence-and-{partner}-bs-boston-bs-degree')
    sid=p['id']+'-participating-colleges-admissions'
    source=next(s for s in p['sources'] if s['id']==sid)
    assert source['url']=='https://admissions.northeastern.edu/academics/combined-majors/'
    assert f'Artificial Intelligence and {label}' in source['locator']
    assert 'associated colleges' in source['locator']
    assert source['catalog_year'] is None  # Admissions is not a dated catalog edition.
    assert sid in p['family']['source_ids']
    assert p['family']['hosting_units']==[
        {'name':'Khoury College of Computer Sciences','source_id':sid},
        {'name':college,'source_id':sid},
    ]
    assert p['hosting_unit'] is None
    assert p['curriculum_status']=='partial'
    assert any('home-college' in gap for gap in p['curriculum_audit']['unresolved_requirements'])
    assert any('not permitted or mandatory home-college' in note for note in p['notes'])
    # A participating-college source supports context only, never a requirement
    # or a new inherited college policy. Check the public persistence boundary too.
    resolved=resolve_program(p,family())
    assert not any(r['source_id']==sid for r in resolved['requirements'])
    conn=db.connect(tmp_path/'atlas.sqlite');db.migrate(conn)
    db.upsert_institution(conn,p['institution'])
    assert ingest_family(conn,family(),program_updates={p['id']:p})
    assert not db.ingest_program(conn,p)
    exported=db.export_data(conn)['programs'][0]
    assert exported['family']['hosting_units']==p['family']['hosting_units']
    assert exported['hosting_unit'] is None and exported['curriculum_status']=='partial'
    assert next(s for s in exported['sources'] if s['id']==sid)['locator']==source['locator']
