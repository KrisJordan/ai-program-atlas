import hashlib
import json
from pathlib import Path
import pytest
from atlas.adapters import ucsd_phil_econ_reviews as review


def fixture(monkeypatch,body='Studies institutions. Prerequisites : ECON 1 or ECON 3; department approval required.'):
    entry=dict(next(e for e in review.SPEC['entries'] if e['code']=='ECON 167'))
    entry['description_hash']=hashlib.sha256(body.encode()).hexdigest()
    monkeypatch.setattr(review,'SPEC',{**review.SPEC,'entries':[entry]})
    return '<h1>Economics</h1><p class="course-disclaimer">UC San Diego General Catalog 2026–27</p>'+f'<p class="course-name">{entry["heading"]}</p><p class="course-descriptions">{body}</p>'


def test_observer_keeps_unsolved_preparation_and_no_review_certification(monkeypatch):
    out=review.parse_observations(fixture(monkeypatch),subject='ECON')
    row=out['courses'][0]
    assert row['prerequisites']=='ECON 1 or ECON 3; department approval required.'
    assert row['credits']==4 and row['credit_unit']=='quarter_hours'
    assert not any(k in row for k in ['category_review','curriculum_audit'])
    assert not any(k in out for k in ['requirements','course_identity_groups'])


def test_changed_full_body_and_edition_withdraw_observations(monkeypatch):
    html=fixture(monkeypatch)
    with pytest.raises(ValueError,match='source changed'):
        review.parse_observations(html.replace('approval required','approval optional'),subject='ECON')
    with pytest.raises(ValueError,match='edition changed'):
        review.parse_observations(html.replace('2026–27','2027–28'),subject='ECON')
    with pytest.raises(ValueError,match='Duplicate'):
        review.parse_observations(html+html,subject='ECON')


def test_missing_heading_appearance_requires_new_review(monkeypatch):
    entry=next(e for e in review.SPEC['entries'] if e['code']=='PHIL 28GS')
    monkeypatch.setattr(review,'SPEC',{**review.SPEC,'entries':[entry]})
    html='<h1>Philosophy</h1><p class="course-disclaimer">General Catalog 2026–27</p>'
    assert review.parse_observations(html,subject='PHIL')['source_dispositions']==[dict(code='PHIL 28GS',status='no_current_heading')]
    with pytest.raises(ValueError,match='identifier appeared'):
        review.parse_observations(html+'<p class="course-name">PHIL 28GS. Newly published (4)</p>',subject='PHIL')


def test_title_conflict_does_not_export_current_metadata_to_old_identity(monkeypatch):
    entry=next(e for e in review.SPEC['entries'] if e['code']=='ECON 185')
    body='Current data course. Prerequisites: ECON 120B or MATH 181B.'
    changed={**entry,'description_hash':hashlib.sha256(body.encode()).hexdigest()}
    monkeypatch.setattr(review,'SPEC',{**review.SPEC,'entries':[changed]})
    html='<h1>Economics</h1><p class="course-disclaimer">General Catalog 2026–27</p>'+f'<p class="course-name">{entry["heading"]}</p><p class="course-descriptions">{body}</p>'
    out=review.parse_observations(html,subject='ECON')
    assert out['courses']==[] and out['source_dispositions'][0]['status']=='source_title_conflict'


def test_manifest_retains_restrictions_and_manual_content_judgments():
    by={e['code']:e for e in review.SPEC['entries']}
    assert len(by)==68 and sum(e['approved_for_integration'] for e in by.values())==65
    assert by['PHIL 12']['category']=='mathematics'
    assert by['PHIL 123']['category']==by['PHIL 124']['category']=='human_context'
    assert any('philosophy majors' in n and 'letter grade' in n for n in by['PHIL 115']['notes'])
    assert any('Warren College' in n for n in by['PHIL 27']['notes'])
    assert any('prohibits credit for both' in n for n in by['ECON 135']['notes'])
    assert any('MA33' in n and 'approval' in n for n in by['ECON 137']['notes'])
    assert any('two repeat-count formulations' in n for n in by['PHIL 185']['notes'])
    assert by['ECON 185']['observed_prerequisites']=='ECON 120B or MATH 181B.'


def test_actual_two_chapters_replay_all_approved_occurrences():
    paths={k:Path(v['cache_path']) for k,v in review.SPEC['sources'].items()}
    if not all(p.exists() for p in paths.values()):pytest.skip('Optional ignored official course chapters absent')
    results=[review.parse_observations(p.read_text(),subject=k) for k,p in paths.items()]
    rows=[c for r in results for c in r['courses']];by={c['code']:c for c in rows}
    assert len(rows)==65
    assert by['PHIL 35']['prerequisites'] is None
    assert by['ECON 165T']['credits']==2 and 'concurrently' in by['ECON 165T']['prerequisites']
    assert 'Enrollment limited' in by['ECON 137']['prerequisites']
    assert by['ECON 167']['prerequisites']=='ECON 1 and 3.'
    assert {x['code'] for r in results for x in r['source_dispositions']}=={'ECON 163','ECON 185','PHIL 28GS'}
