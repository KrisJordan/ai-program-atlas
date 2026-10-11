"""Source guards and composition for independently reviewed Miami CSC options."""
import hashlib
from copy import deepcopy
from pathlib import Path

import pytest
from atlas.adapters import miami_csc_option_reviews as module
from atlas.adapters.business_society_minors import clean
from bs4 import BeautifulSoup

BS = 'miami-data-science-ai-bs'
BA = 'university-of-miami-data-science-and-artificial-intelligence-ba-degree'
CODES = {'CSC '+n for n in ['115','210','322','329','405','410','411','412','423','431','506','542','543','548','549','550']}


@pytest.fixture
def synthetic(monkeypatch):
    spec = deepcopy(module.SPEC)
    blocks = []
    for code, entry in spec.items():
        raw = '1-3' if code in {'CSC 410', 'CSC 411', 'CSC 412'} else '1' if code == 'CSC 405' else '3'
        label = 'Credit Hour' if raw == '1' else 'Credit Hours'
        pre = ('Pre/Corequisite: TEST 101 or TEST score of 10.' if code == 'CSC 115'
               else 'Prerequisite: TEST101 or TEST102 and TEST103 or TEST104.')
        block = (f'<div class="courseblock"><p class="courseblocktitle">{code}. '
                 f'{entry["name"]}. {raw} {label}.</p><p>Synthetic reviewed content. '
                 f'{pre} Components: LEC. Grading: GRD.</p></div>')
        entry['digest'] = hashlib.sha256(clean(BeautifulSoup(block, 'html.parser').get_text(' ', strip=True)).encode()).hexdigest()
        blocks.append(block)
    monkeypatch.setattr(module, 'SPEC', spec)
    return '<h1>Computer Science (CSC)</h1>' + ''.join(blocks)


@pytest.mark.parametrize('pid', [BS, BA])
def test_singular_and_variable_credits_exact_conditions_no_manual_review(pid, synthetic):
    result = module.parse(synthetic, pid)
    courses = {c['code']: c for c in result['courses']}
    assert set(courses) == (CODES if pid == BS else CODES - {'CSC 506'})
    assert courses['CSC 405']['credits'] == 1
    for code in ['CSC 410', 'CSC 411', 'CSC 412']:
        assert courses[code]['credits'] is None
        assert result['observed_credit_ranges'][code] == {
            'minimum': 1, 'maximum': 3, 'credit_unit': 'semester_hours'}
        assert '1–3' in courses[code]['description']
    assert courses['CSC 115']['prerequisites'].startswith('Pre/Corequisite:')
    if pid == BS:
        assert courses['CSC 506']['prerequisites'] == 'Prerequisite: TEST101 or TEST102 and TEST103 or TEST104.'
    assert 'last_verified' not in result and 'curriculum_audit' not in result
    assert all('category_review' not in c for c in courses.values())


def test_missing_duplicate_changed_source_and_wrong_directory_fail(synthetic):
    first = BeautifulSoup(synthetic, 'html.parser').select_one('.courseblock')
    for html in [synthetic.replace(str(first), ''), synthetic + str(first),
                 synthetic.replace('Synthetic reviewed content.', 'Changed content.', 1),
                 synthetic.replace('Computer Science (CSC)', 'Unrelated directory')]:
        with pytest.raises(ValueError):
            module.parse(html, BS)


def test_register_composes_existing_response_without_losing_requirements(synthetic):
    sources = [module.URL]
    previous = {'id': BS, 'courses': [{'id': BS+'-csc-315', 'code': 'CSC 315'}],
                'requirements': [{'id': 'keep-primary-policy'}], 'primary_observation': True}
    original = deepcopy(previous)
    parsers = {module.URL: lambda html: previous}
    module.register(BS, sources, parsers)
    callback = parsers[module.URL]
    module.register(BS, sources, parsers)
    assert parsers[module.URL] is callback and sources == [module.URL]
    merged = callback(synthetic)
    assert len(merged['courses']) == 17
    assert merged['requirements'] == previous['requirements']
    assert merged['primary_observation'] is True and previous == original
    duplicate = {'id': BS, 'courses': [module.parse(synthetic, BS)['courses'][0]]}
    with pytest.raises(ValueError, match='Duplicate'):
        module._compose(lambda html: duplicate, synthetic, BS)


def test_declared_subject_decisions_not_inferred_from_application_pool():
    assert set(module.SPEC) == CODES
    expected = {'CSC 115': 'foundations', 'CSC 210': 'other', 'CSC 322': 'systems',
                'CSC 329': 'foundations', 'CSC 405': 'other', 'CSC 410': 'foundations',
                'CSC 411': 'foundations', 'CSC 412': 'other', 'CSC 423': 'systems',
                'CSC 431': 'foundations', 'CSC 506': 'other', 'CSC 542': 'ai_ml',
                'CSC 543': 'ai_ml', 'CSC 548': 'other', 'CSC 549': 'other', 'CSC 550': 'applications'}
    assert {code: e['category'] for code, e in module.SPEC.items()} == expected
    for code, entry in module.SPEC.items():
        assert set(entry['program_ids']) == ({BS} if code == 'CSC 506' else {BS, BA})
        assert entry['rationale'] and entry['description']
        if entry['review_status'] == 'mixed':
            assert entry['category'] == 'other' and len(entry['candidate_categories']) >= 2


def test_optional_actual_source_replay():
    path = Path('.cache/http') / (hashlib.sha256(module.URL.encode()).hexdigest()+'.body')
    if not path.exists():
        pytest.skip('Raw official cache deliberately uncommitted')
    result = module.parse(path.read_text(), BS)
    assert len(result['courses']) == 16
    for c in result['courses']:
        expected = module.SPEC[c['code']]
        assert (c['name'], c['credits'], c['prerequisites']) == (
            expected['name'], expected['credits'], expected['prerequisites'])
