import hashlib
from pathlib import Path
import pytest
from atlas.adapters import ucsd_health_development_reviews as m


def fixture(monkeypatch,code='PH 102',body='Statistics. Prerequisites: preparatory course.'):
    e=dict(next(e for e in m.SPEC['entries']if e['code']==code));e['description_hash']=hashlib.sha256(body.encode()).hexdigest();key=e['source_key'];src=m.SPEC['sources'][key]
    html=f'<h1>{src["heading"]}</h1><h2>Courses</h2><p class="course-disclaimer">For course descriptions not found in the UC San Diego General Catalog 2026–27</p><h3>{e["division"]}</h3><p class="course-name">{e["heading"]}</p><p class="course-descriptions">{body}</p>'
    sources={**m.SPEC['sources'],key:{**src,'chapter_context_sha256':m.chapter_context_hash(html)}}
    monkeypatch.setattr(m,'SPEC',{**m.SPEC,'entries':[e],'sources':sources})
    return html,key


def test_source_actual_statistics_primary_subject(monkeypatch):
    html,key=fixture(monkeypatch);c=m.parse_observations(html,subject=key)['courses'][0]
    assert c['category']=='mathematics' and c['credits']==4
    assert 'category_review'not in c
    assert 'prerequisites' in c


def test_shared_honors_heading_has_individual_amount_and_unknown_topic(monkeypatch):
    html,key=fixture(monkeypatch,'HDS 194C','Three-quarter supervised honors project.')
    c=m.parse_observations(html,subject=key)['courses'][0]
    assert c['code']=='HDS 194C' and c['credits']==4
    assert c['category']=='other'
    assert any('not the12-unit sequence total' in n for n in c['notes'])


@pytest.mark.parametrize('old,new',[('Statistics.','Unrelated.'),('2026–27','2027–28'),('PH 102.','PH 103.')])
def test_changes_withdraw_observations(monkeypatch,old,new):
    html,key=fixture(monkeypatch)
    with pytest.raises(ValueError):m.parse_observations(html.replace(old,new),subject=key)


def test_department_major_grade_scope_and_early_questionnaire():
    by={e['code']:e for e in m.SPEC['entries']}
    assert any('not generalized into an AI-degree' in n for n in by['PH 193']['notes'])
    assert 'senior public health majors only' in by['PH 193']['observed_prerequisites']
    assert any('one academic year' in n for n in by['HDS 191']['notes'])
    assert by['HDS 191']['credits']==6 and by['PH 196BH']['credits']==6
    assert by['HDS 133']['category_review']['status']=='mixed'
    assert by['HDS 193']['category_review']['status']=='unclassified'
    assert 'subtitled' in by['PH 157']['observed_prerequisites']


@pytest.mark.parametrize('subject,count,missing',[('HDS',8,2),('PH',10,0)])
def test_actual_chapter_scope_and_duplicate_guards(subject,count,missing):
    path=Path(m.SPEC['sources'][subject]['cache_path'])
    if not path.exists():pytest.skip('Optional ignored official source absent')
    html=path.read_text();r=m.parse_observations(html,subject=subject)
    assert len(r['courses'])==count and len(r['source_dispositions'])==missing
    assert not {'requirements','curriculum_audit','course_identity_groups'}&r.keys()
    assert all('category_review'not in c for c in r['courses'])
    code='HDS 191'if subject=='HDS'else'PH 193'
    entry=next(e for e in m.SPEC['entries']if e['code']==code)
    with pytest.raises(ValueError,match='division'):
        m.parse_observations(html.replace(entry['heading'],'<h3>Graduate</h3>'+entry['heading']),subject=subject)
