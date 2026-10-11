from collections import Counter
import hashlib
from pathlib import Path
import pytest
from atlas.adapters import ucsd_codeonly_social_reviews as m


def synthetic(monkeypatch, code, body='Studies social institutions. Prerequisites: instructor consent.'):
    entry=dict(next(e for e in m.SPEC['entries'] if e['code']==code))
    entry['description_hash']=hashlib.sha256(body.encode()).hexdigest()
    monkeypatch.setattr(m,'SPEC',{**m.SPEC,'entries':[entry]})
    subject=code.split()[0];source=m.SPEC['sources'][subject]
    header='<h1>'+source['heading']+'</h1><p class="course-disclaimer">2026–27</p>'
    policy=m.SPEC['section_policies'].get(subject)
    section='<h2>'+entry['region']+'</h2>'
    if policy and entry['region']=='Upper Division':section+='<p>'+policy['text']+'</p>'
    if entry['section']!=entry['region']:section+='<h3>'+entry['section']+'</h3>'
    tail=''
    if policy and entry['region']!='Upper Division':tail='<h2>Upper Division</h2><p>'+policy['text']+'</p>'
    return header+section+'<p class="course-name">'+entry['heading']+'</p><p class="course-descriptions">'+body+'</p>'+tail


@pytest.mark.parametrize('code',['ETHN 103A','POLI 10','POLI 10D','PHIL 10'])
def test_literal_shared_or_individual_heading_emits_only_assigned_metadata(monkeypatch,code):
    out=m.parse_observations(synthetic(monkeypatch,code),subject=code.split()[0])
    assert [c['code'] for c in out['courses']]==[code]
    assert 'category_review' not in out['courses'][0]
    assert 'requirements' not in out and 'course_identity_groups' not in out


@pytest.mark.parametrize('before,after',[('2026–27','2027–28'),('Studies social institutions.','Studies software implementation.'),('instructor consent.','instructor consent. Enrollment limited to graduate students.')])
def test_entire_description_and_eligibility_suffix_require_review(monkeypatch,before,after):
    html=synthetic(monkeypatch,'PHIL 10')
    with pytest.raises(ValueError):m.parse_observations(html.replace(before,after),subject='PHIL')


def test_changed_shared_heading_does_not_reuse_a_missing_code(monkeypatch):
    html=synthetic(monkeypatch,'POLI 10D').replace('10 or 10R or 10D or 10DR.','10 or 10R or 10DR.')
    with pytest.raises(ValueError,match='course block'):m.parse_observations(html,subject='POLI')


@pytest.mark.parametrize('code',['POLI 142A','ETHN 103A'])
def test_chapter_preparation_change_or_course_move_withdraws_observation(monkeypatch,code):
    html=synthetic(monkeypatch,code);subject=code.split()[0]
    with pytest.raises(ValueError,match='preparation policy'):
        m.parse_observations(html.replace('standing','graduate standing',1),subject=subject)
    moved=html.replace('<p class="course-name">','<h2>Lower Division</h2><h3>'+next(e for e in m.SPEC['entries']if e['code']==code)['section']+'</h3><p class="course-name">')
    with pytest.raises(ValueError,match='section membership'):m.parse_observations(moved,subject=subject)


def test_current_seven_chapters_replay_all_exact_targets():
    rows=[];gaps=[]
    for subject,source in m.SPEC['sources'].items():
        path=Path(source['cache_path'])
        if not path.exists():pytest.skip('Optional ignored source capture absent')
        out=m.parse_observations(path.read_text(),subject=subject);rows+=out['courses'];gaps+=out['source_dispositions']
    assert len(rows)==79 and len(gaps)==6
    assert {d['code']for d in gaps}=={'ETHN 149','ETHN 153','ETHN 163J','ECON 123','POLI 102H','COMM 109E'}
    assert Counter(c['category']for c in rows)=={'human_context':69,'mathematics':4,'applications':5,'other':1}
    assert Counter(c['credits']for c in rows)=={4:78,6:1}
    by={c['code']:c for c in rows}
    assert by['CGS 2B']['prerequisites'] is None
    assert 'Course-specific prerequisites: POLI 12 or consent of instructor.' in by['POLI 142A']['prerequisites']
    assert 'quarter of lower-division political science' in by['POLI 100A']['prerequisites']
    assert by['ETHN 120D']['prerequisites'].endswith('upper-division standing or consent of instructor.')
    assert by['COMM 101']['prerequisites']=='COMM 10.'


def test_specific_manual_distinctions_and_published_exclusions():
    entries={e['code']:e for e in m.SPEC['entries']}
    assert entries['PHIL 10']['category']=='mathematics'
    assert entries['PHIL 150']['category']=='human_context' # philosophy, not AI method instruction
    assert entries['ECON 172A']['category']=='mathematics'
    assert entries['SOCI 60']['category']=='applications' # actual social-research design
    assert entries['COMM 101']['credits']==6 and entries['COMM 101']['category']=='applications'
    assert entries['COMM 80']['category']=='human_context' # communication practice
    assert entries['ECON 5']['category_review']['status']=='mixed'
    assert any('after ECE 109' in n for n in entries['ECON 120A']['notes'])
    assert any('ETHN 1C' in n for n in entries['ETHN 3']['notes'])
    assert any('strongly recommended' in n for n in entries['ETHN 120D']['notes'])
    assert entries['POLI 10']['id']!=entries['POLI 10D']['id']


def test_newly_available_previously_missing_identifier_requires_review(monkeypatch):
    absent=dict(next(e for e in m.SPEC['entries'] if e['code']=='COMM 109E'))
    monkeypatch.setattr(m,'SPEC',{**m.SPEC,'entries':[absent]})
    html='<h1>Communication</h1><p class="course-disclaimer">2026–27</p><h2>Upper Division</h2><p class="course-name">COMM 109E. Newly Listed Subject (4)</p><p class="course-descriptions">New evidence.</p>'
    with pytest.raises(ValueError,match='Previously missing'):m.parse_observations(html,subject='COMM')


def test_duplicate_assigned_heading_requires_review(monkeypatch):
    html=synthetic(monkeypatch,'PHIL 10')
    html+='<p class="course-name">PHIL 10. Second Conflicting Listing (4)</p><p class="course-descriptions">Different scope.</p>'
    with pytest.raises(ValueError,match='Duplicate'):m.parse_observations(html,subject='PHIL')
