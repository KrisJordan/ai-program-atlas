from html import escape

import pytest

from atlas.adapters import stevens_option_eligibility_reviews as m


def fixture(code):
    entry = m.SPEC[code]
    rule = entry['eligibility_rule']
    field = (f'<div><h3 class="field-label">Student Eligibility Rule</h3>'
             f'<div class="field-value">{escape(rule)}</div></div>') if rule else ''
    return (f'<article class="flex-1"><h1>{code}</h1><h2>{entry["name"]}</h2>'
            '<div role="tab" aria-selected="true">Eligibility</div>' + field + '</article>')


def test_boolean_conditions_and_description_preparation_survive_without_regrouping():
    for code in ('CS 545', 'CS 584', 'CS 589'):
        course = m.parse(fixture(code), code)['courses'][0]
        assert course['prerequisites'].endswith(m.SPEC[code]['eligibility_rule'])
        prior = m.SPEC[code].get('description_prerequisites')
        if prior:
            assert course['prerequisites'].startswith(prior + ' Published eligibility: ')
        assert 'category_review' not in course
        assert 'credits' not in course


def test_blank_tab_is_not_a_null_prerequisite_observation():
    # CH 115's information tab explicitly has a corequisite, despite blank eligibility.
    assert m.SPEC['CH 115']['description_prerequisites'] == 'Corequisite: CH 117.'
    assert m.parse(fixture('CH 115'), 'CH 115')['courses'] == []
    assert m.parse(fixture('BIO 181'), 'BIO 181')['courses'] == []


def test_reject_wrong_identity_tab_transition_new_field_and_changed_rule():
    html = fixture('PEP 112')
    for changed in (
        html.replace('PEP 112', 'PEP 111'),
        html.replace('Electricity and Magnetism', 'Different title'),
        html.replace('>Eligibility<', '>Course Information<'),
        html.replace('and PEP 111', 'or PEP 111'),
        html.replace('</article>', '<h3>Course Description</h3></article>'),
        html.replace('</article>', '<h3>Permission required</h3></article>'),
        html.replace('</article>', '<div aria-busy="true"></div></article>'),
    ):
        with pytest.raises(ValueError):
            m.parse(changed, 'PEP 112')
    with pytest.raises(ValueError):
        m.parse('<h1>Let us confirm you are human</h1>', 'PEP 112')
    with pytest.raises(ValueError):
        m.parse('', 'ENGR 116')


def test_manifest_keeps_reviewed_blank_and_blocked_sources_distinct():
    assert len(m.SPEC) == 54
    assert sum(x['review_status'] == 'reviewed_rule' for x in m.SPEC.values()) == 18
    assert sum(x['review_status'] == 'reviewed_no_published_rule' for x in m.SPEC.values()) == 14
    assert sum(x['review_status'] == 'blocked_by_public_browser_challenge' for x in m.SPEC.values()) == 22
    assert m.SPEC['QF 102']['held']
    assert m.SPEC['HASS 101']['review_status'] == 'blocked_by_public_browser_challenge'
    sources, parsers = [], {}
    m.register(sources, parsers)
    m.register(sources, parsers)
    assert len(sources) == len(parsers) == 32
    assert all('/eligibility-6OfL6' in url for url in sources)
    with pytest.raises(ValueError):
        m.register([], {sources[0]: lambda html: {}})
