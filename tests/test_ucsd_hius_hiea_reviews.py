import hashlib
from pathlib import Path
import pytest
from atlas.adapters import ucsd_hius_hiea_reviews as review


def fixture(monkeypatch,code='HIEA 122',body='Late imperial society. Prerequisites: upper-division; department approval. +'):
    entry=dict(next(e for e in review.SPEC['entries']if e['code']==code))
    entry['description_hash']=hashlib.sha256(body.encode()).hexdigest()
    monkeypatch.setattr(review,'SPEC',{**review.SPEC,'entries':[entry]})
    return ('<h1>History</h1><p class="course-disclaimer">General Catalog 2026–27</p>'
            '<p class="course-subhead-1">+ indicates courses that focus on the period before 1800.</p>'
            f'<p class="course-name">{entry["heading"]}</p><p class="course-descriptions">{body}</p>')


def test_combined_observer_keeps_exact_preparation_and_no_certification(monkeypatch):
    out=review.parse_observations(fixture(monkeypatch));c=out['courses'][0]
    assert c['code']=='HIEA 122' and c['credits']==4
    assert c['prerequisites']=='upper-division; department approval. +'
    assert any('not required' in n for n in c['notes'])
    assert not {'requirements','curriculum_audit','course_identity_groups'}&out.keys()
    assert 'category_review'not in c


@pytest.mark.parametrize('before,after',[('department approval','no approval'),('HIEA 122.','HIEA 122S.'),('2026–27','2027–28'),('before 1800','after 1800')])
def test_any_body_identity_edition_or_marker_change_requires_review(monkeypatch,before,after):
    with pytest.raises(ValueError):review.parse_observations(fixture(monkeypatch).replace(before,after))


def test_same_code_different_history_course_remains_a_hold(monkeypatch):
    out=review.parse_observations(fixture(monkeypatch,'HIUS 120','Peace movements and opposition to wars.'))
    assert out['courses']==[]
    assert out['source_dispositions']==[dict(code='HIUS 120',status='source_title_conflict',observed_name='Peace Movements in America')]


def test_missing_department_code_is_not_repaired_from_another_department(monkeypatch):
    entry=next(e for e in review.SPEC['entries']if e['code']=='HIEA 149')
    html=fixture(monkeypatch).split('<p class="course-name">')[0]
    monkeypatch.setattr(review,'SPEC',{**review.SPEC,'entries':[entry]})
    html+='<p class="course-name">HIEU 149. Land of Three Faiths (4)</p>'
    assert review.parse_observations(html)['source_dispositions']==[dict(code='HIEA 149',status='no_current_heading')]
    with pytest.raises(ValueError,match='identifier appeared'):
        review.parse_observations(html.replace('HIEU 149','HIEA 149'))


def test_body_conditions_recommendations_and_coscheduling_remain_distinct():
    by={e['code']:e for e in review.SPEC['entries']}
    assert len(by)==89 and sum(e['approved_for_integration']for e in by.values())==81
    assert sum(e['heading']is None for e in by.values())==7
    assert by['HIEA 170']['observed_prerequisites']is None
    assert any('Department approval' in n for n in by['HIEA 170']['notes'])
    assert any('coscheduled' in n and 'equal workload' in n for n in by['HIEA 170']['notes'])
    assert any('Global Seminars' in n for n in by['HIEA 139GS']['notes'])
    assert by['HIEA 150']['observed_prerequisites']is None
    assert any('recommended' in n for n in by['HIEA 150']['notes'])
    assert any('1949–1976' in n and 'present' in n for n in by['HIEA 132']['notes'])
    for code in ['HIEA 144','HIEA 144P','HIEA 180','HIEA 199']:
        assert by[code]['category_review']['status']=='unclassified'
    assert any('135A or 135B' in n for n in by['HIUS 135']['notes'])


def test_actual_shared_chapter_composes_both_subjects_without_hieu_replay():
    path=Path(review.SPEC['sources']['HIUS']['cache_path'])
    if not path.exists():pytest.skip('Optional ignored current History chapter absent')
    html=path.read_text();out=review.SOURCE_PARSERS['https://catalog.ucsd.edu/courses/HIST.html'](html)
    assert len(out['courses'])==81 and len(out['source_dispositions'])==8
    assert all(c['credits']==4 and c['credit_unit']=='quarter_hours'for c in out['courses'])
    assert {c['code'].split()[0]for c in out['courses']}=={'HIUS','HIEA'}
    assert len(review.parse_observations(html,subject='HIUS')['courses'])==42
    assert len(review.parse_observations(html,subject='HIEA')['courses'])==39
    with pytest.raises(ValueError):review.parse_observations(html+html)


def test_joint_heading_and_section_eligibility_are_both_guarded(monkeypatch):
    entry=next(e for e in review.SPEC['entries'] if e['code']=='HIEA 163')
    body='Cinema and society. Prerequisites: upper-division or graduate standing and department stamp.'
    html=fixture(monkeypatch,'HIEA 163',body)
    prefix='<h3>EAST ASIA</h3><h4>Colloquia</h4><p>'+review.SPEC['section_conditions']['EAST ASIA']+'</p>'
    html=html.replace('<p class="course-name">',prefix+'<p class="course-name">')
    html+='<h4>Another section</h4><p class="course-descriptions">Unrelated prose must not leak.</p>'
    courses=review.parse_observations(html)['courses']
    assert [c['code'] for c in courses]==['HIEA 163']
    assert 'graduate standing' in courses[0]['prerequisites']
    assert any('EASY' in n for n in courses[0]['notes'])
    with pytest.raises(ValueError,match='eligibility'):
        review.parse_observations(html.replace('consent of the instructor','no consent'))
    with pytest.raises(ValueError,match='source changed'):
        review.parse_observations(html.replace('HIEA 163/263.','HIEA 163/264.'))


def test_joint_undergraduate_courses_keep_credit_and_workload_limits():
    by={e['code']:e for e in review.SPEC['entries']}
    assert by['HIUS 120D']['category_review']['status']=='mixed'
    assert any('strongly recommended' in n for n in by['HIUS 120D']['notes'])
    assert any('additional paper' in n for n in by['HIEA 163']['notes'])
    assert by['HIEA 190M']['category_review']['status']=='unclassified'
    assert by['HIEA 190M']['observed_prerequisites'] is None
    assert any('Department approval' in n for n in by['HIEA 190M']['notes'])
