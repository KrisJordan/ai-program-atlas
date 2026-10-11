"""Observe the public Tableau crosstab, retaining campus/approval-term boundaries.

No descriptions, credits, prerequisites or editorial category review are supplied
by this membership source. The HTML shell is not an export or a successful parse.
"""
import csv
import hashlib
import io
import json
import re
from pathlib import Path

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())


def _digest(row):
    return hashlib.sha256(json.dumps(row, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def _term(value):
    if value == 'The End of Time':
        return (9999, 9)
    match = re.fullmatch(r'(Winter|Spring|Summer|Fall) (\d{4})', value)
    if not match:
        raise ValueError('Unknown approval-term expression')
    return int(match[2]), {'Winter': 0, 'Spring': 1, 'Summer': 2, 'Fall': 3}[match[1]]


def parse_tsv(data):
    if isinstance(data, bytes):
        data = data.decode('utf-16')
    reader = csv.DictReader(io.StringIO(data.lstrip('\ufeff')), delimiter='\t')
    if reader.fieldnames != SPEC['fields']:
        raise ValueError('Purdue UCC export columns changed')
    rows = list(reader)
    if len(rows) != SPEC['source_rows'] or sorted(_digest(r) for r in rows) != SPEC['all_row_digests']:
        raise ValueError('Purdue UCC complete export changed; review approvals and campus scope')
    selected = []
    for row in rows:
        if row['UCC Requirement'][:5] not in SPEC['selection']['outcomes'] or SPEC['selection']['campus'] not in row['CAMPUS_LIST'].split(', '):
            continue
        raw, name = row['Course '].split(' - ', 1)
        code = re.sub(r'(?<=[A-Z])(?=\d)', ' ', raw)
        selected.append(dict(outcome=row['UCC Requirement'], code=code, name=name,
                             campuses=row['CAMPUS_LIST'].split(', '),
                             approval_start=row['Academic Period Start'], approval_end=row['Academic Period End'],
                             eligible_in_reviewed_term=_term(row['Academic Period Start']) <= _term(SPEC['selection']['cohort_term']) <= _term(row['Academic Period End']),
                             source_id=SPEC['source_id']))
    return {'id': SPEC['program_id'], 'pool_memberships': selected}
