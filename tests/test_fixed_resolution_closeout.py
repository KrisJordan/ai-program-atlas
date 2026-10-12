"""Closeout accepts exactly assigned evidence scopes; no whole-degree promotion."""
import json
from pathlib import Path

from atlas.degree_audit import collect_ledgers

ROOT = Path(__file__).resolve().parents[1]


def test_latest_scoped_proposals_applied_without_whole_degree_promotion():
    proposals = {}
    for path in (ROOT/'research/degree-audit').glob('independent-resolution-*.json'):
        for row in json.loads(path.read_text())['programs']:
            assert row['program_id'] not in proposals
            proposals[row['program_id']] = row
    assert len(proposals) == 16
    # Later university-only evidence supersedes these dated proposals; Furman
    # and already-verified Purdue BS remain at their accepted earlier scope.
    followup = {}
    for path in (ROOT/'research').glob('university-core-followup-*.json'):
        for row in json.loads(path.read_text())['programs']:
            assert row['program_id'] not in followup
            followup[row['program_id']] = row
    assert len(followup) == 14
    assert all('furman' not in pid for pid in followup)
    proposals.update(followup)
    programs = [json.loads(path.read_text()) for path in (ROOT/'data/programs').glob('*.json')]
    ledger = collect_ledgers(ROOT/'research/degree-audit', programs)
    lookup = {row['program_id']: row for row in ledger['programs']}
    for pid, proposal in proposals.items():
        accepted = {k: v for k, v in lookup[pid]['core_review'].items() if k != 'ledger'}
        if proposal.get('superseded_by'):
            assert (ROOT / proposal['superseded_by']).exists()
            assert accepted['reviewed_at'] > proposal['reviewed_at']
            assert accepted['expected_profile']['required']['count'] == (11 if pid == 'purdue-ai-ba' else 7)
            assert accepted['full_degree_verified'] is False
        else:
            assert accepted == proposal
        assert lookup[pid]['status'] == 'blocked'
    assert sum(row['status'] == 'audited' for row in ledger['programs']) == 2
    assert sum(row['status'] == 'blocked' for row in ledger['programs']) == 61
    purdue = proposals['purdue-ai-bs']
    assert purdue['dimensions']['fixed_requirements']['status'] == 'verified'
    assert len(purdue['expected_course_ids']['required']) == 9
    assert purdue['full_degree_verified'] is False
    economic = proposals['university-at-buffalo-suny-ai-and-quantitative-economics-bs-degree']
    assert economic['dimensions']['fixed_requirements']['status'] == 'partial'
    assert len(economic['expected_course_ids']['required']) == 19
    assert len(economic['expected_course_ids']['options']) == 16


def test_stevens_reconstruction_does_not_certify_named_options():
    row = json.loads((ROOT/'research/degree-audit/independent-resolution-stevens.json').read_text())['programs'][0]
    assert 'reviewed_option_subset' not in row
    assert row['expected_course_ids']['required'] is None
    assert row['dimensions']['fixed_requirements']['status'] == 'unverified'
    assert row['dimensions']['choice_rules']['status'] == 'partial'
    assert 'primary' in row['dimensions']['choice_rules']['limitations'][0].lower()
    reconstruction = next(c for c in row['source_captures'] if 'reviewed-labels' in c['path'])
    assert reconstruction['evidence_kind'] == 'primary_reconstruction_not_actual_source'
