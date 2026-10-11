import json
from pathlib import Path
import pytest
from atlas.adapters.rit_biology_course_reviews import parse, SPECS
URL=next(iter(SPECS))

def fixture():
    title=SPECS[URL][0]
    return f'<main><h1>{title}</h1><h2>Curriculum for 2026-2027 for {title}</h2><table class="sc_courselist"><tbody><tr><td><a class="code_bubble">BIOL-216</a></td><td>Lab</td><td>1</td></tr></tbody></table></main><div class="courseblock"><span class="detail-code">BIOL-216</span><span class="detail-title">Biology Lab</span><span class="detail-hours_html">(1 Credit)</span><div class="courseblockextra">Synthetic molecular laboratory practice.</div><span class="detail-requisites">BIOL-206 concurrently.</span></div>'


def test_one_credit_lab_is_actual_course_amount_not_contact_hours():
    a=parse(fixture(),url=URL)
    assert a['courses'][0]['credits']==1 and a['courses'][0]['credit_unit']=='unknown'
    assert a['courses'][0]['prerequisites']=='BIOL-206 concurrently.'
    assert a['courses'][0]['category']=='other' and 'category_review' not in a['courses'][0]
    b=parse(fixture().replace('(1 Credit)','(4 Credits)'),url=URL)
    assert b['courses'][0]['credits']==4 and b['requirements']==[]


@pytest.mark.parametrize('before,after',[('2026-2027','2025-2026'),('class="courseblockextra"','class="missing"'),('class="detail-code">BIOL-216','class="detail-code">BIOL-999')])
def test_rejects_stale_missing_and_unbound_cards(before,after):
    with pytest.raises(ValueError):parse(fixture().replace(before,after),url=URL)


def test_all_13_actual_reviews_keep_credit_and_prerequisite_conditions():
    m=json.loads(Path('atlas/adapters/rit_biology_course_reviews.json').read_text());c=m['courses']
    assert len(c)==13
    assert sum(x['credits']==4 for x in c.values())==5
    assert sum(x['credits']==3 for x in c.values())==7
    assert c['BIOL-216']['credits']==1 and 'Co-requisite:BIOL-206&' in c['BIOL-216']['prerequisites']
    assert 'grade of C- or higher' in c['BIOL-206']['prerequisites']
    assert c['BIOL-311']['credits']==4 and c['BIOL-427']['credits']==4
    assert all(x['category']=='applications' and x['category_review']['status']=='reviewed' for x in c.values())
    assert 'Writing Intensive: General Education' in c['BIOL-240']['attributes']
