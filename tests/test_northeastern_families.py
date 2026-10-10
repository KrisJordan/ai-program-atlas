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
}
ANNOTATIONS={'origin','component','component_classification','family_requirement_id','family_source_id'}


def family():return json.loads((ROOT/'data/families'/f'{FID}.json').read_text())
def program(pid):return json.loads((ROOT/'data/programs'/f'{pid}.json').read_text())


@pytest.mark.parametrize('pid',EXPECTED)
def test_initial_variant_reconstruction_preserves_entire_original_graph(pid):
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
