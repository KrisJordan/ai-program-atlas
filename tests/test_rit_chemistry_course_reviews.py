import json
from pathlib import Path
import pytest
from atlas.adapters.rit_chemistry_course_reviews import parse
URL='https://www.rit.edu/study/chemistry-immersion'

def fixture():
    return '<main><h1>Chemistry Immersion</h1><h2>Curriculum for 2026-2027 for Chemistry Immersion</h2><table class="sc_courselist"><tbody><tr><td><a class="code_bubble">CHMG-145</a></td><td>Lab</td><td></td></tr></tbody></table></main><div class="courseblock"><span class="detail-code">CHMG-145</span><span class="detail-title">Chemical Lab</span><span class="detail-hours_html">(1 Credit)</span><div class="courseblockextra">Synthetic laboratory chemistry.</div></div>'


def test_source_bound_singular_credit_and_absent_prerequisite_remain_distinct():
    a=parse(fixture(),url=URL)['courses'][0]
    assert a['credits']==1 and a['credit_unit']=='unknown' and a['prerequisites'] is None
    assert a['category']=='other' and 'category_review' not in a
    for before,after in [('2026-2027','2025-2026'),('class="detail-code">CHMG-145','class="detail-code">CHMG-999'),('class="courseblockextra"','class="missing"')]:
        with pytest.raises(ValueError):parse(fixture().replace(before,after),url=URL)


def test_actual_chemistry_reviews_keep_preparation_labs_and_mixed_climate_scope():
    c=json.loads(Path('atlas/adapters/rit_chemistry_course_reviews.json').read_text())['courses']
    assert len(c)==12 and sum(x['credits']==1 for x in c.values())==2
    assert c['CHMG-131']['prerequisites'] is None and c['CHMG-141']['prerequisites'] is None
    assert 'Corequisites: CHMO-235' in c['CHMO-231']['prerequisites']
    assert 'Co-requisites: CHMA-315' in c['CHMA-311']['prerequisites']
    assert c['CHEM-531']['category_review']['status']=='mixed'
    assert c['CHEM-531']['category_review']['candidate_categories']==['applications','human_context']
    assert c['CHEM-531']['prerequisites'].endswith('at least 3rd year standing.')
    assert sum(x['category']=='applications' for x in c.values())==11
