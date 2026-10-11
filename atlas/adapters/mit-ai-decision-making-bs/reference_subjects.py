"""Limited judgments of exact printed reference titles, never descriptions."""
import json
from pathlib import Path

REVIEWS=json.loads(Path(__file__).with_name('reviewed_reference_subjects.json').read_text())


def observe(courses):
    for course in courses:
        reviewed=REVIEWS.get(course['id'])
        if reviewed:
            course['category']=reviewed['category'] if course['name']==reviewed['name'] else 'other'
    return courses
