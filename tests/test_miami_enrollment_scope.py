import hashlib
from pathlib import Path
import pytest
from atlas.adapters import miami_enrollment_scope as m


def actual(key):
    p=Path('.cache/research/miami-degree-audit')/('policy-'+key+'.html')
    if not p.exists():pytest.skip('Optional official policy cache unavailable')
    return p.read_text()


@pytest.mark.parametrize('key',list(m.HASHES))
def test_policy_observations_are_conditional_and_course_free(key):
    html=actual(key);pid=sorted(m.PROGRAMS)[0];observed=m.parse(html,pid=pid,key=key)
    assert len(observed['requirements'])==len(m.NOTES[key])
    assert all(r['kind']=='note' and not r['course_ids'] and r['credits']is None for r in observed['requirements'])
    assert 'curriculum_audit'not in observed and observed['courses']==[]
    old=lambda _:dict(id=pid,requirements=[dict(id='prior',kind='note')],courses=[])
    assert m._compose(old,html,pid=pid,key=key)['requirements'][0]['id']=='prior'
    with pytest.raises(ValueError):m.parse(html,pid='unrelated',key=key)


@pytest.mark.parametrize('key,before,after',[
 ('courses','semester system','quarter system'),
 ('courses','25%','50%'),
 ('graduation','150 credit hours','120 credit hours'),
 ('graduation','not simply requested','simply requested')])
def test_changed_unit_modality_approval_or_degree_scope_requires_review(key,before,after):
    html=actual(key);assert before in html
    with pytest.raises(ValueError):m.parse(html.replace(before,after),pid=sorted(m.PROGRAMS)[0],key=key)


def test_permissions_and_optional_dual_degree_do_not_promote_membership():
    courses=' '.join(n[2]for n in m.NOTES['courses']);graduation=' '.join(n[2]for n in m.NOTES['graduation'])
    assert 'does not promise a prerequisite override' in courses
    assert 'not completed enrollment' in courses
    assert 'does not increase the single degree' in graduation
    assert 'before the first degree' in graduation


def test_undergraduate_progression_and_proficiency_keep_scope():
    grades=m.NOTES['grades'][0][2];general=' '.join(n[2] for n in m.NOTES['general'])
    assert 'subject to a college' in grades and 'college exceptions' in grades
    assert '13 credits' in grades
    assert 'specifically approves MAS110 for the BBA' in general
    assert 'not generalized' in general and 'does not award' in general
