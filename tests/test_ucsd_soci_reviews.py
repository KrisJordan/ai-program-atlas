import hashlib
from pathlib import Path
import pytest
from atlas.adapters import ucsd_soci_reviews as review


def fixture(monkeypatch,code='SOCI 102',body='Collects and analyzes social-network data. Prerequisites: SOCI 60 or CSS 2, and upper-division standing.'):
    entry=dict(next(e for e in review.SPEC['entries'] if e['code']==code))
    entry['description_hash']=hashlib.sha256(body.encode()).hexdigest()
    monkeypatch.setattr(review,'SPEC',{**review.SPEC,'entries':[entry]})
    return '<h1>Sociology</h1><p class="course-disclaimer">UC San Diego General Catalog 2026–27</p>'+f'<p class="course-name">{entry["heading"]}</p><p class="course-descriptions">{body}</p>'


def test_actual_preparation_and_no_manual_certification(monkeypatch):
    out=review.parse_observations(fixture(monkeypatch))
    course=out['courses'][0]
    assert course['category']=='applications'
    assert course['prerequisites']=='SOCI 60 or CSS 2, and upper-division standing.'
    assert course['credits']==4 and course['credit_unit']=='quarter_hours'
    assert not {'requirements','course_identity_groups','curriculum_audit'}&out.keys()
    assert 'category_review'not in course


def test_changed_entire_block_withdraws_old_facts(monkeypatch):
    html=fixture(monkeypatch)
    for changed in [html.replace('Collects and analyzes','Never collects'),html.replace('SOCI 60 or CSS 2','SOCI 60 and CSS 2')]:
        with pytest.raises(ValueError,match='source changed'):review.parse_observations(changed)
    with pytest.raises(ValueError,match='edition changed'):review.parse_observations(html.replace('2026–27','2027–28'))
    with pytest.raises(ValueError,match='identity changed'):review.parse_observations(html.replace('<h1>Sociology</h1>','<h1>Other courses</h1>'))
    with pytest.raises(ValueError,match='Duplicate'):review.parse_observations(html+html)


def test_unknown_prerequisite_does_not_become_none_required(monkeypatch):
    out=review.parse_observations(fixture(monkeypatch,body='Collects and analyzes social-network data.'))
    assert out['courses'][0]['prerequisites'] is None


def test_current_technology_title_is_not_transferred_to_older_identity(monkeypatch):
    out=review.parse_observations(fixture(monkeypatch,code='SOCI 171',body='Technology and society. Prerequisites: upper-division standing.'))
    assert out['courses']==[]
    assert out['source_dispositions']==[dict(code='SOCI 171',status='source_title_conflict',observed_name='Technology and Society')]


def test_newly_appearing_old_identifier_requires_manual_review(monkeypatch):
    entry=next(e for e in review.SPEC['entries']if e['code']=='SOCI 144P')
    monkeypatch.setattr(review,'SPEC',{**review.SPEC,'entries':[entry]})
    html='<h1>Sociology</h1><p class="course-disclaimer">General Catalog 2026–27</p>'
    assert review.parse_observations(html)['source_dispositions']==[dict(code='SOCI 144P',status='no_current_heading')]
    with pytest.raises(ValueError,match='identifier appeared'):
        review.parse_observations(html+'<p class="course-name">SOCI 144P. New course (4)</p>')


def test_all_target_dispositions_and_eligibility_are_explicit():
    by={e['code']:e for e in review.SPEC['entries']}
    assert len(by)==87 and sum(e['approved_for_integration']for e in by.values())==83
    assert {e['code']for e in by.values()if e['heading']is None}=={'SOCI 123','SOCI 144P','SOCI 158J'}
    assert {e['code']for e in by.values()if e['category']=='applications'}=={'SOCI 102','SOCI 103M','SOCI 108','SOCI 109'}
    for code in ['SOCI 194','SOCI 196A','SOCI 196B']:
        assert by[code]['category']=='other'and by[code]['category_review']['status']=='unclassified'
    assert any('six-unit internship' in n for n in by['SOCI 194']['notes'])
    assert any('malformed' in n for n in by['SOCI 105']['notes'])
    assert any('does not print' in n for n in by['SOCI 188I']['notes'])
    assert all(any('Global Seminar' in n for n in by[c]['notes'])for c in ['SOCI 138GS','SOCI 189GS','SOCI 190GS'])


def test_actual_chapter_replays_full_bounded_inventory():
    path=Path(review.SPEC['sources']['SOCI']['cache_path'])
    if not path.exists():pytest.skip('Optional ignored official course chapter absent')
    out=review.parse_observations(path.read_text());by={c['code']:c for c in out['courses']}
    assert len(by)==83
    assert by['SOCI 105']['credits']==6
    assert by['SOCI 194']['credits']==4
    assert 'SOCI for SOCI 105' in by['SOCI 105']['prerequisites']
    assert by['SOCI 2']['prerequisites'] is None
    assert 'Global Seminar' in by['SOCI 138GS']['prerequisites']
    assert '196A' in by['SOCI 196B']['prerequisites']
    assert {d['code']for d in out['source_dispositions']}=={'SOCI 123','SOCI 144P','SOCI 158J','SOCI 171'}
