import json
from pathlib import Path
import pytest
from atlas.adapters import uc_policy_closure as p
from atlas.db import validate_program


def test_petition_reads_threshold_without_implying_ge_approval():
    html = '''<h1>How to Petition Courses</h1><p>Course Syllabus (PDF);
    Departmental Exception - Minors Only; College Exception - GE Requests;
    University Exception - DEI Requests; ONE PDF file;
    If your information is missing, it will not be processed;
    at least 62% or more Chicanx and Latinx Studies related content</p>'''
    r = p.parse_petition(html)
    assert '62%' in r['requirements'][0]['summary']
    assert 'does not automatically authorize Warren GE credit' in r['requirements'][0]['summary']
    assert 'curriculum_audit' not in r
    with pytest.raises(ValueError):
        p.parse_petition(html.replace('62%', 'missing'))


def test_language_directory_is_not_a_course_approval_pool():
    html = '<h1>Colleges, Majors, and Minors Requiring Language Courses</h1><ul><li>Marshall – options for Disciplinary Breadth GE</li></ul>'
    r = p.parse_language(html)
    assert not r.get('courses')
    assert 'no course-level eligibility list' in r['requirements'][0]['summary']
    with pytest.raises(ValueError):
        p.parse_language(html.replace('options for Disciplinary Breadth GE', 'required'))


@pytest.mark.parametrize('pid,college', [(p.PID, 'Seventh College'), ('ucsb-ai-bs', 'UCSB Engineering')])
def test_general_calgetc_policy_keeps_local_waiver_unresolved(pid, college):
    html = '<h1>Cal-GETC</h1><p>fall 2025 or later; Complete all the Cal-GETC courses before you transfer; grades of a C or better; not a UC admission requirement; specific freshman/sophomore-level general education requirements of your UC college or school</p>'
    r = p.parse_calgetc(html, pid)
    assert 'does not establish ' + college in r['requirements'][0]['summary']
    assert r['curriculum_status'] == 'partial'
    d = json.loads(Path('data/programs/' + pid + '.json').read_text())
    validate_program(d)
    assert any(n['id'] == pid + '-closure-calgetc-context' for n in d['requirements'])
