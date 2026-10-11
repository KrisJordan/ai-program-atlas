"""Exact observed subjects; pool membership never certifies course subject matter."""
import json
from pathlib import Path

IDENTITIES = json.loads(Path(__file__).with_name('reviewed_subjects.json').read_text())


def classify_observed(observation):
    for course in observation.get('courses', []):
        reviewed = IDENTITIES.get(course['code'])
        course['category'] = (reviewed['category'] if reviewed and course['name'] == reviewed['name'] else 'other')
    return observation
