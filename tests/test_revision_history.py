"""The history migration must preserve exact payloads and roll back corruption."""
from pathlib import Path
import sqlite3
import zlib

import pytest
from atlas import db

ROOT = Path(__file__).resolve().parents[1]


def legacy_database(path, corrupt=False):
    conn = db.connect(path)
    # Reproduce the schema immediately before the storage migration.
    for file in sorted((ROOT / 'atlas/migrations').glob('*.sql')):
        version = int(file.name.split('_')[0])
        if version >= 7:
            break
        conn.executescript(file.read_text())
        conn.execute('INSERT INTO schema_migrations VALUES (?,?)', (version, '2026-10-10'))
    conn.execute("INSERT INTO institutions(id,name) VALUES ('test','Test')")
    record = {'id':'test-ai', 'title':'AI — résumé', 'nested':{'choices':[1,2]}, 'notes':['x' * 1000]}
    payload = db.canonical(record)
    digest = db.digest(record)
    conn.execute("""INSERT INTO programs(id,institution_id,title,award_level,program_kind,status,verification_status,
        curriculum_status,last_verified,content_hash,record_json) VALUES
        ('test-ai','test','AI','minor','minor','active','confirmed','partial','2026-10-10',?,?)""", (digest,payload))
    conn.execute("INSERT INTO scrape_runs(id,adapter,started_at,status) VALUES (7,'test','2026-10-10','success')")
    conn.execute("INSERT INTO program_revisions VALUES (42,'test-ai',?,?,'2026-10-10',7)",
                 ('wrong' if corrupt else digest,payload))
    conn.commit()
    return conn, record, payload


def test_migration_preserves_payload_metadata_and_is_repeatable(tmp_path):
    conn, record, payload = legacy_database(tmp_path / 'history.sqlite')
    before = conn.execute('SELECT record_json FROM programs').fetchone()[0]
    db.migrate(conn)
    row = conn.execute('SELECT * FROM program_revisions').fetchone()
    assert (row['id'],row['program_id'],row['changed_at'],row['scrape_run_id']) == (42,'test-ai','2026-10-10',7)
    assert zlib.decompress(row['record_zlib']).decode() == payload
    assert len(row['record_zlib']) < len(payload.encode())
    assert db.revision_record(row) == record
    assert db.canonical(db.program_record(conn.execute('SELECT record_zlib,content_hash FROM programs').fetchone())) == before
    db.migrate(conn)
    assert conn.execute('SELECT count(*) FROM program_revisions').fetchone()[0] == 1
    assert conn.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    assert not conn.execute('PRAGMA foreign_key_check').fetchall()


def test_migration_rolls_back_if_historical_hash_is_corrupt(tmp_path):
    conn, record, payload = legacy_database(tmp_path / 'corrupt.sqlite', corrupt=True)
    with pytest.raises(sqlite3.OperationalError):
        db.migrate(conn)
    assert conn.execute('SELECT record_json FROM program_revisions').fetchone()[0] == payload
    assert conn.execute('SELECT count(*) FROM schema_migrations WHERE version=7').fetchone()[0] == 0
    assert conn.execute("SELECT count(*) FROM sqlite_master WHERE name='program_revisions_uncompressed'").fetchone()[0] == 0


def test_revision_decode_rejects_payload_with_wrong_hash():
    with pytest.raises(ValueError, match='hash mismatch'):
        db.revision_record({'record_zlib':zlib.compress(b'{"id":"changed"}'),'content_hash':'wrong'})
