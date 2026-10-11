import copy
import hashlib
from pathlib import Path
import pytest
from atlas.adapters import ucsd_math_remaining_reviews as review


def fixture(monkeypatch, code='MATH 11', body='Statistical methods. Prerequisites: calculus.'):
    spec=copy.deepcopy(review.SPEC); e=next(e for e in spec['entries'] if e['code']==code)
    spec['entries']=[e]; e['description_hash']=hashlib.sha256(body.encode()).hexdigest()
    html=(f'<h1>Mathematics</h1><h2>Courses</h2><p>For course descriptions not found in the UC San Diego General Catalog 2026–27, contact the department.</p>'
          f'<h2>{e["section"]}</h2><p class="course-name">{e["heading"]}</p><p>{body}</p>')
    spec['sources']['MATH']['chapter_context_sha256']=review.chapter_context_hash(html)
    monkeypatch.setattr(review,'SPEC',spec);return html


def test_metadata_only_five_units(monkeypatch):
    out=review.parse_observations(fixture(monkeypatch));c=out['courses'][0]
    assert c['credits']==5 and c['credit_unit']=='quarter_hours'
    assert c['prerequisites']=='calculus.'
    assert 'category_review' not in c and 'requirements' not in out


@pytest.mark.parametrize('transform',[
 lambda s:s.replace('Statistical methods.','Changed content.'),
 lambda s:s.replace('calculus.','permission.'),
 lambda s:s.replace('(5)','(4)'),
 lambda s:s.replace('2026–27','2027–28'),
 lambda s:s.replace('<h1>Mathematics</h1>','<h1>Physics</h1>'),
 lambda s:s+'<p>New entry restriction.</p>',
 lambda s:s+'<input type="password">',
 lambda s:s.replace('<h2>Courses</h2>','<h2>Courses</h2><p>Different substitution policy.</p>'),
 lambda s:s+'<p class="course-name">MATH 11. Duplicate (5)</p>',
])
def test_changes_are_not_silent_recertification(monkeypatch,transform):
    with pytest.raises(ValueError):review.parse_observations(transform(fixture(monkeypatch)))


def test_absent_identifier_appearing_needs_review(monkeypatch):
    spec=copy.deepcopy(review.SPEC);spec['entries']=[next(e for e in spec['entries'] if e['code']=='MATH 15A')]
    html='<h1>Mathematics</h1><h2>Courses</h2><p>For course descriptions not found in the UC San Diego General Catalog 2026–27, contact the department.</p><h2>Lower Division</h2>'
    spec['sources']['MATH']['chapter_context_sha256']=review.chapter_context_hash(html)
    monkeypatch.setattr(review,'SPEC',spec)
    out=review.parse_observations(html)
    assert out['courses']==[] and out['source_dispositions']==[{'code':'MATH 15A','status':'no_current_heading'}]
    with pytest.raises(ValueError,match='Previously unmatched'):
        review.parse_observations(html+'<p class="course-name">MATH 15A. New course (4)</p><p>New content.</p>')


def test_manual_content_scope_and_credit_conditions():
    by={e['code']:e for e in review.SPEC['entries']}
    assert len(by)==35 and sum(e['approved_for_integration'] for e in by.values())==34
    assert by['MATH 181D']['category']=='ai_ml'
    assert all(e['category']=='mathematics' for c,e in by.items() if c not in ['MATH 15A','MATH 181D'])
    assert by['MATH 11']['credits']==5
    assert all(e['credits']==4 for c,e in by.items() if c not in ['MATH 15A','MATH 11'])
    assert any('only two' in n for n in by['MATH 20C']['notes'])
    assert any('concurrent ECON 120A prevents' in n for n in by['MATH 180A']['notes'])
    assert any('explicitly not required' in n for n in by['MATH 182']['notes'])
    assert 'course_identity_groups' not in review.SPEC
    assert all(any('equivalent or higher-level' in n for n in e['notes']) for e in by.values() if e['approved_for_integration'])


def test_exact_ignored_source_replay():
    s=review.SPEC['sources']['MATH'];p=Path(s['cache_path'])
    if not p.exists():pytest.skip('Optional ignored source absent')
    raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==s['source_hash']
    out=review.parse_observations(raw.decode())
    assert len(out['courses'])==34 and len(out['source_dispositions'])==1
    c=next(c for c in out['courses'] if c['code']=='MATH 31AH')
    assert 'grade of A or better in each' in c['prerequisites']
