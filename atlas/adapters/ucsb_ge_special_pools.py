"""Observe special designations within the reviewed D/E/F/G export only.

This is an intersection, not the complete catalog-wide special-course pool.
The complete source-row observer guards all 856 rows before tags are read.
"""
import csv
import io
from . import ucsb_ge_catalog_pools

DESIGNATIONS = {'Writing': 'WRT', 'Ethnicity': 'ETH',
                'European Traditions': 'EUR', 'World Cultures': 'NWC',
                'Quantitative Relationships': 'QNT'}


def parse_csv(data: str) -> dict:
    reviewed = ucsb_ge_catalog_pools.parse_csv(data)
    memberships = []
    for row in csv.DictReader(io.StringIO(data)):
        if 'Special Subject Areas' not in row:
            raise ValueError('Missing special-designation field')
        raw = row['Special Subject Areas']
        labels = [] if raw == '-' else [s.strip() for s in raw.split(',')]
        if any(s not in DESIGNATIONS for s in labels):
            raise ValueError('Unknown UCSB special designation')
        memberships.append({'code': (row['Subject & Prefix']+' '+row['Course Number']).strip(),
                            'special_areas': [DESIGNATIONS[s] for s in labels]})
    return {'program_id': reviewed['program_id'], 'catalog_year': reviewed['catalog_year'],
            'pool_scope': 'Reviewed D/E/F/G intersection; full special-designation pool unverified',
            'special_memberships': memberships}
