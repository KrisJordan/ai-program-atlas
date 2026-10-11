import json
from pathlib import Path
import pytest
from atlas.adapters.rit_applied_science_course_reviews import parse
URL='https://www.rit.edu/study/climate-change-interdisciplinary-problem-immersion'
TITLE='Climate Change: An Interdisciplinary Problem Immersion'

def fixture():
    return f'<main><h1>{TITLE}</h1><h2>Curriculum for 2026-2027 for {TITLE}</h2><table class="sc_courselist"><tbody><tr><td><a class="code_bubble">ENVS-111</a></td><td>Soil Science</td><td>3</td></tr></tbody></table></main><div class="courseblock"><span class="detail-code">ENVS-111</span><span class="detail-title">Soil Science</span><span class="detail-hours_html">(4 Credits)</span><div class="courseblockextra">Synthetic soil sampling and laboratory analysis.</div></div>'


def test_actual_card_amount_wins_over_route_row_and_missing_prerequisite_stays_null():
    o=parse(fixture(),url=URL);c=o['courses'][0]
    assert c['credits']==4 and c['credit_unit']=='unknown' and c['prerequisites'] is None
    assert c['category']=='other' and 'category_review' not in c and 'curriculum_audit' not in o
    assert parse(fixture().replace('(4 Credits)','(2 Credits)'),url=URL)['courses'][0]['credits']==2
    assert o['requirements']==[]


@pytest.mark.parametrize('before,after',[('2026-2027','2025-2026'),('class="detail-code">ENVS-111','class="detail-code">ENVS-999'),('class="courseblockextra"','class="missing"')])
def test_rejects_wrong_year_unbound_identity_and_unsettled_description(before,after):
    with pytest.raises(ValueError):parse(fixture().replace(before,after),url=URL)


def test_manual_conditions_and_content_are_distinct_from_similar_titles():
    m=json.loads(Path('atlas/adapters/rit_applied_science_course_reviews.json').read_text());c=m['courses']
    assert len(c)==13 and sum(x['credits']==4 for x in c.values())==4
    assert 'Honors program' in c['ENVS-152H']['prerequisites']
    assert 'RIT Global' in c['ENVS-310']['prerequisites'] and 'additional fee' in c['ENVS-310']['notes'][0]
    assert c['MEDS-250']['prerequisites']==c['MEDS-251']['prerequisites']
    assert 'MEDS-250' not in c['MEDS-251']['prerequisites']
    assert c['CMPE-257']['category']=='foundations' and c['MEDS-201']['category']=='human_context'
    assert c['ENVS-531']['category_review']['status']==c['PUBL-531']['category_review']['status']=='mixed'
    assert c['ESHS-360']['category_review']['candidate_categories']==['applications','human_context']
    assert sum(x['category']=='applications' for x in c.values())==8
