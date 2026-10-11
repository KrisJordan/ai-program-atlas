import copy
import hashlib
import json
from functools import partial
from pathlib import Path

import pytest
from atlas.adapters import stevens_option_course_reviews as m
from atlas.adapters.stevens_ai_general_education import parse_graduate_course


def fixture(entry, text='Synthetic reviewed content.', credits=None):
    credits = entry['credits'] if credits is None else credits
    return (f'<article class="flex-1"><h1>{entry["source_heading"]}</h1><h2>{entry["name"]}</h2>'
            f'<div><h3 class="field-label">Course Description</h3><div class="field-value">{text}</div></div>'
            f'<div><h3 class="field-label">Credits</h3><div class="field-value">{credits}</div></div></article>')


def test_identity_content_and_credit_changes_fail_before_stale_observation(monkeypatch):
    entry = copy.deepcopy(m.SPEC['CS 545'])
    entry['description_digest'] = hashlib.sha256(b'Synthetic reviewed content.').hexdigest()
    monkeypatch.setitem(m.SPEC, 'CS 545', entry)
    html = fixture(entry)
    course = m.parse(html, 'CS 545')['courses'][0]
    assert course['category'] == 'other'
    assert course['credit_unit'] == 'unknown'
    assert course['prerequisites'] == entry['description_prerequisites']
    assert 'category_review' not in course
    for changed in (html.replace('Synthetic reviewed','Changed source'), html.replace('>3<','>4<'),
                    html.replace(entry['name'], 'Different version'), html.replace('>CS 545<','>CS 544<')):
        with pytest.raises(ValueError):
            m.parse(changed, 'CS 545')


def test_held_current_version_produces_no_course_metadata(monkeypatch):
    entry = copy.deepcopy(m.SPEC['QF 102'])
    entry['description_digest'] = hashlib.sha256(b'Synthetic reviewed content.').hexdigest()
    monkeypatch.setitem(m.SPEC, 'QF 102', entry)
    assert m.parse(fixture(entry), 'QF 102')['courses'] == []
    with pytest.raises(ValueError):
        m.parse(fixture(entry).replace('Basic Financial Tools', 'A resolved new title'), 'QF 102')


def test_registration_composes_existing_school_observers_and_refuses_unknowns():
    parsers = {m.SPEC[c]['url']: partial(parse_graduate_course, code=c) for c in ('MA 661','BIA 665')}
    sources = list(parsers)
    m.register(sources, parsers)
    m.register(sources, parsers)
    assert len(sources) == len(parsers) == 54
    assert parsers[m.SPEC['MA 661']['url']].func is m.combined
    with pytest.raises(ValueError):
        m.register([], {m.SPEC['PEP 111']['url']: lambda html: {}})


def test_all_represented_subject_dispositions_keep_versions_and_missingness():
    p = json.loads(Path('data/programs/'+m.PID+'.json').read_text())
    courses = {c['code']: c for c in p['courses']}
    assert len(courses) == 79 and all(c.get('category_review') for c in courses.values())
    assert len(m.SPEC) == 54
    assert courses['QF 102']['name'] == 'Introduction to Quantitative Finance II'
    assert courses['QF 102']['description'] is None
    assert 'original precise official title' in courses['QF 102']['category_review']['rationale']
    assert courses['HASS 101']['description'] is None
    assert 'precise official title' in courses['HASS 101']['category_review']['rationale']
    assert courses['HASS 101']['credits'] == 3
    assert courses['MA 661']['category_review']['status'] == 'mixed'
    assert courses['CS 582']['category'] == 'mathematics'
    assert courses['HST 381']['category'] == 'human_context'
    assert courses['CS 105']['category'] == courses['HAR 271']['category'] == 'foundations'
    assert courses['ME 598']['category'] == 'applications'
    assert courses['CS 545']['category_review']['candidate_categories'] == ['human_context','foundations']
    assert all(courses[c]['credit_unit'] == 'unknown' for c in m.SPEC if c != 'QF 102')
    assert p['curriculum_status'] == 'partial'


@pytest.mark.parametrize('code', list(m.SPEC))
def test_optional_actual_public_description_replay(code):
    index_path = Path('/tmp/atlas-stevens-options/index.json')
    if not index_path.exists():
        pytest.skip('Ignored public source captures are not redistributed')
    index = json.loads(index_path.read_text())
    html = (index_path.parent / index[code]['file']).read_text()
    parsers = {m.SPEC[c]['url']: partial(parse_graduate_course, code=c) for c in ('MA 661','BIA 665')}
    m.register(list(parsers), parsers)
    result = parsers[m.SPEC[code]['url']](html)
    assert result['id'] == m.PID
    assert all('category_review' not in c for c in result['courses'])
    if code in ('MA 661','BIA 665'):
        assert len(result['requirements']) == 1
        assert result['requirements'][0]['kind'] == 'note'
    if code == 'QF 102':
        assert result['courses'] == []


def test_independent_named_role_union_does_not_promote_context_or_open_pools():
    from atlas.curriculum_profile import requirement_profile
    from atlas.degree_audit import audit_summary
    p = json.loads(Path('data/programs/'+m.PID+'.json').read_text())
    ledger = json.loads(Path('research/degree-audit/national-degree-batch.json').read_text())
    entry = next(r for r in ledger['programs'] if r['program_id'] == m.PID)
    assert [entry['expected_profile'][r]['count'] for r in ('required','options','unresolved')] == [24,30,25]
    assert 'stevens-hass-101' in entry['expected_course_ids']['unresolved']
    assert 'stevens-cs-545' in entry['expected_course_ids']['options']
    assert 'stevens-hst-381' not in entry['expected_course_ids']['required']
    assert requirement_profile(p)['options']['classification'] == dict(reviewed=24,mixed=6,unclassified=0,unreviewed=0)
    audit_summary({'programs':[entry]}, [p])
