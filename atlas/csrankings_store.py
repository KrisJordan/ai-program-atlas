"""Transactional storage of independently reviewed research-ranking snapshots."""
import math
import json

FIELDS = ('ai', 'vision', 'mlmining', 'nlp', 'inforet', 'aggregate')
MISSINGNESS = {'observed', 'no_selected_output', 'not_listed', 'outside_eligible', 'unmatched', 'source_missing'}


def validate_artifact(artifact, institution_ids):
    method = artifact.get('methodology', {})
    if method.get('status') != 'available' or method.get('fields') != list(FIELDS[:-1]):
        raise ValueError('CSRankings needs the explicit five-field available configuration')
    if method.get('aggregate_field') != 'aggregate' or method.get('geographic_filter') != 'us':
        raise ValueError('CSRankings needs an explicit US aggregate scope')
    if not isinstance(method.get('year_start'), int) or not isinstance(method.get('year_end'), int) or method['year_start'] > method['year_end']:
        raise ValueError('CSRankings needs an ordered publication-year window')
    for key in ('method', 'source_snapshot', 'source_url'):
        if not isinstance(method.get(key), str) or not method[key].strip():
            raise ValueError(f'CSRankings missing reproducibility field: {key}')
    if not method['source_url'].startswith('https://'):
        raise ValueError('CSRankings source must be an HTTPS citation')
    full = {}
    for row in artifact.get('full_us_results', []):
        key = (row.get('upstream_institution'), row.get('field'))
        if not key[0] or key[1] not in FIELDS or key in full:
            raise ValueError('Duplicate or invalid full-US CSRankings result')
        validate_observation(row)
        full[key] = row
    if not full:
        raise ValueError('CSRankings must compute the full US population before roster matching')
    names = {name for name, _ in full}
    if set(full) != {(name, field) for name in names for field in FIELDS}:
        raise ValueError('Full-US population needs all six selections for each listed institution')
    for field in FIELDS:
        observed = [r for (name, f), r in full.items() if f == field and r['missingness'] == 'observed']
        observed.sort(key=lambda row: -row['value'])
        previous = None; rank = None
        for index, row in enumerate(observed, 1):
            if row['value'] != previous:
                rank = index
            if row['rank'] != rank:
                raise ValueError('CSRankings ranks must be full-US competition ranks after display rounding')
            previous = row['value']
    seen = set()
    for row in artifact.get('observations', []):
        key = (row.get('institution_id'), row.get('field'))
        if key[0] not in institution_ids or key[1] not in FIELDS or key in seen:
            raise ValueError('Unknown or duplicate Atlas CSRankings observation')
        seen.add(key); validate_observation(row)
        if row.get('upstream_institution'):
            upstream = full.get((row['upstream_institution'], row['field']))
            if upstream is None:
                raise ValueError('CSRankings match is absent from the full-US calculation')
            for name in ('value', 'rank', 'missingness', 'adjusted_count', 'unrounded_score', 'component_counts'):
                if row.get(name) != upstream.get(name):
                    raise ValueError('CSRankings cohort match differs from full-US evidence')
    if seen != {(iid, field) for iid in institution_ids for field in FIELDS}:
        raise ValueError('Every Atlas institution needs six explicit CSRankings observations or missingness states')


def validate_observation(row):
    state = row.get('missingness')
    if state not in MISSINGNESS:
        raise ValueError('CSRankings needs explicit observation missingness')
    if state == 'observed':
        value, rank = row.get('value'), row.get('rank')
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError('Observed CSRankings score must be finite and positive')
        if isinstance(rank, bool) or not isinstance(rank, int) or rank < 1:
            raise ValueError('Observed CSRankings rank must be a positive integer')
        if not row.get('upstream_institution'):
            raise ValueError('Observed CSRankings values need a verified upstream institution')
        for key in ('adjusted_count', 'unrounded_score'):
            value = row.get(key)
            if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0):
                raise ValueError('CSRankings adjusted counts and scores must be finite and nonnegative')
        if row['field'] == 'aggregate':
            counts = row.get('component_counts')
            if not isinstance(counts, dict) or set(counts) != set(FIELDS[:-1]) or any(
                    isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0 for v in counts.values()):
                raise ValueError('Aggregate needs five finite nonnegative component counts')
        elif row.get('component_counts') is not None:
            raise ValueError('Individual field cannot carry aggregate components')
    elif any(row.get(key) is not None for key in ('value', 'rank', 'adjusted_count', 'unrounded_score', 'component_counts')):
        raise ValueError('Missing CSRankings evidence cannot become a zero score or last-place rank')


def ingest(conn, artifact):
    from . import db
    institution_ids = {row[0] for row in conn.execute('SELECT id FROM institutions')}
    validate_artifact(artifact, institution_ids)
    method = artifact['methodology']; fingerprint = db.digest(artifact)
    with db.atomic(conn):
        previous = conn.execute("SELECT value_json FROM metadata WHERE key='csrankings_artifact'").fetchone()
        if previous and db.digest(json.loads(previous[0])) == fingerprint:
            return False
        conn.execute('INSERT OR IGNORE INTO csrankings_revisions(content_hash,source_snapshot,imported_at,artifact_json) VALUES (?,?,?,?)',
                     (fingerprint, method['source_snapshot'], db.now(), db.canonical(artifact)))
        conn.execute('INSERT OR REPLACE INTO csrankings_config VALUES (1,?,?,?,?,?,?,?,?)',
                     (db.canonical(method['fields']), method['year_start'], method['year_end'], method['geographic_filter'],
                      method['method'], method['source_snapshot'], method['source_url'], method['status']))
        conn.execute('DELETE FROM csrankings_observations WHERE config_id=1')
        conn.executemany('INSERT INTO csrankings_observations VALUES (?,?,?,?,?,1)',
                         [(r['institution_id'], r['field'], r.get('value'), r.get('rank'), r['missingness']) for r in artifact['observations']])
        conn.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)', ('csrankings_artifact', db.canonical(artifact)))
    return True


def export(conn, config):
    row = conn.execute("SELECT value_json FROM metadata WHERE key='csrankings_artifact'").fetchone()
    observations = [dict(r) for r in conn.execute('SELECT * FROM csrankings_observations ORDER BY institution_id,field')]
    if not row:
        return {'methodology': config, 'observations': observations}
    artifact = json.loads(row[0])
    validate_artifact(artifact, {r[0] for r in conn.execute('SELECT id FROM institutions')})
    expected = {(r['institution_id'], r['field']): r for r in artifact['observations']}
    if len(observations) != len(expected):
        raise ValueError('CSRankings relational observations disagree with reviewed snapshot')
    for observed in observations:
        original = expected.get((observed['institution_id'], observed['field']))
        if not original or any(observed[key] != original.get(key) for key in ('value', 'rank', 'missingness')):
            raise ValueError('CSRankings relational values disagree with reviewed snapshot')
    for key in ('fields', 'year_start', 'year_end', 'geographic_filter', 'method', 'source_snapshot', 'source_url', 'status'):
        if config.get(key) != artifact['methodology'].get(key):
            raise ValueError('CSRankings relational configuration disagrees with reviewed snapshot')
    return artifact
