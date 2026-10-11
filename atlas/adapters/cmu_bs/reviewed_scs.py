"""Source observations for the 51 manually reviewed SCS course descriptions."""
import json
from pathlib import Path
from bs4 import BeautifulSoup
from .common import text, requirement
from .course_metadata import parse_metadata

PID = 'cmu-bs-ai'
SID = PID + '-course-directory'
SUBJECTS = json.loads(Path(__file__).with_name('reviewed_scs_subjects.json').read_text())
CONDITIONS = {
 '15-151': ('Open to CS freshmen only', 'The catalog limits this course to CS freshmen; the AI degree separately specifies its conditional substitution rule. Enrollment permission is not inferred.'),
 '05-391': ('undergraduate students are automatically placed the wait list', 'Undergraduate registration enters a waitlist; HCI minor/SCS concentration students receive stated priority. This does not make an AI elective choice automatically enrollable.'),
 '16-385': ('undergraduate students only', 'Enrollment is restricted to undergraduates.'),
 '07-128': ('Enrollment is limited to SCS First Year students ONLY', 'The first-year seminar is limited to SCS first-year students.'),
 '07-402': ('Students are enrolled by invitation only', 'Enrollment requires invitation.'),
 '17-562': ('Open to sophomores by permission of the instructor', 'Juniors, seniors and graduate students may enroll; sophomores require instructor permission.'),
 '10-423': ('Before registering, you must review the full policy on the course website', 'The description requires reviewing the course recording policy before registration and agreeing to recording authorization to attend. Individual consent or policy acceptance is not inferred.'),
}


def parse(html):
    observed = parse_metadata(html, pid=PID, codes=set(SUBJECTS))
    if {c['code'] for c in observed['courses']} != set(SUBJECTS):
        raise ValueError('Reviewed SCS course inventory changed')
    for c in observed['courses']:
        review = SUBJECTS[c['code']]
        digest = observed['observed_description_digests'][c['code']]
        c['category'] = review['category'] if c['name'] == review['name'] and digest == review['description_digest'] else 'other'
    soup = BeautifulSoup(html, 'html.parser')
    blocks = {text(b.dt).split()[0]: b for b in soup.find_all('dl', class_='courseblock') if b.dt and b.dd}
    for code, (marker, summary) in CONDITIONS.items():
        if marker not in text(blocks[code].dd):
            raise ValueError('SCS course-entry condition changed: ' + code)
        observed['requirements'].append(requirement(PID, 'course-entry-' + code, 'Course-entry condition: ' + code, SID, kind='note', summary=summary))
    return observed


def classify_titles(observed):
    """Primary-list observations do not imply a new description review."""
    for c in observed.get('courses', []):
        review = SUBJECTS.get(c['code'])
        if review:
            c['category'] = review['category'] if c['name'] == review['name'] else 'other'
    return observed
