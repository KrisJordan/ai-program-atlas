"""Replay bounded Asia/Portuguese/LAIS facts only for the unchanged official GE export.

Manual category reviews stay in the manifest for program-owner integration.
This helper does not infer prerequisites, requirement roles, or identities.
"""
import csv
import hashlib
import io
import json
from copy import deepcopy
from pathlib import Path

from atlas.adapters import ucsb_ge_catalog_pools as pools

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())
SOURCES = [SPEC['source_url']]


def parse_csv(data):
    """Validate the full export and every owned row, then emit course facts."""
    pools.parse_csv(data)
    rows = {}
    for row in csv.DictReader(io.StringIO(data)):
        if row['Subject & Prefix'] not in SPEC['subjects']:
            continue
        code = row['Subject & Prefix'] + ' ' + row['Course Number']
        if code in rows:
            raise ValueError('Duplicate UCSB Asia/Portuguese/LAIS source row: ' + code)
        rows[code] = row
    if set(rows) != {entry['source_code'] for entry in SPEC['entries']}:
        raise ValueError('UCSB Asia/Portuguese/LAIS scope changed; review required')
    courses = []
    for entry in SPEC['entries']:
        row = rows[entry['source_code']]
        digest = hashlib.sha256(json.dumps(
            row, sort_keys=True, ensure_ascii=False, separators=(',', ':')
        ).encode()).hexdigest()
        if digest != entry['row_digest']:
            raise ValueError('Reviewed UCSB Asia/Portuguese/LAIS source row changed: ' + entry['code'])
        course = {key: deepcopy(entry[key]) for key in (
            'id', 'code', 'name', 'description', 'credits', 'credit_unit',
            'category', 'notes'
        )}
        course.update(prerequisites=None, source_id=SPEC['source_id'], url=SPEC['source_url'])
        courses.append(course)
    return {'id': SPEC['program_id'], 'courses': courses}
