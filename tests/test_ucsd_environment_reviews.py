import copy
import hashlib
from pathlib import Path

import pytest
from atlas.adapters import ucsd_environment_reviews as review


def fixture(monkeypatch, code='ENVR 144', body='Outdoor leadership. Prerequisites: approval.'):
    spec=copy.deepcopy(review.SPEC)
    entry=next(e for e in spec['entries'] if e['code']==code)
    entry['description_hash']=hashlib.sha256(body.encode()).hexdigest()
    spec['entries']=[entry];key=entry['source_key']
    html=(f'<h1>{spec["sources"][key]["heading"]}</h1><h2>Courses</h2>'
          '<p>For course descriptions not found in the UC San Diego General Catalog 2026–27, contact the department.</p>'
          '<h2>Upper Division</h2>'
          f'<p class="course-name">{entry["heading"]}</p><p class="course-descriptions">{body}</p>')
    spec['sources'][key]['chapter_context_sha256']=review.chapter_context_hash(html)
    monkeypatch.setattr(review,'SPEC',spec)
    return html


def test_exact_metadata_without_review_certification(monkeypatch):
    result=review.parse_observations(fixture(monkeypatch));c=result['courses'][0]
    assert c['credits']==2 and c['credit_unit']=='quarter_hours'
    assert c['prerequisites']=='approval.' and c['category']=='applications'
    assert 'category_review' not in c and 'requirements' not in result
    assert any('noncredit' in n for n in c['notes'])


@pytest.mark.parametrize('transform',[
    lambda s:s.replace('Outdoor leadership.','Changed methods.'),
    lambda s:s.replace('approval.','none.'),
    lambda s:s.replace('(2)','(4)'),
    lambda s:s.replace('2026–27','2027–28'),
    lambda s:s.replace('Environmental Studies','Different chapter'),
    lambda s:s+'<p>New exclusion.</p>',
    lambda s:s+'<input type="password">',
    lambda s:s.replace('<h2>Upper Division</h2>','<h2>Upper Division</h2><p>New admission restriction.</p>'),
])
def test_changed_source_requires_review(monkeypatch,transform):
    with pytest.raises(ValueError):review.parse_observations(transform(fixture(monkeypatch)))


def test_exact_missing_headings_are_not_replaced_by_similar_titles(monkeypatch):
    missing=next(e for e in review.SPEC['entries'] if e['code']=='ESYS 190B')
    html=fixture(monkeypatch,'ESYS 103')
    monkeypatch.setattr(review,'SPEC',{**review.SPEC,'entries':[missing]})
    html+='<p class="course-name">ESYS 187C. Environmental Systems Senior Seminar (4)</p><p>Related course.</p>'
    assert review.parse_observations(html)['source_dispositions']==[{'code':'ESYS 190B','status':'no_current_heading'}]
    with pytest.raises(ValueError):
        review.parse_observations(html+'<p class="course-name">ESYS 190B. Newly present course (4)</p>')


def test_actual_scope_and_conditions():
    by={e['code']:e for e in review.SPEC['entries']}
    assert len(by)==12 and sum(e['approved_for_integration'] for e in by.values())==10
    assert {e['code'] for e in by.values() if not e['approved_for_integration']}=={'ESYS 120','ESYS 190B'}
    assert by['ENVR 144']['credits']==2
    assert by['ENVR 150GS']['category']=='human_context'
    assert any('Global Seminar' in n for n in by['ENVR 150GS']['notes'])
    assert all(by[c]['category_review']['status']=='mixed' for c in ['ENVR 30','ESYS 10'])
    assert by['ESYS 187A']['category_review']['status']=='unclassified'
    assert any('MAE 124' in n for n in by['ESYS 103']['notes'])
    assert any('older climate' in n for n in by['ESYS 103']['notes'])
    hold,=review.SPEC['identity_holds']
    assert hold['code']=='ESD 119' and not hold['approved_for_integration']
    assert hold['related_observation']['code']=='EDS/LIGN 119'
    assert 'course_identity_groups' not in review.SPEC


@pytest.mark.parametrize('subject,count,missing',[('ENVR',6,0),('ESYS',4,2)])
def test_ignored_exact_source_replay(subject,count,missing):
    source=review.SPEC['sources'][subject];p=Path(source['cache_path'])
    if not p.exists():pytest.skip('Optional ignored source absent')
    body=p.read_bytes();assert hashlib.sha256(body).hexdigest()==source['source_hash']
    out=review.parse_observations(body.decode(),subject=subject)
    assert len(out['courses'])==count and len(out['source_dispositions'])==missing
    assert all(c['prerequisites'] is not None for c in out['courses'])
