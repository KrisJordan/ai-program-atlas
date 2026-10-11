"""Course teaching resources are distinct from curricular evidence pages."""
import json
from pathlib import Path
REVIEWS=json.loads(Path(__file__).with_name('reviewed_public_resources.json').read_text())['courses']


def observed_resources(course_id, observed_url):
    reviewed=REVIEWS.get(course_id)
    if reviewed is None or reviewed['public_site']!=observed_url:
        return dict(public_site=None,syllabus=None)
    return dict(public_site=reviewed['public_site'],syllabus=reviewed['syllabus'])
