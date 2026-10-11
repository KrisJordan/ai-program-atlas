import copy
import hashlib
from pathlib import Path

import pytest

from atlas.adapters import ucsd_engineering_reviews as review


def fixture(monkeypatch, code='ECE 25', body='Digital circuits. Prerequisites: none.'):
    spec = copy.deepcopy(review.SPEC)
    entry = next(e for e in spec['entries'] if e['code'] == code)
    entry['description_hash'] = hashlib.sha256(body.encode()).hexdigest()
    spec['entries'] = [entry]; key = entry['source_key']
    html = (f'<h1>{spec["sources"][key]["heading"]}</h1><h2>Courses</h2>'
            '<p>For course descriptions not found in the UC San Diego General Catalog 2026–27, contact the department.</p>'
            '<h2>Upper Division</h2>'
            f'<p class="course-name">{entry["heading"]}</p>'
            f'<p class="course-descriptions">{body}</p>')
    spec['sources'][key]['chapter_context_sha256'] = review.chapter_context_hash(html)
    monkeypatch.setattr(review, 'SPEC', spec)
    return html


def test_metadata_only_explicit_none(monkeypatch):
    out = review.parse_observations(fixture(monkeypatch)); c = out['courses'][0]
    assert set(out) == {'id', 'courses', 'source_dispositions'}
    assert c['credits'] == 4 and c['credit_unit'] == 'quarter_hours'
    assert c['prerequisites'] == 'none.' and c['category'] == 'systems'
    assert 'category_review' not in c


@pytest.mark.parametrize('transform,match', [
    (lambda s: s.replace('Digital circuits.', 'Unrelated research.'), 'source changed'),
    (lambda s: s.replace('Prerequisites: none.', 'Prerequisites: approval.'), 'source changed'),
    (lambda s: s.replace('(4)', '(6)'), 'source changed'),
    (lambda s: s + '<p>New credit exclusion.</p>', 'source changed'),
    (lambda s: s.replace('2026–27', '2027–28'), 'edition changed'),
    (lambda s: s.replace('Electrical and Computer Engineering (ECE)', 'Other chapter'), 'Expected one'),
    (lambda s: s + s, 'edition changed'),
    (lambda s: s + '<input type="password">', 'Access page'),
])
def test_material_source_guards(monkeypatch, transform, match):
    with pytest.raises(ValueError, match=match):
        review.parse_observations(transform(fixture(monkeypatch)))


def test_duplicate_course_and_section_policy_changes(monkeypatch):
    html = fixture(monkeypatch)
    with pytest.raises(ValueError, match='Duplicate'):
        review.parse_observations(html + '<p class="course-name">ECE 25. Duplicate (4)</p>')
    with pytest.raises(ValueError, match='chapter context changed'):
        review.parse_observations(html.replace('<h2>Upper Division</h2>', '<h2>Upper Division</h2><p>New restriction.</p>'))


def test_complete_nested_and_unwrapped_course_text(monkeypatch):
    html = fixture(monkeypatch, body='Circuits. Conditions apply. Prerequisites: approval.')
    html = html.replace('Circuits. Conditions apply. Prerequisites: approval.',
                        '<strong>Circuits.</strong></p>Conditions apply.<div><p>Prerequisites: approval.</p></div><p>')
    assert review.parse_observations(html)['courses'][0]['prerequisites'] == 'approval.'
    with pytest.raises(ValueError, match='source changed'):
        review.parse_observations(html.replace('Conditions apply.', ''))


def test_missing_heading_and_title_hold(monkeypatch):
    original = review.SPEC
    missing = next(e for e in original['entries'] if e['code'] == 'MAE 124')
    html = fixture(monkeypatch, 'MAE 118')
    assert review.parse_observations(html)['source_dispositions'][0]['status'] == 'source_title_conflict'
    monkeypatch.setattr(review, 'SPEC', {**review.SPEC, 'entries': [missing]})
    assert review.parse_observations(html)['source_dispositions'] == [dict(code='MAE 124', status='no_current_heading')]
    with pytest.raises(ValueError, match='identifier appeared'):
        review.parse_observations(html + '<p class="course-name">MAE 124. New course (4)</p>')


def test_combined_chapter_routes_ceng_and_nano(monkeypatch):
    out = review.parse_observations(fixture(monkeypatch, 'CENG 124A'))
    assert out['courses'][0]['code'] == 'CENG 124A'
    assert out['courses'][0]['source_id'].endswith('-nano-courses')
    with pytest.raises(ValueError, match='Unreviewed'):
        review.parse_observations('', subject='CENG')


def test_range_credits_omission_and_spaced_prerequisite_label(monkeypatch):
    original = review.SPEC
    out = review.parse_observations(fixture(monkeypatch, 'BENG 196', 'Industrial practice. Prerequisites : approval.'))
    assert out['courses'][0]['credits'] is None and out['courses'][0]['prerequisites'] == 'approval.'
    monkeypatch.setattr(review, 'SPEC', original)
    c = review.parse_observations(fixture(monkeypatch, 'ECE 5', 'Circuits and programming.'))['courses'][0]
    assert c['prerequisites'] is None


def test_manual_content_and_policy_scope():
    by = {e['code']: e for e in review.SPEC['entries']}
    assert len(by) == 29 and sum(e['approved_for_integration'] for e in by.values()) == 25
    assert by['ECE 25']['category'] == 'systems'
    for code in ['ECE 148', 'MAE 148']:
        assert set(by[code]['category_review']['candidate_categories']) == {'applications', 'ai_ml'}
    for code in ['ECE 190', 'ECE 191', 'ECE 193H', 'ECE 196']:
        assert by[code]['category_review']['status'] == 'unclassified'
    assert by['SE 165']['category'] == 'applications'
    assert by['ECE 115']['category'] == 'applications'
    assert by['BENG 196']['credits'] is None and by['ECE 193H']['credits'] is None
    assert any('immediately preceding quarter' in n for n in by['MAE 156B']['notes'])
    assert any('MC 27 and MC 30–34' in n for n in by['MAE 156A']['notes'])
    assert any('requested as a requirement' in n for n in by['BENG 193']['notes'])
    assert any('not an automatic AI-degree' in n for n in by['BENG 196']['notes'])
    assert any('C– or better' in n and 'not transferred to NANO' in n for n in by['CENG 124A']['notes'])
    assert any('not assigned here' in n for n in by['NANO 120A']['notes'])
    assert any('not imposed as AI-degree' in n for n in by['MAE 154']['notes'])


@pytest.mark.parametrize('subject,expected,dispositions', [('ECE',9,0),('MAE',6,3),('SE',5,0),('BENG',2,1),('NANO',3,0)])
def test_exact_cached_chapter_replay(subject, expected, dispositions):
    source = review.SPEC['sources'][subject]; path = Path(source['cache_path'])
    if not path.exists():
        pytest.skip('Optional ignored current chapter absent')
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source['source_hash']
    out = review.SOURCE_PARSERS[source['url']](raw.decode())
    assert len(out['courses']) == expected and len(out['source_dispositions']) == dispositions
    assert all(c['code'].split()[0] in source['subjects'] for c in out['courses'])
