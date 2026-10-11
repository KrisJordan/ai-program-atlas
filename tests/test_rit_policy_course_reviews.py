"""Synthetic observed HTML, never a claim of a cached live popup replay."""
from collections import Counter
import pytest
from atlas.adapters.rit_policy_course_reviews import parse, MANIFEST
URL='https://www.rit.edu/study/public-policy-immersion'
TITLE='Public Policy Immersion'

def fixture(code='PUBL-589',amount='(1-4 Credits)'):
    return f'<main><h1>{TITLE}</h1><h2>Curriculum for 2026-2027 for {TITLE}</h2><table class="sc_courselist"><tbody><tr><td><a class="code_bubble">{code}</a></td><td>Synthetic title</td><td>9</td></tr></tbody></table></main><div class="courseblock"><span class="detail-code">{code}</span><span class="detail-title">Synthetic title</span><span class="detail-hours_html">{amount}</span><div class="courseblockextra">Synthetic policy description.</div><span class="detail-contact_hours">Lecture 3</span></div>'

def test_observation_reads_changed_values_without_review_or_credit_inference():
    observed=parse(fixture(),url=URL);c=observed['courses'][0]
    assert c['credits'] is None and c['credit_unit']=='unknown'
    assert c['description']=='Synthetic policy description.' and c['prerequisites'] is None
    assert 'category_review' not in c and 'curriculum_audit' not in observed
    assert observed['requirements']==[]
    changed=parse(fixture('PUBL-301','(2 Credits)').replace('</div><span class="detail-contact_hours">','</div><span class="detail-requisites">Synthetic changed condition</span><span class="detail-contact_hours">'),url=URL)['courses'][0]
    assert changed['credits']==2 and changed['prerequisites']=='Synthetic changed condition'

@pytest.mark.parametrize('before,after',[
    ('2026-2027','2025-2026'),
    ('class="detail-code">PUBL-589','class="detail-code">PUBL-999'),
    ('class="courseblockextra"','class="unsettled"'),
    ('(1-4 Credits)','(4-1 Credits)'),
])
def test_source_identity_version_description_and_range_guards(before,after):
    with pytest.raises(ValueError):parse(fixture().replace(before,after),url=URL)

def test_manual_scope_and_exact_conditions():
    c=MANIFEST['courses'];assert len(c)==12
    assert Counter(v['category'] for v in c.values())=={'human_context':8,'mathematics':1,'other':3}
    assert c['PUBL-589']['credits'] is None and '1–4' in c['PUBL-589']['notes'][0]
    assert c['PUBL-301']['category_review']['status']=='mixed'
    assert c['SOIS-333']['credits']==3 and '3rd year' in c['SOIS-333']['prerequisites']
    assert c['PUBL-301']['prerequisites']==c['PUBL-302']['prerequisites']
    assert c['PUBL-363']['category']=='human_context'
    assert 'same topic may not' in c['PUBL-360']['notes'][0]
