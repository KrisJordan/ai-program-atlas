import json
from pathlib import Path
from atlas.curriculum_profile import requirement_profile
from atlas.db import validate_program


def test_integrated_religious_studies_and_comparative_literature_keep_scope():
    d = json.loads(Path('data/programs/ucsb-ai-bs.json').read_text())
    validate_program(d)
    c = {c['code']: c for c in d['courses']}
    assert c['C LIT 152']['category'] == 'foundations'
    assert c['C LIT 27']['category_review']['status'] == 'mixed'
    assert c['RG ST 152VR']['category'] == 'human_context'
    assert c['RG ST 193B']['category'] == 'human_context'
    assert c['RG ST 147']['credits'] == 4
    assert any('eight' in n.lower() or '8' in n for n in c['RG ST 147']['notes'])
    assert any('5' in n and '4' in n for n in c['RG ST 4']['notes'])
    assert any('C LITW 40' in n and 'C LIT 40' in n for n in c['C LITW 40']['notes'])
    assert c['C LIT 155']['source_id'] != 'ucsb-ai-bs-ge-defg-export'
    assert 'ucsb-ai-bs-ge-defg-export' in c['C LIT 155']['category_review']['source_ids']
    assert len([x for x in d['courses'] if x['id'] == 'ucsb-c-lit-155']) == 1
    assert [requirement_profile(d)[k]['count'] for k in ('required', 'options', 'unresolved')] == [20, 262, 2]
