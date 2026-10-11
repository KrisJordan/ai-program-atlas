from copy import deepcopy
import sqlite3

import pytest

from atlas import db
from atlas.awards import major_award_buckets
from tests.test_core_review import conn, program  # noqa: F401


def option(label, normalized):
    return dict(label=label, normalized=normalized, source_id='catalog',
                locator='Official degree award heading')


@pytest.mark.parametrize('award,expected', [('BS','BS'), ('BSE','BSE'), ('BA','BA'),
    ('BSAI','other'), ('BSChE','other'), ('BSBA','other'), ('BSEnvE','other'),
    ('BS/BA','other'), ('other','other')])
def test_exact_labels_only_never_infer_from_host_or_prefix(award, expected):
    p = program()
    p.update(award_level=award, hosting_unit='School of Engineering')
    assert major_award_buckets(p) == [expected]
    p['program_kind'] = 'additional_major'
    assert major_award_buckets(p) == ['other']


def test_multiple_verified_awards_preserve_labels_provenance_history_and_reruns(conn):
    p = program()
    p['award_options'] = [option('Bachelor of Arts', 'BA'),
                          option('Bachelor of Science', 'BS')]
    before = deepcopy(p)
    assert major_award_buckets(p) == ['BS','BA']
    assert p == before
    assert db.ingest_program(conn,p)
    assert not db.ingest_program(conn,p)
    assert [tuple(row) for row in conn.execute(
        'SELECT label,normalized,source_id,locator FROM program_awards ORDER BY ordinal')]
    assert db.export_data(conn)['programs'][0]['award_options'] == p['award_options']
    revision = conn.execute('SELECT * FROM program_revisions').fetchone()
    assert db.revision_record(revision)['award_options'] == p['award_options']
    db.migrate(conn)
    assert not db.ingest_program(conn,p)
    p.pop('award_options')
    assert db.ingest_program(conn,p)
    assert conn.execute('SELECT COUNT(*) FROM program_awards').fetchone()[0] == 0
    assert 'award_options' not in db.export_data(conn)['programs'][0]
    assert conn.execute('PRAGMA foreign_key_check').fetchall() == []


@pytest.mark.parametrize('bad', [
    [option('Bachelor of Science','engineering')],
    [{**option('Bachelor of Science','BS'), 'source_id':'unregistered'}],
    [{**option('Bachelor of Science','BS'), 'locator':''}],
    [{**option('Bachelor of Science','BS'), 'label':''}],
    [option('Bachelor of Science','BS'),option('Bachelor of Science','BS')],
])
def test_unverified_or_duplicate_mapping_is_rejected_without_replacing_record(conn,bad):
    p = program()
    db.ingest_program(conn,p)
    p['award_options'] = bad
    with pytest.raises(ValueError):
        db.ingest_program(conn,p)
    assert 'award_options' not in db.export_data(conn)['programs'][0]


def test_additional_major_cannot_claim_independent_degree_mapping(conn):
    p = program()
    p.update(program_kind='additional_major',award_options=[option('Bachelor of Science','BS')])
    with pytest.raises(ValueError,match='standalone'):
        db.ingest_program(conn,p)


@pytest.mark.parametrize('normalized,source,label', [
    ('BSAI','catalog','BSAI'), ('BS','missing','Bachelor of Science'),
    ('BS','catalog','')])
def test_relational_award_constraints(conn,normalized,source,label):
    p = program()
    db.ingest_program(conn,p)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute('INSERT INTO program_awards VALUES (?,?,?,?,?,?)',
                     (p['id'],0,label,normalized,source,'Degree heading'))
    conn.rollback()
