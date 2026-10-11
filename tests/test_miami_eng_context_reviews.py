"""Meaningful changes and source-scope boundaries for the English contribution."""
from collections import Counter
from copy import deepcopy
import hashlib
from pathlib import Path

from bs4 import BeautifulSoup
import pytest
from atlas.adapters import miami_eng_context_reviews as module
from atlas.adapters.business_society_minors import clean

PID = 'miami-data-science-ai-bs'


@pytest.fixture
def synthetic(monkeypatch):
    spec = deepcopy(module.SPEC)
    spec['courses'] = {c: spec['courses'][c] for c in ['ENG 250', 'ENG 319', 'ENG 344']}
    blocks = []
    for code, entry in spec['courses'].items():
        credit = '1-5' if code == 'ENG 250' else '3'
        block = (f'<div class="courseblock"><p class="courseblocktitle">{code}. '
                 f'{entry["name"]}. {credit} Credit Hours.</p>'
                 '<p>Synthetic subject description. Prerequisite: TEST 101 or TEST 102. '
                 'Components: LEC.</p></div>')
        entry['block_hash'] = hashlib.sha256(clean(BeautifulSoup(block, 'html.parser').get_text(' ', strip=True)).encode()).hexdigest()
        blocks.append(block)
    monkeypatch.setattr(module, 'SPEC', spec)
    return '<h1>English and Creative Writing (ENG)</h1>' + ''.join(blocks)


def test_observes_range_without_scalar_or_review_promotion(synthetic):
    result = module.parse(synthetic, pid=PID)
    records = {c['code']: c for c in result['courses']}
    assert records['ENG 250']['credits'] is None
    assert result['observed_credit_ranges']['ENG 250'] == {
        'minimum': 1, 'maximum': 5, 'credit_unit': 'semester_hours'}
    assert records['ENG 344']['credits'] == 3
    assert 'requirements' not in result and 'curriculum_audit' not in result
    assert 'last_verified' not in result
    assert all('category_review' not in c for c in records.values())


@pytest.mark.parametrize('change', ['missing', 'duplicate', 'description', 'eligibility', 'credits', 'heading', 'login'])
def test_source_changes_and_wrong_page_fail_closed(change, synthetic):
    soup = BeautifulSoup(synthetic, 'html.parser')
    first = str(soup.select_one('.courseblock'))
    altered = {
        'missing': synthetic.replace(first, ''),
        'duplicate': synthetic + first,
        'description': synthetic.replace('Synthetic subject description.', 'Changed subject.', 1),
        'eligibility': synthetic.replace('TEST 101 or TEST 102', 'TEST 101 and TEST 102', 1),
        'credits': synthetic.replace('1-5 Credit Hours', '3 Credit Hours', 1),
        'heading': synthetic.replace('English and Creative Writing (ENG)', 'Other chapter'),
        'login': '<h1>Sign in</h1><form>Password</form>',
    }[change]
    with pytest.raises(ValueError):
        module.parse(altered, pid=PID)


def test_scope_and_composition_preserve_existing_requirements(synthetic):
    with pytest.raises(ValueError):
        module.parse(synthetic, pid='unreviewed-program')
    old = {'id': PID, 'courses': [{'id': 'existing', 'code': 'TEST 200'}],
           'requirements': [{'id': 'preserve-local-rule'}],
           'observed_credit_ranges': {'TEST 200': {'minimum': 1, 'maximum': 2}}}
    before = deepcopy(old)
    sources, parsers = [], {module.URL: lambda html: old}
    module.register(PID, sources, parsers)
    callback = parsers[module.URL]
    module.register(PID, sources, parsers)
    assert parsers[module.URL] is callback and sources == [module.URL]
    observed = callback(synthetic)
    assert old == before and observed['requirements'] == old['requirements']
    assert len(observed['courses']) == 4
    assert 'TEST 200' in observed['observed_credit_ranges']


def test_manual_dispositions_preserve_specific_uncertainty():
    entries = module.SPEC['courses']
    assert len(entries) == 143
    assert Counter(c['category'] for c in entries.values()) == {'human_context': 120, 'other': 23}
    unknown = {f'ENG {n}' for n in [250,251,253,254,255,257,258,259,*range(350,360),395,396,397,495,595]}
    assert {c for c,e in entries.items() if e['review']['status'] == 'unclassified'} == unknown
    assert entries['ENG 344']['category'] == 'human_context'
    assert entries['ENG 493']['review']['rationale'].startswith('Limited exact-title')
    assert 'concurrently' in entries['ENG 319']['prerequisites']
    assert entries['ENG 350']['credits'] == 3
    assert sum(e['credit_range'] is not None for e in entries.values()) == 17
    assert module.SPEC['sources']['eng']['catalog_year'] is None


def test_optional_actual_source_replay_all_four_scopes():
    path = Path('.cache/research/miami-degree-audit/eng.html')
    if not path.exists():
        pytest.skip('Raw official capture deliberately uncommitted')
    html = path.read_text()
    pids = {p for e in module.SPEC['courses'].values() for p in e['program_ids']}
    assert len(pids) == 4
    for pid in pids:
        result = module.parse(html, pid=pid)
        assert len(result['courses']) == 143
        for c in result['courses']:
            e = module.SPEC['courses'][c['code']]
            assert (c['name'],c['credits'],c['prerequisites']) == (e['name'],e['credits'],e['prerequisites'])
