"""The directory is a compact view; complete evidence remains in static exports."""
from copy import deepcopy
import json
from pathlib import Path

from atlas.site import CATEGORIES, build, directory_payload
from tests.test_site import site_data  # noqa: F401


def test_projection_preserves_search_counts_evidence_and_root_choices(site_data, tmp_path):
    p = site_data['programs'][0]
    p['institution']['aliases'] = ['Example alias']
    p['hosting_unit'] = 'School of synthetic computing'
    p['courses'][0].update(description='A sourced description.', prerequisites='AI 001', credits=0)
    p['courses'][1] = deepcopy(p['courses'][0])
    p['courses'].append(dict(p['courses'][0], id='unsourced', code='AI 999', name=None,
                             category='not-classified', credits=None, credit_unit='unknown',
                             url='javascript:unsafe', source_id=None))
    p['requirements'] = [
        dict(id='root', parent_id=None, title='Choose a pathway', kind='choose_courses', count=1,
             source_id='outcome-source', summary='Two possible nested choices.', course_ids=[]),
        dict(id='nested', parent_id='root', title='Nested evidence only on detail page', kind='note',
             source_id='outcome-source', source_text='An important nested rule.', course_ids=[]),
    ]
    p['sources'][0]['locator'] = 'Detailed source locator'
    original = deepcopy(site_data)
    view = directory_payload(site_data, '/nested/atlas/')
    projected = view['programs'][0]
    assert site_data == original
    assert 'courses' not in projected and 'notes' not in projected
    for text in ['Machine Learning', 'AI 001', 'AI 999', 'Example alias', 'School of synthetic computing']:
        assert text in projected['search_text']
    assert 'None' not in projected['search_text']
    profile = projected['course_profile']
    assert profile['count'] == 2 and profile['unknown_credits'] == 1
    assert profile['metadata'] == dict(description=1, prerequisites=1, credits=1, credit_unit=1)
    assert profile['categories']['ai_ml'] == 1 and profile['categories']['other'] == 1
    assert sum(profile['categories'].values()) == 2
    assert profile['credit_units'] == ['semester_hours', 'unknown']
    assert len(projected['requirements']) == 1
    assert projected['requirements'][0]['has_children'] is True
    assert projected['outcomes'][0]['source_id'] == 'outcome-source'
    assert projected['sources'] == [{'id': 'outcome-source', 'url': 'https://example.edu/outcome'}]
    assert view['institutions'][0]['rankings'][0]['source_url'] == 'https://example.edu/ranking'
    build(site_data, tmp_path, '/nested/atlas/')
    assert json.loads((tmp_path / 'data.json').read_text()) == site_data
    detail = (tmp_path / 'programs/test-ai-0/index.html').read_text()
    for text in ['A sourced description.', 'An important nested rule.', 'Detailed source locator']:
        assert text in detail
    index = (tmp_path / 'index.html').read_text()
    assert 'A sourced description.' not in index
    assert 'href="/nested/atlas/programs/test-ai-0/"' in index


def test_family_projection_keeps_nested_local_changes_and_source_precedence(site_data):
    from tests.e2e.test_atlas import family_fixture
    family_fixture(site_data)
    p = site_data['programs'][0]
    p['family']['requirement_overrides'] = [dict(shared_id='shared-core', operation='exclude',
                                                reason='Explicit test exception', source_id='override')]
    p['sources'].append(dict(id='override', url='https://example.edu/exception'))
    p['requirements'].append(dict(id='local-child', parent_id='variant-0', title='Nested local rule',
                                  kind='note', origin='replacement', component='domain',
                                  summary='Source-backed replacement', source_id='override'))
    view = directory_payload(site_data, '/')
    projected = view['programs'][0]
    assert projected['family']['requirement_overrides'][0]['reason'] == 'Explicit test exception'
    assert any(r['id'] == 'local-child' for r in projected['requirements'])
    assert {'id': 'override', 'url': 'https://example.edu/exception'} in projected['sources']
    assert view['families'][0]['shared_requirements'][0]['id'] == 'shared-core'
    assert view['families'][0]['sources'] == [{'id': 'family-source', 'url': 'https://example.edu/family'}]


def test_current_inventory_projection_is_materially_smaller_and_lossless_for_counts(tmp_path):
    from atlas import db
    from atlas.cli import ingest_all
    conn = db.connect(tmp_path / 'check.sqlite')
    db.migrate(conn)
    ingest_all(conn, Path(__file__).resolve().parents[1] / 'data')
    data = db.export_data(conn)
    conn.close()
    view = directory_payload(data, '/ai-program-atlas/')
    full = {'programs': data['programs'], 'institutions': data['institutions'],
            'families': data.get('families', []), 'categories': CATEGORIES, 'base_path': '/ai-program-atlas/'}
    # Ratio leaves room for new research while catching accidental full-payload embedding.
    assert len(json.dumps(view)) < len(json.dumps(full)) * .4
    for original, projected in zip(data['programs'], view['programs']):
        courses = {c['id']: c for c in original['courses']}.values()
        assert projected['course_profile']['count'] == len(courses)
        for c in courses:
            for value in (c.get('code'), c.get('name')):
                if value:
                    assert value in projected['search_text']
        for field in ('description', 'prerequisites', 'credits', 'credit_unit'):
            sources = {s['id']: s for s in original['sources']}
            sourced = lambda c: any(str(url or '').startswith(('http://', 'https://')) for url in [c.get('url'), sources.get(c.get('source_id'), {}).get('url')])
            expected = sum(sourced(c) and c.get(field) is not None and c.get(field) != '' and (field != 'credit_unit' or c.get(field) != 'unknown') for c in courses)
            assert projected['course_profile']['metadata'][field] == expected
