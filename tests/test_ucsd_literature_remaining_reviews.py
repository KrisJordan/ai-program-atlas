from pathlib import Path
import hashlib
import pytest
from atlas.adapters import ucsd_literature_remaining_reviews as m


def fixture(monkeypatch, code='LTFR 123', body='Literary interpretation.'):
    e=dict(next(e for e in m.SPEC['entries'] if e['code']==code))
    e['description_hash']=hashlib.sha256(body.encode()).hexdigest()
    monkeypatch.setattr(m,'SPEC',{**m.SPEC,'entries':[e],'additional_contexts':[],'supplementary_blocks':[]})
    return f'<h1>Literature</h1><p class="course-disclaimer">2026–27</p><h2>{e["region"]}</h2><h3>{e["division"]}</h3><p>{e["section_text"]}</p><p class="course-name">{e["heading"]}</p><p class="course-description">{body}</p>'


def test_french_language_and_both_prerequisite_scopes(monkeypatch):
    c=m.parse_observations(fixture(monkeypatch))['courses'][0]
    assert 'upper-division standing or consent' in c['prerequisites']
    assert 'LTFR 104' in c['prerequisites']
    assert any('taught in French' in x for x in c['notes'])
    assert c['credits']==4 and c['category']=='human_context'
    assert 'category_review'not in c


def test_lower_italian_does_not_inherit_upper_or_graduate_eligibility(monkeypatch):
    c=m.parse_observations(fixture(monkeypatch,'LTIT 12AR'))['courses'][0]
    assert c['prerequisites']is None
    assert any('distance education' in x for x in c['notes'])


def test_russian_rubric_rule_survives_translation_heading(monkeypatch):
    c=m.parse_observations(fixture(monkeypatch,'LTRU 110A'))['courses'][0]
    assert 'Translation' in c['name']
    assert any('LTRU enrollment is for reading and writing in Russian' in x for x in c['notes'])


def test_title_scope_hold_does_not_transfer_current_content(monkeypatch):
    result=m.parse_observations(fixture(monkeypatch,'LTAM 110GS'))
    assert result['courses']==[]
    assert result['source_dispositions'][0]['status']=='source_title_conflict'


@pytest.mark.parametrize('change', ['body','edition','section','placement'])
def test_source_changes_require_review(monkeypatch,change):
    html=fixture(monkeypatch)
    old,new={'body':('Literary interpretation.','Other subject.'),'edition':('2026–27','2027–28'),'section':('upper-division standing or consent of instructor','graduate standing'),'placement':('<p class="course-name">','<h3>Graduate</h3><p class="course-name">')}[change]
    with pytest.raises(ValueError):m.parse_observations(html.replace(old,new))


def test_manual_content_dispositions_and_explicit_successor_limits():
    entries={e['code']:e for e in m.SPEC['entries']}
    assert len(entries)==53
    assert entries['LTCS 108']['category']=='human_context'
    assert entries['LTCS 155']['category']=='human_context'
    assert entries['LTSP 166']['category']=='applications'
    assert entries['LTWR 126']['heading']is None
    assert any('renumbered' in x for x in entries['LTWR 126']['notes'])
    assert entries['LTWR 113']['heading']is None
    assert any('no explicit renumbering' in x for x in entries['LTWR 113']['notes'])
    assert {e['code']for e in m.SPEC['supplementary_blocks']}=={'LTWR 101W','LTWR 126W','LTWR 113C'}


def test_actual_source_replay_and_successor_context_guards():
    path=Path('/tmp/ucsd-literature.html')
    if not path.exists():pytest.skip('Optional ignored source capture absent')
    html=path.read_text();r=m.parse_observations(html)
    assert len(r['courses'])==46 and len(r['source_dispositions'])==7
    assert all(c['credits']==4 for c in r['courses'])
    assert sum(c['category']=='human_context'for c in r['courses'])==45
    assert not {'requirements','curriculum_audit','course_identity_groups'}&r.keys()
    with pytest.raises(ValueError,match='successor'):
        m.parse_observations(html.replace('Renumbered from LTWR 126.','Renumbering unknown.'))
    with pytest.raises(ValueError,match='language/context'):
        m.parse_observations(html.replace('All upper-division courses are taught in French.','All courses use English.'))
