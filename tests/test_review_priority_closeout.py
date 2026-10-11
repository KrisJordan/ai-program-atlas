"""Independent peer acceptance remains pinned separately from host-degree claims."""
import json
from pathlib import Path
from atlas.additional_major_audit import collect_ledgers, review_fingerprint

ROOT = Path(__file__).resolve().parents[1]


def test_all_five_additional_majors_match_independent_peer_acceptance():
    programs = [json.loads(p.read_text()) for p in (ROOT/'data/programs').glob('*.json')]
    result = collect_ledgers(ROOT/'research', programs)
    assert len(result['programs']) == 5
    lookup = {p['id']:p for p in programs}
    for row in result['programs']:
        review = row['independent_review']
        assert row['second_pass_status'] == 'verified'
        assert review['full_host_degree_verified'] is False
        assert review['reviewed_content_hash'] == review_fingerprint(lookup[row['program_id']])
        peer = json.loads((ROOT/review['ledger']).read_text())
        accepted = next(r for r in peer.get('programs',[peer]) if r['program_id'] == row['program_id'])
        assert accepted.get('reviewed_content_hash', accepted.get('final_program_review_fingerprint')) == review['reviewed_content_hash']
    dimensions = {r['program_id']:r['dimensions'] for r in result['programs']}
    assert all(r['fixed_requirements']['status'] == 'verified' for r in dimensions.values())
    assert sum(r['eligibility_review']['status'] == 'partial' for r in result['programs']) == 2


def test_stevens_draft_scope_and_catalog_conflict_remain_explicit():
    evidence = json.loads((ROOT/'research/university-core-followup-authoritative-plans.json').read_text())
    row = next(r for r in evidence['programs'] if 'stevens' in r['program_id'])
    assert row['dimensions']['fixed_requirements']['status'] == 'partial'
    assert row['full_degree_verified'] is False
    assert len(row['expected_course_ids']['required']) == 24
    program = json.loads((ROOT/'data/programs'/f"{row['program_id']}.json").read_text())
    text = json.dumps(program)
    assert 'UNOFFICIAL DRAFT' in text and 'Workday' in text
    assert 'EN 250' in text and 'CE 240' in text and 'NANO 200' in text
