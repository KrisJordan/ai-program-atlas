import json
from pathlib import Path
import pytest
from atlas.adapters.rit_statistics_course_reviews import parse


def fixture():
    return '<main><h1>Applied Statistics Immersion</h1><h2>Curriculum for 2026-2027 for Applied Statistics Immersion</h2><table class="sc_courselist"><tbody><tr><td><a class="code_bubble">STAT-330</a></td><td>Data Visualization</td><td></td></tr></tbody></table></main><div class="courseblock"><span class="detail-code">STAT-330</span><span class="detail-title">Data Visualization</span><span class="detail-hours_html">(3 Credits)</span><div class="courseblockextra">Synthetic visualization design and practice.</div><span class="detail-requisites">STAT-205 or equivalent.</span></div>'


def test_extracts_actual_changed_fields_without_manual_reviews():
    a=parse(fixture());b=parse(fixture().replace('(3 Credits)','(4 Credits)').replace('STAT-205 or equivalent.','Permission required.'))
    assert a['courses'][0]['credits']==3 and b['courses'][0]['credits']==4
    assert b['courses'][0]['prerequisites']=='Permission required.'
    assert a['courses'][0]['credit_unit']=='unknown'
    assert a['courses'][0]['category']=='other'
    assert 'category_review' not in a['courses'][0]
    assert a['requirements']==[] and 'curriculum_audit' not in a


@pytest.mark.parametrize('before,after', [('2026-2027','2025-2026'),('class="courseblockextra"','class="missing"'),('class="sc_courselist"','class="shell"'),('class="detail-code">STAT-330','class="detail-code">STAT-999')])
def test_rejects_missing_version_table_body_and_unbound_identity(before,after):
    with pytest.raises(ValueError):parse(fixture().replace(before,after))


def test_manual_review_retains_enrollment_conditions_and_separate_subject_judgment():
    m=json.loads(Path('atlas/adapters/rit_statistics_course_reviews.json').read_text())
    c=m['courses'];assert len(c)==11
    assert all(x['credits']==3 and x['credit_unit']=='semester_hours' for x in c.values())
    assert sum(x['category']=='mathematics' for x in c.values())==10
    assert c['STAT-330']['category']=='applications'
    assert 'MATH-241 and (MATH-252 or STAT-205 or STAT-257) or equivalent' in c['STAT-305']['prerequisites']
    assert 'STAT-405' in c['STAT-406']['prerequisites']
    assert 'Writing Intensive: General Education' in c['STAT-325']['attributes']
    assert 'STAT-145' in c['STAT-205']['restrictions'][0]
