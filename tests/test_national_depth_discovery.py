"""Six identities: reviewed scopes, separate host degrees and honest lifecycle."""
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest
from atlas import db
from atlas.adapters.national_depth_discovery import CONFIG, parse_identity

ROOT = Path(__file__).resolve().parents[1]


def fixture(key):
    heading = CONFIG[key][3]
    text = {
        'fsu': 'The CS@FSU Artificial Intelligence Concentration is designed for computer science students.',
        'umass': 'The AI Concentration is available to students pursuing a BS in Computer Science.',
        'rpi': 'The minor explores connections between cognition and computing.',
        'smu-ba': 'The Bachelor of Arts in computer science requires nine credit hours from track electives: artificial intelligence and machine learning, research or another track.',
        'smu-bs': 'The Bachelor of Science in computer science requires nine credit hours from track electives: artificial intelligence and machine learning specialization, research or another track.',
        'uic': 'The Specialization level introduces a formal AI concentration.</p><p>The tracks will be available to incoming computer science students.',
    }[key]
    if key.startswith('smu-'):
        return f'<div class="program-header-intro"><h1>{heading}</h1></div><div id="faq-accordion"><p>{text}</p></div>'
    return f'<main><h1>{heading}</h1><p>{text}</p></main>'


def load(key):
    pid = CONFIG[key][0]
    spec = importlib.util.spec_from_file_location(pid, ROOT / 'atlas/adapters' / pid / 'adapter.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize('key', CONFIG)
def test_scoped_identity_and_contract(key):
    pid = CONFIG[key][0]
    seed = json.loads((ROOT / 'data/programs' / f'{pid}.json').read_text())
    db.validate_program(seed)
    observed = parse_identity(fixture(key), key)
    assert observed == {k: seed[k] for k in ('id', 'title', 'award_level', 'program_kind')}
    assert seed['curriculum_status'] in ('pending', 'partial')
    if seed['curriculum_status'] == 'partial':
        assert seed['curriculum_audit']['unresolved_requirements']
        with pytest.raises(ValueError):
            load(key).parse(fixture(key))
    else:
        assert not seed['courses'] and not seed['requirements']
    assert seed['first_offered'] is None
    assert set(load(key).SOURCES) <= {s['url'] for s in seed['sources']}
    assert not {'last_verified', 'curriculum_audit', 'curriculum_status', 'first_offered'} & observed.keys()


@pytest.mark.parametrize('key', CONFIG)
@pytest.mark.parametrize('wrapper', ['nav', 'aside', 'footer'])
def test_navigation_is_not_evidence(key, wrapper):
    with pytest.raises(ValueError):
        parse_identity(f'<{wrapper}>{fixture(key)}</{wrapper}><main><h1>Unrelated</h1></main>', key)


@pytest.mark.parametrize('key', CONFIG)
def test_absent_title_and_gate(key):
    with pytest.raises(ValueError):
        parse_identity(fixture(key).replace(CONFIG[key][3], 'Unrelated curriculum'), key)
    with pytest.raises(ValueError):
        parse_identity('<h1>Access denied</h1>' + fixture(key), key)
    with pytest.raises(ValueError):
        parse_identity('<input type="password">' + fixture(key), key)


@pytest.mark.parametrize('key,other', [('smu-ba','smu-bs'), ('smu-bs','smu-ba')])
def test_smu_cannot_borrow_sibling_degree(key, other):
    with pytest.raises(ValueError, match='Credential-specific'):
        parse_identity(fixture(other), key)


def test_uic_course_sequence_does_not_prove_concentration():
    html = fixture('uic').replace('Specialization level introduces a formal AI concentration', 'Progressive AI Integration introduces a four-course programming sequence')
    with pytest.raises(ValueError, match='Credential-specific'):
        parse_identity(html, 'uic')


def test_umass_graduate_context_not_undergraduate_identity():
    with pytest.raises(ValueError, match='Credential-specific'):
        parse_identity(fixture('umass').replace('BS in Computer Science', 'MS in Computer Science'), 'umass')


@pytest.mark.parametrize('key', CONFIG)
def test_optional_actual_cache_replay(key):
    mod = load(key)
    raw = ROOT / '.cache/http' / (hashlib.sha256(mod.SOURCES[0].encode()).hexdigest() + '.body')
    if not raw.exists():
        pytest.skip('Optional ignored official source capture unavailable')
    observed = mod.parse(raw.read_text())
    assert all(observed[k] == parse_identity(fixture(key), key)[k] for k in ('id', 'title', 'award_level', 'program_kind'))
    assert not {'last_verified', 'curriculum_audit', 'first_offered'} & observed.keys()


def test_coverage_is_bounded_and_announcement_is_not_launch():
    survey = json.loads((ROOT / 'data/surveys/national-depth-supplement-2026-10-11.json').read_text())
    assert len(survey) == 10
    assert sum(r['status'] == 'confirmed' for r in survey) == 5
    assert sum(len(r['discoveries']) for r in survey) == 6
    assert all(r['status'] in ('confirmed', 'inspected') for r in survey)
    uic = json.loads((ROOT / 'data/programs/uic-cs-ai-concentration.json').read_text())
    assert uic['status'] == 'announced'
    assert uic['sources'][0]['source_date'] == '2026-04-01'
    assert uic['first_offered'] is None
