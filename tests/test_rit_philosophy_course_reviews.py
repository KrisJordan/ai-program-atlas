import json
from pathlib import Path
import pytest
from atlas.adapters.rit_philosophy_course_reviews import parse
URL='https://www.rit.edu/study/philosophy-immersion'

def fixture():
    return '<main><h1>Philosophy Immersion</h1><h2>Curriculum for 2026-2027 for Philosophy Immersion</h2><table class="sc_courselist"><tbody><tr><td><a class="code_bubble">PHIL-205</a></td><td>Logic</td><td></td></tr></tbody></table></main><div class="courseblock"><span class="detail-code">PHIL-205</span><span class="detail-title">Symbolic Logic</span><span class="detail-hours_html">(3 Credits)</span><div class="courseblockextra">Synthetic proof and derivation content.</div></div>'


def test_actual_fields_are_observed_without_manual_logic_classification():
    a=parse(fixture(),url=URL);b=parse(fixture().replace('(3 Credits)','(4 Credits)'),url=URL)
    assert a['courses'][0]['credits']==3 and b['courses'][0]['credits']==4
    assert a['courses'][0]['category']=='other' and 'category_review' not in a['courses'][0]
    assert a['courses'][0]['prerequisites'] is None and a['courses'][0]['credit_unit']=='unknown'
    assert a['requirements']==[] and 'curriculum_audit' not in a


@pytest.mark.parametrize('a,b',[('2026-2027','2025-2026'),('class="detail-code">PHIL-205','class="detail-code">PHIL-999'),('class="courseblockextra"','class="missing"')])
def test_guards_version_identity_and_settled_content(a,b):
    with pytest.raises(ValueError):parse(fixture().replace(a,b),url=URL)


def test_individual_review_distinguishes_formal_methods_ethics_and_unknown_topic():
    c=json.loads(Path('atlas/adapters/rit_philosophy_course_reviews.json').read_text())['courses']
    assert len(c)==37 and all(x['credits']==3 for x in c.values())
    assert sum(x['prerequisites'] is not None for x in c.values())==13
    assert c['PHIL-205']['category']=='mathematics'
    assert c['PHIL-103']['category']==c['PHIL-320']['category']==c['MGMT-340']['category']=='human_context'
    assert c['PHIL-416']['category_review']['status']==c['PHIL-449']['category_review']['status']=='unclassified'
    assert 'permission' in c['PHIL-401']['notes'][0] and 'permission' not in c['PHIL-401']['prerequisites']
    assert 'PSYC-BS' in c['PHIL-402']['prerequisites']
    assert c['PHIL-504']['prerequisites'] is None and 'undergraduate and graduate' in c['PHIL-504']['notes'][0]
