import hashlib
from pathlib import Path
import pytest
from atlas.adapters import ucsd_ltsp_remaining_reviews as m


def fixture(monkeypatch,code='LTSP 110',body='Language analysis.'):
    e=dict(next(e for e in m.SPEC['entries']if e['code']==code));e['description_hash']=hashlib.sha256(body.encode()).hexdigest()
    monkeypatch.setattr(m,'SPEC',{**m.SPEC,'entries':[e]})
    return f'<h1>Literature</h1><p class="course-disclaimer">2026–27</p><h2>{e["region"]}</h2><h3>{e["division"]}</h3><p>{e["section_text"]}</p><p class="course-name">{e["heading"]}</p><p class="course-descriptions">{body}</p>'


def test_actual_grammar_methods_not_prefix_classification(monkeypatch):
    c=m.parse_observations(fixture(monkeypatch))['courses'][0]
    assert c['category']=='applications'and c['credits']==4
    assert 'Section prerequisite' in c['prerequisites']and'Course prerequisite' in c['prerequisites']
    assert 'category_review'not in c


def test_five_unit_lower_course_has_heritage_and_test_routes(monkeypatch):
    c=m.parse_observations(fixture(monkeypatch,'LTSP 2A'))['courses'][0]
    assert c['credits']==5 and 'upper-division'not in c['prerequisites']
    assert 'AP Spanish' in c['prerequisites']
    assert any('heritage' in n for n in c['notes'])


@pytest.mark.parametrize('old,new',[('2026–27','2027–28'),('Language analysis.','New field.'),('upper-division standing or consent of instructor','graduate standing')])
def test_source_or_section_changes_withdraw(monkeypatch,old,new):
    with pytest.raises(ValueError):m.parse_observations(fixture(monkeypatch).replace(old,new))


def test_renumbered_older_identity_not_automatically_replaced():
    es={e['code']:e for e in m.SPEC['entries']}
    for older,newer in [('LTSP 2D','LTSP 2F'),('LTSP 2E','LTSP 3F'),('LTSP 100B','LTSP 100F')]:
        assert es[older]['heading']is None
        assert any(newer in n and 'renumbered' in n for n in es[older]['notes'])
    assert '100F'not in es['LTSP 174GS']['course_prerequisites']
    assert 'consent'not in es['LTSP 174GS']['course_prerequisites']
    assert 'Global Seminars' in es['LTSP 174GS']['course_prerequisites']
    assert es['LTSP 128']['category']=='applications'
    assert es['LTSP 124']['category']=='human_context'


def test_actual_complete_replay():
    p=Path('/tmp/ucsd-literature.html')
    if not p.exists():pytest.skip('Optional official capture absent')
    r=m.parse_observations(p.read_text())
    assert len(r['courses'])==35 and len(r['source_dispositions'])==6
    assert sum(c['credits']==5 for c in r['courses'])==3
    assert sum(c['category']=='human_context'for c in r['courses'])==33
    assert not {'requirements','curriculum_audit','course_identity_groups'}&r.keys()
