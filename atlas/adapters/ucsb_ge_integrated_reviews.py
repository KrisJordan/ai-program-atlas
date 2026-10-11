"""Compose completed cached GE source observations; never fetch the catalog shell.

Manual category audits and accepted crosslisting decisions live in the curated
program, not this repeatable source observer. Each child guards the full export
and its complete source rows before emitting metadata.
"""
from importlib import import_module
from . import ucsb_ge_catalog_pools

SUBJECT_BATCHES = (
    'ling', 'arthi', 'rgst', 'clit', 'engl', 'history_asam', 'social',
    'romance', 'classics_german_slavic', 'asia_portuguese_lais',
    'performing_arts', 'misc',
)


def parse_csv(data: str) -> dict:
    pools = ucsb_ge_catalog_pools.parse_csv(data)
    courses = []
    seen = set()
    for batch in SUBJECT_BATCHES:
        result = import_module(f'atlas.adapters.ucsb_ge_{batch}_reviews').parse_csv(data)
        for course in result['courses']:
            if course['id'] in seen:
                raise ValueError(f"Duplicate reviewed GE identity: {course['id']}")
            seen.add(course['id'])
            courses.append(course)
    if len(courses) != 856:
        raise ValueError('The reviewed GE export must contain all 856 source rows')
    return {**pools, 'courses': courses}
