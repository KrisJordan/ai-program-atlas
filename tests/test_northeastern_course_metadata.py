"""Course metadata comes from live subject blocks, with no reviewed seed replay."""
import pytest
from atlas.adapters.northeastern_course_metadata import parse_subject


def page(block='', heading='Data Science (DS)'):
    return f'<header id="site-title"><h1>{heading}</h1></header><div id="textcontainer">{block}</div>'


def block(credits='4', prerequisite='CS 2100 with a minimum grade of D-', description='Introduces linear algebra and probability for AI.'):
    return f'''<div class="courseblock"><p class="courseblocktitle"><strong>DS 3000. Mathematical Foundations of Artificial Intelligence. ({credits} Hours)</strong></p><p class="cb_desc">{description}</p><p class="courseblockextra"><strong>Prerequisite(s): </strong>{prerequisite}</p></div>'''


def parse(html):
    return parse_subject(html,program_id='test-program',subject='DS',heading='Data Science (DS)',codes=['DS 3000'],url='https://catalog.northeastern.edu/course-descriptions/ds/')


def test_changed_metadata_changes_observation_and_no_review_claims():
    result=parse(page(block()))
    course=result['courses'][0]
    assert course['credits']==4
    assert 'CS 2100' in course['prerequisites']
    assert course['description']=='Studies the mathematical basis of AI through linear algebra, probability and computational exercises.'
    assert course['source_id']=='test-program-ds-courses'
    changed=parse(page(block('3','CS 2500 with a minimum grade of C')))
    assert changed['courses'][0]['credits']==3
    assert changed['courses'][0]['prerequisites']=='CS 2500 with a minimum grade of C'
    assert 'last_verified' not in result and 'curriculum_audit' not in result
    assert result['requirements']==[]


def test_changed_description_does_not_replay_unsupported_paraphrase():
    assert parse(page(block(description='This course has a different scope.')))['courses'][0]['description'] is None


def test_missing_prerequisite_remains_unknown():
    assert parse(page(block(prerequisite='')))['courses'][0]['prerequisites'] is None


@pytest.mark.parametrize('html',[
    page(block(),heading='Unrelated (XX)'),
    page(''),
    page('')+'<nav>'+block()+'</nav>',
    page(block()+block()),
])
def test_wrong_or_ambiguous_source_rejected(html):
    with pytest.raises(ValueError):parse(html)


def test_additional_description_prerequisite_preserved():
    html=page('''<div class="courseblock"><p class="courseblocktitle">LING 4654. Seminar in Linguistics. (4 Hours)</p><p class="cb_desc">Explores a topic in current linguistics research. Requires prior completion of either two 3000-level LING courses or one 3000-level LING course and permission of instructor.</p><p class="courseblockextra">Prerequisite(s): LING 2350 with a minimum grade of D-</p></div>''',heading='Linguistics (LING)')
    result=parse_subject(html,program_id='test-program',subject='LING',heading='Linguistics (LING)',codes=['LING 4654'],url='https://catalog.northeastern.edu/course-descriptions/ling/')
    prerequisites=result['courses'][0]['prerequisites']
    assert 'LING 2350' in prerequisites and 'two 3000-level LING courses' in prerequisites and 'permission of instructor' in prerequisites
