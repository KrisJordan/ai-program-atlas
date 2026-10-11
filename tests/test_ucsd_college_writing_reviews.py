import copy
import hashlib
from pathlib import Path
import pytest
from atlas.adapters import ucsd_college_writing_reviews as review


def fixture(monkeypatch,code='HUM 1',body='Textual study. Prerequisites: writing requirement.'):
    spec=copy.deepcopy(review.SPEC);e=next(e for e in spec['entries'] if e['code']==code);key=e['source_key']
    e['description_hash']=hashlib.sha256(body.encode()).hexdigest();spec['entries']=[e]
    html=(f'<h1>{spec["sources"][key]["heading"]}</h1><h2>Courses</h2>'
          '<p>For course descriptions not found in the UC San Diego General Catalog 2026–27, contact the department.</p>'
          f'<h2>Lower Division</h2><p class="course-name">{e["heading"]}</p><p>{body}</p>')
    spec['sources'][key]['chapter_context_sha256']=review.chapter_context_hash(html)
    monkeypatch.setattr(review,'SPEC',spec);return html


def test_metadata_credits_without_manual_certificate(monkeypatch):
    out=review.parse_observations(fixture(monkeypatch));c=out['courses'][0]
    assert c['credits']==6 and c['credit_unit']=='quarter_hours'
    assert c['prerequisites']=='writing requirement.' and c['category']=='human_context'
    assert 'category_review' not in c and 'requirements' not in out


@pytest.mark.parametrize('change',[
    lambda s:s.replace('Textual study.','New topic.'),
    lambda s:s.replace('writing requirement.','department approval.'),
    lambda s:s.replace('(6)','(4)'),
    lambda s:s.replace('2026–27','2027–28'),
    lambda s:s.replace('Humanities','Different chapter'),
    lambda s:s+'<p>New enrollment restriction.</p>',
    lambda s:s+'<input type="password">',
    lambda s:s.replace('<h2>Lower Division</h2>','<h2>Lower Division</h2><p>New rule.</p>'),
])
def test_material_changes_require_review(monkeypatch,change):
    with pytest.raises(ValueError):review.parse_observations(change(fixture(monkeypatch)))


def test_changed_title_is_not_automatically_promoted(monkeypatch):
    out=review.parse_observations(fixture(monkeypatch,'HUM 2'))
    assert out['courses']==[]
    assert out['source_dispositions']==[dict(code='HUM 2',status='source_title_conflict',observed_name='Rome and the Medieval World')]


def test_scope_course_conditions_and_taxonomy():
    by={e['code']:e for e in review.SPEC['entries']}
    assert len(by)==21 and sum(e['approved_for_integration'] for e in by.values())==20
    assert by['CAT 90']['credits']==1
    assert all(by[c]['credits']==6 for c in ['HUM 1','HUM 2','DOC 2','DOC 3','CAT 3CE'])
    assert all(by[c]['category_review']['status']=='mixed' for c in ['CAT 3CE','TMC 120'])
    assert all(by[c]['category_review']['status']=='unclassified' for c in ['CAT 90','CAT 124'])
    assert by['MCWP 40C']['category']=='human_context'
    assert any('not every AI student' in n for n in by['MCWP 40C']['notes'])
    assert any('across colleges' in n for n in by['DOC 100D']['notes'])
    assert any('concurrently' in n for n in by['DOC 1']['notes'])
    assert any('recommended' in n for n in by['CAT 125']['notes'])
    assert any('Online' in n for n in by['CAT 125R']['notes'])
    assert any('Boolean wording' in n for n in by['MMW 15']['notes'])
    assert 'course_identity_groups' not in review.SPEC


@pytest.mark.parametrize('key,count,holds',[('HUM',5,1),('CAT',5,0),('DOC',4,0),('AWP',2,0),('TMC',2,0),('MCWP',1,0),('MMW',1,0)])
def test_exact_ignored_source_replay(key,count,holds):
    s=review.SPEC['sources'][key];p=Path(s['cache_path'])
    if not p.exists():pytest.skip('Optional ignored course source absent')
    raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==s['source_hash']
    out=review.parse_observations(raw.decode(),subject=key)
    assert len(out['courses'])==count and len(out['source_dispositions'])==holds
    if key=='DOC':assert 'AWP 3' in next(c for c in out['courses'] if c['code']=='DOC 1')['prerequisites']
    if key=='MCWP':assert out['courses'][0]['prerequisites'] is None
