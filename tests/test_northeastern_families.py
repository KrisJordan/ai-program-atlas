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
}
ANNOTATIONS={'origin','component','component_classification','family_requirement_id','family_source_id'}


def family():return json.loads((ROOT/'data/families'/f'{FID}.json').read_text())
def program(pid):return json.loads((ROOT/'data/programs'/f'{pid}.json').read_text())


@pytest.mark.parametrize('pid',EXPECTED)
def test_reviewed_variant_reconstruction_preserves_entire_original_graph(pid):
    p=program(pid);f=family();db.validate_program(p,f);resolved=resolve_program(p,f)
    rows=[{k:v for k,v in r.items() if k not in ANNOTATIONS} for r in resolved['requirements']]
    digest=hashlib.sha256(json.dumps(sorted(rows,key=lambda r:r['id']),sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert digest==EXPECTED[pid]
    shared=[r for r in resolved['requirements'] if r['origin']=='family']
    assert len(shared)==9
    assert not {r['id'] for r in p['requirements']} & {r['id'] for r in shared}
    assert p['award_level']=='BS' and p['curriculum_status']=='partial'
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
    assert conn.execute('SELECT count(*) FROM family_requirement_groups').fetchone()[0]==9
    for p in exported['programs']:
        assert len([r for r in p['requirements'] if r['origin']=='family'])==9
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
