"""Compression preserves bytes, relationships and failure atomicity."""
import hashlib
import sqlite3
import zlib
from pathlib import Path

import pytest
from atlas import db
from tests.test_core_review import program


def legacy_current(path, corrupt=False):
    conn = db.connect(path)
    conn.create_function('atlas_compress_revision', 2, db._compress_revision)
    for file in sorted((Path(db.__file__).parent / 'migrations').glob('*.sql')):
        version = int(file.name.split('_')[0])
        if version >= 14:
            break
        conn.executescript(file.read_text())
        conn.execute('INSERT INTO schema_migrations VALUES (?,?)', (version, '2026-10-11'))
    record = program()
    record['overview'] = 'Résumé — repeated factual context. ' * 100
    payload = db.canonical(record)
    db.upsert_institution(conn, record['institution'])
    conn.execute('''INSERT INTO programs(id,institution_id,title,award_level,program_kind,status,
        overview,verification_status,curriculum_status,last_verified,content_hash,record_json)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
        (record['id'],record['institution']['id'],record['title'],record['award_level'],
         record['program_kind'],record['status'],record['overview'],record['verification_status'],
         record['curriculum_status'],record['last_verified'],'wrong' if corrupt else db.digest(record),payload))
    conn.execute('INSERT INTO program_links VALUES (?,?,?,?)', (record['id'],'catalog','https://example.edu/catalog','Preserved'))
    conn.execute('INSERT INTO manual_overrides VALUES (?,?,?,?,?,?)',
                 (record['id'],'overview','"Reviewed override"','Evidence correction','https://example.edu/evidence','2026-10-11'))
    conn.execute('INSERT INTO program_revisions(program_id,content_hash,record_zlib,changed_at) VALUES (?,?,?,?)',
                 (record['id'],db.digest(record),zlib.compress(payload.encode()),'2026-10-11'))
    conn.commit()
    return conn, record, payload


def test_current_migration_preserves_canonical_bytes_children_and_overrides(tmp_path):
    conn, record, payload = legacy_current(tmp_path/'current.sqlite')
    before = {table:[tuple(r) for r in conn.execute('SELECT * FROM '+table)]
              for table in ('program_links','manual_overrides','program_revisions')}
    db.migrate(conn)
    row = conn.execute('SELECT * FROM programs').fetchone()
    assert zlib.decompress(row['record_zlib']).decode() == payload
    assert db.program_record(row) == record
    assert len(row['record_zlib']) < len(payload.encode())
    assert row['content_hash'] == hashlib.sha256(payload.encode()).hexdigest()
    assert 'record_json' not in row.keys()
    for table, rows in before.items():
        assert [tuple(r) for r in conn.execute('SELECT * FROM '+table)] == rows
    assert db.export_data(conn)['programs'][0]['overview'] == 'Reviewed override'
    db.migrate(conn)
    assert conn.execute('SELECT count(*) FROM schema_migrations WHERE version=14').fetchone()[0] == 1
    assert conn.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    assert not conn.execute('PRAGMA foreign_key_check').fetchall()


def test_current_migration_rolls_back_corrupt_hash_without_touching_children(tmp_path):
    conn, record, payload = legacy_current(tmp_path/'corrupt.sqlite', corrupt=True)
    with pytest.raises(sqlite3.OperationalError):
        db.migrate(conn)
    row = conn.execute('SELECT * FROM programs').fetchone()
    assert row['record_json'] == payload
    assert 'record_zlib' not in row.keys()
    assert conn.execute('SELECT count(*) FROM schema_migrations WHERE version=14').fetchone()[0] == 0
    assert conn.execute('SELECT count(*) FROM program_links').fetchone()[0] == 1
    assert not conn.execute('PRAGMA foreign_key_check').fetchall()


def test_current_decode_fails_closed_for_changed_or_invalid_payload():
    with pytest.raises(ValueError, match='Program content hash mismatch'):
        db.program_record({'record_zlib':zlib.compress(b'{"id":"changed"}'),'content_hash':'wrong'})
    with pytest.raises(zlib.error):
        db.program_record({'record_zlib':b'\x00','content_hash':'wrong'})
