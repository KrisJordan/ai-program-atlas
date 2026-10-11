"""Reviewed snapshots transact atomically and never silently turn missingness into zero."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from atlas import db
from atlas.csrankings import score_population, join_roster
from atlas.csrankings_store import ingest, validate_artifact


def artifact():
    results = score_population([
        dict(name='Faculty', dept='A', area='aaai', count='1', adjustedcount='1', year='2020')
    ], [dict(institution='A', countryabbrv='us'), dict(institution='Empty', countryabbrv='us')])
    method = json.loads((Path(__file__).resolve().parents[1] / 'data/csrankings.json').read_text())['methodology']
    mappings = {'institutions': [dict(institution_id='a', status='matched', upstream_institution='A'),
                                dict(institution_id='unknown', status='unmatched', upstream_institution=None)]}
    return dict(methodology=method, full_us_results=results,
                observations=join_roster(results, mappings, [dict(id='a'), dict(id='unknown')]))


def connection(tmp_path):
    conn = db.connect(tmp_path / 'research.sqlite'); db.migrate(conn)
    for iid in ('a', 'unknown'):
        db.upsert_institution(conn, dict(id=iid, name=iid, aliases=[], calendar='unknown', website='https://example.edu'))
    conn.commit()
    return conn


def test_snapshot_rerun_revision_export_and_configuration_preservation(tmp_path):
    conn = connection(tmp_path); original = artifact()
    assert ingest(conn, original)
    assert not ingest(conn, original)
    db.initialize_csrankings(conn)
    assert db.export_data(conn)['csrankings'] == original
    changed = deepcopy(original); changed['methodology']['retrieved_date'] = '2026-10-12'
    assert ingest(conn, changed)
    assert not ingest(conn, changed)
    assert conn.execute('SELECT count(*) FROM csrankings_revisions').fetchone()[0] == 2
    assert json.loads(conn.execute('SELECT artifact_json FROM csrankings_revisions ORDER BY id').fetchone()[0]) == original
    assert db.export_data(conn)['csrankings'] == changed
    assert not conn.execute('PRAGMA foreign_key_check').fetchall()
    conn.close()


@pytest.mark.parametrize('mutation', ['missing_selection', 'rank', 'matched_value', 'missing_to_zero', 'missing_components', 'unknown_state', 'partial_population', 'bad_component'])
def test_invalid_partial_or_changed_evidence_preserves_previous_snapshot(tmp_path, mutation):
    conn = connection(tmp_path); original = artifact(); ingest(conn, original)
    changed = deepcopy(original)
    if mutation == 'missing_selection': changed['observations'].pop()
    if mutation == 'rank': changed['full_us_results'][0]['rank'] = 2
    if mutation == 'matched_value': changed['observations'][0]['value'] = 99
    missing = next(r for r in changed['observations'] if r['missingness'] == 'unmatched')
    if mutation == 'missing_to_zero': missing['value'] = 0
    if mutation == 'missing_components': missing['component_counts'] = {'ai': 0}
    if mutation == 'unknown_state': missing['missingness'] = 'probably_bad'
    if mutation == 'partial_population': changed['full_us_results'].pop()
    if mutation == 'bad_component':
        next(r for r in changed['full_us_results'] if r['field'] == 'aggregate' and r['missingness'] == 'observed')['component_counts']['ai'] = -1
    with pytest.raises(ValueError): ingest(conn, changed)
    assert db.export_data(conn)['csrankings'] == original
    assert conn.execute('SELECT count(*) FROM csrankings_revisions').fetchone()[0] == 1
    conn.close()


def test_sql_failure_rolls_back_observations_configuration_and_revision(tmp_path):
    conn = connection(tmp_path); original = artifact(); ingest(conn, original)
    changed = deepcopy(original); changed['methodology']['retrieved_date'] = '2026-10-12'
    conn.execute("CREATE TRIGGER reject_research BEFORE INSERT ON csrankings_observations BEGIN SELECT RAISE(ABORT,'simulated storage failure'); END")
    conn.commit()
    with pytest.raises(Exception, match='simulated storage failure'): ingest(conn, changed)
    assert db.export_data(conn)['csrankings'] == original
    assert conn.execute('SELECT count(*) FROM csrankings_revisions').fetchone()[0] == 1
    conn.close()


def test_export_rejects_relational_corruption(tmp_path):
    conn = connection(tmp_path); ingest(conn, artifact())
    conn.execute("UPDATE csrankings_observations SET value=999 WHERE institution_id='a' AND field='ai'")
    with pytest.raises(ValueError, match='relational values'): db.export_data(conn)
    conn.close()


def test_complete_committed_snapshot_has_explicit_missingness_for_entire_roster():
    root = Path(__file__).resolve().parents[1]
    validate_artifact(json.loads((root/'data/csrankings.json').read_text()),
                      {i['id'] for i in json.loads((root/'data/cohort.json').read_text())['institutions']})
