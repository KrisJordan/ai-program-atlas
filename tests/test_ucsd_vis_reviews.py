import hashlib
from pathlib import Path
import pytest
from atlas.adapters import ucsd_vis_reviews as review


def fixture(monkeypatch,code='VIS 42',body='Teaches programming and computational thinking through creative projects. Prerequisites: none.'):
    entry=dict(next(e for e in review.SPEC['entries']if e['code']==code))
    entry['description_hash']=hashlib.sha256(body.encode()).hexdigest()
    monkeypatch.setattr(review,'SPEC',{**review.SPEC,'entries':[entry]})
    return '<h1>Visual Arts</h1><p class="course-disclaimer">General Catalog 2026–27</p>'+f'<p class="course-name">{entry["heading"]}</p><p class="course-descriptions">{body}</p>'


def test_actual_programming_content_without_manual_certification(monkeypatch):
    out=review.parse_observations(fixture(monkeypatch));c=out['courses'][0]
    assert c['category']=='foundations'and c['prerequisites']=='none.'
    assert not {'requirements','course_identity_groups','curriculum_audit'}&out.keys()
    assert 'category_review'not in c


def test_practice_and_critical_content_are_not_inferred_from_arts_prefix():
    by={e['code']:e for e in review.SPEC['entries']}
    assert by['VIS 42']['category']=='foundations'
    assert by['VIS 6']['category']=='human_context'
    assert by['VIS 181']['category']=='applications'
    assert by['VIS 157']['category_review']['status']=='mixed'
    assert by['VIS 160A']['category_review']['status']==by['VIS 160B']['category_review']['status']=='unclassified'


def test_changed_whole_body_edition_and_duplicate_withdraw_observation(monkeypatch):
    html=fixture(monkeypatch)
    with pytest.raises(ValueError,match='source changed'):review.parse_observations(html.replace('programming','only painting'))
    with pytest.raises(ValueError,match='source changed'):review.parse_observations(html.replace('Prerequisites: none.','Prerequisites: permission.'))
    with pytest.raises(ValueError,match='edition changed'):review.parse_observations(html.replace('2026–27','2027–28'))
    with pytest.raises(ValueError,match='Duplicate'):review.parse_observations(html+html)


def test_historical_seminar_label_does_not_inherit_current_different_field(monkeypatch):
    out=review.parse_observations(fixture(monkeypatch,'VIS 129A','Advanced ancient art. Prerequisites: VIS 112 or two art history courses.'))
    assert out['courses']==[]
    assert out['source_dispositions']==[dict(code='VIS 129A',status='source_title_conflict',observed_name='Seminar in Premodern Art History')]


def test_missing_heading_appearance_requires_manual_review(monkeypatch):
    entry=next(e for e in review.SPEC['entries']if e['code']=='VIS 126D')
    monkeypatch.setattr(review,'SPEC',{**review.SPEC,'entries':[entry]})
    html='<h1>Visual Arts</h1><p class="course-disclaimer">General Catalog 2026–27</p>'
    assert review.parse_observations(html)['source_dispositions']==[dict(code='VIS 126D',status='no_current_heading')]
    with pytest.raises(ValueError,match='identifier appeared'):
        review.parse_observations(html+'<p class="course-name">VIS 126D. A newly listed course (4)</p>')


def test_all_target_dispositions_and_policy_limits():
    by={e['code']:e for e in review.SPEC['entries']}
    assert len(by)==87 and sum(e['approved_for_integration']for e in by.values())==67
    assert sum(e['heading']is None for e in by.values())==13
    assert {c for c,e in by.items()if e['disposition']=='source_title_conflict'}=={'VIS 129A','VIS 129B','VIS 129C','VIS 129D','VIS 129E','VIS 152','VIS 155'}
    assert by['VIS 190']['credits']==8
    assert any('Latin American' in n for n in by['VIS 152']['notes'])
    assert any('not an automatic replacement' in n for n in by['VIS 126I']['notes'])
    assert any('two production' in n.lower() for n in by['VIS 110F']['notes'])


def test_actual_chapter_replays_approved_metadata_and_exact_major_limits():
    path=Path(review.SPEC['sources']['VIS']['cache_path'])
    if not path.exists():pytest.skip('Optional ignored current chapter absent')
    out=review.parse_observations(path.read_text());by={c['code']:c for c in out['courses']}
    assert len(by)==67 and len(out['source_dispositions'])==20
    assert by['VIS 190']['credits']==8
    assert by['VIS 120A']['prerequisites']=='none.'
    assert any('Recommended preparation: VIS 20' in n for n in by['VIS 120A']['notes'])
    assert 'ICAM majors only' in by['VIS 160A']['prerequisites']
    assert 'Department stamp required' in by['VIS 160A']['prerequisites']
    assert by['VIS 103B']['prerequisites']=='upper-division standing.'
