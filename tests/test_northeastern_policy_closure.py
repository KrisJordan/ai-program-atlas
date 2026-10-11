from pathlib import Path
import json
import pytest
from atlas.adapters import northeastern_policy_closure as m


def business_fixture():
    parts=['all students are required to complete a cooperative education plan','academic advisor and co-op coordinator','Students should consult their degree program and catalog term']
    for _,title,guards,_ in m.BUSINESS_RULES:parts.append('<h2>'+title+'</h2><p>'+'; '.join(guards)+'</p>')
    return '<div id="site-title"><h1>D\'Amore-McKim School of Business</h1></div>2026-2027<div id="textcontainer">'+''.join(parts)+'</div>'


def test_business_conditional_rules_do_not_infer_extra_fixed_courses_or_permission():
    result=m.observe_business(business_fixture(),program_id=m.BUSINESS)
    assert len(result['requirements'])==7 and result['courses']==[]
    assert all(r['kind']=='note' and not r['course_ids'] for r in result['requirements'])
    summaries=' '.join(r['summary']for r in result['requirements'])
    assert 'not approval granted' in summaries
    assert 'practicum, internship and co-op' in summaries
    assert 'normally not transferable' in summaries
    assert 'prescribed degree curriculum' in summaries


@pytest.mark.parametrize('old,new',[('32 semester hours','28 semester hours'),('16 semester hours','12 semester hours'),('maximum of 50%','maximum of 75%'),('prior written approval','subsequent approval'),('2026-2027','2025-2026'),("D'Amore-McKim School of Business",'Other College')])
def test_business_changed_limits_conditions_version_or_identity_requires_review(old,new):
    with pytest.raises(ValueError):m.observe_business(business_fixture().replace(old,new),program_id=m.BUSINESS)


def test_all_actual_cssh_and_business_policy_replays_and_eligibility_boundaries():
    cache=Path('.cache/research/degree-audit-northeastern')
    if not (cache/'business-policy.html').exists():pytest.skip('Ignored actual policy capture unavailable')
    assert len(m.observe_business((cache/'business-policy.html').read_text(),program_id=m.BUSINESS)['requirements'])==7
    for url,filename in [(m.CSSH_CATALOG,'home-14.html'),(m.CSSH_CHANGE,'home-10.html'),(m.CSSH_PROGRESS,'home-11.html')]:
        for pid in m.CSSH_PROGRAMS:
            result=m.observe_cssh((cache/filename).read_text(),program_id=pid,source=url)
            assert len(result['requirements'])==1 and result['requirements'][0]['kind']=='note'
            assert result['courses']==[]
        with pytest.raises(ValueError):m.observe_cssh((cache/filename).read_text(),program_id=m.BUSINESS,source=url)
    change=m.observe_cssh((cache/'home-10.html').read_text(),program_id=next(iter(m.CSSH_PROGRAMS)),source=m.CSSH_CHANGE)['requirements'][0]
    assert 'not list AI and International Affairs' in change['summary']
    assert 'strongly recommended, not mandatory' in change['summary']
    changed=(cache/'home-11.html').read_text().replace('first day class offerings are posted','last day class offerings are posted')
    with pytest.raises(ValueError):m.observe_cssh(changed,program_id=next(iter(m.CSSH_PROGRAMS)),source=m.CSSH_PROGRESS)


def test_seven_concrete_scopes_have_independent_participation_sources_and_no_course_deltas():
    pids=m.CSSH_PROGRAMS|{m.BUSINESS,m.PREFIX+'journalism-bs-boston-bs-degree'}
    for pid in pids:
        seed=json.loads((Path('data/programs')/(pid+'.json')).read_text())
        source=next(s for s in seed['sources']if s['id']==pid+'-college-participation-audit')
        assert source['url']=='https://admissions.northeastern.edu/academics/combined-majors/'
        assert '(Khoury/' in source['locator']
        if pid in m.CSSH_PROGRAMS:
            rows=[r for r in seed['requirements']if r['source_id'].endswith(('cssh-catalog-supplement','cssh-change-supplement','cssh-reentry-supplement'))]
            assert len(rows)==3 and all(r['kind']=='note' and not r['course_ids']for r in rows)
