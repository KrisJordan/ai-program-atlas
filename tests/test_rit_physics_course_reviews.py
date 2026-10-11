import json
from pathlib import Path
import pytest
from atlas.adapters.rit_physics_course_reviews import parse
URL='https://www.rit.edu/study/physics-immersion'

def fixture():
    return '<main><h1>Physics Immersion</h1><h2>Curriculum for 2026-2027 for Physics Immersion</h2><table class="sc_courselist"><tbody><tr><td><a class="code_bubble">PHYS-320</a></td><td>Methods</td><td>3</td></tr></tbody></table></main><div class="courseblock"><span class="detail-code">PHYS-320</span><span class="detail-title">Mathematical Methods</span><span class="detail-hours_html">(3 Credits)</span><div class="courseblockextra">Synthetic mathematical tools course.</div><span class="detail-requisites">Calculus or equivalent.</span></div>'


def test_observation_extracts_current_content_without_manual_subject_review():
    r=parse(fixture(),url=URL)
    assert r['courses'][0]['category']=='other' and 'category_review' not in r['courses'][0]
    assert r['courses'][0]['credits']==3 and r['courses'][0]['credit_unit']=='unknown'
    assert parse(fixture().replace('(3 Credits)','(4 Credits)'),url=URL)['courses'][0]['credits']==4
    for before,after in [('2026-2027','2025-2026'),('class="courseblockextra"','class="missing"'),('class="detail-code">PHYS-320','class="detail-code">PHYS-999')]:
        with pytest.raises(ValueError):parse(fixture().replace(before,after),url=URL)


def test_manual_subject_and_program_specific_entry_conditions():
    c=json.loads(Path('atlas/adapters/rit_physics_course_reviews.json').read_text())['courses']
    assert len(c)==16 and sum(v['category']=='applications' for v in c.values())==15
    assert c['PHYS-320']['category']=='mathematics'
    assert sum(v['credits']==4 for v in c.values())==4
    assert '(PHYS-BS or PHYS-MN or PHYS-IM)' in c['PHYS-315']['prerequisites']
    assert 'Students in the PHYS-BS program are also required' in c['PHYS-330']['prerequisites']
    assert 'Co-requisites: PHYS-320' in c['PHYS-330']['prerequisites']
    assert 'Writing Intensive: General Education' in c['PHYS-315']['attributes']
    assert 'MATH-241H' in c['PHYS-414']['prerequisites']
