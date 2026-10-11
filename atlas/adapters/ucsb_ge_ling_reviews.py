"""Exact public CSV observations; no HTML-shell or manual-audit replay."""
import csv
import hashlib
import io
import json
from pathlib import Path
from atlas.adapters import ucsb_ge_catalog_pools as pools

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())


def parse_csv(data):
    pools.parse_csv(data)
    rows = {r['Subject & Prefix'] + ' ' + r['Course Number']: r
            for r in csv.DictReader(io.StringIO(data))}
    courses = []
    for entry in SPEC['entries']:
        row = rows.get(entry['code'])
        digest = hashlib.sha256(json.dumps(row, sort_keys=True, ensure_ascii=False,
                                         separators=(',', ':')).encode()).hexdigest()
        if row is None or digest != entry['row_digest']:
            raise ValueError('UCSB reviewed GE content changed: ' + entry['code'])
        courses.append({**{k: entry[k] for k in ('id', 'code', 'name', 'description', 'credits', 'category')},
                        'credit_unit': 'quarter_hours', 'prerequisites': None,
                        'source_id': SPEC['source_id'], 'url': SPEC['source_url'],
                        'notes': list(entry['notes'])})
    return {'id': SPEC['program_id'], 'courses': courses}
