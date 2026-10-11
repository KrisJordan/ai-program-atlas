"""Guarded observations of actually reviewed UCSB English public-export rows.

This is an explicit CSV evidence parser. A catalog HTML shell is not equivalent
input; runtime observations never emit independent reviews or requirement roles.
"""
import csv
import hashlib
import io
import json
from pathlib import Path
from atlas.adapters import ucsb_ge_catalog_pools as pools

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())


def parse_csv(data):
    pools.parse_csv(data)
    rows = {}
    for row in csv.DictReader(io.StringIO(data)):
        code = ' '.join((row['Subject & Prefix']+' '+row['Course Number']).split())
        if code in rows:
            raise ValueError('Duplicate normalized UCSB course identity')
        rows[code] = row
    courses = []
    for entry in SPEC['entries']:
        row = rows.get(entry['code'])
        digest = hashlib.sha256(json.dumps(row, sort_keys=True, ensure_ascii=False,
                                         separators=(',', ':')).encode()).hexdigest()
        if row is None or digest != entry['row_digest']:
            raise ValueError('UCSB reviewed English content changed: '+entry['code'])
        courses.append({**{k:entry[k] for k in ('id','code','name','description','credits','category')},
            'credit_unit':'quarter_hours', 'prerequisites':None,
            'source_id':SPEC['source_id'], 'url':SPEC['source_url'],
            'notes':list(entry['notes'])})
    return {'id':SPEC['program_id'], 'courses':courses}
