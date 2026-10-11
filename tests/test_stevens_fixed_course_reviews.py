import copy
import hashlib
import json
from pathlib import Path

import pytest
from atlas.adapters import stevens_fixed_course_reviews as m


def fixture(code, name, text, eligibility=False, credits=3):
    label = 'Student Eligibility Rule' if eligibility else 'Course Description'
    block = '' if text is None else f'<div><h3 class="field-label">{label}</h3><div class="field-value">{text}</div></div>'
    if not eligibility:
        block += f'<div><h3 class="field-label">Credits</h3><div class="field-value">{credits}</div></div>'
    tab = 'Eligibility' if eligibility else 'Course Information'
    return f'<article class="flex-1"><h1>{code}</h1><h2>{name}</h2><a role="tab" aria-selected="true">{tab}</a>{block}</article>'


def test_synthetic_observation_is_guarded_not_manual_review(monkeypatch):
    entry = copy.deepcopy(m.SPEC['CS 583'])
    entry['description_digest'] = hashlib.sha256(b'Synthetic neural methods.').hexdigest()
    entry['eligibility_digest'] = hashlib.sha256(b'A or B and (C or D)').hexdigest()
    monkeypatch.setitem(m.SPEC, 'CS 583', entry)
    html = fixture('CS 583', entry['name'], 'Synthetic neural methods.')
    observed = m.parse(html, 'CS 583')['courses'][0]
    assert 'category_review' not in observed
    assert observed['credit_unit'] == 'unknown'
    assert observed['prerequisites'] == entry['description_prerequisites']
    rule = m.parse(fixture('CS 583', entry['name'], 'A or B and (C or D)', True), 'CS 583', True)['courses'][0]
    assert rule['prerequisites'].endswith('Published eligibility: A or B and (C or D)')
    for changed in (html.replace('Synthetic neural', 'Changed neural'), html.replace('>3<', '>4<'), html.replace(entry['name'], 'Different title'), html.replace('Course Information</a>', 'Eligibility</a>')):
        with pytest.raises(ValueError):
            m.parse(changed, 'CS 583')


def test_blank_rule_requires_settled_selected_eligibility():
    entry = m.SPEC['CS 101']
    blank = fixture('CS 101', entry['name'], None, True)
    assert m.parse(blank, 'CS 101', True)['courses'][0]['prerequisites'] is None
    with pytest.raises(ValueError):
        m.parse(blank.replace('Eligibility</a>', 'Course Information</a>'), 'CS 101', True)
    with pytest.raises(ValueError):
        m.parse(fixture('CS 101', entry['name'], 'New rule', True), 'CS 101', True)


def test_exact_scope_classification_and_registration():
    assert set(m.SPEC) == {'HASS 103','CS 101','CS 115','MA 121','MA 122','PRV 101','HASS 105','CS 284','MA 125','MA 126','CS 367','CS 385','MA 223','MGT 103','MA 331','CS 334','CS 559','CS 583','CS 423','CS 424'}
    assert m.SPEC['CS 101']['category_review']['status'] == 'unclassified'
    assert m.SPEC['PRV 101']['category_review']['status'] == 'mixed'
    assert m.SPEC['CS 423']['category'] == m.SPEC['CS 424']['category'] == 'foundations'
    assert len(m.SPEC['CS 424']['category_review']['source_ids']) == 2
    assert m.SPEC['CS 559']['eligibility_rule'] == '(MA 223 and MA 331) or CS 556'
    sources, parsers = [], {}
    m.register(sources, parsers)
    m.register(sources, parsers)
    assert len(sources) == len(parsers) == 40
    with pytest.raises(ValueError):
        m.register([], {m.SPEC['CS 101']['url']: lambda x: {}})


def test_optional_actual_rendered_capture():
    path = Path('/tmp/stevens-fixed-course-captures.json')
    if not path.exists():
        pytest.skip('Ignored public UI captures are not distributed')
    captures = json.loads(path.read_text())['captures']
    assert len(captures) == 40
    for capture in captures:
        out = m.parse(capture['html'], capture['code'], capture['kind'] == 'eligibility')
        assert out['courses'][0]['id'] == m.SPEC[capture['code']]['id']
        assert 'category_review' not in out['courses'][0]
