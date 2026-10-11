"""Guard a public UI-exported GE pool; do not certify course content or roles.

The CSV is downloaded through the catalog's ordinary Export all results button.
The course-search HTML shell is not a CSV and cannot refresh this inventory.
"""
import csv
import hashlib
import io
import json
from pathlib import Path

SPEC=json.loads(Path(__file__).with_suffix('.json').read_text())


def parse_csv(data):
    rows=list(csv.DictReader(io.StringIO(data)))
    if len(rows)!=SPEC['export_row_count']:
        raise ValueError('UCSB GE pool row count changed; review required')
    observed={}
    for row in rows:
        if not {'Subject & Prefix','Course Number','Full Course Title','General Subject Areas'} <= row.keys():
            raise ValueError('UCSB GE export columns changed')
        code=row['Subject & Prefix']+' '+row['Course Number']
        if code in observed:
            raise ValueError('Duplicate UCSB GE code in export')
        observed[code]=row
    output=[]
    for entry in SPEC['entries']:
        row=observed.get(entry['code'])
        digest=hashlib.sha256(json.dumps(row,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
        if row is None or digest!=entry['row_digest']:
            raise ValueError('UCSB GE source row changed: '+entry['code'])
        output.append({'code':entry['code'],'name':entry['name'],'general_areas':list(entry['general_areas'])})
    return {'program_id':SPEC['program_id'],'catalog_year':SPEC['catalog_year'],'pool_memberships':output}
