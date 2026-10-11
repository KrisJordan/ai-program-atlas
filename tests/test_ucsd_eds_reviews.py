import hashlib
from pathlib import Path
import pytest
from atlas.adapters import ucsd_eds_reviews as m


def fixture(monkeypatch):
    entry=dict(next(e for e in m.SPEC['entries']if e['code']=='EDS 139'))
    body='Field practice. Corequisites: one approved concurrent course. Prerequisites: department approval.'
    entry['description_hash']=hashlib.sha256(body.encode()).hexdigest()
    monkeypatch.setattr(m,'SPEC',{**m.SPEC,'entries':[entry]})
    return '<h1>Education Studies Program</h1><p class="course-disclaimer">2026–27</p><p class="course-name">'+entry['heading']+'</p><p>'+body+'</p>'


def test_exact_condition_observation_not_a_required_course_inference(monkeypatch):
    result=m.parse_observations(fixture(monkeypatch));c=result['courses'][0]
    assert c['credits']==2 and c['prerequisites']=='department approval.'
    assert 'category_review'not in c and 'requirements'not in result
    assert any('concurrently' in n for n in c['notes'])


def test_body_edition_and_identity_are_guarded(monkeypatch):
    html=fixture(monkeypatch)
    for changed in [html.replace('department approval','no approval'),html+'<p>New condition.</p>',html.replace('2026–27','2027–28'),html.replace('EDS 139.','EDS 139R.')]:
        with pytest.raises(ValueError):m.parse_observations(changed)
    assert m.parse_observations(html+'<h4>Graduate</h4><p>Unrelated condition.</p>')['courses']


def test_actual_catalog_review_preserves_major_restrictions_and_source_anomalies():
    path=Path(m.SPEC['sources']['EDS']['cache_path'])
    if not path.exists():pytest.skip('Optional ignored official EDS chapter')
    r=m.parse_observations(path.read_text());c={c['code']:c for c in r['courses']}
    assert len(c)==31 and r['source_dispositions']==[{'code':'EDS 138','status':'no_current_heading'}]
    assert c['EDS 103']['prerequisites']=='ED25 major and upper-division standing.'
    assert c['EDS 103']['category']=='mathematics'
    assert c['EDS 114']['category']=='applications'
    assert c['EDS 155']['category']=='human_context'
    assert c['EDS 190']['credits']is None
    assert c['EDS 135']['credits']==6 and c['EDS 22']['credits']==2 and c['EDS 139']['credits']==2
    assert 'EDS 140' in c['EDS 141']['prerequisites']
    assert 'placement form' in c['EDS 141']['prerequisites']
    assert any('source-copy anomaly' in n for n in c['EDS 141']['notes'])
    assert any('twelve times' in n for n in c['EDS 139']['notes'])
    assert len(c['EDS 120']['prerequisites'])>300
