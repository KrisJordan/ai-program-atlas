import copy
import hashlib
from pathlib import Path
import pytest
from atlas.adapters import ucsd_linguistics_remaining_reviews as review


def fixture(monkeypatch,code='LIHL 116F',body='Language practice. Prerequisites: instructor approval.'):
    spec=copy.deepcopy(review.SPEC);e=next(e for e in spec['entries'] if e['code']==code);spec['entries']=[e]
    e['description_hash']=hashlib.sha256(body.encode()).hexdigest()
    html=(f'<h1>Linguistics</h1><h2>Courses</h2><p>For course descriptions not found in the UC San Diego General Catalog 2026–27, contact the department.</p>'
          f'<h3>{e["section"]}</h3><p class="course-name">{e["heading"]}</p><p>{body}</p>')
    spec['sources']['LING']['chapter_context_sha256']=review.chapter_context_hash(html)
    monkeypatch.setattr(review,'SPEC',spec);return html


def test_expanded_identifier_and_metadata_only(monkeypatch):
    out=review.parse_observations(fixture(monkeypatch));c=out['courses'][0]
    assert c['code']=='LIHL 116F' and c['credits']==4 and c['category']=='human_context'
    assert c['prerequisites']=='instructor approval.'
    assert 'category_review' not in c and 'requirements' not in out


@pytest.mark.parametrize('change',[
 lambda s:s.replace('Language practice.','Different course.'),
 lambda s:s.replace('instructor approval.','upper-division standing.'),
 lambda s:s.replace('(4)','(6)'),
 lambda s:s.replace('2026–27','2027–28'),
 lambda s:s.replace('<h1>Linguistics</h1>','<h1>History</h1>'),
 lambda s:s+'<input type="password">',
 lambda s:s+'<p>Additional proficiency rule.</p>',
 lambda s:s.replace('<h2>Courses</h2>','<h2>Courses</h2><p>New placement condition.</p>'),
 lambda s:s.replace('116F.','116W.'),
])
def test_changed_content_requires_review(monkeypatch,change):
    with pytest.raises(ValueError):review.parse_observations(change(fixture(monkeypatch)))


def test_unknown_credit_and_unlabeled_prerequisite_spacing(monkeypatch):
    out=review.parse_observations(fixture(monkeypatch,'LIGN 9GS','Signing. Prerequisites : admission to Global Seminars.'))
    c=out['courses'][0]
    assert c['credits'] is None and c['prerequisites']=='admission to Global Seminars.'


def test_full_review_scope_and_conditional_language_rules():
    by={e['code']:e for e in review.SPEC['entries']}
    assert len(by)==50 and all(e['approved_for_integration'] for e in by.values())
    assert {c for c,e in by.items() if e['category']=='ai_ml'}=={'LIGN 6','LIGN 165','LIGN 167'}
    assert sum(e['category']=='human_context' for e in by.values())==47
    assert by['LIGN 9GS']['credits'] is None
    assert by['LIGN 6']['observed_prerequisites'] is None
    assert all(e['credits']==4 for c,e in by.items() if c!='LIGN 9GS')
    assert any('1EX' in n for n in by['LISL 1E']['notes'])
    assert any('LIHL 112' in n for n in by['LIHL 112W']['notes'])
    assert 'media and arts' in by['LIHL 116W']['description']
    assert 'entertainment and culture' in by['LIHL 116P']['description']
    assert 'domestic culture' in by['LIHL 124W']['description']
    assert 'course_identity_groups' not in review.SPEC


def test_exact_ignored_source_replay():
    s=review.SPEC['sources']['LING'];p=Path(s['cache_path'])
    if not p.exists():pytest.skip('Optional ignored source absent')
    raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==s['source_hash']
    out=review.parse_observations(raw.decode())
    assert len(out['courses'])==50 and not out['source_dispositions']
    assert 'ability to program' in next(c for c in out['courses'] if c['code']=='LIGN 167')['prerequisites']
