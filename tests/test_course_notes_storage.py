"""Lossless ordered note queries, upgrade backfill and atomic replacement."""
from copy import deepcopy
from pathlib import Path
import sqlite3
import pytest
from atlas import db
from tests.test_core_review import program

def record():
    p=program();p['courses']=[dict(id='cs1',code='CS 1',name='Example',source_id='catalog',notes=['Permission is required, not granted.','Dated version — current eligibility unknown.'])];return p

def rows(c):
    return [tuple(r) for r in c.execute('SELECT course_id,position,note FROM course_notes ORDER BY course_id,position')]

def test_upgrade_backfills_without_changing_canonical_or_history(tmp_path):
    c=db.connect(tmp_path/'legacy.sqlite')
    c.create_function('atlas_compress_revision',2,db._compress_revision)
    for file in sorted((Path(db.__file__).parent/'migrations').glob('*.sql')):
        version=int(file.name.split('_')[0])
        if version>=15:break
        c.executescript(file.read_text());c.execute('INSERT INTO schema_migrations VALUES (?,?)',(version,'2026-10-11'));c.commit()
    p=record();db.ingest_program(c,p);before=[tuple(r) for r in c.execute('SELECT * FROM program_revisions')];hash_before=c.execute('SELECT content_hash FROM programs').fetchone()[0]
    db.migrate(c);assert rows(c)==[('cs1',i,n) for i,n in enumerate(p['courses'][0]['notes'])]
    assert db.export_data(c)['programs'][0]['courses'][0]['notes']==p['courses'][0]['notes']
    assert [tuple(r) for r in c.execute('SELECT * FROM program_revisions')]==before
    assert c.execute('SELECT content_hash FROM programs').fetchone()[0]==hash_before
    db.migrate(c);assert not db.ingest_program(c,p);assert len(rows(c))==2
    assert not c.execute('PRAGMA foreign_key_check').fetchall();c.close()

def test_replacement_removes_old_notes_and_rejects_bad_update_atomically(tmp_path):
    c=db.connect(tmp_path/'new.sqlite');db.migrate(c);p=record();db.ingest_program(c,p)
    changed=deepcopy(p);changed['courses'][0]['notes']=['Revised conditional rule.'];db.ingest_program(c,changed)
    assert rows(c)==[('cs1',0,'Revised conditional rule.')]
    for invalid in ['not a list',[None],[' '],{'one':'note'}]:
        bad=deepcopy(changed);bad['courses'][0]['notes']=invalid
        with pytest.raises(ValueError,match='Course notes'):db.ingest_program(c,bad)
        assert rows(c)==[('cs1',0,'Revised conditional rule.')]
    with pytest.raises(sqlite3.IntegrityError):c.execute('INSERT INTO course_notes VALUES (?,?,?,?)',(p['id'],'missing',0,'Orphan'))
    changed['courses'][0].pop('notes');db.ingest_program(c,changed);assert rows(c)==[]
    assert not c.execute('PRAGMA foreign_key_check').fetchall();c.close()
