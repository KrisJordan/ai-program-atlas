"""Conditional source sections, changed rules and non-exhaustive suggestions."""
from importlib import import_module
import json
from pathlib import Path

import pytest

m = import_module('atlas.adapters.mit-ai-decision-making-bs.hass_music_theater')
ROOT = Path(__file__).resolve().parents[1]


def tab(label, body):
    return '<div class="b-tabs__entry-content"><p><strong>' + label + '</strong></p>' + body + '</div>'


def music():
    body = '''<p>A Humanities concentration in music requires four subjects;
    may start with one or more of our introductory subjects</p>
    <ul><li>21M.998: Synthetic Introduction (CI-H)</li></ul>
    <p>encouraged to begin at whatever level is appropriate to their experience;
    two semesters of two different music ensembles;
    three semesters of performance ensembles (two of one ensemble and one of a different ensemble);
    another half-term or six-unit subject from the curriculum;
    Most 9- or 12-unit Music subjects; Distribution Component;
    Two 6-unit performance subjects can also be combined;
    following classes fulfill the Communication Requirement as CI-H subjects</p>
    <ul><li>21M.998: Synthetic Introduction (HASS Arts) (CI-H)</li></ul>
    <p>The seminar joint listed with Music, 21M.997J, also fulfills both a music concentration and CI-H requirement;
    schedule a meeting before filling out your concentration proposal</p>'''
    return '<main><h1>Degree Requirements</h1>' + tab('Music Minor', '<p>six subjects and 72 units</p><ul><li>21M.999: Minor-only title</li></ul>') + tab('Music Concentration', body) + '</main>'


def theater():
    return '<main><h1>Degree Requirements</h1>' + tab('Theater Major', '<p>thesis and mandatory 21T.999</p>') + tab('The Concentration in Theater Arts', '''<p>three to four 9-to-12-unit courses;
    minimum of 36 credits in the Theater Arts curriculum;
    Up to nine units of theater practicum (acting, directing, or design)
    in Theater Arts productions can be counted toward the concentration;
    current Concentration Advisor</p>''') + '</main>'


def test_music_extracts_changed_rows_not_seed_and_excludes_minor():
    d = m.parse_music(music())
    assert [(c['code'], c['name']) for c in d['courses']] == [('21M.998', 'Synthetic Introduction'), ('21M.997J', None)]
    assert d['requirements'][0]['kind'] == 'note'
    assert d['requirements'][1]['count'] == 4
    assert d['requirements'][1]['course_ids'] == []  # Intro suggestions are not a closed choice pool.
    assert all(r['parent_id'] == 'mit-ai-hass-music' for r in d['requirements'][1:])
    assert all(c['credits'] is None and c['prerequisites'] is None for c in d['courses'])
    assert 'curriculum_audit' not in d and 'last_verified' not in d
    from atlas.curriculum_profile import requirement_profile
    profile = requirement_profile(d)
    assert profile['required']['count'] == profile['options']['count'] == 0
    assert profile['unresolved']['count'] == 2


@pytest.mark.parametrize('old,new', [('requires four subjects','requires five subjects'),
    ('Two 6-unit performance subjects','Three 6-unit performance subjects'),
    ('schedule a meeting before','schedule a meeting after'),
    ('another half-term or six-unit subject','another twelve-unit subject')])
def test_music_changed_material_conditions_require_review(old,new):
    with pytest.raises(ValueError):
        m.parse_music(music().replace(old,new))


def test_theater_keeps_range_unknown_credit_unit_and_practicum_limit():
    d = m.parse_theater(theater())
    assert not d.get('courses')
    selected = d['requirements'][1]
    assert selected['kind'] == 'note' and selected['credits'] == 36
    assert selected['count'] is None and selected['credit_unit'] == 'unknown'
    assert selected['course_ids'] == []
    assert 'not an additional' in d['requirements'][2]['summary']
    assert all(r['parent_id'] == 'mit-ai-hass-theater' for r in d['requirements'][1:])


@pytest.mark.parametrize('old,new', [('three to four','four to five'),('36 credits','48 credits'),('Up to nine units','Up to twelve units')])
def test_theater_changed_selection_policy_rejected(old,new):
    with pytest.raises(ValueError):
        m.parse_theater(theater().replace(old,new))


@pytest.mark.parametrize('fn,html', [(m.parse_music,music),(m.parse_theater,theater)])
def test_wrong_source_tabs_duplicate_tabs_and_access_page_rejected(fn,html):
    source = html()
    with pytest.raises(ValueError):
        fn(source.replace('Concentration','Minor').replace('concentration','minor'))
    with pytest.raises(ValueError):
        fn(source.replace('</main>', source.replace('<main>', '').replace('</main>', '') + '</main>'))
    with pytest.raises(ValueError):
        fn('<title>Access denied</title>' + source)


def test_reviewed_seed_fields_have_scoped_evidence_without_degree_promotion():
    p = json.loads((ROOT/'data/programs/mit-ai-decision-making-bs.json').read_text())
    sources = {s['id']: s for s in p['sources']}
    for key, url in [('music',m.MUSIC),('theater',m.THEATER)]:
        sid = m.PID + '-hass-' + key + '-current'
        assert sources[sid]['url'] == url
        rows = [r for r in p['requirements'] if r['source_id'] == sid]
        assert rows[0]['kind'] == 'note'
        assert all(r['parent_id'] == 'mit-ai-hass-' + key for r in rows[1:])
    assert p['curriculum_status'] == 'partial'
    assert p['curriculum_audit']['unresolved_requirements']


@pytest.mark.parametrize('key,fn', [('music',m.parse_music),('theater',m.parse_theater)])
def test_optional_actual_page_replay_matches_reviewed_source_slice(key,fn):
    cache = Path('/tmp/atlas-mit-hass-' + key + '-degree.html')
    if not cache.exists():
        pytest.skip('Optional normally fetched official HTML')
    d = fn(cache.read_text())
    p = json.loads((ROOT/'data/programs/mit-ai-decision-making-bs.json').read_text())
    sid = m.PID + '-hass-' + key + '-current'
    # These lists observe identity/membership, not the separately reviewed course
    # description or unit evidence that can enrich the curated records later.
    expected={c['id']:c for c in p['courses'] if c['source_id']==sid}
    assert {c['id'] for c in d.get('courses',[])}==set(expected)
    for observed in d.get('courses',[]):
        assert {k:observed[k] for k in ('id','code','name','source_id','url')} == {
            k:expected[observed['id']][k] for k in ('id','code','name','source_id','url')}
        assert observed['description'] is None and observed['credits'] is None
        assert 'category_review' not in observed
    assert d.get('requirements',[]) == [r for r in p['requirements'] if r['source_id']==sid]
