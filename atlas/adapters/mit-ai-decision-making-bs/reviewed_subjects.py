"""Observed annotations reuse a manual subject judgment only on exact evidence."""
import hashlib
import json
from pathlib import Path

SUBJECTS = json.loads(Path(__file__).with_name('reviewed_versioned_subjects.json').read_text())


def classify(course, annotation):
    reviewed = SUBJECTS.get(course['code'])
    if reviewed is None:
        return None
    digest = hashlib.sha256(annotation.encode()).hexdigest() if annotation else None
    course['category'] = reviewed['category'] if course['name'] == reviewed['name'] and digest == reviewed['annotation_digest'] else 'other'
    # A parser observation is not a new review, including when content matches.
    return digest
