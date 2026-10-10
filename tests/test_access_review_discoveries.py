"""Identity evidence is bounded, source-specific and never curriculum freshness."""
import importlib.util
import json
from pathlib import Path

import pytest
from atlas.db import validate_program

ROOT = Path(__file__).resolve().parents[1]
ENTRIES = json.loads((ROOT / 'research/access-review-discoveries.json').read_text())


def load(pid):
    spec = importlib.util.spec_from_file_location(pid, ROOT / 'atlas/adapters' / pid / 'adapter.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fixture(entry):
    seed = json.loads((ROOT / 'data/programs' / (entry['id'] + '.json')).read_text())
    if entry['id'].startswith('uva-'):
        section = 'BSCS' if 'bscs' in entry['id'] else 'BACS'
        return f'<main><h1>Artificial Intelligence Concentration</h1><h2>{section} AI Concentration</h2><p>Four courses.</p></main>'
    return '<main><h1>' + seed['sources'][0]['title'] + '</h1><p>' + ('Bachelor of Science' if entry['award_level'] == 'BS' else '') + '</p></main>'


@pytest.mark.parametrize('entry', ENTRIES, ids=lambda e: e['id'])
def test_source_identity_and_explicit_pending_inventory(entry):
    mod = load(entry['id'])
    seed = json.loads((ROOT / 'data/programs' / (entry['id'] + '.json')).read_text())
    validate_program(seed)
    assert mod.parse(fixture(entry)) == {k: seed[k] for k in ('id', 'title', 'award_level', 'program_kind')}
    assert seed['curriculum_status'] == 'pending'
    assert not seed['courses'] and not seed['requirements']
    with pytest.raises(ValueError):
        mod.parse('<nav>' + fixture(entry) + '</nav><main><h1>Unrelated program</h1></main>')
    with pytest.raises(ValueError):
        mod.parse('<h1>Access denied</h1>' + fixture(entry))


@pytest.mark.parametrize('pid,wrong', [('uva-bscs-ai-concentration', 'BACS'), ('uva-bacs-ai-concentration', 'BSCS')])
def test_uva_requires_correct_parent_degree_section(pid, wrong):
    with pytest.raises(ValueError, match='parent-degree'):
        load(pid).parse(f'<main><h1>Artificial Intelligence Concentration</h1><h2>{wrong} AI Concentration</h2></main>')


@pytest.mark.parametrize('entry', ENTRIES, ids=lambda e: e['id'])
def test_optional_local_official_source_replay(entry):
    source = Path('/tmp/atlas-review-' + entry['fixture_key'] + '.html')
    if not source.exists():
        pytest.skip('Optional ignored official-source cache is unavailable')
    observed = load(entry['id']).parse(source.read_text())
    assert observed['id'] == entry['id']
    assert not {'courses', 'requirements', 'last_verified', 'curriculum_audit', 'curriculum_status'} & observed.keys()
