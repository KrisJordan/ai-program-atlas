"""PSU policy closure preserves conditional rules without inventing course obligations."""
import json
from pathlib import Path

from atlas.curriculum_profile import requirement_profile
from atlas.degree_audit import validate_ledger

ROOT = Path(__file__).resolve().parents[1]
PIDS = ('penn-state-ai-engineering-bs', 'penn-state-ai-methods-applications-ist-bs')


def records():
    return [json.loads((ROOT / 'data/programs' / (pid + '.json')).read_text()) for pid in PIDS]


def test_policy_additions_do_not_promote_honors_or_prerequisite_courses():
    for p, expected in zip(records(), ((17, 13), (9, 156))):
        profile = requirement_profile(p)
        assert (profile['required']['count'], profile['options']['count']) == expected
        rules = {r['id']: r for r in p['requirements']}
        for suffix in ('honors-communication', 'catalog-cohort', 'gpa-exceptions', 'residence-notice'):
            rule = rules[p['id'] + '-' + suffix]
            assert rule['kind'] == 'note' and not rule['course_ids']
        assert 'Incoming Schreyer' in rules[p['id'] + '-honors-communication']['summary']
        residence = rules[p['id'] + '-residence-notice']['summary']
        assert 'first bachelor' in residence and 'intervening military service' in residence
        assert 'pending implementation' in residence
        assert 'unverified future replacement' in residence


def test_closure_blockers_are_exact_existing_source_gaps_not_pending_rules():
    entries = json.loads((ROOT / 'research/degree-audit/national-degree-batch.json').read_text())['programs']
    owned = [e for e in entries if e['program_id'] in PIDS]
    validate_ledger(owned, records())
    assert len(owned) == 2
    for entry in owned:
        assert entry['status'] == 'blocked'
        assert entry['second_pass_status'] == 'partial'
        assert entry['blockers']
        assert not any('Pending implementation' in b['issue'] for b in entry['blockers'])
    engineering = next(e for e in owned if e['program_id'] == PIDS[0])
    ist = next(e for e in owned if e['program_id'] == PIDS[1])
    assert '27' in engineering['blockers'][0]['issue']
    assert {b['url'].rstrip('/').split('/')[-1] for b in ist['blockers']} == {'ist', 'sra', 'phil'}


def test_college_guidance_is_source_scoped_and_scrapers_observe_new_notes():
    from atlas.adapters.psu_degree_policy_details import source_parsers, SPEC
    for p in records():
        parsers = source_parsers(p['id'])
        engineering_url = SPEC['engineering-advising-procedure']['url']
        ist_url = SPEC['ist-graduation-procedure']['url']
        assert (engineering_url in parsers) == (p['id'] == PIDS[0])
        assert (ist_url in parsers) == (p['id'] == PIDS[1])
    ist = records()[1]
    assert any('AIMA is expressly exempt' in (r.get('summary') or '') for r in ist['requirements'])
    assert not any(r['kind'] == 'all' and 'psu-ist-495' in r['course_ids'] for r in ist['requirements'])
