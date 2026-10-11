import pytest
from atlas.adapters.rit_english_communication_course_reviews import parse,SPECS,MANIFEST
URL='https://www.rit.edu/study/creative-writing-immersion'


def fixture():
    title=SPECS[URL][0]
    return f'<main><h1>{title}</h1><h2>Curriculum for 2026-2027 for {title}</h2><table class="sc_courselist"><tbody><tr><td><a class="code_bubble">ENGL-376</a></td><td>Experimental Writing</td><td>3</td></tr></tbody></table></main><div class="courseblock"><span class="detail-code">ENGL-376</span><span class="detail-title">Experimental Writing</span><span class="detail-hours_html">(3 Credits)</span><div class="courseblockextra">Critical reading of experimental literature.</div><span class="detail-contact_hours">Lecture 4</span><span class="detail-requisites">ENGL-211 or first-year writing or equivalent.</span></div>'


def test_actual_credit_and_prerequisite_operators_not_contact_hours_or_review_replay():
    c=parse(fixture(),url=URL)['courses'][0]
    assert c['credits']==3 and c['prerequisites']=='ENGL-211 or first-year writing or equivalent.'
    assert c['description']=='Critical reading of experimental literature.'
    assert c['category']=='other' and 'category_review'not in c
    assert parse(fixture().replace('Critical reading','Changed reading'),url=URL)['courses'][0]['description'].startswith('Changed')


@pytest.mark.parametrize('old,new',[('2026-2027','2027-2028'),('class="courseblockextra"','class="missing"'),('class="detail-code">ENGL-376','class="detail-code">ENGL-999'),('(3 Credits)','(three Credits)')])
def test_structure_edition_membership_and_credit_changes_reject(old,new):
    with pytest.raises(ValueError):parse(fixture().replace(old,new),url=URL)


def test_duplicate_popup_rejects_without_deduplicating_possible_conflicting_evidence():
    with pytest.raises(ValueError,match='Duplicate'):parse(fixture()+fixture(),url=URL)


def test_reviewed_writing_cultural_analysis_and_actual_production_are_distinguished():
    c=MANIFEST['courses'];assert len(c)==67
    assert sum(code.startswith('ENGL-')for code in c)==38
    assert sum(code.startswith('COMM-')for code in c)==29
    assert all(v['credits']==3 for v in c.values())
    for code in ['COMM-343','COMM-374','ENGL-315','ENGL-392','ENGL-543']:
        assert c[code]['category']=='human_context'
    assert c['COMM-223']['category']=='applications'
    assert c['ENGL-475']['category']=='applications'
    assert set(c['ENGL-320']['category_review']['candidate_categories'])=={'applications','human_context'}
    assert c['ENGL-379']['category_review']['status']=='mixed'
    assert c['COMM-322']['prerequisites']=='Prerequisites: COMM-211 and COMM-212 or equivalent courses.'
    assert c['COMM-321']['prerequisites']=='Prerequisites: COMM-211 or equivalent course.'
    assert c['COMM-304']['prerequisites']is None
    assert any('not a formal prerequisite' in n for n in c['COMM-304']['notes'])


def test_repeat_and_preparation_conditions_remain_specific():
    c=MANIFEST['courses']
    assert any('different instructors' in n for n in c['ENGL-389']['notes'])
    assert any('helpful but not required' in n for n in c['ENGL-389']['notes'])
    assert any('different topics' in n for n in c['ENGL-390']['notes'])
    assert any('4lecture contact hours' in n for n in c['ENGL-376']['notes'])
    assert sum(v['prerequisites']is not None for v in c.values())==17
    assert all(v['source_id']in {s['id']for s in MANIFEST['sources']}for v in c.values())
