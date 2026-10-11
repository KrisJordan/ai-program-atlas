import hashlib
import json
from pathlib import Path

import pytest

from atlas.csrankings import SNAPSHOT, displayed_score, join_roster, score_population, verify_sources


def author(dept, area, credit, year=2020):
    return {'name': 'Person', 'dept': dept, 'area': area, 'count': '100', 'adjustedcount': str(credit), 'year': str(year)}


def institution(name, country='us'):
    return {'institution': name, 'countryabbrv': country}


def row(results, dept, field):
    return next(r for r in results if r['upstream_institution'] == dept and r['field'] == field)


def test_fractional_credit_window_country_and_default_venues():
    results = score_population([
        author('A', 'aaai', .25), author('A', 'ijcai', .5),
        author('A', 'kdd', 999), author('A', 'aaai', 999, 2015),
        author('A', 'aaai', 999, 2026), author('Canada', 'aaai', 999),
        author('Unregistered', 'aaai', 999), author('A', 'iclr', .5, 2016),
        author('A', 'nips', .5, 2025),
    ], [institution('A'), institution('Empty'), institution('Canada', 'ca')])
    assert row(results, 'A', 'ai')['adjusted_count'] == .75
    assert row(results, 'A', 'ai')['value'] == 1.8
    assert row(results, 'A', 'mlmining')['adjusted_count'] == 1
    assert len(results) == 12
    assert row(results, 'Empty', 'aggregate')['missingness'] == 'no_selected_output'
    assert row(results, 'Empty', 'aggregate')['value'] is None


def test_geometric_aggregate_includes_zero_component_smoothing():
    results = score_population([author('A', 'aaai', 31)], [institution('A')])
    aggregate = row(results, 'A', 'aggregate')
    assert aggregate['unrounded_score'] == pytest.approx(2)
    assert aggregate['value'] == 2
    assert aggregate['adjusted_count'] is None
    assert aggregate['component_counts']['vision'] == 0
    assert row(results, 'A', 'vision')['adjusted_count'] is None
    assert row(results, 'A', 'vision')['rank'] is None


def test_round_before_competition_ties_and_preserve_full_population_rank():
    results = score_population([author('A', 'aaai', 1.24), author('B', 'aaai', 1.21), author('C', 'aaai', 1.1)],
                               [institution('A'), institution('B'), institution('C')])
    assert [row(results, dept, 'ai')['rank'] for dept in 'ABC'] == [1, 1, 3]
    joined = join_roster(results, {'institutions': [{'institution_id': 'c', 'status': 'matched', 'upstream_institution': 'C'}]}, [{'id': 'c'}])
    assert next(r for r in joined if r['field'] == 'ai')['rank'] == 3
    assert displayed_score(1.25) == 1.3  # JS positive halves, unlike bankers rounding


@pytest.mark.parametrize('status', ['not_listed', 'outside_eligible', 'unmatched', 'source_missing'])
def test_nonobserved_is_null_not_zero(status):
    rows = join_roster([], {'institutions': [{'institution_id': 'a', 'status': status, 'upstream_institution': None}]}, [{'id': 'a'}])
    assert len(rows) == 6
    for item in rows:
        assert item['missingness'] == status
        assert all(item[key] is None for key in ('value', 'rank', 'adjusted_count', 'unrounded_score', 'component_counts'))


def test_crosswalk_rejects_sibling_campus_duplication_and_missing_coverage():
    results = score_population([author('A', 'aaai', 1)], [institution('A')])
    mappings = [{'institution_id': name, 'status': 'matched', 'upstream_institution': 'A'} for name in ['a', 'b']]
    with pytest.raises(ValueError, match='duplicate'):
        join_roster(results, {'institutions': mappings}, [{'id': 'a'}, {'id': 'b'}])
    with pytest.raises(ValueError, match='every roster'):
        join_roster(results, {'institutions': mappings[:1]}, [{'id': 'a'}, {'id': 'b'}])


def test_snapshot_hash_guard(tmp_path):
    (tmp_path / 'data.csv').write_bytes(b'original')
    manifest = [{'filename': 'data.csv', 'url': f'https://raw.githubusercontent.com/emeryberger/CSrankings/{SNAPSHOT}/data.csv', 'sha256': hashlib.sha256(b'original').hexdigest()}]
    verify_sources(tmp_path, manifest)
    (tmp_path / 'data.csv').write_bytes(b'changed')
    with pytest.raises(ValueError, match='changed'):
        verify_sources(tmp_path, manifest)


def test_committed_artifact_consistency_and_unknown_semantics():
    base = Path(__file__).resolve().parents[1]
    artifact = json.loads((base / 'data/csrankings.json').read_text())
    crosswalk = json.loads((base / 'data/csrankings-crosswalk.json').read_text())
    roster = json.loads((base / 'data/cohort.json').read_text())['institutions']
    assert artifact['observations'] == join_roster(artifact['full_us_results'], crosswalk, roster)
    assert artifact['methodology']['crosswalk_sha256'] == hashlib.sha256((base / 'data/csrankings-crosswalk.json').read_bytes()).hexdigest()
    assert artifact['population']['listed_us_institutions'] == 201
    for item in artifact['full_us_results'] + artifact['observations']:
        if item['missingness'] != 'observed':
            assert all(item[k] is None for k in ('value', 'rank', 'adjusted_count', 'unrounded_score', 'component_counts'))
