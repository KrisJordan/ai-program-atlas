import hashlib
from pathlib import Path
import pytest
from atlas.adapters import ucsd_hila_reviews as m


def synthetic(monkeypatch):
    entry=dict(next(e for e in m.SPEC['entries'] if e['code']=='HILA 167'))
    body='Historical scholarship. Graduate students write an additional paper. Prerequisites: reading knowledge of Spanish.'
    policy='Undergraduates need department approval or instructor consent.'
    entry['description_hash']=hashlib.sha256(body.encode()).hexdigest()
    monkeypatch.setattr(m,'SPEC',{**m.SPEC,'entries':[entry],'colloquium_policy':{
        'anchor_code':'HILA 167','heading':'Colloquia','body_hash':hashlib.sha256(policy.encode()).hexdigest(),'course_codes':['HILA 167']}})
    return ('<h1>History</h1><p class="course-disclaimer">2026–27</p>'
            '<p class="course-subhead-1">+ indicates courses that focus on the period before 1800.</p>'
            '<h4>Colloquia</h4><p class="course-note">'+policy+'</p>'
            '<p class="course-name">'+entry['heading']+'</p><p>'+body+'</p>')


def test_shared_undergraduate_heading_is_not_a_second_graduate_record(monkeypatch):
    result=m.parse_observations(synthetic(monkeypatch))
    assert [c['code'] for c in result['courses']]==['HILA 167']
    c=result['courses'][0]
    assert c['prerequisites']=='reading knowledge of Spanish.'
    assert 'category_review' not in c and 'requirements' not in result
    assert any('graduate' in n.lower() and 'not' in n.lower() for n in c['notes'])


def test_complete_block_section_scope_and_edition_are_guarded(monkeypatch):
    html=synthetic(monkeypatch)
    for changed in [html+'<p>New enrollment restriction.</p>',html.replace('or instructor consent','only'),html.replace('2026–27','2027–28'),html.replace('<p class="course-name">','<h4>Lecture Courses</h4><p class="course-name">')]:
        with pytest.raises(ValueError):m.parse_observations(changed)
    # A new section is not part of the preceding course body.
    assert m.parse_observations(html+'<h4>Another section</h4><p>Unrelated policy.</p>')['courses']


def test_actual_dispositions_and_colloquium_boundaries():
    s=m.SPEC['sources']['HILA'];path=Path(s['cache_path'])
    if not path.exists():pytest.skip('Optional ignored official History chapter')
    r=m.parse_observations(path.read_text());cs={c['code']:c for c in r['courses']}
    assert len(cs)==34 and {d['code']for d in r['source_dispositions']}=={'HILA 100D','HILA 133S','HILA 163'}
    assert cs['HILA 119']['credits'] is None
    assert sum(c['credits']==4 for c in cs.values())==33
    assert sum(c['category']=='human_context'for c in cs.values())==29
    assert len(m.SPEC['colloquium_policy']['course_codes'])==8
    assert not any('EASY' in n for n in cs['HILA 145']['notes'])
    assert all(any('EASY' in n for n in cs[code]['notes']) for code in m.SPEC['colloquium_policy']['course_codes'])
    assert 'reading knowledge of Spanish' in cs['HILA 167']['prerequisites']
    assert cs['HILA 144']['category']=='other'
    assert cs['HILA 145']['category']=='human_context'
    assert not any(int(code.split()[1][:3])>=200 for code in cs)
