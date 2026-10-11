import hashlib
from pathlib import Path
import pytest
from atlas.adapters import ucsd_hieu_reviews as review


def fixture(monkeypatch, code='HIEU 198', body='Supervised study. Prerequisites: upper-division standing and department stamp.'):
    entry=dict(next(e for e in review.SPEC['entries'] if e['code']==code))
    entry['description_hash']=hashlib.sha256(body.encode()).hexdigest()
    monkeypatch.setattr(review,'SPEC',{**review.SPEC,'entries':[entry],'supplementary_blocks':[], 'colloquium_policy':None})
    return ('<h1>History</h1><p class="course-disclaimer">General Catalog 2026–27</p>'
            '<p class="course-subhead-1">+ indicates courses that focus on the period before 1800.</p>'
            f'<p class="course-name">{entry["heading"]}</p><p class="course-descriptions">{body}</p>')


def test_variable_study_preserves_exact_eligibility_without_certification(monkeypatch):
    out=review.parse_observations(fixture(monkeypatch));course=out['courses'][0]
    assert course['code']=='HIEU 198' and course['credits'] is None
    assert course['category']=='other'
    assert course['prerequisites']=='upper-division standing and department stamp.'
    assert not {'requirements','curriculum_audit','course_identity_groups'} & out.keys()
    assert 'category_review' not in course


def test_block_edition_marker_and_identity_changes_withdraw_observation(monkeypatch):
    html=fixture(monkeypatch)
    for changed in [html.replace('department stamp','instructor permission'),html.replace('HIEU 198.','HIEU 198S.')]:
        with pytest.raises(ValueError,match='source changed'):review.parse_observations(changed)
    with pytest.raises(ValueError,match='edition changed'):review.parse_observations(html.replace('2026–27','2027–28'))
    with pytest.raises(ValueError,match='marker changed'):review.parse_observations(html.replace('before 1800','after 1800'))
    with pytest.raises(ValueError,match='Duplicate'):review.parse_observations(html+html)


def test_absent_unsuffixed_identifier_is_not_filled_by_suffixed_course(monkeypatch):
    entry=next(e for e in review.SPEC['entries'] if e['code']=='HIEU 105')
    html=fixture(monkeypatch,'HIEU 105S')
    monkeypatch.setattr(review,'SPEC',{**review.SPEC,'entries':[entry]})
    assert review.parse_observations(html)['source_dispositions']==[dict(code='HIEU 105',status='no_current_heading')]
    with pytest.raises(ValueError,match='identifier appeared'):
        review.parse_observations(html+'<p class="course-name">HIEU 105. Newly published (4)</p>')


def test_changed_title_is_disposition_not_code_based_metadata_transfer(monkeypatch):
    out=review.parse_observations(fixture(monkeypatch,'HIEU 122','Greek history through the Persian Wars.'))
    assert not out['courses']
    assert out['source_dispositions']==[dict(code='HIEU 122',status='source_title_conflict',observed_name='Ancient Greece in the Archaic Period')]


def test_supplementary_exclusion_has_its_own_full_block_guard(monkeypatch):
    original=review.SPEC
    html=fixture(monkeypatch,'HIEU 124')
    supplement=original['supplementary_blocks'][0].copy()
    body='Students may not receive credit for both HIEU 124 and HIEU 124GS.'
    supplement['description_hash']=hashlib.sha256(body.encode()).hexdigest()
    monkeypatch.setattr(review,'SPEC',{**review.SPEC,'supplementary_blocks':[supplement]})
    html+=f'<p class="course-name">{supplement["heading"]}</p><p class="course-descriptions">{body}</p>'
    out=review.parse_observations(html)
    assert len(out['courses'])==1 and out['courses'][0]['credits'] is None
    with pytest.raises(ValueError,match='Supplementary'):
        review.parse_observations(html.replace('may not','may'))


def test_manual_dispositions_distinguish_public_history_practice_and_unknown_topics():
    entries={e['code']:e for e in review.SPEC['entries']}
    assert len(entries)==74 and sum(e['approved_for_integration'] for e in entries.values())==72
    assert sum(e['heading'] is None for e in entries.values())==1
    assert entries['HIEU 145']['category_review']['status']=='mixed'
    assert set(entries['HIEU 145']['category_review']['candidate_categories'])=={'human_context','applications'}
    for code in ['144','153','160','198','199']:
        assert entries['HIEU '+code]['category_review']['status']=='unclassified'
    assert entries['HIEU 158']['category']=='human_context'
    assert entries['HIEU 124']['credits'] is None
    assert any('124GS' in note for note in entries['HIEU 124']['notes'])
    assert any('both 116B and 117A' in note for note in entries['HIEU 117A']['notes'])


def test_actual_current_history_chapter_replays_bounded_evidence():
    path=Path(review.SPEC['sources']['HIEU']['cache_path'])
    if not path.exists():pytest.skip('Optional ignored History chapter absent')
    out=review.parse_observations(path.read_text());by={c['code']:c for c in out['courses']}
    assert len(by)==72 and len(out['source_dispositions'])==2
    assert {'HIEU 159','HIEU 159S','HIEU 116B','HIEU 117A'}<=by.keys()
    assert 'minimum UC San Diego GPA of 2.95' in by['HIEU 198']['prerequisites']
    assert 'ninety units' in by['HIEU 198']['prerequisites']
    assert by['HIEU 199']['prerequisites']=='consent of instructor.'
    assert by['HIEU 160']['prerequisites']=='upper-division standing and department approval required. +'
    assert by['HIEU 124']['credits'] is None and by['HIEU 198']['credits'] is None
    assert 'HIEU 124GS' not in by and 'HIEU 122' not in by


def test_shared_heading_and_section_conditions_are_independently_guarded(monkeypatch):
    e=dict(next(e for e in review.SPEC['entries']if e['code']=='HIEU 161'))
    body='Changing historical topics. Prerequisites: advanced standing.'
    policy='Undergraduates need approval. Graduate work differs.'
    e['description_hash']=hashlib.sha256(body.encode()).hexdigest()
    spec={**review.SPEC,'entries':[e],'supplementary_blocks':[],
          'colloquium_policy':{'anchor_code':'HIEU 161','heading':'Colloquia',
            'body_hash':hashlib.sha256(policy.encode()).hexdigest(),'course_codes':['HIEU 161']}}
    monkeypatch.setattr(review,'SPEC',spec)
    html=('<h1>History</h1><p class="course-disclaimer">2026–27</p>'
          '<p class="course-subhead-1">+ indicates courses that focus on the period before 1800.</p>'
          '<h4>Colloquia</h4><p class="course-note">'+policy+'</p>'
          '<p class="course-name">'+e['heading']+'</p><p>'+body+'</p>')
    r=review.parse_observations(html)
    assert [c['code']for c in r['courses']]==['HIEU 161']
    assert 'course_identity_groups'not in r
    assert any('graduate additional-work rules are not undergraduate obligations' in n for n in r['courses'][0]['notes'])
    for changed in [html.replace('Undergraduates need approval','Undergraduates never need approval'),html.replace('<h4>Colloquia</h4>','<h4>Lecture Courses</h4>'),html+'<p>New course condition.</p>']:
        with pytest.raises(ValueError):review.parse_observations(changed)


def test_actual_shared_headings_restore_present_codes_without_graduate_expansion():
    path=Path(review.SPEC['sources']['HIEU']['cache_path'])
    if not path.exists():pytest.skip('Optional History chapter')
    r=review.parse_observations(path.read_text());cs={c['code']:c for c in r['courses']}
    assert len(cs)==72 and len(r['source_dispositions'])==2
    assert all('HIEU '+n in cs for n in ['107','161','162','163','164','166','167','171','172','174','176','178','181','182','183','184'])
    assert not any(int(c.split()[1][:3])>=200 for c in cs)
    assert any('EASY' in n for n in cs['HIEU 164']['notes'])
    assert not any('EASY' in n for n in cs['HIEU 107']['notes'])
    assert any('graduate' in n.lower() and 'not' in n.lower()for n in cs['HIEU 172']['notes'])
    assert len(review.SPEC['colloquium_policy']['course_codes'])==18
