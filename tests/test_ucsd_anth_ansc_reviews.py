import hashlib
from pathlib import Path
import pytest
from atlas.adapters import ucsd_anth_ansc_reviews as review


def fixture(monkeypatch,code='ANTH 196B',body='Independent thesis. Prerequisites: completion of ANTH 196A with grade of B+ or better.'):
    entry=dict(next(e for e in review.SPEC['entries']if e['code']==code))
    entry['description_hash']=hashlib.sha256(body.encode()).hexdigest()
    monkeypatch.setattr(review,'SPEC',{**review.SPEC,'entries':[entry]})
    return '<h1>Anthropology</h1><p class="course-disclaimer">General Catalog 2026–27</p>'+f'<p class="course-name">{entry["heading"]}</p><p class="course-descriptions">{body}</p>'


def test_combined_observer_keeps_grade_without_certifying_manual_review(monkeypatch):
    out=review.parse_observations(fixture(monkeypatch));c=out['courses'][0]
    assert c['code']=='ANTH 196B' and c['prerequisites']=='completion of ANTH 196A with grade of B+ or better.'
    assert c['category']=='other'
    assert not {'curriculum_audit','requirements','course_identity_groups'}&out.keys()
    assert 'category_review'not in c


def test_full_description_or_grade_changes_withdraw_old_observation(monkeypatch):
    html=fixture(monkeypatch)
    for changed in [html.replace('B+','C'),html.replace('Independent thesis','Laboratory course')]:
        with pytest.raises(ValueError,match='source changed'):review.parse_observations(changed)
    with pytest.raises(ValueError,match='edition changed'):review.parse_observations(html.replace('2026–27','2027–28'))
    with pytest.raises(ValueError,match='Duplicate'):review.parse_observations(html+html)


def test_regional_title_discrepancy_remains_disposition(monkeypatch):
    out=review.parse_observations(fixture(monkeypatch,'ANSC 190GS','Medical anthropology in South Asia. Prerequisites: department approval.'))
    assert out['courses']==[]
    assert out['source_dispositions']==[dict(code='ANSC 190GS',status='source_title_conflict',observed_name='Medicine and Healing in South Asia')]


def test_formerly_missing_identifier_appearance_requires_review(monkeypatch):
    entry=next(e for e in review.SPEC['entries']if e['code']=='ANTH 44')
    monkeypatch.setattr(review,'SPEC',{**review.SPEC,'entries':[entry]})
    html='<h1>Anthropology</h1><p class="course-disclaimer">General Catalog 2026–27</p>'
    assert review.parse_observations(html)['source_dispositions']==[dict(code='ANTH 44',status='no_current_heading')]
    with pytest.raises(ValueError,match='identifier appeared'):
        review.parse_observations(html+'<p class="course-name">ANTH 44. New content (4)</p>')


def test_bounded_manual_content_and_scoping():
    by={e['code']:e for e in review.SPEC['entries']}
    assert len(by)==75 and sum(e['approved_for_integration']for e in by.values())==72
    assert {c for c,e in by.items()if e['heading']is None}=={'ANTH 44','ANSC 116'}
    assert by['ANSC 138']['category']==by['ANSC 171']['category']=='applications'
    assert by['ANTH 43']['category_review']['status']=='mixed'
    assert by['ANTH 128A']['credits']==6 and by['ANTH 128A']['category_review']['status']=='mixed'
    assert by['ANSC 100']['category_review']['status']=='unclassified'
    assert any('fifteen students' in n for n in by['ANSC 169']['notes'])
    assert any('not an additional mandatory prerequisite' in n for n in by['ANSC 137']['notes'])
    assert any('not establish equivalent identities' in n for n in by['ANSC 139']['notes'])
    assert any('renumbered' in n and 'only one' in n for n in by['ANSC 180']['notes'])
    assert by['ANSC 152']['id']!=by['ANSC 189']['id']


def test_actual_chapter_replays_both_prefixes_without_other_anthropology_subjects():
    path=Path(review.SPEC['sources']['ANTH']['cache_path'])
    if not path.exists():pytest.skip('Optional ignored current chapter absent')
    out=review.parse_observations(path.read_text());by={c['code']:c for c in out['courses']}
    assert len(by)==72 and {c.split()[0]for c in by}=={'ANTH','ANSC'}
    assert by['ANTH 1']['prerequisites'] is None
    assert 'B+ or better' in by['ANTH 196B']['prerequisites']
    assert 'apply' in by['ANSC 106S']['prerequisites']
    assert by['ANTH 128A']['credits']==6
    assert {d['code']for d in out['source_dispositions']}=={'ANTH 44','ANSC 116','ANSC 190GS'}
    separate=[review.parse_observations(path.read_text(),subject=s)for s in ['ANTH','ANSC']]
    assert sum(len(x['courses'])for x in separate)==len(by)
