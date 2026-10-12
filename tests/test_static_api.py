"""Verify static responses against the public contract and SQLite, not hand-built totals."""
import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

from atlas import db
from atlas.curriculum_profile import requirement_profile
from atlas.static_api import build_api, encode, openapi, responses


@pytest.fixture(scope='module')
def public_data():
    conn = db.connect(Path('data/atlas.sqlite'))
    try:
        yield db.export_data(conn)
    finally:
        conn.close()


def validator(contract, shape):
    return Draft202012Validator({'components': contract['components'], **shape})


def test_every_response_validates_and_examples_exist(public_data):
    contract = openapi(public_data, '/nested/atlas/')
    assert contract['openapi'] == '3.1.0'
    assert contract['servers'] == [{'url': '/nested/atlas/api/v1'}]
    bodies = responses(public_data, '/nested/atlas/')
    for schema in contract['components']['schemas'].values():
        Draft202012Validator.check_schema(schema)
    for path, entry in contract['paths'].items():
        if path == '/index.json':
            continue
        operation = entry['get']
        content = operation['responses']['200']['content']['application/json']
        example = content.get('examples', {}).get('current', {}).get('externalValue')
        if example:
            assert example.removeprefix('/nested/atlas/api/v1/') in bodies
        assert 'text/html' in operation['responses']['404']['content']
        shape = content['schema']
        v = validator(contract, shape)
        matches = [body for filename, body in bodies.items() if
                   ('{' not in path and filename == path[1:]) or
                   ('{' in path and filename.startswith(path.split('/{')[0][1:] + '/'))]
        assert matches, path
        for body in matches:
            v.validate(body)


def test_lossless_completeness_and_references(public_data):
    bodies = responses(public_data, '/')
    assert bodies['dataset.json'] is public_data
    conn = db.connect(Path('data/atlas.sqlite'))
    try:
        for collection in ('programs', 'institutions'):
            assert len(public_data[collection]) == conn.execute(
                f'SELECT count(*) FROM {collection}').fetchone()[0]
        assert sum(len(p['courses']) for p in public_data['programs']) == conn.execute(
            'SELECT count(*) FROM courses').fetchone()[0]
    finally:
        conn.close()
    institutions = {i['id']: i for i in public_data['institutions']}
    programs = {p['id']: p for p in public_data['programs']}
    families = {f['id']: f for f in public_data['families']}
    for inst in institutions.values():
        assert set(inst['program_ids']) == {p['id'] for p in programs.values()
                                           if p['institution']['id'] == inst['id']}
    for family in families.values():
        assert family['institution_id'] in institutions
        assert set(family['variant_ids']) <= programs.keys()
    for p in programs.values():
        pid = p['id']
        assert p['institution']['id'] in institutions
        assert bodies[f'programs/{pid}.json'] == p
        assert bodies[f'courses/{pid}.json'] == p['courses']
        assert bodies[f'requirements/{pid}.json'] == p['requirements']
        assert bodies[f'profiles/{pid}.json'] == requirement_profile(p, include_course_ids=True)
        if p.get('family'):
            assert p['family']['id'] in families
        course_ids = {c['id'] for c in p['courses']}
        requirement_ids = {r['id'] for r in p['requirements']}
        source_ids = {s['id'] for s in p['sources']}
        assert len(course_ids) == len(p['courses'])
        assert len(requirement_ids) == len(p['requirements'])
        for course in p['courses']:
            assert course['source_id'] in source_ids
        for requirement in p['requirements']:
            assert set(requirement['course_ids']) <= course_ids
            assert requirement['parent_id'] is None or requirement['parent_id'] in requirement_ids
            assert requirement['source_id'] in source_ids
        for outcome in p['outcomes']:
            assert outcome['source_id'] in source_ids
    # Only public export fields: no database revisions, source captures or run logs.
    assert set(public_data) == {'meta', 'programs', 'institutions', 'families', 'rankings', 'csrankings'}


def test_deterministic_files_manifest_and_stale_cleanup(tmp_path, public_data):
    build_api(public_data, tmp_path, '/ai-program-atlas/')
    root = tmp_path / 'api/v1'
    files = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in root.rglob('*.json')}
    assert (root / 'dataset.json').read_text() == encode(public_data)
    manifest = json.loads((root / 'index.json').read_text())
    assert manifest['dataset_sha256'] == files['dataset.json']
    contract = json.loads((root / 'openapi.json').read_text())
    validator(contract, {'$ref': '#/components/schemas/Manifest'}).validate(manifest)
    (root / 'programs/obsolete.json').write_text('{}')
    build_api(public_data, tmp_path, '/ai-program-atlas/')
    assert files == {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in root.rglob('*.json')}


def test_contract_rejects_wrong_types_and_keeps_nulls(public_data):
    contract = openapi(public_data, '/')
    v = validator(contract, {'$ref': '#/components/schemas/Course'})
    course = deepcopy(public_data['programs'][0]['courses'][0])
    course['credits'] = None
    course['code'] = None
    v.validate(course)
    for invalid in ['unknown', True, -1]:
        course['credits'] = invalid
        with pytest.raises(ValidationError):
            v.validate(course)
    v = validator(contract, {'$ref': '#/components/schemas/Requirement'})
    requirement = deepcopy(public_data['programs'][0]['requirements'][0])
    requirement['course_ids'] = 'not-an-array'
    with pytest.raises(ValidationError):
        v.validate(requirement)


@pytest.mark.parametrize('collection', ['programs', 'institutions', 'families'])
def test_all_path_ids_are_safe_and_unique(public_data, collection):
    data = deepcopy(public_data)
    data[collection][0]['id'] = '../escape'
    with pytest.raises(ValueError):
        responses(data, '/')
    data = deepcopy(public_data)
    data[collection].append(data[collection][0])
    with pytest.raises(ValueError):
        responses(data, '/')


def test_unchecked_audit_categories_remain_null(public_data):
    contract = openapi(public_data, '/')
    data = deepcopy(public_data)
    audit = data['meta']['degree_audit']['programs'][0]
    for role in ('required', 'options', 'unresolved'):
        audit['expected_profile'][role]['categories'] = None
    validator(contract, {'$ref': '#/components/schemas/Dataset'}).validate(data)
    # Audit expectations and always-derived profile counts have different contracts.
    profile = requirement_profile(public_data['programs'][0], include_course_ids=True)
    profile['options']['categories'] = None
    with pytest.raises(ValidationError):
        validator(contract, {'$ref': '#/components/schemas/Profile'}).validate(profile)
