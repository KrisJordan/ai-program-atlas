"""Bounded public petition/language policies and Cal-GETC context.

General UC guidance does not establish a particular college's waiver.
"""
import re
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import requirement, text
from atlas.adapters.ucsd_degree_policies import PID, guarded

PETITION_URL = 'https://cls.ucsd.edu/courses/petition.html'
LANGUAGE_URL = 'https://advising.ucsd.edu/students/degree-requirements/language-requirement.html'
CALGETC_URL = 'https://admission.universityofcalifornia.edu/admission-requirements/transfer-requirements/preparing-to-transfer/general-education-igetc/cal-getc/'


def body(html, heading):
    soup = BeautifulSoup(html, 'html.parser')
    if not any(text(h) == heading for h in soup.find_all(['h1', 'h2'])):
        raise ValueError('Policy heading changed')
    return soup, text(soup)


def result(pid, key, title, summary):
    return {'id': pid, 'curriculum_status': 'partial', 'requirements': [requirement(
        pid, 'closure-' + key, title, pid + '-closure-' + key,
        unit='quarter_hours', category='human_context', kind='note', summary=summary)]}


def parse_petition(html):
    _, value = body(html, 'How to Petition Courses')
    guarded(value, ['Course Syllabus (PDF)', 'Departmental Exception - Minors Only',
                    'College Exception - GE Requests', 'University Exception - DEI Requests',
                    'ONE PDF file', 'If your information is missing, it will not be processed'])
    match = re.search(r'at least (\d+)% or more Chicanx and Latinx Studies related content', value)
    if not match or not 0 < int(match[1]) <= 100:
        raise ValueError('CLS petition content threshold missing')
    return result(PID, 'cls-petition', 'Chicanx/Latinx petition evidence and separate approvals',
                  'A CLS minor petition needs the undergraduate petition form, course syllabus and supporting evidence of at least '
                  + match[1] + '% related subject content, combined into one PDF. The request must identify the exact requirement and intended use; incomplete requests are not processed. The form distinguishes departmental minor exceptions, college GE exceptions and university DEI exceptions. This minor-review threshold does not automatically authorize Warren GE credit, waive its rules or approve a starred seasonal offering. Community-college articulation is checked through ASSIST. No petition was submitted.')


def parse_language(html):
    soup, _ = body(html, 'Colleges, Majors, and Minors Requiring Language Courses')
    rows = [text(li) for li in soup.find_all('li') if text(li).startswith('Marshall')]
    if len(rows) != 1 or 'options for Disciplinary Breadth GE' not in rows[0]:
        raise ValueError('Marshall language classification changed')
    return result(PID, 'marshall-language', 'Marshall language route independently confirmed',
                  'Current undergraduate advising classifies Marshall language study as an option for disciplinary breadth GE. It supplies no course-level eligibility list or automatic proficiency waiver. Apply the separately verified major-discipline, course-unit, upper-division, writing and overlap rules; this directory does not resolve the broken language-course-list link.')


def parse_calgetc(html, pid=PID):
    _, value = body(html, 'Cal-GETC')
    guarded(value, ['fall 2025 or later', 'Complete all the Cal-GETC courses before you transfer',
                    'grades of a C or better', 'not a UC admission requirement',
                    'specific freshman/sophomore-level general education requirements of your UC college or school'])
    college = 'Seventh College' if pid == PID else 'UCSB Engineering'
    return result(pid, 'calgetc-context', 'UC Cal-GETC context; college applicability unresolved',
                  'UC admissions identifies Cal-GETC as the available CCC pattern for entrants from fall2025 onward. Complete the pattern before transfer; otherwise the receiving college or school evaluates its own lower-division GE. Courses require C or better, including Pass/Credit only where equivalent to C. The pattern is not required for UC admission. This systemwide page does not establish ' + college + ' specific substitutions, remaining requirements or certification treatment; retain that unresolved college decision rather than extend its IGETC rules by assumption.')
