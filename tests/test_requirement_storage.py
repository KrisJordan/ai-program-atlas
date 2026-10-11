"""Storage changes preserve reviewed graphs, history, constraints and rollback."""
from pathlib import Path
import sqlite3

import pytest
from atlas import db

MIGRATIONS = Path(db.__file__).parent / "migrations"


def populated_v7(path):
    conn = db.connect(path)
    conn.create_function("atlas_compress_revision", 2, db._compress_revision)
    for file in sorted(MIGRATIONS.glob("*.sql")):
        version = int(file.name.split("_")[0])
        if version >= 8:
            break
        conn.executescript(file.read_text())
        conn.execute("INSERT INTO schema_migrations VALUES (?,?)", (version, "2026-10-10"))
    record = {
        "id": "storage-ai", "institution": {"id": "storage-u", "name": "Test University"},
        "title": "Artificial Intelligence", "award_level": "minor", "program_kind": "minor",
        "status": "active", "verification_status": "confirmed", "curriculum_status": "partial",
        "last_verified": "2026-10-10", "sources": [
            {"id": "catalog", "url": "https://example.edu/ai", "title": "Synthetic evidence"}],
        "courses": [{"id": "ai1", "code": "AI 1", "name": "AI — résumé", "credits": None,
                     "credit_unit": "unknown", "source_id": "catalog"}],
        "requirements": [
            {"id": "parent", "parent_id": None, "title": "Requirements", "kind": "all",
             "credit_unit": "unknown", "source_id": "catalog", "course_ids": []},
            {"id": "child", "parent_id": "parent", "title": "Choice", "kind": "choose_courses",
             "count": 1, "credit_unit": "unknown", "source_id": "catalog",
             "source_text": None, "summary": "Unicode — alternative", "course_ids": ["ai1"]}],
        "outcomes": [],
    }
    db.ingest_program(conn, record)
    db.set_override(conn, "storage-ai", "overview", "Reviewed correction", "Synthetic reason",
                    "https://example.edu/correction")
    conn.commit()
    return conn, record


def rows(conn, table):
    return [tuple(row) for row in conn.execute(f"SELECT * FROM {table} ORDER BY 1,2")]


def test_storage_migration_preserves_export_graph_history_and_repeat(tmp_path):
    conn, record = populated_v7(tmp_path / "storage.sqlite")
    tables = ["requirement_groups", "requirement_courses", "program_revisions", "manual_overrides"]
    before_rows = {t: rows(conn, t) for t in tables}
    before_export = db.export_data(conn)
    db.migrate(conn)
    assert {t: rows(conn, t) for t in tables} == before_rows
    assert db.export_data(conn) == before_export
    assert not db.ingest_program(conn, record)
    db.migrate(conn)
    assert {t: rows(conn, t) for t in tables} == before_rows
    assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert not conn.execute("PRAGMA foreign_key_check").fetchall()
    for table in tables[:2]:
        sql = conn.execute("SELECT sql FROM sqlite_master WHERE name=?", (table,)).fetchone()[0]
        assert "WITHOUT ROWID" in sql
    assert conn.execute("SELECT 1 FROM sqlite_master WHERE name='groups_parent'").fetchone()


@pytest.mark.parametrize("sql", [
    "INSERT INTO requirement_courses VALUES ('storage-ai','child','ai1')",
    "INSERT INTO requirement_courses VALUES ('storage-ai','child','missing-course')",
    "INSERT INTO requirement_courses VALUES ('storage-ai','missing-group','ai1')",
    "UPDATE requirement_groups SET source_id='missing-source' WHERE id='child'",
    "UPDATE requirement_groups SET choose_count=0 WHERE id='child'",
    "UPDATE requirement_groups SET parent_id=id WHERE id='child'",
])
def test_migrated_storage_retains_constraints(tmp_path, sql):
    conn, _ = populated_v7(tmp_path / "constraints.sqlite")
    db.migrate(conn)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(sql)
    conn.rollback()
    assert conn.execute("SELECT count(*) FROM requirement_courses").fetchone()[0] == 1


def test_migrated_group_delete_cascades_links_only(tmp_path):
    conn, _ = populated_v7(tmp_path / "cascade.sqlite")
    db.migrate(conn)
    conn.execute("DELETE FROM requirement_groups WHERE id='child'")
    assert conn.execute("SELECT count(*) FROM requirement_courses").fetchone()[0] == 0
    assert conn.execute("SELECT count(*) FROM courses").fetchone()[0] == 1
    assert conn.execute("SELECT count(*) FROM requirement_groups").fetchone()[0] == 1


def test_failed_storage_migration_restores_original_tables(tmp_path, monkeypatch):
    conn, _ = populated_v7(tmp_path / "rollback.sqlite")
    before = {t: rows(conn, t) for t in ["requirement_groups", "requirement_courses"]}
    directory = tmp_path / "migrations"
    directory.mkdir()
    sql = (MIGRATIONS / "008_compact_requirement_keys.sql").read_text()
    (directory / "008_failure.sql").write_text(sql + "\nSELECT * FROM deliberate_missing_table;")
    monkeypatch.setattr(db, "__file__", str(tmp_path / "db.py"))
    with pytest.raises(sqlite3.OperationalError):
        db.migrate(conn)
    assert {t: rows(conn, t) for t in before} == before
    assert not conn.execute("SELECT 1 FROM schema_migrations WHERE version=8").fetchone()
    assert not conn.execute("SELECT 1 FROM sqlite_master WHERE name LIKE 'saved_requirement_%'").fetchone()
    assert "WITHOUT ROWID" not in conn.execute(
        "SELECT sql FROM sqlite_master WHERE name='requirement_groups'").fetchone()[0]


def test_compact_command_preserves_current_facts_history_and_overrides(tmp_path, capsys):
    from atlas.cli import main
    path = tmp_path / "compact.sqlite"
    conn, _ = populated_v7(path)
    db.migrate(conn)
    before = db.export_data(conn)
    history = rows(conn, "program_revisions")
    conn.execute("CREATE TABLE disposable_space(payload BLOB)")
    conn.execute("INSERT INTO disposable_space VALUES (zeroblob(1000000))")
    conn.execute("DROP TABLE disposable_space")
    conn.commit()
    conn.close()
    before_size = path.stat().st_size
    main(["--db", str(path), "compact"])
    assert "facts and history retained" in capsys.readouterr().out
    assert path.stat().st_size < before_size
    conn = db.connect(path)
    assert db.export_data(conn) == before
    assert rows(conn, "program_revisions") == history
    assert not conn.execute("PRAGMA foreign_key_check").fetchall()
