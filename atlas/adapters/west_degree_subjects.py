"""Exact reviewed title observations; unknown subjects never follow pool roles.

Independent category reviews live only in curated evidence, not parser output.
"""
from functools import wraps
import json
from pathlib import Path

_RAW = json.loads(Path(__file__).with_suffix('.json').read_text())
SUBJECTS = {pid: {(c['code'], c['name']): c['category'] for c in rows}
            for pid, rows in _RAW.items()}


def observe(parser, program_id):
    @wraps(parser)
    def wrapped(*args, **kwargs):
        result = parser(*args, **kwargs)
        for row in result.get('courses', []):
            row['category'] = SUBJECTS[program_id].get((row.get('code'), row.get('name')), 'other')
            row.pop('category_review', None)
        return result
    return wrapped
