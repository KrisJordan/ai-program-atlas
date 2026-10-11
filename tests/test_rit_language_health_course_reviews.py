import pytest
from atlas.adapters.rit_language_health_course_reviews import parse,SPECS,MANIFEST
URL='https://www.rit.edu/study/american-sign-language-and-deaf-cultural-studies-immersion'


def fixture():
    title=SPECS[URL][0]
    return f'<main><h1>{title}</h1><h2>Curriculum for 2026-2027 for {title}</h2><table class="sc_courselist"><tbody><tr><td><a class="code_bubble">NASL-180</a></td><td>New Signers Program</td><td>4</td></tr></tbody></table></main><div class="courseblock"><span class="detail-code">NASL-180</span><span class="detail-title">New Signers Program</span><span class="detail-hours_html">(4 Credits)</span><div class="courseblockextra">ASL communication for new signers.</div><span class="detail-contact_hours">Laboratory 4, Lecture 2</span><span class="detail-requisites">NTID supported students with placement score 0.</span></div>'


def test_actual_credit_not_contact_hours_and_runtime_does_not_replay_review():
    course=parse(fixture(),url=URL)['courses'][0]
    assert course['credits']==4 and course['prerequisites']=='NTID supported students with placement score 0.'
    assert course['category']=='other' and 'category_review'not in course
    assert parse(fixture().replace('ASL communication','Changed content'),url=URL)['courses'][0]['description'].startswith('Changed content')


@pytest.mark.parametrize('old,new',[('2026-2027','2027-2028'),('class="courseblockextra"','class="missing"'),('class="detail-code">NASL-180','class="detail-code">NASL-999'),('(4 Credits)','(four Credits)')])
def test_edition_membership_missing_description_and_unrecognized_credits_reject(old,new):
    with pytest.raises(ValueError):parse(fixture().replace(old,new),url=URL)


def test_duplicate_cards_are_not_silently_deduplicated():
    with pytest.raises(ValueError,match='Duplicate'):parse(fixture()+fixture(),url=URL)


def test_source_scoped_credit_eligibility_and_communication_taxonomy():
    courses=MANIFEST['courses'];assert len(courses)==31
    assert sum(c['credits']==4 for c in courses.values())==6
    assert sum(c['credits']==3 for c in courses.values())==25
    assert sum(c['prerequisites']is not None for c in courses.values())==15
    for code in ['MLAS-352','LING-302','NASL-275','NHSS-275','MLFR-151']:
        assert courses[code]['category']=='human_context'
    assert courses['LING-449']['category_review']['status']=='unclassified'
    assert courses['GLPH-105']['category']=='applications'
    assert courses['DCHP-301']['category_review']['status']=='mixed'
    assert 'C- or D' in courses['NASL-190']['prerequisites']
    assert 'MLAS-401' in courses['NASL-230']['prerequisites']
    assert 'MLAS-301' in courses['NASL-240']['prerequisites']
    assert any('AOS or CARPRP-UND' in n for n in courses['NHSS-251']['notes'])
    assert any('fluency' in n for n in courses['MLAS-352']['notes'])
    assert courses['MLAS-352']['prerequisites']is None
    assert any('unlabelled parenthetical' in n for n in courses['MEDG-106']['notes'])
    assert set(c['source_id']for c in courses.values())=={s['id']for s in MANIFEST['sources']}
