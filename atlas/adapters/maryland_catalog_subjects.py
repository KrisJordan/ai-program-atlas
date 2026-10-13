"""Exact manually reviewed catalog-title candidates, never review certification.

Full descriptions remain unavailable for these entries. The whitelist records a
bounded source judgment, not a reusable classifier for arbitrary AI title text.
"""
from functools import wraps
import json
from pathlib import Path

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())


def observe(parser):
    @wraps(parser)
    def wrapped(*args, **kwargs):
        result = parser(*args, **kwargs)
        for course in result.get('courses', []):
            spec = SPEC.get(course.get('code'))
            if spec and course.get('name') == spec['name']:
                course['category'] = spec['category']
            # Observations never replay a manual review, confidence certification,
            # full-description summary or completeness/verification timestamp.
            course.pop('category_review', None)
        return result
    return wrapped
