from pathlib import Path
import hashlib
import pytest
from atlas.adapters import ucsd_history_remaining_reviews as m


def fixture(monkeypatch,code='HISA 199',body='Directed reading.'):
    e=dict(next(e for e in m.SPEC['entries']if e['code']==code));e['description_hash']=hashlib.sha256(body.encode()).hexdigest()
    monkeypatch.setattr(m,'SPEC',{**m.SPEC,'entries':[e]})
    intro='<h1>History</h1><p class="course-disclaimer">2026–27</p><p class="course-subhead-1">'+m.SPEC['chapter_marker']+'</p>'
    region=e.get('section_condition_region')
    if region:intro+='<h3>'+region+'</h3><h4>Colloquia</h4><p>'+m.SPEC['section_conditions'][region]+'</p>'
    return intro+'<p class="course-name">'+e['heading']+'</p><p class="course-descriptions">'+body+'</p>'


def test_variable_catalog_credits_do_not_replace_four_credit_pool_condition(monkeypatch):
    c=m.parse_observations(fixture(monkeypatch))['courses'][0]
    assert c['credits']is None and c['credit_unit']=='quarter_hours'
    assert any('pool specifically requires' in n for n in c['notes'])
    assert 'category_review'not in c
    assert c['prerequisites']is None


def test_six_credit_seminar_does_not_add_its_separate_internship(monkeypatch):
    html=fixture(monkeypatch,'HITO 193','Research seminar. Prerequisites: department stamp required; participating in UCDC program.')
    c=m.parse_observations(html)['courses'][0]
    assert c['code']=='HITO 193' and c['credits']==6
    assert 'UCDC' in c['prerequisites']
    assert any('no doubling' in n for n in c['notes'])
    with pytest.raises(ValueError,match='outside reviewed colloquium'):
        m.parse_observations(html.replace('<p class="course-name">','<h4>Lecture Courses</h4><p class="course-name">'))
    with pytest.raises(ValueError,match='eligibility'):
        m.parse_observations(html.replace('consent of the instructor','automatic enrollment'))


@pytest.mark.parametrize('before,after',[('2026–27','2027–28'),('Directed reading.','Different reading.'),('HISA 199.','HISA 198.'),('before 1800','after 1800')])
def test_body_edition_identity_and_period_marker_changes_require_review(monkeypatch,before,after):
    with pytest.raises(ValueError):m.parse_observations(fixture(monkeypatch).replace(before,after))


def test_internal_description_and_external_title_conflicts_are_distinct(monkeypatch):
    out=m.parse_observations(fixture(monkeypatch,'HISC 144','Selected topics in South Asian history.'))
    assert out['courses']==[] and out['source_dispositions'][0]['status']=='source_content_conflict'
    monkeypatch.undo()
    out=m.parse_observations(fixture(monkeypatch,'HINE 116','Ottoman contacts with Europe.'))
    assert out['courses']==[] and out['source_dispositions'][0]['status']=='source_title_conflict'


def test_full_current_chapter_replay_does_not_fail_on_unassigned_duplicate():
    path=Path('/tmp/ucsd-hieu.html')
    if not path.exists():pytest.skip('Optional ignored History chapter absent')
    out=m.parse_observations(path.read_text());assert len(out['courses'])==78 and len(out['source_dispositions'])==7
    assert sum(c['credits']==4 for c in out['courses'])==76
    assert sum(c['credits']==6 for c in out['courses'])==1
    assert sum(c['credits']is None for c in out['courses'])==1
    assert not {'requirements','curriculum_audit','course_identity_groups'}&out.keys()
    with pytest.raises(ValueError):m.parse_observations(path.read_text()+path.read_text())


def test_actual_eligibility_repetition_and_renumbering_are_not_inferred_globally():
    by={e['code']:e for e in m.SPEC['entries']}
    assert len(by)==85
    assert sum(e['approved_for_integration']for e in by.values())==78
    assert sum(e.get('category_review',{}).get('status')=='unclassified'for e in by.values())==10
    assert any('Application and acceptance' in n for n in by['HILD 7GS']['notes'])
    assert any('does not publish an application' in n for n in by['HINE 135GS']['notes'])
    assert any('maximum of12' in n for n in by['HITO 165']['notes'])
    assert any('instructor permission' in n for n in by['HINE 186']['notes'])
    assert by['HINE 186']['observed_prerequisites']is None
    assert any('renumbered from HITO104' in n for n in by['HIGL 104']['notes'])
    assert by['HITO 104']['heading']is None
