import hashlib
from pathlib import Path
import pytest
from atlas.adapters import ucsd_poli_reviews as review


def fixture(monkeypatch,code='POLI 30D',body='Quantitative inquiry. POLI 30 is lecture only and 30D has discussion.'):
    entry=dict(next(e for e in review.SPEC['entries']if e['code']==code))
    entry['description_hash']=hashlib.sha256(body.encode()).hexdigest()
    monkeypatch.setattr(review,'SPEC',{**review.SPEC,'entries':[entry]})
    return '<h1>Political Science</h1><p class="course-disclaimer">General Catalog 2026–27</p>'+f'<p class="course-name">{entry["heading"]}</p><p class="course-descriptions">{body}</p>'


def test_explicit_group_member_keeps_distinct_id_and_no_certification(monkeypatch):
    out=review.parse_observations(fixture(monkeypatch));c=out['courses'][0]
    assert c['code']=='POLI 30D'and c['category']=='other'
    assert c['prerequisites'] is None
    assert not {'requirements','course_identity_groups','curriculum_audit'}&out.keys()
    assert 'category_review'not in c


def test_group_member_removal_or_body_change_withdraws_observation(monkeypatch):
    html=fixture(monkeypatch)
    with pytest.raises(ValueError,match='source changed'):review.parse_observations(html.replace('POLI 30 or 30D.','POLI 30.'))
    with pytest.raises(ValueError,match='source changed'):review.parse_observations(html.replace('Quantitative inquiry','Completely different content'))
    with pytest.raises(ValueError,match='edition changed'):review.parse_observations(html.replace('2026–27','2027–28'))
    with pytest.raises(ValueError,match='Duplicate'):review.parse_observations(html+html)


def test_unwrapped_132_prose_is_observed_but_other_text_is_not(monkeypatch):
    html=fixture(monkeypatch,'POLI 132','Political development and modern China.').replace('<p class="course-descriptions">','').replace('China.</p>','China.')
    assert len(review.parse_observations(html)['courses'])==1
    with pytest.raises(ValueError,match='source changed'):review.parse_observations(html.replace('development','unrelated content'))


def test_missing_exact_identifier_appearing_requires_review(monkeypatch):
    entry=next(e for e in review.SPEC['entries']if e['code']=='POLI 132B')
    monkeypatch.setattr(review,'SPEC',{**review.SPEC,'entries':[entry]})
    html='<h1>Political Science</h1><p class="course-disclaimer">General Catalog 2026–27</p>'
    assert review.parse_observations(html)['source_dispositions']==[dict(code='POLI 132B',status='no_current_heading')]
    with pytest.raises(ValueError,match='identifier appeared'):
        review.parse_observations(html+'<p class="course-name">POLI 132B. New title (4)</p>')


def test_actual_content_rather_than_department_or_intelligence_keyword():
    by={e['code']:e for e in review.SPEC['entries']}
    assert len(by)==116 and sum(e['approved_for_integration']for e in by.values())==113
    assert by['POLI 170A']['category']=='mathematics'
    assert by['POLI 149']['category']=='applications'
    assert by['POLI 143']['category']=='human_context'
    assert by['POLI 104J']['category']=='applications'
    assert by['POLI 5D']['category_review']['status']=='mixed'
    assert set(by['POLI 30']['category_review']['candidate_categories'])=={'mathematics','applications'}
    assert by['POLI 154']['category_review']['status']=='unclassified'
    assert any('Latin American' in n for n in by['POLI 154']['notes'])
    assert any('Same' in n or 'same course' in n for n in by['POLI 124']['notes'])


def test_sequence_credit_and_cross_course_eligibility_not_flattened():
    by={e['code']:e for e in review.SPEC['entries']}
    assert by['POLI 191A']['credits'] is None and '(4-4)'in by['POLI 191A']['heading']
    assert by['POLI 194']['credits']==4
    assert any('graduate standing belongs to 220J' in n for n in by['POLI 120J']['notes'])
    assert any('letter grade' in n for n in by['POLI 28']['notes'])
    assert any('same-quarter corequisite' in n for n in by['POLI 194SD']['notes'])


def test_actual_chapter_replays_all_printed_individual_and_grouped_identifiers():
    path=Path(review.SPEC['sources']['POLI']['cache_path'])
    if not path.exists():pytest.skip('Optional ignored current chapter absent')
    out=review.parse_observations(path.read_text());by={c['code']:c for c in out['courses']}
    assert len(by)==113
    assert {'POLI 5','POLI 5D','POLI 13','POLI 13D','POLI 13R','POLI 27','POLI 28','POLI 30','POLI 30D','POLI 191A'}<=by.keys()
    assert by['POLI 132']['description'] and by['POLI 132']['prerequisites']is None
    assert 'Corequisites: POLI 197SD' in by['POLI 194SD']['prerequisites']
    assert 'for POLI 220J, graduate standing' in by['POLI 120J']['prerequisites']
    assert {d['code']for d in out['source_dispositions']}=={'POLI 132B','POLI 133DD','POLI 134A'}
