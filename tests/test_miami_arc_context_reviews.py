from copy import deepcopy
import hashlib
from pathlib import Path
from bs4 import BeautifulSoup
import pytest
from atlas.adapters import miami_arc_context_reviews as module
from atlas.adapters.business_society_minors import clean

PID = 'miami-data-science-ai-bs'


@pytest.fixture
def synthetic(monkeypatch):
    spec = deepcopy(module.SPEC)
    spec['courses'] = {c: spec['courses'][c] for c in ['ARC 121', 'ARC 141', 'ARC 293', 'ARC 585']}
    blocks = []
    for code, entry in spec['courses'].items():
        credit = '3-6' if code == 'ARC 141' else '1' if code == 'ARC 121' else '3'
        block = (f'<div class="courseblock"><p class="courseblocktitle">{code}. '
                 f'{entry["name"]}. {credit} Credit Hours.</p>'
                 '<p>Synthetic design scope. Pre-requisite: TEST 1. Components: LEC.</p></div>')
        entry['block_hash'] = hashlib.sha256(clean(BeautifulSoup(block, 'html.parser').get_text(' ', strip=True)).encode()).hexdigest()
        blocks.append(block)
    monkeypatch.setattr(module, 'SPEC', spec)
    return '<h1>Architecture (ARC)</h1>' + ''.join(blocks)


def test_exact_credits_and_source_conditions(synthetic):
    result = module.parse(synthetic, pid=PID)
    records = {c['code']: c for c in result['courses']}
    assert records['ARC 121']['credits'] == 1
    assert records['ARC 121']['prerequisites'] == 'Corequisite: ARC 101, 111.'
    assert records['ARC 293']['prerequisites'] == 'Pre-requisite: ARC 292 .'
    assert records['ARC 141']['credits'] is None
    assert result['observed_credit_ranges']['ARC 141'] == {
        'minimum': 3, 'maximum': 6, 'credit_unit': 'semester_hours'}
    assert records['ARC 585']['category'] == 'other'
    assert 'requirements' not in result
    assert all('category_review' not in c for c in records.values())


@pytest.mark.parametrize('change', ['missing', 'duplicate', 'content', 'prerequisite', 'range', 'heading'])
def test_changed_field_or_missing_record_fails(synthetic, change):
    first = str(BeautifulSoup(synthetic, 'html.parser').select_one('.courseblock'))
    altered = {
        'missing': synthetic.replace(first, ''), 'duplicate': synthetic + first,
        'content': synthetic.replace('Synthetic design scope.', 'Different scope.', 1),
        'prerequisite': synthetic.replace('TEST 1.', 'TEST 2.', 1),
        'range': synthetic.replace('3-6 Credit Hours', '3 Credit Hours'),
        'heading': synthetic.replace('Architecture (ARC)', 'Wrong chapter'),
    }[change]
    with pytest.raises(ValueError):
        module.parse(altered, pid=PID)


def test_scopes_and_composition_preserve_context(synthetic):
    with pytest.raises(ValueError):
        module.parse(synthetic, pid='not-reviewed')
    old = {'id': PID, 'courses': [{'id': 'other', 'code': 'OTHER 1'}],
           'requirements': [{'id': 'contextual-rule'}]}
    snapshot = deepcopy(old)
    sources, parsers = [], {module.URL: lambda html: old}
    module.register(PID, sources, parsers)
    callback = parsers[module.URL]
    module.register(PID, sources, parsers)
    assert callback is parsers[module.URL]
    result = callback(synthetic)
    assert old == snapshot and result['requirements'] == old['requirements']
    assert len(result['courses']) == 5


def test_individual_subject_decisions_and_nonidentity():
    entries = module.SPEC['courses']
    assert len(entries) == 50
    assert {c for c, e in entries.items() if e['review']['status'] == 'unclassified'} == {'ARC 585', 'ARC 586'}
    assert entries['ARC 594']['category'] == 'applications'
    assert entries['ARC 513']['category'] == 'applications'
    assert entries['ARC 267']['category'] == 'human_context'
    assert entries['ARC 109']['review']['candidate_categories'] == ['applications', 'human_context']
    assert 'ARC 544' in entries and 'ARC 644' in entries
    assert entries['ARC 568']['prerequisites'] == 'Corequisite: ARC502.'
    assert module.SPEC['sources']['arc']['catalog_year'] is None


def test_optional_actual_capture():
    path = Path('.cache/research/miami-degree-audit/arc.html')
    if not path.exists():
        pytest.skip('Copyrighted source capture remains private')
    pids = {p for e in module.SPEC['courses'].values() for p in e['program_ids']}
    assert len(pids) == 4
    for pid in pids:
        records = module.parse(path.read_text(), pid=pid)['courses']
        assert len(records) == 50
        assert all(c['credits'] == module.SPEC['courses'][c['code']]['credits'] for c in records)
