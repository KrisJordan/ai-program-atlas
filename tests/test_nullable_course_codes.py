"""Title-only source facts and lossless upgrade of the referenced course table."""
from copy import deepcopy
from pathlib import Path
import sqlite3

import pytest

from atlas import db
from atlas.curriculum_profile import requirement_profile
from atlas.families import resolve_program
from atlas.site import build
from tests.test_course_identity import record
from tests.test_families import synthetic_family, synthetic_variant


def legacy_connection(path):
    c = db.connect(path)
    c.create_function('atlas_compress_revision', 2, db._compress_revision)
    c.create_function('atlas_verified_program_json', 2, lambda payload, fingerprint:
        db.canonical(db._decode_record({'record_zlib': payload, 'content_hash': fingerprint}, 'Program')))
    for file in sorted((Path(db.__file__).parent / 'migrations').glob('*.sql')):
        version = int(file.name.split('_')[0])
        if version > 15:
            break
        c.executescript(file.read_text())
        c.execute('INSERT INTO schema_migrations VALUES (?,?)', (version, '2026-10-11'))
        c.commit()
    return c


def rich_record():
    p = record()
    p['courses'][0]['notes'] = ['Official version qualification.', 'Permission remains conditional.']
    p['courses'][0]['category_review'] = dict(status='reviewed', taxonomy_version='1',
        reviewed_at='2026-10-11', source_ids=['catalog'], locator='Official course body',
        rationale='The source explicitly describes machine learning.')
    return p


def snapshot(c):
    tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name!='schema_migrations'")]
    return {table: [tuple(r) for r in c.execute(f'SELECT * FROM "{table}"')] for table in tables}


def test_upgrade_preserves_all_tables_history_overrides_and_foreign_keys(tmp_path):
    c = legacy_connection(tmp_path / 'legacy.sqlite')
    p = rich_record()
    db.ingest_program(c, p)
    c.execute('INSERT INTO manual_overrides VALUES (?,?,?,?,?,?)',
        (p['id'], 'overview', '"Manual review survives"', 'Reviewed', 'https://example.edu', '2026-10-11'))
    c.commit()
    before = snapshot(c)
    db.migrate(c)
    assert snapshot(c) == before
    assert c.execute('PRAGMA foreign_keys').fetchone()[0] == 1
    assert not c.execute('PRAGMA foreign_key_check').fetchall()
    assert not next(r for r in c.execute('PRAGMA table_info(courses)') if r['name'] == 'code')['notnull']
    # Every former child FK still points at courses, with its existing actions.
    for table in ('requirement_courses', 'course_notes', 'course_category_reviews',
                  'course_identity_groups', 'course_identity_members'):
        assert any(r['table'] == 'courses' for r in c.execute(f'PRAGMA foreign_key_list({table})'))
    with pytest.raises(sqlite3.IntegrityError):
        c.execute('INSERT INTO course_notes VALUES (?,?,?,?)', (p['id'], 'missing', 0, 'Orphan'))
    db.migrate(c)
    assert not db.ingest_program(c, p)
    assert snapshot(c) == before
    c.close()


def test_failed_fk_verification_rolls_back_rebuild_and_restores_enforcement(tmp_path):
    c = legacy_connection(tmp_path / 'broken.sqlite')
    db.ingest_program(c, rich_record())
    c.commit()
    c.execute('PRAGMA foreign_keys=OFF')
    c.execute('INSERT INTO course_notes VALUES (?,?,?,?)', ('missing-program', 'missing', 0, 'Orphan'))
    c.commit()
    before = snapshot(c)
    with pytest.raises(sqlite3.IntegrityError, match='foreign key verification'):
        db.migrate(c)
    assert snapshot(c) == before
    assert c.execute('PRAGMA foreign_keys').fetchone()[0] == 1
    assert next(r for r in c.execute('PRAGMA table_info(courses)') if r['name'] == 'code')['notnull']
    assert not c.execute('SELECT 1 FROM schema_migrations WHERE version=16').fetchone()
    assert not c.execute("SELECT 1 FROM sqlite_master WHERE name='courses_new'").fetchone()
    c.close()


def title_record():
    p = record()
    p.pop('course_identity_groups')
    for i, course in enumerate(p['courses']):
        course.update(code=None, name=f'Official Named Course {i + 1}')
    return p


def test_title_only_ingest_export_history_profile_and_static_display(tmp_path):
    c = db.connect(tmp_path / 'fresh.sqlite')
    db.migrate(c)
    p = title_record()
    assert db.ingest_program(c, p)
    assert not db.ingest_program(c, p)
    assert all(r[0] is None for r in c.execute('SELECT code FROM courses'))
    exported = db.export_data(c)
    assert exported['programs'][0]['courses'] == p['courses']
    assert db.revision_record(c.execute('SELECT * FROM program_revisions').fetchone()) == p
    assert requirement_profile(exported['programs'][0])['options']['count'] == 3
    out = tmp_path / 'site'
    build(exported, out, base_path='/atlas-test/')
    html = (out / 'programs' / p['id'] / 'index.html').read_text()
    assert 'Code unknown' in html and 'Official Named Course 1' in html
    assert '>Unknown<span>' in html
    assert not c.execute('PRAGMA foreign_key_check').fetchall()
    c.close()


@pytest.mark.parametrize('change', [dict(name=None), dict(name=' '), dict(code=''),
    dict(code=123), dict(id='unsafe/id'), dict(source_id=None), dict(source_id='missing')])
def test_title_records_keep_name_id_code_and_source_validation(change):
    p = title_record()
    p['courses'][0].update(change)
    with pytest.raises(ValueError):
        db.validate_program(p)


def test_missing_code_is_not_silently_converted_to_null():
    p = title_record()
    p['courses'][0].pop('code')
    with pytest.raises(ValueError, match='explicit null'):
        db.validate_program(p)


def test_unknown_code_does_not_bind_reviewed_shared_codes():
    p = synthetic_variant()
    p['courses'][0]['code'] = None
    with pytest.raises(ValueError, match='known course codes'):
        resolve_program(p, synthetic_family())
    # A local named course outside the shared binding remains valid.
    p = synthetic_variant()
    p['courses'][2]['code'] = None
    assert resolve_program(p, synthetic_family())['courses'][2]['code'] is None
