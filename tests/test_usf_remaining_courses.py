from importlib import import_module
import hashlib
import json
from pathlib import Path

import pytest

PID = 'university-of-south-florida-artificial-intelligence-bs-degree'
module = import_module('atlas.adapters.' + PID + '.remaining_courses')
adapter = import_module('atlas.adapters.' + PID + '.adapter')


def test_manual_course_content_decisions_and_uncertainty():
    from atlas.db import validate_program
    p = json.loads((Path('data/programs') / (PID + '.json')).read_text())
    validate_program(p)
    c = {row['code']: row for row in p['courses']}
    assert all(row['description'] and row.get('category_review') for row in c.values())
    expected = {
        'foundations': {'COP 2510', 'COP 3514', 'COP 4530', 'COT 4400'},
        'mathematics': {'MAC 2311', 'MAC 2312', 'COT 3100', 'EGN 4450', 'EGN 2440', 'STA 2023'},
        'systems': {'CDA 3103', 'CAI 4624'},
        'applications': {'PHY 2048', 'PHY 2048L', 'PSY 2012'},
        'human_context': {'ENC 1101', 'ENC 1102', 'POS 2041', 'AMH 2010', 'AMH 2020', 'CAI 4024'},
        'ai_ml': {'CAI 1000', 'CAI 2001', 'CAI 4002', 'CAI 4105', 'CAI 4203', 'CAI 4841', 'CAP 4641'},
        'other': {'CIS 1930'},
    }
    # This test owns the original 29 brochure/civic identities; GE additions have their own audit.
    original = set().union(*expected.values())
    c = {code: row for code, row in c.items() if code in original}
    assert len(c) == 29
    assert {key: {code for code, row in c.items() if row['category'] == key}
            for key in expected} == expected
    assert c['CIS 1930']['category_review']['status'] == 'unclassified'
    assert c['CIS 1930']['credits'] == 1
    assert c['EGN 4450']['credits'] == 2
    assert c['MAC 2311']['credits'] == c['MAC 2312']['credits'] == 4
    assert 'AND' in c['EGN 4450']['prerequisites'] and 'OR' in c['EGN 4450']['prerequisites']
    assert 'Consent of Instructor or Department' in c['COP 3514']['prerequisites']
    assert 'dropped simultaneously' in c['PHY 2048']['prerequisites']
    assert c['POS 2041']['prerequisites'] is None
    assert all(row['credit_unit'] == 'unknown' for row in c.values())
    assert 'course_identity_groups' not in p  # Credit exclusions do not certify aliases.
    assert p['curriculum_status'] == 'partial'


@pytest.mark.parametrize('review', module.REVIEWS, ids=lambda r: r['code'])
def test_actual_permitted_course_replay(review):
    path = Path('.cache/http') / (hashlib.sha256(review['url'].encode()).hexdigest() + '.body')
    if not path.exists():
        pytest.skip('Optional ignored permitted source cache unavailable')
    html = path.read_text()
    result = adapter.SOURCE_PARSERS[review['url']](html)
    seed = json.loads((Path('data/programs') / (PID + '.json')).read_text())
    expected = next(c for c in seed['courses'] if c['id'] == review['course_id'])
    observed = result['courses'][0]
    for field in ('id', 'code', 'name', 'description', 'prerequisites', 'credits', 'credit_unit', 'category', 'url', 'source_id'):
        assert observed[field] == expected[field]
    assert 'category_review' not in observed
    assert not {'requirements', 'curriculum_audit', 'curriculum_status'} & result.keys()
    with pytest.raises(ValueError):
        adapter.SOURCE_PARSERS[review['url']]('<h1>Access denied</h1>' + html)


def synthetic_source():
    values = dict.fromkeys(module.FIELDS, '')
    values.update(lblDescription='A synthetic orientation description.', lblcredithours='1',
                  lblprereq='AA 1000 OR BB 1000', lblOtherInfo='Permission required.')
    heading = 'CIS 1930: Synthetic orientation'
    html = '<main><h1>Course Details</h1><h2>' + heading + '</h2>'
    html += ''.join('<span id="MainContent_' + k + '">' + v + '</span>' for k, v in values.items()) + '</main>'
    review = dict(next(r for r in module.REVIEWS if r['code'] == 'CIS 1930'))
    review['observed_fields_sha256'] = hashlib.sha256(json.dumps(
        {'heading': heading, 'fields': values}, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return html, review


@pytest.mark.parametrize('old,new', [('synthetic orientation description', 'changed description'),
    ('>1</span>', '>2</span>'), ('AA 1000 OR BB 1000', 'AA 1000 AND BB 1000'),
    ('Permission required.', 'Permission waived.'), ('Synthetic orientation', 'Renamed course'),
    ('MainContent_lblcoprereq', 'missing-coprerequisite')])
def test_any_reviewed_field_change_requires_review(old, new):
    html, review = synthetic_source()
    assert module.parse_reviewed_course(html, review)['courses'][0]['credits'] == 1
    with pytest.raises(ValueError):
        module.parse_reviewed_course(html.replace(old, new), review)
