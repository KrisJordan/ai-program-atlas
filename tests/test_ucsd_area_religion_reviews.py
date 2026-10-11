from pathlib import Path
import hashlib
import pytest
from atlas.adapters import ucsd_area_religion_reviews as m


def fixture(monkeypatch,code='AAS 170',body='History of science and society.'):
    e=dict(next(e for e in m.SPEC['entries']if e['code']==code));e['description_hash']=hashlib.sha256(body.encode()).hexdigest();monkeypatch.setattr(m,'SPEC',{**m.SPEC,'entries':[e]});subject=code.split()[0]
    return '<h1>'+m.SPEC['sources'][subject]['heading']+'</h1><p class="course-disclaimer">2026–27</p><h2>'+e['section']+'</h2><p class="course-name">'+e['heading']+'</p><p class="course-descriptions">'+body+'</p>'


@pytest.mark.parametrize('code',['AAS 170','AAS 170R','AAS 185'])
def test_literal_shared_heading_supplies_target_without_alias_merge(monkeypatch,code):
    result=m.parse_observations(fixture(monkeypatch,code),subject='AAS')
    assert [c['code']for c in result['courses']]==[code]
    assert 'category_review'not in result['courses'][0]
    assert 'course_identity_groups'not in result


@pytest.mark.parametrize('before,after',[('2026–27','2027–28'),('History of science','New scientific methods'),('AAS 170/R.','AAS 170.')])
def test_edition_full_content_and_group_heading_changes_require_review(monkeypatch,before,after):
    with pytest.raises(ValueError):m.parse_observations(fixture(monkeypatch).replace(before,after),subject='AAS')


def test_course_movement_is_not_silently_bound_to_another_section(monkeypatch):
    html=fixture(monkeypatch).replace('<p class="course-name">','<h2>Graduate</h2><p class="course-name">')
    with pytest.raises(ValueError,match='section changed'):m.parse_observations(html,subject='AAS')


def test_real_chapters_replay_exact_bounded_inventory():
    rows=[];missing=[]
    for subject,source in m.SPEC['sources'].items():
        p=Path(source['cache_path'])
        if not p.exists():pytest.skip('Optional ignored chapter capture absent')
        out=m.parse_observations(p.read_text(),subject=subject);rows+=out['courses'];missing+=out['source_dispositions']
    assert len(rows)==42 and len(missing)==4
    assert {d['code']for d in missing}=={'LATI 87','LATI 191','RELI 100','RELI 110B'}
    assert sum(c['credits']is None for c in rows)==5
    assert sum(c['category']=='other'for c in rows)==12
    assert sum(c['category']=='human_context'for c in rows)==29
    assert next(c for c in rows if c['code']=='JWSP 196B')['prerequisites'].startswith('admission to Jewish Studies Honors Program; previous enrollment')


def test_precise_grade_approval_repeat_and_credit_exclusion_notes():
    e={c['code']:c for c in m.SPEC['entries']}
    assert 'overall 3.3 GPA; 3.5 in Jewish studies' in e['JWSP 196A']['observed_prerequisites']
    assert 'ninety units' in e['AAS 198']['observed_prerequisites']
    assert any('P/NP' in n and 'four units' in n for n in e['AAS 198']['notes'])
    assert any('no credit for both' in n.lower()for n in e['RELI 147']['notes'])
    assert e['AAS 191']['category']=='human_context' # social impacts of science, not biological methods
    assert e['LATI 150']['category']=='human_context' # oral-history practice, not inferred programming
    assert e['AAS 171']['category']=='applications'
