from copy import deepcopy
import hashlib
from pathlib import Path

from bs4 import BeautifulSoup
import pytest
from atlas.adapters import miami_apy_context_reviews as module
from atlas.adapters.business_society_minors import clean

PID = 'miami-data-science-ai-bs'


@pytest.fixture
def synthetic(monkeypatch):
    spec = deepcopy(module.SPEC)
    spec['courses'] = {c: spec['courses'][c] for c in ['APY 312', 'APY 418', 'APY 423', 'APY 501']}
    blocks = []
    for code, entry in spec['courses'].items():
        credit = '2-6' if code == 'APY 501' else '3'
        block = (f'<div class="courseblock"><p class="courseblocktitle">{code}. '
                 f'{entry["name"]}. {credit} Credit Hours.</p>'
                 '<p>Synthetic field description. Prerequisite: TEST 1 or permission. '
                 'Components: LEC.</p></div>')
        entry['block_hash'] = hashlib.sha256(clean(BeautifulSoup(block, 'html.parser').get_text(' ', strip=True)).encode()).hexdigest()
        blocks.append(block)
    monkeypatch.setattr(module, 'SPEC', spec)
    return '<h1>Anthropology (APY)</h1>' + ''.join(blocks)


def test_variable_credit_and_conditional_permission_are_preserved(synthetic):
    result = module.parse(synthetic, pid=PID)
    courses = {c['code']: c for c in result['courses']}
    assert courses['APY 501']['credits'] is None
    assert result['observed_credit_ranges']['APY 501'] == {
        'minimum': 2, 'maximum': 6, 'credit_unit': 'semester_hours'}
    assert courses['APY 423']['prerequisites'] == 'Prerequisite: APY 414 and APY 416 Or Instructor Permission.'
    assert courses['APY 312']['category'] == 'applications'
    assert courses['APY 418']['category'] == 'other'
    assert not {'requirements', 'curriculum_audit', 'last_verified'} & set(result)
    assert all('category_review' not in c for c in courses.values())


@pytest.mark.parametrize('change', ['missing', 'duplicate', 'subject', 'eligibility', 'range', 'heading', 'login'])
def test_changed_source_requires_review(synthetic, change):
    first = str(BeautifulSoup(synthetic, 'html.parser').select_one('.courseblock'))
    altered = {
        'missing': synthetic.replace(first, ''), 'duplicate': synthetic + first,
        'subject': synthetic.replace('Synthetic field description.', 'Different topic.', 1),
        'eligibility': synthetic.replace('TEST 1 or permission.', 'TEST 2.', 1),
        'range': synthetic.replace('2-6 Credit Hours', '6 Credit Hours'),
        'heading': synthetic.replace('Anthropology (APY)', 'Unrelated chapter'),
        'login': '<h1>Login</h1><form>Account required</form>',
    }[change]
    with pytest.raises(ValueError):
        module.parse(altered, pid=PID)


def test_composition_retains_prior_observations_and_requirements(synthetic):
    with pytest.raises(ValueError):
        module.parse(synthetic, pid='not-reviewed')
    old = {'id': PID, 'courses': [{'id': 'earlier-apy-313', 'code': 'APY 313'}],
           'requirements': [{'id': 'contextual-cognate-rule'}]}
    snapshot = deepcopy(old)
    sources, parsers = [], {module.URL: lambda html: old}
    module.register(PID, sources, parsers)
    callback = parsers[module.URL]
    module.register(PID, sources, parsers)
    assert callback is parsers[module.URL] and sources == [module.URL]
    result = callback(synthetic)
    assert old == snapshot and result['requirements'] == old['requirements']
    assert len(result['courses']) == 5


def test_review_scope_and_subject_distinctions():
    entries = module.SPEC['courses']
    assert len(entries) == 52 and 'APY 313' not in entries
    assert entries['APY 312']['category'] == 'applications'  # biological cognition, not AI
    assert entries['APY 390']['category'] == 'human_context'  # ethics, not osteology
    assert entries['APY 414']['category'] == 'applications'  # skeletal identification
    assert entries['APY 418']['review']['status'] == 'unclassified'
    assert entries['APY 423']['review']['candidate_categories'] == ['applications', 'human_context']
    assert module.SPEC['sources']['apy']['catalog_year'] is None
    assert 'course-information/' in module.SPEC['credit_unit_evidence']['url']


def test_optional_source_replay():
    path = Path('.cache/research/miami-degree-audit/apy.html')
    if not path.exists():
        pytest.skip('Copyrighted source capture stays private')
    pids = {p for e in module.SPEC['courses'].values() for p in e['program_ids']}
    assert len(pids) == 4
    for pid in pids:
        records = module.parse(path.read_text(), pid=pid)['courses']
        assert len(records) == 52
        for record in records:
            expected = module.SPEC['courses'][record['code']]
            assert (record['name'], record['credits'], record['prerequisites']) == (
                expected['name'], expected['credits'], expected['prerequisites'])
