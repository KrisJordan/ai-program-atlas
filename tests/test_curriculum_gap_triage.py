"""Frozen research queue integrity; later program edits do not rewrite its claims."""
import collections
import hashlib
import json
from pathlib import Path
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
TRIAGE = ROOT / 'research/curriculum-gap-triage.json'


def test_snapshot_queue_covers_all_concrete_ids_and_separates_evidence_dimensions():
    data = json.loads(TRIAGE.read_text())
    rows = data['programs']
    ids = [r['id'] for r in rows]
    assert len(ids) == len(set(ids)) == data['counts']['included'] == 96
    assert collections.Counter(r['curriculum_status'] for r in rows) == {'partial': 90, 'pending': 6}
    assert len(data['excluded_complete_program_ids']) == 29
    assert not set(ids) & set(data['excluded_complete_program_ids'])
    assert collections.Counter(r['classification']['category'] for r in rows) == data['counts']['categories']
    grouped = {g['id']: g for g in data['groups']}
    assert len(grouped['northeastern-home-college']['program_ids']) == 23
    buffalo = [r for r in rows if r['triage_group'] == 'buffalo-catalog']
    assert len(buffalo) == 10
    assert sum(r['family_id'] == 'buffalo-ai-plus-x-degrees' for r in buffalo) == 8
    assert sum(r['program_kind'] == 'minor' and r['family_id'] is None for r in buffalo) == 2
    markdown = TRIAGE.with_suffix('.md').read_text()
    for r in rows:
        assert f"`{r['id']}`" in markdown
        assert r['classification']['kind'] == 'analyst_classified'
        assert r['requirement_gaps'] and r['next_action'] and r['classification']['provenance']
        dimensions = r['classification']['dimensions']
        assert r['classification']['category'] == ('mixed' if len(dimensions) > 1 else dimensions[0])
        if 'access_barrier' in dimensions:
            assert r['access_observations']
            assert all(a['fresh_network_verification'] is False for a in r['access_observations'])
        else:
            assert not r['access_observations']
        assert 'unknown_course_fields' in r['metadata_and_optional_fields']
        assert r['audit_evidence_sources']
    lookup = {r['id']: r for r in rows}
    # Historical failures corrected by later research must not become current barriers.
    for pid in ['penn-bse-ai', 'tufts-ai-development-minor', 'rit-ai-society-minor']:
        assert 'access_barrier' not in lookup[pid]['classification']['dimensions']
    for pid in ['uc-merced-ai-bs', 'uc-merced-cse-ai-emphasis']:
        assert lookup[pid]['access_observations'][0]['exact_failed_url'] is None


def test_triage_exact_audits_and_note_lines_match_pinned_commit():
    data = json.loads(TRIAGE.read_text())
    sha = data['snapshot_commit']
    available = subprocess.run(['git', 'cat-file', '-e', sha + '^{commit}'], cwd=ROOT, capture_output=True)
    if available.returncode:
        pytest.skip('Frozen research commit is unavailable in this shallow/source-only checkout')

    def read(path):
        return subprocess.check_output(['git', 'show', f'{sha}:{path}'], cwd=ROOT)

    paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', sha, 'data/programs'], cwd=ROOT, text=True).splitlines()
    programs = {p['id']: p for path in paths if path.endswith('.json') for p in [json.loads(read(path))]}
    expected = {pid for pid, p in programs.items() if p['curriculum_status'] != 'complete'}
    assert {r['id'] for r in data['programs']} == expected
    assert set(data['excluded_complete_program_ids']) == set(programs) - expected
    for row in data['programs']:
        raw = read(f"data/programs/{row['id']}.json")
        assert hashlib.sha256(raw).hexdigest() == row['source_record_sha256']
        p = programs[row['id']]
        audit = p.get('curriculum_audit')
        if audit:
            stored = row['requirement_gaps'] + row['metadata_and_optional_fields']['reclassified_credit_normalization_annotations']
            ordered = sorted(stored, key=lambda g: int(g['provenance']['pointer'].split('/')[-1]))
            assert [g['text'] for g in ordered] == audit['unresolved_requirements']
            assert [g['text'] for g in row['metadata_and_optional_fields']['audit_annotations']] == audit['metadata_gaps']
        notes_path = row['classification']['provenance'][1]['path']
        notes = read(notes_path)
        assert hashlib.sha256(notes).hexdigest() == row['notes_sha256']
        lines = notes.decode().splitlines()
        for note in row['adapter_note_evidence']:
            assert note['text'] == lines[note['line'] - 1]
        sources = {s['id']: s for s in p['sources']}
        for source in row['audit_evidence_sources'] + row['other_recorded_sources']:
            assert source['url'] == sources[source['id']]['url']
            assert source['locator'] == sources[source['id']].get('locator')
