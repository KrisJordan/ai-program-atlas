from copy import deepcopy
import sqlite3
from types import SimpleNamespace
import pytest
from atlas import db
from atlas.awards import major_award_buckets
from atlas.http import FetchResult
from atlas.scrape import scrape_one
from tests.test_core_review import conn, program  # noqa: F401


def parent_record():
    p=program();p.update(program_kind='concentration',award_level='concentration')
    p['parent_programs']=[dict(id='computer-science-bs',title='Computer Science',award_level='BS',
        award_label='Bachelor of Science',relationship='concentration',parent_program_id=None,
        eligibility=None,source_ids=['catalog'],locator='BS curricular concentrations',reviewed_at='2026-10-11')]
    p['parent_program_review']=dict(status='verified',reviewed_at='2026-10-11',source_ids=['catalog'],notes=[])
    return p


def second_record():
    p=program();p.update(program_kind='additional_major',award_level='other')
    p['major_relationship']=dict(kind='second_major_only',official_term='Co-Major',
        eligibility='Must accompany a primary business major.',source_ids=['catalog'],
        locator='Co-major eligibility',reviewed_at='2026-10-11')
    return p


def test_confirmed_second_major_is_a_relationship_not_award(conn):
    p=second_record();before=deepcopy(p)
    assert major_award_buckets(p)==['second_major']
    assert db.ingest_program(conn,p) and not db.ingest_program(conn,p)
    assert db.export_data(conn)['programs'][0]['award_level']=='other'
    assert tuple(conn.execute('SELECT kind,official_term FROM program_major_relationships').fetchone())==('second_major_only','Co-Major')
    assert p==before
    p.pop('major_relationship');assert db.ingest_program(conn,p)
    assert major_award_buckets(p)==['other']
    assert conn.execute('SELECT count(*) FROM program_major_relationship_sources').fetchone()[0]==0


def test_optional_double_major_and_unknown_awards_do_not_become_second_major(conn):
    p=program();p.update(award_level='other',notes=['Can be combined with an optional second major.'])
    assert major_award_buckets(p)==['other']
    p['major_relationship']=second_record()['major_relationship']
    with pytest.raises(ValueError,match='additional-major'):db.ingest_program(conn,p)


def test_multiple_parent_awards_roundtrip_history_removal_and_idempotence(conn):
    p=parent_record();p['parent_programs'].append({**p['parent_programs'][0],'id':'computer-science-ba','award_level':'BA','award_label':'Bachelor of Arts'})
    assert db.ingest_program(conn,p) and not db.ingest_program(conn,p)
    assert db.export_data(conn)['programs'][0]['parent_programs']==p['parent_programs']
    assert conn.execute('SELECT count(*) FROM program_parents').fetchone()[0]==2
    assert db.revision_record(conn.execute('SELECT * FROM program_revisions').fetchone())['parent_programs']==p['parent_programs']
    p['parent_programs']=[];p['parent_program_review']['status']='unknown'
    assert db.ingest_program(conn,p)
    assert not conn.execute('SELECT * FROM program_parent_sources').fetchall()
    assert not conn.execute('PRAGMA foreign_key_check').fetchall()


def test_parent_name_with_unverified_award_remains_partial(conn):
    p=parent_record();p['parent_programs'][0]['award_level']=None;p['parent_program_review']['status']='partial'
    assert db.ingest_program(conn,p)
    assert db.export_data(conn)['programs'][0]['parent_programs'][0]['award_level'] is None
    p['parent_program_review']['status']='verified'
    with pytest.raises(ValueError,match='explicit parent and award'):db.ingest_program(conn,p)


@pytest.mark.parametrize('change',[
    {'source_ids':[]},{'source_ids':['missing']},{'title':''},{'relationship':'hosting_unit'},
    {'id':'bad/slash'},{'locator':''},{'reviewed_at':'unknown'},{'award_level':''},
    {'parent_program_id':'review-ai-bs'}])
def test_unproven_parent_preserves_existing_relationships(conn,change):
    p=parent_record();db.ingest_program(conn,p);p['parent_programs'][0].update(change)
    with pytest.raises(ValueError):db.ingest_program(conn,p)
    assert db.export_data(conn)['programs'][0]['parent_programs']==parent_record()['parent_programs']


def test_parent_source_foreign_key_and_uniqueness(conn):
    p=parent_record();db.ingest_program(conn,p)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute('INSERT INTO program_parent_sources VALUES (?,?,?)',(p['id'],'computer-science-bs','missing'))
    conn.rollback()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute('INSERT INTO program_parents SELECT * FROM program_parents')
    conn.rollback()


def test_migration_keeps_legacy_unknown_relationships_unknown(conn):
    p=program();db.ingest_program(conn,p);db.migrate(conn)
    exported=db.export_data(conn)['programs'][0]
    assert 'parent_programs' not in exported and 'major_relationship' not in exported
    assert not db.ingest_program(conn,p)


@pytest.mark.parametrize('field',['major_relationship','parent_programs','parent_program_review'])
def test_scraper_cannot_self_certify_or_erase_relationships(conn,field):
    p=parent_record() if field.startswith('parent') else second_record()
    db.ingest_program(conn,p);before=db.export_data(conn)['programs']
    class Fetch:
        def fetch(self,url,**kwargs):
            return FetchResult(url,'changed official page','new-hash','2026-10-11',200,False)
    module=SimpleNamespace(SOURCES=['https://catalog.example.edu/ai'],
        parse=lambda _: {'id':p['id'],field:p[field]})
    result=scrape_one(conn,p['id'],module,Fetch())
    assert result['new_candidates']==0 and 'cannot certify' in result['errors'][0]
    assert db.export_data(conn)['programs']==before


def test_real_second_major_inventory_is_explicit_not_unknown_award_inference():
    import json
    from pathlib import Path
    records=[json.loads(f.read_text()) for f in Path('data/programs').glob('*.json')]
    second=[p for p in records if p.get('major_relationship')]
    assert {p['id'] for p in second}=={
        'cmu-additional-ai','marquette-applied-ai-business-major','villanova-analytics-ai-co-major',
        'northwestern-ai-second-major-mccormick','northwestern-ai-second-major-non-mccormick'}
    for p in second:
        db.validate_program(p)
        assert major_award_buckets(p)==['second_major'] and p['award_level']=='other'
    assert all(major_award_buckets(p)!=['second_major'] for p in records if p['program_kind']=='degree')


def test_parent_atlas_link_must_exist_and_atomic_failure_preserves_record(conn):
    p=parent_record();db.ingest_program(conn,p)
    p['parent_programs'][0]['parent_program_id']='missing-parent'
    with pytest.raises(sqlite3.IntegrityError):db.ingest_program(conn,p)
    assert db.export_data(conn)['programs'][0]['parent_programs'][0]['parent_program_id'] is None
