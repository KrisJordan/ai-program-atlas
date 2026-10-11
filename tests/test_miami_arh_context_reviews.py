from copy import deepcopy
import hashlib
from pathlib import Path
from bs4 import BeautifulSoup
import pytest
from atlas.adapters import miami_arh_context_reviews as module
from atlas.adapters.business_society_minors import clean

PID = 'miami-data-science-ai-bs'


@pytest.fixture
def synthetic(monkeypatch):
    spec = deepcopy(module.SPEC)
    spec['courses'] = {c: spec['courses'][c] for c in ['ARH 220', 'ARH 326', 'ARH 385', 'ARH 411']}
    blocks = []
    for code, entry in spec['courses'].items():
        credit = '1-3' if code == 'ARH 385' else '1' if code == 'ARH 220' else '3'
        block = (f'<div class="courseblock"><p class="courseblocktitle">{code}. '
                 f'{entry["name"]}. {credit} Credit Hours.</p>'
                 '<p>Synthetic field description. Prerequisite: TEST 1. '
                 'Requisite: Two additional courses. Components: LEC.</p></div>')
        entry['block_hash'] = hashlib.sha256(clean(BeautifulSoup(block, 'html.parser').get_text(' ', strip=True)).encode()).hexdigest()
        blocks.append(block)
    monkeypatch.setattr(module, 'SPEC', spec)
    return '<h1>Art History (ARH)</h1>' + ''.join(blocks)


def test_range_unknown_subject_and_both_requisite_fields(synthetic):
    result = module.parse(synthetic, pid=PID)
    courses = {c['code']: c for c in result['courses']}
    assert courses['ARH 385']['credits'] is None
    assert result['observed_credit_ranges']['ARH 385'] == {
        'minimum': 1, 'maximum': 3, 'credit_unit': 'semester_hours'}
    assert courses['ARH 220']['credits'] == 1
    assert courses['ARH 411']['prerequisites'] == 'Prerequisite: ARH 225 . Requisite: Two additional art history courses.'
    assert courses['ARH 385']['category'] == 'other'
    assert 'geographical scope is unresolved' in courses['ARH 326']['description']
    assert not {'requirements', 'curriculum_audit', 'last_verified'} & set(result)
    assert all('category_review' not in c for c in courses.values())


@pytest.mark.parametrize('change', ['missing', 'duplicate', 'subject', 'eligibility', 'range', 'heading'])
def test_source_changes_require_review(synthetic, change):
    first = str(BeautifulSoup(synthetic, 'html.parser').select_one('.courseblock'))
    altered = {
        'missing': synthetic.replace(first, ''), 'duplicate': synthetic + first,
        'subject': synthetic.replace('Synthetic field description.', 'Changed content.', 1),
        'eligibility': synthetic.replace('Two additional courses.', 'One additional course.', 1),
        'range': synthetic.replace('1-3 Credit Hours', '3 Credit Hours'),
        'heading': synthetic.replace('Art History (ARH)', 'Wrong chapter'),
    }[change]
    with pytest.raises(ValueError):
        module.parse(altered, pid=PID)


def test_scope_and_prior_observations_survive_composition(synthetic):
    with pytest.raises(ValueError):
        module.parse(synthetic, pid='unreviewed-program')
    old = {'id': PID, 'courses': [{'id': 'earlier-course', 'code': 'TEST 200'}],
           'requirements': [{'id': 'contextual-cognate'}]}
    snapshot = deepcopy(old)
    sources, parsers = [], {module.URL: lambda html: old}
    module.register(PID, sources, parsers)
    callback = parsers[module.URL]
    module.register(PID, sources, parsers)
    assert callback is parsers[module.URL]
    result = callback(synthetic)
    assert old == snapshot and result['requirements'] == old['requirements']
    assert len(result['courses']) == 5


def test_manual_content_scope():
    entries = module.SPEC['courses']
    assert len(entries) == 50
    assert {c for c, e in entries.items() if e['review']['status'] == 'unclassified'} == {
        'ARH 385', 'ARH 411', 'ARH 505', 'ARH 506'}
    assert entries['ARH 326']['name'] == 'Art of Japan'
    assert 'South Asian' in entries['ARH 326']['description']
    assert entries['ARH 560']['review']['candidate_categories'] == ['human_context', 'applications']
    assert entries['ARH 207']['category'] == 'human_context'
    assert entries['ARH 508']['category'] == 'applications'
    assert module.SPEC['sources']['arh']['catalog_year'] is None


def test_optional_actual_source_replay():
    path = Path('.cache/research/miami-degree-audit/arh.html')
    if not path.exists():
        pytest.skip('Copyrighted source capture remains private')
    pids = {p for e in module.SPEC['courses'].values() for p in e['program_ids']}
    assert len(pids) == 4
    for pid in pids:
        records = module.parse(path.read_text(), pid=pid)['courses']
        assert len(records) == 50
        for record in records:
            expected = module.SPEC['courses'][record['code']]
            assert (record['name'], record['credits'], record['prerequisites']) == (
                expected['name'], expected['credits'], expected['prerequisites'])
