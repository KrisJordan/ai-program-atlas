"""Field-specific choices must remain conditional, source-driven and nonadditive."""
from importlib import import_module
from pathlib import Path
import pytest

m = import_module('atlas.adapters.mit-ai-decision-making-bs.hass_fields')


def fixture(key, course_rows=None):
    spec = m.FIELDS[key]
    rows = ['<main><h1>' + spec['title'] + ' Concentration</h1><section><h2>Subject requirements</h2><div class="body-content">']
    rows.append('<p>Policy markers: ' + '; '.join(spec['markers']) + '</p>')
    rows.append('<p>one subject that also counts toward the HASS Distribution</p>')
    if course_rows is not None:
        rows.append(course_rows)
    elif spec['areas']:
        for i, area in enumerate(spec['areas']):
            rows.append(f'<h3>{area}</h3><p>21H.{100+i} Fictional Area Course {i}, HASS-H</p>')
    else:
        rows.append('<p>21H.199 Fictional Course, HASS-H</p>')
    return ''.join(rows) + '</div></section></main>'


@pytest.mark.parametrize('key', [k for k in m.FIELDS if k != 'archaeology-and-archaeological-science'])
def test_choices_are_conditional_and_courses_observed(key):
    d = m.parse_field(key, fixture(key))
    assert d['requirements'][0]['parent_id'] is None
    assert d['requirements'][0]['kind'] == 'note'
    assert all(r['parent_id'] == d['requirements'][0]['id'] for r in d['requirements'][1:])
    assert d['requirements'][1]['count'] == m.FIELDS[key]['count']
    assert all(c['name'].startswith('Fictional') for c in d['courses'])
    assert 'curriculum_status' not in d and 'curriculum_audit' not in d and 'last_verified' not in d
    for r in d['requirements']:
        if r['title'].endswith('source option group'):
            assert r['kind'] == 'note'


def test_archaeology_breaks_and_required_vs_choice():
    key = 'archaeology-and-archaeological-science'
    d = m.parse_field(key, fixture(key, '<p><a>3.986</a> Fictional Required One, CI-H, HASS-S<br><a>3.985J</a> Fictional Required Two [5.24J], HASS-S</p><p>3.999 Fictional Option, HASS-S<br>3.998 Fictional Other Option, HASS-S</p>'))
    assert len(d['courses']) == 4
    assert d['courses'][1]['code'] == '3.985J [5.24J]'
    assert d['courses'][1]['name'] == 'Fictional Required Two'
    req, pool = d['requirements'][1:3]
    assert req['kind'] == 'all' and len(req['course_ids']) == 2
    assert pool['kind'] == 'choose_courses' and pool['count'] == 2
    assert set(req['course_ids']).isdisjoint(pool['course_ids'])
    changed = m.parse_field(key, fixture(key, '<p>3.986 Fictional Required One, HASS-S<br>3.985J Fictional Required Two, HASS-S<br>3.123 Newly Published Option, HASS-S</p>'))
    assert any(c['code'] == '3.123' for c in changed['courses'])
    assert not any(c['code'] == '3.999' for c in changed['courses'])


def test_crosslisting_does_not_create_two_required_courses_or_invent_units():
    key = 'religious-studies'
    d = m.parse_field(key, fixture(key, '<p>17.565 / 17.567 Fictional Paired Listing, HASS-S</p><p>21L.607 Greek I [6-unit course] **</p>'))
    assert len(d['courses']) == 2
    assert d['courses'][0]['code'] == '17.565/17.567'
    assert d['courses'][0]['credits'] is None
    assert d['courses'][1]['credits'] == 6 and d['courses'][1]['credit_unit'] == 'units'
    assert d['courses'][1]['name'] == 'Greek I'


def test_area_overlays_remain_within_selection_total():
    d = m.parse_field('american-studies', fixture('american-studies'))
    overlays = [r for r in d['requirements'] if '-overlay-' in r['id']]
    assert len(overlays) == 2 and all(r['count'] == 1 for r in overlays)
    assert all(set(r['course_ids']) <= set(d['requirements'][1]['course_ids']) for r in overlays)
    assert all('within' in r['summary'] for r in overlays)
    d = m.parse_field('legal-studies', fixture('legal-studies'))
    assert d['requirements'][-1]['count'] == 2
    assert 'not two additional' in d['requirements'][-1]['summary']


@pytest.mark.parametrize('key', list(m.FIELDS))
def test_changed_material_rule_is_not_fresh_evidence(key):
    html = fixture(key).replace(m.FIELDS[key]['markers'][0], 'Changed academic rule')
    with pytest.raises(ValueError, match='condition changed'):
        m.parse_field(key, html)


def test_missing_section_and_reordered_area_fail():
    with pytest.raises(ValueError, match='section missing'):
        m.parse_field('religious-studies', '<h1>Religious Studies Concentration</h1>')
    html = fixture('legal-studies').replace('<h3>Law and Policy</h3>', '<h3>New area</h3>')
    with pytest.raises(ValueError, match='area structure'):
        m.parse_field('legal-studies', html)


@pytest.mark.parametrize('key', list(m.FIELDS))
def test_optional_reviewed_source_replay(key):
    path = Path('/tmp/atlas-mit-hass-' + key + '.html')
    if not path.exists():
        pytest.skip('Optional local reviewed source cache')
    d = m.parse_field(key, path.read_text())
    assert d['courses'] and d['requirements']
    assert len({c['id'] for c in d['courses']}) == len(d['courses'])
    assert all('HASS-' not in c['name'] for c in d['courses'])
