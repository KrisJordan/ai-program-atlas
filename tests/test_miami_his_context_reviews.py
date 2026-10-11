"""History evidence review preserves open eligibility and unclassified content."""
from collections import Counter
from copy import deepcopy
import hashlib
from pathlib import Path

from bs4 import BeautifulSoup
import pytest
from atlas.adapters import miami_his_context_reviews as module
from atlas.adapters.business_society_minors import clean

PID = 'miami-data-science-ai-bs'


@pytest.fixture
def synthetic(monkeypatch):
    spec = deepcopy(module.SPEC)
    selected = ['HIS 192', 'HIS 315', 'HIS 382', 'HIS 397']
    spec['courses'] = {c: spec['courses'][c] for c in selected}
    blocks = []
    for code, entry in spec['courses'].items():
        credit = '1-5' if code == 'HIS 192' else '0-3' if code == 'HIS 382' else '3'
        block = (f'<div class="courseblock"><p class="courseblocktitle">{code}. '
                 f'{entry["name"]}. {credit} Credit Hours.</p>'
                 '<p>Synthetic historical scope. Prerequisite: One TEST course. '
                 'Components: LEC.</p></div>')
        entry['block_hash'] = hashlib.sha256(clean(BeautifulSoup(block, 'html.parser').get_text(' ', strip=True)).encode()).hexdigest()
        blocks.append(block)
    monkeypatch.setattr(module, 'SPEC', spec)
    return '<h1>History (HIS)</h1>' + ''.join(blocks)


def test_zero_lower_bound_is_range_not_free_or_zero_credit(synthetic):
    result = module.parse(synthetic, pid=PID)
    courses = {c['code']: c for c in result['courses']}
    assert courses['HIS 382']['credits'] is None
    assert result['observed_credit_ranges']['HIS 382'] == {
        'minimum': 0, 'maximum': 3, 'credit_unit': 'semester_hours'}
    assert courses['HIS 315']['prerequisites'] == 'Prerequisite: One HIS Course.'
    assert courses['HIS 397']['prerequisites'] == 'Faculty approval and close faculty supervision are required.'
    assert courses['HIS 397']['category'] == 'other'
    assert not {'requirements','curriculum_audit','last_verified'} & set(result)
    assert all('category_review' not in c for c in courses.values())


@pytest.mark.parametrize('change', ['missing','duplicate','subject','eligibility','range','heading','login'])
def test_changed_reviewed_block_or_wrong_page_requires_new_review(synthetic, change):
    soup = BeautifulSoup(synthetic, 'html.parser')
    first = str(soup.select_one('.courseblock'))
    altered = {
        'missing': synthetic.replace(first, ''), 'duplicate': synthetic + first,
        'subject': synthetic.replace('Synthetic historical scope.', 'Different topic.', 1),
        'eligibility': synthetic.replace('One TEST course.', 'Two TEST courses.', 1),
        'range': synthetic.replace('0-3 Credit Hours', '3 Credit Hours'),
        'heading': synthetic.replace('History (HIS)', 'Unrelated chapter'),
        'login': '<h1>Login</h1><form>Institutional account required</form>',
    }[change]
    with pytest.raises(ValueError):
        module.parse(altered, pid=PID)


def test_composition_scope_and_idempotence(synthetic):
    with pytest.raises(ValueError):
        module.parse(synthetic, pid='not-reviewed')
    old = {'id': PID, 'courses': [{'id': 'existing', 'code': 'TEST 200'}],
           'requirements': [{'id': 'existing-requirement'}],
           'observed_credit_ranges': {'TEST 200': {'minimum': 1, 'maximum': 2}}}
    snapshot = deepcopy(old)
    sources, parsers = [], {module.URL: lambda html: old}
    module.register(PID, sources, parsers)
    callback = parsers[module.URL]
    module.register(PID, sources, parsers)
    assert callback is parsers[module.URL] and sources == [module.URL]
    result = callback(synthetic)
    assert old == snapshot and result['requirements'] == old['requirements']
    assert len(result['courses']) == 5 and 'TEST 200' in result['observed_credit_ranges']


def test_manual_subject_dispositions_and_edition_are_explicit():
    entries = module.SPEC['courses']
    unknown = {f'HIS {n}' for n in [192,193,194,292,293,294,296,392,393,394,396,397,592,593,594]}
    assert len(entries) == 151
    assert Counter(e['category'] for e in entries.values()) == {'human_context':136,'other':15}
    assert {c for c,e in entries.items() if e['review']['status'] == 'unclassified'} == unknown
    assert sum(e['credit_range'] is not None for e in entries.values()) == 13
    assert entries['HIS 501']['category'] == 'human_context'  # actual description specifies African history
    assert entries['HIS 330']['category'] == 'human_context'  # historical scientific change, not physics methods
    assert entries['HIS 316']['prerequisites'] == 'Prerequisite: One HIS Course.'
    assert module.SPEC['sources']['his']['catalog_year'] is None
    assert 'course-information/' in module.SPEC['credit_unit_evidence']['url']


def test_optional_actual_capture_replay_for_all_four_scopes():
    path = Path('.cache/research/miami-degree-audit/his.html')
    if not path.exists():
        pytest.skip('Official raw capture is deliberately uncommitted')
    pids = {p for e in module.SPEC['courses'].values() for p in e['program_ids']}
    assert len(pids) == 4
    for pid in pids:
        result = module.parse(path.read_text(), pid=pid)
        assert len(result['courses']) == 151
        for record in result['courses']:
            expected = module.SPEC['courses'][record['code']]
            assert (record['name'],record['credits'],record['prerequisites']) == (
                expected['name'],expected['credits'],expected['prerequisites'])
