from pathlib import Path
import hashlib
import pytest
from atlas.adapters import ucsd_literature_first_reviews as m


def fixture(monkeypatch,code='LTEA 151',body='Literary study.'):
    entry=dict(next(e for e in m.SPEC['entries']if e['code']==code));entry['description_hash']=hashlib.sha256(body.encode()).hexdigest()
    monkeypatch.setattr(m,'SPEC',{**m.SPEC,'entries':[entry],'additional_contexts':[]})
    return ('<h1>Literature</h1><p class="course-disclaimer">2026–27</p><h2>'+entry['region']+'</h2><h3>'+entry['division']+'</h3><p>'+entry.get('section_text','')+'</p><p class="course-name">'+str(entry['heading'])+'</p><p class="course-descriptions">'+body+'</p>')


def test_section_preparation_and_unlabeled_language_fluency_are_preserved(monkeypatch):
    c=m.parse_observations(fixture(monkeypatch))['courses'][0]
    assert 'upper-division standing or consent' in c['prerequisites']
    assert 'intermediate fluency' in c['prerequisites']
    assert c['credits']==4 and c['category']=='human_context'
    assert 'category_review'not in c


def test_move_out_of_reviewed_division_or_changed_section_rule_withdraws(monkeypatch):
    html=fixture(monkeypatch)
    with pytest.raises(ValueError,match='outside reviewed section'):
        m.parse_observations(html.replace('<p class="course-name">','<h3>Lower Division</h3><p class="course-name">'))
    with pytest.raises(ValueError,match='eligibility'):
        m.parse_observations(html.replace('upper-division standing or consent of instructor','open enrollment'))


@pytest.mark.parametrize('before,after',[('2026–27','2027–28'),('Literary study.','New subject.'),('LTEA 151.','LTEA 152.')])
def test_edition_body_identity_changes_require_review(monkeypatch,before,after):
    with pytest.raises(ValueError):m.parse_observations(fixture(monkeypatch).replace(before,after))


def test_changed_topic_hold_is_not_replaced_by_number_match(monkeypatch):
    result=m.parse_observations(fixture(monkeypatch,'LTWL 134','Islam and cinema.'))
    assert result['courses']==[]
    assert result['source_dispositions']==[dict(code='LTWL 134',status='source_title_conflict',observed_name='Cinema and Islam')]


def test_variable_credit_and_pass_fail_are_not_fixed_four(monkeypatch):
    course=m.parse_observations(fixture(monkeypatch,'LTWL 199'))['courses'][0]
    assert course['credits']is None
    assert 'upper-division standing and department approval' in course['prerequisites']
    assert any('P/NP' in n and '2 or 4' in n for n in course['notes'])


def test_actual_chapter_replay_and_language_context_guard():
    path=Path('/tmp/ucsd-literature.html')
    if not path.exists():pytest.skip('Optional ignored actual Literature capture absent')
    html=path.read_text();out=m.parse_observations(html)
    assert len(out['courses'])==64 and len(out['source_dispositions'])==8
    assert sum(c['credits']==4 for c in out['courses'])==63
    assert sum(c['category']=='human_context'for c in out['courses'])==63
    assert sum(c['prerequisites']is None for c in out['courses'])==3
    assert all('category_review'not in c for c in out['courses'])
    assert not {'requirements','curriculum_audit','course_identity_groups'}&out.keys()
    with pytest.raises(ValueError,match='language/context'):
        m.parse_observations(html.replace('lectures and discussions are conducted in English','lectures and discussions are conducted in Russian'))


def test_credit_exclusions_and_shared_repeat_caps_remain_local():
    by={e['code']:e for e in m.SPEC['entries']}
    assert len(by)==72 and len({e['id']for e in by.values()})==72
    assert any('cannot be earned for both' in n for n in by['LTEU 150A']['notes'])
    assert any('combined two-enrollment' in n for n in by['LTEN 181']['notes'])
    assert any('twelve total units' in n for n in by['LTEN 185']['notes'])
    assert any('138R and 138GS' in n for n in by['LTEA 138']['notes'])
    assert by['LTWL 159']['category']=='human_context' # technology's cultural effects, not implementation
    assert by['LTWL 198']['category_review']['status']=='unclassified'
    assert by['LTEA 130']['heading']is None
