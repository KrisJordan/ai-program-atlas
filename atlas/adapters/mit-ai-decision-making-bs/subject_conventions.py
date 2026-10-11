"""Catalog's published subject notation; no inferred credit conversion."""
import re
from atlas.adapters.national_curriculum_common import content, require_phrases, rule

PID = 'mit-ai-decision-making-bs'
URL = 'https://catalog.mit.edu/subjects/'
SID = PID + '-subject-conventions'


def credits(annotation):
    """Only a complete three-component unit expression has a known total."""
    match = re.search(r'Units: (\d+)-(\d+)-(\d+)(?=\s|$)', annotation)
    return sum(map(int, match.groups())) if match else None


def parse(html):
    root = content(html, 'Subjects')
    require_phrases(root, ['How to Read Subject Descriptions',
        'The total unit credit for a subject is obtained by adding together all the units shown.',
        'Students who have not completed the stated prerequisites must obtain the instructor',
        'Subjects that meet together have different coursework requirements.',
        'Credit cannot also be received for'])
    return dict(id=PID, courses=[], requirements=[
        rule('mit-ai-subject-units', 'Published unit notation', SID, kind='note',
             summary='The three unit components represent class time, laboratory/design/fieldwork, and preparation; their sum is the subject total. Units arranged remains instructor-arranged. This is MIT units, not a conversion to another credit system.'),
        rule('mit-ai-subject-entry', 'Prerequisite and identity notation', SID, kind='note',
             summary='Missing stated prerequisites require instructor permission to register. Descriptions may add prerequisites; corequisites are simultaneous and implicit prerequisites may be omitted. Same subject as establishes a cross-list; meets with can have different coursework. Credit cannot also be received for marks a credit exclusion, not identity. Special-group restrictions remain applicable.')])


SOURCE_PARSERS = {URL: parse}
