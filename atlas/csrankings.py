"""Original, snapshot-pinned CSRankings scoring for the Atlas educational project.

The input adjustedcount is the upstream fractional author credit, already rounded
by its data generator. Never replace it with paper count or faculty-size averages.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Iterable

SNAPSHOT = '5e8a27d68310c728a182b8bb3b6437c39bce0cad'
FIELDS = ('ai', 'vision', 'mlmining', 'nlp', 'inforet')
VENUES = {
    'ai': ('aaai', 'ijcai'),
    'vision': ('cvpr', 'eccv', 'iccv'),
    'mlmining': ('iclr', 'icml', 'nips'),
    'nlp': ('acl', 'emnlp', 'naacl'),
    'inforet': ('sigir', 'www'),
}
DIMENSIONS = (*FIELDS, 'aggregate')
NONOBSERVED = {'no_selected_output', 'not_listed', 'outside_eligible', 'unmatched', 'source_missing'}


def verify_sources(directory: Path, sources: list[dict]) -> None:
    for source in sources:
        filename = source['filename']
        if Path(filename).name != filename or source['url'] != f'https://raw.githubusercontent.com/emeryberger/CSrankings/{SNAPSHOT}/{filename}':
            raise ValueError('Source must identify a plain filename at the pinned official commit')
        path = directory / filename
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
            raise ValueError(f"Missing or changed pinned source: {source['filename']}")


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def displayed_score(score: float) -> float:
    """JavaScript Math.round for finite nonnegative publication scores."""
    return math.floor(score * 10 + 0.5) / 10


def score_population(authors: Iterable[dict], institutions: Iterable[dict],
                     year_start: int = 2016, year_end: int = 2025) -> list[dict]:
    """Rank the complete upstream US population, separately for each selection.

    Rows for listed institutions with no selected output remain null. For an
    observed aggregate only, absent component counts are zero for +1 smoothing.
    """
    if year_start > year_end:
        raise ValueError('Inverted year window')
    us = {row['institution']: row for row in institutions if row['countryabbrv'] == 'us'}
    venue_field = {venue: field for field, venues in VENUES.items() for venue in venues}
    totals: dict[tuple[str, str], float] = {}
    present: set[tuple[str, str]] = set()
    for row in authors:
        dept, venue = row['dept'], row['area']
        if dept not in us or venue not in venue_field or not year_start <= int(row['year']) <= year_end:
            continue
        count = float(row['adjustedcount'])
        if not math.isfinite(count) or count <= 0:
            raise ValueError('Selected upstream credit must be finite and positive')
        key = (dept, venue_field[venue])
        totals[key] = totals.get(key, 0.0) + count
        present.add(key)
    results = []
    for dept in sorted(us):
        counts = {field: totals.get((dept, field), 0.0) for field in FIELDS}
        for field in DIMENSIONS:
            observed = any((dept, component) in present for component in FIELDS) if field == 'aggregate' else (dept, field) in present
            score = math.prod(counts[f] + 1 for f in FIELDS) ** (1 / len(FIELDS)) if field == 'aggregate' else counts[field] + 1
            results.append({
                'upstream_institution': dept, 'field': field,
                'value': displayed_score(score) if observed else None,
                'rank': None,
                'missingness': 'observed' if observed else 'no_selected_output',
                'adjusted_count': counts[field] if observed and field != 'aggregate' else None,
                'unrounded_score': score if observed else None,
                'component_counts': counts.copy() if observed and field == 'aggregate' else None,
            })
    for field in DIMENSIONS:
        ranked = sorted((row for row in results if row['field'] == field and row['missingness'] == 'observed'),
                        key=lambda row: (-row['value'], row['upstream_institution']))
        last_value, rank = None, None
        for position, row in enumerate(ranked, 1):
            if row['value'] != last_value:
                rank = position
                last_value = row['value']
            row['rank'] = rank
    return results


def join_roster(results: list[dict], crosswalk: dict, roster: list[dict]) -> list[dict]:
    entries = crosswalk['institutions']
    ids = [entry['institution_id'] for entry in entries]
    if len(ids) != len(set(ids)) or set(ids) != {row['id'] for row in roster}:
        raise ValueError('Crosswalk must cover every roster ID exactly once')
    lookup = {(row['upstream_institution'], row['field']): row for row in results}
    used: set[str] = set()
    observations = []
    for entry in entries:
        status, upstream = entry['status'], entry.get('upstream_institution')
        if status == 'matched':
            if upstream in used or (upstream, 'aggregate') not in lookup:
                raise ValueError(f'Invalid or duplicate upstream crosswalk: {upstream}')
            used.add(upstream)
        elif status not in {'not_listed', 'outside_eligible', 'unmatched', 'source_missing'} or upstream is not None:
            raise ValueError('Invalid crosswalk status/name')
        for field in DIMENSIONS:
            row = dict(lookup[(upstream, field)]) if status == 'matched' else {
                'upstream_institution': None, 'field': field, 'value': None, 'rank': None,
                'missingness': status, 'adjusted_count': None, 'unrounded_score': None, 'component_counts': None,
            }
            observations.append({'institution_id': entry['institution_id'], **row})
    return observations


def build_artifact(source_dir: Path, crosswalk_path: Path, cohort_path: Path) -> dict:
    crosswalk = json.loads(crosswalk_path.read_text())
    if crosswalk['source_snapshot'] != SNAPSHOT:
        raise ValueError('Crosswalk snapshot does not match scorer snapshot')
    sources = crosswalk['sources']
    verify_sources(source_dir, sources)
    institutions = read_csv(source_dir / 'institutions.csv')
    results = score_population(read_csv(source_dir / 'generated-author-info.csv'), institutions)
    roster = json.loads(cohort_path.read_text())['institutions']
    observations = join_roster(results, crosswalk, roster)
    return {
        'methodology': {
            'fields': list(FIELDS), 'aggregate_field': 'aggregate',
            'field_membership': {field: list(venues) for field, venues in VENUES.items()},
            'year_start': 2016, 'year_end': 2025, 'geographic_filter': 'us',
            'method': 'CSRankings fractional author credit; +1 field scores; five-field geometric mean; one-decimal display rounding; competition ranks',
            'source_snapshot': SNAPSHOT, 'source_url': 'https://csrankings.org/', 'status': 'available',
            'source_commit_date': '2026-09-28T04:21:02Z', 'retrieved_date': '2026-10-11',
            'commit_resolution_evidence': crosswalk['commit_resolution_evidence'],
            'upstream_defaults_as_of_retrieval': {'year_start': 2016, 'year_end': 2026, 'kdd_enabled': False, 'dense_ranking': False},
            'excluded_next_tier_venues': ['kdd'],
            'value_semantics': 'Displayed upstream score, rounded to one decimal before sorting and assigning ties; individual field score = adjusted_count + 1; aggregate score = product(component_count + 1) ** (1/5), without subtracting one.',
            'adjusted_count_semantics': 'Sum of pinned generated-author-info.csv adjustedcount in CSV order for selected venues/years/current department; aggregate adjusted_count is null.',
            'missingness_semantics': {'observed': 'Selected publication output in the pinned US population.', 'no_selected_output': 'Upstream US institution is listed but has no output in this selection/window.', 'not_listed': 'No corresponding institution is listed in the complete pinned US institution registry; PhD eligibility is not inferred.', 'outside_eligible': 'Separately evidenced as outside upstream eligibility.', 'unmatched': 'Institution identity cannot be resolved safely.', 'source_missing': 'Necessary source information unavailable.'},
            'faculty_scope': 'Upstream full-time tenure-track faculty with at least 75% appointment who can solely advise CS PhD students; affiliations reflect the pinned snapshot, not historical affiliation.',
            'permission': {'statement': 'We have permission to use csrankings data for this educational project.', 'confirmed_date': '2026-10-11', 'authority': 'Project owner statement in user conversation', 'scope': 'This educational project', 'permission_document': None, 'broader_permission_inferred': False},
            'attribution': {'project': 'CSRankings', 'maintainer': 'Emery Berger and contributors', 'repository': 'https://github.com/emeryberger/CSrankings', 'license_url': 'https://github.com/emeryberger/CSrankings/blob/' + SNAPSHOT + '/COPYING', 'license': 'CC BY-NC-ND 4.0; project use separately authorized by owner statement', 'publication_data': 'DBLP; attribution notice retained in upstream README (Open Data Commons Attribution License).'},
            'limitations': ['Research publication indicator, not undergraduate teaching or AI curriculum quality.', 'Not normalized by faculty size.', 'The project window excludes partial 2026; it is not the live site default.', 'Upstream fractional values have source precision; no reconstruction of unrounded paper-author fractions.'],
            'sources': sources,
            'crosswalk_sha256': hashlib.sha256(crosswalk_path.read_bytes()).hexdigest(),
            'cohort_sha256': hashlib.sha256(cohort_path.read_bytes()).hexdigest(),
        },
        'population': {'listed_us_institutions': len(results) // len(DIMENSIONS), 'ranked_institutions_by_field': {field: sum(r['field'] == field and r['missingness'] == 'observed' for r in results) for field in DIMENSIONS}, 'roster_institutions': len(roster), 'ranking_scope': 'Full upstream US positive-output population for each selection, before project roster join'},
        'observations': observations,
        'full_us_results': results,
    }
